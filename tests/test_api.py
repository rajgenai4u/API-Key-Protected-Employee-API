"""API tests: auth behaviour + CRUD + Pydantic validation."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store

API_KEY = "super30-secret-key"
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    store.clear()
    yield
    store.clear()


def auth(key: str = API_KEY) -> dict:
    return {"X-API-Key": key}


def sample_employee(**overrides) -> dict:
    data = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "role": "Software Engineer",
        "department": "Engineering",
        "salary": 95000.0,
        "age": 30,
    }
    data.update(overrides)
    return data


def test_health():
    assert client.get("/health").status_code == 200


def test_list_employees_is_public():
    response = client.get("/employees")
    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}


def test_create_without_key_returns_401():
    response = client.post("/employees", json=sample_employee())
    assert response.status_code == 401
    assert "Missing API key" in response.json()["detail"]


def test_create_with_wrong_key_returns_403():
    response = client.post("/employees", json=sample_employee(), headers=auth("wrong-key"))
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API key."


def test_delete_with_wrong_key_returns_403():
    assert client.delete("/employees/1", headers=auth("nope")).status_code == 403


def test_update_without_key_returns_401():
    assert client.put("/employees/1", json={"salary": 1.0}).status_code == 401


def test_full_crud_flow():
    created = client.post("/employees", json=sample_employee(), headers=auth())
    assert created.status_code == 201
    body = created.json()
    employee_id = body["id"]

    listed = client.get("/employees").json()
    assert listed["total"] == 1

    updated = client.put(
        f"/employees/{employee_id}",
        json={"salary": 120000.0, "role": "Principal Engineer"},
        headers=auth(),
    )
    assert updated.status_code == 200
    assert updated.json()["salary"] == 120000.0
    assert updated.json()["role"] == "Principal Engineer"
    assert updated.json()["name"] == "Ada Lovelace"  # untouched fields preserved

    deleted = client.delete(f"/employees/{employee_id}", headers=auth())
    assert deleted.status_code == 204
    assert client.get(f"/employees/{employee_id}").status_code == 404


def test_validation_rejects_bad_email():
    response = client.post("/employees", json=sample_employee(email="not-an-email"), headers=auth())
    assert response.status_code == 422


def test_validation_rejects_negative_salary():
    response = client.post("/employees", json=sample_employee(salary=-5), headers=auth())
    assert response.status_code == 422


def test_validation_rejects_unknown_department():
    response = client.post("/employees", json=sample_employee(department="Pirate"), headers=auth())
    assert response.status_code == 422


def test_validation_rejects_missing_fields():
    response = client.post("/employees", json={"name": "No Email"}, headers=auth())
    assert response.status_code == 422
    assert any(err["loc"][-1] == "email" for err in response.json()["detail"])

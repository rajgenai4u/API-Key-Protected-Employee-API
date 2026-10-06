# Employee Management API (API-Key Protected)

A FastAPI CRUD API for managing employees, where the write endpoints are protected by an API key passed in the `X-API-Key` request header. Request and response payloads are validated with **Pydantic**.

## Endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/employees` | Public | List employees (optional `?department=` filter) |
| `GET` | `/employees/{employee_id}` | Public | Get a single employee |
| `POST` | `/employees` | **API key** | Create an employee |
| `PUT` | `/employees/{employee_id}` | **API key** | Update an employee (partial update) |
| `DELETE` | `/employees/{employee_id}` | **API key** | Delete an employee |
| `GET` | `/health` | Public | Service health check |
| `GET` | `/docs` | Public | Interactive Swagger UI |

## Authentication logic

Protected endpoints require this header:

```
X-API-Key: <your-secret-key>
```

The dependency in [`app/auth.py`](app/auth.py) decides the response:

| Situation | Status | Why |
| --- | --- | --- |
| Header missing / empty | **401 Unauthorized** (+ `WWW-Authenticate: ApiKey`) | The client never presented credentials |
| Header present but wrong | **403 Forbidden** | Credentials were presented but are not valid |
| Header correct | Request continues | Key compared with `hmac.compare_digest` (constant time, no timing attacks) |

The expected key is read at runtime from the `API_KEY` environment variable, so **no real secret is stored in this repository**. A placeholder development key (`super30-secret-key`) is used only when `API_KEY` is not set, so the demo runs out of the box.

## Pydantic validation

- `name` / `role`: 2–80 characters, blank values rejected
- `email`: must be a valid email (`EmailStr`)
- `department`: must be one of `Engineering, Human Resources, Marketing, Finance, Sales, Operations`
- `salary`: must be `> 0` and `<= 10,000,000`
- `age`: optional, 18–75
- Unknown/missing fields → `422 Unprocessable Entity` with a structured error body

## Project structure

```
.
├── app/
│   ├── main.py       # FastAPI app, CORS, /health
│   ├── auth.py       # X-API-Key dependency (401/403 logic)
│   ├── routes.py     # /employees CRUD routes
│   ├── schemas.py    # Pydantic models + validators
│   └── store.py      # Thread-safe in-memory store
├── tests/test_api.py # Auth, CRUD and validation tests
├── requirements.txt
├── .env.example      # Template for the secret (copy to .env)
└── .gitignore        # Blocks .env and other secrets from being committed
```

## Getting started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then edit .env and set your own API_KEY
uvicorn app.main:app --reload
```

The API now serves at <http://localhost:8000> (Swagger UI at `/docs`).

## Demo: successful and failed requests

### 1. Public read — no key needed (200)

```bash
curl -i http://localhost:8000/employees
```

### 2. Protected write with NO key → 401

```bash
curl -i -X POST http://localhost:8000/employees \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada Lovelace","email":"ada@example.com","role":"Software Engineer",
       "department":"Engineering","salary":95000,"age":30}'
```

```json
{"detail":"Missing API key. Provide it in the 'X-API-Key' header."}
```

### 3. Protected write with a WRONG key → 403

```bash
curl -i -X POST http://localhost:8000/employees \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wrong-key" \
  -d '{"name":"Ada Lovelace","email":"ada@example.com","role":"Software Engineer",
       "department":"Engineering","salary":95000,"age":30}'
```

```json
{"detail":"Invalid API key."}
```

### 4. Protected write with the CORRECT key → 201

```bash
curl -i -X POST http://localhost:8000/employees \
  -H "Content-Type: application/json" \
  -H "X-API-Key: super30-secret-key" \
  -d '{"name":"Ada Lovelace","email":"ada@example.com","role":"Software Engineer",
       "department":"Engineering","salary":95000,"age":30}'
```

```json
{"id":1,"name":"Ada Lovelace","email":"ada@example.com","role":"Software Engineer",
 "department":"Engineering","salary":95000.0,"age":30,"is_active":true,
 "created_at":"2026-10-06T17:03:45Z","updated_at":"2026-10-06T17:03:45Z"}
```

### 5. Update and delete (key required)

```bash
curl -i -X PUT http://localhost:8000/employees/1 \
  -H "Content-Type: application/json" -H "X-API-Key: super30-secret-key" \
  -d '{"salary":120000}'

curl -i -X DELETE http://localhost:8000/employees/1 \
  -H "X-API-Key: super30-secret-key"
```

### 6. Invalid payload → 422 (Pydantic)

```bash
curl -i -X POST http://localhost:8000/employees \
  -H "Content-Type: application/json" -H "X-API-Key: super30-secret-key" \
  -d '{"name":"A","email":"not-an-email","role":"Eng","department":"Pirate","salary":-5}'
```

```json
{"detail":[
  {"type":"string_too_short","loc":["body","name"],"msg":"String should have at least 2 characters",...},
  {"type":"value_error","loc":["body","email"],"msg":"value is not a valid email address...",...},
  {"type":"value_error","loc":["body","department"],"msg":"Value error, department must be one of ...",...},
  {"type":"greater_than","loc":["body","salary"],"msg":"Input should be greater than 0",...}
]}
```

## Running the tests

```bash
python3 -m pytest tests -q
```

Covers: missing key (401), wrong key (403), correct key CRUD flow, and Pydantic rejection cases.

## Security notes

- The real API key lives **only** in `.env`, which is listed in `.gitignore` and is never pushed to GitHub.
- `.env.example` contains a placeholder only.
- Key comparison uses `hmac.compare_digest` to avoid timing side channels.
- Rotate the key by updating the `API_KEY` environment variable on the server; no code change required.

## Demo video

YouTube walkthrough (successful vs. failed requests + auth logic): _link added after upload_

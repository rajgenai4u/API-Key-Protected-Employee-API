"""Employee CRUD endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from .auth import require_api_key
from .schemas import Employee, EmployeeCreate, EmployeeList, EmployeeUpdate
from .store import store

router = APIRouter(prefix="/employees", tags=["employees"])

# Reads are public, writes require the X-API-Key header.
PROTECTED = {"dependencies": [Depends(require_api_key)]}


@router.get("", response_model=EmployeeList, summary="List employees (public)")
def list_employees(department: Optional[str] = Query(default=None, description="Filter by department")) -> EmployeeList:
    employees = store.list(department=department)
    return EmployeeList(total=len(employees), items=[Employee.model_validate(e) for e in employees])


@router.get("/{employee_id}", response_model=Employee, summary="Get one employee (public)")
def get_employee(employee_id: int) -> Employee:
    employee = store.get(employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return Employee.model_validate(employee)


@router.post("", response_model=Employee, status_code=status.HTTP_201_CREATED, summary="Create employee (protected)", **PROTECTED)
def create_employee(payload: EmployeeCreate) -> Employee:
    return Employee.model_validate(store.create(payload))


@router.put("/{employee_id}", response_model=Employee, summary="Update employee (protected)", **PROTECTED)
def update_employee(employee_id: int, payload: EmployeeUpdate) -> Employee:
    employee = store.update(employee_id, payload)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return Employee.model_validate(employee)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete employee (protected)", **PROTECTED)
def delete_employee(employee_id: int) -> None:
    if not store.delete(employee_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

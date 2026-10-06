"""Thread-safe in-memory employee store (no database required for the demo)."""

import threading
from typing import Dict, List, Optional

from .schemas import EmployeeCreate, EmployeeUpdate, utcnow


class EmployeeStore:
    def __init__(self) -> None:
        self._employees: Dict[int, dict] = {}
        self._next_id = 1
        self._lock = threading.Lock()

    def list(self, department: Optional[str] = None) -> List[dict]:
        with self._lock:
            employees = list(self._employees.values())
        if department:
            employees = [e for e in employees if e["department"] == department.title()]
        return employees

    def get(self, employee_id: int) -> Optional[dict]:
        with self._lock:
            return self._employees.get(employee_id)

    def create(self, payload: EmployeeCreate) -> dict:
        with self._lock:
            employee_id = self._next_id
            self._next_id += 1
            now = utcnow()
            employee = {"id": employee_id, "created_at": now, "updated_at": now, **payload.model_dump()}
            self._employees[employee_id] = employee
            return employee

    def update(self, employee_id: int, payload: EmployeeUpdate) -> Optional[dict]:
        with self._lock:
            employee = self._employees.get(employee_id)
            if employee is None:
                return None
            changes = payload.model_dump(exclude_unset=True)
            employee.update(changes)
            employee["updated_at"] = utcnow()
            return employee

    def delete(self, employee_id: int) -> bool:
        with self._lock:
            return self._employees.pop(employee_id, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._employees.clear()
            self._next_id = 1


store = EmployeeStore()

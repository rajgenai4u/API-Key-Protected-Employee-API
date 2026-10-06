"""Pydantic models used for request validation and response serialization."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

DEPARTMENTS = ("Engineering", "Human Resources", "Marketing", "Finance", "Sales", "Operations")


class EmployeeBase(BaseModel):
    """Fields shared by create/update requests and responses."""

    name: str = Field(..., min_length=2, max_length=80, examples=["Ada Lovelace"])
    email: EmailStr = Field(..., examples=["ada@example.com"])
    role: str = Field(..., min_length=2, max_length=80, examples=["Software Engineer"])
    department: str = Field(..., examples=["Engineering"])
    salary: float = Field(..., gt=0, le=10_000_000, examples=[95000.0])
    age: Optional[int] = Field(default=None, ge=18, le=75)
    is_active: bool = Field(default=True)

    @field_validator("name", "role")
    @classmethod
    def strip_and_validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("department")
    @classmethod
    def validate_department(cls, value: str) -> str:
        cleaned = value.strip().title()
        if cleaned not in DEPARTMENTS:
            raise ValueError(f"department must be one of {', '.join(DEPARTMENTS)}")
        return cleaned


class EmployeeCreate(EmployeeBase):
    """Payload for POST /employees."""


class EmployeeUpdate(BaseModel):
    """Payload for PUT /employees/{employee_id}. All fields are optional (partial update)."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=80)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(default=None, min_length=2, max_length=80)
    department: Optional[str] = None
    salary: Optional[float] = Field(default=None, gt=0, le=10_000_000)
    age: Optional[int] = Field(default=None, ge=18, le=75)
    is_active: Optional[bool] = None

    @field_validator("name", "role")
    @classmethod
    def strip_and_validate_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("department")
    @classmethod
    def validate_department(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip().title()
        if cleaned not in DEPARTMENTS:
            raise ValueError(f"department must be one of {', '.join(DEPARTMENTS)}")
        return cleaned


class Employee(EmployeeBase):
    """Response model returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class EmployeeList(BaseModel):
    total: int
    items: list[Employee]


class ErrorResponse(BaseModel):
    detail: str


def utcnow() -> datetime:
    return datetime.now(timezone.utc)

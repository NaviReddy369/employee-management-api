from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, condecimal, model_validator


class GenderEnum(str, Enum):
    """Stored in DB column `employees.gender` (same values as CSV `Gender`)."""

    F = "F"
    M = "M"


SalaryDecimal = condecimal(max_digits=12, decimal_places=2, gt=0)

_EMPLOYEE_CREATE_EXAMPLE = {
    "EMPLOYEE_ID": 1,
    "GENDER": "F",
    "EXPERIENCE_YEARS": 4,
    "POSITION": "DevOps Engineer",
    "SALARY": "109976.00",
}

_EMPLOYEE_OUT_EXAMPLE = {
    "employee_id": 1,
    "gender": "F",
    "experience_years": 4,
    "position": "DevOps Engineer",
    "salary": "109976.00",
    "created_at": "2026-04-01T12:00:00+00:00",
    "updated_at": "2026-04-01T12:00:00+00:00",
}

_EMPLOYEE_UPDATE_EXAMPLE = {
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Senior DevOps Engineer",
    "SALARY": "120000.00",
}


class EmployeeCreate(BaseModel):
    """
    Request body for **POST /employees**. Maps to table `employees` and to **employee_data.csv** columns:

    | CSV | JSON |
    |-----|------|
    | ID | EMPLOYEE_ID |
    | Gender | GENDER |
    | Experience (Years) | EXPERIENCE_YEARS |
    | Position | POSITION |
    | Salary | SALARY |
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={"example": _EMPLOYEE_CREATE_EXAMPLE},
    )

    EMPLOYEE_ID: int = Field(
        ...,
        gt=0,
        description="Primary key. DB: `employees.employee_id`. CSV: `ID`.",
    )
    GENDER: GenderEnum = Field(
        ...,
        description="DB: `employees.gender`. CSV: `Gender` (F or M).",
    )
    EXPERIENCE_YEARS: int = Field(
        ...,
        ge=0,
        le=80,
        description="DB: `employees.experience_years`. CSV: `Experience (Years)`.",
    )
    POSITION: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="DB: `employees.position`. CSV: `Position`.",
    )
    SALARY: SalaryDecimal = Field(
        ...,
        description="DB: `employees.salary` (NUMERIC). CSV: `Salary`.",
    )


class EmployeeUpdate(BaseModel):
    """Request body for **PUT /employees/{employee_id}**. Omitted fields stay unchanged."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={"example": _EMPLOYEE_UPDATE_EXAMPLE},
    )

    GENDER: GenderEnum | None = Field(
        None,
        description="DB: `employees.gender`.",
    )
    EXPERIENCE_YEARS: int | None = Field(
        None,
        ge=0,
        le=80,
        description="DB: `employees.experience_years`.",
    )
    POSITION: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="DB: `employees.position`.",
    )
    SALARY: SalaryDecimal | None = Field(
        None,
        description="DB: `employees.salary`.",
    )

    @model_validator(mode="after")
    def at_least_one_field(self):
        if (
            self.GENDER is None
            and self.EXPERIENCE_YEARS is None
            and self.POSITION is None
            and self.SALARY is None
        ):
            raise ValueError(
                "Provide at least one of GENDER, EXPERIENCE_YEARS, POSITION, SALARY"
            )
        return self


class EmployeeOut(BaseModel):
    """Response shape: mirrors `employees` table (snake_case JSON keys)."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": _EMPLOYEE_OUT_EXAMPLE},
    )

    employee_id: int = Field(
        ...,
        description="PK `employees.employee_id` (CSV `ID`).",
    )
    gender: str = Field(
        ...,
        description="`employees.gender`",
    )
    experience_years: int = Field(
        ...,
        description="`employees.experience_years`",
    )
    position: str = Field(
        ...,
        description="`employees.position`",
    )
    salary: Decimal = Field(
        ...,
        description="`employees.salary`",
    )
    created_at: str | None = Field(
        None,
        description="`employees.created_at` (timestamptz)",
    )
    updated_at: str | None = Field(
        None,
        description="`employees.updated_at` (timestamptz)",
    )


class ExportResult(BaseModel):
    employee_count: int
    s3_uri: str | None = None
    sns_message_id: str | None = None


class CsvPreviewRow(BaseModel):
    """First rows as they map from CSV to API fields."""

    EMPLOYEE_ID: int = Field(description="From CSV `ID`")
    GENDER: str = Field(description="From CSV `Gender`")
    EXPERIENCE_YEARS: int = Field(description="From CSV `Experience (Years)`")
    POSITION: str = Field(description="From CSV `Position`")
    SALARY: str = Field(description="From CSV `Salary`")


class CsvPreview(BaseModel):
    path: str
    total_rows: int
    sample: list[CsvPreviewRow]


class ImportCsvResult(BaseModel):
    path: str
    total_rows_in_file: int
    imported: int
    skipped: int
    errors: list[dict]

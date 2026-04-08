"""Map employee_data.csv (ID, Gender, Experience (Years), Position, Salary) to API."""

import csv
from pathlib import Path

from pydantic import ValidationError

from app.schemas import EmployeeCreate, GenderEnum

CSV_EXPERIENCE_KEY = "Experience (Years)"


def row_to_employee_create(row: dict) -> EmployeeCreate:
    rid = int(str(row["ID"]).strip())
    gender = str(row["Gender"]).strip().upper()
    exp = int(float(str(row[CSV_EXPERIENCE_KEY]).strip()))
    pos = (row.get("Position") or "").strip()
    sal = str(row["Salary"]).strip()
    return EmployeeCreate(
        EMPLOYEE_ID=rid,
        GENDER=GenderEnum(gender),
        EXPERIENCE_YEARS=exp,
        POSITION=pos,
        SALARY=sal,
    )


def parse_employee_csv(path: Path) -> tuple[list[EmployeeCreate], list[dict], int]:
    """Returns (valid rows, parse errors, count of non-empty ID rows)."""
    valid: list[EmployeeCreate] = []
    errors: list[dict] = []
    counted = 0
    if not path.is_file():
        return valid, [{"error": f"File not found: {path}"}], 0

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            if not row.get("ID", "").strip():
                continue
            counted += 1
            try:
                valid.append(row_to_employee_create(row))
            except (KeyError, ValueError, ValidationError) as e:
                errors.append({"line": i, "error": str(e)})
    return valid, errors, counted

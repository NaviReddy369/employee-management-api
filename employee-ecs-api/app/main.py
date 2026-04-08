from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path as ApiPath, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.config import settings
from app.csv_import import parse_employee_csv
from app.database import engine, get_db
from app.exceptions import EmployeeAlreadyExistsError
from app.models import Base
from app.schemas import (
    CsvPreview,
    CsvPreviewRow,
    EmployeeCreate,
    EmployeeOut,
    EmployeeUpdate,
    ExportResult,
    ImportCsvResult,
)
from app.services.aws_export import export_employees_json_to_s3_and_notify


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Employee API",
    description=(
        "REST API backed by PostgreSQL table **employees**, aligned with **employee_data.csv**: "
        "`ID` → `employee_id`, `Gender` → `gender`, `Experience (Years)` → `experience_years`, "
        "`Position` → `position`, `Salary` → `salary`. "
        "See each schema below for DB column names and examples."
    ),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "employees",
            "description": "CRUD on the `employees` table (same fields as the CSV).",
        },
        {
            "name": "import",
            "description": "Bulk load from `employee_data.csv` on the server.",
        },
        {
            "name": "export",
            "description": "Write all rows as JSON to S3 and notify SNS (optional AWS env).",
        },
    ],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(EmployeeAlreadyExistsError)
async def employee_exists_handler(_, exc: EmployeeAlreadyExistsError):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
            "employee_id": exc.employee_id,
            "existing_position": exc.position,
        },
    )


@app.post(
    "/employees",
    response_model=EmployeeOut,
    tags=["employees"],
    summary="Create employee (POST)",
    response_description="Row from `employees` after insert.",
)
async def post_employee(
    body: EmployeeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = await crud.create_employee(db, body)
    return _to_out(row)


@app.get(
    "/employees/{employee_id}",
    response_model=EmployeeOut,
    tags=["employees"],
    summary="Get employee by ID (GET)",
    response_description="Single row from `employees` by primary key.",
)
async def get_employee(
    employee_id: Annotated[
        int,
        ApiPath(description="Primary key `employees.employee_id` (CSV column `ID`).", ge=1),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = await crud.get_employee(db, employee_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _to_out(row)


@app.delete(
    "/employees/{employee_id}",
    status_code=204,
    tags=["employees"],
    summary="Delete employee (DELETE)",
)
async def delete_employee(
    employee_id: Annotated[
        int,
        ApiPath(description="Primary key `employees.employee_id`.", ge=1),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ok = await crud.delete_employee(db, employee_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found")


@app.put(
    "/employees/{employee_id}",
    response_model=EmployeeOut,
    tags=["employees"],
    summary="Update employee (PUT)",
    response_description="Updated row from `employees`.",
)
async def put_employee(
    employee_id: Annotated[
        int,
        ApiPath(description="Primary key `employees.employee_id`.", ge=1),
    ],
    body: EmployeeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = await crud.update_employee(db, employee_id, body)
    if row is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _to_out(row)


@app.get(
    "/employees",
    response_model=list[EmployeeOut],
    tags=["employees"],
    summary="List employees (GET)",
    response_description="All rows from `employees`, optional filter on `created_at`.",
)
async def list_employees(
    db: Annotated[AsyncSession, Depends(get_db)],
    year: int | None = Query(
        None,
        ge=2000,
        le=2100,
        description="Filter: year of `employees.created_at` (use with `month` or alone).",
    ),
    month: int | None = Query(
        None,
        ge=1,
        le=12,
        description="Filter: month of `employees.created_at` (requires `year`).",
    ),
):
    if month is not None and year is None:
        raise HTTPException(
            status_code=400,
            detail="Provide both year and month for monthly filter",
        )
    rows = await crud.list_employees(db, year=year, month=month)
    return [_to_out(r) for r in rows]


def _resolve_csv_path() -> Path:
    p = Path(settings.employee_csv_path)
    root = Path(__file__).resolve().parent.parent
    return p if p.is_absolute() else (root / p)


@app.get(
    "/employees/import/csv/preview",
    response_model=CsvPreview,
    tags=["import"],
    summary="Preview CSV → DB mapping",
    description=(
        "Shows how the first rows of `employee_data.csv` map to `EMPLOYEE_ID`, `GENDER`, "
        "`EXPERIENCE_YEARS`, `POSITION`, `SALARY` (same as table `employees`)."
    ),
)
async def preview_employee_csv():
    path = _resolve_csv_path()
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"CSV not found: {path}")
    items, _, counted = parse_employee_csv(path)
    sample: list[CsvPreviewRow] = []
    for e in items[:5]:
        sample.append(
            CsvPreviewRow(
                EMPLOYEE_ID=e.EMPLOYEE_ID,
                GENDER=e.GENDER.value,
                EXPERIENCE_YEARS=e.EXPERIENCE_YEARS,
                POSITION=e.POSITION,
                SALARY=str(e.SALARY),
            )
        )
    return CsvPreview(
        path=str(path.resolve()),
        total_rows=counted,
        sample=sample,
    )


@app.post(
    "/employees/import/csv",
    response_model=ImportCsvResult,
    tags=["import"],
    summary="Import all rows from CSV",
    description="Inserts every row from `employee_data.csv`; skips IDs that already exist.",
)
async def import_employee_csv(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    path = _resolve_csv_path()
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"CSV not found: {path}")
    items, parse_errors, counted = parse_employee_csv(path)
    imported, skipped, row_errors = await crud.import_employees_batch(db, items)
    return ImportCsvResult(
        path=str(path.resolve()),
        total_rows_in_file=counted,
        imported=imported,
        skipped=skipped,
        errors=parse_errors + row_errors,
    )


@app.get(
    "/employees/export/s3",
    response_model=ExportResult,
    tags=["export"],
    summary="Export JSON to S3 + SNS",
    description="Reads all `employees` rows, writes JSON to S3, publishes SNS (if configured).",
)
async def export_employees_to_s3(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rows = await crud.list_employees(db)
    payload = [
        {
            "employee_id": r.employee_id,
            "gender": r.gender,
            "experience_years": r.experience_years,
            "position": r.position,
            "salary": str(r.salary),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    s3_uri, sns_id = export_employees_json_to_s3_and_notify(payload)
    return ExportResult(
        employee_count=len(rows),
        s3_uri=s3_uri,
        sns_message_id=sns_id,
    )


def _to_out(row) -> EmployeeOut:
    return EmployeeOut(
        employee_id=row.employee_id,
        gender=row.gender,
        experience_years=row.experience_years,
        position=row.position,
        salary=row.salary,
        created_at=row.created_at.isoformat() if row.created_at else None,
        updated_at=row.updated_at.isoformat() if row.updated_at else None,
    )


static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.is_dir():
    app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")


@app.get("/")
async def root():
    index = static_dir / "index.html"
    if index.is_file():
        return FileResponse(index)
    return {"docs": "/docs", "ui": "/ui/"}

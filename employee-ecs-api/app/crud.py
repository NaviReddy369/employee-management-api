from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import EmployeeAlreadyExistsError
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeUpdate


async def create_employee(db: AsyncSession, data: EmployeeCreate) -> Employee:
    existing = await db.get(Employee, data.EMPLOYEE_ID)
    if existing is not None:
        raise EmployeeAlreadyExistsError(
            employee_id=data.EMPLOYEE_ID,
            position=existing.position,
        )
    row = Employee(
        employee_id=data.EMPLOYEE_ID,
        gender=data.GENDER.value,
        experience_years=data.EXPERIENCE_YEARS,
        position=data.POSITION,
        salary=data.SALARY,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def get_employee(db: AsyncSession, employee_id: int) -> Employee | None:
    return await db.get(Employee, employee_id)


async def delete_employee(db: AsyncSession, employee_id: int) -> bool:
    row = await db.get(Employee, employee_id)
    if row is None:
        return False
    await db.execute(delete(Employee).where(Employee.employee_id == employee_id))
    await db.commit()
    return True


async def update_employee(
    db: AsyncSession, employee_id: int, data: EmployeeUpdate
) -> Employee | None:
    row = await db.get(Employee, employee_id)
    if row is None:
        return None
    if data.GENDER is not None:
        row.gender = data.GENDER.value
    if data.EXPERIENCE_YEARS is not None:
        row.experience_years = data.EXPERIENCE_YEARS
    if data.POSITION is not None:
        row.position = data.POSITION
    if data.SALARY is not None:
        row.salary = Decimal(str(data.SALARY))
    row.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(row)
    return row


async def list_employees(
    db: AsyncSession,
    year: int | None = None,
    month: int | None = None,
) -> list[Employee]:
    q = select(Employee).order_by(Employee.employee_id)
    if year is not None and month is not None:
        q = q.where(
            extract("year", Employee.created_at) == year,
            extract("month", Employee.created_at) == month,
        )
    elif year is not None:
        q = q.where(extract("year", Employee.created_at) == year)
    result = await db.execute(q)
    return list(result.scalars().all())


async def count_employees(db: AsyncSession) -> int:
    from sqlalchemy import func

    r = await db.execute(select(func.count()).select_from(Employee))
    return int(r.scalar_one())


async def import_employees_batch(
    db: AsyncSession,
    items: list[EmployeeCreate],
) -> tuple[int, int, list[dict]]:
    """Insert many rows; skip duplicate IDs. Returns (imported, skipped, row_errors)."""
    imported = 0
    skipped = 0
    row_errors: list[dict] = []
    for data in items:
        try:
            await create_employee(db, data)
            imported += 1
        except EmployeeAlreadyExistsError:
            skipped += 1
        except Exception as e:
            row_errors.append({"employee_id": data.EMPLOYEE_ID, "error": str(e)})
    return imported, skipped, row_errors

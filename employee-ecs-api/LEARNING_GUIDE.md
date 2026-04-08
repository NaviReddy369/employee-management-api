# 🎓 Employee ECS API - Complete Learning Guide

## Table of Contents
1. [Project Navigation](#project-navigation)
2. [CRUD API Design & REST Conventions](#1-crud-api-design--rest-conventions)
3. [Async Programming](#2-async-programming)
4. [Data Validation with Pydantic](#3-data-validation-with-pydantic)
5. [Database Relationships](#4-database-relationships)
6. [Error Handling](#5-error-handling)
7. [CSV Processing](#6-csv-processing)
8. [AWS Integration](#7-aws-integration)
9. [Docker Architecture](#8-docker-architecture)

---

# 📂 Project Navigation

## File Structure Explained

```
employee-ecs-api/
├── app/                          # Main application code
│   ├── __init__.py              # Package initializer
│   ├── main.py                  # 🎯 API routes & FastAPI app (START HERE)
│   ├── models.py                # SQLAlchemy ORM models (database tables)
│   ├── schemas.py               # Pydantic validation schemas (request/response)
│   ├── crud.py                  # Database operations (Create, Read, Update, Delete)
│   ├── database.py              # SQLAlchemy engine & session setup
│   ├── config.py                # Settings & environment variables
│   ├── csv_import.py            # CSV parsing logic
│   ├── exceptions.py            # Custom error classes
│   └── services/
│       └── aws_export.py        # S3 & SNS integration
├── docker-compose.yml           # Multi-container setup (PostgreSQL + API)
├── Dockerfile                   # Container image definition
├── requirements.txt             # Python dependencies
├── employee_data.csv            # Sample data (49 employees)
└── static/
    └── index.html               # Basic UI

```

## How to Navigate the Code

**Level 1 (Start here):**
1. Open `docker-compose.yml` - Understand how services connect
2. Read `requirements.txt` - See what libraries are installed
3. Check `app/config.py` - Learn what settings exist

**Level 2 (Core logic):**
1. `app/main.py` - All API endpoints
2. `app/schemas.py` - Data validation rules
3. `app/models.py` - Database structure

**Level 3 (Implementation):**
1. `app/crud.py` - How data is stored/retrieved
2. `app/database.py` - Database connection setup
3. `app/csv_import.py` - CSV parsing

**Level 4 (Advanced):**
1. `app/services/aws_export.py` - Cloud integration
2. `app/exceptions.py` - Custom errors

---

# 1️⃣ CRUD API Design & REST Conventions

## What is REST?

**REST = Representational State Transfer**
- Uses standard HTTP methods (GET, POST, PUT, DELETE)
- Resources are identified by URLs
- Stateless (each request is independent)
- HTTP Status codes convey results

## The 4 CRUD Operations

| Operation | HTTP Method | Purpose | Status Code |
|-----------|------------|---------|------------|
| **CREATE** | POST | Add new resource | 201 Created |
| **READ** | GET | Retrieve resource(s) | 200 OK |
| **UPDATE** | PUT | Modify existing resource | 200 OK |
| **DELETE** | DELETE | Remove resource | 204 No Content |

## Employee API Examples

### 📁 Location: `app/main.py` (lines 78-175)

### ✅ CREATE - POST /employees

**Code:**
```python
@app.post(
    "/employees",
    response_model=EmployeeOut,  # Validates response
    tags=["employees"],
    summary="Create employee (POST)",
)
async def post_employee(
    body: EmployeeCreate,          # Pydantic validation
    db: Annotated[AsyncSession, Depends(get_db)],  # Database dependency
):
    row = await crud.create_employee(db, body)
    return _to_out(row)
```

**What happens:**
1. Client sends JSON with employee data
2. Pydantic validates against `EmployeeCreate` schema
3. `crud.create_employee()` inserts into PostgreSQL
4. Returns the created employee with `created_at` timestamp

**Test it:**
```powershell
# Terminal command
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 100,
    "GENDER": "F",
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Senior DevOps Engineer",
    "SALARY": "150000.00"
  }'
```

**Expected Response (201 Created):**
```json
{
  "employee_id": 100,
  "gender": "F",
  "experience_years": 5,
  "position": "Senior DevOps Engineer",
  "salary": "150000.00",
  "created_at": "2026-04-07T15:30:00+00:00",
  "updated_at": "2026-04-07T15:30:00+00:00"
}
```

---

### 📖 READ - GET /employees/{id}

**Code:**
```python
@app.get(
    "/employees/{employee_id}",
    response_model=EmployeeOut,
    tags=["employees"],
    summary="Get employee by ID (GET)",
)
async def get_employee(
    employee_id: Annotated[int, ApiPath(..., ge=1)],  # Path parameter
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = await crud.get_employee(db, employee_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _to_out(row)
```

**What happens:**
1. Extracts `employee_id` from URL (e.g., `/employees/1`)
2. Queries database for that ID
3. Returns 404 if not found, else returns employee data

**Test it:**
```powershell
curl http://localhost:8000/employees/1
```

---

### 📋 READ - GET /employees (List All)

**Code:**
```python
@app.get(
    "/employees",
    response_model=list[EmployeeOut],
    tags=["employees"],
    summary="List employees (GET)",
)
async def list_employees(
    db: Annotated[AsyncSession, Depends(get_db)],
    year: int | None = Query(None, ge=2000, le=2100),  # Optional filter
    month: int | None = Query(None, ge=1, le=12),      # Optional filter
):
    rows = await crud.list_employees(db, year=year, month=month)
    return [_to_out(r) for r in rows]
```

**What happens:**
1. Retrieves all employees
2. Optionally filters by creation year/month
3. Returns list of employees

**Test it:**
```powershell
# Get all
curl http://localhost:8000/employees

# Filter by year
curl "http://localhost:8000/employees?year=2026"

# Filter by year and month
curl "http://localhost:8000/employees?year=2026&month=4"
```

---

### ✏️ UPDATE - PUT /employees/{id}

**Code:**
```python
@app.put(
    "/employees/{employee_id}",
    response_model=EmployeeOut,
    tags=["employees"],
    summary="Update employee (PUT)",
)
async def put_employee(
    employee_id: Annotated[int, ApiPath(..., ge=1)],
    body: EmployeeUpdate,          # Partial update allowed (all fields optional)
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = await crud.update_employee(db, employee_id, body)
    if row is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _to_out(row)
```

**What happens:**
1. Takes employee ID from URL
2. Takes partial data from body (only fields to update)
3. Updates only provided fields, leaves others unchanged
4. Returns updated employee

**Test it:**
```powershell
# Update only salary and position
curl -X PUT http://localhost:8000/employees/1 `
  -H "Content-Type: application/json" `
  -d '{
    "POSITION": "Principal Engineer",
    "SALARY": "200000.00"
  }'
```

---

### 🗑️ DELETE - DELETE /employees/{id}

**Code:**
```python
@app.delete(
    "/employees/{employee_id}",
    status_code=204,               # No Content response
    tags=["employees"],
    summary="Delete employee (DELETE)",
)
async def delete_employee(
    employee_id: Annotated[int, ApiPath(..., ge=1)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ok = await crud.delete_employee(db, employee_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found")
```

**What happens:**
1. Finds employee by ID
2. Deletes from database
3. Returns 204 (No Content) on success
4. Returns 404 if employee doesn't exist

**Test it:**
```powershell
curl -X DELETE http://localhost:8000/employees/100
```

---

## REST Convention Rules to Remember

✅ **DO:**
- Use plural nouns for resources: `/employees` not `/employee`
- Use GET for read-only operations
- Use POST for creation
- Use PUT for updates
- Use DELETE for removal
- Return appropriate HTTP status codes
- Include resource ID in URL path for specific operations

❌ **DON'T:**
- Use verbs in URLs: ❌ `/getEmployee`, ✅ `/employees/{id}`
- Use GET for data changes
- Mix POST and PUT (POST for new, PUT for existing)

---

# 2️⃣ Async Programming

## Why Async/Await Matters

### The Problem: Blocking Code

**Traditional (Blocking) Code:**
```python
# Without async: If DB takes 1 second, user waits 1 second
response = database.query(sql)  # BLOCKS here for 1 second
return response
```

If 100 users request simultaneously:
- User 1 waits 1s → User 2 waits 2s → User 3 waits 3s → ... → User 100 waits 100 seconds! 😱

### The Solution: Async/Await

**Async Code:**
```python
# With async: While waiting for DB, handle other requests
response = await database.query(sql)  # Non-blocking wait
return response
```

If 100 users request simultaneously:
- All 100 can be handled concurrently ⚡
- Total time = ~1 second (max DB latency) instead of 100 seconds!

## How Async Works in This Project

### 📁 Location: `app/main.py`, `app/crud.py`, `app/database.py`

### Key Components

**1. Async Function Definition:**
```python
async def post_employee(
    body: EmployeeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # "async" keyword = this function is asynchronous
    row = await crud.create_employee(db, body)  # "await" waits without blocking
    return _to_out(row)
```

**Anatomy:**
- `async def` - Creates an async function
- `await` - Pauses execution until result, allows other tasks to run
- Cannot use `await` outside `async` function

**2. Async Database Engine:**

📄 `app/database.py`:
```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Create async engine (can handle multiple requests concurrently)
engine = create_async_engine(
    settings.database_url,  # postgresql+asyncpg://...
    echo=False,
    pool_pre_ping=True,     # Check connection before using
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session  # Provides session to endpoint
```

**What's happening:**
- `asyncpg` - PostgreSQL driver for async Python
- `AsyncSession` - Non-blocking database session
- Multiple requests can use session pool concurrently

**3. Async CRUD Operations:**

📄 `app/crud.py`:
```python
async def create_employee(db: AsyncSession, data: EmployeeCreate) -> Employee:
    # Check if employee exists (async query)
    existing = await db.get(Employee, data.EMPLOYEE_ID)  # ⬅️ Doesn't block!
    
    if existing is not None:
        raise EmployeeAlreadyExistsError(...)
    
    # Create new employee
    row = Employee(...)
    db.add(row)
    
    # Commit to database (async)
    await db.commit()  # ⬅️ Waits for DB without blocking other requests
    await db.refresh(row)  # ⬅️ Reload from DB
    
    return row
```

### Real-World Scenario

**Scenario: Two users request simultaneously**

**Without Async (Blocking):**
```
User A: POST /employees        Server: Insert into DB... (1 second)
User B: GET /employees         Server: WAITING for User A... (1 second)
                               Server: Now query DB (1 second)
Total: User B waits 2 seconds!
```

**With Async (Non-Blocking):**
```
User A: POST /employees        Server: Start insert... (doesn't block)
User B: GET /employees         Server: While waiting, handle GET!
                               Server: Both run concurrently
Total: Both done in ~1 second! ✅
```

### Performance Comparison

```
Scenario: 100 concurrent users, each DB call takes 100ms

Without Async:
  Request 1: 100ms
  Request 2: 200ms (waits for 1)
  Request 3: 300ms (waits for 1 & 2)
  ...
  Request 100: 10,000ms (waits for all others!)
  Total time: 10 seconds

With Async:
  Requests 1-100: ~100ms each (all concurrent!)
  Total time: ~100ms
  
✅ 100x faster!
```

### Key Async Patterns in Code

**Pattern 1: Async Query**
```python
user = await db.get(Employee, employee_id)  # Get by ID
```

**Pattern 2: Async List**
```python
result = await db.execute(select(Employee))
employees = result.scalars().all()
```

**Pattern 3: Async Commit**
```python
db.add(new_employee)
await db.commit()  # Save to DB
await db.refresh(new_employee)  # Reload with DB values
```

---

# 3️⃣ Data Validation with Pydantic

## What is Pydantic?

**Pydantic** = Automatic type checking & validation library
- Validates incoming data before processing
- Converts/coerces types safely
- Generates error messages
- Creates JSON schemas automatically

## Why Data Validation Matters

### Without Validation ❌
```python
# Client sends malformed data
{"EMPLOYEE_ID": "abc", "GENDER": "X", "SALARY": -1000}

# Server processes invalid data
employee = Employee(...)
# Bad data in database! 💥
```

### With Validation ✅
```python
# Same malformed data
{"EMPLOYEE_ID": "abc", "GENDER": "X", "SALARY": -1000}

# Pydantic rejects it immediately
# Response: "EMPLOYEE_ID must be an integer"
# No bad data in database! ✅
```

## Pydantic Schemas in This Project

### 📁 Location: `app/schemas.py`

### Schema 1: EmployeeCreate (For POST Requests)

```python
class EmployeeCreate(BaseModel):
    """Request body for POST /employees"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Auto-trim whitespace
    )
    
    EMPLOYEE_ID: int = Field(
        ...,                    # Required (... = must provide)
        gt=0,                   # Greater than 0
        description="Primary key"
    )
    
    GENDER: GenderEnum = Field(
        ...,
        description="F or M"
    )
    
    EXPERIENCE_YEARS: int = Field(
        ...,
        ge=0,                   # Greater than or equal 0
        le=80,                  # Less than or equal 80
        description="0-80 years"
    )
    
    POSITION: str = Field(
        ...,
        min_length=1,           # At least 1 character
        max_length=255,         # Max 255 characters
        description="Job title"
    )
    
    SALARY: SalaryDecimal = Field(
        ...,                    # Required
        description="Positive decimal with 2 places"
    )
```

**Validation Rules:**
| Field | Rule | Example ✅ | Example ❌ |
|-------|------|-----------|-----------|
| EMPLOYEE_ID | gt 0 (>0) | 1, 100 | 0, -5, "abc" |
| GENDER | Must be "F" \| "M" | "F", "M" | "X", "Female" |
| EXPERIENCE_YEARS | 0-80 | 5, 0, 80 | -1, 81, "five" |
| POSITION | 1-255 chars | "Engineer" | "", "x"*256 |
| SALARY | Positive decimal | "100.50" | "-50", "abc" |

**Test Validation:**

```powershell
# ✅ Valid request
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 1,
    "GENDER": "F",
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Engineer",
    "SALARY": "100000.00"
  }'
# Response: 200 OK + employee data

# ❌ Invalid - EMPLOYEE_ID must be > 0
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 0,
    "GENDER": "F",
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Engineer",
    "SALARY": "100000.00"
  }'
# Response: 422 Validation Error

# ❌ Invalid - SALARY negative
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 1,
    "GENDER": "F",
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Engineer",
    "SALARY": "-5000.00"
  }'
# Response: 422 Validation Error: "ensure this value is greater than 0"
```

### Schema 2: EmployeeUpdate (For PUT Requests)

```python
class EmployeeUpdate(BaseModel):
    """Request body for PUT /employees/{id}
    
    All fields are OPTIONAL (can omit any field)
    Only provided fields are updated
    """
    
    GENDER: GenderEnum | None = None       # Optional
    EXPERIENCE_YEARS: int | None = None    # Optional
    POSITION: str | None = None            # Optional
    SALARY: SalaryDecimal | None = None    # Optional
```

**Key Difference:**
- `EmployeeCreate` - All fields required
- `EmployeeUpdate` - All fields optional

**Example:**
```powershell
# Update ONLY position and salary (experience_years unchanged)
curl -X PUT http://localhost:8000/employees/1 `
  -H "Content-Type: application/json" `
  -d '{
    "POSITION": "Senior Engineer",
    "SALARY": "150000.00"
  }'
```

### Schema 3: EmployeeOut (For Responses)

```python
class EmployeeOut(BaseModel):
    """Response from GET/POST/PUT endpoints
    
    This is what the API returns to the client
    """
    
    employee_id: int
    gender: str
    experience_years: int
    position: str
    salary: Decimal      # Always returns as string in JSON
    created_at: str      # ISO format timestamp
    updated_at: str      # ISO format timestamp
```

### Special Types

**1. GenderEnum - Restricted to F or M**

```python
class GenderEnum(str, Enum):
    F = "F"
    M = "M"

# Only these values allowed
GenderEnum("F")  # ✅
GenderEnum("M")  # ✅
GenderEnum("X")  # ❌ ValueError
```

**2. SalaryDecimal - Precise decimal with rules**

```python
SalaryDecimal = condecimal(
    max_digits=12,      # Max 12 total digits
    decimal_places=2,   # Exactly 2 decimal places
    gt=0                # Must be > 0
)

# Valid: 123456789.99, 0.01
# Invalid: -100, 50.999, 0
```

## How Validation Works Step-by-Step

```python
# Request comes in
POST /employees
{
  "EMPLOYEE_ID": 1,
  "GENDER": "F",
  "EXPERIENCE_YEARS": 5,
  "POSITION": "Engineer",
  "SALARY": "100000.00"
}

# Step 1: FastAPI deserializes JSON
# Step 2: Pydantic validates against EmployeeCreate schema
#   - EMPLOYEE_ID: Check it's int and > 0 ✅
#   - GENDER: Check it's "F" or "M" ✅
#   - EXPERIENCE_YEARS: Check it's 0-80 ✅
#   - POSITION: Check it's 1-255 chars ✅
#   - SALARY: Check it's positive decimal ✅
# Step 3: If all pass, create EmployeeCreate object
# Step 4: Pass to endpoint handler

@app.post("/employees")
async def post_employee(body: EmployeeCreate, ...):
    # body is now guaranteed to be valid!
    # No need to check types
    row = await crud.create_employee(db, body)
    return row
```

---

# 4️⃣ Database Relationships

## This Project's Database Design

### Single Table: `employees`

This project uses the simplest database design: **one table, one primary key**.

```sql
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    gender CHAR(1),
    experience_years INTEGER,
    position VARCHAR(255),
    salary NUMERIC(12, 2),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### 📁 Location: `app/models.py`

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Integer, Numeric, String

class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass

class Employee(Base):
    """Maps to SQL: CREATE TABLE employees (...)"""
    
    __tablename__ = "employees"  # SQL table name
    
    # Column Definitions
    employee_id: Mapped[int] = mapped_column(
        primary_key=True,      # This is the unique identifier
        autoincrement=False    # Don't auto-increment (comes from CSV)
    )
    
    gender: Mapped[str] = mapped_column(String(1))
    # SQL: gender CHAR(1)
    
    experience_years: Mapped[int] = mapped_column(Integer)
    # SQL: experience_years INTEGER
    
    position: Mapped[str] = mapped_column(String(255))
    # SQL: position VARCHAR(255)
    
    salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    # SQL: salary NUMERIC(12, 2)  -- allows up to 12 digits, 2 decimal places
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)  # Auto-set on insert
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),        # Auto-set on insert
        onupdate=lambda: datetime.now(timezone.utc)        # Auto-update on modify
    )
```

## Understanding Each Column

| Column | Type | Purpose | Example |
|--------|------|---------|---------|
| `employee_id` | INT (PK) | Unique identifier | 1, 2, 3, ... |
| `gender` | CHAR(1) | Gender of employee | "F" or "M" |
| `experience_years` | INT | Years working | 5, 10, 0 |
| `position` | VARCHAR(255) | Job title | "DevOps Engineer" |
| `salary` | NUMERIC(12,2) | Annual salary | 100000.50 |
| `created_at` | TIMESTAMP | Record creation time | 2026-04-07T15:30:00Z |
| `updated_at` | TIMESTAMP | Last modification time | 2026-04-07T15:30:00Z |

## Primary Key Explanation

**Primary Key = Unique Identifier**

```python
employee_id: Mapped[int] = mapped_column(
    primary_key=True,      # ⬅️ This column is the primary key
    autoincrement=False    # ⬅️ Don't auto-generate (we set manually from CSV)
)
```

**What it means:**
- Each employee has a unique `employee_id`
- No two employees can have the same ID
- Used to quickly find specific employee
- Foreign keys (in other tables) would reference this

**Example:**
```sql
-- Valid data
employee_id | position
1           | Engineer
2           | Manager
3           | Developer

-- Invalid - duplicate ID rejected!
employee_id | position
1           | Engineer
1           | Manager    ❌ Error!
```

## Why This Design?

**Pros:**
- ✅ Simple and easy to understand
- ✅ Fast queries (single table)
- ✅ Perfect for learning/interviews
- ✅ No complex joins

**Cons:**
- ❌ No relationships to other tables
- ❌ Repeats data if scaled

## Entity-Relationship Diagram

```
┌─────────────────────────────────┐
│         employees               │
├─────────────────────────────────┤
│ PK: employee_id (INT)           │
│     gender (CHAR(1))            │
│     experience_years (INT)      │
│     position (VARCHAR(255))     │
│     salary (NUMERIC(12,2))      │
│     created_at (TIMESTAMP)      │
│     updated_at (TIMESTAMP)      │
└─────────────────────────────────┘

Single table, no relationships to other tables
```

## How Queries Work

**Get employee by ID (Primary Key Search):**
```python
employee = await db.get(Employee, employee_id=1)
# SQL Generated: SELECT * FROM employees WHERE employee_id = 1
# ⚡ Fast! (uses index on PK)
```

**List all employees:**
```python
result = await db.execute(select(Employee))
employees = result.scalars().all()
# SQL Generated: SELECT * FROM employees
```

**Filter by creation date:**
```python
q = select(Employee).where(
    extract("year", Employee.created_at) == 2026
)
result = await db.execute(q)
# SQL Generated: SELECT * FROM employees WHERE EXTRACT(YEAR FROM created_at) = 2026
```

---

# 5️⃣ Error Handling

## Custom Exception for Duplicate Employees

### 📁 Location: `app/exceptions.py`

```python
class EmployeeAlreadyExistsError(Exception):
    """Raised when trying to create employee with existing ID"""
    
    def __init__(self, employee_id: int, position: str):
        self.employee_id = employee_id
        self.position = position
        super().__init__(
            f"Employee ID {employee_id} already exists (Position: {position})"
        )
```

**Anatomy:**
- Inherits from `Exception` - Standard Python exception
- Stores details: `employee_id` and `position`
- `super().__init__()` - Calls parent exception initializer

## How Error Handling Works

### Location: `app/crud.py` (lines 11-20)

```python
async def create_employee(db: AsyncSession, data: EmployeeCreate) -> Employee:
    # Step 1: Check if employee already exists
    existing = await db.get(Employee, data.EMPLOYEE_ID)
    
    if existing is not None:
        # Step 2: Raise custom exception
        raise EmployeeAlreadyExistsError(
            employee_id=data.EMPLOYEE_ID,
            position=existing.position,
        )
    
    # Step 3: If no duplicate, create new employee
    row = Employee(...)
    db.add(row)
    await db.commit()
    return row
```

### Location: `app/main.py` (lines 67-76)

```python
@app.exception_handler(EmployeeAlreadyExistsError)
async def employee_exists_handler(_, exc: EmployeeAlreadyExistsError):
    """Convert custom exception to HTTP response"""
    return JSONResponse(
        status_code=409,  # Conflict - resource already exists
        content={
            "detail": str(exc),
            "employee_id": exc.employee_id,
            "existing_position": exc.position,
        },
    )
```

## HTTP Status Codes Used

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | GET, PUT succeed |
| 201 | Created | POST succeeds |
| 204 | No Content | DELETE succeeds |
| 400 | Bad Request | Invalid query params |
| 404 | Not Found | Employee doesn't exist |
| 409 | Conflict | Duplicate employee ID |
| 422 | Validation Error | Invalid request body |

## Complete Error Flow

**Scenario: Try to create duplicate employee**

```powershell
# First creation - succeeds
curl -X POST http://localhost:8000/employees `
  -d '{"EMPLOYEE_ID": 1, "GENDER": "F", "EXPERIENCE_YEARS": 5, ...}'
# Response: 201 Created

# Second creation with same ID - fails
curl -X POST http://localhost:8000/employees `
  -d '{"EMPLOYEE_ID": 1, "GENDER": "M", "EXPERIENCE_YEARS": 10, ...}'
# Response: 409 Conflict
# Content:
# {
#   "detail": "Employee ID 1 already exists (Position: Engineer)",
#   "employee_id": 1,
#   "existing_position": "Engineer"
# }
```

## Other Error Handling Examples

**404 Not Found:**
```python
@app.get("/employees/{employee_id}")
async def get_employee(employee_id: int, db: AsyncSession):
    row = await crud.get_employee(db, employee_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )
    return _to_out(row)
```

**422 Validation Error:**
```python
# Sent by Pydantic automatically
# If EMPLOYEE_ID is not an integer:
curl -X POST http://localhost:8000/employees `
  -d '{"EMPLOYEE_ID": "abc", ...}'
# Response: 422 Unprocessable Entity
# Pydantic automatically raises this!
```

---

# 6️⃣ CSV Processing

## What CSV Processing Does

Reads `employee_data.csv` and loads all rows into the PostgreSQL database.

**CSV File:** `employee_data.csv` (49 rows)

```
ID,Gender,Experience (Years),Position,Salary
1,F,4,DevOps Engineer,109976
2,M,6,DevOps Engineer,120088
3,M,17,Web Developer,181301
4,M,7,Systems Administrator,77530
...
```

## CSV Processing Pipeline

```
CSV File
  ↓
Parse Rows (extract ID, Gender, etc.)
  ↓
Validate Each Row (type checking, ranges)
  ↓
Skip Duplicates (if ID already in DB)
  ↓
Insert Valid Rows into Database
  ↓
Report: X imported, Y skipped, Z errors
```

## Step 1: CSV Parsing

### 📁 Location: `app/csv_import.py`

```python
def parse_employee_csv(path: Path) -> tuple[list[EmployeeCreate], list[dict], int]:
    """
    Parse CSV file and validate rows.
    
    Returns:
        - List of valid EmployeeCreate objects
        - List of parse errors
        - Total row count
    """
    valid: list[EmployeeCreate] = []  # Valid parsed rows
    errors: list[dict] = []           # Parsing errors
    counted = 0                        # Total rows processed
    
    # Check file exists
    if not path.is_file():
        return valid, [{"error": f"File not found: {path}"}], 0
    
    # Open and read CSV
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)  # DictReader = treats first row as headers
        for i, row in enumerate(reader, start=2):  # start=2 (row 1 is header)
            # Skip empty rows
            if not row.get("ID", "").strip():
                continue
            
            counted += 1
            
            try:
                # Convert CSV row to EmployeeCreate object
                employee_create = row_to_employee_create(row)
                valid.append(employee_create)
            except (KeyError, ValueError, ValidationError) as e:
                # Track parsing errors with line number
                errors.append({"line": i, "error": str(e)})
    
    return valid, errors, counted
```

### Step 1a: Convert Row Format

```python
def row_to_employee_create(row: dict) -> EmployeeCreate:
    """Convert CSV row to Pydantic model
    
    CSV columns → Python types → Pydantic model
    """
    
    # Extract ID column, convert to int
    rid = int(str(row["ID"]).strip())
    
    # Extract Gender, ensure uppercase
    gender = str(row["Gender"]).strip().upper()
    
    # Extract Experience, convert to int
    exp = int(float(str(row["Experience (Years)"])))
    
    # Extract Position
    pos = (row.get("Position") or "").strip()
    
    # Extract Salary
    sal = str(row["Salary"]).strip()
    
    # Create Pydantic model (automatically validates!)
    return EmployeeCreate(
        EMPLOYEE_ID=rid,
        GENDER=GenderEnum(gender),  # Validates is F or M
        EXPERIENCE_YEARS=exp,
        POSITION=pos,
        SALARY=sal,
    )
```

**Example Conversion:**
```
CSV Row: {"ID": "1", "Gender": "f", "Experience (Years)": "4.5", "Position": " DevOps Engineer ", "Salary": "109976"}

After Conversion:
EmployeeCreate(
    EMPLOYEE_ID=1,
    GENDER=GenderEnum.F,
    EXPERIENCE_YEARS=4,
    POSITION="DevOps Engineer",
    SALARY=Decimal("109976.00")
)

All validated! ✅
```

## Step 2: Batch Import (Handles Duplicates)

### 📁 Location: `app/crud.py` (lines 62-80)

```python
async def import_employees_batch(
    db: AsyncSession,
    items: list[EmployeeCreate],
) -> tuple[int, int, list[dict]]:
    """
    Insert many rows; skip duplicate IDs.
    
    Returns: (imported count, skipped count, errors list)
    """
    imported = 0
    skipped = 0
    row_errors: list[dict] = []
    
    # Try to insert each employee
    for data in items:
        try:
            # Attempt to create employee
            # If ID already exists, raises EmployeeAlreadyExistsError
            await create_employee(db, data)
            imported += 1
        except EmployeeAlreadyExistsError:
            # Expected error - ID already exists
            skipped += 1
        except Exception as e:
            # Unexpected error - record it
            row_errors.append({
                "employee_id": data.EMPLOYEE_ID,
                "error": str(e)
            })
    
    return imported, skipped, row_errors
```

**Logic:**
- For each employee in CSV
- Try to create in database
- If ID exists (duplicate), skip it
- If other error occurs, record the error
- Return summary statistics

## Step 3: API Endpoints for Import

### Preview Endpoint

📁 Location: `app/main.py` (lines 195-225)

```python
@app.get(
    "/employees/import/csv/preview",
    tags=["import"],
    summary="Preview CSV → DB mapping",
)
async def preview_employee_csv():
    """Show first 5 rows from CSV without importing"""
    
    path = _resolve_csv_path()  # Get CSV file path
    
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"CSV not found: {path}")
    
    # Parse CSV (but don't import yet)
    items, _, counted = parse_employee_csv(path)
    
    # Build preview (first 5 rows only)
    sample: list[CsvPreviewRow] = []
    for e in items[:5]:
        sample.append(CsvPreviewRow(
            EMPLOYEE_ID=e.EMPLOYEE_ID,
            GENDER=e.GENDER.value,
            EXPERIENCE_YEARS=e.EXPERIENCE_YEARS,
            POSITION=e.POSITION,
            SALARY=str(e.SALARY),
        ))
    
    return CsvPreview(
        path=str(path.resolve()),
        total_rows=counted,
        sample=sample,
    )
```

**Test it:**
```powershell
curl http://localhost:8000/employees/import/csv/preview
```

**Response:**
```json
{
  "path": "C:\\Users\\gudim\\employee-ecs-api\\employee_data.csv",
  "total_rows": 49,
  "sample": [
    {"EMPLOYEE_ID": 1, "GENDER": "F", "EXPERIENCE_YEARS": 4, "POSITION": "DevOps Engineer", "SALARY": "109976.00"},
    {"EMPLOYEE_ID": 2, "GENDER": "M", "EXPERIENCE_YEARS": 6, "POSITION": "DevOps Engineer", "SALARY": "120088.00"},
    ...
  ]
}
```

### Import Endpoint

📁 Location: `app/main.py` (lines 228-250)

```python
@app.post(
    "/employees/import/csv",
    tags=["import"],
    summary="Import all rows from CSV",
)
async def import_employee_csv(db: AsyncSession):
    """Load all CSV rows into database"""
    
    path = _resolve_csv_path()  # Resolve path
    
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"CSV not found: {path}")
    
    # Parse CSV
    items, parse_errors, counted = parse_employee_csv(path)
    
    # Batch import (skip duplicates)
    imported, skipped, row_errors = await crud.import_employees_batch(db, items)
    
    # Return summary
    return ImportCsvResult(
        path=str(path.resolve()),
        total_rows_in_file=counted,
        imported=imported,
        skipped=skipped,
        errors=parse_errors + row_errors,  # Combine all errors
    )
```

**Test it:**
```powershell
curl -X POST http://localhost:8000/employees/import/csv
```

**Response (First import):**
```json
{
  "path": "C:\\Users\\gudim\\employee-ecs-api\\employee_data.csv",
  "total_rows_in_file": 49,
  "imported": 49,
  "skipped": 0,
  "errors": []
}
```

**Response (Second import - all duplicates):**
```json
{
  "path": "C:\\Users\\gudim\\employee-ecs-api\\employee_data.csv",
  "total_rows_in_file": 49,
  "imported": 0,
  "skipped": 49,
  "errors": []
}
```

## CSV Processing Workflow - Complete Example

```
1. Admin calls: POST /employees/import/csv

2. System:
   - Reads employee_data.csv
   - Parses 49 rows
   - Validates each row against Pydantic schema
   
3. Batch Insert:
   - Employee 1: Check if exists? No → INSERT ✅ (imported++)
   - Employee 2: Check if exists? No → INSERT ✅ (imported++)
   - Employee 3: Check if exists? No → INSERT ✅ (imported++)
   - ...
   - Employee 49: Check if exists? No → INSERT ✅ (imported++)

4. Summary:
   {
     "imported": 49,
     "skipped": 0,
     "errors": []
   }

5. Database now has 49 employees! ✅
```

---

# 7️⃣ AWS Integration

## What is AWS Export?

`GET /employees/export/s3` does two things:
1. **Writes all employee data as JSON to S3** (cloud file storage)
2. **Publishes SNS notification** (sends a message that something happened)

## Technologies

| Service | Purpose |
|---------|---------|
| **S3** | Cloud file storage (like Google Drive for data) |
| **SNS** | Notification system (like email alerts) |
| **boto3** | Python library to interact with AWS |

## AWS Configuration

### 📁 Location: `app/config.py`

```python
class Settings(BaseSettings):
    # ... other settings ...
    
    aws_region: str = "us-east-1"              # AWS region
    s3_export_bucket: str = ""                 # S3 bucket name (empty = disabled)
    s3_export_prefix: str = "exports/json/"    # Folder in S3
    sns_topic_arn: str = ""                    # SNS topic ARN (empty = disabled)
```

**How to Enable:**
```bash
# Set environment variables before running
export AWS_REGION=us-east-1
export S3_EXPORT_BUCKET=my-company-employees-bucket
export SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789:my-topic
```

**In Docker Compose:**
```yaml
environment:
  AWS_REGION: us-east-1
  S3_EXPORT_BUCKET: my-company-employees-bucket
  SNS_TOPIC_ARN: arn:aws:sns:us-east-1:123456789:my-topic
```

## AWS Export Implementation

### 📁 Location: `app/services/aws_export.py`

```python
def export_employees_json_to_s3_and_notify(
    employees_payload: list[dict],
) -> tuple[str | None, str | None]:
    """
    Writes JSON to S3 and notifies via SNS.
    
    Returns: (s3_uri, sns_message_id)
    """
    
    # If S3 not configured, skip
    if not settings.s3_export_bucket:
        return None, None
    
    # Step 1: Generate S3 file name with timestamp
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = f"{settings.s3_export_prefix}employees-{ts}.json"
    # Result: "exports/json/employees-20260407T153000Z.json"
    
    # Step 2: Convert employees to JSON
    body = json.dumps(employees_payload, default=str, indent=2)
    # Result: Pretty-printed JSON string
    
    # Step 3: Upload to S3
    client = boto3.client("s3", region_name=settings.aws_region)
    client.put_object(
        Bucket=settings.s3_export_bucket,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
    )
    s3_uri = f"s3://{settings.s3_export_bucket}/{key}"
    # Result: "s3://my-bucket/exports/json/employees-20260407T153000Z.json"
    
    # Step 4: Publish SNS notification (if configured)
    sns_id = None
    if settings.sns_topic_arn:
        sns = boto3.client("sns", region_name=settings.aws_region)
        msg = json.dumps({
            "message": "Employee export JSON is available in S3",
            "s3_uri": s3_uri,
            "bucket": settings.s3_export_bucket,
            "key": key,
        })
        resp = sns.publish(
            TopicArn=settings.sns_topic_arn,
            Subject="Employee data export ready",
            Message=msg,
        )
        sns_id = resp.get("MessageId")
    
    return s3_uri, sns_id
```

### API Endpoint

📁 Location: `app/main.py` (lines 253-273)

```python
@app.get(
    "/employees/export/s3",
    tags=["export"],
    summary="Export JSON to S3 + SNS",
)
async def export_employees_to_s3(
    db: AsyncSession,
):
    """
    1. Get all employees from database
    2. Convert to JSON
    3. Upload to S3
    4. Send SNS notification
    """
    
    # Step 1: Fetch all employees
    rows = await crud.list_employees(db)
    
    # Step 2: Convert to JSON-serializable format
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
    
    # Step 3: Export to S3 and notify SNS
    s3_uri, sns_id = export_employees_json_to_s3_and_notify(payload)
    
    # Step 4: Return result
    return ExportResult(
        employee_count=len(rows),
        s3_uri=s3_uri,
        sns_message_id=sns_id,
    )
```

## Data Flow Example

```
Employee 1 (ORM Object)
├─ employee_id: 1
├─ gender: "F"
├─ experience_years: 4
├─ position: "DevOps Engineer"
├─ salary: Decimal("109976.00")
└─ created_at: datetime(...)

                ↓ (Convert to dict)

{
  "employee_id": 1,
  "gender": "F",
  "experience_years": 4,
  "position": "DevOps Engineer",
  "salary": "109976.00",
  "created_at": "2026-04-07T15:30:00+00:00"
}

                ↓ (Convert to JSON string)

"{\n  \"employee_id\": 1,\n  \"gender\": \"F\",\n  ...}"

                ↓ (Upload to S3)

s3://my-bucket/exports/json/employees-20260407T153000Z.json

                ↓ (Notify SNS subscribers)

Email: "Your employee data is ready in S3!"
```

## Test AWS Export (Without Real AWS)

**Currently:** `s3_export_bucket=""` (empty), so export is disabled

```powershell
# Call export endpoint
curl http://localhost:8000/employees/export/s3

# Response (since AWS disabled):
{
  "employee_count": 49,
  "s3_uri": null,
  "sns_message_id": null
}
```

**To Enable:** You'd need valid AWS credentials and set environment variables

```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export S3_EXPORT_BUCKET=my-company-bucket
export SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:my-topic
```

---

# 8️⃣ Docker Architecture

## What is Docker?

**Docker** = Package your application + all dependencies into a container
- Run consistently on any machine
- No "works on my machine" problems
- Isolated environments
- Easy deployment

## Docker Components in This Project

```
┌─────────────────────────────────────────────┐
│        docker-compose.yml                   │
│  (Defines 2 services: PostgreSQL + API)     │
├─────────────────────────────────────────────┤
│                                             │
│  Service 1: PostgreSQL Container            │
│  ├─ Image: postgres:16-alpine               │
│  ├─ Port: 5432                              │
│  ├─ Volume: pgdata (persistent data)        │
│  └─ Healthcheck: pg_isready                 │
│                                             │
│  Service 2: API Container                   │
│  ├─ Image: Built from Dockerfile            │
│  ├─ Port: 8000                              │
│  ├─ Depends on: db (healthcheck)            │
│  └─ Volume: employee_data.csv (read-only)   │
│                                             │
└─────────────────────────────────────────────┘
```

## File 1: Dockerfile

### 📁 Location: `Dockerfile`

```dockerfile
# Step 1: Start with base Python image
FROM python:3.12-slim

# Step 2: Set working directory inside container
WORKDIR /app

# Step 3: Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1  # Don't create .pyc files
ENV PYTHONUNBUFFERED=1          # Print output immediately

# Step 4: Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Result: All Python packages installed

# Step 5: Copy application code
COPY app ./app
COPY static ./static
COPY employee_data.csv ./employee_data.csv

# Step 6: Expose port
EXPOSE 8000  # Container listens on port 8000

# Step 7: Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Starts FastAPI server on 0.0.0.0:8000
```

**What Gets Built:**
```
Dockerfile
    ↓
Python 3.12 Base Image
    + pip install requirements.txt
    + COPY app/
    + COPY static/
    + COPY employee_data.csv
    + EXPOSE 8000
    ↓
Docker Image (ready to run)
```

## File 2: docker-compose.yml

### 📁 Location: `docker-compose.yml`

```yaml
# Compose file: defines multiple containers that work together
services:

  # Service 1: PostgreSQL Database
  db:
    image: postgres:16-alpine  # Official PostgreSQL image (small version)
    
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: employees    # Database name
    
    ports:
      - "5432:5432"            # Port mapping: host:container
    
    volumes:
      - pgdata:/var/lib/postgresql/data  # Persistent storage
    
    healthcheck:               # Check if PostgreSQL is ready
      test: ["CMD-SHELL", "pg_isready -U postgres -d employees"]
      interval: 5s             # Check every 5 seconds
      timeout: 5s              # Wait max 5 seconds for response
      retries: 5               # Try 5 times before failing
      start_period: 10s        # Wait 10s before first check

  # Service 2: FastAPI Application
  api:
    build: .                   # Build from Dockerfile in current dir
    
    ports:
      - "8000:8000"           # Port mapping: host:container
    
    environment:
      # Connection string for database
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/employees
      # @db = container name (Docker DNS)
      
      AWS_REGION: ${AWS_REGION:-us-east-1}
      S3_EXPORT_BUCKET: ${S3_EXPORT_BUCKET:-}
      SNS_TOPIC_ARN: ${SNS_TOPIC_ARN:-}
      EMPLOYEE_CSV_PATH: employee_data.csv
    
    volumes:
      - ./employee_data.csv:/app/employee_data.csv:ro
      # Mount CSV file from host to container (read-only)
    
    depends_on:
      db:
        condition: service_healthy  # Wait for DB healthcheck!

# Persistent storage volume
volumes:
  pgdata:
```

## How docker-compose Works

### Startup Sequence

```
1. Run: docker-compose up

2. Docker starts service "db":
   - Pulls postgres:16-alpine image
   - Creates container
   - Starts PostgreSQL process
   - Runs healthcheck: pg_isready

3. Healthcheck succeeds ✅

4. Docker starts service "api":
   - Builds image from Dockerfile
   - Creates container
   - Sets environment variables
   - Mounts volumes
   - Starts FastAPI with uvicorn

5. Both services running!
   ✅ PostgreSQL on 5432
   ✅ FastAPI on 8000

6. Containers can communicate:
   - API → "db" (automatic DNS)
   - DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/employees
     (Note "db" = container name!)
```

### Networking

**Without Docker Compose:**
```
Host Machine
├─ PostgreSQL running: localhost:5432
├─ FastAPI running: localhost:8000
└─ Client traffic goes to each directly
```

**With Docker Compose:**
```
┌───────────────────────────────────────┐
│  Docker Internal Network              │
├───────────────────────────────────────┤
│                                       │
│  Container "db"        Container "api"│
│  PostgreSQL            FastAPI        │
│  Port: 5432            Port: 8000     │
│                                       │
│  Can talk via: @db     Port: 8000     │
│  (automatic DNS!)      exposed        │
│                                       │
└───────────────────────────────────────┘
     ↑                           ↑
     |                           |
Host Port 5432         Host Port 8000
(to localhost)         (to localhost)
```

## Health Checks Explained

### Why Health Checks Matter

```
Without healthcheck:
1. Start DB container
2. Immediately start API container
3. API tries to connect to DB
4. DB still starting... ❌ Connection error!

With healthcheck:
1. Start DB container
2. API container waits...
3. DB says "I'm ready!" ✅
4. API container starts
5. API can connect to ready DB ✅
```

### PostgreSQL Healthcheck

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d employees"]
  # Runs: pg_isready -U postgres -d employees
  # Returns: 0 if ready, non-zero if not ready
  
  interval: 5s
  # Check every 5 seconds
  
  timeout: 5s
  # If check takes >5s, consider it failed
  
  retries: 5
  # Try 5 times before giving up
  
  start_period: 10s
  # Wait 10s before first check (PostgreSQL needs time to start)
```

## Persistent Data with Volumes

### pgdata Volume

```yaml
volumes:
  pgdata:
    # Named volume = Docker manages storage
```

```yaml
services:
  db:
    volumes:
      - pgdata:/var/lib/postgresql/data
      # Mount pgdata volume to /var/lib/postgresql/data
      # This is where PostgreSQL stores database files
```

**What This Means:**
```
- Container 1 runs, creates 49 employees ✅
- Container stops
- Container 2 starts
- Data still there! ✅ (because volume persists)

Without volume:
- Container stops
- All data deleted ❌
```

**To Access Data from Host:**
```powershell
# Data is stored in Docker's managed location
# Usually: C:\ProgramData\Docker\volumes\... (on Windows)

# Access via container:
docker-compose exec db psql -U postgres -d employees
# Enter PostgreSQL shell

# Or backup:
docker-compose exec db pg_dump -U postgres employees > backup.sql
```

## Common Docker Commands

```powershell
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build

# View logs
docker-compose logs api
docker-compose logs db
docker-compose logs -f api  # Follow logs

# Stop services
docker-compose down

# Remove volumes (delete data!)
docker-compose down -v

# View running containers
docker-compose ps

# Execute command in container
docker-compose exec api python -c "import app; print('Works!')"
```

## Understanding Port Mapping

```yaml
ports:
  - "8000:8000"  # host:container
```

```
Host Machine
│
├─ localhost:8000  (host port)
│       ↓
│  (Docker forwards to)
│       ↓
Container
└─ 0.0.0.0:8000   (container port)
   Internal to container
```

**In Dockerfile:**
```dockerfile
EXPOSE 8000  # Container listens here
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**In docker-compose:**
```yaml
ports:
  - "8000:8000"  # Forward host 8000 to container 8000
```

**How to Access:**
```powershell
# From host machine
curl http://localhost:8000/employees

# From inside container
curl http://0.0.0.0:8000/employees
# or
curl http://db:5432  (if on same network)
```

## Container Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    Host Machine                            │
│  (Windows, Mac, Linux)                                     │
│                                                            │
│  localhost:8000 ◄──────────────────┐                       │
│  localhost:5432 ◄────────────┐     │                       │
│                              │     │                       │
├──────────────────────────────┼─────┼────────────────────────┤
│  Docker Desktop              │     │                        │
│  ┌────────────────────────┐  │     │                        │
│  │ Docker Internal Network│  │     │                        │
│  │ ┌──────────────┐ ┌────┴───┴──┐ │                        │
│  │ │ db Container │ │api Container│ │                        │
│  │ │ PostgreSQL   │ │ FastAPI    │ │                        │
│  │ │ 5432  ◄──────┼─┤ 8000 ──────┼─┤ (port mapping)       │
│  │ └──────────────┘ └────────────┘ │                        │
│  │ (database)      (API server)    │                        │
│  └────────────────────────────────┘ │                        │
│  shared network: @db, @api          │                        │
└────────────────────────────────────────────────────────────┘
```

---

# 🎯 Quick Reference & Review

## Concept Quick Links

| Concept | File | Key Function |
|---------|------|--------------|
| API Routes | `app/main.py` | FastAPI endpoint definitions |
| Database Models | `app/models.py` | SQLAlchemy ORM models |
| Validation | `app/schemas.py` | Pydantic validation schemas |
| CRUD Operations | `app/crud.py` | Database queries |
| CSV Import | `app/csv_import.py` | CSV parsing logic |
| AWS Export | `app/services/aws_export.py` | S3 & SNS integration |
| Configuration | `app/config.py` | Settings & environment |
| Exceptions | `app/exceptions.py` | Custom error classes |
| Database Setup | `app/database.py` | SQLAlchemy engine |
| Docker Setup | `docker-compose.yml` | Container orchestration |

## Interview Talking Points

**Async Programming:**
- "This project uses async/await to handle multiple concurrent requests without blocking"
- "asyncpg is a high-performance PostgreSQL driver for Python async"
- "Allows 100 users to be handled in ~1 second instead of 100 seconds"

**Pydantic Validation:**
- "Request bodies are validated against Pydantic schemas before processing"
- "If invalid, returns 422 error automatically"
- "Ensures type safety and consistency"

**CRUD API Design:**
- "RESTful API with standard methods: POST (create), GET (read), PUT (update), DELETE (delete)"
- "Uses HTTP status codes: 201 Created, 404 Not Found, 409 Conflict"
- "Resource-based URLs: `/employees/{id}` not `/getEmployee/{id}`"

**CSV Processing:**
- "Reads CSV file, validates each row, batches inserts"
- "Skips duplicate IDs without stopping import"
- "Reports import summary: imported, skipped, errors"

**Error Handling:**
- "Custom exceptions for domain errors (EmployeeAlreadyExistsError)"
- "Exception handlers convert to appropriate HTTP responses"
- "409 Conflict status for duplicates"

**Database Design:**
- "Single table with simple primary key"
- "Easy to understand, perfect for interviews"
- "Created_at/updated_at for audit trails"

**Docker:**
- "Multi-container setup: PostgreSQL + FastAPI"
- "Health checks ensure database is ready before API starts"
- "Volumes provide persistent data storage"
- "Port mapping exposes services to host machine"

---

## Next Steps

1. **Explore the Code:** Open each file mentioned and read through
2. **Test the APIs:** Use curl or Postman to test endpoints
3. **Check Swagger UI:** Visit http://localhost:8000/docs for interactive docs
4. **Modify & Experiment:** Try adding a new field to Employee schema
5. **Read Error Messages:** Pay attention to validation errors when testing

Good luck with your interview! 🚀

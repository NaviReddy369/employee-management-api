# 🗺️ Code Navigation Map

Quick reference for finding code and understanding flow.

---

# 📁 File-by-File Code Reference

## 1. app/main.py - All API Endpoints

**Size:** ~300 lines | **Read Order:** 1st

### What's in it:
- FastAPI app initialization
- CORS middleware setup
- Exception handlers
- All 7 endpoints

### Key Sections:

| Lines | What | Description |
|-------|------|-------------|
| 1-30 | Imports | All dependencies and models imported |
| 32-40 | Lifespan | Database table creation on startup |
| 42-75 | App Setup | FastAPI app config, CORS, exception handler |
| 78-100 | POST /employees | Create new employee |
| 102-120 | GET /employees/{id} | Get one employee |
| 122-150 | DELETE /employees/{id} | Delete employee |
| 152-175 | PUT /employees/{id} | Update employee |
| 177-200 | GET /employees | List all (with filtering) |
| 195-225 | GET /employees/import/csv/preview | Preview CSV |
| 228-250 | POST /employees/import/csv | Import CSV data |
| 253-273 | GET /employees/export/s3 | Export to S3 |
| 275-290 | Helpers | _to_out(), _resolve_csv_path() |

### How to read it:

```python
@app.post(
    "/employees",           # ← URL endpoint
    response_model=EmployeeOut,  # ← Type of response
    tags=["employees"],     # ← Category in Swagger
    summary="Create employee (POST)",  # ← Description
)
async def post_employee(
    body: EmployeeCreate,   # ← Request body (validated by Pydantic)
    db: Annotated[AsyncSession, Depends(get_db)],  # ← Database dependency
):
    row = await crud.create_employee(db, body)
    return _to_out(row)
```

**Key Pattern:** All endpoints follow this structure
- Decorator with endpoint details
- Async function
- Dependencies injected
- Call to crud module
- Return response

---

## 2. app/models.py - Database Schema

**Size:** ~50 lines | **Read Order:** 2nd

### What's in it:
- SQLAlchemy ORM model for `employees` table
- Column definitions with types

### The Employee Model:

```python
class Employee(Base):
    __tablename__ = "employees"
    
    # Primary Key
    employee_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    
    # Regular Columns
    gender: Mapped[str] = mapped_column(String(1))
    experience_years: Mapped[int] = mapped_column(Integer)
    position: Mapped[str] = mapped_column(String(255))
    salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    
    # Timestamps (auto-managed)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), ...)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), ...)
```

### What to remember:
- `Mapped[type]` = Column type
- `primary_key=True` = Unique identifier
- `autoincrement=False` = Manual ID (from CSV)
- `default=lambda: datetime.now(timezone.utc)` = Auto-set timestamp

---

## 3. app/schemas.py - Request/Response Validation

**Size:** ~150 lines | **Read Order:** 2nd

### What's in it:
- Pydantic models for validation
- Request schemas: EmployeeCreate, EmployeeUpdate
- Response schema: EmployeeOut
- Helper types: GenderEnum, SalaryDecimal

### Key Schemas:

| Schema | Purpose | Usage |
|--------|---------|-------|
| `GenderEnum` | Valid genders | Enum with "F" \| "M" |
| `SalaryDecimal` | Validated salary | Positive decimal |
| `EmployeeCreate` | POST body | All fields required |
| `EmployeeUpdate` | PUT body | All fields optional |
| `EmployeeOut` | Response | What client receives |

### Validation Rules:

```python
class EmployeeCreate(BaseModel):
    EMPLOYEE_ID: int = Field(..., gt=0)
    # Required (...)
    # Must be > 0 (gt=0)
    
    EXPERIENCE_YEARS: int = Field(..., ge=0, le=80)
    # Must be 0-80
    
    POSITION: str = Field(..., min_length=1, max_length=255)
    # 1-255 characters
    
    SALARY: SalaryDecimal = Field(...)
    # Must be positive decimal with 2 places
```

### How validation works:

1. Client sends JSON
2. Pydantic model receives it
3. Validates against rules
4. If valid → creates model instance
5. If invalid → raises ValueError → 422 error

---

## 4. app/crud.py - Database Operations

**Size:** ~100 lines | **Read Order:** 3rd

### What's in it:
- Database queries using SQLAlchemy
- All "CRUD" operations
- Batch operations for CSV import

### Operations:

| Function | SQL | What it does |
|----------|-----|------------|
| `create_employee()` | INSERT | Add new employee |
| `get_employee()` | SELECT WHERE id | Get one employee |
| `delete_employee()` | DELETE WHERE id | Remove employee |
| `update_employee()` | UPDATE WHERE id | Modify employee |
| `list_employees()` | SELECT * | Get all (with optional filters) |
| `count_employees()` | SELECT COUNT(*) | Count employees |
| `import_employees_batch()` | Multiple INSERT | Logic for CSV import |

### Code Pattern:

```python
async def get_employee(db: AsyncSession, employee_id: int) -> Employee | None:
    return await db.get(Employee, employee_id)
    # db.get(Model, primary_key) = query by PK
    # Returns Employee object or None
```

### Async Pattern:

```python
async def create_employee(db: AsyncSession, data: EmployeeCreate) -> Employee:
    existing = await db.get(Employee, data.EMPLOYEE_ID)  # Query
    if existing is not None:
        raise EmployeeAlreadyExistsError(...)
    
    row = Employee(...)
    db.add(row)
    await db.commit()  # Save
    await db.refresh(row)  # Reload
    return row
```

---

## 5. app/csv_import.py - CSV Processing

**Size:** ~60 lines | **Read Order:** 4th

### What's in it:
- Read CSV file
- Parse rows
- Validate each row
- Convert to EmployeeCreate objects

### Main Functions:

```python
def parse_employee_csv(path: Path) -> tuple[list[EmployeeCreate], list[dict], int]:
    # Reads CSV file
    # Returns: (valid_rows, errors, total_count)
    
def row_to_employee_create(row: dict) -> EmployeeCreate:
    # Converts single CSV row to model
    # Handles type conversion and validation
```

### CSV to Python Mapping:

```
CSV column     Python variable  Conversion
─────────────────────────────────────────
ID             rid             int()
Gender         gender          upper()
Experience...  exp             int(float())
Position       pos             .strip()
Salary         sal             keep as string
```

### Error Handling:

```python
for i, row in enumerate(reader, start=2):
    try:
        employee = row_to_employee_create(row)
        valid.append(employee)  # Success
    except (KeyError, ValueError, ValidationError) as e:
        errors.append({"line": i, "error": str(e)})  # Log error
        # Continue to next row
```

---

## 6. app/database.py - Connection Setup

**Size:** ~20 lines | **Read Order:** 5th

### What's in it:
- SQLAlchemy async engine
- Session management
- Database connection

### Code:

```python
# Create engine (connection pool)
engine = create_async_engine(
    settings.database_url,  # postgresql+asyncpg://...
    echo=False,
    pool_pre_ping=True,  # Check connection health
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
)

# Dependency for endpoints
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session  # Provides session to endpoint
        # Auto-closes after endpoint finishes
```

### Key Concepts:

- `engine` = Connection pool (manages connections)
- `AsyncSessionLocal` = Factory to create sessions
- `get_db()` = Dependency injection (FastAPI uses this)
- `yield` = Provides session, cleans up after

---

## 7. app/config.py - Settings

**Size:** ~15 lines | **Read Order:** Reference

### What's in it:
- Environment variables
- Configuration defaults

### Settings:

```python
database_url: str = "postgresql+asyncpg://..."
# How to connect to database

aws_region: str = "us-east-1"
# AWS region for S3/SNS

s3_export_bucket: str = ""
# S3 bucket name (empty = disabled)

sns_topic_arn: str = ""
# SNS topic for notifications

employee_csv_path: str = "employee_data.csv"
# Where CSV file is located
```

### How it works:

```python
settings = Settings()
# Reads from:
# 1. Environment variables (docker-compose env vars)
# 2. .env file (if exists)
# 3. Default values

# In code:
DATABASE_URL = settings.database_url
```

---

## 8. app/exceptions.py - Custom Errors

**Size:** ~10 lines | **Read Order:** Reference

### What's in it:
- Custom exception classes
- Domain-specific errors

### Custom Exception:

```python
class EmployeeAlreadyExistsError(Exception):
    def __init__(self, employee_id: int, position: str):
        self.employee_id = employee_id
        self.position = position
        super().__init__(f"Employee ID {employee_id} already exists...")
```

### How it's used:

```python
# In crud.py
if existing is not None:
    raise EmployeeAlreadyExistsError(
        employee_id=data.EMPLOYEE_ID,
        position=existing.position,
    )

# In main.py
@app.exception_handler(EmployeeAlreadyExistsError)
async def employee_exists_handler(_, exc):
    return JSONResponse(
        status_code=409,  # HTTP Conflict
        content={...}
    )
```

---

## 9. app/services/aws_export.py - AWS Integration

**Size:** ~50 lines | **Read Order:** Reference

### What's in it:
- S3 upload logic
- SNS notification logic

### Main Function:

```python
def export_employees_json_to_s3_and_notify(employees_payload: list[dict]):
    # Step 1: Create filename with timestamp
    # Step 2: Convert to JSON string
    # Step 3: Upload to S3
    # Step 4: Publish SNS message
    # Return: (s3_uri, sns_message_id)
```

### Flow:

```
Employees List
    ↓
JSON String
    ↓
S3 Upload
    ↓
SNS Notification
    ↓
Response (s3_uri, msg_id)
```

---

# 🔄 Request Flow Diagrams

## Flow 1: Create Employee (POST /employees)

```
┌─────────────────────────────────────────────────────┐
│ Client sends: curl -X POST /employees               │
│ Body: {"EMPLOYEE_ID": 1, "GENDER": "F", ...}       │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ FastAPI in main.py                                  │
│ @app.post("/employees")                             │
│ async def post_employee(body: EmployeeCreate, ...)  │
└─────────────────────────────────────────────────────┘
                          ↓
                   [PYDANTIC]
┌─────────────────────────────────────────────────────┐
│ Validate body against EmployeeCreate schema         │
│ - Check types                                       │
│ - Check constraints (EMPLOYEE_ID > 0, etc.)        │
│ - Convert types if needed                          │
│ If invalid → Return 422 error                       │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ call crud.create_employee(db, body)                 │
│ in app/crud.py                                      │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ Check if employee_id already exists                 │
│ existing = await db.get(Employee, EMPLOYEE_ID)     │
│ if existing → raise EmployeeAlreadyExistsError     │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ Create Employee ORM object                          │
│ row = Employee(employee_id=1, gender="F", ...)     │
│ db.add(row)                                         │
│ await db.commit()                                   │
│ await db.refresh(row)                              │
└─────────────────────────────────────────────────────┘
                          ↓
                     [DATABASE]
┌─────────────────────────────────────────────────────┐
│ PostgreSQL executes:                                │
│ INSERT INTO employees                               │
│ VALUES (1, 'F', ..., NOW(), NOW())                  │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ Return Employee object to main.py                   │
│ Convert to JSON using _to_out()                     │
│ Response: 201 Created + JSON body                   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ Client receives JSON:                               │
│ {                                                   │
│   "employee_id": 1,                                 │
│   "gender": "F",                                    │
│   ...                                               │
│   "created_at": "2026-04-07T15:30:00+00:00"        │
│ }                                                   │
└─────────────────────────────────────────────────────┘
```

## Flow 2: Import CSV (POST /employees/import/csv)

```
┌─────────────────────────────────────────────────────┐
│ Client sends: curl -X POST /employees/import/csv    │
│ No body required                                    │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ main.py - import_employee_csv()                     │
│ path = _resolve_csv_path()                          │
│ items, parse_errors, counted = parse_employee_csv() │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ csv_import.py - parse_employee_csv()                │
│ Open employee_data.csv                              │
│ For each row:                                       │
│   - Validate columns exist                          │
│   - Convert types (string → int, etc.)              │
│   - Create EmployeeCreate object                    │
│   - If error, log it                                │
│ Return (valid_rows, errors, total_count)            │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ back in main.py                                     │
│ call crud.import_employees_batch(db, items)        │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ crud.py - import_employees_batch()                  │
│ For each EmployeeCreate object:                     │
│   - Try: await create_employee(db, data)            │
│   - Success → imported++                            │
│   - EmployeeAlreadyExistsError → skipped++          │
│   - Other error → row_errors.append()               │
│ Return (imported_count, skipped_count, errors)      │
└─────────────────────────────────────────────────────┘
                          ↓
                     [DATABASE]
┌─────────────────────────────────────────────────────┐
│ For each valid object from CSV:                     │
│ INSERT INTO employees VALUES (...)                  │
│ (49 inserts total from CSV)                         │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ Client receives JSON:                               │
│ {                                                   │
│   "total_rows_in_file": 49,                         │
│   "imported": 49,                                   │
│   "skipped": 0,                                     │
│   "errors": []                                      │
│ }                                                   │
└─────────────────────────────────────────────────────┘
```

---

# 🎯 Finding Code by Feature

### "I want to find..."

**...how employees are created**
1. Go to `app/main.py` (lines 78-100)
2. Look at `post_employee()` function
3. It calls `crud.create_employee()` in `app/crud.py` (lines 11-26)

**...how validation works**
1. Go to `app/schemas.py`
2. Look at any model class (EmployeeCreate, EmployeeUpdate, etc.)
3. See the Field() constraints

**...how CSV is imported**
1. Go to `app/main.py` (lines 228-250)
2. Look at `import_employee_csv()` endpoint
3. It calls `parse_employee_csv()` in `app/csv_import.py`
4. Which calls `row_to_employee_create()` for conversion

**...how database queries work**
1. Go to `app/crud.py`
2. Each function (get_employee, list_employees, etc.) shows query pattern
3. Uses SQLAlchemy with `await` for async

**...how errors are handled**
1. Custom exceptions in `app/exceptions.py`
2. Error handlers in `app/main.py` (around line 67)
3. Returns appropriate HTTP error codes

**...database connection setup**
1. `app/database.py` - Creates engine and session factory
2. `app/config.py` - Configuration/connection string

**...API documentation**
1. `app/main.py` - Top of file with FastAPI app() call
2. Each endpoint has tags, summary, description

**...AWS integration**
1. `app/services/aws_export.py` - S3 upload and SNS notify
2. Called from main.py endpoint (lines 253-273)

---

# 📝 Code Reading Order for Learning

0. **Start:** `app/config.py` (2 min) - Understand settings
1. **First:** `app/models.py` (3 min) - See database structure
2. **Second:** `app/schemas.py` (5 min) - Validation rules
3. **Third:** `app/main.py` (10 min) - All endpoints
4. **Fourth:** `app/crud.py` (5 min) - Database operations
5. **Fifth:** `app/csv_import.py` (3 min) - CSV logic
6. **Sixth:** `app/database.py` (2 min) - Connection setup
7. **Reference:** `docker-compose.yml` (3 min) - Infrastructure
8. **Advanced:** `app/services/aws_export.py` (3 min) - Cloud integration

**Total:** ~35 minutes to understand entire codebase

---

# 🔍 Key Code Patterns

### Pattern 1: Async Database Query

```python
async def get_employee(db: AsyncSession, employee_id: int) -> Employee | None:
    return await db.get(Employee, employee_id)
    
# Always:
# - Use "async def"
# - Use "await" for database calls
# - No blocking operations
```

### Pattern 2: Pydantic Validation

```python
@app.post("/employees")
async def post_employee(
    body: EmployeeCreate,  # ← Pydantic validates here
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # body is guaranteed valid at this point
    row = await crud.create_employee(db, body)
    return row
```

### Pattern 3: Error Handling

```python
# Raise custom exception
if employee_exists:
    raise EmployeeAlreadyExistsError(id, position)

# In main.py, convert to HTTP response
@app.exception_handler(EmployeeAlreadyExistsError)
async def handler(_, exc):
    return JSONResponse(status_code=409, content={...})
```

### Pattern 4: Dependency Injection

```python
@app.get("/employees")
async def list_employees(
    db: Annotated[AsyncSession, Depends(get_db)],
    # ↑ FastAPI provides db session automatically
):
    return await crud.list_employees(db)
```

### Pattern 5: Batch Operations

```python
for item in items:
    try:
        # Try operation
        result = await operation(db, item)
        success_count += 1
    except SpecificError:
        # Expected error - skip
        skip_count += 1
    except Exception as e:
        # Unexpected - record
        errors.append({"item_id": item.id, "error": str(e)})

return success_count, skip_count, errors
```

---

Now you can navigate the codebase with confidence! 🚀

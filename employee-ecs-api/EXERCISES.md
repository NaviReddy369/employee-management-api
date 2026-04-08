# 🧪 Practical Exercises & Test Commands

This file contains hands-on exercises you can run to test each concept.

## Prerequisites

Ensure your containers are running:
```powershell
cd c:\Users\gudim\employee-ecs-api
docker-compose up --build
```

Check containers are running:
```powershell
docker-compose ps
# Should see:
# NAME                COMMAND                 STATUS
# postgres container  postgres                Up (healthy)
# python container    uvicorn app.main:app    Up
```

---

# 1️⃣ CRUD API Exercises

## Exercise 1.1: Create an Employee (POST)

**Goal:** Test creating a new employee with valid data

```powershell
# Create employee
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 100,
    "GENDER": "M",
    "EXPERIENCE_YEARS": 8,
    "POSITION": "Cloud Architect",
    "SALARY": "180000.00"
  }'

# Expected Response (201 Created):
# {
#   "employee_id": 100,
#   "gender": "M",
#   "experience_years": 8,
#   "position": "Cloud Architect",
#   "salary": "180000.00",
#   "created_at": "2026-04-07T16:30:00+00:00",
#   "updated_at": "2026-04-07T16:30:00+00:00"
# }
```

✅ **What to notice:**
- Status code is 201 (Created)
- `created_at` is automatically set to now
- `updated_at` is same as created_at initially

## Exercise 1.2: Create Duplicate Employee (POST - Should Fail)

**Goal:** Test error handling for duplicate IDs

```powershell
# Try to create same employee again
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 100,
    "GENDER": "F",
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Different Position",
    "SALARY": "100000.00"
  }'

# Expected Response (409 Conflict):
# {
#   "detail": "Employee ID 100 already exists (Position: Cloud Architect)",
#   "employee_id": 100,
#   "existing_position": "Cloud Architect"
# }
```

✅ **What to notice:**
- Status code is 409 (Conflict)
- Custom exception caught and converted to HTTP error
- Response includes employee_id and existing_position

## Exercise 1.3: Invalid Data - Negative Salary (POST - Should Fail)

**Goal:** Test Pydantic validation

```powershell
# Try negative salary
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 101,
    "GENDER": "F",
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Engineer",
    "SALARY": "-50000.00"
  }'

# Expected Response (422 Unprocessable Entity):
# {
#   "detail": [
#     {
#       "type": "greater_than",
#       "loc": ["body", "SALARY"],
#       "msg": "Input should be greater than 0",
#       ...
#     }
#   ]
# }
```

✅ **What to notice:**
- Status code is 422 (Validation Error)
- Pydantic automatically validates
- Error explains exactly what's wrong

## Exercise 1.4: Invalid Data - Bad Gender (POST - Should Fail)

**Goal:** Test enum validation

```powershell
# Try invalid gender
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 102,
    "GENDER": "X",
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Engineer",
    "SALARY": "100000.00"
  }'

# Expected Response (422):
# Error about invalid gender value
```

## Exercise 1.5: Get Single Employee (GET)

**Goal:** Test retrieving one employee by ID

```powershell
# Get employee we created
curl http://localhost:8000/employees/100

# Expected Response (200 OK):
# {
#   "employee_id": 100,
#   "gender": "M",
#   "experience_years": 8,
#   "position": "Cloud Architect",
#   "salary": "180000.00",
#   "created_at": "2026-04-07T16:30:00+00:00",
#   "updated_at": "2026-04-07T16:30:00+00:00"
# }
```

## Exercise 1.6: Get Non-Existent Employee (GET - Should Fail)

**Goal:** Test 404 error

```powershell
# Try to get employee that doesn't exist
curl http://localhost:8000/employees/99999

# Expected Response (404 Not Found):
# {
#   "detail": "Employee not found"
# }
```

## Exercise 1.7: List All Employees (GET)

**Goal:** Test listing with filtering

```powershell
# Get all employees
curl "http://localhost:8000/employees"

# Expected Response: Array of all employees

# Filter by year
curl "http://localhost:8000/employees?year=2026"

# Filter by year and month
curl "http://localhost:8000/employees?year=2026&month=4"
```

✅ **What to notice:**
- Employees imported from CSV appear
- Your newly created employee 100 also appears
- Filtering works by creation date

## Exercise 1.8: Update Employee (PUT)

**Goal:** Test partial update

```powershell
# Update only position and salary (don't change gender)
curl -X PUT http://localhost:8000/employees/100 `
  -H "Content-Type: application/json" `
  -d '{
    "POSITION": "Principal Cloud Architect",
    "SALARY": "200000.00"
  }'

# Expected Response (200 OK):
# {
#   "employee_id": 100,
#   "gender": "M",
#   "experience_years": 8,
#   "position": "Principal Cloud Architect",
#   "salary": "200000.00",
#   "created_at": "2026-04-07T16:30:00+00:00",
#   "updated_at": "2026-04-07T16:30:10+00:00"  ⬅️ Changed!
# }
```

✅ **What to notice:**
- `updated_at` timestamp changed
- `created_at` stayed the same
- Gender unchanged (we didn't provide it)

## Exercise 1.9: Delete Employee (DELETE)

**Goal:** Test deletion

```powershell
# Delete the employee
curl -X DELETE http://localhost:8000/employees/100

# Expected Response (204 No Content):
# (empty body)
```

Then verify it's deleted:
```powershell
curl http://localhost:8000/employees/100

# Expected Response (404):
# {
#   "detail": "Employee not found"
# }
```

---

# 2️⃣ Async/Await Exercises

## Exercise 2.1: Observe Concurrent Requests

**Goal:** See async handling multiple requests at once

```powershell
# Terminal 1: Create 5 employees rapidly
$employees = 201..205
foreach ($id in $employees) {
    curl -X POST http://localhost:8000/employees `
      -H "Content-Type: application/json" `
      -d "{
        \"EMPLOYEE_ID\": $id,
        \"GENDER\": \"M\",
        \"EXPERIENCE_YEARS\": 5,
        \"POSITION\": \"Engineer\",
        \"SALARY\": \"100000.00\"
      }" | Write-Host "Created: $id"
}

# All created quickly (async handling!)
# If this was blocking, each would take time
```

## Exercise 2.2: Check Database Response Time

**Goal:** Notice fast responses from database

```powershell
# Get all employees (49 in database)
Measure-Command {
    curl http://localhost:8000/employees | Out-Null
}

# Response time: Usually < 100ms
# With 100 concurrent users, still ~100ms (async!)
# Without async: would be seconds
```

---

# 3️⃣ Pydantic Validation Exercises

## Exercise 3.1: Type Coercion

**Goal:** See Pydantic convert types intelligently

```powershell
# Send experience as string "10" (not integer)
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 206,
    "GENDER": "F",
    "EXPERIENCE_YEARS": "10",
    "POSITION": "Engineer",
    "SALARY": "100000.00"
  }'

# ✅ Works! Pydantic converts string "10" to int 10
# Response includes: "experience_years": 10
```

## Exercise 3.2: Salary Type Conversion

**Goal:** See Pydantic handle decimal conversion

```powershell
# Send salary as string
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 207,
    "GENDER": "M",
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Engineer",
    "SALARY": "123456.78"
  }'

# ✅ Pydantic converts and validates decimal
# Respons includes: "salary": "123456.78"
```

## Exercise 3.3: Validation Constraint - Experience Range

**Goal:** Test min/max constraints

```powershell
# Try experience_years > 80
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 208,
    "GENDER": "M",
    "EXPERIENCE_YEARS": 100,
    "POSITION": "Engineer",
    "SALARY": "100000.00"
  }'

# ❌ 422 Error: experience_years must be <= 80
```

## Exercise 3.4: Validation Constraint - Position Length

**Goal:** Test string length constraints

```powershell
# Try empty position
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 209,
    "GENDER": "M",
    "EXPERIENCE_YEARS": 5,
    "POSITION": "",
    "SALARY": "100000.00"
  }'

# ❌ 422 Error: position must have at least 1 character
```

---

# 4️⃣ CSV Import Exercises

## Exercise 4.1: Preview CSV

**Goal:** See how CSV will be imported without importing

```powershell
curl http://localhost:8000/employees/import/csv/preview

# Response shows:
# {
#   "path": "C:\\Users\\gudim\\employee-ecs-api\\employee_data.csv",
#   "total_rows": 49,
#   "sample": [
#     {"EMPLOYEE_ID": 1, "GENDER": "F", ...},
#     {"EMPLOYEE_ID": 2, "GENDER": "M", ...},
#     ...
#   ]
# }
```

✅ **What to notice:**
- Shows first 5 rows only
- Total row count: 49 employees
- CSV mapping is correct (ID → EMPLOYEE_ID, etc.)

## Exercise 4.2: First Import

**Goal:** Import the CSV data for the first time

```powershell
# Fresh database (or after docker-compose down -v)
curl -X POST http://localhost:8000/employees/import/csv

# Response:
# {
#   "path": "C:\\...",
#   "total_rows_in_file": 49,
#   "imported": 49,
#   "skipped": 0,
#   "errors": []
# }
```

✅ **What to notice:**
- All 49 rows imported
- No skips or errors
- Database now has employees 1-49 from CSV

## Exercise 4.3: Second Import (Duplicate Handling)

**Goal:** See how duplicates are handled

```powershell
# Import again
curl -X POST http://localhost:8000/employees/import/csv

# Response:
# {
#   "path": "C:\\...",
#   "total_rows_in_file": 49,
#   "imported": 0,
#   "skipped": 49,
#   "errors": []
# }
```

✅ **What to notice:**
- No new rows imported
- All 49 skipped (already exist)
- No errors (skipping is expected behavior)
- Database still has 49 employees total

## Exercise 4.4: Verify Import Data

**Goal:** Confirm employees were imported correctly

```powershell
# List all
curl http://localhost:8000/employees | ConvertFrom-Json | Select-Object -First 5

# Or get specific employee from CSV
curl http://localhost:8000/employees/1

# Response should match employee_data.csv row 1:
# {
#   "employee_id": 1,
#   "gender": "F",
#   "experience_years": 4,
#   "position": "DevOps Engineer",
#   "salary": "109976.00",
#   ...
# }
```

---

# 5️⃣ Error Handling Exercises

## Exercise 5.1: 409 Conflict Error

**Goal:** Trigger duplicate employee error

```powershell
# Try to create employee 1 (already exists from import)
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 1,
    "GENDER": "M",
    "EXPERIENCE_YEARS": 10,
    "POSITION": "New Position",
    "SALARY": "150000.00"
  }'

# Response (409 Conflict):
# {
#   "detail": "Employee ID 1 already exists (Position: DevOps Engineer)",
#   "employee_id": 1,
#   "existing_position": "DevOps Engineer"
# }
```

## Exercise 5.2: 404 Not Found

**Goal:** Try to get non-existent employee

```powershell
curl http://localhost:8000/employees/99999

# Response (404):
# {
#   "detail": "Employee not found"
# }
```

## Exercise 5.3: 422 Validation Error

**Goal:** Send invalid data

```powershell
# Missing GENDER field
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 300,
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Engineer",
    "SALARY": "100000.00"
  }'

# Response (422):
# Pydantic error about missing GENDER
```

---

# 6️⃣ Database & ORM Exercises

## Exercise 6.1: Check Database Contents

**Goal:** Direct database inspection

```powershell
# Connect to PostgreSQL inside container
docker-compose exec db psql -U postgres -d employees

# Inside psql shell:
SELECT COUNT(*) FROM employees;
# Shows: 49+ (original CSV + any you created)

SELECT * FROM employees LIMIT 5;
# Shows first 5 employees

# Find employee with high salary:
SELECT employee_id, position, salary FROM employees ORDER BY salary DESC LIMIT 5;

# Exit psql
\q
```

## Exercise 6.2: Check Timestamps

**Goal:** Verify created_at and updated_at

```powershell
# Get employee (shows timestamps in API response)
curl http://localhost:8000/employees/1

# Check database directly
docker-compose exec db psql -U postgres -d employees -c "SELECT employee_id, created_at, updated_at FROM employees WHERE employee_id = 1;"
```

## Exercise 6.3: Create and Update Timestamps

**Goal:** See timestamps change

```powershell
# Create new employee
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{
    "EMPLOYEE_ID": 350,
    "GENDER": "F",
    "EXPERIENCE_YEARS": 5,
    "POSITION": "Test Engineer",
    "SALARY": "100000.00"
  }' | ConvertFrom-Json | Select-Object -Property employee_id, created_at, updated_at

# Output example:
# employee_id created_at                   updated_at
# ----------- ----------                   ----------
# 350         2026-04-07T16:45:00+00:00   2026-04-07T16:45:00+00:00

# Wait 5 seconds, then update
Start-Sleep -Seconds 5

curl -X PUT http://localhost:8000/employees/350 `
  -H "Content-Type: application/json" `
  -d '{"POSITION": "Senior Test Engineer"}' | ConvertFrom-Json | Select-Object -Property employee_id, created_at, updated_at

# Output:
# employee_id created_at                   updated_at
# ----------- ----------                   ----------
# 350         2026-04-07T16:45:00+00:00   2026-04-07T16:45:05+00:00
#                         ↑ Same!                       ↑ Changed!
```

---

# 7️⃣ API Documentation

## Exercise 7.1: Interactive API Docs

**Goal:** Use Swagger UI for testing

```
Open browser: http://localhost:8000/docs

- See all endpoints
- Click "Try it out" on any endpoint
- Fill in request body
- Execute and see response
- Check status codes and response times
```

## Exercise 7.2: Alternative Documentation

**Goal:** Try ReDoc format

```
Open browser: http://localhost:8000/redoc

- Alternative documentation format
- Read-only (no testing)
- Good for reviewing API spec
```

---

# 📊 Performance Testing

## Exercise 8.1: Concurrent Requests with Async

**Goal:** Demonstrate async advantage

```powershell
# Create 20 employees concurrently
Measure-Command {
    1..20 | ForEach-Object {
        curl -X POST http://localhost:8000/employees `
          -H "Content-Type: application/json" `
          -d "{
            \"EMPLOYEE_ID\": $($_+400),
            \"GENDER\": \"M\",
            \"EXPERIENCE_YEARS\": 5,
            \"POSITION\": \"Engineer\",
            \"SALARY\": \"100000.00\"
          }" | Out-Null
    }
}

# Should complete in ~2-3 seconds
# Without async: would be ~20+ seconds (sequential)
```

## Exercise 8.2: Query Performance

**Goal:** See query response times

```powershell
# Large list query
Measure-Command {
    curl http://localhost:8000/employees | Out-Null
}
# Typical: <100ms

# Single employee lookup
Measure-Command {
    curl http://localhost:8000/employees/1 | Out-Null
}
# Typical: <50ms (primary key index)
```

---

# 📋 Docker Exercises

## Exercise 9.1: Check Docker Compose Status

**Goal:** Verify containers are running

```powershell
docker-compose ps

# Output:
# NAME              COMMAND                     STATUS
# api               uvicorn app.main:app...    Up
# db                postgres                    Up (healthy)
```

## Exercise 9.2: View Logs

**Goal:** Debug by checking logs

```powershell
# API logs
docker-compose logs api

# Database logs
docker-compose logs db

# Follow logs (live)
docker-compose logs -f api

# Exit: Ctrl+C
```

## Exercise 9.3: Connect to Database Container

**Goal:** Access PostgreSQL directly

```powershell
# Enter PostgreSQL shell
docker-compose exec db psql -U postgres -d employees

# Now inside container:
postgres=# SELECT COUNT(*) FROM employees;
postgres=# \dt  (show tables)
postgres=# \q   (quit)
```

## Exercise 9.4: View Environment Variables

**Goal:** See how configuration is set

```powershell
# Inside API container
docker-compose exec api printenv | findstr DATABASE

# Output:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/employees
#
# Note: @db = Docker DNS to db container
```

---

# 🎯 Interview Preparation Exercises

## Interview Q1: Explain Async

**Exercise:** Run concurrent requests and measure time

```powershell
# What to say:
# "This project uses async/await to handle requests concurrently.
#  Python's asyncpg driver allows non-blocking database operations.
#  Multiple users can be handled simultaneously without blocking."

# Demonstrate:
Measure-Command {
    1..10 | % { curl http://localhost:8000/employees | Out-Null }
}
# Should be ~100ms, not 1 second per request
```

## Interview Q2: Explain REST API Design

**Exercise:** Walk through CRUD operations

```powershell
# POST (Create)
curl -X POST http://localhost:8000/employees -d '{...}'

# GET (Read)
curl http://localhost:8000/employees
curl http://localhost:8000/employees/1

# PUT (Update)
curl -X PUT http://localhost:8000/employees/1 -d '{...}'

# DELETE (Delete)
curl -X DELETE http://localhost:8000/employees/1

# What to say:
# "This project follows REST conventions:
#  - Resource-based URLs (/employees, /employees/{id})
#  - Standard HTTP methods (POST, GET, PUT, DELETE)
#  - Appropriate status codes (201 Created, 404 Not Found, 409 Conflict)
#  - Request/response use JSON with Pydantic validation"
```

## Interview Q3: Describe Error Handling

**Exercise:** Trigger different errors

```powershell
# 409 Conflict - Duplicate
curl -X POST http://localhost:8000/employees -d '{"EMPLOYEE_ID": 1, ...}'

# 404 Not Found - Missing
curl http://localhost:8000/employees/99999

# 422 Validation - Bad data
curl -X POST http://localhost:8000/employees -d '{"EMPLOYEE_ID": "abc", ...}'

# What to say:
# "Error handling is done at multiple levels:
#  - Pydantic validates request bodies (422 if invalid)
#  - Custom exceptions for business logic (409 Conflict for duplicates)
#  - Exception handlers convert to HTTP responses
#  - Appropriate status codes for different scenarios"
```

---

# 🔍 Debugging Checklist

If something doesn't work:

```powershell
# 1. Check Docker status
docker-compose ps
# PostgreSQL should be "healthy"

# 2. Check logs
docker-compose logs api
docker-compose logs db

# 3. Test API connectivity
curl http://localhost:8000/employees
# Should work if API running

# 4. Verify database
docker-compose exec db psql -U postgres -d employees -c "SELECT COUNT(*) FROM employees;"

# 5. Restart if needed
docker-compose down
docker-compose up --build

# 6. Check port conflicts
# If ports 8000 or 5432 already in use, may cause issues
```

---

Now go explore! 🚀

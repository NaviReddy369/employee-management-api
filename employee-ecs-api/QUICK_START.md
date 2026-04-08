# ⚡ Quick Start Reference

**Bookmark this page!** Quick answers to common questions.

---

## 🚀 Getting Started (5 minutes)

### 1. Start Docker
```powershell
cd c:\Users\gudim\employee-ecs-api
docker-compose up --build
```

### 2. Wait for startup
```
✅ "db" service: "service_healthy"
✅ "api" service: "Up"
```

### 3. Access the API
```
Browser: http://localhost:8000/docs
API: http://localhost:8000
Database: localhost:5432
```

---

## 📚 Documentation Files Created

| File | Purpose | Read Time |
|------|---------|-----------|
| **LEARNING_GUIDE.md** | Complete explanation of all 8 concepts | 45 min |
| **EXERCISES.md** | Hands-on exercises with commands | 30 min |
| **CODE_NAVIGATION.md** | Find code by feature/topic | Reference |
| **This file** | Quick answers | 5 min |

---

## 🎯 Common Questions & Answers

### Q: What is this project?
**A:** REST API for managing employees in a database, demonstrating modern Python backend patterns.

### Q: What language?
**A:** Python with FastAPI framework

### Q: What database?
**A:** PostgreSQL (in Docker)

### Q: How do I start?
**A:** `docker-compose up --build` then visit http://localhost:8000/docs

### Q: How do I test APIs?
**A:** Use Swagger UI at http://localhost:8000/docs or curl commands

### Q: How do I understand async?
**A:** Read **LEARNING_GUIDE.md → Section 2** (explains with examples)

### Q: What are REST conventions?
**A:** Read **LEARNING_GUIDE.md → Section 1** or run exercises in **EXERCISES.md → 1️⃣**

### Q: How do I learn about Pydantic?
**A:** Read **LEARNING_GUIDE.md → Section 3** or run exercises in **EXERCISES.md → 3️⃣**

### Q: Where do I find code?
**A:** Use **CODE_NAVIGATION.md** file

### Q: How does CSV import work?
**A:** Read **LEARNING_GUIDE.md → Section 6** or run exercises in **EXERCISES.md → 4️⃣**

### Q: What about AWS?
**A:** Read **LEARNING_GUIDE.md → Section 7** (currently disabled in dev)

### Q: How does Docker work?
**A:** Read **LEARNING_GUIDE.md → Section 8**

---

## 🔧 Common Commands

### Start/Stop
```powershell
docker-compose up --build        # Start from scratch
docker-compose up                # Just start
docker-compose down              # Stop (keep data)
docker-compose down -v           # Stop (delete data)
```

### View Status
```powershell
docker-compose ps                # See running containers
docker-compose logs api          # View API logs
docker-compose logs -f db        # View DB logs (live)
```

### Access Database
```powershell
docker-compose exec db psql -U postgres -d employees
# Inside psql:
SELECT * FROM employees;
\dt
\q (quit)
```

### Test APIs (choose one method)

**Method 1: curl (command line)**
```powershell
curl http://localhost:8000/employees
curl -X POST http://localhost:8000/employees -d '{"EMPLOYEE_ID": 1, ...}'
```

**Method 2: Swagger UI (browser)**
Visit: http://localhost:8000/docs

**Method 3: ReDoc (read-only)**
Visit: http://localhost:8000/redoc

---

## 📊 Project Architecture at a Glance

```
Client Request
    ↓
FastAPI (app/main.py)
    ↓
Pydantic Validation (app/schemas.py)
    ↓
CRUD Operations (app/crud.py)
    ↓
SQLAlchemy ORM (app/models.py)
    ↓
PostgreSQL Database
```

---

## 🎓 Interview Talking Points (2-3 min)

### Async Programming
"Request handling is asynchronous. Multiple requests are handled concurrently without blocking. The asyncpg driver enables non-blocking PostgreSQL queries, so 100 concurrent users experience response time of ~100ms instead of 100+ seconds."

### REST API Design
"This API follows REST conventions with resource-based URLs like `/employees` and `/employees/{id}`, standard HTTP methods (POST/GET/PUT/DELETE), and appropriate status codes (201 Created, 404 Not Found, 409 Conflict)."

### Data Validation
"Pydantic validates all incoming requests before processing. If data is invalid, returns 422 error immediately. Ensures type safety and consistency. Invalid data never reaches the database."

### Error Handling
"Custom exceptions for domain logic (e.g., EmployeeAlreadyExistsError) are caught and converted to appropriate HTTP responses. Different errors return different status codes for client clarity."

### CSV Processing
"Reads CSV file, validates each row, and batches inserts into database. Automatically skips duplicate IDs without stopping. Reports import summary: imported count, skipped count, and any errors."

### Database Design
"Single table with simple primary key design. Perfect for interviews. Includes timestamps (created_at, updated_at) for audit trails. Easy to understand but scalable patterns."

### Async ORM
"SQLAlchemy 2.0 with asyncpg allows non-blocking database operations. All queries use await keyword to allow concurrent request handling."

### Docker
"Multi-container setup with PostgreSQL and FastAPI in separate containers. Health checks ensure database is ready before API starts. Volumes provide persistent data storage."

---

## 🧪 Quick Test Sequence

**5-minute hands-on test:**

```powershell
# 1. Create employee
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{"EMPLOYEE_ID":100,"GENDER":"F","EXPERIENCE_YEARS":5,"POSITION":"Engineer","SALARY":"100000"}'

# 2. Get it back
curl http://localhost:8000/employees/100

# 3. Update it
curl -X PUT http://localhost:8000/employees/100 `
  -H "Content-Type: application/json" `
  -d '{"POSITION":"Senior Engineer"}'

# 4. List all
curl http://localhost:8000/employees | more

# 5. Delete it
curl -X DELETE http://localhost:8000/employees/100

# 6. Verify deleted (should get 404)
curl http://localhost:8000/employees/100
```

---

## 📋 8 Concepts Quick Reference

| # | Concept | File | Key Code |
|---|---------|------|----------|
| 1 | CRUD API | main.py | @app.post/get/put/delete |
| 2 | Async | crud.py | async def + await |
| 3 | Validation | schemas.py | Pydantic models |
| 4 | Database | models.py | SQLAlchemy ORM |
| 5 | Error Handling | exceptions.py | raise EmployeeAlreadyExistsError |
| 6 | CSV Processing | csv_import.py | parse_employee_csv() |
| 7 | AWS | services/aws_export.py | boto3 S3/SNS |
| 8 | Docker | docker-compose.yml | Multi-container setup |

---

## 🚨 Troubleshooting

### API not responding
```powershell
docker-compose ps
# If api container is not "Up", check logs:
docker-compose logs api
```

### Port already in use
```powershell
# If port 8000 or 5432 already in use, stop other services
docker-compose down
# free up ports then:
docker-compose up --build
```

### Database connection error
```powershell
# Database might not be ready yet
# Wait 15 seconds and try again
# Check health:
docker-compose exec db pg_isready -U postgres -d employees
```

### "Cannot import module"
```powershell
# Dependencies not installed
# Rebuild container:
docker-compose down
docker-compose up --build
```

### Data not persisting
```powershell
# Check volume exists:
docker-compose ps
# Volumes should mount pgdata

# Backup data before deleting:
docker-compose exec db pg_dump -U postgres employees > backup.sql
```

---

## 📖 Reading Roadmap

**If you have 30 minutes:**
1. Read this file (5 min)
2. Read LEARNING_GUIDE.md Section 1 (10 min)
3. Try EXERCISES.md Section 1 (15 min)

**If you have 1 hour:**
1. Read this file (5 min)
2. Read LEARNING_GUIDE.md Sections 1-4 (20 min)
3. Try EXERCISES.md Sections 1-3 (35 min)

**If you have 2 hours:**
1. Read LEARNING_GUIDE.md completely (45 min)
2. Try EXERCISES.md completely (60 min)
3. Read CODE_NAVIGATION.md (15 min)

**Full Deep Dive (4 hours):**
1. Read LEARNING_GUIDE.md (45 min)
2. Try EXERCISES.md (60 min)
3. Read CODE_NAVIGATION.md (15 min)
4. Modify code - add a new field to Employee (60 min)

---

## 🎯 Interview Preparation Checklist

- [ ] Understand REST conventions (POST/GET/PUT/DELETE)
- [ ] Explain why async matters (concurrent requests)
- [ ] Know how Pydantic validates data
- [ ] Understand database schema (single table, PK)
- [ ] Explain error handling (409 Conflict)
- [ ] Know CSV processing flow (parse, validate, batch)
- [ ] Understand Docker multi-container setup
- [ ] Familiar with async/await pattern in Python
- [ ] Can explain the project in 2-3 minutes
- [ ] Can draw architecture diagram on whiteboard

---

## 🔗 File Map

```
employee-ecs-api/
├── 📄 LEARNING_GUIDE.md          ← START HERE (READ FIRST)
├── 📄 EXERCISES.md               ← HANDS-ON TESTS
├── 📄 CODE_NAVIGATION.md         ← FIND CODE
├── 📄 QUICK_START.md             ← THIS FILE
│
├── docker-compose.yml            ← Infrastructure
├── Dockerfile                    ← Container image
├── requirements.txt              ← Dependencies
├── employee_data.csv             ← Sample data
│
└── app/
    ├── main.py                   ← All endpoints (START CODE HERE)
    ├── models.py                 ← Database schema
    ├── schemas.py                ← Pydantic validation
    ├── crud.py                   ← Database operations
    ├── csv_import.py             ← CSV processing
    ├── database.py               ← Connection setup
    ├── config.py                 ← Settings
    ├── exceptions.py             ← Custom errors
    └── services/
        └── aws_export.py         ← S3/SNS integration
```

---

## 💡 Key Takeaways

1. **Async/Await** - Enables high concurrency (100 users in ~100ms)
2. **Pydantic** - Validates all inputs automatically (no bad data)
3. **REST API** - Follows conventions for familiar, scalable API
4. **ORM** - SQLAlchemy handles database operations elegantly
5. **Error Handling** - Custom exceptions → appropriate HTTP codes
6. **CSV Batch** - Processes files efficiently, skips duplicates
7. **Docker** - Containerized, reproducible environment
8. **PostgreSQL** - Reliable database with async driver

---

## 📞 Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLAlchemy Async:** https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html
- **Pydantic:** https://docs.pydantic.dev/
- **asyncpg:** https://github.com/MagicStack/asyncpg
- **Docker:** https://docs.docker.com/

---

## ✅ Quick Validation

Run this to confirm everything works:

```powershell
# 1. Check containers running
docker-compose ps
# Should show both "api" and "db" as "Up"

# 2. Test API
curl http://localhost:8000/employees | more
# Should return JSON list of employees

# 3. Check database
docker-compose exec db psql -U postgres -d employees -c "SELECT COUNT(*) FROM employees;"
# Should return employee count (49+)

# 4. One API test
curl -X POST http://localhost:8000/employees `
  -H "Content-Type: application/json" `
  -d '{"EMPLOYEE_ID":999,"GENDER":"M","EXPERIENCE_YEARS":5,"POSITION":"Test","SALARY":"100000"}'
# Should return 201 Created

echo "✅ All systems go!"
```

---

## 🎓 Next Steps

1. **Now:** Open http://localhost:8000/docs in browser
2. **Then:** Read LEARNING_GUIDE.md section by section
3. **Next:** Run exercises in EXERCISES.md
4. **Finally:** Look at actual code files mentioned in CODE_NAVIGATION.md

You've got this! 🚀

Good luck with your interview! 💪

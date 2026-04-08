# Employee Management REST API

A production-ready FastAPI application for managing employee data with comprehensive CRUD operations, async/await support, Pydantic validation, and CSV import capabilities.

## 🎯 Project Overview

This project demonstrates a complete REST API implementation built with modern Python technologies. It showcases best practices in API design, database management, error handling, and asynchronous programming.

### Key Features

✨ **Full CRUD Operations**
- Create, Read, Update, and Delete employee records
- RESTful endpoint design with proper HTTP status codes
- Partial updates with smart field handling

🚀 **Async/Await Architecture**
- Non-blocking database operations using `asyncpg`
- Concurrent request handling for high performance
- Optimized for scaling with multiple concurrent users

🔐 **Data Validation & Error Handling**
- Pydantic schema validation for all requests
- Custom exception handling with meaningful error messages
- Proper HTTP status codes (201, 404, 409, 422, etc.)
- Duplicate detection with detailed conflict information

📊 **CSV Import Functionality**
- Preview CSV data before importing
- Batch import with duplicate handling
- Detailed import statistics (imported, skipped, errors)
- Seeding with sample employee data

🐳 **Docker & Containerization**
- Docker Compose setup with PostgreSQL
- Multi-container orchestration
- Environment-based configuration
- Health checks and automatic container restart

📚 **API Documentation**
- Interactive Swagger UI at `/docs`
- ReDoc alternative documentation at `/redoc`
- Generated OpenAPI schema
- Comprehensive endpoint descriptions

⏱️ **Timestamps & Audit Trail**
- Automatic `created_at` and `updated_at` fields
- Track record creation and modification times
- Query filtering by date ranges

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy (async) |
| **Database Driver** | asyncpg |
| **Validation** | Pydantic v2 |
| **Server** | Uvicorn |
| **Containerization** | Docker & Docker Compose |
| **Language** | Python 3.11+ |

## 📋 Project Structure

```
employee-management-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app & route definitions
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── crud.py                 # Database CRUD operations
│   ├── database.py             # Database connection & session
│   ├── config.py               # Configuration management
│   ├── exceptions.py           # Custom exception classes
│   ├── csv_import.py           # CSV import logic
│   └── services/
│       └── aws_export.py       # AWS export utilities
├── infrastructure/
│   └── lambda_csv/
│       └── handler.py          # AWS Lambda handler
├── static/
│   └── index.html             # Frontend (optional)
├── sample_data/
│   └── employees_seed.json    # Sample data for seeding
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── requirements.txt            # Python dependencies
├── QUICK_START.md             # Quick start guide
├── LEARNING_GUIDE.md          # Learning resources
├── EXERCISES.md               # Hands-on exercises
└── CODE_NAVIGATION.md         # Code navigation guide
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Python 3.11+ (for local development)
- PostgreSQL (or use Docker)

### Running with Docker

```bash
# Clone the repository
git clone https://github.com/NaviReddy369/employee-management-api.git
cd employee-management-api

# Start containers
docker-compose up --build

# API will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
# PostgreSQL at localhost:5432
```

### Running Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/employees"

# Run database migrations (if applicable)
# python -m alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## 📖 API Endpoints

### Employee Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/employees` | Create a new employee |
| `GET` | `/employees` | List all employees (with filtering) |
| `GET` | `/employees/{id}` | Get single employee by ID |
| `PUT` | `/employees/{id}` | Update employee |
| `DELETE` | `/employees/{id}` | Delete employee |

### CSV Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/employees/import/csv/preview` | Preview CSV before import |
| `POST` | `/employees/import/csv` | Import employees from CSV |

## 💻 Example API Usage

### Create Employee
```bash
curl -X POST http://localhost:8000/employees \
  -H "Content-Type: application/json" \
  -d '{
    "EMPLOYEE_ID": 100,
    "GENDER": "M",
    "EXPERIENCE_YEARS": 8,
    "POSITION": "Cloud Architect",
    "SALARY": "180000.00"
  }'
```

### Get All Employees
```bash
curl http://localhost:8000/employees
```

### Update Employee
```bash
curl -X PUT http://localhost:8000/employees/100 \
  -H "Content-Type: application/json" \
  -d '{
    "POSITION": "Principal Cloud Architect",
    "SALARY": "200000.00"
  }'
```

### Delete Employee
```bash
curl -X DELETE http://localhost:8000/employees/100
```

## 🧪 Testing & Exercises

The project includes comprehensive exercises in [EXERCISES.md](EXERCISES.md) covering:

- ✅ CRUD operations
- ✅ Async/await behavior
- ✅ Pydantic validation
- ✅ CSV import functionality
- ✅ Error handling
- ✅ Database operations
- ✅ API documentation
- ✅ Performance testing
- ✅ Docker management

Run exercises using PowerShell commands provided in the exercises file.

## 🔍 Database Schema

### Employees Table
```sql
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    gender CHAR(1) NOT NULL,
    experience_years INTEGER NOT NULL CHECK (experience_years >= 0 AND experience_years <= 80),
    position VARCHAR(255) NOT NULL,
    salary NUMERIC(10, 2) NOT NULL CHECK (salary > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 🔒 Validation Rules

| Field | Type | Constraints |
|-------|------|-------------|
| `employee_id` | Integer | Primary Key, Required |
| `gender` | String | Enum: M, F, O |
| `experience_years` | Integer | 0-80 years, Required |
| `position` | String | Min 1 char, Max 255 chars, Required |
| `salary` | Decimal | > 0, Required |

## 🎓 Learning Outcomes

This project teaches:

- **REST API Design** - Proper HTTP methods, status codes, and resource naming
- **Async Programming** - Non-blocking I/O using `async`/`await`
- **Database Design** - SQL schema design and relationships
- **ORM Usage** - SQLAlchemy for database abstraction
- **Data Validation** - Pydantic schemas for request/response validation
- **Error Handling** - Custom exceptions and HTTP error responses
- **CSV Processing** - Reading and importing data from files
- **Docker** - Containerization and orchestration
- **API Documentation** - Auto-generated docs with Swagger/ReDoc

## 📚 Additional Resources

- **[QUICK_START.md](QUICK_START.md)** - Get up and running in minutes
- **[LEARNING_GUIDE.md](LEARNING_GUIDE.md)** - Detailed learning materials
- **[CODE_NAVIGATION.md](CODE_NAVIGATION.md)** - Code structure and file explanations
- **[EXERCISES.md](EXERCISES.md)** - Hands-on practical exercises

## 🤝 Interview Preparation

This project is excellent for demonstrating knowledge in:

1. **API Design** - Show how REST conventions are followed
2. **Database Management** - Explain schema design and relationships
3. **Async Programming** - Demonstrate understanding of concurrent operations
4. **Error Handling** - Discuss validation and exception handling strategies
5. **Testing** - Show how to validate functionality with different scenarios
6. **DevOps** - Explain Docker and containerization

See [EXERCISES.md](EXERCISES.md) for interview preparation scenarios.

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
# or kill existing process on ports 8000/5432
```

### Database Connection Issues
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs db
docker-compose logs api
```

### Fresh Start
```bash
# Remove volumes and restart
docker-compose down -v
docker-compose up --build
```

## 📊 Performance

- **Response Time**: < 100ms for typical queries
- **Concurrent Users**: High throughput with async/await
- **Database**: Optimized with indexes on primary keys
- **Import Speed**: 49 employees in < 1 second

## 📝 License

This project is open source and available for learning and development purposes.

## 👨‍💼 Author

Built as a practical learning project demonstrating modern Python web development practices.

---

## 🎉 Getting Started

1. Clone the repository
2. Run `docker-compose up --build`
3. Visit `http://localhost:8000/docs`
4. Follow the [EXERCISES.md](EXERCISES.md) for hands-on learning
5. Reference [CODE_NAVIGATION.md](CODE_NAVIGATION.md) to understand the codebase

Happy coding! 🚀

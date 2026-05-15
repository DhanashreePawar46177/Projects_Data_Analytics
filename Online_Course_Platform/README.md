# FastAPI Online Course Platform

This project is a fully functional backend system built using FastAPI

## Project Overview
The Online Course Platform allows:
- Managing courses and students
- Enrolling students in courses
- Tracking course completion status
- Searching, sorting, and paginating data

## Tech Stack
- FastAPI
- Python
- SQLAlchemy (ORM)
- MySQL
- Pydantic (Validation)

## Features Implemented

### 1. GET APIs
- Home route
- Get all courses, students, enrollments
- Get record by ID
- Summary endpoint

### 2. POST + Validation
- Request body validation using Pydantic
- Field constraints (min_length, gt, EmailStr)
- Error handling using HTTPException

### 3. Helper Functions
- find_course()
- find_student()
- calculate_total_revenue()
- filter_courses()

### 4. CRUD Operations
- Create, Update, Delete for:
  - Courses
  - Students
  - Enrollments

### 5. Multi-Step Workflow
- Enroll → Complete → Track Status

### 6. Advanced APIs
- Keyword search
- Sorting
- Pagination
- Combined browsing API

## API Endpoints (Examples)
### Courses
- GET /courses
- POST /courses
- GET /courses/{id}
- PUT /courses/{id}
- DELETE /courses/{id}
- GET /courses/search
- GET /courses/sort
- GET /courses/page
- GET /courses/browse

### Students
- GET /students
- POST /students
- GET /students/{id}
- PUT /students/{id}
- DELETE /students/{id}

### Enrollments
- POST /enroll
- GET /enrollments
- GET /enrollments/{id}
- PUT /enrollments/{id}
- DELETE /enrollments/{id}
- PUT /complete
- GET /enrollments/status

## Additional APIs
- GET /summary
- GET /revenue

## API Testing
Test all APIs using Swagger UI:
http://127.0.0.1:8000/docs

## Screenshots
All API screenshots are available in the `Screenshots/` folder.

## How to Run Project

1. Install dependencies:
```bash
pip install -r requirements.txt

2. Run server:
uvicorn main:app --reload

2. Open Swagger:
http://127.0.0.1:8000/docs
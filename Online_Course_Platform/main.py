#import FastAPI framework
from fastapi import FastAPI,Query

#import to connect database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker #Creates DB sessions

#import to define table columns
from sqlalchemy import Column, Integer, String, Float

#import to create base class for models(tables)
from sqlalchemy.orm import declarative_base

#import to restrict duplicate entries 
from sqlalchemy import UniqueConstraint

#import for request validation
from pydantic import BaseModel, Field

#import for optional fields
from typing import Optional

#import for dependenct injection for DB
from fastapi import Depends
from sqlalchemy.orm import Session

#import for error handling
from fastapi import HTTPException

#import for validates email format
from pydantic import EmailStr

#import to handles duplicate errors(DB level)
from sqlalchemy.exc import IntegrityError

#MySQL database connection string
DATABASE_URL = "mysql+pymysql://root:mysql123@localhost/online_course_db"

#Connects FastAPI to MySQL
engine = create_engine(DATABASE_URL)

#Creates DB session factory
SessionLocal = sessionmaker(bind=engine)

#Helper functions
def find_course(db, course_id):
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if not course:
        raise HTTPException(404, "Course not found")
    return course

def find_student(db, student_id):
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")
    return student

def calculate_total_revenue(db):
    courses = db.query(CourseModel).all() #get all courses
    return sum(course.price for course in courses) #sum all prices

def filter_courses(query, keyword):
    if keyword is not None:
        query = query.filter(
            (CourseModel.title.contains(keyword)) |
            (CourseModel.category.contains(keyword))
        )
    return query

#Response Builder Function
def response_model(status: str, message: str, data=None):
    return {
        "status": status,
        "message": message,
        "data": data
    }

#Create API app
#app = FastAPI()
app = FastAPI(
    title="Online Course Platform API",
    description="API for managing courses, students, and enrollments"
)

#Route
@app.get("/")
def home():
    #Root endpoint to check if API is running.
    return response_model(
        "success",
        "Welcome to Online Course Platform"
    )

#Database Models(Tables)
Base = declarative_base()

class CourseModel(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    price = Column(Float)
    category = Column(String(50))

class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True) 

class EnrollmentModel(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)
    course_id = Column(Integer)
    status = Column(String(20), default="ongoing")

    #Same student can't enroll twice in same course
    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),
    )

#Automatically creates tables in DB
Base.metadata.create_all(bind=engine)

#Pydantic Schemas(Validation)
#Course schema
class Course(BaseModel):
    title: str = Field(..., min_length=3)
    price: float = Field(..., gt=0)
    category: str

class Student(BaseModel):
    name: str = Field(..., min_length=3)
    email: EmailStr

class Enrollment(BaseModel):
    student_id: int
    course_id: int
    status: Optional[str] = "ongoing"

#DB Dependency
def get_db():
    #Create session
    db = SessionLocal()
    try:
        #Send DB to API
        yield db
    finally:
        db.close()

#Course APIs
@app.get("/courses")
def get_courses(db: Session = Depends(get_db)):
    return response_model(
        "success",
        f"{len(db.query(CourseModel).all())} courses fetched",
        db.query(CourseModel).all()
    )

#Create Course
@app.post("/courses", status_code=201)
def create_course(course: Course, db: Session = Depends(get_db)):
    new_course = CourseModel(**course.dict()) #Convert request to DB object
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return response_model(
        "success",
        "Course created successfully",
        new_course
    )

#Pagination
@app.get("/courses/page")
def paginate_courses(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    return db.query(CourseModel).offset(skip).limit(limit).all()

@app.get("/courses/search")
def search_courses(
    keyword: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(CourseModel)
    query = filter_courses(query, keyword)
    return query.all()
    

@app.get("/courses/sort")
def sort_courses(order: str = "asc", db: Session = Depends(get_db)):
    if order == "desc":
        return db.query(CourseModel).order_by(CourseModel.price.desc()).all()
    return db.query(CourseModel).order_by(CourseModel.price.asc()).all()

#Browse(Search+Sort+Pagination)
@app.get("/courses/browse")
def browse_courses(
    keyword: str = Query(None),
    order: str = "asc",
    skip: int = 0,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    query = db.query(CourseModel)

    # Search
    if keyword is not None:
        query = query.filter(
            (CourseModel.title.contains(keyword)) |
            (CourseModel.category.contains(keyword))
        )

    # Sort
    if order == "desc":
        query = query.order_by(CourseModel.price.desc())
    else:
        query = query.order_by(CourseModel.price.asc())

    # Pagination
    return query.offset(skip).limit(limit).all()
    
@app.get("/courses/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = course = find_course(db, course_id)

    if not course:
        raise HTTPException(404, "Course not found")

    return response_model(
        "success",
        "Course fetched successfully",
        course
    )

#Update Course
@app.put("/courses/{course_id}")
def update_course(course_id: int, updated: Course, db: Session = Depends(get_db)):
    course = course = find_course(db, course_id)

    if not course:
        raise HTTPException(404, "Course not found")

    for key, value in updated.dict().items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course) 

    return response_model(
        "success",
        "Course Updated successfully",
        course.__dict__
    )

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = course = find_course(db, course_id)

    if not course:
        raise HTTPException(404, "Course not found")

    db.delete(course)
    db.commit()

    return response_model(
        "success",
        "Course deleted successfully",
        course
    )

#Student APIs
@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    students=db.query(StudentModel).all()
    return response_model(
        "success",
        f"{len(students)} students fetched",
        students
    )

@app.post("/students", status_code=201)
def create_student(student: Student, db: Session = Depends(get_db)):

    # Check duplicate email
    existing = db.query(StudentModel).filter(StudentModel.email == student.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_student = StudentModel(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return response_model(
        "success",
        "Student Added successfully",
        new_student
    )

@app.get("/students/page")
def paginate_students(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    return db.query(StudentModel).offset(skip).limit(limit).all()

@app.get("/students/search")
def search_students(
    keyword: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(StudentModel)

    if keyword is not None:
        query = query.filter(
            (StudentModel.name.contains(keyword)) |
            (StudentModel.email.contains(keyword))
        )

    return query.all()

@app.get("/students/sort")
def sort_students(order: str = "asc", db: Session = Depends(get_db)):
    if order == "desc":
        return db.query(StudentModel).order_by(StudentModel.name.desc()).all()
    return db.query(StudentModel).order_by(StudentModel.name.asc()).all()

@app.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = find_student(db, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return response_model(
        "success",
        "Student fetched successfully",
        student
    )

@app.put("/students/{student_id}")
def update_student(student_id: int, updated: Student, db: Session = Depends(get_db)):

    student = find_student(db, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check duplicate email (important)
    existing = db.query(StudentModel).filter(
        StudentModel.email == updated.email,
        StudentModel.id != student_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already in use")

    # Update fields
    student.name = updated.name
    student.email = updated.email

    db.commit()
    db.refresh(student)

    return response_model(
        "success",
        "Student updated successfully",
        student
    )

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):

    student = find_student(db, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()

    return response_model(
        "success",
        f"Student with ID {student_id} deleted successfully",
        student
    )

#Enrollment APIs
@app.post("/enroll", status_code=201)
def enroll(data: Enrollment, db: Session = Depends(get_db)):

    course = db.query(CourseModel).filter(CourseModel.id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    student = db.query(StudentModel).filter(StudentModel.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    new_enroll = EnrollmentModel(
        student_id=data.student_id,
        course_id=data.course_id,
        status="ongoing" 
    )

    try:
        db.add(new_enroll)
        db.commit()
        db.refresh(new_enroll)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Student already enrolled in this course"
        )

    return response_model(
            "success",
            "Student enrolled successfully",
            new_enroll
        )
    #return {"message": "Enrolled successfully", "status": "ongoing"}

@app.get("/enrollments")
def get_enrollments(db: Session = Depends(get_db)):
    return db.query(EnrollmentModel).all()

@app.get("/enrollments/page")
def paginate_enrollments(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    return db.query(EnrollmentModel).offset(skip).limit(limit).all()

@app.get("/enrollments/search")
def search_enrollments(
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(EnrollmentModel)

    if status is not None:
        query = query.filter(EnrollmentModel.status.contains(status))

    return query.all()

@app.get("/enrollments/sort")
def sort_enrollments(order: str = "asc", db: Session = Depends(get_db)):
    if order == "desc":
        return db.query(EnrollmentModel).order_by(EnrollmentModel.id.desc()).all()
    return db.query(EnrollmentModel).order_by(EnrollmentModel.id.asc()).all()


@app.get("/enrollments/status")
def get_by_status(status: str, db: Session = Depends(get_db)):
    return db.query(EnrollmentModel).filter(EnrollmentModel.status == status).all()

@app.get("/enrollments/{enroll_id}")
def get_enrollment_by_id(enroll_id: int, db: Session = Depends(get_db)):

    enroll = db.query(EnrollmentModel).filter(
        EnrollmentModel.id == enroll_id
    ).first()

    if not enroll:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    return enroll

@app.put("/enrollments/{enroll_id}")
def update_enrollment(
    enroll_id: int,
    data: Enrollment,
    db: Session = Depends(get_db)
):
    enroll = db.query(EnrollmentModel).filter(EnrollmentModel.id == enroll_id).first()

    if not enroll:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    #if new course exists
    course = db.query(CourseModel).filter(CourseModel.id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    #if new student exists
    student = db.query(StudentModel).filter(StudentModel.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Update fields
    enroll.student_id = data.student_id
    enroll.course_id = data.course_id
    enroll.status = data.status

    try:
        db.commit()
        db.refresh(enroll)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Duplicate enrollment (student already enrolled in this course)"
        )

    return {
        "message": "Enrollment updated successfully",
        "data": enroll
    }

@app.delete("/enrollments/{enroll_id}")
def delete_enrollment(enroll_id: int, db: Session = Depends(get_db)):

    enroll = db.query(EnrollmentModel).filter(EnrollmentModel.id == enroll_id).first()

    if not enroll:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    db.delete(enroll)
    db.commit()

    return {"message": f"Enrollment {enroll_id} deleted successfully"}

@app.put("/complete")
def complete_course(data: Enrollment, db: Session = Depends(get_db)):

    enroll = db.query(EnrollmentModel).filter(
        EnrollmentModel.student_id == data.student_id,
        EnrollmentModel.course_id == data.course_id
    ).first()

    if not enroll:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    enroll.status = "completed"

    db.commit()
    db.refresh(enroll)

    return response_model(
        "success",
        "Course marked as completed",
        enroll
    )

#Summary API
#Counts records
@app.get("/summary")
def summary(db: Session = Depends(get_db)):
    return {
        "total_courses": db.query(CourseModel).count(),
        "total_students": db.query(StudentModel).count(),
        "total_enrollments": db.query(EnrollmentModel).count()
    }

#Revenue API
@app.get("/revenue")
def get_revenue(db: Session = Depends(get_db)):
    total = calculate_total_revenue(db)
    return {"total_revenue": total}
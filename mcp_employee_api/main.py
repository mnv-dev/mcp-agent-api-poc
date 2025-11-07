from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from mcp_employee_api import crud, schemas, models
from mcp_employee_api.database import engine, get_db

app = FastAPI(
    title="MCP-Employee API",
    description="Pilot Microservice for Employee CRUD and Filtering.",
    version="1.0.1"
)

models.Base.metadata.create_all(bind=engine)

# Create a new employee
@app.post("/employees/", response_model=schemas.Employee, status_code=201, tags=["Employees"])
def create_new_employee(
        employee: schemas.EmployeeCreate,
        db: Session = Depends(get_db)
):
    db_employee_exists = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if db_employee_exists:
        raise HTTPException(status_code=400, detail=f"Employee with email '{employee.email}' already exists.")
    return crud.create_employee(db=db, employee=employee)

# Get employees with optional filters
@app.get("/employees/", response_model=List[schemas.Employee], tags=["Employees"])
def read_employees_list(
        name: Optional[str] = Query(None, description="Partial match filter for employee name."),
        email: Optional[str] = Query(None, description="Partial match filter for employee email."),
        position: Optional[str] = Query(None, description="Partial match filter for employee position."),
        skip: int = Query(0, description="Number of items to skip (pagination offset)."),
        limit: int = Query(100, description="Maximum number of items to return (pagination limit)."),
        db: Session = Depends(get_db)
):
    employees = crud.get_employees_list(
        db,
        name=name,
        email=email,
        position=position,
        skip=skip,
        limit=limit
    )
    return employees

# Get a single employee by ID
@app.get("/employees/{employee_id}", response_model=schemas.Employee, tags=["Employees"])
def read_employee_by_id_or_filter(
        employee_id: int,
        db: Session = Depends(get_db)
):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found.")
    return db_employee
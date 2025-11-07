from sqlalchemy.orm import Session
from typing import Optional

from mcp_employee_api import models, schemas
from mcp_employee_api.models import Employee

# Retrieve a list of employees with optional filtering
def get_employees_list(
        db: Session,
        name: Optional[str] = None,
        email: Optional[str] = None,
        position: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
) -> list[type[Employee]]:
    query = db.query(models.Employee)
    if name:
        query = query.filter(models.Employee.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(models.Employee.email.ilike(f"%{email}%"))
    if position:
        query = query.filter(models.Employee.position.ilike(f"%{position}%"))
    return query.offset(skip).limit(limit).all()

# Retrieve a single employee by ID or exact field match
def get_employee(
        db: Session,
        employee_id: Optional[int] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        position: Optional[str] = None,
) -> Optional[models.Employee]:
    query = db.query(models.Employee)
    if employee_id is not None:
        return query.filter(models.Employee.id == employee_id).first()
    if name:
        query = query.filter(models.Employee.name == name)
    if email:
        query = query.filter(models.Employee.email == email)
    if position:
        query = query.filter(models.Employee.position == position)
    return query.first()

# Save a new employee record to the database
def create_employee(db: Session, employee: schemas.EmployeeCreate) -> models.Employee:
    db_employee = models.Employee(
        name=employee.name,
        email=employee.email,
        position=employee.position
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee
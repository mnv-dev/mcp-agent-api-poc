from pydantic import BaseModel, Field


# Base schema for shared attributes
class EmployeeBase(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    position: str = Field(min_length=1)

# Schema for creating an employee
class EmployeeCreate(EmployeeBase):
    pass

# Schema for reading/responding with an employee
class Employee(EmployeeBase):
    id: int = Field(gt=0)

    class Config:
        orm_mode = True
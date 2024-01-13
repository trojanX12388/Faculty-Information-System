# IMPORTING PYDANTIC CLASS
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

Base = declarative_base()

import datetime


# FACULTY PROFILE
# --------------------------------------------------------------

class FISFaculty(Base):
    __tablename__ = 'FISFaculty'

    FacultyId = Column(Integer, primary_key=True, index=True)
    FacultyType = Column(String)
    Rank = Column(String)
    Units = Column(Integer)
    Name = Column(String)
    FirstName = Column(String)
    LastName = Column(String)
    MiddleName = Column(String)
    MiddleInitial = Column(String)
    NameExtension = Column(String)
    BirthDate = Column(String)
    DateHired = Column(String)
    Degree = Column(String)
    Remarks = Column(String)
    FacultyCode = Column(String)
    Honorific = Column(String)
    Age = Column(Integer)
    
    Email = Column(String)
    ResidentialAddress = Column(String)
    MobileNumber = Column(String)
    Gender = Column(Integer)
    
    ProfilePic = Column(String)
    IsActive = Column(Boolean, default=True)

# Pydantic model for data validation
class FISFaculty_Model(BaseModel):
    FacultyId: int
    FacultyType: str
    Rank: str
    Units: int
    Name: str
    FirstName: str  = "" 
    LastName: str = ""
    MiddleName: Optional[str]
    MiddleInitial: Optional[str]
    NameExtension: Optional[str]
    BirthDate: datetime.date 
    DateHired: datetime.date 
    Degree: Optional[str]
    Remarks: Optional[str]
    FacultyCode: int
    Honorific: Optional[str]
    Age: int
    Email: str = ""
    ResidentialAddress: str = ""
    MobileNumber: str = ""
    Gender: int
    ProfilePic: str = ""
    IsActive: bool 

    class Config:
        orm_mode = True
        from_attributes=True

# --------------------------------------------------------------

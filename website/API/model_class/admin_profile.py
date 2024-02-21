# IMPORTING PYDANTIC CLASS
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime

Base = declarative_base()

import datetime


# FACULTY PROFILE
# --------------------------------------------------------------

class FISAdmin(Base):
    __tablename__ = 'FISAdmin'

    AdminId = Column(Integer, primary_key=True, index=True)
    AdminType = Column(String)
    Rank = Column(String)
    Units = Column(Float)
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
    Specialization = Column(String)
    PreferredSchedule = Column(String)
    
    Email = Column(String)
    ResidentialAddress = Column(String)
    MobileNumber = Column(String)
    Gender = Column(Integer)
    
    ProfilePic = Column(String)
    Status = Column(String)
    
    created_at = Column(DateTime)

# Pydantic model for data validation
class FISAdmin_Model(BaseModel):
    AdminId: int
    AdminType: str
    Rank: str
    Units: float
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
    Specialization: Optional[str]
    PreferredSchedule: Optional[str]
    Email: str = ""
    ResidentialAddress: str = ""
    MobileNumber: str = ""
    Gender: int
    ProfilePic: str = ""
    Status: Optional[str] 
    
    created_at: datetime.datetime  # Use datetime.datetime for timestamp

    class Config:
        orm_mode = True
        from_attributes=True

# --------------------------------------------------------------

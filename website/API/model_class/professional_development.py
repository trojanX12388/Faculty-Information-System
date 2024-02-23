# IMPORTING PYDANTIC CLASS
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime

Base = declarative_base()

import datetime


# FACULTY PROFILE
# --------------------------------------------------------------

class FISProfessionalDevelopment(Base):
    __tablename__ = 'FISProfessionalDevelopment'

    id = Column(Integer, primary_key=True, index=True)
    FacultyId = Column(String)
    title = Column(String)
    date_start = Column(DateTime)
    date_end = Column(DateTime)
    hours = Column(Integer)
    conducted_by = Column(String)
    type = Column(String)
    file_id = Column(String)
    

# Pydantic model for data validation
class FISProfessionalDevelopment_Model(BaseModel):
    id: int
    FacultyId: int
    title: Optional[str]
    date_start: datetime.date 
    date_end: datetime.date
    hours: int
    conducted_by: Optional[str]
    type: Optional[str]
    file_id: Optional[str]
    
    class Config:
        orm_mode = True
        from_attributes=True

# --------------------------------------------------------------

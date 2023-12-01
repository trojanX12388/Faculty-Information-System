# IMPORTING PYDANTIC CLASS
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

Base = declarative_base()

import datetime


# FACULTY PROFILE
# --------------------------------------------------------------

class Faculty_Profile(Base):
    __tablename__ = 'Faculty_Profile'

    faculty_account_id = Column(String, primary_key=True, index=True)
    faculty_type = Column(String)
    units = Column(Integer)
    name = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    middle_initial = Column(String)
    name_extension = Column(String)
    birth_date = Column(String)
    date_hired = Column(String)
    remarks = Column(String)
    faculty_code = Column(String)
    honorific = Column(String)
    age = Column(Integer)
    email = Column(String)
    profile_pic = Column(String)
    is_active = Column(Boolean, default=True)

# Pydantic model for data validation
class Faculty_Profile_Model(BaseModel):
    faculty_account_id: str
    faculty_type: str
    units: int
    name: str
    first_name: str  = "" 
    last_name: str = ""
    middle_name: Optional[str]
    middle_initial: Optional[str]
    name_extension: Optional[str]
    birth_date: datetime.date 
    date_hired: datetime.date 
    remarks: Optional[str]
    faculty_code: int
    honorific: Optional[str]
    age: int
    email: str = ""
    profile_pic: str = ""
    is_active: bool 

    class Config:
        orm_mode = True
        from_attributes=True

# --------------------------------------------------------------

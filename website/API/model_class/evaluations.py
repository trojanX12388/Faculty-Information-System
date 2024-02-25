# IMPORTING PYDANTIC CLASS
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, Date

Base = declarative_base()

from datetime import datetime


# FACULTY PROFILE
# --------------------------------------------------------------

class FISEvaluations(Base):
    __tablename__ = 'FISEvaluations'

    id = Column(Integer, primary_key=True)
    FacultyId = Column(Integer)
    Evaluator_Name = Column(String)
    EvaluatorId = Column(Integer)
    Type = Column(String)
    acad_head = Column(Float)
    acad_head_a = Column(Float)
    acad_head_b = Column(Float)
    acad_head_c = Column(Float)
    acad_head_d = Column(Float)
    director = Column(Float)
    director_a = Column(Float)
    director_b = Column(Float)
    director_c = Column(Float)
    director_d = Column(Float)
    self = Column(Float)
    self_a = Column(Float)
    self_b = Column(Float)
    self_c = Column(Float)
    self_d = Column(Float)
    peer = Column(Float)
    peer_a = Column(Float)
    peer_b = Column(Float)
    peer_c = Column(Float)
    peer_d = Column(Float)
    student = Column(Float)
    student_a = Column(Float)
    student_b = Column(Float)
    student_c = Column(Float)
    student_d = Column(Float)
    school_year = Column(Date)
    semester = Column(String)
    is_delete = Column(Boolean)

# Pydantic model for data validation
class FISEvaluations_Model(BaseModel):
    id: int
    FacultyId: int
    Evaluator_Name: Optional[str]
    EvaluatorId: int
    Type: Optional[str]
    acad_head: float
    acad_head_a: float
    acad_head_b: float
    acad_head_c: float
    acad_head_d: float
    director: float
    director_a: float
    director_b: float
    director_c: float
    director_d: float
    self: float
    self_a: float
    self_b: float
    self_c: float
    self_d: float
    peer: float
    peer_a: float
    peer_b: float
    peer_c: float
    peer_d: float
    student: float
    student_a: float
    student_b: float
    student_c: float
    student_d: float
    school_year: datetime
    semester: Optional[str]
    is_delete: bool 

    class Config:
        orm_mode = True
        from_attributes=True

# --------------------------------------------------------------
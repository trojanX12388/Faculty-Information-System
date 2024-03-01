# IMPORTING PYDANTIC CLASS
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

from datetime import datetime

class FacultyResearchPaper(Base):
    __tablename__ = 'RISfaculty_research_papers'

    id = Column(String, primary_key=True, nullable=False)
    title = Column(String)
    content = Column(String)
    abstract = Column(String)
    file_path = Column(String)
    date_publish = Column(Date)
    category = Column(String)
    publisher = Column(String)
    user_id = Column(String, default=None)

# Pydantic model for data validation
class FacultyResearchPaper_Model(BaseModel):
    id: str
    title: Optional[str]
    content: Optional[str]
    abstract: Optional[str]
    file_path: Optional[str]
    date_publish: datetime
    category: Optional[str]
    publisher: Optional[str]
    user_id: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True
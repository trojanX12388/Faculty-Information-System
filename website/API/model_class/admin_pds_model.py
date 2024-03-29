# IMPORTING PYDANTIC CLASS
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float

Base = declarative_base()

import datetime

# ADMIN PDS

class AdminFISPDS_PersonalDetails(Base):
    __tablename__ = 'FISPDS_PersonalDetails'

    id = Column(Integer, primary_key=True, index=True)
    AdminId = Column(Integer)
    sex = Column(String)
    gender = Column(String)
    height = Column(Float)
    weight = Column(Float)
    religion = Column(String)
    civil_status = Column(String)
    blood_type = Column(String)
    pronoun = Column(String)
    country = Column(String)
    city = Column(String)
    citizenship = Column(String)
    dual_citizenship = Column(String)
    Remarks = Column(String)
    is_delete = Column(Boolean, default=False)

# Pydantic model for data validation
class AdminFISPDS_PersonalDetails_Model(BaseModel):
    id: int
    AdminId : int
    sex : Optional[str]
    gender : Optional[str]
    height : Optional[float]
    weight : Optional[float]
    religion : Optional[str]
    civil_status : Optional[str]
    blood_type : Optional[str]
    pronoun : Optional[str]
    country : Optional[str]
    city : Optional[str]
    citizenship : Optional[str]
    dual_citizenship : Optional[str]
    Remarks : Optional[str]
    is_delete: bool 

    class Config:
        orm_mode = True
        from_attributes=True

# --------------------------------------------------------------



# ADMIN PDS Contact Details  
# --------------------------------------------------------------

class AdminFISPDS_ContactDetails(Base):
    __tablename__ = 'FISPDS_ContactDetails'

    id = Column(Integer, primary_key=True, index=True)
    AdminId = Column(Integer)
    Email = Column(String)
    mobile_number = Column(String)
    perm_country = Column(String)
    perm_region = Column(String)   
    perm_province = Column(String) 
    perm_city = Column(String)
    perm_address = Column(String) 
    perm_zip_code = Column(String) 
    perm_phone_number = Column(String)
    res_country = Column(String)
    res_region = Column(String)   
    res_province = Column(String)  
    res_city = Column(String) 
    res_address = Column(String) 
    res_zip_code = Column(String)
    res_phone_number = Column(String)
    Remarks = Column(String)
    is_delete = Column(Boolean, default=False)

# Pydantic model for data validation
class AdminFISPDS_ContactDetails_Model(BaseModel):
    id: int
    AdminId : int
    Email : Optional[str]
    mobile_number : Optional[str]
    perm_country : Optional[str]
    perm_region : Optional[str]  
    perm_province : Optional[str] 
    perm_city : Optional[str]
    perm_address : Optional[str]
    perm_zip_code : Optional[str] 
    perm_phone_number : Optional[str]
    res_country : Optional[str]
    res_region : Optional[str]
    res_province : Optional[str]
    res_city : Optional[str]
    res_address : Optional[str]
    res_zip_code : Optional[str]
    res_phone_number : Optional[str]
    Remarks : Optional[str]
    is_delete: bool 

    class Config:
        orm_mode = True
        from_attributes=True
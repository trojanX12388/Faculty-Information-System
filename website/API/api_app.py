from flask import Flask, jsonify, request, Blueprint
from flask_restx import Api
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

import os,ast

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# IMPORTING PYDANTIC CLASS
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

# LOADING AUTHENTICATION
from .authentication import *

# EXECUTING DATABASE

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy setup

engine=create_engine(os.getenv('DATABASE_URI'), pool_pre_ping=True, pool_size=10, max_overflow=20, pool_recycle=1800)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Access API keys from environment variables

API_KEYS = ast.literal_eval(os.environ["API_KEYS"])

# ---------------------------------------------------------

# LOAD MODELS
from .model_class.faculty_profile import Faculty_Profile
# PDS
from .model_class.pds_model import PDS_Personal_Details,PDS_Contact_Details

# LOAD PYDANTIC MODELS
from .model_class.faculty_profile import Faculty_Profile_Model
# PDS 
from .model_class.pds_model import PDS_Personal_Details_Model,PDS_Contact_Details_Model


# ---------------------------------------------------------

# MAIN API V1

# JSON DATA API

API = Blueprint('API', __name__)


from sqlalchemy.orm import aliased

@API.route('/api/all/Faculty_Profile', methods=['GET'])
@admin_token_required  # Get the API key from the request header
def get_combined_profile():
    token = request.headers.get('token')  # Get the API key from the request header
    key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    key = key['key']

    if key not in API_KEYS.values():
        return jsonify(message="access denied!"), 403

    else:
        db = SessionLocal()
        try:
            # Perform outer joins with Faculty_Profile, PDS_Personal_Details, and PDS_Contact_Details
            faculty_alias = aliased(Faculty_Profile)
            personal_details_alias = aliased(PDS_Personal_Details)
            contact_details_alias = aliased(PDS_Contact_Details)

            combined_data = db.query(Faculty_Profile, personal_details_alias, contact_details_alias).outerjoin(
                personal_details_alias, Faculty_Profile.faculty_account_id == personal_details_alias.faculty_account_id
            ).outerjoin(
                contact_details_alias, Faculty_Profile.faculty_account_id == contact_details_alias.faculty_account_id
            ).all()

            # Create a dictionary to store combined data
            combined_profile = []
            for faculty, pds_personal_details, pds_contact_details in combined_data:
                faculty_dict = Faculty_Profile_Model.from_orm(faculty).dict()

                if pds_personal_details:
                    faculty_dict['PDS_Personal_Details'] = PDS_Personal_Details_Model.from_orm(pds_personal_details).dict()
                else:
                    faculty_dict['PDS_Personal_Details'] = None

                if pds_contact_details:
                    faculty_dict['PDS_Contact_Details'] = PDS_Contact_Details_Model.from_orm(pds_contact_details).dict()
                else:
                    faculty_dict['PDS_Contact_Details'] = None

                combined_profile.append(faculty_dict)

            return jsonify({'Faculties': combined_profile})

        except ValidationError as e:
            return jsonify({'error': f'Validation error: {e}'})
        finally:
            db.close()

# FACULTY DATA 
# -------------------------------------------------------------------------

@API.route('/api/Faculty_Profile', methods=['GET'])
@admin_token_required # Get the API key from the request header
def get_all_faculty():
    token = request.headers.get('token') # Get the API key from the request header
    key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    key = key['key']
    
    if not key in API_KEYS.values():
         return jsonify(message="access denied!"), 403
    
    else:
        db = SessionLocal()
        faculty_profile = db.query(Faculty_Profile).all()
        db.close()
        try:
            profile = [Faculty_Profile_Model.from_orm(faculty).dict() for faculty in faculty_profile]
            return jsonify({'Faculty_Profile': profile})
        
        
        
        
        except ValidationError as e:
            return jsonify({'error': f'Validation error: {e}'})



@API.route('/api/Faculty_Profile/<faculty_account_id>',  methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_token_required # Get the API key from the request header
def get_task(faculty_account_id):
    token = request.headers.get('token')  # Get the API key from the request header
    key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    key = key['key']
    
    if not key in API_KEYS.values():
         return jsonify(message="access denied!"), 403
    
    else:
        if request.method == 'GET':
            db = SessionLocal()
            faculty_profile = db.query(Faculty_Profile).filter(Faculty_Profile.faculty_account_id == faculty_account_id).first()
            db.close()
            if faculty_profile is None:
                return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'Faculty_Profile': Faculty_Profile_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        
        elif request.method == 'POST':
            data = request.json
            faculty_profile = Faculty_Profile_Model(**data)
            db = SessionLocal()
            db_faculty_profile = Faculty_Profile(**Faculty_Profile_Model.dict())
            db.add(db_faculty_profile)
            db.commit()
            db.refresh(db_faculty_profile)
            db.close()
            if faculty_profile is None:
                    return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'Faculty_Profile': Faculty_Profile_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
            
            
        elif request.method == 'PUT':
            data = request.json
            db = SessionLocal()
            db_faculty_profile = db.query(Faculty_Profile).filter(Faculty_Profile.faculty_account_id == faculty_account_id).first()
            if db_faculty_profile is None:
                db.close()
                return jsonify({'error': 'no data found'}), 404
            for field, value in data.items():
                setattr(db_faculty_profile, field, value)
            db.commit()
            db.refresh(db_faculty_profile)
            db.close()
            if db_faculty_profile is None:
                    return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'Faculty_Profile': Faculty_Profile_Model.from_orm(db_faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        
        elif request.method == 'DELETE':
            db = SessionLocal()
            db_faculty_profile = db.query(Faculty_Profile).filter(Faculty_Profile.faculty_account_id == faculty_account_id).first()
            if db_faculty_profile is None:
                db.close()
                return jsonify({'error': 'no data found'}), 404
            db.delete(db_faculty_profile)
            db.commit()
            db.close()
            return jsonify({'result': True})

# -------------------------------------------------------------------------

# PERSONAL DETAILS
# -------------------------------------------------------------------------

@API.route('/api/Faculty_Profile/PDS_Personal_Details', methods=['GET'])
@admin_token_required # Get the API key from the request header
def get_all_pds_personal_details():
    token = request.headers.get('token')  # Get the API key from the request header
    key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    key = key['key']
    
    if not key in API_KEYS.values():
         return jsonify(message="access denied!"), 403
    
    else:
        db = SessionLocal()
        faculty_profile = db.query(PDS_Personal_Details).all()
        db.close()
        try:
            profile = [PDS_Personal_Details_Model.from_orm(faculty).dict() for faculty in faculty_profile]
            return jsonify({'PDS_Personal_Details': profile})
        except ValidationError as e:
            return jsonify({'error': f'Validation error: {e}'})



@API.route('/api/Faculty_Profile/PDS_Personal_Details/<faculty_account_id>',  methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_token_required # Get the API key from the request header
def get_pds_personal_details(faculty_account_id):
    token = request.headers.get('token')  # Get the API key from the request header
    key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    key = key['key']
    
    if not key in API_KEYS.values():
         return jsonify(message="access denied!"), 403
    
    else:
        if request.method == 'GET':
            db = SessionLocal()
            faculty_profile = db.query(PDS_Personal_Details).filter(PDS_Personal_Details.faculty_account_id == faculty_account_id).first()
            db.close()
            if faculty_profile is None:
                return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'PDS_Personal_Details': PDS_Personal_Details_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        
        elif request.method == 'POST':
            data = request.json
            faculty_profile = PDS_Personal_Details_Model(**data)
            db = SessionLocal()
            db_faculty_profile = PDS_Personal_Details(**PDS_Personal_Details_Model.dict())
            db.add(db_faculty_profile)
            db.commit()
            db.refresh(db_faculty_profile)
            db.close()
            if faculty_profile is None:
                    return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'PDS_Personal_Details': PDS_Personal_Details_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
            
            
        elif request.method == 'PUT':
            data = request.json
            db = SessionLocal()
            db_faculty_profile = db.query(PDS_Personal_Details).filter(PDS_Personal_Details.faculty_account_id == faculty_account_id).first()
            if db_faculty_profile is None:
                db.close()
                return jsonify({'error': 'no data found'}), 404
            for field, value in data.items():
                setattr(db_faculty_profile, field, value)
            db.commit()
            db.refresh(db_faculty_profile)
            db.close()
            if db_faculty_profile is None:
                    return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'PDS_Personal_Details': PDS_Personal_Details_Model.from_orm(db_faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        elif request.method == 'DELETE':
            db = SessionLocal()
            db_faculty_profile = db.query(PDS_Personal_Details).filter(PDS_Personal_Details.faculty_account_id == faculty_account_id).first()
            if db_faculty_profile is None:
                db.close()
                return jsonify({'error': 'no data found'}), 404
            db.delete(db_faculty_profile)
            db.commit()
            db.close()
            return jsonify({'result': True})
    

 # PDS Contact Details  
# -------------------------------------------------------------------------

@API.route('/api/Faculty_Profile/PDS_Contact_Details', methods=['GET'])
@admin_token_required # Get the API key from the request header
def get_all_pds_contact_details():
    token = request.headers.get('token') # Get the API key from the request header
    key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    key = key['key']
    
    if not key in API_KEYS.values():
         return jsonify(message="access denied!"), 403
    
    else:
        db = SessionLocal()
        faculty_profile = db.query(PDS_Contact_Details).all()
        db.close()
        try:
            profile = [PDS_Contact_Details_Model.from_orm(faculty).dict() for faculty in faculty_profile]
            return jsonify({'PDS_Contact_Details': profile})
        except ValidationError as e:
            return jsonify({'error': f'Validation error: {e}'})



@API.route('/api/Faculty_Profile/PDS_Contact_Details/<faculty_account_id>',  methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_token_required # Get the API key from the request header
def get_pds_contact_details(faculty_account_id):
    token = request.headers.get('token')  # Get the API key from the request header
    key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    key = key['key']
    
    if not key in API_KEYS.values():
         return jsonify(message="access denied!"), 403
    
    else:
        if request.method == 'GET':
            db = SessionLocal()
            faculty_profile = db.query(PDS_Contact_Details).filter(PDS_Contact_Details.faculty_account_id == faculty_account_id).first()
            db.close()
            if faculty_profile is None:
                return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'PDS_Contact_Details': PDS_Contact_Details_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        
        elif request.method == 'POST':
            data = request.json
            faculty_profile = PDS_Contact_Details_Model(**data)
            db = SessionLocal()
            db_faculty_profile = PDS_Contact_Details(**PDS_Contact_Details_Model.dict())
            db.add(db_faculty_profile)
            db.commit()
            db.refresh(db_faculty_profile)
            db.close()
            if faculty_profile is None:
                    return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'PDS_Contact_Details': PDS_Contact_Details_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
            
            
        elif request.method == 'PUT':
            data = request.json
            db = SessionLocal()
            db_faculty_profile = db.query(PDS_Contact_Details).filter(PDS_Contact_Details.faculty_account_id == faculty_account_id).first()
            if db_faculty_profile is None:
                db.close()
                return jsonify({'error': 'no data found'}), 404
            for field, value in data.items():
                setattr(db_faculty_profile, field, value)
            db.commit()
            db.refresh(db_faculty_profile)
            db.close()
            if db_faculty_profile is None:
                    return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'PDS_Contact_Details': PDS_Contact_Details_Model.from_orm(db_faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        elif request.method == 'DELETE':
            db = SessionLocal()
            db_faculty_profile = db.query(PDS_Contact_Details).filter(PDS_Contact_Details.faculty_account_id == faculty_account_id).first()
            if db_faculty_profile is None:
                db.close()
                return jsonify({'error': 'no data found'}), 404
            db.delete(db_faculty_profile)
            db.commit()
            db.close()
            return jsonify({'result': True})
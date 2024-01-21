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
from flask_cors import CORS  # Import CORS

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
from .model_class.faculty_profile import FISFaculty
# PDS
from .model_class.pds_model import FISPDS_PersonalDetails,FISPDS_ContactDetails

# LOAD PYDANTIC MODELS
from .model_class.faculty_profile import FISFaculty_Model
# PDS 
from .model_class.pds_model import FISPDS_PersonalDetails_Model,FISPDS_ContactDetails_Model


# ---------------------------------------------------------

# MAIN API V1

# JSON DATA API

API = Blueprint('API', __name__)

# Enable CORS for all routes
CORS(app, origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600)

from sqlalchemy.orm import aliased

@API.route('/api/all/FISFaculty', methods=['GET'])
# @admin_token_required  # Get the API key from the request header
def get_combined_profile():
    # token = request.headers.get('token')  # Get the API key from the request header
    # key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    # key = key['key']

    # if key not in API_KEYS.values():
    #     return jsonify(message="access denied!"), 403

    # else:
        db = SessionLocal()
        try:
            # Perform outer joins with FISFaculty, FISPDS_PersonalDetails, and FISPDS_ContactDetails
            faculty_alias = aliased(FISFaculty)
            personal_details_alias = aliased(FISPDS_PersonalDetails)
            contact_details_alias = aliased(FISPDS_ContactDetails)

            combined_data = db.query(FISFaculty, personal_details_alias, contact_details_alias).outerjoin(
                personal_details_alias, FISFaculty.FacultyId == personal_details_alias.FacultyId
            ).outerjoin(
                contact_details_alias, FISFaculty.FacultyId == contact_details_alias.FacultyId
            ).all()

            # Create a dictionary to store combined data with FacultyId as keys
            combined_profile_by_id = {}

            for faculty, pds_personal_details, pds_contact_details in combined_data:
                faculty_dict = FISFaculty_Model.from_orm(faculty).dict()
                faculty_id = faculty.FacultyId

                if pds_personal_details:
                    faculty_dict['FISPDS_PersonalDetails'] = FISPDS_PersonalDetails_Model.from_orm(pds_personal_details).dict()
                else:
                    faculty_dict['FISPDS_PersonalDetails'] = None

                if pds_contact_details:
                    faculty_dict['FISPDS_ContactDetails'] = FISPDS_ContactDetails_Model.from_orm(pds_contact_details).dict()
                else:
                    faculty_dict['FISPDS_ContactDetails'] = None

                # Store combined data with FacultyId as keys in the dictionary
                combined_profile_by_id[faculty_id] = faculty_dict

            return jsonify({'Faculties': combined_profile_by_id})

        except ValidationError as e:
            return jsonify({'error': f'Validation error: {e}'})
        finally:
            db.close()

# FACULTY DATA 
# -------------------------------------------------------------------------

@API.route('/api/FISFaculty', methods=['GET'])
# @admin_token_required # Get the API key from the request header
def get_all_faculty():
    # token = request.headers.get('token') # Get the API key from the request header
    # key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    # key = key['key']
    
    # if not key in API_KEYS.values():
    #      return jsonify(message="access denied!"), 403
    
    # else:
        db = SessionLocal()
        faculty_profile = db.query(FISFaculty).all()
        db.close()
        try:
            profile = [FISFaculty_Model.from_orm(faculty).dict() for faculty in faculty_profile]
            return jsonify({'Faculties': profile})
        
        
        
        
        except ValidationError as e:
            return jsonify({'error': f'Validation error: {e}'})



@API.route('/api/FISFaculty/<FacultyId>',  methods=['GET', 'POST', 'PUT', 'DELETE'])
# @admin_token_required # Get the API key from the request header
def get_task(FacultyId):
    # token = request.headers.get('token')  # Get the API key from the request header
    # key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    # key = key['key']
    
    # if not key in API_KEYS.values():
    #      return jsonify(message="access denied!"), 403
    
    # else:
        if request.method == 'GET':
            db = SessionLocal()
            faculty_profile = db.query(FISFaculty).filter(FISFaculty.FacultyId == FacultyId).first()
            db.close()
            if faculty_profile is None:
                return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'Faculties': FISFaculty_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        
        elif request.method == 'POST':
            data = request.json
            faculty_profile = FISFaculty_Model(**data)
            db = SessionLocal()
            db_faculty_profile = FISFaculty(**FISFaculty_Model.dict())
            db.add(db_faculty_profile)
            db.commit()
            db.refresh(db_faculty_profile)
            db.close()
            if faculty_profile is None:
                    return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'Faculties': FISFaculty_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
            
            
        elif request.method == 'PUT':
            data = request.json
            db = SessionLocal()
            db_faculty_profile = db.query(FISFaculty).filter(FISFaculty.FacultyId == FacultyId).first()
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
                return jsonify({'Faculties': FISFaculty_Model.from_orm(db_faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        
        elif request.method == 'DELETE':
            db = SessionLocal()
            db_faculty_profile = db.query(FISFaculty).filter(FISFaculty.FacultyId == FacultyId).first()
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

@API.route('/api/FISFaculty/FISPDS_PersonalDetails', methods=['GET'])
# @admin_token_required # Get the API key from the request header
def get_all_pds_personal_details():
    # token = request.headers.get('token')  # Get the API key from the request header
    # key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    # key = key['key']
    
    # if not key in API_KEYS.values():
    #      return jsonify(message="access denied!"), 403
    
    # else:
        db = SessionLocal()
        faculty_profile = db.query(FISPDS_PersonalDetails).all()
        db.close()
        try:
            profile = [FISPDS_PersonalDetails_Model.from_orm(faculty).dict() for faculty in faculty_profile]
            return jsonify({'FISPDS_PersonalDetails': profile})
        except ValidationError as e:
            return jsonify({'error': f'Validation error: {e}'})



@API.route('/api/FISFaculty/FISPDS_PersonalDetails/<FacultyId>',  methods=['GET', 'POST', 'PUT', 'DELETE'])
# @admin_token_required # Get the API key from the request header
def get_pds_personal_details(FacultyId):
    # token = request.headers.get('token')  # Get the API key from the request header
    # key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    # key = key['key']
    
    # if not key in API_KEYS.values():
    #      return jsonify(message="access denied!"), 403
    
    # else:
        if request.method == 'GET':
            db = SessionLocal()
            faculty_profile = db.query(FISPDS_PersonalDetails).filter(FISPDS_PersonalDetails.FacultyId == FacultyId).first()
            db.close()
            if faculty_profile is None:
                return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'FISPDS_PersonalDetails': FISPDS_PersonalDetails_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        
        elif request.method == 'POST':
            data = request.json
            faculty_profile = FISPDS_PersonalDetails_Model(**data)
            db = SessionLocal()
            db_faculty_profile = FISPDS_PersonalDetails(**FISPDS_PersonalDetails_Model.dict())
            db.add(db_faculty_profile)
            db.commit()
            db.refresh(db_faculty_profile)
            db.close()
            if faculty_profile is None:
                    return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'FISPDS_PersonalDetails': FISPDS_PersonalDetails_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
            
            
        elif request.method == 'PUT':
            data = request.json
            db = SessionLocal()
            db_faculty_profile = db.query(FISPDS_PersonalDetails).filter(FISPDS_PersonalDetails.FacultyId == FacultyId).first()
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
                return jsonify({'FISPDS_PersonalDetails': FISPDS_PersonalDetails_Model.from_orm(db_faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        elif request.method == 'DELETE':
            db = SessionLocal()
            db_faculty_profile = db.query(FISPDS_PersonalDetails).filter(FISPDS_PersonalDetails.FacultyId == FacultyId).first()
            if db_faculty_profile is None:
                db.close()
                return jsonify({'error': 'no data found'}), 404
            db.delete(db_faculty_profile)
            db.commit()
            db.close()
            return jsonify({'result': True})
    

 # PDS Contact Details  
# -------------------------------------------------------------------------

@API.route('/api/FISFaculty/FISPDS_ContactDetails', methods=['GET'])
# @admin_token_required # Get the API key from the request header
def get_all_pds_contact_details():
    # token = request.headers.get('token') # Get the API key from the request header
    # key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    # key = key['key']
    
    # if not key in API_KEYS.values():
    #      return jsonify(message="access denied!"), 403
    
    # else:
        db = SessionLocal()
        faculty_profile = db.query(FISPDS_ContactDetails).all()
        db.close()
        try:
            profile = [FISPDS_ContactDetails_Model.from_orm(faculty).dict() for faculty in faculty_profile]
            return jsonify({'FISPDS_ContactDetails': profile})
        except ValidationError as e:
            return jsonify({'error': f'Validation error: {e}'})



@API.route('/api/FISFaculty/FISPDS_ContactDetails/<FacultyId>',  methods=['GET', 'POST', 'PUT', 'DELETE'])
# @admin_token_required # Get the API key from the request header
def get_pds_contact_details(FacultyId):
    # token = request.headers.get('token')  # Get the API key from the request header
    # key = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    # key = key['key']
    
    # if not key in API_KEYS.values():
    #      return jsonify(message="access denied!"), 403
    
    # else:
        if request.method == 'GET':
            db = SessionLocal()
            faculty_profile = db.query(FISPDS_ContactDetails).filter(FISPDS_ContactDetails.FacultyId == FacultyId).first()
            db.close()
            if faculty_profile is None:
                return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'FISPDS_ContactDetails': FISPDS_ContactDetails_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        
        elif request.method == 'POST':
            data = request.json
            faculty_profile = FISPDS_ContactDetails_Model(**data)
            db = SessionLocal()
            db_faculty_profile = FISPDS_ContactDetails(**FISPDS_ContactDetails_Model.dict())
            db.add(db_faculty_profile)
            db.commit()
            db.refresh(db_faculty_profile)
            db.close()
            if faculty_profile is None:
                    return jsonify({'error': 'no data found'}), 404
            try:
                return jsonify({'FISPDS_ContactDetails': FISPDS_ContactDetails_Model.from_orm(faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
            
            
        elif request.method == 'PUT':
            data = request.json
            db = SessionLocal()
            db_faculty_profile = db.query(FISPDS_ContactDetails).filter(FISPDS_ContactDetails.FacultyId == FacultyId).first()
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
                return jsonify({'FISPDS_ContactDetails': FISPDS_ContactDetails_Model.from_orm(db_faculty_profile).dict()})
            except ValidationError as e:
                return jsonify({'error': f'Validation error: {e}'})
        
        elif request.method == 'DELETE':
            db = SessionLocal()
            db_faculty_profile = db.query(FISPDS_ContactDetails).filter(FISPDS_ContactDetails.FacultyId == FacultyId).first()
            if db_faculty_profile is None:
                db.close()
                return jsonify({'error': 'no data found'}), 404
            db.delete(db_faculty_profile)
            db.commit()
            db.close()
            return jsonify({'result': True})
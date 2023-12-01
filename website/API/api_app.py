from flask import Flask, jsonify, request, Blueprint
from flask_restx import Api
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from .authentication import *

import os

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# IMPORTING PYDANTIC CLASS
from pydantic import BaseModel, Field, ValidationError
from typing import Optional


# EXECUTING DATABASE

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy setup

engine=create_engine(os.getenv('DATABASE_URI'), pool_pre_ping=True, pool_size=10, max_overflow=20, pool_recycle=1800)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------

# LOAD MODELS
from .model_class.faculty_profile import Faculty_Profile

# LOAD PYDANTIC MODELS
from .model_class.faculty_profile import Faculty_Profile_Model


# ---------------------------------------------------------

# MAIN API V1

# JSON DATA API

API = Blueprint('API', __name__)

# FACULTY DATA 

@API.route('/api/all/faculty_profile', methods=['GET'])
def get_all_faculty():
    db = SessionLocal()
    faculty_profile = db.query(Faculty_Profile).all()
    db.close()
    try:
        profile = [Faculty_Profile_Model.from_orm(faculty).dict() for faculty in faculty_profile]
        return jsonify({'Faculty_Profile': profile})
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {e}'})



@API.route('/api/all/faculty_profile/<faculty_account_id>', methods=['GET'])
def get_task(faculty_account_id):
    db = SessionLocal()
    faculty_profile = db.query(Faculty_Profile).filter(Faculty_Profile.faculty_account_id == faculty_account_id).first()
    db.close()
    if faculty_profile is None:
        return jsonify({'error': 'faculty profile not found'}), 404
    try:
        return jsonify({'task': Faculty_Profile_Model.from_orm(faculty_profile).dict()})
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {e}'})


@app.route('/api/all/faculty_profile/', methods=['POST'])
def create_task():
    data = request.json
    faculty_profile = Faculty_Profile_Model(**data)
    db = SessionLocal()
    db_faculty_profile = Faculty_Profile(**Faculty_Profile_Model.dict())
    db.add(db_faculty_profile)
    db.commit()
    db.refresh(db_faculty_profile)
    db.close()
    if faculty_profile is None:
            return jsonify({'error': 'faculty profile not found'}), 404
    try:
        return jsonify({'task': Faculty_Profile_Model.from_orm(faculty_profile).dict()})
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {e}'})


@app.route('/api/all/faculty_profile/<faculty_account_id>', methods=['PUT'])
def update_task(faculty_account_id):
    data = request.json
    db = SessionLocal()
    db_faculty_profile = db.query(Faculty_Profile).filter(Faculty_Profile.faculty_account_id == faculty_account_id).first()
    if db_faculty_profile is None:
        db.close()
        return jsonify({'error': 'Task not found'}), 404
    for field, value in data.items():
        setattr(db_faculty_profile, field, value)
    db.commit()
    db.refresh(db_faculty_profile)
    db.close()
    if db_faculty_profile is None:
            return jsonify({'error': 'faculty profile not found'}), 404
    try:
        return jsonify({'task': Faculty_Profile_Model.from_orm(db_faculty_profile).dict()})
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {e}'})


@app.route('/api/all/faculty_profile/<faculty_account_id>', methods=['DELETE'])
def delete_task(task_id):
    db = SessionLocal()
    db_faculty_profile = db.query(Faculty_Profile).filter(Faculty_Profile.faculty_account_id == faculty_account_id).first()
    if db_faculty_profile is None:
        db.close()
        return jsonify({'error': 'Task not found'}), 404
    db.delete(db_faculty_profile)
    db.commit()
    db.close()
    return jsonify({'result': True})

from flask import Flask, Blueprint, abort, flash, json, make_response, redirect, render_template, request, jsonify, url_for
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from flask_login import login_user,login_required, logout_user, current_user, LoginManager
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from flask_mail import Mail,Message
from datetime import datetime, timedelta, timezone

import os,requests

from sqlalchemy.exc import IntegrityError  # Import this for catching database integrity errors
import traceback 


load_dotenv()

# IMPORT LOCAL FUNCTIONS
from website.API.authentication import *
from website.Token.token_gen import *
from website.Token.token_check import Check_Token, SysCheck_Token

# IMPORT SMTP EMAILING FUNCTIONS

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

# DATABASE CONNECTION
from website.models import db
from sqlalchemy import update

# LOADING MODEL CLASSES
from website.models import FISFaculty, FISAdmin, FISUser_Notifications, FISSystemAdmin, FISAdmin_Notifications


# LOAD JWT MODULE
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, decode_token

# EXECUTING DATABASE

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

engine=create_engine(os.getenv('DATABASE_URI'), pool_pre_ping=True, pool_size=10, max_overflow=20, pool_recycle=1800)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------------------------------------------------------------

# SMTP CONFIGURATION

app.config["MAIL_SERVER"]=os.getenv("MAILSERVER") 
app.config["MAIL_PORT"]=os.getenv("MAILPORT") 
app.config["MAIL_USERNAME"] = os.getenv("FISGMAIL")     
app.config['MAIL_PASSWORD'] = os.getenv("FISGMAILPASS")       
app.config['MAIL_DEFAULT_SENDER'] = 'PUPQC FIS'     
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True


# -------------------------------------------------------------

# PYDRIVE AUTH CONFIGURATION
gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# Default Profile Pic
profile_default='14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08'

# -------------------------------------------------------------
# WEB AUTH ROUTES URL
notification = Blueprint('notification', __name__)

# -------------------------------------------------------------

# FACULTY NOTIFICATION API 

  
@notification.route('/api/Faculty/Notifications', methods=['GET', 'POST'])
@login_required
@Check_Token
def notificationFaculty_func():
    
    # Fetch all data from FISRequests
    requests = FISUser_Notifications.query.filter_by(FacultyId=current_user.FacultyId).all() 
    
    # Create a list to store the selected fields for each log entry
    formatted_requests = []
  
    # Iterate over the logs and extract the required fields
    for request in requests:
        # Determine whether it's a Faculty or Admin log entry
        
        # Fetch FirstName from FISFaculty or FISAdmin based on identifier_type
        notifier_name = None
        
        if request.notifier_type == "Admin":
    
            identifier_entry = FISAdmin.query.filter_by(AdminId=request.notif_by).first()

            if identifier_entry:
                notifier_name = identifier_entry.FirstName + " " + identifier_entry.LastName
            
            
            # Create a dictionary with the required data
            formatted_request = {
                'id': request.id,
                'DateTime': request.DateTime.strftime("%Y-%m-%d %H:%M:%S"),  # Format datetime as string
                'Status': request.Status,
                'Type': request.Type,
                'Notification': request.Notification,
                'Notif_By': notifier_name,
                'Profile_Pic': identifier_entry.ProfilePic,
                'IdentifierId': request.notif_by,
                'IdentifierType': request.notifier_type,
                'updated_at': request.updated_at.strftime("%Y-%m-%d %H:%M:%S"), 
            }

            formatted_requests.append(formatted_request)
            
        elif request.notifier_type == "Faculty":
    
            identifier_entry = FISFaculty.query.filter_by(FacultyId=request.notif_by).first()

            if identifier_entry:
                notifier_name = identifier_entry.FirstName + " " + identifier_entry.LastName
            
            
            # Create a dictionary with the required data
            formatted_request = {
                'id': request.id,
                'DateTime': request.DateTime.strftime("%Y-%m-%d %H:%M:%S"),  # Format datetime as string
                'Status': request.Status,
                'Type': request.Type,
                'Notification': request.Notification,
                'Notif_By': notifier_name,
                'Profile_Pic': identifier_entry.ProfilePic,
                'IdentifierId': request.notif_by,
                'IdentifierType': request.notifier_type,
                'updated_at': request.updated_at.strftime("%Y-%m-%d %H:%M:%S"), 
            }

            formatted_requests.append(formatted_request)
        
        else:
    
            identifier_entry = FISSystemAdmin.query.first()

            if identifier_entry:
                notifier_name = identifier_entry.name
            
            
            # Create a dictionary with the required data
            formatted_request = {
                'id': request.id,
                'DateTime': request.DateTime.strftime("%Y-%m-%d %H:%M:%S"),  # Format datetime as string
                'Status': request.Status,
                'Type': request.Type,
                'Notification': request.Notification,
                'Notif_By': notifier_name,
                'Profile_Pic': identifier_entry.ProfilePic,
                'IdentifierId': 'System',
                'IdentifierType': request.notifier_type,
                'updated_at': request.updated_at.strftime("%Y-%m-%d %H:%M:%S"), 
            }

            formatted_requests.append(formatted_request)

    # Create a dictionary with the required data
    api_response_data = {
        'requests': formatted_requests
    }

    # Return the data as JSON using Flask's jsonify
    return jsonify(api_response_data)




# ADMIN NOTIFICATION API 

  
@notification.route('/api/Admin/Notifications', methods=['GET', 'POST'])
@login_required
@Check_Token
def notificationAdmin_func():
    
    # Fetch all data from FISRequests
    requests = FISAdmin_Notifications.query.all() 
    
    # Create a list to store the selected fields for each log entry
    formatted_requests = []
  
    # Iterate over the logs and extract the required fields
    for request in requests:
        # Determine whether it's a Faculty or Admin log entry
        
        # Fetch FirstName from FISFaculty or FISAdmin based on identifier_type
        notifier_name = None
        
        if request.notifier_type == "Admin":
            if request.notif_by == current_user.AdminId:
                pass
                    
            else:  
                identifier_entry = FISAdmin.query.filter_by(AdminId=request.notif_by).first()

                if identifier_entry:
                    notifier_name = identifier_entry.FirstName + " " + identifier_entry.LastName
                
                
                # Create a dictionary with the required data
                formatted_request = {
                    'id': request.id,
                    'DateTime': request.DateTime.strftime("%Y-%m-%d %H:%M:%S"),  # Format datetime as string
                    'Status': request.Status,
                    'Type': request.Type,
                    'Notification': request.Notification,
                    'Notif_By': notifier_name,
                    'Profile_Pic': identifier_entry.ProfilePic,
                    'IdentifierId': request.notif_by,
                    'IdentifierType': request.notifier_type,
                    'updated_at': request.updated_at.strftime("%Y-%m-%d %H:%M:%S"), 
                }

                formatted_requests.append(formatted_request)
            
        elif request.notifier_type == "Faculty":
    
            identifier_entry = FISFaculty.query.filter_by(FacultyId=request.notif_by).first()

            if identifier_entry:
                notifier_name = identifier_entry.FirstName + " " + identifier_entry.LastName
            
            
            # Create a dictionary with the required data
            formatted_request = {
                'id': request.id,
                'DateTime': request.DateTime.strftime("%Y-%m-%d %H:%M:%S"),  # Format datetime as string
                'Status': request.Status,
                'Type': request.Type,
                'Notification': request.Notification,
                'Notif_By': notifier_name,
                'Profile_Pic': identifier_entry.ProfilePic,
                'IdentifierId': request.notif_by,
                'IdentifierType': request.notifier_type,
                'updated_at': request.updated_at.strftime("%Y-%m-%d %H:%M:%S"), 
            }

            formatted_requests.append(formatted_request)
        
        else:
            if request.AdminId != current_user.AdminId:
                pass
                    
            else:     
                identifier_entry = FISSystemAdmin.query.first()

                if identifier_entry:
                    notifier_name = identifier_entry.name
                
                
                # Create a dictionary with the required data
                formatted_request = {
                    'id': request.id,
                    'DateTime': request.DateTime.strftime("%Y-%m-%d %H:%M:%S"),  # Format datetime as string
                    'Status': request.Status,
                    'Type': request.Type,
                    'Notification': request.Notification,
                    'Notif_By': notifier_name,
                    'Profile_Pic': identifier_entry.ProfilePic,
                    'IdentifierId': 'System',
                    'IdentifierType': request.notifier_type,
                    'updated_at': request.updated_at.strftime("%Y-%m-%d %H:%M:%S"), 
                }

                formatted_requests.append(formatted_request)

    # Create a dictionary with the required data
    api_response_data = {
        'requests': formatted_requests
    }

    # Return the data as JSON using Flask's jsonify
    return jsonify(api_response_data)
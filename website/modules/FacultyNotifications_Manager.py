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
facultynotification = Blueprint('facultynotification', __name__)

# -------------------------------------------------------------

# FACULTY NOTIFICATIONS 

       
# ------------------------------- FACULTY NOTIFICATIONS ----------------------------  

@facultynotification.route("/Faculty-Notifications", methods=['GET', 'POST'])
@login_required
@Check_Token
def FN_H():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
         
        done=0
        notifs=0
        read=0
        update=0
        pending=0
        mandatory=0
        trash=0
           
        for notif in current_user.FISUser_Notifications:
            if notif.Type == 'done' :
                done +=1 
            elif notif.Type == 'pending':
                pending += 1
            elif notif.Type == 'read':
                read +=1
            elif notif.Type == 'update':
                update +=1
            elif notif.Type == 'mandatory':
                mandatory +=1
            elif notif.Type == 'trash':
                trash +=1
            else:
                notifs +=1
            

        # if request.method == 'POST':
        
        #     select = request.form.get('select')
            
        #     exams_status = record.exams_status
        #     year = record.year

  
        #     records = {
        #                     'exams_status': exams_status,
        #                     'year': year,
              
        #                 }
        
        return render_template("Faculty-Home-Page/Notifications/index.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               done=done,
                                notifs=notifs,
                                read=read,
                                update=update,
                                pending=pending,
                                mandatory=mandatory,
                                trash=trash,
                            #    records = records,
                               profile_pic=ProfilePic)
        
        

@facultynotification.route("/Faculty-Notifications/read", methods=['GET', 'POST'])
@login_required
@Check_Token
def FN_R():
   # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            id = request.form.get('id')

            u = update(FISUser_Notifications)
            u = u.values({"Type": 'read',"Status": 'read',})
            
            u = u.where(FISUser_Notifications.id == id)
            
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            
            return redirect(url_for('facultynotification.FN_H'))
        


@facultynotification.route("/Faculty-Notifications/unread", methods=['GET', 'POST'])
@login_required
@Check_Token
def FN_UR():
   # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            id = request.form.get('id')

            u = update(FISUser_Notifications)
            u = u.values({"Type": 'notif',"Status": 'read',})
            
            u = u.where(FISUser_Notifications.id == id)
            
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            
            return redirect(url_for('facultynotification.FN_H'))
        

@facultynotification.route("/Faculty-Notifications/trash", methods=['GET', 'POST'])
@login_required
@Check_Token
def FN_T():
    # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            id = request.form.get('id')

            u = update(FISUser_Notifications)
            u = u.values({"Type": 'trash',})
            
            u = u.where(FISUser_Notifications.id == id)
            
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('facultynotification.FN_H'))
        
        
      

@facultynotification.route("/Faculty-Notifications/delete", methods=['GET', 'POST'])
@login_required
@Check_Token
def FN_D():
    # DELETE RECORD
         
        id = request.form.get('id')
        
        data = FISUser_Notifications.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('facultynotification.FN_H'))

  



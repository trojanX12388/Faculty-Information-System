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
from website.models import FISFaculty, FISAdmin, FISLoginToken, FISSystemAdmin


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


mail=Mail(app)

class EmailForm(Form):
    Email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(Form):
    Password = PasswordField('Email', validators=[DataRequired()])

# -------------------------------------------------------------

# PYDRIVE AUTH CONFIGURATION
gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# Default Profile Pic
profile_default='14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08'

# -------------------------------------------------------------
# WEB AUTH ROUTES URL
sysadmin = Blueprint('sysadmin', __name__)

# -------------------------------------------------------------


# -------------------------------------------------------------

# FACULTY RESET PASSWORD ROUTE

# AUTHENTICATION FUNCTION WITH TOKEN KEY TO RESET PASSWORD

def token_required(func):
    # decorator factory which invoks update_wrapper() method and passes decorated function as an argument
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401

        try:

            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
        # You can use the JWT errors in exception
        # except jwt.InvalidTokenError:
        #     return 'Invalid token. Please log in again.'
        except:
            return jsonify({'Message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated

@sysadmin.route('/reset-pass', methods=['GET', 'POST'])
@token_required
def facultyRP():
    token = request.args.get('token')
    user = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    Email = user['user']

    # UPDATE NEW PASSWORD TO THE FACULTY ACCOUNT
    if request.method == 'POST':
        if password1 == password2:
            # Update
            u = update(FISFaculty)
            u = u.values({"Password": generate_password_hash(password1)})
            u = u.where(FISFaculty.Email == Email)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('sysadmin.facultyL')) 
    
    return render_template("Faculty-Login-Page/resetpass.html", Email=Email) 


# -------------------------------------------------------------


# ------------------- SYSTEM ADMIN -----------------------


# SYSTEM ADMIN PAGE ROUTE

@sysadmin.route('/auth/sysadmin/login', methods=['GET', 'POST'])
def sysadminL():
    import random

    session['otp_gained'] = False
    session['sysadminid'] = None
    
    def generate_random_6_digit():
        return random.randint(100000, 999999)
    
    def send_otp_email(otp, Email):
        subject = 'SYSTEM ADMIN OTP CODE'
        sender = ("PUPQC FIS", "fis.pupqc2023@gmail.com")
        recipients = [Email]

        msg = Message(subject, sender=sender, recipients=recipients)
        
        # Construct the HTML body with the OTP code in bold
        msg.html = render_template(
        'Email/otp-code-msg.html',
        otp=otp
        )
    
        # Send the email
        mail.send(msg)
    
    
    if request.method == 'POST':
        id = request.form.get('id')
        Password = request.form.get('password')

        User = FISSystemAdmin.query.filter_by(SystemAdminId=id).first()

        if not User:
            flash('Incorrect ID or Password!', category='error')
        else:
            
            if check_password_hash(User.Password,Password):
                    session['otp_gained'] = True
                    session['sysadminid'] = id
                    
                    random_number = generate_random_6_digit()
                    
                    Email = "fis.pupqc2023@gmail.com"  # Replace with the actual recipient's email
                    send_otp_email(random_number, Email)

                    if FISSystemAdmin.query.filter_by(SystemAdminId=id).first():
                            u = update(FISSystemAdmin)
                            u = u.values({"otp_code": random_number})
                            u = u.where(FISSystemAdmin.SystemAdminId == User.SystemAdminId)
                            db.session.execute(u)
                            db.session.commit()
                            db.session.close()
                            
                    else:
                        add_record = FISSystemAdmin( otp_code = random_number, SystemAdminId = current_user.SystemAdminId)
                    
                        db.session.add(add_record)
                        db.session.commit()
                        db.session.close()
             
             
             
                    return redirect(url_for('sysadmin.sysadminLotp'))   
                    
            else:
                    flash('Invalid Credentials! Please Try again...', category='error')
               
                  
    return render_template("System-Admin-Page/index.html")


# SYSTEM ADMIN OTP LOGIN

@sysadmin.route('/auth/sysadmin/otp-verification', methods=['GET', 'POST'])
def sysadminLotp():
    is_otp_gained = session['otp_gained']
    id = session['sysadminid'] 
    
    if is_otp_gained == True and id != None:
      
        if request.method == 'POST':
            otp_code = request.form.get('otp_code')
            
            User = FISSystemAdmin.query.filter_by(SystemAdminId=id).first()

            if not User:
                flash('Incorrect ID or Password!', category='error')
            else:
                    
                if User.otp_code == otp_code:
                        login_user(User, remember=False)
                        session['otp_gained'] = False
                        session['sysadminid'] = None
                        
                        access_token = generate_access_token(User.SystemAdminId)
                        refresh_token = generate_refresh_token(User.SystemAdminId)
                        
                        if FISSystemAdmin.query.filter_by(SystemAdminId=current_user.SystemAdminId).first():
                            u = update(FISSystemAdmin)
                            u = u.values({"access_token": access_token,
                                        "refresh_token": refresh_token
                                        })
                            u = u.where(FISSystemAdmin.SystemAdminId == User.SystemAdminId)
                            db.session.execute(u)
                            db.session.commit()
                            db.session.close()
                            
                        else:
                            add_record = FISSystemAdmin(   access_token = access_token,
                                                        refresh_token = refresh_token,
                                                        SystemAdminId = current_user.SystemAdminId)
                        
                            db.session.add(add_record)
                            db.session.commit()
                            db.session.close()

                        return redirect(url_for('sysadmin.sysadminH'))   
                        
                else:
                        flash('Invalid OTP Code! Please Try again...', category='error')
               
                  
        return render_template("System-Admin-Page/otp-verification.html")
    
    else:
        return redirect(url_for('sysadmin.sysadminL')) 


# SYSTEM ADMIN OTP LOGIN

@sysadmin.route('/auth/sysadmin/homepage', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminH():
    
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT   
    username = FISSystemAdmin.query.filter_by(SystemAdminId=current_user.SystemAdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')  
                  
    return render_template("System-Admin-Page/base.html",
                            User= username.name,
                            user = current_user,
                            token = selected_token,
                            profile_pic=ProfilePic)
    

@sysadmin.route('/auth/sysadmin/Faculty-Management', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminFM():
    
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT   
    username = FISSystemAdmin.query.filter_by(SystemAdminId=current_user.SystemAdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')  
                  
    return render_template("System-Admin-Page/Faculty-Management.html",
                            User= username.name,
                            user = current_user,
                            token = selected_token,
                            profile_pic=ProfilePic)

# FACULTY LOGOUT ROUTE
@sysadmin.route("/auth/sysadmin/logout")
@login_required
def sysadminLogout():
    session['entry'] = 3
    logout_user()
    flash('Logged Out Successfully!', category='success')
    return redirect(url_for('sysadmin.sysadminL')) 
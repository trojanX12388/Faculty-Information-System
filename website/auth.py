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
from .API.authentication import *
from .Token.token_gen import *
from .Token.token_check import Check_Token, SysCheck_Token

# IMPORT SMTP EMAILING FUNCTIONS

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

# DATABASE CONNECTION
from .models import db
from sqlalchemy import update

# LOADING MODEL CLASSES
from .models import FISFaculty, FISAdmin, FISLoginToken, FISSystemAdmin


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
auth = Blueprint('auth', __name__)

# -------------------------------------------------------------



# -------------------------------------------------------------

# FACULTY PAGE ROUTE

@auth.route('/faculty-login', methods=['GET', 'POST'])
def facultyL():
    if 'entry' not in session:
        session['entry'] = 3  # Set the maximum number of allowed attempts initially

    if request.method == 'POST':
        Email = request.form.get('email')
        year = request.form.get('year')
        month = request.form.get('month')
        day = request.form.get('day')
        Password = request.form.get('password')

        entry = session['entry']
        User = FISFaculty.query.filter_by(Email=Email, IsActive=True).first()

        if not User:
            flash('Incorrect Email or Password!', category='error')
        else:
            year = int(year)
            month = int(month)
            day = int(day)
                
            if check_password_hash(User.Password,Password) and User.BirthDate.year == year and User.BirthDate.month == month and User.BirthDate.day == day:
                    login_user(User, remember=False)
                    access_token = generate_access_token(User.FacultyId)
                    refresh_token = generate_refresh_token(User.FacultyId)
                    
                    if FISLoginToken.query.filter_by(FacultyId=current_user.FacultyId).first():
                        u = update(FISLoginToken)
                        u = u.values({"access_token": access_token,
                                    "refresh_token": refresh_token
                                    })
                        u = u.where(FISLoginToken.FacultyId == User.FacultyId)
                        db.session.execute(u)
                        db.session.commit()
                        db.session.close()
                        
                    else:
                        add_record = FISLoginToken(   access_token = access_token,
                                                    refresh_token = refresh_token,
                                                    FacultyId = current_user.FacultyId)
                    
                        db.session.add(add_record)
                        db.session.commit()
                        db.session.close()
                    session['entry'] = 3
                    return redirect(url_for('auth.facultyH'))   
                    
            else:
                entry -= 1
                if entry == 0:
                    flash('Invalid Credentials! Please Try again...', category='error')
                else:
                    session['entry'] = entry
                    flash('Invalid Credentials! Please Try again...', category='error')
    else:
        flash('Invalid Credentials! Please Try again...', category='error')                 
    return render_template("Faculty-Login-Page/index.html")



# FACULTY RESET ENTRY FOR LOGIN

@app.route('/reset-entry', methods=['POST'])
def reset_entry():
    session['entry'] = 3  # Reset the entry session variable
    return jsonify({'message': 'Entry reset successfully'})

# -------------------------------------------------------------
 
# FACULTY HOME PAGE ROUTE

@auth.route("/faculty-home-page")
@login_required
@Check_Token
def facultyH():
        
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
                                
        return render_template("Faculty-Home-Page/base.html", 
                               User= username.FirstName + " " + username.LastName,
                               user= current_user,
                               profile_pic=ProfilePic)



# -------------------------------------------------------------

# IF USER SESSION IS NULL

@auth.route("/login-denied")
def login_denied():
    return redirect(url_for('views.home'))

@auth.route("/access-denied")
def login_error_modal():
    return render_template('404/error_modal.html')  # Render the template containing your modal


# -------------------------------------------------------------

# FACULTY LOGOUT ROUTE
@auth.route("/logout")
@login_required
def Logout():
    
    
    # # REVOKE USER TOKEN FROM ALL BROWSERS
    # token_list = current_user.FISLoginToken  # This returns a list of FISLoginToken objects
    # if token_list:
    #     # Access the first token from the list
    #     token_id = token_list[0].id  # Assuming you want the first token
    #     user_token = FISLoginToken.query.filter_by(id=token_id, FacultyId=current_user.FacultyId).first()
    #     # Now 'user_token' should contain the specific FISLoginToken object
    #     if user_token:
    #         db.session.delete(user_token)
    #         db.session.commit()
    #         db.session.close()
    # else:
    #     pass
    
    logout_user()
    session['entry'] = 3
    
    flash('Logged Out Successfully!', category='success')
    return redirect(url_for('auth.facultyL')) 


# -------------------------------------------------------------

# FORGOT PASSWORD ROUTE
@auth.route('/request-reset-pass', methods=["POST"])
def facultyF():
    Email = request.form['resetpass']
    User = FISFaculty.query.filter_by(Email=Email).first()
    
    # CHECKING IF ENTERED EMAIL IS NOT IN THE DATABASE
    if request.method == 'POST':
        if not User:
            return render_template("Faculty-Login-Page/Emailnotfound.html", Email=Email) 
        else:
            token = jwt.encode({
                    'user': request.form['resetpass'],
                    # don't foget to wrap it in str function, otherwise it won't work 
                    'exp': (datetime.datetime.utcnow() + timedelta(minutes=15))
                },
                    app.config['SECRET_KEY'])
            
            accesstoken = token
            
            
            Email = request.form['resetpass']
            msg = Message( 
                            'Reset Faculty Password', 
                            sender=("PUPQC FIS", "fis.pupqc2023@gmail.com"),
                            recipients = [Email] 
                        ) 
            assert msg.sender == "PUPQC FIS <fis.pupqc2023@gmail.com>"
            
            recover_url = url_for(
                    'auth.facultyRP',
                    token=accesstoken,
                    _external=True)

            
            msg.html = render_template(
                    'Email/Recover.html',
                    recover_url=recover_url)
            
            msg.body = (accesstoken)
            mail.send(msg)
            return render_template("Faculty-Login-Page/index.html", sentreset=1) 

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

@auth.route('/reset-pass', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.facultyL')) 
    
    return render_template("Faculty-Login-Page/resetpass.html", Email=Email) 


# -------------------------------------------------------------

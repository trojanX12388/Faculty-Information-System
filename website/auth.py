from flask import Flask, Blueprint, abort, flash, json, make_response, redirect, render_template, request, jsonify, url_for, session
from flask_restx import Api, Resource
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from flask_login import login_user,login_required, logout_user, current_user
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from flask_mail import Mail,Message

import psycopg2
import os

load_dotenv()

# IMPORT LOCAL FUNCTIONS
from .API.authentication import *
from .Token.token_gen import *

# IMPORT SMTP EMAILING FUNCTIONS

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

# DATABASE CONNECTION
from .models import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect,update, values
from sqlalchemy.orm.attributes import flag_modified

# LOADING MODEL CLASSES
from .models import Faculty_Profile

# EXECUTING DATABASE

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -------------------------------------------------------------

# SMTP CONFIGURATION

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"] = os.getenv("FISGMAIL")     
app.config['MAIL_PASSWORD'] = os.getenv("FISGMAILPASS")       
app.config['MAIL_DEFAULT_SENDER'] = 'PUPQC FIS'     
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True

mail=Mail(app)

class EmailForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(Form):
    password = PasswordField('Email', validators=[DataRequired()])

# -------------------------------------------------------------


# WEB AUTH ROUTES URL

auth = Blueprint('auth', __name__)


# -------------------------------------------------------------

# FACULTY PAGE ROUTE

@auth.route('/faculty-login', methods=['GET', 'POST'])
def facultyL():

    email = request.form.get('email')
    password = request.form.get('password')

    User = Faculty_Profile.query.filter_by(email=email).first()
    
    # CHECKING IF ENTERED EMAIL IS NOT IN THE DATABASE
    if request.method == 'POST':
        if not User:
            flash('Entered Email is not found in the system.', category='error')  
        
        # USER ACCOUNT VERIFICATION
        else:
            if check_password_hash(User.password,password):
                    session['user'] = email
                    session['faculty_logged_in'] = True
                    login_user(User, remember=True)
                    
                    return redirect(url_for('auth.facultyH'))   
                    
            else:
                flash('Incorrect Password.', category='error')
                          
    return render_template("Faculty-Login-Page/index.html")

# -------------------------------------------------------------

# FACULTY HOME PAGE ROUTE

@auth.route("/faculty-home-page")
@login_required
def facultyH():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(name=current_user.name).first() 
        message = 'Welcome! ' f'{username.name}'
                                
        flash(message, category='success') 
        return render_template("Faculty-Home-Page/home.html", User=current_user)
  
  
# ------------------------------------------------------------- 
      
# IF USER SESSION IS NULL

@auth.route("/faculty-login-denied")
def faculty_denied():
     flash('Session Expired. Please Login again.', category='error')
     return redirect(url_for('auth.facultyL')) 


# -------------------------------------------------------------

# LOGOUT ROUTE
@auth.route("/logout")
@login_required
def Logout():
    session.pop('user', None)
    session.pop('faculty_logged_in', None)
    logout_user()
    flash('Logged Out Successfully!', category='success')
    return redirect(url_for('auth.facultyL')) 


# -------------------------------------------------------------

# FORGOT PASSWORD ROUTE
@auth.route('/request-reset-pass', methods=["POST"])
def facultyF():
    email = request.form['resetpass']
    User = Faculty_Profile.query.filter_by(email=email).first()
    
    # CHECKING IF ENTERED EMAIL IS NOT IN THE DATABASE
    if request.method == 'POST':
        if not User:
            return render_template("Faculty-Login-Page/emailnotfound.html", email=email) 
        else:
            token = jwt.encode({
                    'user': request.form['resetpass'],
                    # don't foget to wrap it in str function, otherwise it won't work [ i struggled with this one! ]
                    'exp': (datetime.utcnow() + timedelta(minutes=15))
                },
                    app.config['SECRET_KEY'])
            accesstoken = token.decode('utf-8')
            
            
            
            email = request.form['resetpass']
            msg = Message( 
                            'Reset Faculty Password', 
                            sender=("PUPQC FIS", "fis.pupqc2023@gmail.com"),
                            recipients = [email] 
                        ) 
            assert msg.sender == "PUPQC FIS <fis.pupqc2023@gmail.com>"
            
            recover_url = url_for(
                    'auth.facultyRP',
                    email=email,
                    token=accesstoken,
                    _external=True)

            
            msg.html = render_template(
                    'Email/Recover.html',
                    recover_url=recover_url)
            
            msg.body = (accesstoken)
            mail.send(msg)
            return render_template("Faculty-Login-Page/index.html", sentreset=1) 

# -------------------------------------------------------------

# RESET PASSWORD ROUTE

# AUTHENTICATION WITH TOKEN KEY TO RESET PASSWORD

def token_required(func):
    # decorator factory which invoks update_wrapper() method and passes decorated function as an argument
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401

        try:

            data = jwt.decode(token, app.config['SECRET_KEY'])
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
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    email = request.args.get('email')

    # UPDATE NEW PASSWORD TO THE FACULTY ACCOUNT
    if request.method == 'POST':
        if password1 == password2:
            # Update
            u = update(Faculty_Profile)
            u = u.values({"password": generate_password_hash(password1)})
            u = u.where(Faculty_Profile.email == email)
            db.session.execute(u)
            db.session.commit()
            return redirect(url_for('auth.facultyL')) 
    
    return render_template("Faculty-Login-Page/resetpass.html", email=email) 


# -------------------------------------------------------------
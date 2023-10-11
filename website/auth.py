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

# FORGOT PASSWORD ROUTE
@auth.route('/request-reset-pass', methods=["POST"])
def facultyF():
    otp = generate_password_hash('sample')
    email = request.form['resetpass']
    msg = Message( 
                    'Reset Faculty Password', 
                    sender=("PUPQC FIS", "fis.pupqc2023@gmail.com"),
                    recipients = [email] 
                ) 
    assert msg.sender == "PUPQC FIS <fis.pupqc2023@gmail.com>"
    msg.body = (otp)
    mail.send(msg)
    return render_template("Faculty-Login-Page/index.html", sentreset=1) 

# -------------------------------------------------------------

# RESET PASSWORD ROUTE

@auth.route('/reset-pass', methods=['GET', 'POST'])
def facultyRP():
    
    # Update
    u = update(Faculty_Profile)
    u = u.values({"password": generate_password_hash('sample123')})
    u = u.where(Faculty_Profile.email == "robertandrewb.up@gmail.com")
    db.session.execute(u)
    db.session.commit()
    
    return render_template("Faculty-Login-Page/resetpass.html") 

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
     
@app.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = Faculty_Profile.query.filter_by(email=form.email.data).first_or_404()

        subject = "Password reset requested"

        # Here we use the URLSafeTimedSerializer we created in `util` at the
        # beginning of the chapter
        token = jwt.encode(Faculty_Profile.email, salt="recover-key")

        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'email/recover.html',
            recover_url=recover_url)

        # SEND EMAIL
        mail.send(user.email, subject, html)

        return redirect(url_for('index'))
    return render_template('reset.html', form=form)
   

# -------------------------------------------------------------

@app.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = jwt.decode(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    form = PasswordForm()

    if form.validate_on_submit():
        user = Faculty_Profile.query.filter_by(email=email).first_or_404()

        user.password = form.password.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('signin'))

    return render_template('reset_with_token.html', form=form, token=token)



# -------------------------------------------------------------
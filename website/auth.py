from flask import Flask, Blueprint, abort, flash, json, make_response, redirect, render_template, request, jsonify, url_for
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from flask_login import login_user,login_required, logout_user, current_user
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from flask_mail import Mail,Message
from datetime import datetime, timedelta, timezone
import jwt
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
from sqlalchemy import update

# LOADING MODEL CLASSES
from .models import Faculty_Profile


# LOAD JWT MODULE
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, decode_token

# EXECUTING DATABASE

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(Form):
    password = PasswordField('Email', validators=[DataRequired()])


app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['REFRESH_TOKEN_SECRET'] = os.getenv('REFRESH_TOKEN_SECRET')
# -------------------------------------------------------------

# PYDRIVE AUTH CONFIGURATION
gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# -------------------------------------------------------------
# WEB AUTH ROUTES URL
auth = Blueprint('auth', __name__)

# -------------------------------------------------------------

# FACULTY PAGE ROUTE
entry = 2

# Default Profile Pic
profile_default='14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08'


@auth.route('/faculty-login', methods=['GET', 'POST'])
def facultyL():

    email = request.form.get('email')
    password = request.form.get('password')
    
    global entry
    
    # CHECKING IF ENTERED EMAIL IS NOT IN THE DATABASE
    if entry != 0:
        if request.method == 'POST':
            User = Faculty_Profile.query.filter_by(email=email).first()
            if not User:
                entry -= 1
                flash('Incorrect email or password!', category='error')  

            # USER ACCOUNT VERIFICATION
            else:
                if check_password_hash(User.password,password):
                        login_user(User, remember=False)
                        access_token = generate_access_token(User.faculty_account_id)
                        refresh_token = generate_refresh_token(User.faculty_account_id)
                        
                        u = update(Faculty_Profile)
                        u = u.values({"access_token": access_token,
                                    "refresh_token": refresh_token
                                    })
                        u = u.where(Faculty_Profile.faculty_account_id == User.faculty_account_id)
                        db.session.execute(u)
                        db.session.commit()
                        db.session.close()
                        
                        return redirect(url_for('auth.facultyH'))   
                        
                else:
                    entry -= 1
                    flash('Incorrect email or password!', category='error')
    else:
        flash('Incorrect attempt... wait 3 minutes to try again.', category='error')   
        entry = 2                 
    return render_template("Faculty-Login-Page/index.html")

# -------------------------------------------------------------
 
# FACULTY HOME PAGE ROUTE

@auth.route("/faculty-home-page")
@login_required
def facultyH():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
        
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/base.html", 
                               User= username.first_name + " " + username.last_name,
                               profile_pic=profile_pic)






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
                    # don't foget to wrap it in str function, otherwise it won't work 
                    'exp': (datetime.datetime.utcnow() + timedelta(minutes=15))
                },
                    app.config['SECRET_KEY'])
            
            accesstoken = token
            
            
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



# -------------------------------------------------------------

# RESET PASSWORD ROUTE

# AUTHENTICATION FUNCTION WITH TOKEN KEY TO RESET PASSWORD

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
            db.session.close()
            return redirect(url_for('auth.facultyL')) 
    
    return render_template("Faculty-Login-Page/resetpass.html", email=email) 


# -------------------------------------------------------------


# # Custom decorator to check access token validity
# def custom_jwt_required():
#     def decorator(fn):
#         def wrapper(*args, **kwargs):
#             access_token = current_user.access_token
#             if not access_token:
#                 return 'Access token is missing', 401

#             # Check if access token exists in the database
#             username = None
#             for user, data in users.items():
#                 if data['access_token'] == access_token:
#                     username = user
#                     break

#             if not username:
#                 return 'Invalid access token', 401

#             # Verify the token using the decode_token function
#             try:
#                 decoded_token = decode_token(access_token)
#                 identity = get_jwt_identity()
#                 if identity != username:
#                     return 'Token does not match user identity', 401
#             except Exception as e:
#                 return 'Token verification failed', 401

#             # If token is valid, call the original function
#             return fn(*args, **kwargs)

#         return wrapper

#     return decorator
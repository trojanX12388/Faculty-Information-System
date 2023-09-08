from flask import Flask, Blueprint, flash, json, make_response, redirect, render_template, request, jsonify, url_for, session
from flask_restx import Api, Resource
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from flask_login import login_user,login_required, logout_user, current_user

import psycopg2
import os

load_dotenv()

# IMPORT LOCAL FUNCTIONS
from .API.authentication import *
from .Token.token_gen import *


# DATABASE CONNECTION
from .models import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

# LOADING MODEL CLASSES
from .models import Faculty_Profile

HOST = os.getenv("HOST")
DB = os.getenv("DB")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

# -------------------------------------------------------------






# -------------------------------------------------------------


# WEB AUTH ROUTES URL

auth = Blueprint('auth', __name__)

# FACULTY PAGE ROUTE

@auth.route('/faculty-login', methods=['GET', 'POST'])
def facultyL():

    email = request.form.get('email')
    password = request.form.get('password')

    User = Faculty_Profile.query.filter_by(email=email).first()
    
    # CHECKING IF ENTERED EMAIL IS NOT IN THE DATABASE
    if request.method == 'POST':
        if not User:
            flash('Entered Email is not found in the system. Please try again.', category='error')  
        
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


@auth.route("/faculty-home-page")
@login_required
def facultyH():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(name=current_user.name).first() 
        message = 'Welcome! ' f'{username.name}'
                                
        flash(message, category='success') 
        return render_template("Faculty-Home-Page/home.html", User=current_user)
   
      
    # IF USER SESSION IS NULL
@auth.route("/faculty-login-denied")
def faculty_denied():
     flash('Session Expired. Please Login again.', category='error')
     return redirect(url_for('auth.facultyL')) 

    # FORGOT PASSWORD ROUTE
@auth.route("/faculty-forgot-pass")
def facultyF():
    return ("<title>Forgot Faculty Password</title><h1>Forgot Password</h1>")

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


# -------------------------------------------------------------
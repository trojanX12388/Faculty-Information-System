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
from sqlalchemy import update, or_

# LOADING MODEL CLASSES
from website.models import FISAdmin, FISAdmin, FISLoginToken, FISSystemAdmin, FISUser_Log, Project, Users

# LOADING FACULTY MODULES
from website.models import FISProfessionalDevelopment, FacultyResearchPaper, ESISUser, IncidentReport, Student, FISMandatoryRequirements, FISMedicalInformation, FISPDS_PersonalDetails


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
admin = Blueprint('admin', __name__)

# -------------------------------------------------------------

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

@admin.route('/reset-pass', methods=['GET', 'POST'])
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
            u = update(FISAdmin)
            u = u.values({"Password": generate_password_hash(password1)})
            u = u.where(FISAdmin.Email == Email)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('admin.adminL')) 
    
    return render_template("Faculty-Login-Page/resetpass.html", Email=Email) 


# -------------------------------------------------------------

# -------------------------------------------------------------

# ADMIN PAGE ROUTE
@admin.route('/admin-login', methods=['GET', 'POST'])
def adminL():
    if 'entry' not in session:
        session['entry'] = 3  # Set the maximum number of allowed attempts initially

    if request.method == 'POST':
        Email = request.form.get('email')
        year = request.form.get('year')
        month = request.form.get('month')
        day = request.form.get('day')
        Password = request.form.get('password')

        entry = session['entry']
        User = FISAdmin.query.filter_by(Email=Email).first()

        if not User:
            flash('Incorrect Email or Password!', category='error')
        elif User.Status == "Disabled":
            flash('Your Account has been disabled. Please contact Administrator to enable your account...', category='error') 
        
        elif User.Status == "Locked":
            flash('Your Account is Locked. Please contact Administrator...', category='error') 
            
        elif User.Status == "Deactivated":
            year = int(year)
            month = int(month)
            day = int(day)

            if User.Login_Attempt != 8:
                u = update(FISAdmin).values({"Login_Attempt": User.Login_Attempt - 1})
                u = u.where(FISAdmin.AdminId == User.AdminId)
                db.session.execute(u)
                db.session.commit()

                if check_password_hash(User.Password, Password) and User.BirthDate.year == year and User.BirthDate.month == month and User.BirthDate.day == day:
                    login_user(User, remember=False)
                    access_token = generate_access_token(User.AdminId)
                    refresh_token = generate_refresh_token(User.AdminId)

                    u = update(FISAdmin).values({"Login_Attempt": 12,
                                                   "Status": "Active",})
                    u = u.where(FISAdmin.AdminId == User.AdminId)
                    db.session.execute(u)
                    db.session.commit()
                        
                    login_token = FISLoginToken.query.filter_by(AdminId=current_user.AdminId).first()
                    if login_token:
                        u = update(FISLoginToken).values({"access_token": access_token,"refresh_token": refresh_token,})
                        u = u.where(FISLoginToken.AdminId == User.AdminId)
                        db.session.execute(u)
                        db.session.commit()
                    else:
                        login_token = FISLoginToken(access_token=access_token, refresh_token=refresh_token, AdminId=current_user.AdminId)
                        db.session.add(login_token)
                        db.session.commit()
                    
                    add_log = FISUser_Log(
                        AdminId=current_user.AdminId,
                        Status= "success",
                        Log = "Activated",
                    )
                    
                    db.session.add(add_log)
                    db.session.commit()
                        
                    db.session.close()    
                    session['entry'] = 3
                    return redirect(url_for('admin.adminH'))

                else:
                    entry -= 1
                    if entry == 0:
                        flash('Your Account is Deactivated, enter the correct password to activate.', category='error')
                    else:
                        session['entry'] = entry
                        flash('Your Account is Deactivated, enter the correct password to activate.', category='error')
                        return redirect(url_for('admin.adminL'))
            
            else:
                u = update(FISAdmin)
                u = u.values({"Status": "Locked",})
                u = u.where(FISAdmin.AdminId == User.AdminId)
                db.session.execute(u)
                db.session.commit()
                
                add_log = FISUser_Log(
                        AdminId=User.AdminId,
                        Status= "alert",
                        Log = "Locked",
                    )
                    
                db.session.add(add_log)
                db.session.commit()
                
                db.session.close()
                flash('Your Account has been locked due to many incorrect attempts.', category='error')
                return redirect(url_for('admin.adminL'))
        
        elif User.Status == "Active":
            year = int(year)
            month = int(month)
            day = int(day)

            if User.Login_Attempt != 0:
                u = update(FISAdmin).values({"Login_Attempt": User.Login_Attempt - 1})
                u = u.where(FISAdmin.AdminId == User.AdminId)
                db.session.execute(u)
                db.session.commit()

                if check_password_hash(User.Password, Password) and User.BirthDate.year == year and User.BirthDate.month == month and User.BirthDate.day == day:
                    login_user(User, remember=False)
                    access_token = generate_access_token(User.AdminId)
                    refresh_token = generate_refresh_token(User.AdminId)

                    u = update(FISAdmin).values({"Login_Attempt": 12})
                    u = u.where(FISAdmin.AdminId == User.AdminId)
                    db.session.execute(u)
                    db.session.commit()
                        
                    login_token = FISLoginToken.query.filter_by(AdminId=current_user.AdminId).first()
                    if login_token:
                        u = update(FISLoginToken).values({"access_token": access_token,"refresh_token": refresh_token,})
                        u = u.where(FISLoginToken.AdminId == User.AdminId)
                        db.session.execute(u)
                        db.session.commit()
                    else:
                        login_token = FISLoginToken(access_token=access_token, refresh_token=refresh_token, AdminId=current_user.AdminId)
                        db.session.add(login_token)
                        db.session.commit()
                    
                    add_log = FISUser_Log(
                        AdminId=current_user.AdminId,
                        Status= "success",
                        Log = "Logged In",
                    )
                    
                    db.session.add(add_log)
                    db.session.commit()
                        
                    db.session.close()    
                    session['entry'] = 3
                    return redirect(url_for('admin.adminH'))

                else:
                    entry -= 1
                    if entry == 0:
                        flash('Invalid Credentials! Please Try again...', category='error')
                    else:
                        session['entry'] = entry
                        flash('Invalid Credentials! Please Try again...', category='error')
                        return redirect(url_for('admin.adminL'))
            
            else:
                u = update(FISAdmin)
                u = u.values({"Status": "Locked",})
                u = u.where(FISAdmin.AdminId == User.AdminId)
                db.session.execute(u)
                db.session.commit()
                
                add_log = FISUser_Log(
                        AdminId=User.AdminId,
                        Status= "alert",
                        Log = "Locked",
                    )
                    
                db.session.add(add_log)
                db.session.commit()
                
                db.session.close()
                flash('Your Account has been locked due to many incorrect attempts.', category='error')
                return redirect(url_for('admin.adminL'))
        else:
           flash('Unknown Account', category='error')  
    else:
        flash('Invalid Credentials! Please Try again...', category='error')                 
    return render_template("Admin-Login-Page/index.html")



# ADMIN HOME PAGE ROUTE

@admin.route("/admin-home-page")
@login_required
@Check_Token
def adminH():    
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT   
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
        
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
            
        API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
        selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
        
        if os.getenv('FLASK_ENV') == 'production':
            base_url = 'https://pupqcfis-com.onrender.com'
        else:
            base_url = 'http://127.0.0.1:8000' 

        endpoint = '/api/all/FISFaculty'
        url = f'{base_url}{endpoint}'
        
        api_key = selected_token

        headers = {
            'Authorization': 'API Key',
            'token': api_key,  # 'token' key with the API key value
            'Content-Type': 'application/json'  # Adjust content type as needed
        }

        # Make a GET request to the API with the API key in the headers
        response = requests.get(url, headers=headers)
        
        total_instructor_I = 0
        total_instructor_II = 0
        total_instructor_III = 0
        total_instructor_IV = 0
        total_instructor_V = 0
        total_assocProf_I = 0
        total_assocProf_II = 0
        total_assocProf_III = 0
        total_assocProf_IV = 0
        total_assocProf_V = 0
        total_assistProf_I = 0
        total_assistProf_II = 0
        total_assistProf_III = 0
        total_assistProf_IV = 0
        total_assistProf_V = 0
        
        instructor = 0
        lecturer = 0
        researcher = 0
        professor = 0
        assistant = 0
        visiting = 0
        associate = 0
        emeritus = 0
        
        faculty_active = 0
        faculty_disabled = 0
        faculty_locked = 0
        faculty_deactivated = 0
        
        # Initialize dictionaries to store counts of part-time and full-time faculty hired each year
        from collections import defaultdict
        from datetime import datetime
        
        instructor_counts = defaultdict(int)
        lecturer_counts = defaultdict(int)
        researcher_counts = defaultdict(int)
        professor_counts = defaultdict(int)
        assistant_counts = defaultdict(int)
        visiting_counts = defaultdict(int)
        associate_counts = defaultdict(int)
        emeritus_counts = defaultdict(int)
        
        
        if response.status_code == 200:
            # Process the API response data
            api_data = response.json()
            FacultyIds = list(api_data['Faculties'].keys())
            
            total_faculty = len(FacultyIds)
            
            for faculty_id in FacultyIds:
                faculty_info = api_data['Faculties'][faculty_id]
                faculty_rank = faculty_info['Rank']
                faculty_type = faculty_info['FacultyType']
                faculty_hired_date = faculty_info['DateHired']
                faculty_status = faculty_info['Status']

                
                if faculty_hired_date:
                    # Convert the date string to a datetime object and extract the year
                    hired_date = datetime.strptime(faculty_hired_date, '%a, %d %b %Y %H:%M:%S %Z')
                    hired_year = hired_date.year

                    # Increment the counts for the respective employment type and year
                    if faculty_type == 'Instructor':
                        instructor_counts[hired_year] += 1
                    elif faculty_type == 'Lecturer':
                        lecturer_counts[hired_year] += 1
                    elif faculty_type == 'Researcher':
                        researcher_counts[hired_year] += 1
                    elif faculty_type == 'Professor':
                        professor_counts[hired_year] += 1
                    elif faculty_type == 'Assistant Professor':
                        assistant_counts[hired_year] += 1
                    elif faculty_type == 'Associate Professor':
                        associate_counts[hired_year] += 1
                    elif faculty_type == 'Visiting Professor':
                        visiting_counts[hired_year] += 1
                    elif faculty_type == 'Emeritus Professor':
                        emeritus_counts[hired_year] += 1

                
                        
                if faculty_type == 'Instructor':
                    instructor += 1
                elif faculty_type == 'Lecturer':
                    lecturer += 1
                elif faculty_type == 'Researcher':
                    researcher += 1
                elif faculty_type == 'Professor':
                    professor += 1
                elif faculty_type == 'Assistant Professor':
                    assistant += 1
                elif faculty_type == 'Associate Professor':
                    associate += 1
                elif faculty_type == 'Visiting Professor':
                    visiting += 1
                elif faculty_type == 'Emeritus Professor':
                    emeritus += 1
                    
                if faculty_rank == 'Instructor I':
                    total_instructor_I += 1
                elif faculty_rank == 'Instructor II':
                    total_instructor_II += 1
                elif faculty_rank == 'Instructor III':
                    total_instructor_III += 1
                elif faculty_rank == 'Instructor IV':
                    total_instructor_IV += 1
                elif faculty_rank == 'Instructor V':
                    total_instructor_V += 1
                    
                elif faculty_rank == 'Associate Professor I':
                    total_assocProf_I += 1
                elif faculty_rank == 'Associate Professor II':
                    total_assocProf_II += 1
                elif faculty_rank == 'Associate Professor III':
                    total_assocProf_III += 1
                elif faculty_rank == 'Associate Professor IV':
                    total_assocProf_IV += 1
                elif faculty_rank == 'Associate Professor V':
                    total_assocProf_V += 1
                    
                elif faculty_rank == 'Assistant Professor I':
                    total_assistProf_I += 1
                elif faculty_rank == 'Assistant Professor II':
                    total_assistProf_II += 1
                elif faculty_rank == 'Assistant Professor III':
                    total_assistProf_III += 1
                elif faculty_rank == 'Assistant Professor IV':
                    total_assistProf_IV += 1
                elif faculty_rank == 'Assistant Professor V':
                    total_assistProf_V += 1


                if faculty_status == 'Active':
                    faculty_active += 1
                elif faculty_status == 'Disabled':
                    faculty_disabled += 1
                elif faculty_status == 'Locked':
                    faculty_locked += 1
                elif faculty_status == 'Deactivated':
                    faculty_deactivated += 1
        
        # Determine the recent year dynamically
        current_year = datetime.now().year

        # Create columns for the recent year and the last six years
        years_range = range(current_year, current_year - 7, -1)
        years_range1 = years_range[0]
        years_range2 = years_range[1]
        years_range3 = years_range[2]
        years_range4 = years_range[3]
        years_range5 = years_range[4]
        years_range6 = years_range[5]
        years_range7 = years_range[6]
        
        total_instructors = total_instructor_I+total_instructor_II+total_instructor_III+total_instructor_IV+total_instructor_V
        total_assistProfs = total_assistProf_I+total_assistProf_II+total_assistProf_III+total_assistProf_IV+total_assistProf_V
        total_assocProfs  = total_assocProf_I+total_assocProf_II+total_assocProf_III+total_assocProf_IV+total_assocProf_V
     
                      
        return render_template("Admin-Home-Page/base.html", 
                               User= username.FirstName + " " + username.LastName,
                               user= current_user,
                               api_data = api_data,
                               
                               total_faculty = total_faculty,
                               FacultyIds = FacultyIds,
                               faculty_info = {faculty_id: api_data['Faculties'][faculty_id] for faculty_id in FacultyIds},
                               
                               total_instructor_I = total_instructor_I,
                               total_instructor_II = total_instructor_II,
                               total_instructor_III = total_instructor_III,
                               total_instructor_IV = total_instructor_IV,
                               total_instructor_V = total_instructor_V,
                               
                               total_assocProf_I = total_assocProf_I,
                               total_assocProf_II = total_assocProf_II,
                               total_assocProf_III = total_assocProf_III,
                               total_assocProf_IV = total_assocProf_IV,
                               total_assocProf_V = total_assocProf_V,
                               
                               total_assistProf_I = total_assistProf_I,
                               total_assistProf_II = total_assistProf_II,
                               total_assistProf_III = total_assistProf_III,
                               total_assistProf_IV = total_assistProf_IV,
                               total_assistProf_V = total_assistProf_V,
                               
                               total_instructors = total_instructors,
                               total_assistProfs = total_assistProfs,
                               total_assocProfs = total_assocProfs,
                               
                               instructor = instructor,
                               lecturer = lecturer,
                               researcher = researcher,
                               professor = professor,
                               assistant = assistant,
                               visiting = visiting,
                               associate = associate,
                               emeritus = emeritus,
                               
                               years_range7 = years_range7,
                               years_range6 = years_range6,
                               years_range5 = years_range5,
                               years_range4 = years_range4,
                               years_range3 = years_range3,
                               years_range2 = years_range2,
                               years_range1 = years_range1,
                               
                               years_range = years_range,
                               
                               instructor_counts = instructor_counts,
                               lecturer_counts = lecturer_counts,
                               researcher_counts = researcher_counts,
                               professor_counts = professor_counts,
                               assistant_counts = assistant_counts,
                               visiting_counts = visiting_counts,
                               associate_counts = associate_counts,
                               emeritus_counts = emeritus_counts,
                               
                               
                               instructor_percentage = "{:.2f}".format((instructor / total_faculty)*100),
                               lecturer_percentage = "{:.2f}".format((lecturer / total_faculty)*100),
                               researcher_percentage = "{:.2f}".format((researcher / total_faculty)*100),
                               professor_percentage = "{:.2f}".format((professor / total_faculty)*100),
                               assistant_percentage = "{:.2f}".format((assistant / total_faculty)*100),
                               visiting_percentage = "{:.2f}".format((visiting / total_faculty)*100),
                               associate_percentage = "{:.2f}".format((associate / total_faculty)*100),
                               emeritus_percentage = "{:.2f}".format((emeritus / total_faculty)*100),
                               
                               
                               total_instructors_percentage = "{:.2f}".format((total_instructors / total_faculty)*100),
                               total_assistProfs_percentage = "{:.2f}".format((total_assistProfs / total_faculty)*100),
                               total_assocProfs_percentage = "{:.2f}".format((total_assocProfs / total_faculty)*100),
                               
                               faculty_active = faculty_active,
                               faculty_locked = faculty_locked,
                               faculty_disabled = faculty_disabled,
                               faculty_deactivated = faculty_deactivated,
                               
                               profile_pic=ProfilePic)

# -------------------------------------------------------------

# ADMIN HOME PAGE ROUTE

@admin.route("/faculty-member/<faculty_id>")
@login_required
@Check_Token
def admin_viewFM(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
        
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/FISFaculty/'+faculty_id
    url = f'{base_url}{endpoint}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()

    date_string = api_data['Faculties']['BirthDate']

    # Parse the string into a datetime object
    date_object = datetime.datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
    BirthDate = date_object.strftime('%b %d %Y')
    
    date_string = api_data['Faculties']['DateHired']

    # Parse the string into a datetime object
    date_object = datetime.datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
    date_hired = date_object.strftime('%b %d %Y')
    
    return render_template("Admin-Home-Page/Faculty/faculty-view.html", 
                           User= username.FirstName + " " + username.LastName,
                           user= current_user,
                           faculty_data = api_data['Faculties'],
                           BirthDate = BirthDate,
                           date_hired = date_hired,
                           profile_pic=ProfilePic)





@admin.route("/faculty-member/<faculty_id>/professional-development")
@login_required
@Check_Token
def admin_viewPD(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/FISFaculty/'+faculty_id
    url = f'{base_url}{endpoint}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()

    date_string = api_data['Faculties']['BirthDate']

    # Parse the string into a datetime object
    date_object = datetime.datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
    BirthDate = date_object.strftime('%b %d %Y')
    
    date_string = api_data['Faculties']['DateHired']

    # Parse the string into a datetime object
    date_object = datetime.datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
    date_hired = date_object.strftime('%b %d %Y')
    
    project = FISProfessionalDevelopment.query.filter_by(FacultyId=faculty_id).all() 
    
    
    return render_template("Admin-Home-Page/Faculty/Professional-Development/Professional-Development.html", 
                           User= username.FirstName + " " + username.LastName,
                           user= current_user,
                           faculty_data = api_data['Faculties'],
                           BirthDate = BirthDate,
                           faculty_id = faculty_id,
                           project = project,
                           date_hired = date_hired,
                           profile_pic=ProfilePic)   
    
 



@admin.route("/faculty-member/<faculty_id>/extension-projects")
@login_required
@Check_Token
def admin_viewExtension(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/FISFaculty/'+faculty_id
    url = f'{base_url}{endpoint}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()

    ESISid = ESISUser.query.filter_by(FacultyId=faculty_id).first()

    if ESISid is not None:
        project = Project.query.filter_by(LeadProponentId=ESISid.UserId).all()
    else:
        project = None
    
    return render_template("Admin-Home-Page/Faculty/Extension-Projects/index.html", 
                           User= username.FirstName + " " + username.LastName,
                           user= current_user,
                           faculty_data = api_data['Faculties'],
                           faculty_id = faculty_id,
                           project = project,
                           profile_pic=ProfilePic)   
    
 




@admin.route("/faculty-member/<faculty_id>/research-publications")
@login_required
@Check_Token
def admin_viewResearch(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/FISFaculty/'+faculty_id
    url = f'{base_url}{endpoint}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()

    
    risid = Users.query.filter_by(faculty_id=faculty_id).first() 
       
    if risid is not None:
        research_publication = FacultyResearchPaper.query.filter_by(user_id=risid.id).all()
    
    else:
        research_publication =  None 
    
    
    return render_template("Admin-Home-Page/Faculty/Research-Publications/Research-Report.html", 
                           User= username.FirstName + " " + username.LastName,
                           user= current_user,
                           faculty_data = api_data['Faculties'],
                           faculty_id = faculty_id,
                           research_publication = research_publication,
                           profile_pic=ProfilePic)   




@admin.route("/faculty-member/<faculty_id>/roles")
@login_required
@Check_Token
def admin_viewRoles(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/FISFaculty/'+faculty_id
    url = f'{base_url}{endpoint}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()

    roles = IncidentReport.query.join(Student, IncidentReport.StudentId == Student.StudentId).\
            add_columns(
                IncidentReport.Date,
                IncidentReport.Time,
                IncidentReport.Description,
                IncidentReport.Status,
                Student.FirstName,
                Student.LastName
            ).\
            filter(IncidentReport.InvestigatorId == faculty_id).all()
    
    if roles is not None:
            faculty_roles = roles
        
    else:
        faculty_roles = None
   
    return render_template("Admin-Home-Page/Faculty/Faculty-Roles/index.html", 
                           User= username.FirstName + " " + username.LastName,
                           user= current_user,
                           faculty_data = api_data['Faculties'],
                           faculty_id = faculty_id,
                           faculty_roles = faculty_roles,
                           profile_pic=ProfilePic)   





@admin.route("/faculty-member/<faculty_id>/mandatory-requirements", methods=['GET', 'POST'])
@login_required
@Check_Token
def admin_viewMandatory(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
    from sqlalchemy import desc

    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/FISFaculty/'+faculty_id
    url = f'{base_url}{endpoint}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()

    faculty_mandatory = FISMandatoryRequirements.query.filter_by(FacultyId=faculty_id).all()

    # VERIFYING IF DATA OF CURRENT USER EXISTS
    if faculty_mandatory:
        if FISMandatoryRequirements.query.filter_by(FacultyId=faculty_id, year=str(datetime.datetime.now().year)).order_by(desc(FISMandatoryRequirements.id)).first():
            record = FISMandatoryRequirements.query.filter_by(FacultyId=faculty_id, year=str(datetime.datetime.now().year)).order_by(desc(FISMandatoryRequirements.id)).first()

            classrecord = record.classrecord
            gradingsheet = record.gradingsheet
            exams = record.exams
            classrecord_status = record.classrecord_status
            gradingsheet_status = record.gradingsheet_status
            exams_status = record.exams_status
            year = record.year


            records = {
                            'classrecord': classrecord,
                            'gradingsheet': gradingsheet,
                            'exams': exams,
                            'classrecord_status': classrecord_status,
                            'gradingsheet_status': gradingsheet_status,
                            'exams_status': exams_status,
                            'year': year,
            
                        }
            
        else:
            records = {
                            'classrecord': "",
                            'gradingsheet': "",
                            'exams': "",
                            'classrecord_status': "None",
                            'gradingsheet_status': "None",
                            'exams_status': "None",
                            'year': str(datetime.datetime.now().year),

                        }
    
    else:
            records = {
                            'classrecord': "",
                            'gradingsheet': "",
                            'exams': "",
                            'classrecord_status': "None",
                            'gradingsheet_status': "None",
                            'exams_status': "None",
                            'year': str(datetime.datetime.now().year),

                        }
                
        
    if request.method == 'POST':
    
        select = request.form.get('select')
        record = FISMandatoryRequirements.query.filter_by(FacultyId=faculty_id, id=select).first()

        classrecord = record.classrecord
        gradingsheet = record.gradingsheet
        exams = record.exams
        classrecord_status = record.classrecord_status
        gradingsheet_status = record.gradingsheet_status
        exams_status = record.exams_status
        year = record.year


        records = {
                        'classrecord': classrecord,
                        'gradingsheet': gradingsheet,
                        'exams': exams,
                        'classrecord_status': classrecord_status,
                        'gradingsheet_status': gradingsheet_status,
                        'exams_status': exams_status,
                        'year': year,
            
                    }
        
        
    return render_template("Admin-Home-Page/Faculty/Mandatory-Requirements/index.html", 
                           User= username.FirstName + " " + username.LastName,
                           user= current_user,
                           faculty_data = api_data['Faculties'],
                           faculty_id = faculty_id,
                           records = records,
                           faculty_mandatory = faculty_mandatory,
                           profile_pic=ProfilePic)   








@admin.route("/faculty-member/<faculty_id>/attendance")
@login_required
@Check_Token
def admin_viewAttendance(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/FISFaculty/'+faculty_id
    url = f'{base_url}{endpoint}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()

    # roles = IncidentReport.query.join(Student, IncidentReport.StudentId == Student.StudentId).\
    #         add_columns(
    #             IncidentReport.Date,
    #             IncidentReport.Time,
    #             IncidentReport.Description,
    #             IncidentReport.Status,
    #             Student.FirstName,
    #             Student.LastName
    #         ).\
    #         filter(IncidentReport.InvestigatorId == faculty_id).all()
    
    # if roles is not None:
    #         faculty_roles = roles
        
    # else:
    #     faculty_roles = None
   
    return render_template("Admin-Home-Page/Faculty/Attendance-Management/index.html", 
                           User= username.FirstName + " " + username.LastName,
                           user= current_user,
                           faculty_data = api_data['Faculties'],
                           faculty_id = faculty_id,
                        #    faculty_roles = faculty_roles,
                           profile_pic=ProfilePic)   





@admin.route("/faculty-member/<faculty_id>/medical-record")
@login_required
@Check_Token
def admin_viewMedical(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/FISFaculty/'+faculty_id
    url = f'{base_url}{endpoint}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()

    is_medical_record =  FISMedicalInformation.query.filter_by(FacultyId=faculty_id).first() 

    if is_medical_record:
            record = is_medical_record  # Assuming you want to get the data from the first entry only

            contact_person_name = record.contact_person_name
            home_contact_number = record.home_contact_number
            address = record.address
            work_phone_number = record.work_phone_number

            # Check and conditionally exclude True/False values
            gridRadiosvaccine = record.gridRadiosvaccine if record.gridRadiosvaccine else "False"
            gridRadiosBooster = record.gridRadiosBooster if record.gridRadiosBooster else "False"

            medical_problem1 = record.medical_problem1
            medical_problem2 = record.medical_problem2
            medical_problem3 = record.medical_problem3
            medical_problem4 = record.medical_problem4
            medical_problem5 = record.medical_problem5
            medical_problem6 = record.medical_problem6

            # Check and conditionally exclude True/False values
            q1 = str(record.q1) if record.q1 is not None else "False"
            q2 = str(record.q2) if record.q2 is not None else "False"
            q3 = str(record.q3) if record.q3 is not None else "False"
    else:
        contact_person_name = ""
        home_contact_number = ""
        address = ""
        work_phone_number = ""
        gridRadiosvaccine = "False"
        gridRadiosBooster = "False"
        medical_problem1 = ""
        medical_problem2 = ""
        medical_problem3 = ""
        medical_problem4 = ""
        medical_problem5 = ""
        medical_problem6 = ""
        q1 = "False"
        q2 = "False"
        q3 = "False"
        
    # Access weight by iterating over the FISPDS_PersonalDetails relationship
    
    faculty = FISPDS_PersonalDetails.query.filter_by(FacultyId=faculty_id).first()  
        
    if faculty:
        weight = faculty.weight
        height = faculty.height

    else:
        weight = 0
        height = 0
   
    return render_template("Admin-Home-Page/Faculty/Medical-Information/index.html", 
                           User= username.FirstName + " " + username.LastName,
                           user= current_user,
                           faculty_data = api_data['Faculties'],
                           faculty_id = faculty_id,
                        #    faculty_roles = faculty_roles,
                            weight=weight,
                            height=height,
                            contact_person_name=contact_person_name,
                            home_contact_number=home_contact_number,
                            address=address,
                            work_phone_number=work_phone_number,
                            gridRadiosvaccine=gridRadiosvaccine,
                            gridRadiosBooster=gridRadiosBooster,
                            medical_problem1=medical_problem1,
                            medical_problem2=medical_problem2,
                            medical_problem3=medical_problem3,
                            medical_problem4=medical_problem4,
                            medical_problem5=medical_problem5,
                            medical_problem6=medical_problem6,
                            q1=q1,
                            q2=q2,
                            q3=q3,
                           profile_pic=ProfilePic)   



@admin.route("/faculty-member/<faculty_id>/absence-leave")
@login_required
@Check_Token
def admin_viewLeave(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/FISFaculty/'+faculty_id
    url = f'{base_url}{endpoint}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()


    return render_template("Admin-Home-Page/Faculty/Leave-Absence-Management/index.html", 
                           User= username.FirstName + " " + username.LastName,
                           user= current_user,
                           faculty_data = api_data['Faculties'],
                           faculty_id = faculty_id,
                        #    faculty_roles = faculty_roles,
                           profile_pic=ProfilePic)   








@admin.route("/faculty-member/<faculty_id>/schedules")
@login_required
@Check_Token
def admin_viewSchedules(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/FISFaculty/'+faculty_id
    url = f'{base_url}{endpoint}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()

    

    return render_template("Admin-Home-Page/Faculty/Schedule-Management/index.html", 
                           User= username.FirstName + " " + username.LastName,
                           user= current_user,
                           faculty_data = api_data['Faculties'],
                           faculty_id = faculty_id,
                        #    faculty_roles = faculty_roles,
                           profile_pic=ProfilePic)   































# -----------------------------------------------------------------
# FORGOT PASSWORD ROUTE
@admin.route('/admin-request-reset-pass', methods=["POST"])
def adminF():
    Email = request.form['resetpass']
    User = FISAdmin.query.filter_by(Email=Email).first()
    
    # CHECKING IF ENTERED EMAIL IS NOT IN THE DATABASE
    if request.method == 'POST':
        if not User:
            return render_template("Admin-Login-Page/Emailnotfound.html", Email=Email) 
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
                            'Reset Admin Password', 
                            sender=("PUPQC FIS", "fis.pupqc2023@gmail.com"),
                            recipients = [Email] 
                        ) 
            assert msg.sender == "PUPQC FIS <fis.pupqc2023@gmail.com>"
            
            recover_url = url_for(
                    'admin.adminRP',
                    token=accesstoken,
                    _external=True)

            
            msg.html = render_template(
                    'Email/Recover.html',
                    recover_url=recover_url)
            
            msg.body = (accesstoken)
            mail.send(msg)
            return render_template("Admin-Login-Page/index.html", sentreset=1) 

# -------------------------------------------------------------

# ADMIN RESET PASSWORD ROUTE

@admin.route('/admin-reset-pass', methods=['GET', 'POST'])
@token_required
def adminRP():
    token = request.args.get('token')
    user = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    Email = user['user']

    # UPDATE NEW PASSWORD TO THE FACULTY ACCOUNT
    if request.method == 'POST':
        if password1 == password2:
            # Update
            u = update(FISAdmin)
            u = u.values({"Password": generate_password_hash(password1)})
            u = u.where(FISAdmin.Email == Email)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('admin.adminL')) 
    
    return render_template("Admin-Login-Page/resetpass.html", Email=Email) 


# -------------------------------------------------------------

# FACULTY LOGOUT ROUTE
@admin.route("/admin-logout")
@login_required
def adminLogout():
    session['entry'] = 3
    
    # # REVOKE USER TOKEN FROM ALL BROWSERS
    # token_list = current_user.FISLoginToken  # This returns a list of FISLoginToken objects
    # if token_list:
    #     # Access the first token from the list
    #     token_id = token_list[0].id  # Assuming you want the first token
    #     user_token = FISLoginToken.query.filter_by(id=token_id, AdminId=current_user.AdminId).first()
    #     # Now 'user_token' should contain the specific FISLoginToken object
    #     if user_token:
    #         db.session.delete(user_token)
    #         db.session.commit()
    #         db.session.close()
    # else:
    #     pass
    
    add_log = FISUser_Log(
                        AdminId=current_user.AdminId,
                        Status= "info",
                        Log = "Logged Out",
                    )
                    
    db.session.add(add_log)
    db.session.commit()
    db.session.close() 
    
    logout_user()
    flash('Logged Out Successfully!', category='success')
    return redirect(url_for('admin.adminL')) 




@admin.route('/api/FISFaculty/Researches', methods=['GET', 'POST'])
@login_required
@Check_Token
def admin_api_research():
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE3_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint1 = '/api/RISUsers/Research_Papers'
    url1 = f'{base_url}{endpoint1}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    all_projects = Project.query.all()

    # Count the number of items
    total_projects = len(all_projects) 
    
    # Make a GET request to the API with the API key in the headers
    response1 = requests.get(url1, headers=headers) 
    
    if response1.status_code == 200:
        # Process the API response data
        api_data = response1.json()
        researches = api_data

        total_researches = len(researches)

        # Create a dictionary with the required data
        api_response_data = {
            'total_researches': total_researches,
            'total_projects': total_projects,
        }

        # Return the data as JSON using Flask's jsonify
        return jsonify(api_response_data)
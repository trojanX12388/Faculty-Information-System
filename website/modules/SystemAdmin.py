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

# calculate age in years
from datetime import date

def calculateAgeFromString(birthdate_str):
    birthdate = datetime.datetime.strptime(birthdate_str, "%Y-%m-%d").date()
    today = date.today()
    
    try:
        birthday = birthdate.replace(year=today.year)
    except ValueError:
        birthday = birthdate.replace(year=today.year, month=birthdate.month + 1, day=1)
    
    if birthday > today:
        return today.year - birthdate.year - 1
    else:
        return today.year - birthdate.year


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
    
    if response.status_code == 200:
        # Process the API response data
        api_data = response.json()
        FacultyIds = list(api_data['Faculties'].keys())
        
    # Format the date before rendering the template
    def format_date(date_str):
        date_object = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
        return date_object.strftime('%b %d, %Y')
    
    # Format the date before rendering the template
    def format_date_2(date_str):
        date_object = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
        return date_object.strftime('%Y-%m-%d')
    
    def extract_day_and_time(schedule_string):
        try:
            # Split the schedule string on ":"
            split_schedule = schedule_string.split(':')

            # Extract day and time variables
            day = split_schedule[0].strip()
            time = ":".join(split_schedule[1:]).strip() if len(split_schedule) > 1 else ""

            return day, time
        except IndexError:
            return "", ""
                  
    return render_template("System-Admin-Page/Faculty-Management.html",
                            User= username.name,
                            user = current_user,
                            
                            api_data = api_data,
                            FacultyIds = FacultyIds,
                            faculty_info = {faculty_id: api_data['Faculties'][faculty_id] for faculty_id in FacultyIds},
                            format_date=format_date,
                            format_date_2= format_date_2,
                            extract_day_and_time = extract_day_and_time,
                            
                            profile_pic=ProfilePic)


# ADD FACULTY ACCOUNT

@sysadmin.route('/auth/sysadmin/Faculty-Management/add-record', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminFM_ADD():
    
    def send_pass_email(password, Email):
        subject = 'FACULTY INFORMATION SYSTEM ACCOUNT'
        sender = ("PUPQC FIS", "fis.pupqc2023@gmail.com")
        recipients = [Email]

        msg = Message(subject, sender=sender, recipients=recipients)
        
        # Construct the HTML body with the OTP code in bold
        msg.html = render_template(
        'Email/new-acc-msg.html',
        password=password
        )
    
        # Send the email
        mail.send(msg)
    
      # INSERT RECORD
    if request.method == 'POST':
        import random
        max_id = db.session.query(func.max(FISFaculty.FacultyId)).scalar()

        # Increment the maximum ID to get the new ID
        new_faculty_id = max_id + 1 if max_id is not None else 1
            
        # VALUES
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')
        middle_initial = request.form.get('middle_initial')
        name_extension = request.form.get('name_extension')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        email = request.form.get('email')
        honorific = request.form.get('honorific')
        res_address = request.form.get('res_address')
        number = request.form.get('number')
        type = request.form.get('type')
        rank = request.form.get('rank')
        units = request.form.get('units')
        degree = request.form.get('degree')
        
        date_hired = request.form.get('date_hired')
        day = request.form.get('day')
        time = request.form.get('time')
        specialization = request.form.get('specialization')
    
        calc_age = calculateAgeFromString(birth_date)
        
        code = random.randint(1000000, 9999999)
        
        password = last_name+'temp'+str(random.randint(1000, 9999))
        
        # Check if email already exists
        existing_email = FISFaculty.query.filter_by(Email=email).first()
        if existing_email:
            flash('Email already exists!', category='error')
            return redirect(url_for('sysadmin.sysadminFM'))
        else:
            # Proceed to add the record
            try:
                add_record = FISFaculty(
                    FacultyId=new_faculty_id,  # Set the new ID
                    Password=generate_password_hash(password),
                    FacultyCode=code,
                    FirstName=first_name,
                    LastName=last_name,
                    MiddleName=middle_name,
                    MiddleInitial=middle_initial,
                    NameExtension=name_extension,
                    Gender=gender,
                    BirthDate=birth_date,
                    Email=email,
                    Age=calc_age,
                    Honorific=honorific,
                    ResidentialAddress=res_address,
                    MobileNumber=number,
                    FacultyType=type,
                    Rank=rank,
                    Units=units,
                    Degree=degree,
                    DateHired=date_hired,
                    PreferredSchedule=day+':'+time,
                    Specialization=specialization,
                    Status= "Deactivated"
                )
                
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                
                send_pass_email(password, email)
                
                flash('Faculty added successfully.', category='success')
            except IntegrityError as e:
                    # Catch database integrity errors, like unique constraint violations
                    db.session.rollback()
                    flash('An error occurred while adding the faculty record. Please try again.', category='error')
                    traceback.print_exc()  # Print detailed error information to console

        return redirect(url_for('sysadmin.sysadminFM'))
        
        
        
# UPDATE FACULTY INFO

@sysadmin.route('/auth/sysadmin/Faculty-Management/update-info', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminFM_update_info():
        
      # UPDATE RECORD
    if request.method == 'POST':
   
        # VALUES
        
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')
        middle_initial = request.form.get('middle_initial')
        name_extension = request.form.get('name_extension')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        email = request.form.get('email')
        honorific = request.form.get('honorific')
        res_address = request.form.get('res_address')
        number = request.form.get('number')
        type = request.form.get('type')
        rank = request.form.get('rank')
        units = request.form.get('units')
        degree = request.form.get('degree')
        
        date_hired = request.form.get('date_hired')
        day = request.form.get('day')
        time = request.form.get('time')
        specialization = request.form.get('specialization')
        id = request.form.get('id')

        calc_age = calculateAgeFromString(birth_date)
        
        PreferredSchedule=day+':'+time,
        
        
        
        try:
            u = update(FISFaculty)
            u = u.values({"FirstName": first_name,
                            "LastName": last_name,
                            "MiddleName": middle_name,
                            "MiddleInitial": middle_initial,
                            "NameExtension": name_extension,
                            "Gender": gender,
                            "BirthDate": birth_date,
                            "Email": email,
                            "Age": calc_age,
                            "Honorific": honorific,
                            "ResidentialAddress": res_address,
                            "MobileNumber": number,
                            "FacultyType": type,
                            "Rank": rank,
                            "Units": units,
                            "Degree": degree,
                            "DateHired": date_hired,
                            "PreferredSchedule": PreferredSchedule,
                            "Specialization": specialization,
                            })
            
            u = u.where(FISFaculty.FacultyId == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            flash('Updated successfully!', category='success')
            
        except:
            flash('Faculty Information was unsuccessfully updated... please try again.', category='error')
                    
        return redirect(url_for('sysadmin.sysadminFM'))


        
# UPDATE FACULTY PASSWORD

@sysadmin.route('/auth/sysadmin/Faculty-Management/update-pass', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminFM_update_pass():
    
    def change_pass_email(password, Email):
        subject = 'FACULTY INFORMATION SYSTEM ACCOUNT CHANGE PASSWORD'
        sender = ("PUPQC FIS", "fis.pupqc2023@gmail.com")
        recipients = [Email]

        msg = Message(subject, sender=sender, recipients=recipients)
        
        # Construct the HTML body with the OTP code in bold
        msg.html = render_template(
        'Email/change-pass-msg.html',
        password=password
        )
    
        # Send the email
        mail.send(msg)   
     
      # UPDATE RECORD
    if request.method == 'POST':
   
        # VALUES
        
        
        new_password = request.form.get('new_password')
        conf_password = request.form.get('conf_password')
        email = request.form.get('email')
        id = request.form.get('id')
        
        if new_password and conf_password:
          
            # CHECK IF NEW AND CONFIRMATION ARE THE SAME
            if not new_password == conf_password:
                flash("New Password and Confirmation do not match.", category="error")
            else:
                hashed_password = generate_password_hash(new_password)
                
                try:
                    u = update(FISFaculty)
                    u = u.values({"Password": hashed_password,})
                    
                    u = u.where(FISFaculty.FacultyId == id)
                    db.session.execute(u)
                    db.session.commit()
                    db.session.close()
                    
                    change_pass_email(new_password, email)
                    flash('Password successfully updated!', category='success')
                    
                except:
                    flash('Faculty Password was unsuccessfully changed... please try again.', category='error')
        else:
            flash("New Password and Confirmation is invalid.", category="error")   
                    
        return redirect(url_for('sysadmin.sysadminFM'))
        
        

        
# UPDATE FACULTY PASSWORD

@sysadmin.route('/auth/sysadmin/Faculty-Management/update-status', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminFM_update_status():
    
      # UPDATE RECORD
    if request.method == 'POST':
   
        # VALUES
        
        status = request.form.get('status')
        id = request.form.get('id')
        
        if status:
            try:
                u = update(FISFaculty)
                u = u.values({"Status": status,})
                u = u.values({"Login_Attempt": 12,})
                
                u = u.where(FISFaculty.FacultyId == id)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                
                flash('Status successfully updated!', category='success')
                
            except:
                flash('Faculty Status was unsuccessfully changed... please try again.', category='error')
        else:
            flash("Invalid Action!.", category="error")   
                    
    return redirect(url_for('sysadmin.sysadminFM'))






# ADMIN MANAGEMENT 


@sysadmin.route('/auth/sysadmin/Admin-Management', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminAM():
    
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT   
    username = FISSystemAdmin.query.filter_by(SystemAdminId=current_user.SystemAdminId).first() 
    
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

    endpoint = '/api/all/FISAdmin'
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
        AdminIds = list(api_data['Admins'].keys())
        
    # Format the date before rendering the template
    def format_date(date_str):
        date_object = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
        return date_object.strftime('%b %d, %Y')
    
    # Format the date before rendering the template
    def format_date_2(date_str):
        date_object = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
        return date_object.strftime('%Y-%m-%d')
    
    def extract_day_and_time(schedule_string):
        try:
            # Split the schedule string on ":"
            split_schedule = schedule_string.split(':')

            # Extract day and time variables
            day = split_schedule[0].strip()
            time = ":".join(split_schedule[1:]).strip() if len(split_schedule) > 1 else ""

            return day, time
        except IndexError:
            return "", ""
                  
    return render_template("System-Admin-Page/Admin-Management.html",
                            User= username.name,
                            user = current_user,
                            
                            api_data = api_data,
                            AdminIds = AdminIds,
                            admin_info = {admin_id: api_data['Admins'][admin_id] for admin_id in AdminIds},
                            format_date=format_date,
                            format_date_2= format_date_2,
                            extract_day_and_time = extract_day_and_time,
                            
                            profile_pic=ProfilePic)


# ADD FACULTY ACCOUNT

@sysadmin.route('/auth/sysadmin/Admin-Management/add-record', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminAM_ADD():
    
    def send_pass_email(password, Email):
        subject = 'FACULTY INFORMATION SYSTEM ADMIN ACCOUNT'
        sender = ("PUPQC FIS", "fis.pupqc2023@gmail.com")
        recipients = [Email]

        msg = Message(subject, sender=sender, recipients=recipients)
        
        # Construct the HTML body with the OTP code in bold
        msg.html = render_template(
        'Email/new-adminacc-msg.html',
        password=password
        )
    
        # Send the email
        mail.send(msg)
    
      # INSERT RECORD
    if request.method == 'POST':
        import random
        max_id = db.session.query(func.max(FISAdmin.AdminId)).scalar()

        # Increment the maximum ID to get the new ID
        new_admin_id = max_id + 1 if max_id is not None else 1
            
        # VALUES
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')
        middle_initial = request.form.get('middle_initial')
        name_extension = request.form.get('name_extension')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        email = request.form.get('email')
        honorific = request.form.get('honorific')
        res_address = request.form.get('res_address')
        number = request.form.get('number')
        type = request.form.get('type')
        rank = request.form.get('rank')
        units = request.form.get('units')
        degree = request.form.get('degree')
        
        date_hired = request.form.get('date_hired')
        day = request.form.get('day')
        time = request.form.get('time')
        specialization = request.form.get('specialization')
    
        calc_age = calculateAgeFromString(birth_date)
        
        code = random.randint(1000000, 9999999)
        
        password = last_name+'temp'+str(random.randint(1000, 9999))
        
        # Check if email already exists
        existing_email = FISAdmin.query.filter_by(Email=email).first()
        if existing_email:
            flash('Email already exists!', category='error')
            return redirect(url_for('sysadmin.sysadminAM'))
        else:
            # Proceed to add the record
            try:
                add_record = FISAdmin(
                    AdminId=new_admin_id,  # Set the new ID
                    Password=generate_password_hash(password),
                    FacultyCode=code,
                    FirstName=first_name,
                    LastName=last_name,
                    MiddleName=middle_name,
                    MiddleInitial=middle_initial,
                    NameExtension=name_extension,
                    Gender=gender,
                    BirthDate=birth_date,
                    Email=email,
                    Age=calc_age,
                    Honorific=honorific,
                    ResidentialAddress=res_address,
                    MobileNumber=number,
                    AdminType=type,
                    Rank=rank,
                    Units=units,
                    Degree=degree,
                    DateHired=date_hired,
                    PreferredSchedule=day+':'+time,
                    Specialization=specialization,
                    Status= "Deactivated"
                )
                
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                
                send_pass_email(password, email)
                
                flash('Admin added successfully.', category='success')
            except IntegrityError as e:
                    # Catch database integrity errors, like unique constraint violations
                    db.session.rollback()
                    flash('An error occurred while adding the admin record. Please try again.', category='error')
                    traceback.print_exc()  # Print detailed error information to console

        return redirect(url_for('sysadmin.sysadminAM'))
        
        
        
# UPDATE FACULTY INFO

@sysadmin.route('/auth/sysadmin/Admin-Management/update-info', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminAM_update_info():
        
      # UPDATE RECORD
    if request.method == 'POST':
   
        # VALUES
        
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')
        middle_initial = request.form.get('middle_initial')
        name_extension = request.form.get('name_extension')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        email = request.form.get('email')
        honorific = request.form.get('honorific')
        res_address = request.form.get('res_address')
        number = request.form.get('number')
        type = request.form.get('type')
        rank = request.form.get('rank')
        units = request.form.get('units')
        degree = request.form.get('degree')
        
        date_hired = request.form.get('date_hired')
        day = request.form.get('day')
        time = request.form.get('time')
        specialization = request.form.get('specialization')
        id = request.form.get('id')

        calc_age = calculateAgeFromString(birth_date)
        
        PreferredSchedule=day+':'+time,
        
        
        
        try:
            u = update(FISAdmin)
            u = u.values({"FirstName": first_name,
                            "LastName": last_name,
                            "MiddleName": middle_name,
                            "MiddleInitial": middle_initial,
                            "NameExtension": name_extension,
                            "Gender": gender,
                            "BirthDate": birth_date,
                            "Email": email,
                            "Age": calc_age,
                            "Honorific": honorific,
                            "ResidentialAddress": res_address,
                            "MobileNumber": number,
                            "AdminType": type,
                            "Rank": rank,
                            "Units": units,
                            "Degree": degree,
                            "DateHired": date_hired,
                            "PreferredSchedule": PreferredSchedule,
                            "Specialization": specialization,
                            })
            
            u = u.where(FISAdmin.AdminId == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            flash('Updated successfully!', category='success')
            
        except:
            flash('Admin Information was unsuccessfully updated... please try again.', category='error')
                    
        return redirect(url_for('sysadmin.sysadminAM'))


        
# UPDATE FACULTY PASSWORD

@sysadmin.route('/auth/sysadmin/Admin-Management/update-pass', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminAM_update_pass():
    
    def change_pass_email(password, Email):
        subject = 'FACULTY INFORMATION SYSTEM ADMIN ACCOUNT CHANGE PASSWORD'
        sender = ("PUPQC FIS", "fis.pupqc2023@gmail.com")
        recipients = [Email]

        msg = Message(subject, sender=sender, recipients=recipients)
        
        # Construct the HTML body with the OTP code in bold
        msg.html = render_template(
        'Email/change-adminpass-msg.html',
        password=password
        )
    
        # Send the email
        mail.send(msg)   
     
      # UPDATE RECORD
    if request.method == 'POST':
   
        # VALUES
        
        new_password = request.form.get('new_password')
        conf_password = request.form.get('conf_password')
        email = request.form.get('email')
        id = request.form.get('id')
        
        if new_password and conf_password:
          
            # CHECK IF NEW AND CONFIRMATION ARE THE SAME
            if not new_password == conf_password:
                flash("New Password and Confirmation do not match.", category="error")
            else:
                hashed_password = generate_password_hash(new_password)
                
                try:
                    u = update(FISAdmin)
                    u = u.values({"Password": hashed_password,})
                    
                    u = u.where(FISAdmin.AdminId == id)
                    db.session.execute(u)
                    db.session.commit()
                    db.session.close()
                    
                    change_pass_email(new_password, email)
                    flash('Password successfully updated!', category='success')
                    
                except:
                    flash('Admin Password was unsuccessfully changed... please try again.', category='error')
        else:
            flash("New Password and Confirmation is invalid.", category="error")   
                    
        return redirect(url_for('sysadmin.sysadminAM'))
        
        

        
# UPDATE FACULTY PASSWORD

@sysadmin.route('/auth/sysadmin/Admin-Management/update-status', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminAM_update_status():
    
      # UPDATE RECORD
    if request.method == 'POST':
   
        # VALUES
        
        status = request.form.get('status')
        id = request.form.get('id')
        
        if status:
            try:
                u = update(FISAdmin)
                u = u.values({"Status": status,})
                u = u.values({"Login_Attempt": 12,})
                
                u = u.where(FISAdmin.AdminId == id)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                
                flash('Status successfully updated!', category='success')
                
            except:
                flash('Admin Status was unsuccessfully changed... please try again.', category='error')
        else:
            flash("Invalid Action!.", category="error")   
                    
    return redirect(url_for('sysadmin.sysadminAM'))


# FACULTY LOGOUT ROUTE
@sysadmin.route("/auth/sysadmin/logout")
@login_required
def sysadminLogout():
    session['entry'] = 3
    logout_user()
    flash('Logged Out Successfully!', category='success')
    return redirect(url_for('sysadmin.sysadminL')) 
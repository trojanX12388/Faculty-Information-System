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
from website.models import FISFaculty, FISAdmin, FISLoginToken, FISSystemAdmin, FISSystemAdmin_Log, FISUser_Log, FISRequests


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
    
                  
    return render_template("System-Admin-Page/base.html",
                            User= username.name,
                            user = current_user,
                            
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
                
                add_log = FISSystemAdmin_Log(
                    FacultyId=new_faculty_id,  # Set the new ID
                    Status= "success",
                    Log = "Create Account",
                )
                
                db.session.add(add_log)
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

            db.session.close()
            
            add_log = FISSystemAdmin_Log(
                    FacultyId=id,  # Set the new ID
                    Status= "update",
                    Log = "Update Info",
                )
                
            db.session.add(add_log)
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
                    
                    add_log = FISSystemAdmin_Log(
                    FacultyId=id,  # Set the new ID
                    Status= "update",
                    Log = "Update Password",
                )
                
                    db.session.add(add_log)
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
                
                if status == "Disabled":
                    add_log = FISSystemAdmin_Log(
                        FacultyId=id,  # Set the new ID
                        Status= "alert",
                        Log = "Disable Account",
                    )
                    
                    db.session.add(add_log)
                    db.session.commit()
                
                else:   
                    add_log = FISSystemAdmin_Log(
                        FacultyId=id,  # Set the new ID
                        Status= "update",
                        Log = "Update Status to "  + str(status),
                    )
                    
                    db.session.add(add_log)
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
                
                add_log = FISSystemAdmin_Log(
                    AdminId=new_admin_id,  # Set the new ID
                    Status= "success",
                    Log = "Create Account",
                )
                
                db.session.add(add_log)
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
            
            add_log = FISSystemAdmin_Log(
                    AdminId=id,  # Set the new ID
                    Status= "update",
                    Log = "Update Info",
                )
                
            db.session.add(add_log)
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
                    
                    add_log = FISSystemAdmin_Log(
                    AdminId=id,  # Set the new ID
                    Status= "update",
                    Log = "Update Password",
                )
                
                    db.session.add(add_log)
                    db.session.commit()
                    
                    db.session.close()
                    
                    change_pass_email(new_password, email)
                    flash('Password successfully updated!', category='success')
                    
                except:
                    flash('Admin Password was unsuccessfully changed... please try again.', category='error')
        else:
            flash("New Password and Confirmation is invalid.", category="error")   
                    
        return redirect(url_for('sysadmin.sysadminAM'))
        
        

        
# UPDATE FACULTY STATUS

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
                
                if status == "Disabled":
                    add_log = FISSystemAdmin_Log(
                        AdminId=id,  # Set the new ID
                        Status= "alert",
                        Log = "Disable Account",
                    )
                    
                    db.session.add(add_log)
                    db.session.commit()
                
                else:   
                    add_log = FISSystemAdmin_Log(
                        AdminId=id,  # Set the new ID
                        Status= "update",
                        Log = "Update Status to "  + str(status),
                    )
                    
                    db.session.add(add_log)
                    db.session.commit()
                
                db.session.close()
                
                flash('Status successfully updated!', category='success')
                
            except:
                flash('Admin Status was unsuccessfully changed... please try again.', category='error')
        else:
            flash("Invalid Action!.", category="error")   
                    
    return redirect(url_for('sysadmin.sysadminAM'))


        

# SYSTEM ADMIN REQUESTS PAGE 


@sysadmin.route('/auth/sysadmin/Requests', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminR():
    
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT   
    username = FISSystemAdmin.query.filter_by(SystemAdminId=current_user.SystemAdminId).first() 
    
    if username.ProfilePic == None:
        ProfilePic=profile_default
    else:
        ProfilePic=username.ProfilePic
    
                  
    return render_template("System-Admin-Page/Requests.html",
                            User= username.name,
                            user = current_user,
                            
                            profile_pic=ProfilePic)



# UPDATE REQUESTS

@sysadmin.route('/auth/sysadmin/Requests/action', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadminAM_update_requests():
    
      # UPDATE RECORD
    if request.method == 'POST':
   
        # VALUES
        
        value = request.form.get('value')
        status = request.form.get('status')
        id = request.form.get('id')
        
        try:
            if status == "pending":
                u = update(FISRequests)
                u = u.values({"Status": value,})
                
                u = u.where(FISRequests.id == id)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
           
                flash('successfully done!', category='success')
                
            elif status == "declined" or status == "done":
                
                data = FISRequests.query.filter_by(id=id).first() 
                db.session.delete(data)
                db.session.commit()
                db.session.close()
           
                flash('successfully deleted!', category='success')
            
        except:
            flash('Request was unsuccessfully updated... please try again.', category='error')
       
                   
    return redirect(url_for('sysadmin.sysadminR'))






# ------------------------------- SETTINGS ------------------------------

@sysadmin.route("/auth/sysadmin/Settings", methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadmin_Settings():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    
        # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT   
        username = FISSystemAdmin.query.filter_by(SystemAdminId=current_user.SystemAdminId).first() 
        
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
        
        # UPDATE 
        
        if request.method == 'POST':
            from werkzeug.security import generate_password_hash
            from werkzeug.security import check_password_hash
         
            # VALUES
           
            password = request.form.get('password')
            newpassword = request.form.get('newpassword')
            renewpassword = request.form.get('renewpassword')
            
            if check_password_hash(current_user.Password, password):

                if newpassword == renewpassword:
                    Password=generate_password_hash(newpassword)
                    
                    u = update(FISSystemAdmin)
                    u = u.values({"Password": Password})
                    
                    u = u.where(FISSystemAdmin.SystemAdminId == current_user.SystemAdminId)
                    db.session.execute(u)
                    db.session.commit()
                    db.session.close()
                    
                    flash('Password successfully updated!', category='success')
                    return redirect(url_for('sysadmin.sysadmin_Settings'))
                 
                else:
                    flash('Invalid input! Password does not match...', category='error')
                    return redirect(url_for('sysadmin.sysadmin_Settings')) 
            else:
                flash('Invalid input! Password does not match...', category='error')
                return redirect(url_for('sysadmin.sysadmin_Settings')) 
                                
        return render_template("System-Admin-Page/Settings.html", 
                               User= username.name,
                               profile_pic=ProfilePic,
                               user = current_user,
                               )










































# FACULTY LOGOUT ROUTE
@sysadmin.route("/auth/sysadmin/logout")
@login_required
def sysadminLogout():
    session['entry'] = 3
    logout_user()
    flash('Logged Out Successfully!', category='success')
    return redirect(url_for('sysadmin.sysadminL')) 











# ----------------------------------------------------------------------------------




# SYS ADMIN API 

@sysadmin.route('/auth/sysadmin/api/FISData', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadmin_api_Faculty():
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint1 = '/api/all/FISFaculty'
    url1 = f'{base_url}{endpoint1}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Initialize dictionaries to store counts of part-time and full-time faculty hired each year
    from collections import defaultdict
    from datetime import datetime
    
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

    # Make a GET request to the API with the API key in the headers
    response1 = requests.get(url1, headers=headers) 
    
    if response1.status_code == 200:
        # Process the API response data
        api_data = response1.json()
        FacultyIds = list(api_data['Faculties'].keys())
    
        # Process the API response data
        api_data = response1.json()
        FacultyIds = list(api_data['Faculties'].keys())

        faculty_active = 0
        faculty_disabled = 0
        faculty_locked = 0
        faculty_deactivated = 0
        
        faculty_years_range1 = 0
        faculty_years_range2 = 0
        faculty_years_range3 = 0
        faculty_years_range4 = 0
        faculty_years_range5 = 0
        faculty_years_range6 = 0
        faculty_years_range7 = 0

        total_faculty = len(FacultyIds)

        for faculty_id in FacultyIds:
            faculty_info = api_data['Faculties'][faculty_id]
            faculty_status = faculty_info['Status']
            faculty_hired_date = faculty_info['created_at']

            if faculty_status == 'Active':
                faculty_active += 1
            elif faculty_status == 'Disabled':
                faculty_disabled += 1
            elif faculty_status == 'Locked':
                faculty_locked += 1
            elif faculty_status == 'Deactivated':
                faculty_deactivated += 1
                
            
            if faculty_hired_date:
            # Convert the date string to a datetime object and extract the year
                hired_date = datetime.strptime(faculty_hired_date, '%a, %d %b %Y %H:%M:%S %Z')
                hired_year = hired_date.year

                # Increment the counts for the respective employment type and year
                if hired_year == years_range1:
                    faculty_years_range1 += 1
                elif hired_year == years_range2:
                    faculty_years_range2 += 1
                elif hired_year == years_range3:
                    faculty_years_range3 += 1
                elif hired_year == years_range4:
                    faculty_years_range4 += 1
                elif hired_year == years_range5:
                    faculty_years_range5 += 1
                elif hired_year == years_range6:
                    faculty_years_range6 += 1
                elif hired_year == years_range7:
                    faculty_years_range7 += 1
    
    # ADMINS
        
    endpoint2 = '/api/all/FISAdmin'
    url2 = f'{base_url}{endpoint2}'
    
    api_key = selected_token

    # Make a GET request to the API with the API key in the headers
    response2 = requests.get(url2, headers=headers) 
    
    if response2.status_code == 200:
        # Process the API response data
        api_data2 = response2.json()
        AdminIds = list(api_data2['Admins'].keys())
    
        # Process the API response data
        api_data2 = response2.json()
        AdminIds = list(api_data2['Admins'].keys())

        # Initialize dictionaries to store counts of part-time and full-time faculty hired each year
        from collections import defaultdict
        from datetime import datetime

        admin_added = defaultdict(int)
        full_time_counts = defaultdict(int)

        admin_active = 0
        admin_disabled = 0
        admin_locked = 0
        admin_deactivated = 0
        
        admin_years_range1 = 0
        admin_years_range2 = 0
        admin_years_range3 = 0
        admin_years_range4 = 0
        admin_years_range5 = 0
        admin_years_range6 = 0
        admin_years_range7 = 0

        total_admin = len(AdminIds)

        for admin_id in AdminIds:
            admin_info = api_data2['Admins'][admin_id]
            admin_status = admin_info['Status']
            admin_hired_date = admin_info['created_at']

            if admin_status == 'Active':
                admin_active += 1
            elif admin_status == 'Disabled':
                admin_disabled += 1
            elif admin_status == 'Locked':
                admin_locked += 1
            elif admin_status == 'Deactivated':
                admin_deactivated += 1

            if admin_hired_date:
                # Convert the date string to a datetime object and extract the year
                hired_date2 = datetime.strptime(admin_hired_date, '%a, %d %b %Y %H:%M:%S %Z')
                hired_year2 = hired_date2.year   
                
                # Increment the counts for the respective employment type and year
                if hired_year2 == years_range1:
                    admin_years_range1 += 1
                elif hired_year2 == years_range2:
                    admin_years_range2 += 1
                elif hired_year2 == years_range3:
                    admin_years_range3 += 1
                elif hired_year2 == years_range4:
                    admin_years_range4 += 1
                elif hired_year2 == years_range5:
                    admin_years_range5 += 1
                elif hired_year2 == years_range6:
                    admin_years_range6 += 1
                elif hired_year2 == years_range7:
                    admin_years_range7 += 1

        
        # Create a dictionary with the required data
        api_response_data = {
            'total_faculty': total_faculty,
            'total_admin': total_admin,
            'faculty_active': faculty_active + admin_active,
            'faculty_disabled': faculty_disabled + admin_disabled,
            'faculty_locked': faculty_locked + admin_locked,
            'faculty_deactivated': faculty_deactivated + admin_deactivated,
            
            'hired_year': hired_year,
            
            'years_range1': years_range1,
            'years_range2': years_range2,
            'years_range2': years_range2,
            'years_range3': years_range3,
            'years_range4': years_range4,
            'years_range5': years_range5,
            'years_range6': years_range6,
            'years_range7': years_range7,
            
            'faculty_years_range1': faculty_years_range1,
            'faculty_years_range2': faculty_years_range2,
            'faculty_years_range3': faculty_years_range3,
            'faculty_years_range4': faculty_years_range4,
            'faculty_years_range5': faculty_years_range5,
            'faculty_years_range6': faculty_years_range6,
            'faculty_years_range7': faculty_years_range7,
            
            'admin_years_range1': admin_years_range1,
            'admin_years_range2': admin_years_range2,
            'admin_years_range3': admin_years_range3,
            'admin_years_range4': admin_years_range4,
            'admin_years_range5': admin_years_range5,
            'admin_years_range6': admin_years_range6,
            'admin_years_range7': admin_years_range7,
            
           "chart_data": [
            {"year": years_range7, "value": faculty_years_range7},
            {"year": years_range6, "value": faculty_years_range6},
            {"year": years_range5, "value": faculty_years_range5},
            {"year": years_range4, "value": faculty_years_range4},
            {"year": years_range3, "value": faculty_years_range3},
            {"year": years_range2, "value": faculty_years_range2},
            {"year": years_range1, "value": faculty_years_range1},
        ],
           
           "chart_data2": [
            {"year": years_range7, "value": admin_years_range7},
            {"year": years_range6, "value": admin_years_range6},
            {"year": years_range5, "value": admin_years_range5},
            {"year": years_range4, "value": admin_years_range4},
            {"year": years_range3, "value": admin_years_range3},
            {"year": years_range2, "value": admin_years_range2},
            {"year": years_range1, "value": admin_years_range1},
        ],
           
        }

        # Return the data as JSON using Flask's jsonify
        return jsonify(api_response_data)
   
@sysadmin.route('/auth/sysadmin/api/User-Log', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadmin_api_user_log():
    
    # Fetch all data from FISUser_Log
    logs = FISUser_Log.query.all()

    # Create a list to store the selected fields for each log entry
    formatted_logs = []

    # Iterate over the logs and extract the required fields
    for log in logs:
        # Determine whether it's a Faculty or Admin log entry
        identifier_type = 'FacultyId' if log.FacultyId is not None else 'AdminId'

        # Fetch FirstName from FISFaculty or FISAdmin based on identifier_type
        identifier_name = None
        if identifier_type == 'FacultyId':
            identifier_entry = FISFaculty.query.filter_by(FacultyId=log.FacultyId).first()
        elif identifier_type == 'AdminId':
            identifier_entry = FISAdmin.query.filter_by(AdminId=log.AdminId).first()

        if identifier_entry:
            identifier_name = identifier_entry.FirstName + " " + identifier_entry.LastName

        # Create a dictionary with the required data
        formatted_log = {
            'id': log.id,
            'DateTime': log.DateTime.strftime("%Y-%m-%d %H:%M:%S"),  # Format datetime as string
            'Status': log.Status,
            'Log': log.Log + " " + identifier_name,
            'IdentifierType': identifier_type,
            'IdentifierValue': log.FacultyId or log.AdminId,  # Choose the available identifier
            'IdentifierName': identifier_name  # Add IdentifierName to the response
        }

        formatted_logs.append(formatted_log)

    # Create a dictionary with the required data
    api_response_data = {
        'logs': formatted_logs
    }

    # Return the data as JSON using Flask's jsonify
    return jsonify(api_response_data)
    
@sysadmin.route('/auth/sysadmin/api/System-Admin-Log', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadmin_api_sysadmin_log():
    
    # Fetch all data from FISSystemAdmin_Log
    logs = FISSystemAdmin_Log.query.all()

    # Create a list to store the selected fields for each log entry
    formatted_logs = []

    # Iterate over the logs and extract the required fields
    for log in logs:
        # Determine whether it's a Faculty or Admin log entry
        identifier_type = 'FacultyId' if log.FacultyId is not None else 'AdminId'

        # Fetch FirstName from FISFaculty or FISAdmin based on identifier_type
        identifier_name = None
        if identifier_type == 'FacultyId':
            identifier_entry = FISFaculty.query.filter_by(FacultyId=log.FacultyId).first()
        elif identifier_type == 'AdminId':
            identifier_entry = FISAdmin.query.filter_by(AdminId=log.AdminId).first()

        if identifier_entry:
            identifier_name = identifier_entry.FirstName + " " + identifier_entry.LastName
        
        # Create a dictionary with the required data
        formatted_log = {
            'id': log.id,
            'DateTime': log.DateTime.strftime("%Y-%m-%d %H:%M:%S"),  # Format datetime as string
            'Status': log.Status,
            'Log': log.Log + " " + "of" + " " + identifier_name,
            'IdentifierType': identifier_type,
            'IdentifierValue': log.FacultyId or log.AdminId  # Choose the available identifier
        }

        formatted_logs.append(formatted_log)

    # Create a dictionary with the required data
    api_response_data = {
        'logs': formatted_logs
    }

    # Return the data as JSON using Flask's jsonify
    return jsonify(api_response_data)

  
@sysadmin.route('/auth/sysadmin/api/Requests', methods=['GET', 'POST'])
@login_required
@SysCheck_Token
def sysadmin_api_sysadmin_requests():
    
    # Fetch all data from FISRequests
    requests = FISRequests.query.all()

    # Create a list to store the selected fields for each log entry
    formatted_requests = []

    # Iterate over the logs and extract the required fields
    for request in requests:
        # Determine whether it's a Faculty or Admin log entry
        identifier_type = 'FacultyId' if request.FacultyId is not None else 'AdminId'

        # Fetch FirstName from FISFaculty or FISAdmin based on identifier_type
        identifier_name = None
        if identifier_type == 'FacultyId':
            identifier_entry = FISFaculty.query.filter_by(FacultyId=request.FacultyId).first()
        elif identifier_type == 'AdminId':
            identifier_entry = FISAdmin.query.filter_by(AdminId=request.AdminId).first()

        if identifier_entry:
            identifier_name = identifier_entry.FirstName + " " + identifier_entry.LastName
        
        # Create a dictionary with the required data
        formatted_request = {
            'id': request.id,
            'DateTime': request.DateTime.strftime("%Y-%m-%d %H:%M:%S"),  # Format datetime as string
            'Status': request.Status,
            'Request': request.Request,
            'IdentifierType': identifier_type,
            'IdentifierName': identifier_name,
            'Profile_Pic': identifier_entry.ProfilePic,
            'IdentifierId': request.FacultyId or request.AdminId,  # Choose the available identifier
            'updated_at': request.updated_at.strftime("%Y-%m-%d %H:%M:%S"), 
        }

        formatted_requests.append(formatted_request)

    # Create a dictionary with the required data
    api_response_data = {
        'requests': formatted_requests
    }

    # Return the data as JSON using Flask's jsonify
    return jsonify(api_response_data)
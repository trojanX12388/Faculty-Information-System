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
from .Token.token_check import Check_Token

# IMPORT SMTP EMAILING FUNCTIONS

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

# DATABASE CONNECTION
from .models import db
from sqlalchemy import update

# LOADING MODEL CLASSES
from .models import Faculty_Profile, Admin_Profile, Login_Token


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
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(Form):
    password = PasswordField('Email', validators=[DataRequired()])

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
        email = request.form.get('email')
        year = request.form.get('year')
        month = request.form.get('month')
        day = request.form.get('day')
        password = request.form.get('password')

        entry = session['entry']
        User = Faculty_Profile.query.filter_by(email=email).first()

        if not User:
            flash('Incorrect email or password!', category='error')
        else:
            year = int(year)
            month = int(month)
            day = int(day)
                
            if check_password_hash(User.password,password) and User.birth_date.year == year and User.birth_date.month == month and User.birth_date.day == day:
                    login_user(User, remember=False)
                    access_token = generate_access_token(User.faculty_account_id)
                    refresh_token = generate_refresh_token(User.faculty_account_id)
                    
                    if Login_Token.query.filter_by(faculty_account_id=current_user.faculty_account_id).first():
                        u = update(Login_Token)
                        u = u.values({"access_token": access_token,
                                    "refresh_token": refresh_token
                                    })
                        u = u.where(Login_Token.faculty_account_id == User.faculty_account_id)
                        db.session.execute(u)
                        db.session.commit()
                        db.session.close()
                        
                    else:
                        add_record = Login_Token(   access_token = access_token,
                                                    refresh_token = refresh_token,
                                                    faculty_account_id = current_user.faculty_account_id)
                    
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
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
        
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/base.html", 
                               User= username.first_name + " " + username.last_name,
                               user= current_user,
                               profile_pic=profile_pic)



# -------------------------------------------------------------

# IF USER SESSION IS NULL

@auth.route("/login-denied")
def login_denied():
    return redirect(url_for('auth.login_error_modal'))

@auth.route("/access-denied")
def login_error_modal():
    return render_template('404/error_modal.html')  # Render the template containing your modal


# -------------------------------------------------------------

# FACULTY LOGOUT ROUTE
@auth.route("/logout")
@login_required
def Logout():
    
    # # REVOKE USER TOKEN FROM ALL BROWSERS
    # token_list = current_user.Login_Token  # This returns a list of Login_Token objects
    # if token_list:
    #     # Access the first token from the list
    #     token_id = token_list[0].id  # Assuming you want the first token
    #     user_token = Login_Token.query.filter_by(id=token_id, faculty_account_id=current_user.faculty_account_id).first()
    #     # Now 'user_token' should contain the specific Login_Token object
    #     if user_token:
    #         db.session.delete(user_token)
    #         db.session.commit()
    #         db.session.close()
    # else:
    #     pass
    
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

    email = user['user']

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

# -------------------------------------------------------------

# ADMIN PAGE ROUTE

@auth.route('/admin-login', methods=['GET', 'POST'])
def adminL():
    if 'entry' not in session:
        session['entry'] = 3  # Set the maximum number of allowed attempts initially

    if request.method == 'POST':
        email = request.form.get('email')
        year = request.form.get('year')
        month = request.form.get('month')
        day = request.form.get('day')
        password = request.form.get('password')

        entry = session['entry']
        User = Admin_Profile.query.filter_by(email=email).first()

        if not User:
            flash('Incorrect email or password!', category='error')
        else:
            year = int(year)
            month = int(month)
            day = int(day)
                
            if check_password_hash(User.password,password) and User.birth_date.year == year and User.birth_date.month == month and User.birth_date.day == day:
                    login_user(User, remember=False)
                    access_token = generate_access_token(User.admin_account_id)
                    refresh_token = generate_refresh_token(User.admin_account_id)
                    
                    if Login_Token.query.filter_by(admin_account_id=current_user.admin_account_id).first():
                        u = update(Login_Token)
                        u = u.values({"access_token": access_token,
                                    "refresh_token": refresh_token
                                    })
                        u = u.where(Login_Token.admin_account_id == User.admin_account_id)
                        db.session.execute(u)
                        db.session.commit()
                        db.session.close()
                        
                    else:
                        add_record = Login_Token(   access_token = access_token,
                                                    refresh_token = refresh_token,
                                                    admin_account_id = current_user.admin_account_id)
                    
                        db.session.add(add_record)
                        db.session.commit()
                        db.session.close()
                    session['entry'] = 3
                    return redirect(url_for('auth.adminH'))   
                    
            else:
                entry -= 1
                if entry == 0:
                    flash('Invalid Credentials! Please Try again...', category='error')
                else:
                    session['entry'] = entry
                    flash('Invalid Credentials! Please Try again...', category='error')
    else:
        flash('Invalid Credentials! Please Try again...', category='error')                 
    return render_template("Admin-Login-Page/index.html")


# ADMIN HOME PAGE ROUTE

@auth.route("/admin-home-page")
@login_required
@Check_Token
def adminH():
        
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Admin_Profile.query.filter_by(admin_account_id=current_user.admin_account_id).first() 
        
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
            
        API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
        selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
        
        if os.getenv('FLASK_ENV') == 'production':
            base_url = 'https://pupqcfis-com.onrender.com'
        else:
            base_url = 'http://127.0.0.1:8000' 

        endpoint = '/api/all/Faculty_Profile'
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
        
        full_time = 0
        part_time = 0
        
        # Initialize dictionaries to store counts of part-time and full-time faculty hired each year
        from collections import defaultdict
        from datetime import datetime
        
        part_time_counts = defaultdict(int)
        full_time_counts = defaultdict(int)
        
        if response.status_code == 200:
            # Process the API response data
            api_data = response.json()
            faculty_account_ids = list(api_data['Faculties'].keys())
            
            total_faculty = len(faculty_account_ids)
            
            for faculty_id in faculty_account_ids:
                faculty_info = api_data['Faculties'][faculty_id]
                faculty_rank = faculty_info['rank']
                faculty_type = faculty_info['faculty_type']
                faculty_hired_date = faculty_info['date_hired']

                if faculty_hired_date:
                    # Convert the date string to a datetime object and extract the year
                    hired_date = datetime.strptime(faculty_hired_date, '%a, %d %b %Y %H:%M:%S %Z')
                    hired_year = hired_date.year

                    # Increment the counts for the respective employment type and year
                    if faculty_type == 'Part Time':
                        part_time_counts[hired_year] += 1
                    elif faculty_type == 'Full Time':
                        full_time_counts[hired_year] += 1

                
                        
                if faculty_type == 'Full Time':
                    full_time += 1
                else:
                    part_time += 1
                    
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
     
        def count_faculty_tokens_with_account_ids(session: Session):
            # Counting Login_Token entries where faculty_account_id is not null
            count = session.query(func.count()).filter(Login_Token.faculty_account_id.isnot(None)).scalar()
            return count
        
        db = SessionLocal()  # Assuming you have your session initialized
        faculty_active = count_faculty_tokens_with_account_ids(db)
        db.close()  # Remember to close the session when you're done
                              
        return render_template("Admin-Home-Page/base.html", 
                               User= username.first_name + " " + username.last_name,
                               user= current_user,
                               api_data = api_data,
                               
                               total_faculty = total_faculty,
                               faculty_account_ids = faculty_account_ids,
                               
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
                               
                               full_time = full_time,
                               part_time = part_time,
                               
                               years_range1 = years_range1,
                               years_range2 = years_range2,
                               years_range3 = years_range3,
                               years_range4 = years_range4,
                               years_range5 = years_range5,
                               years_range6 = years_range6,
                               years_range7 = years_range7,
                               
                               years_range = years_range,
                               part_time_counts = part_time_counts,
                               full_time_counts = full_time_counts,
                               
                               full_time_percentage = "{:.2f}".format((full_time / total_faculty)*100),
                               part_time_percentage = "{:.2f}".format((part_time / total_faculty)*100),
                               
                               total_instructors_percentage = "{:.2f}".format((total_instructors / total_faculty)*100),
                               total_assistProfs_percentage = "{:.2f}".format((total_assistProfs / total_faculty)*100),
                               total_assocProfs_percentage = "{:.2f}".format((total_assocProfs / total_faculty)*100),
                               
                               faculty_active = faculty_active,
                               profile_pic=profile_pic)

# -------------------------------------------------------------

# ADMIN HOME PAGE ROUTE

@auth.route("/faculty-member/<faculty_id>")
@login_required
@Check_Token
def admin_viewFM(faculty_id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = Admin_Profile.query.filter_by(admin_account_id=current_user.admin_account_id).first() 
    
    if username.profile_pic == None:
        profile_pic=profile_default
    else:
        profile_pic=username.profile_pic
        
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint = '/api/Faculty_Profile/'+faculty_id
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

    date_string = api_data['Faculty_Profile']['birth_date']

    # Parse the string into a datetime object
    date_object = datetime.datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
    birth_date = date_object.strftime('%b %d %Y')
    
    date_string = api_data['Faculty_Profile']['date_hired']

    # Parse the string into a datetime object
    date_object = datetime.datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
    date_hired = date_object.strftime('%b %d %Y')
    
    return render_template("Admin-Home-Page/Faculty/faculty-view.html", 
                           User= username.first_name + " " + username.last_name,
                           user= current_user,
                           faculty_data = api_data['Faculty_Profile'],
                           birth_date = birth_date,
                           date_hired = date_hired,
                           profile_pic=profile_pic)


# -----------------------------------------------------------------
# FORGOT PASSWORD ROUTE
@auth.route('/admin-request-reset-pass', methods=["POST"])
def adminF():
    email = request.form['resetpass']
    User = Admin_Profile.query.filter_by(email=email).first()
    
    # CHECKING IF ENTERED EMAIL IS NOT IN THE DATABASE
    if request.method == 'POST':
        if not User:
            return render_template("Admin-Login-Page/emailnotfound.html", email=email) 
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
                            'Reset Admin Password', 
                            sender=("PUPQC FIS", "fis.pupqc2023@gmail.com"),
                            recipients = [email] 
                        ) 
            assert msg.sender == "PUPQC FIS <fis.pupqc2023@gmail.com>"
            
            recover_url = url_for(
                    'auth.adminRP',
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

@auth.route('/admin-reset-pass', methods=['GET', 'POST'])
@token_required
def adminRP():
    token = request.args.get('token')
    user = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    email = user['user']

    # UPDATE NEW PASSWORD TO THE FACULTY ACCOUNT
    if request.method == 'POST':
        if password1 == password2:
            # Update
            u = update(Admin_Profile)
            u = u.values({"password": generate_password_hash(password1)})
            u = u.where(Admin_Profile.email == email)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('auth.adminL')) 
    
    return render_template("Admin-Login-Page/resetpass.html", email=email) 


# -------------------------------------------------------------

# FACULTY LOGOUT ROUTE
@auth.route("/admin-logout")
@login_required
def adminLogout():
    
    # # REVOKE USER TOKEN FROM ALL BROWSERS
    # token_list = current_user.Login_Token  # This returns a list of Login_Token objects
    # if token_list:
    #     # Access the first token from the list
    #     token_id = token_list[0].id  # Assuming you want the first token
    #     user_token = Login_Token.query.filter_by(id=token_id, faculty_account_id=current_user.faculty_account_id).first()
    #     # Now 'user_token' should contain the specific Login_Token object
    #     if user_token:
    #         db.session.delete(user_token)
    #         db.session.commit()
    #         db.session.close()
    # else:
    #     pass
    
    logout_user()
    flash('Logged Out Successfully!', category='success')
    return redirect(url_for('auth.adminL')) 
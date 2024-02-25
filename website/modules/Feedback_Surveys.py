from flask import Flask, Blueprint, redirect, render_template, request, url_for, jsonify
from dotenv import load_dotenv
from flask_login import login_required, current_user
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from urllib.request import urlretrieve
from cryptography.fernet import Fernet
import rsa

import os,requests,ast
import os.path

load_dotenv()

# DATABASE CONNECTION
from website.models import db
from sqlalchemy import update, desc

# LOADING MODEL CLASSES
from website.models import FISFaculty, FISEvaluations

# LOADING FUNCTION CHECK TOKEN
from website.Token.token_check import Check_Token

# WEB AUTH ROUTES URL
FS = Blueprint('FS', __name__)

# -------------------------------------------------------------

# PYDRIVE AUTH CONFIGURATION
gauth = GoogleAuth()
drive = GoogleDrive(gauth)


# -------------------------------------------------------------

# ENCRYPTION / DECRYPTION

private_key = rsa.PrivateKey.load_pkcs1(os.getenv('PRIVATE_KEY'))

with open(os.path.dirname(__file__) + '/../key/filekey.key', "rb") as f:
    enckey = f.read()

key = rsa.decrypt(enckey,private_key)

# using the generated key
fernet = Fernet(key)

# -------------------------------------------------------------

# Default Profile Pic
profile_default='14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08'



# -------------------------------------------------------------


#                                                    AWARDS AND RECOGNITIONS ROUTE


# ------------------------------- AWARDS AND RECOGNITIONS ----------------------------  

@FS.route("/Feedback-Surveys", methods=['GET', 'POST'])
@login_required
@Check_Token
def FS_H():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
                      
        return render_template("Faculty-Home-Page/Feedback-Survey/index.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               profile_pic=ProfilePic)

 
# ------------------------------------------------------------- 



@FS.route("/Feedback-Surveys/add-record", methods=['GET', 'POST'])
@login_required
def FS_add():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            from datetime import datetime
            
            # VALUES
           
            averageInputA = request.form.get('averageInputA')
            averageInputB = request.form.get('averageInputB')
            averageInputC = request.form.get('averageInputC')
            averageInputD = request.form.get('averageInputD')
            AverageRate = request.form.get('AverageRate')
            semester = request.form.get('SEMESTER')
            schoolYear = request.form.get('School_Year')
            FacultyId = request.form.get('select')
            
            print(AverageRate)
            print(semester)
            print(schoolYear)
            print(FacultyId)
            
            # Get the highest ID using order_by and desc
            highest_id_record = FISEvaluations.query.order_by(desc(FISEvaluations.id)).first()

            school_year = datetime.strptime(f"{schoolYear}-02-02 00:00:00", "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S.000 +0800")
            
            add_record = FISEvaluations(id=highest_id_record.id+1,
                                        FacultyId=FacultyId,
                                        peer=AverageRate,
                                        peer_a=averageInputA,
                                        peer_b=averageInputB,
                                        peer_c=averageInputC,
                                        peer_d=averageInputD,
                                        school_year=school_year,
                                        semester=semester,
                                        Type = current_user.FacultyType,
                                        Evaluator_Name = str(current_user.LastName + ', ' + current_user.FirstName + ' ' + current_user.MiddleInitial),
                                        EvaluatorId = current_user.FacultyId)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('FS.FS_H'))
        



@FS.route('/Feedback-Surveys/FISFaculty', methods=['GET', 'POST'])
@login_required
@Check_Token
def FS_requests_faculties():
    
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

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url1, headers=headers) 
    
    if response.status_code == 200:
            # Process the API response data
            api_data1 = response.json()
            
            return jsonify(api_data1)
        

@FS.route('/Feedback-Surveys/FISFaculty/Evaluations', methods=['GET', 'POST'])
@login_required
@Check_Token
def FS_requests_evaluations():
    
    API_TOKENS = ast.literal_eval(os.environ["API_TOKENS"])
    selected_token = API_TOKENS.get('WEBSITE1_API_TOKEN')
    
    if os.getenv('FLASK_ENV') == 'production':
        base_url = 'https://pupqcfis-com.onrender.com'
    else:
        base_url = 'http://127.0.0.1:8000' 

    endpoint1 = '/api/FISFaculty/Evaluations_secret'
    url1 = f'{base_url}{endpoint1}'
    
    api_key = selected_token

    headers = {
        'Authorization': 'API Key',
        'token': api_key,  # 'token' key with the API key value
        'Content-Type': 'application/json'  # Adjust content type as needed
    }

    # Make a GET request to the API with the API key in the headers
    response = requests.get(url1, headers=headers) 
    
    if response.status_code == 200:
            # Process the API response data
            api_data1 = response.json()
            
            return jsonify(api_data1)


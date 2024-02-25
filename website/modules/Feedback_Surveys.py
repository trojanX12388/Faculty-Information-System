from flask import Flask, Blueprint, redirect, render_template, request, url_for, jsonify, flash
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
            
            school_year = datetime.strptime(f"{schoolYear}-02-02 00:00:00", "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S.000 +0800")

            # Get the highest ID using order_by and desc
            highest_id_record = FISEvaluations.query.order_by(desc(FISEvaluations.id)).first()

            
            if FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester, EvaluatorId = current_user.FacultyId).first():
                try:
                    u = update(FISEvaluations)
                    u = u.values({"peer": AverageRate,
                                "peer_a": averageInputA,
                                "peer_b": averageInputB,
                                "peer_c": averageInputC,
                                "peer_d": averageInputD,
                                "EvaluatorId": current_user.FacultyId,
                                "Evaluator_Name": str(current_user.LastName + ', ' + current_user.FirstName + ' ' + current_user.MiddleInitial),
                                })
                    
                    u = u.where((FISEvaluations.FacultyId == FacultyId) & (FISEvaluations.school_year == school_year) & (FISEvaluations.semester == semester) & (FISEvaluations.EvaluatorId == current_user.FacultyId))
                    db.session.execute(u)
                    db.session.commit()
                    
                    flash('Evaluated successfully1!', category='success')
                    print("success1")
                    db.session.close()   
                    return redirect(url_for('FS.FS_H'))

                except Exception as e:
                    print(f"An error occurred1: {str(e)}")
                    db.session.rollback()  # Rollback changes in case of an error
                    flash('An error occurred while evaluating!', category='error')
                       
                    return redirect(url_for('FS.FS_H'))
                
            elif not FISEvaluations.query.filter_by(FacultyId=current_user.FacultyId, school_year = school_year, semester = semester).first():
                try:
                    add_record = FISEvaluations(id=highest_id_record.id+1,
                                                FacultyId=FacultyId,
                                                
                                                acad_head=0,
                                                acad_head_a=0,
                                                acad_head_b=0,
                                                acad_head_c=0,
                                                acad_head_d=0,
                                                
                                                director=0,
                                                director_a=0,
                                                director_b=0,
                                                director_c=0,
                                                director_d=0,
                                                
                                                student=0,
                                                student_a=0,
                                                student_b=0,
                                                student_c=0,
                                                student_d=0,
                                                
                                                self_eval=AverageRate,
                                                self_a=averageInputA,
                                                self_b=averageInputB,
                                                self_c=averageInputC,
                                                self_d=averageInputD,
                                                
                                                peer=0,
                                                peer_a=0,
                                                peer_b=0,
                                                peer_c=0,
                                                peer_d=0,
                                                
                                                school_year=school_year,
                                                semester=semester,
                                                Type = current_user.FacultyType,
                                                Evaluator_Name = str(current_user.LastName + ', ' + current_user.FirstName + ' ' + current_user.MiddleInitial),
                                                EvaluatorId = current_user.FacultyId)
                    db.session.add(add_record)
                    db.session.commit() 
                    flash('Evaluated successfully3!', category='success')
                    print("success3")
                    db.session.close()   
                    return redirect(url_for('FS.FS_H')) 
                 
                except Exception as e:
                    print(f"An error occurred3: {str(e)}")
                    db.session.rollback()  # Rollback changes in case of an error
                    flash('An error occurred while evaluating!', category='error') 
                      
                    return redirect(url_for('FS.FS_H'))
                
            elif not FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester, EvaluatorId = current_user.FacultyId).first():
                try:
  
                    add_record = FISEvaluations(
                        id=highest_id_record.id + 1,
                        FacultyId=FacultyId,
                        AdminId=None,  # Set to appropriate value if needed
                        Evaluator_Name=str(current_user.LastName + ', ' + current_user.FirstName + ' ' + current_user.MiddleInitial),
                        EvaluatorId=current_user.FacultyId,
                        Type=current_user.FacultyType,
                        acad_head=0,
                        acad_head_a=0,
                        acad_head_b=0,
                        acad_head_c=0,
                        acad_head_d=0,
                        director=0,
                        director_a=0,
                        director_b=0,
                        director_c=0,
                        director_d=0,
                        self_eval=0,
                        self_a=0,
                        self_b=0,
                        self_c=0,
                        self_d=0,
                        peer=AverageRate,  # Make sure AverageRate is defined
                        peer_a=averageInputA,
                        peer_b=averageInputB,
                        peer_c=averageInputC,
                        peer_d=averageInputD,
                        student=0,
                        student_a=0,
                        student_b=0,
                        student_c=0,
                        student_d=0,
                        school_year=school_year,
                        semester=semester,
                        is_delete=False,
                    )

                    db.session.add(add_record)
                    db.session.commit()
                    flash('Evaluated successfully4!', category='success')
                    print("success4")
                    db.session.close()
                    return redirect(url_for('FS.FS_H'))

                except Exception as e:
                    print(f"An error occurred4: {str(e)}")
                    db.session.rollback()
                    flash('An error occurred while evaluating!', category='error')
                    return redirect(url_for('FS.FS_H'))
                
            else:
                try:
                    u = update(FISEvaluations)
                    u = u.values({"self_eval": AverageRate,
                                "self_a": averageInputA,
                                "self_b": averageInputB,
                                "self_c": averageInputC,
                                "self_d": averageInputD,
                                "EvaluatorId": current_user.FacultyId,
                                "Evaluator_Name": str(current_user.LastName + ', ' + current_user.FirstName + ' ' + current_user.MiddleInitial),
                                })
                    
                    u = u.where((FISEvaluations.FacultyId == current_user.FacultyId) & (FISEvaluations.school_year == school_year) & (FISEvaluations.semester == semester))
                    db.session.execute(u)
                    db.session.commit()
                    
                    flash('Evaluated successfully2!', category='success')
                    print("success2")
                    db.session.close()   
                    return redirect(url_for('FS.FS_H'))
                
                except Exception as e:
                    print(f"An error occurred2: {str(e)}")
                    db.session.rollback()  # Rollback changes in case of an error
                    flash('An error occurred while evaluating!', category='error')
                       
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


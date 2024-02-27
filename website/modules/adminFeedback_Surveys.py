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
from sqlalchemy import update, desc, text

# LOADING MODEL CLASSES
from website.models import FISAdmin, FISEvaluations, FISUser_Notifications, FISAdmin

# LOADING FUNCTION CHECK TOKEN
from website.Token.token_check import Check_Token

# WEB AUTH ROUTES URL
aFS = Blueprint('aFS', __name__)

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

@aFS.route("/Admin-Feedback-Surveys", methods=['GET', 'POST'])
@login_required
@Check_Token
def aFS_H():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
                      
        return render_template("Admin-Home-Page/Feedback-Survey/index.html", 
                               User= username.FirstName + " " + username.LastName,
                               user= current_user,
                               profile_pic=ProfilePic)

 
# ------------------------------------------------------------- 



@aFS.route("/Admin-Feedback-Surveys/add-record", methods=['GET', 'POST'])
@login_required
def aFS_add():

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
            acad_head = 0
            director_head = 0
            
            if current_user.AdminType == "Academic Head":
                if FISEvaluations.query.filter_by(FacultyId=FacultyId,semester=semester, school_year = school_year ).first():
                    evaluation_item_id = FISEvaluations.query.filter_by(FacultyId=FacultyId,semester=semester, school_year = school_year ).first()
                    if evaluation_item_id.acad_head_ids == 'None':
                        eval_id = str(current_user.AdminId)
                    else:
                        eval_id  = evaluation_item_id.acad_head_ids+","+str(current_user.AdminId)
                else:
                    eval_id = str(current_user.AdminId)
            else:
                if FISEvaluations.query.filter_by(FacultyId=FacultyId,semester=semester, school_year = school_year ).first():
                    evaluation_item_id = FISEvaluations.query.filter_by(FacultyId=FacultyId,semester=semester, school_year = school_year ).first()
                    if evaluation_item_id.director_ids == 'None':
                        eval_id = str(current_user.AdminId)
                    else:
                        eval_id  = evaluation_item_id.director_ids+","+str(current_user.AdminId)
                else:
                    eval_id = str(current_user.AdminId)
            
            if current_user.AdminType == "Academic Head":
                acad_head = 1
                if FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester).first():
                    data = FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester).first() 
                    try:
                        u = update(FISEvaluations)
                        
                        if(data.acad_head == 0):
                            u = u.values({"acad_head": AverageRate,
                                        "acad_head_a": averageInputA,
                                        "acad_head_b": averageInputB,
                                        "acad_head_c": averageInputC,
                                        "acad_head_d": averageInputD,
                                        "acad_head_ids": eval_id,
                                        "acad_head_evaluators": text("acad_head_evaluators + 1"),
                                        })
                        else:
                            u = u.values({"acad_head": (float(data.acad_head) + float(AverageRate)) / 2,
                                        "acad_head_a": (float(data.acad_head_a) + float(averageInputA)) / 2,
                                        "acad_head_b": (float(data.acad_head_b) + float(averageInputB)) / 2,
                                        "acad_head_c": (float(data.acad_head_c) + float(averageInputC)) / 2,
                                        "acad_head_d": (float(data.acad_head_d) + float(averageInputD)) / 2,
                                        "acad_head_ids": eval_id,
                                        "acad_head_evaluators": text("acad_head_evaluators + 1"),
                                        })
                        
                        u = u.where((FISEvaluations.FacultyId == FacultyId) & (FISEvaluations.school_year == school_year) & (FISEvaluations.semester == semester))
                        db.session.execute(u)
                        db.session.commit()
                        
                        add_notif = FISUser_Notifications(
                        FacultyId=FacultyId,
                        Status= "pending",
                        Type= "notif",
                        notif_by = current_user.AdminId,
                        notifier_type = "Admin",
                        Notification = "Academic Head evaluated you for " + semester + " Semester, School Year : " + schoolYear ,
                        )
                        
                        db.session.add(add_notif)
                        db.session.commit()
                        
                        flash('Evaluated successfully!', category='success')
                        # print("success1")
                        db.session.close()   
                        return redirect(url_for('aFS.aFS_H'))

                    except Exception as e:
                        # print(f"An error occurred1: {str(e)}")
                        db.session.rollback()  # Rollback changes in case of an error
                        flash('An error occurred while evaluating!', category='error')
                        
                        return redirect(url_for('aFS.aFS_H'))
                else:
                    try:
                        add_record = FISEvaluations(
                            id=highest_id_record.id + 1,
                            AdminId=None,
                            FacultyId=FacultyId,  # Set to appropriate value if needed
                            Evaluator_Name="",
                            EvaluatorIds="None",
                            Type="",
                            acad_head_evaluators = 1,
                            acad_head=AverageRate,
                            acad_head_a=averageInputA,
                            acad_head_b=averageInputB,
                            acad_head_c=averageInputC,
                            acad_head_d=averageInputD,
                            acad_head_ids=eval_id,
                            direktor_evaluators=0,
                            director_ids="None",
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
                            peer=0,  # Make sure AverageRate is defined
                            peer_a=0,
                            peer_b=0,
                            peer_c=0,
                            peer_d=0,
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
                        
                        add_notif = FISUser_Notifications(
                        FacultyId=FacultyId,
                        Status= "pending",
                        Type= "notif",
                        notif_by = current_user.AdminId,
                        notifier_type = "Admin",
                        Notification = "Academic Head evaluated you for " + semester + " Semester, School Year : " + schoolYear ,
                        )
                        
                        db.session.add(add_notif)
                        db.session.commit()
                        
                        flash('Evaluated successfully!', category='success')
                        # print("success2")
                        db.session.close()
                        return redirect(url_for('aFS.aFS_H'))

                    except Exception as e:
                        # print(f"An error occurred4: {str(e)}")
                        db.session.rollback()
                        flash('An error occurred while evaluating!', category='error')
                        return redirect(url_for('aFS.aFS_H'))
            
            else:
                director_head = 1
                if FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester).first():  
                    data = FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester).first()      
                    try:
                        u = update(FISEvaluations)
                        if(data.director == 0):
                            u = u.values({"director": AverageRate,
                                        "director_a": averageInputA,
                                        "director_b": averageInputB,
                                        "director_c": averageInputC,
                                        "director_d": averageInputD,
                                        "director_ids": eval_id,
                                        "direktor_evaluators": text("direktor_evaluators + 1"),
                                        })
                        else:
                            u = u.values({"director": (float(data.director) + float(AverageRate)) / 2,
                                        "director_a": (float(data.director_a) + float(averageInputA)) / 2,
                                        "director_b": (float(data.director_b) + float(averageInputB)) / 2,
                                        "director_c": (float(data.director_c) + float(averageInputC)) / 2,
                                        "director_d": (float(data.director_d) + float(averageInputD)) / 2,
                                        "director_ids": eval_id,
                                        "direktor_evaluators": text("direktor_evaluators + 1"),
                                        })
                        
                        u = u.where((FISEvaluations.FacultyId == FacultyId) & (FISEvaluations.school_year == school_year) & (FISEvaluations.semester == semester))
                        db.session.execute(u)
                        db.session.commit()
                        
                        add_notif = FISUser_Notifications(
                        FacultyId=FacultyId,
                        Status= "pending",
                        Type= "notif",
                        notif_by = current_user.AdminId,
                        notifier_type = "Admin",
                        Notification = "Director evaluated you for " + semester + " Semester, School Year : " + schoolYear ,
                        )
                        
                        db.session.add(add_notif)
                        db.session.commit()
                        
                        flash('Evaluated successfully!', category='success')
                        # print("success3")
                        db.session.close()   
                        return redirect(url_for('aFS.aFS_H'))

                    except Exception as e:
                        print(f"An error occurred1: {str(e)}")
                        db.session.rollback()  # Rollback changes in case of an error
                        flash('An error occurred while evaluating!', category='error')
                        
                        return redirect(url_for('aFS.aFS_H'))
                else:
                    try:
                        add_record = FISEvaluations(
                            id=highest_id_record.id + 1,
                            AdminId=None,
                            FacultyId=FacultyId,  # Set to appropriate value if needed
                            Evaluator_Name="",
                            EvaluatorIds="None",
                            Type="",
                            acad_head_ids="None",
                            acad_head=0,
                            acad_head_a=0,
                            acad_head_b=0,
                            acad_head_c=0,
                            acad_head_d=0,
                            acad_head_evaluators = 0,
                            direktor_evaluators = 1,
                            director=AverageRate,
                            director_a=averageInputA,
                            director_b=averageInputB,
                            director_c=averageInputC,
                            director_d=averageInputD,
                            director_ids=eval_id,
                            self_eval=0,
                            self_a=0,
                            self_b=0,
                            self_c=0,
                            self_d=0,
                            peer=0,
                            peer_a=0,
                            peer_b=0,
                            peer_c=0,
                            peer_d=0,
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
                        
                        add_notif = FISUser_Notifications(
                        FacultyId=FacultyId,
                        Status= "pending",
                        Type= "notif",
                        notif_by = current_user.AdminId,
                        notifier_type = "Admin",
                        Notification = "Director evaluated you for " + semester + " Semester, School Year : " + schoolYear ,
                        )
                        
                        db.session.add(add_notif)
                        db.session.commit()
                        
                        flash('Evaluated successfully!', category='success')
                        # print("success4")
                        db.session.close()
                        return redirect(url_for('aFS.aFS_H'))

                    except Exception as e:
                        # print(f"An error occurred4: {str(e)}")
                        db.session.rollback()
                        flash('An error occurred while evaluating!', category='error')
                        return redirect(url_for('aFS.aFS_H'))
                         
        
            
            

@aFS.route('/Admin-Feedback-Surveys/FISFaculty', methods=['GET', 'POST'])
@login_required
@Check_Token
def aFS_requests_faculties():
    
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
        

@aFS.route('/Admin-Feedback-Surveys/FISFaculty/Evaluations', methods=['GET', 'POST'])
@login_required
@Check_Token
def aFS_requests_evaluations():
    
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


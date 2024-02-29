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
from website.models import FISFaculty, FISEvaluations, FISUser_Notifications

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
            
             
            if FISEvaluations.query.filter_by(FacultyId=FacultyId,semester=semester, school_year = school_year ).first():
                evaluation_item_id = FISEvaluations.query.filter_by(FacultyId=FacultyId,semester=semester, school_year = school_year ).first()
                if evaluation_item_id.EvaluatorIds == 'None':
                    eval_id = str(current_user.FacultyId)
                else:
                    eval_id  = evaluation_item_id.EvaluatorIds+","+str(current_user.FacultyId)
            else:
                eval_id = str(current_user.FacultyId)
                
            
            if FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester).all():
                if FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester).first() and FISEvaluations.query.filter_by(FacultyId=current_user.FacultyId, school_year = school_year, semester = semester).first():
                    data = FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester).first() 
                    try:
                        u = update(FISEvaluations)
                        
                        if(data.self_eval == 0):
                            u = u.values({"self_eval": AverageRate,
                                        "self_a": averageInputA,
                                        "self_b": averageInputB,
                                        "self_c": averageInputC,
                                        "self_d": averageInputD,
                                        "EvaluatorIds": eval_id,
                                        "Evaluator_Name": str(current_user.LastName + ', ' + current_user.FirstName + ' ' + current_user.MiddleInitial),
                                        "Type": current_user.FacultyType,
                                        "fac_evaluators": text("fac_evaluators + 1"),
                                        })
                        else:
                            u = u.values({"self_eval": (float(data.self_eval) + float(AverageRate)) / 2,
                                        "self_a": (float(data.self_a) + float(averageInputA)) / 2,
                                        "self_b": (float(data.self_b) + float(averageInputB)) / 2,
                                        "self_c": (float(data.self_c) + float(averageInputC)) / 2,
                                        "self_d": (float(data.self_d) + float(averageInputD)) / 2,
                                        "EvaluatorIds": eval_id,
                                        "Type": current_user.FacultyType,
                                        "Evaluator_Name": str(current_user.LastName + ', ' + current_user.FirstName + ' ' + current_user.MiddleInitial),
                                        "fac_evaluators": text("fac_evaluators + 1"),
                                        })
                        
                        u = u.where((FISEvaluations.id == evaluation_item_id.id))
                        db.session.execute(u)
                        db.session.commit()
                        
                        add_notif = FISUser_Notifications(
                        FacultyId=current_user.FacultyId,
                        Status= "pending",
                        Type= "notif",
                        notif_by = current_user.FacultyId,
                        notifier_type = "Faculty",
                        Notification = "Successfully Evaluated self for " + semester + " Semester, School Year : " + schoolYear ,
                        )
                        
                        db.session.add(add_notif)
                        db.session.commit()
                        
                        flash('Evaluated successfully!', category='success')
                        # print("success1")
                        db.session.close()   
                        return redirect(url_for('FS.FS_H'))
                    
                    except Exception as e:
                        # print(f"An error occurred1: {str(e)}")
                        db.session.rollback()  # Rollback changes in case of an error
                        flash('An error occurred while evaluating!', category='error')
                        
                        return redirect(url_for('FS.FS_H')) 
                    
                else:
                    data = FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester).first()   
                    try:
                        u = update(FISEvaluations)
                        if(data.peer == 0):
                            u = u.values({"peer": AverageRate,
                                        "peer_a": averageInputA,
                                        "peer_b": averageInputB,
                                        "peer_c": averageInputC,
                                        "peer_d": averageInputD,
                                        "EvaluatorIds": eval_id,
                                        "fac_evaluators": text("fac_evaluators + 1"),
                                        })
                        else:
                            u = u.values({"peer": (float(data.peer) + float(AverageRate)) / 2,
                                            "peer_a": (float(data.peer_a) + float(averageInputA)) / 2,
                                            "peer_b": (float(data.peer_b) + float(averageInputB)) / 2,
                                            "peer_c": (float(data.peer_c) + float(averageInputC)) / 2,
                                            "peer_d": (float(data.peer_d) + float(averageInputD)) / 2,
                                            "EvaluatorIds": eval_id,
                                            "fac_evaluators": text("fac_evaluators + 1"),
                                            })
                        u = u.where((FISEvaluations.id == evaluation_item_id.id))
                        db.session.execute(u)
                        db.session.commit()
                        
                        add_notif = FISUser_Notifications(
                        FacultyId=FacultyId,
                        Status= "pending",
                        Type= "notif",
                        notif_by = current_user.FacultyId,
                        notifier_type = "Faculty",
                        Notification = "Evaluated you for " + semester + " Semester, School Year : " + schoolYear ,
                        )
                        
                        db.session.add(add_notif)
                        db.session.commit()
                        
                        flash('Evaluated successfully!', category='success')
                        # print("success2")
                        db.session.close()   
                        return redirect(url_for('FS.FS_H'))

                    except Exception as e:
                        # print(f"An error occurred1: {str(e)}")
                        db.session.rollback()  # Rollback changes in case of an error
                        flash('An error occurred while evaluating!', category='error')
                        
                        return redirect(url_for('FS.FS_H'))
                
            elif FISEvaluations.query.filter_by(FacultyId=FacultyId,semester=semester, school_year = school_year ).first() == None:
                if current_user.FacultyId == FacultyId:
                    try:
                        add_record = FISEvaluations(
                                                    id=highest_id_record.id+1,
                                                    FacultyId=FacultyId,
                                                    AdminId=None,  # Set to appropriate value if needed
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
                                                    
                                                    director_ids="None",
                                                    acad_head_ids="None",
                                                    school_year=school_year,
                                                    semester=semester,
                                                    Type = current_user.FacultyType,
                                                    Evaluator_Name = str(current_user.LastName + ', ' + current_user.FirstName + ' ' + current_user.MiddleInitial),
                                                    EvaluatorIds = eval_id,
                                                
                                                    fac_evaluators = 1,
                                                    is_delete=False,
                                                    )
                        db.session.add(add_record)
                        db.session.commit() 
                        
                        add_notif = FISUser_Notifications(
                        FacultyId=current_user.FacultyId,
                        Status= "pending",
                        Type= "notif",
                        notif_by = current_user.FacultyId,
                        notifier_type = "Faculty",
                        Notification = "Successfully Evaluated self for " + semester + " Semester, School Year : " + schoolYear ,
                        )
                        
                        db.session.add(add_notif)
                        db.session.commit()
                        
                        flash('Evaluated successfully!', category='success')
                        # print("success3")
                        db.session.close()   
                        return redirect(url_for('FS.FS_H')) 
                    
                    except Exception as e:
                        # print(f"An error occurred3: {str(e)}")
                        db.session.rollback()  # Rollback changes in case of an error
                        flash('An error occurred while evaluating!', category='error') 
                        
                        return redirect(url_for('FS.FS_H'))
                        
                else:
                    try:
    
                        add_record = FISEvaluations(
                            id=highest_id_record.id + 1,
                            FacultyId=FacultyId,
                            AdminId=None,  # Set to appropriate value if needed
                            Evaluator_Name="",
                            director_ids="None",
                            acad_head_ids="None",
                            EvaluatorIds= eval_id,
                            fac_evaluators = 1,
                            Type="",
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
                        
                        add_notif = FISUser_Notifications(
                        FacultyId=FacultyId,
                        Status= "pending",
                        Type= "notif",
                        notif_by = current_user.FacultyId,
                        notifier_type = "Faculty",
                        Notification = "Evaluated you for " + semester + " Semester, School Year : " + schoolYear ,
                        )
                        
                        db.session.add(add_notif)
                        db.session.commit()
                        
                        flash('Evaluated successfully!', category='success')
                        # print("success4")
                        db.session.close()
                        return redirect(url_for('FS.FS_H'))

                    except Exception as e:
                        # print(f"An error occurred4: {str(e)}")
                        db.session.rollback()
                        flash('An error occurred while evaluating!', category='error')
                        return redirect(url_for('FS.FS_H'))
          
            else:
                # print(f"An error occurred5")
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






#FACULTY STUDENT EVALUATION FORM


@FS.route("Student/Feedback-Surveys", methods=['GET', 'POST'])
@login_required
@Check_Token
def SFS_H():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
                      
        return render_template("Faculty-Home-Page/Feedback-Survey/student_form.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               profile_pic=ProfilePic)

 
# ------------------------------------------------------------- 



@FS.route("Student/Feedback-Surveys/add-record", methods=['GET', 'POST'])
@login_required
def SFS_add():

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

            evaluation_item_id = FISEvaluations.query.filter_by(FacultyId=FacultyId,semester=semester, school_year = school_year ).first()
            
            if FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester).all():
                    data = FISEvaluations.query.filter_by(FacultyId=FacultyId, school_year = school_year, semester = semester).first() 
                    try:
                        u = update(FISEvaluations)
                        
                        if(data.student == 0):
                            u = u.values({"student": AverageRate,
                                        "student_a": averageInputA,
                                        "student_b": averageInputB,
                                        "student_c": averageInputC,
                                        "student_d": averageInputD,
                                        "student_evaluators": text("student_evaluators + 1"),
                                        })
                        else:
                            u = u.values({"student": (float(data.student) + float(AverageRate)) / 2,
                                        "student_a": (float(data.student_a) + float(averageInputA)) / 2,
                                        "student_b": (float(data.student_b) + float(averageInputB)) / 2,
                                        "student_c": (float(data.student_c) + float(averageInputC)) / 2,
                                        "student_d": (float(data.student_d) + float(averageInputD)) / 2,
                                        "student_evaluators": text("student_evaluators + 1"),
                                        })
                        
                        u = u.where((FISEvaluations.id == evaluation_item_id.id))
                        db.session.execute(u)
                        db.session.commit()
                        
                        flash('Evaluated successfully!', category='success')
                        # print("success1")
                        db.session.close()   
                        return redirect(url_for('FS.SFS_H'))
                    
                    except Exception as e:
                        # print(f"An error occurred1: {str(e)}")
                        db.session.rollback()  # Rollback changes in case of an error
                        flash('An error occurred while evaluating!', category='error')
                        
                        return redirect(url_for('FS.SFS_H'))   
          
            else:
                # print(f"An error occurred5")
                flash('An error occurred while evaluating!', category='error')
                return redirect(url_for('FS.SFS_H'))
            

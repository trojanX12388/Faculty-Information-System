from flask import Flask, Blueprint, redirect, render_template, request, url_for
from dotenv import load_dotenv
from flask_login import login_required, current_user
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from urllib.request import urlretrieve
from cryptography.fernet import Fernet
import rsa


import os
import os.path

load_dotenv()

# DATABASE CONNECTION
from website.models import db
from sqlalchemy import update

# LOADING MODEL CLASSES
from website.models import FISFaculty, FISTeachingAssignments, FISAdvisingClasses_Schedule, FISEvaluations, FISInstructionalMaterialsDeveloped, FISAdvisingStudent, Student, FISSpecialProject, FISCapstone

# LOADING FUNCTION CHECK TOKEN
from website.Token.token_check import Check_Token

# WEB AUTH ROUTES URL
TI = Blueprint('TI', __name__)

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


#                                                    TEACHING INSTRUCTIONS ROUTE


# ------------------------------- TEACHING ASSIGNMENTS ----------------------------  
import requests

@TI.route("/TI-Teaching-Assignments", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_TA():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 

    if username.ProfilePic == None:
        ProfilePic = profile_default
    else:
        ProfilePic = username.ProfilePic

    # Fetch API data
    api_url = "https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading"  # Replace with the actual API endpoint
    headers = {
        'Authorization': 'Bearer '+ os.environ["API_TOKENS_SCHEDULER"],
        'Content-Type': 'application/json'  # Adjust content type as needed
    }
    
    api_response = requests.get(api_url,headers=headers)
    
    if api_response.status_code == 200:
        api_data = api_response.json()
    else:
        api_data = {"message": "Failed to fetch data", "data": []}
        
    # Fetch API data semester
    api_url1 = "https://schedulerserver-6e565d991c10.herokuapp.com/semesters/getsemester"  # Replace with the actual API endpoint
    api_response1 = requests.get(api_url1, headers=headers)
    
    if api_response1.status_code == 200:
        semester = api_response1.json()

    else:
        semester = {"message": "Failed to fetch data", "data": []}
        
    # Fetch API data acad year
    api_url2 = "https://schedulerserver-6e565d991c10.herokuapp.com/academicyears/getacadyr"  # Replace with the actual API endpoint
    api_response2 = requests.get(api_url2, headers=headers)
    
    if api_response2.status_code == 200:
        acad_year = api_response2.json()
    else:
        acad_year = {"message": "Failed to fetch data", "data": []}
   
    # # Fetch API data for Classroom
    # api_url1 = "https://schedulerserver-6e565d991c10.herokuapp.com/rooms/getrooms"  # Replace with the actual API endpoint
    # headers = {
    #     'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpbnRlZ3JhdGlvbkBnbWFpbC5jb20iLCJ1c2VydHlwZSI6InN0YWZmIiwiZXhwIjoxNzA4NzA1Mjc5fQ.vBx_831N2vKXv913WShd4TmX_olT-XuHm7DNfTov2bI'
    # }

    # # Make a GET request to the API with the API key in the headers
    # api_response1 = requests.get(api_url1, headers=headers)
    
    # if api_response1.status_code == 200:
    #     rooms = api_response1.json()
    # else:
    #     rooms = {"message": "Failed to fetch data", "data": []}
        
    # print(rooms)

    # ... (your existing code)
    course_names_dict = {}

    # Iterate through the fetched data
    for entry in api_data.get("data", []):
        # Check if facultyid matches current_user_id
        if entry.get("facultyid") == current_user.FacultyId:
            # Fetch and store the course_description
            current_course_description = entry.get("course_description")

            # If the course_description is not already in the dictionary, add it as subject_a, subject_b, etc.
            if current_course_description not in course_names_dict.values():
                next_subject = chr(97 + len(course_names_dict))  # Use ASCII characters for subject_a, subject_b, etc.
                course_names_dict[next_subject] = current_course_description
                
    # if request.method == 'POST':
    #     acad_year = request.form.get('acad_year')
    #     semester = request.form.get('semester')
    #     for data in api_data.data:
    #         if data.facultyid == current_user.FacultyId and data.semester_id == semester and data.acadyear_id == acad_year :
    #             filtered_data = {
    #                 'roomname': data.roomname,
    #                 'course_code': data.course_code,
    #                 'course_description': data.course_description,
    #                 'classname': data.classname,
    #                 'units': data.units,
    #                 'lec': data.lec,
    #                 'lab': data.lab,
    #             }

    return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Teaching-Assignments.html", 
                           User=username.FirstName + " " + username.LastName,
                           faculty_code=username.FacultyCode,
                           user=current_user,
                           TI="show",
                           activate_TA="active",
                           profile_pic=ProfilePic,
                           course_names_dict = course_names_dict,
                           api_data=api_data,
                           semester = semester,
                           acad_year = acad_year,
                           )
 
# ------------------------------------------------------------- 

# ------------------------------- TEACHING ASSIGNMENTS SCHEDULES----------------------------  

@TI.route("/TI-Teaching-Assignments/<id>/Schedules", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_TAS(id):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        item = FISTeachingAssignments.query.filter_by(id=id).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
        # # UPDATE PROFILE BASIC DETAILS
        
        # if request.method == 'POST':

        #     # UPDATE BASIC DETAILS
        #     # VALUES
        #     FacultyCode = request.form.get('FacultyCode')
        #     honorific = request.form.get('honorific')

        #     u = update(FISFaculty)
        #     u = u.values({"FacultyCode": FacultyCode,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(FISFaculty.FacultyId == current_user.FacultyId)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Teaching-Assignments-Schedules.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               item=item,
                               activate_TA="active",
                               profile_pic=ProfilePic)

 
# ------------------------------------------------------------- 


# ------------------------------- ADVISING MENTORING ----------------------------  

@TI.route("/TI-Advising-Mentoring", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_AM():
    
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
    advising_students = FISAdvisingStudent.query.filter_by(FacultyId=current_user.FacultyId).all() 

    students = []
    for data2 in advising_students:
        student = Student.query.filter_by(StudentId=data2.StudentId).first()
        if student:
            students.append({
                'StudentNumber': student.StudentNumber,
                'FullName': f"{student.LastName}, {student.FirstName} {student.MiddleName}",
                'CourseSection': f"{data2.course}/{data2.section}",
                'Subject': data2.subject,
                'Status': data2.status,
                'Id': data2.id
            })

    if username.ProfilePic is None:
        ProfilePic = profile_default
    else:
        ProfilePic = username.ProfilePic

    return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Advising-Mentoring.html", 
                           User=username.FirstName + " " + username.LastName,
                           faculty_code=username.FacultyCode,
                           user=current_user,
                           TI="show",
                           students=students,
                           activate_AdM="active",
                           profile_pic=ProfilePic)
 
# ------------------------------------------------------------- 

# ------------------------------- ADVISING CLASS SCHEDULES----------------------------  

@TI.route("/TI-Advising-Class/<classid>/Schedules", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_AMCS(classid):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        item = FISAdvisingClasses_Schedule.query.filter_by(FacultyId=current_user.FacultyId, id=classid).all()

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
       
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Advising-Class-Schedules.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               item = item,
                               activate_AdM="active",
                               profile_pic=ProfilePic)

 
# ------------------------------------------------------------- 

# ------------------------------- ADVISING STUDENT SCHEDULES----------------------------  

@TI.route("/TI-Advising-Student/<StudentId>/Schedules", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_AMSS(StudentId):
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        advising_students = FISAdvisingStudent.query.filter_by(FacultyId=current_user.FacultyId,id=StudentId).all() 

        sched = []
        for data2 in advising_students:
            student = Student.query.filter_by(StudentId=data2.StudentId).first()
            if student:
                sched.append({
                    'StudentNumber': student.StudentNumber,
                    'FullName': f"{student.LastName}, {student.FirstName} {student.MiddleName}",
                    'CourseSection': f"{data2.course}/{data2.section}",
                    'Subject': data2.subject,
                    'Status': data2.status,
                    'Id': data2.id
                })

    
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Advising-Student-Schedules.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               sched = sched,
                               activate_AdM="active",
                               profile_pic=ProfilePic)

 
# ------------------------------------------------------------- 

# ------------------------------- MENTORING STUDENT SCHEDULES----------------------------  

@TI.route("/TI-Advising-Mentoring/2020-0056-CM/Mentoring/Schedules", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_AMMS():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
        # # UPDATE PROFILE BASIC DETAILS
        
        # if request.method == 'POST':

        #     # UPDATE BASIC DETAILS
        #     # VALUES
        #     FacultyCode = request.form.get('FacultyCode')
        #     honorific = request.form.get('honorific')

        #     u = update(FISFaculty)
        #     u = u.values({"FacultyCode": FacultyCode,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(FISFaculty.FacultyId == current_user.FacultyId)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Mentoring-Student-Schedules.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               activate_AdM="active",
                               profile_pic=ProfilePic)

 
# ------------------------------------------------------------- 

# ------------------------------- TEACHING EFFECTIVENESS ----------------------------  

@TI.route("/TI-Teaching-Effectiveness", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_TE():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT   
        from sqlalchemy import desc
        
        def convert_to_percentage(grade):
            # Assuming the maximum grade is 5.0
            max_grade = 5.0

            # Perform linear conversion
            percentage = (grade / max_grade) * 100

            # Round the result to two decimal places
            return '{:.4f}'.format(percentage)
        
        def convert_to_interpretation(grade):
            # Legend for conversion
            legend = {
                (4.5, 5.0): 'Very Outstanding',
                (3.5, 4.49): 'Outstanding',
                (2.5, 3.49): 'Satisfactory',
                (1.5, 2.49): 'Fair',
                (1.0, 1.49): 'Poor'
            }

            # Iterate through legend and find the corresponding range
            for key, value in legend.items():
                if key[0] <= grade <= key[1]:
                    return value

            return None  # Handle the case where the grade doesn't fall into any range
        
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
            
        # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.FISEvaluations:
        
            year_sem = FISEvaluations.query.filter_by(FacultyId=current_user.FacultyId).order_by(desc(FISEvaluations.id)).first()

            acad_head_a = year_sem.acad_head_a
            acad_head_b = year_sem.acad_head_b
            acad_head_c = year_sem.acad_head_c
            acad_head_d = year_sem.acad_head_d
            director = year_sem.director
            director_a = year_sem.director_a
            director_b = year_sem.director_b
            director_c = year_sem.director_c
            director_d = year_sem.director_d
            self_eval = year_sem.self_eval
            self_a = year_sem.self_a
            self_b = year_sem.self_b
            self_c = year_sem.self_c
            self_d = year_sem.self_d
            peer = year_sem.peer
            peer_a = year_sem.peer_a
            peer_b = year_sem.peer_b
            peer_c = year_sem.peer_c
            peer_d = year_sem.peer_d
            student = year_sem.student
            student_a = year_sem.student_a
            student_b = year_sem.student_b
            student_c = year_sem.student_c
            student_d = year_sem.student_d
            
            # Calculate the average of acad_head_a, acad_head_b, acad_head_c, and acad_head_d
            acad_head_ave = (acad_head_a + acad_head_b + acad_head_c + acad_head_d) / 4
            director_ave = (director_a + director_b + director_c + director_d) / 4
            self_ave = (self_a + self_b + self_c + self_d) / 4
            peer_ave = (peer_a + peer_b + peer_c + peer_d) / 4
            student_ave = (student_a + student_b + student_c + student_d) / 4
            
            
            # CALCULATED RATING
            acad_head_calc = (acad_head_ave) * 0.10
            director_calc = (director_ave) * 0.20
            self_calc = (self_ave) * 1.0
            peer_calc = (peer_ave) * 0.20
            student_calc = (student_ave) * 0.70
            
            general_rating = (acad_head_calc) + (director_calc) + (student_calc)
            
            calc_data = {
                            'acad_head_a': convert_to_percentage(acad_head_a),
                            'acad_head_b': convert_to_percentage(acad_head_b),
                            'acad_head_c': convert_to_percentage(acad_head_c),
                            'acad_head_d': convert_to_percentage(acad_head_d),
                            'acad_head_ave': convert_to_percentage(acad_head_ave),
                            'acad_head_calc': convert_to_percentage(acad_head_calc),
                            'acad_head_interpret': convert_to_interpretation(acad_head_ave),
                            
                            
                            'director': convert_to_percentage(director),
                            'director_a': convert_to_percentage(director_a),
                            'director_b': convert_to_percentage(director_b),
                            'director_c': convert_to_percentage(director_c),
                            'director_d': convert_to_percentage(director_d),
                            'director_ave': convert_to_percentage(director_ave),
                            'director_calc': convert_to_percentage(director_calc),
                            'director_interpret': convert_to_interpretation(director_ave),
                            
                            'self_eval': convert_to_percentage(self_eval),
                            'self_a': convert_to_percentage(self_a),
                            'self_b': convert_to_percentage(self_b),
                            'self_c': convert_to_percentage(self_c),
                            'self_d': convert_to_percentage(self_d),
                            'self_ave': convert_to_percentage(self_ave),
                            'self_calc': convert_to_percentage(self_calc),
                            'self_interpret': convert_to_interpretation(self_ave),
                            
                            'peer': convert_to_percentage(peer),
                            'peer_a': convert_to_percentage(peer_a),
                            'peer_b': convert_to_percentage(peer_b),
                            'peer_c': convert_to_percentage(peer_c),
                            'peer_d': convert_to_percentage(peer_d),
                            'peer_ave': convert_to_percentage(peer_ave),
                            'peer_calc': convert_to_percentage(peer_calc),
                            'peer_interpret': convert_to_interpretation(peer_ave),
                            
                            'student': convert_to_percentage(student),
                            'student_a': convert_to_percentage(student_a),
                            'student_b': convert_to_percentage(student_b),
                            'student_c': convert_to_percentage(student_c),
                            'student_d': convert_to_percentage(student_d),
                            'student_ave': convert_to_percentage(student_ave),
                            'student_calc': convert_to_percentage(student_calc),
                            'student_interpret': convert_to_interpretation(student_ave),
                            
                            'fac_evaluators': year_sem.fac_evaluators,
                            'acad_head_evaluators': year_sem.acad_head_evaluators,
                            'direktor_evaluators': year_sem.direktor_evaluators,
                            'student_evaluators': year_sem.student_evaluators,
                            
                            'overall_evaluators': (year_sem.student_evaluators) + (year_sem.acad_head_evaluators) + (year_sem.fac_evaluators) + (year_sem.direktor_evaluators),
                            
                            'general_rating': convert_to_percentage(general_rating),
                            'general_interpret': convert_to_interpretation(general_rating),
                            
                        }
            
        else:
            calc_data = {
                            'acad_head_a': '',
                            'acad_head_b': '',
                            'acad_head_c': '',
                            'acad_head_d': '',
                            'acad_head_ave': '',
                            'acad_head_calc': '',
                            'acad_head_interpret': '',
                            
                            
                            'director': '',
                            'director_a': '',
                            'director_b': '',
                            'director_c': '',
                            'director_d': '',
                            'director_ave': '',
                            'director_calc': '',
                            'director_interpret': '',
                            
                            'self_eval': '',
                            'self_a': '',
                            'self_b': '',
                            'self_c': '',
                            'self_d': '',
                            'self_ave': '',
                            'self_calc': '',
                            'self_interpret': '',
                            
                            'peer': '',
                            'peer_a': '',
                            'peer_b': '',
                            'peer_c': '',
                            'peer_d': '',
                            'peer_ave': '',
                            'peer_calc': '',
                            'peer_interpret': '',
                            
                            'student': '',
                            'student_a': '',
                            'student_b': '',
                            'student_c': '',
                            'student_d': '',
                            'student_ave': '',
                            'student_calc': '',
                            'student_interpret': '',
                            
                            'fac_evaluators': 0,
                            'acad_head_evaluators': 0,
                            'direktor_evaluators': 0,
                            'student_evaluators': 0,
                            
                            'overall_evaluators': 0,
                            
                            'general_rating': '',
                            'general_interpret': '',
                            
                        }
            year_sem = {
                    'Remarks':"",
                    'school_year':None,
                    }
                    
            
        if request.method == 'POST':
        
            select = request.form.get('select')
            year_sem = FISEvaluations.query.filter_by(FacultyId=current_user.FacultyId, id=select).first()
           
            acad_head_a = year_sem.acad_head_a
            acad_head_b = year_sem.acad_head_b
            acad_head_c = year_sem.acad_head_c
            acad_head_d = year_sem.acad_head_d
            director = year_sem.director
            director_a = year_sem.director_a
            director_b = year_sem.director_b
            director_c = year_sem.director_c
            director_d = year_sem.director_d
            self_eval = year_sem.self_eval
            self_a = year_sem.self_a
            self_b = year_sem.self_b
            self_c = year_sem.self_c
            self_d = year_sem.self_d
            peer = year_sem.peer
            peer_a = year_sem.peer_a
            peer_b = year_sem.peer_b
            peer_c = year_sem.peer_c
            peer_d = year_sem.peer_d
            student = year_sem.student
            student_a = year_sem.student_a
            student_b = year_sem.student_b
            student_c = year_sem.student_c
            student_d = year_sem.student_d
            
            # Calculate the average of acad_head_a, acad_head_b, acad_head_c, and acad_head_d
            acad_head_ave = (acad_head_a + acad_head_b + acad_head_c + acad_head_d) / 4
            director_ave = (director_a + director_b + director_c + director_d) / 4
            self_ave = (self_a + self_b + self_c + self_d) / 4
            peer_ave = (peer_a + peer_b + peer_c + peer_d) / 4
            student_ave = (student_a + student_b + student_c + student_d) / 4
            

            
            # CALCULATED RATING
            acad_head_calc = (acad_head_ave) * 0.10
            director_calc = (director_ave) * 0.20
            self_calc = (self_ave) * 1.0
            peer_calc = (peer_ave) * 0.20
            student_calc = (student_ave) * 0.70
            
            general_rating = (acad_head_calc) + (director_calc) + (student_calc)
            
            calc_data = {
                            'acad_head_a': convert_to_percentage(acad_head_a),
                            'acad_head_b': convert_to_percentage(acad_head_b),
                            'acad_head_c': convert_to_percentage(acad_head_c),
                            'acad_head_d': convert_to_percentage(acad_head_d),
                            'acad_head_ave': convert_to_percentage(acad_head_ave),
                            'acad_head_calc': convert_to_percentage(acad_head_calc),
                            'acad_head_interpret': convert_to_interpretation(acad_head_ave),
                            
                            
                            'director': convert_to_percentage(director),
                            'director_a': convert_to_percentage(director_a),
                            'director_b': convert_to_percentage(director_b),
                            'director_c': convert_to_percentage(director_c),
                            'director_d': convert_to_percentage(director_d),
                            'director_ave': convert_to_percentage(director_ave),
                            'director_calc': convert_to_percentage(director_calc),
                            'director_interpret': convert_to_interpretation(director_ave),
                            
                            'self_eval': convert_to_percentage(self_eval),
                            'self_a': convert_to_percentage(self_a),
                            'self_b': convert_to_percentage(self_b),
                            'self_c': convert_to_percentage(self_c),
                            'self_d': convert_to_percentage(self_d),
                            'self_ave': convert_to_percentage(self_ave),
                            'self_calc': convert_to_percentage(self_calc),
                            'self_interpret': convert_to_interpretation(self_ave),
                            
                            'peer': convert_to_percentage(peer),
                            'peer_a': convert_to_percentage(peer_a),
                            'peer_b': convert_to_percentage(peer_b),
                            'peer_c': convert_to_percentage(peer_c),
                            'peer_d': convert_to_percentage(peer_d),
                            'peer_ave': convert_to_percentage(peer_ave),
                            'peer_calc': convert_to_percentage(peer_calc),
                            'peer_interpret': convert_to_interpretation(peer_ave),
                            
                            'student': convert_to_percentage(student),
                            'student_a': convert_to_percentage(student_a),
                            'student_b': convert_to_percentage(student_b),
                            'student_c': convert_to_percentage(student_c),
                            'student_d': convert_to_percentage(student_d),
                            'student_ave': convert_to_percentage(student_ave),
                            'student_calc': convert_to_percentage(student_calc),
                            'student_interpret': convert_to_interpretation(student_ave),
                            
                            'fac_evaluators': year_sem.fac_evaluators,
                            'acad_head_evaluators': year_sem.acad_head_evaluators,
                            'direktor_evaluators': year_sem.direktor_evaluators,
                            'student_evaluators': year_sem.student_evaluators,
                            
                            'overall_evaluators': (year_sem.student_evaluators) + (year_sem.acad_head_evaluators) + (year_sem.fac_evaluators) + (year_sem.direktor_evaluators),
                            
                            'general_rating': convert_to_percentage(general_rating),
                            'general_interpret': convert_to_interpretation(general_rating),
                            
                        }
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Teaching-Effectiveness.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               item_id = year_sem,
                               calc_data = calc_data,
                               activate_TE="active",
                               profile_pic=ProfilePic)

 
# ------------------------------------------------------------- 

# ------------------------------- TEACHING EFFECTIVENESS FORM----------------------------  

@TI.route("/TI-Faculty-Feedback-Form", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_TEFF():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
        # # UPDATE PROFILE BASIC DETAILS
        
        # if request.method == 'POST':

        #     # UPDATE BASIC DETAILS
        #     # VALUES
        #     FacultyCode = request.form.get('FacultyCode')
        #     honorific = request.form.get('honorific')

        #     u = update(FISFaculty)
        #     u = u.values({"FacultyCode": FacultyCode,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(FISFaculty.FacultyId == current_user.FacultyId)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Teaching-Effectiveness-Feedback-Form.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               activate_TE="active",
                               profile_pic=ProfilePic)

 
# ------------------------------------------------------------- 

# ------------------------------- CURRICULUM ----------------------------  

@TI.route("/TI-Curriculum", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_C():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
        # # UPDATE PROFILE BASIC DETAILS
        
        # if request.method == 'POST':

        #     # UPDATE BASIC DETAILS
        #     # VALUES
        #     FacultyCode = request.form.get('FacultyCode')
        #     honorific = request.form.get('honorific')

        #     u = update(FISFaculty)
        #     u = u.values({"FacultyCode": FacultyCode,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(FISFaculty.FacultyId == current_user.FacultyId)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Curriculum.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               activate_C="active",
                               profile_pic=ProfilePic)

 
@TI.route("/TI-Curriculum-Syllabus", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_CS():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        import datetime

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
        # # UPDATE PROFILE BASIC DETAILS
        
        # if request.method == 'POST':

        #     # UPDATE BASIC DETAILS
        #     # VALUES
        #     FacultyCode = request.form.get('FacultyCode')
        #     honorific = request.form.get('honorific')

        #     u = update(FISFaculty)
        #     u = u.values({"FacultyCode": FacultyCode,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(FISFaculty.FacultyId == current_user.FacultyId)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
            current_year = datetime.datetime.now().year
    
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Curriculum-Syllabus.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               activate_C="active",
                               current_year=current_year,
                               profile_pic=ProfilePic)
 
# ------------------------------------------------------------- 

# ------------------------------- INSTRUCIOTNAL MATERIALS DEVELOPED ----------------------------  

@TI.route("/TI-Instructional-Materials-Developed", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_IMD():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
            
         # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            title = request.form.get('title')
            abstract = request.form.get('abstract')
            id = request.form.get('id')

            u = update(FISInstructionalMaterialsDeveloped)
            u = u.values({"title": title,
                          "abstract": abstract
                          })
            u = u.where(FISInstructionalMaterialsDeveloped.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('TI.TI_IMD'))
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Instructional-Materials-Developed.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               activate_IMD="active",
                               profile_pic=ProfilePic)

        
@TI.route("/TI-Instructional-Materials-Developed/add-record", methods=['GET', 'POST'])
@login_required
def TI_IMDadd():
        
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        
        title = request.form.get('title')
        abstract = request.form.get('abstract')
        
        file =  request.form.get('base64')
        ext = request.files.get('fileup')
        ext = ext.filename
        
        id = f'{str(username.FacultyId)}{str(title)}'
        
        # INSTRUCTIONAL MATERIAL FOLDER ID
        folder = '1pAV7w6lXy6_EP6AswA34OP0-PogVg8KG'
        
        
        url = """data:application/pdf;base64,{}""".format(file)
                
        filename, m = urlretrieve(url)
    
        file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
        try:
            for file1 in file_list:
                if file1['title'] == str(id):
                    file1.Delete()                
        except:
            pass
        # CONFIGURE FILE FORMAT AND NAME
        file1 = drive.CreateFile(metadata={
            "title": ""+ str(id),
            "parents": [{"id": folder}],
            "mimeType": "application/pdf"
            })
        
        # GENERATE FILE AND UPLOAD
        file1.SetContentFile(filename)
        file1.Upload()
        
        add_record = FISInstructionalMaterialsDeveloped(title=title,abstract=abstract,file_id='%s'%(file1['id']),FacultyId = current_user.FacultyId)
        
        db.session.add(add_record)
        db.session.commit()
        db.session.close()
        
        return redirect(url_for('TI.TI_IMD'))
            
           
@TI.route("/TI-Instructional-Materials-Developed/delete-record", methods=['GET', 'POST'])
@login_required
def TI_IMDdel():
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 

        id = request.form.get('id')
        
        
        data = FISInstructionalMaterialsDeveloped.query.filter_by(id=id).first() 
        
        if data:
            id = f'{str(username.FacultyId)}{str(data.title)}'
        
            # INSTRUCTIONAL MATERIAL FOLDER ID
            folder = '1pAV7w6lXy6_EP6AswA34OP0-PogVg8KG'
        
            # CLEAR PROFILE PIC
            file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
            try:
                for file1 in file_list:
                    if file1['title'] == str(id):
                        file1.Delete()                
            except:
                pass

            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('TI.TI_IMD'))        

        
# ------------------------------- SPECIAL PROJECT ----------------------------  

@TI.route("/TI-Special-Project", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_SP():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Special-Project.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               activate_SP="active",
                               profile_pic=ProfilePic)
        
       
@TI.route("/TI-Special-Project/add-record", methods=['GET', 'POST'])
@login_required
def TI_SPadd():
        
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        
        title = request.form.get('title')
        status = request.form.get('status')
        due = request.form.get('due_date')
        
        file =  request.form.get('base64')
        ext = request.files.get('fileup')
        ext = ext.filename
        
        id = f'{str(username.FacultyId)}{str(title)}'
        
        # SPECIAL PROJECT FOLDER ID
        folder = '1DhQuE0zHYxK5lzeHUNKpnncOyZe_KThb'
        
        
        url = """data:application/pdf;base64,{}""".format(file)
                
        filename, m = urlretrieve(url)
    
        file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
        try:
            for file1 in file_list:
                if file1['title'] == str(id):
                    file1.Delete()                
        except:
            pass
        # CONFIGURE FILE FORMAT AND NAME
        file1 = drive.CreateFile(metadata={
            "title": ""+ str(id),
            "parents": [{"id": folder}],
            "mimeType": "application/pdf"
            })
        
        # GENERATE FILE AND UPLOAD
        file1.SetContentFile(filename)
        file1.Upload()
        
        add_record = FISSpecialProject(title=title,status=status,due=due,file_id='%s'%(file1['id']),FacultyId = current_user.FacultyId)
        
        db.session.add(add_record)
        db.session.commit()
        db.session.close()
        
        return redirect(url_for('TI.TI_SP'))
            
           
@TI.route("/TI-Special-Project/delete-record", methods=['GET', 'POST'])
@login_required
def TI_SPdel():
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 

        id = request.form.get('id')
        
        
        data = FISSpecialProject.query.filter_by(id=id).first() 
        
        if data:
            id = f'{str(username.FacultyId)}{str(data.title)}'
        
            # SPECIAL PROJECT FOLDER ID
            folder = '1DhQuE0zHYxK5lzeHUNKpnncOyZe_KThb'
        
            file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
            try:
                for file1 in file_list:
                    if file1['title'] == str(id):
                        file1.Delete()                
            except:
                pass

            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('TI.TI_SP'))                
        
# ------------------------------- CAPSTONE ----------------------------  

@TI.route("/TI-Capstone", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_Caps():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
         # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            title = request.form.get('title')
            abstract = request.form.get('abstract')
            id = request.form.get('id')

            u = update(FISCapstone)
            u = u.values({"title": title,
                          "abstract": abstract
                          })
            u = u.where(FISCapstone.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('TI.TI_Caps'))
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Capstone.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               activate_Caps="active",
                               profile_pic=ProfilePic)

      
@TI.route("/TI-Capstone/add-record", methods=['GET', 'POST'])
@login_required
def TI_Capsadd():
        
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        
        title = request.form.get('title')
        abstract = request.form.get('abstract')
        
        file =  request.form.get('base64')
        ext = request.files.get('fileup')
        ext = ext.filename
        
        id = f'{str(username.FacultyId)}{str(title)}'
        
       # CAPSTONE FOLDER ID
        folder = '1kG_rx1cqzFhrix6zYK5Gnv4B0MQniKQv'
        
        
        url = """data:application/pdf;base64,{}""".format(file)
                
        filename, m = urlretrieve(url)
    
        file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
        try:
            for file1 in file_list:
                if file1['title'] == str(id):
                    file1.Delete()                
        except:
            pass
        # CONFIGURE FILE FORMAT AND NAME
        file1 = drive.CreateFile(metadata={
            "title": ""+ str(id),
            "parents": [{"id": folder}],
            "mimeType": "application/pdf"
            })
        
        # GENERATE FILE AND UPLOAD
        file1.SetContentFile(filename)
        file1.Upload()
        
        add_record = FISCapstone(title=title,abstract=abstract,file_id='%s'%(file1['id']),FacultyId = current_user.FacultyId)
        
        db.session.add(add_record)
        db.session.commit()
        db.session.close()
        
        return redirect(url_for('TI.TI_Caps'))
            
           
@TI.route("/TI-Capstone/delete-record", methods=['GET', 'POST'])
@login_required
def TI_Capsdel():
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 

        id = request.form.get('id')
        
        
        data = FISCapstone.query.filter_by(id=id).first() 
        
        if data:
            id = f'{str(username.FacultyId)}{str(data.title)}'
        
            # CAPSTONE FOLDER ID
            folder = '1kG_rx1cqzFhrix6zYK5Gnv4B0MQniKQv'
        
            file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
            try:
                for file1 in file_list:
                    if file1['title'] == str(id):
                        file1.Delete()                
            except:
                pass

            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('TI.TI_Caps'))  
        
# ------------------------------- SERVICES ----------------------------  

@TI.route("/TI-Services", methods=['GET', 'POST'])
@login_required
@Check_Token
def TI_S():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
        # # UPDATE PROFILE BASIC DETAILS
        
        # if request.method == 'POST':

        #     # UPDATE BASIC DETAILS
        #     # VALUES
        #     FacultyCode = request.form.get('FacultyCode')
        #     honorific = request.form.get('honorific')

        #     u = update(FISFaculty)
        #     u = u.values({"FacultyCode": FacultyCode,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(FISFaculty.FacultyId == current_user.FacultyId)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
                      
        return render_template("Faculty-Home-Page/Teaching-Instructions/TI-Services.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               TI="show",
                               activate_S="active",
                               profile_pic=ProfilePic)
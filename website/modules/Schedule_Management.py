from flask import Flask, Blueprint, redirect, render_template, request, url_for, jsonify
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
from website.models import FISFaculty

# LOADING FUNCTION CHECK TOKEN
from website.Token.token_check import Check_Token

# WEB AUTH ROUTES URL
SM = Blueprint('SM', __name__)

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


#                                                    SCHEDULE MANAGEMENT ROUTE
        
# ------------------------------- CAMPUS SCHEDULE ----------------------------  

@SM.route("/SM-Campus-Schedule", methods=['GET', 'POST'])
@login_required
@Check_Token
def SM_CS():
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
                      
        return render_template("Faculty-Home-Page/Schedule-Management/SM-Campus-Schedule.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               SM="show",
                               activate_CS= "active",
                               profile_pic=ProfilePic)
        
# ------------------------------- UNVIERSITY SCHEDULE ----------------------------  

@SM.route("/SM-University-Schedule", methods=['GET', 'POST'])
@login_required
@Check_Token
def SM_US():
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
                      
        return render_template("Faculty-Home-Page/Schedule-Management/SM-University-Schedule.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               SM="show",
                               activate_US= "active",
                               profile_pic=ProfilePic)

# ------------------------------- CLASS SCHEDULE ----------------------------  

@SM.route("/SM-Class-Schedule", methods=['GET', 'POST'])
@login_required
@Check_Token
def SM_ClS():
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
                      
        return render_template("Faculty-Home-Page/Schedule-Management/SM-Class-Schedule.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               SM="show",
                               activate_ClS= "active",
                               profile_pic=ProfilePic)
        
# ------------------------------- SCHEDULED EVENTS ----------------------------  

@SM.route("/SM-Scheduled-Events", methods=['GET', 'POST'])
@login_required
@Check_Token
def SM_SE():
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
                      
        return render_template("Faculty-Home-Page/Schedule-Management/SM-Scheduled-Events.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               SM="show",
                               activate_SE= "active",
                               profile_pic=ProfilePic)
        
        





# ------------------------------- TEACHING ASSIGNMENTS ----------------------------  
import requests

@SM.route("/Schedule/api/get", methods=['GET', 'POST'])
@login_required
@Check_Token
def SM_Schedules():
    
      # Fetch API data
    api_url = "https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading"  # Replace with the actual API endpoint
    headers = {
        'Authorization': 'Bearer '+ os.environ["API_TOKENS_SCHEDULER"],
        'Content-Type': 'application/json'  # Adjust content type as needed
    }
    
    api_response = requests.get(api_url,headers=headers)
    
    if api_response.status_code == 200:
        api_data = api_response.json()
        return jsonify(api_data)
    else:
        api_data = {"message": "Failed to fetch data", "data": []}
        return jsonify(api_data)
   
   

@SM.route("/Schedule/api/get-semester", methods=['GET', 'POST'])
@login_required
@Check_Token
def SM_Schedules_sem():
    
      # Fetch API data
    api_url = "https://schedulerserver-6e565d991c10.herokuapp.com/semesters/getsemester"  # Replace with the actual API endpoint
    headers = {
        'Authorization': 'Bearer '+ os.environ["API_TOKENS_SCHEDULER"],
        'Content-Type': 'application/json'  # Adjust content type as needed
    }
    
    api_response = requests.get(api_url,headers=headers)
    
    if api_response.status_code == 200:
        api_data = api_response.json()
        return jsonify(api_data)
    else:
        api_data = {"message": "Failed to fetch data", "data": []}
        return jsonify(api_data)


@SM.route("/Schedule/api/get-acadyear", methods=['GET', 'POST'])
@login_required
@Check_Token
def SM_Schedules_acadyear():
    
      # Fetch API data
    api_url = "https://schedulerserver-6e565d991c10.herokuapp.com/academicyears/getacadyr"  # Replace with the actual API endpoint
    headers = {
        'Authorization': 'Bearer '+ os.environ["API_TOKENS_SCHEDULER"],
        'Content-Type': 'application/json'  # Adjust content type as needed
    }
    
    api_response = requests.get(api_url,headers=headers)
    
    if api_response.status_code == 200:
        api_data = api_response.json()
        return jsonify(api_data)
    else:
        api_data = {"message": "Failed to fetch data", "data": []}
        return jsonify(api_data)
   
 
 
        
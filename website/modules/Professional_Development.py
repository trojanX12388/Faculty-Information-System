from flask import Flask, Blueprint, redirect, render_template, request, url_for
from dotenv import load_dotenv
from flask_login import login_required, current_user
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from urllib.request import urlretrieve
from cryptography.fernet import Fernet
from datetime import datetime
import rsa

import os
import os.path
import requests

load_dotenv()

# DATABASE CONNECTION
from website.models import db
from sqlalchemy import update

# LOADING MODEL CLASSES
from website.models import FISFaculty

# LOADING FUNCTION CHECK TOKEN
from website.Token.token_check import Check_Token

# WEB AUTH ROUTES URL
PD = Blueprint('PD', __name__)

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


#                                                    PROFESSIONAL DEVELOPMENT

# ------------------------------- WORKSHOPS ----------------------------  

@PD.route("/PD-Workshops", methods=['GET', 'POST'])
@login_required
@Check_Token
def PD_W():
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
        #     faculty_code = request.form.get('faculty_code')
        #     honorific = request.form.get('honorific')

        #     u = update(FISFaculty)
        #     u = u.values({"faculty_code": faculty_code,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(FISFaculty.FacultyId == current_user.FacultyId)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
                      
        return render_template("Faculty-Home-Page/Professional-Development/PD-Workshops.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               profile_pic=ProfilePic,
                               PD="show",
                               activate_W= "active")

 
# ------------------------------------------------------------- 

# ------------------------------- TRAININGS ----------------------------  

@PD.route("/PD-Trainings", methods=['GET', 'POST'])
@login_required
@Check_Token
def PD_T():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        url = 'https://acmis.onrender.com/api/faculty/certificate/records/?format=json'
        response = requests.get(url)
    
        if response.status_code == 200:
            # Process the API response data
            api_data = response.json()

            # Filter the data for the person named "Alma Fernandez"
            records = [record for record in api_data if record.get('first_name', '') == current_user.FirstName and record.get('last_name', '') == current_user.LastName]

        # Format the date in the desired format
        for record in records:
            date_str = record.get('date', '')
            if date_str:
                formatted_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').strftime('%B %d, %Y')
                record['date'] = formatted_date

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
        # # UPDATE PROFILE BASIC DETAILS
        
        # if request.method == 'POST':

        #     # UPDATE BASIC DETAILS
        #     # VALUES
        #     faculty_code = request.form.get('faculty_code')
        #     honorific = request.form.get('honorific')

        #     u = update(FISFaculty)
        #     u = u.values({"faculty_code": faculty_code,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(FISFaculty.FacultyId == current_user.FacultyId)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
                      
        return render_template("Faculty-Home-Page/Professional-Development/PD-Trainings.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               profile_pic=ProfilePic,
                               records = records)

 
# ------------------------------------------------------------- 

# ------------------------------- SEMINARS ----------------------------  

@PD.route("/PD-Seminars", methods=['GET', 'POST'])
@login_required
@Check_Token
def PD_S():
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
        #     faculty_code = request.form.get('faculty_code')
        #     honorific = request.form.get('honorific')

        #     u = update(FISFaculty)
        #     u = u.values({"faculty_code": faculty_code,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(FISFaculty.FacultyId == current_user.FacultyId)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
                      
        return render_template("Faculty-Home-Page/Professional-Development/PD-Seminars.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               profile_pic=ProfilePic,
                               PD="show",
                               activate_S= "active")

 
# ------------------------------------------------------------- 

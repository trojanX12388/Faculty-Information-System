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
from website.models import FISFaculty

# LOADING FUNCTION CHECK TOKEN
from website.Token.token_check import Check_Token

# WEB AUTH ROUTES URL
MI = Blueprint('MI', __name__)

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


#                                                    MEDICAL INFORMATION ROUTE
        
# ------------------------------- MEDICAL INFORMATION ----------------------------  

@MI.route("/Medical-Information", methods=['GET', 'POST'])
@login_required
@Check_Token
def MI_H():
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
        # Access weight by iterating over the FISPDS_PersonalDetails relationship
        if username.FISPDS_PersonalDetails:
            for personal_details in username.FISPDS_PersonalDetails:
                weight = personal_details.weight
                height = personal_details.height
                break  # Assuming you want to get the weight from the first entry only
        else:
            weight = 0
            height = 0
    
                      
        return render_template("Faculty-Home-Page/Medical-Information/index.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               weight = weight,
                               height = height,
                               profile_pic=ProfilePic)
        
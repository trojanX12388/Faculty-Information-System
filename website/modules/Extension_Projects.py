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
from website.models import FISFaculty, ESISUser, Project, Collaborator

# LOADING FUNCTION CHECK TOKEN
from website.Token.token_check import Check_Token

# WEB AUTH ROUTES URL
EP = Blueprint('EP', __name__)

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


#                                                    RECORDS ROUTE


# ------------------------------- RECORDS ----------------------------  

@EP.route("/Extension-Projects", methods=['GET', 'POST'])
@login_required
@Check_Token
def R_H():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        
        ESISid = ESISUser.query.filter_by(FacultyId=current_user.FacultyId).first()

        if ESISid is not None:
            project = Project.query.filter_by(LeadProponentId=ESISid.UserId).all()
        else:
            project = None
        
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
    
            
        return render_template("Faculty-Home-Page/Extension-Projects/index.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               project=project, 
                               profile_pic=ProfilePic)

 
# ------------------------------------------------------------- 
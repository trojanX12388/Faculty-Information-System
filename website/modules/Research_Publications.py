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
from website.models import Faculty_Profile

# LOADING FUNCTION CHECK TOKEN
from website.Token.token_check import Check_Token

# WEB AUTH ROUTES URL
RP = Blueprint('RP', __name__)

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

@RP.route("/RP-collaboration-research-opportunities", methods=['GET', 'POST'])
@login_required
@Check_Token
def RP_H():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
        

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
           
        
        # # UPDATE PROFILE BASIC DETAILS
        
        # if request.method == 'POST':

        #     # UPDATE BASIC DETAILS
        #     # VALUES
        #     faculty_code = request.form.get('faculty_code')
        #     honorific = request.form.get('honorific')

        #     u = update(Faculty_Profile)
        #     u = u.values({"faculty_code": faculty_code,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(Faculty_Profile.faculty_account_id == current_user.faculty_account_id)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
        
        gatch = Faculty_Profile.query.filter_by(faculty_account_id='000-000-A-002').first() 
        dem = Faculty_Profile.query.filter_by(faculty_account_id='000-000-A-004').first() 
        che = Faculty_Profile.query.filter_by(faculty_account_id='000-000-A-012').first() 
        drew = Faculty_Profile.query.filter_by(faculty_account_id='2020-00073-D-1').first() 
        celeste = Faculty_Profile.query.filter_by(faculty_account_id='000-000-A-022').first() 
        berna = Faculty_Profile.query.filter_by(faculty_account_id='000-000-A-017').first() 
                      
        return render_template("Faculty-Home-Page/Research-Publications/Collaboration-Research-Opportunities.html", 
                               User= username.first_name + " " + username.last_name,
                               faculty_code= username.faculty_code,
                               user= current_user,
                               gatch = gatch,
                               dem = dem,
                               che = che,
                               drew = drew,
                               celeste = celeste,
                               berna = berna,
                               profile_pic=profile_pic,
                               RP="show",
                               activate_CRO= "active")

 
# ------------------------------------------------------------- 

@RP.route("/RP-Thesis", methods=['GET', 'POST'])
@login_required
@Check_Token
def RP_T():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
        

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
           
        
        # # UPDATE PROFILE BASIC DETAILS
        
        # if request.method == 'POST':

        #     # UPDATE BASIC DETAILS
        #     # VALUES
        #     faculty_code = request.form.get('faculty_code')
        #     honorific = request.form.get('honorific')

        #     u = update(Faculty_Profile)
        #     u = u.values({"faculty_code": faculty_code,
        #                   "honorific": honorific
        #                   })
        #     u = u.where(Faculty_Profile.faculty_account_id == current_user.faculty_account_id)
        #     db.session.execute(u)
        #     db.session.commit()
        #     db.session.close()
        #     return redirect(url_for('PDM.PDM_BD')) 
                      
        return render_template("Faculty-Home-Page/Research-Publications/Thesis.html", 
                               User= username.first_name + " " + username.last_name,
                               faculty_code= username.faculty_code,
                               user= current_user,
                               profile_pic=profile_pic,
                               RP="show",
                               activate_T= "active")

 
# ------------------------------------------------------------- 
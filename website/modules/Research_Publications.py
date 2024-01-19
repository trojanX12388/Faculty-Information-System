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


                                               


# ------------------------------- COLLABORATION AND RESEARCH OPPORTUNITIES ----------------------------  

@RP.route("/RP-collaboration-research-opportunities", methods=['GET', 'POST'])
@login_required
@Check_Token
def RP_CRO():
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
        
        gatch = FISFaculty.query.filter_by(FacultyId='10016').first() 
        dem = FISFaculty.query.filter_by(FacultyId='10001').first() 
        che = FISFaculty.query.filter_by(FacultyId='10009').first() 
        drew = FISFaculty.query.filter_by(FacultyId='10021').first() 
        celeste = FISFaculty.query.filter_by(FacultyId='10030').first() 
        berna = FISFaculty.query.filter_by(FacultyId='10008').first() 
                      
        return render_template("Faculty-Home-Page/Research-Publications/Collaboration-Research-Opportunities.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               gatch = gatch,
                               dem = dem,
                               che = che,
                               drew = drew,
                               celeste = celeste,
                               berna = berna,
                               profile_pic=ProfilePic,
                               RP="show",
                               activate_CRO= "active")


 
# ------------------------------------------------------------- THESIS ----------------------------------------------------
# ------------------------------------------------------------- 

@RP.route("/RP-Thesis", methods=['GET', 'POST'])
@login_required
@Check_Token
def RP_T():
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
                      
        return render_template("Faculty-Home-Page/Research-Publications/Thesis.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               profile_pic=ProfilePic,
                               RP="show",
                               activate_T= "active")

 
# ------------------------------------------------------------- 

# ------------------------------------------------------------- RESEARCH UTILIZATION ----------------------------------------------------
# ------------------------------------------------------------- 

@RP.route("/RP-Research-Utilization", methods=['GET', 'POST'])
@login_required
@Check_Token
def RP_RU():
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
                      
        return render_template("Faculty-Home-Page/Research-Publications/Research-Utilization.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               profile_pic=ProfilePic,
                               RP="show",
                               activate_RU= "active")

 
# ------------------------------------------------------------- 

# ------------------------------------------------------------- DISSERTATION ----------------------------------------------------
# ------------------------------------------------------------- 

@RP.route("/RP-Dissertation", methods=['GET', 'POST'])
@login_required
@Check_Token
def RP_D():
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
                      
        return render_template("Faculty-Home-Page/Research-Publications/Dissertation.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               profile_pic=ProfilePic,
                               RP="show",
                               activate_D= "active")

 
# ------------------------------------------------------------- 

# ------------------------------------------------------------- MASTERS THESIS ----------------------------------------------------
# ------------------------------------------------------------- 

@RP.route("/RP-Master-Thesis", methods=['GET', 'POST'])
@login_required
@Check_Token
def RP_MT():
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
                      
        return render_template("Faculty-Home-Page/Research-Publications/Master-Thesis.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               profile_pic=ProfilePic,
                               RP="show",
                               activate_MT= "active")

 
# ------------------------------------------------------------- 
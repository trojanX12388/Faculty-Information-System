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
from website.models import FISFaculty, FISProfessionalDevelopment

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

# ------------------------------- PROFESSIONAL DEVELOPMENT ----------------------------  

@PD.route("/Professional-Development", methods=['GET', 'POST'])
@login_required
@Check_Token
def PD_T():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
        if request.method == 'POST':
         
            # VALUES
           
            title = request.form.get('title')
            date_start = request.form.get('date_start')
            date_end = request.form.get('date_end')
            hours = request.form.get('hours')
            conduct_by = request.form.get('conduct_by')
            type = request.form.get('type')
            
            namefile = title + "_" + type
            
            id = request.form.get('id')
            file_id = request.form.get('file_id')
            
            file =  request.form.get('base64')
            
            ext = request.files.get('fileup')
            ext = ext.filename
            
            nameFile = f'{str(username.FacultyId)}{str(namefile)}'
            
        # PROFESSIONAL DEVELOPMENT FOLDER ID
            folder = '1j_3naGGNLgnSoLOq5IF7ZeGbBd8prsJ-'
            
            
            url = """data:application/pdf;base64,{}""".format(file)
                    
            filename, m = urlretrieve(url)
        
            file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
            try:
                for file1 in file_list:
                    if file1['id'] == str(file_id):
                        file1.Delete()                
            except:
                pass
            # CONFIGURE FILE FORMAT AND NAME
            file1 = drive.CreateFile(metadata={
                "title": ""+ str(nameFile),
                "parents": [{"id": folder}],
                "mimeType": "application/pdf"
                })
            
            # GENERATE FILE AND UPLOAD
            file1.SetContentFile(filename)
            file1.Upload()
            
            u = update(FISProfessionalDevelopment)
            u = u.values({"title": title,
                          "file_id": file_id,
                          "date_start": date_start,
                          "date_end": date_end,
                          "hours": hours,
                          "conducted_by": conduct_by,
                          "type": type,
              
                          })
            u = u.where(FISProfessionalDevelopment.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PD.PD_T')) 
                      
        return render_template("Faculty-Home-Page/Professional-Development/Professional-Development.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               profile_pic=ProfilePic)


     
@PD.route("/Professional-Development/add-record", methods=['GET', 'POST'])
@login_required
def PD_add():
        
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        
        title = request.form.get('title')
        date_start = request.form.get('date_start')
        date_end = request.form.get('date_end')
        hours = request.form.get('hours')
        conduct_by = request.form.get('conduct_by')
        type = request.form.get('type')
        
        namefile = title + "_" + type
        
        file =  request.form.get('base64')
        ext = request.files.get('fileup')
        ext = ext.filename
        
        id = f'{str(username.FacultyId)}{str(namefile)}'
        
       # CAPSTONE FOLDER ID
        folder = '1j_3naGGNLgnSoLOq5IF7ZeGbBd8prsJ-'
        
        
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
        
        add_record = FISProfessionalDevelopment(title=title,
                                                file_id='%s'%(file1['id']),
                                                date_start=date_start,
                                                date_end=date_end,
                                                hours=hours,
                                                conducted_by=conduct_by,
                                                type=type,
                                                FacultyId = current_user.FacultyId,
                                                )
        
        db.session.add(add_record)
        db.session.commit()
        db.session.close()
        
        return redirect(url_for('PD.PD_T'))
            
           
@PD.route("/Professional-Development/delete-record", methods=['GET', 'POST'])
@login_required
def PD_del():
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 

        id = request.form.get('id')
        
        
        data = FISProfessionalDevelopment.query.filter_by(id=id).first() 
        
        if data:
            namefile = data.title + "_" + data.type
            id = f'{str(username.FacultyId)}{str(namefile)}'
        
            # CAPSTONE FOLDER ID
            folder = '1j_3naGGNLgnSoLOq5IF7ZeGbBd8prsJ-'
        
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
            return redirect(url_for('PD.PD_T'))   
 
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

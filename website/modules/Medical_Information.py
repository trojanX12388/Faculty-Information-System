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
from website.models import FISFaculty, FISMedicalInformation

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
           
        
        # UPDATE MEDICAL INFORMATION DETAILS
        if request.method == 'POST':
            # UPDATE BASIC DETAILS
            contact_person_name = request.form.get('contact_person_name')
            home_contact_number = request.form.get('home_contact_number')
            address = request.form.get('address')
            work_phone_number = request.form.get('work_phone_number')

            # GENERAL MEDICAL HISTORY
            gridRadiosvaccine = request.form.get('gridRadiosvaccine') == 'True'
            gridRadiosBooster = request.form.get('gridRadiosBooster') == 'True'

            medical_problem1 = request.form.get('medical_problem1')
            medical_problem2 = request.form.get('medical_problem2')
            medical_problem3 = request.form.get('medical_problem3')
            medical_problem4 = request.form.get('medical_problem4')
            medical_problem5 = request.form.get('medical_problem5')
            medical_problem6 = request.form.get('medical_problem6')

            # ADDITIONAL INFORMATION
            q1 = request.form.get('q1') == 'True'
            q2 = request.form.get('q2') == 'True'
            q3 = request.form.get('q3') == 'True'

            # Check if FacultyId exists
            existing_record = db.session.query(FISMedicalInformation).filter_by(FacultyId=current_user.FacultyId).first()

            if existing_record:
                # FacultyId exists, update the existing record
                existing_record.contact_person_name = contact_person_name
                existing_record.home_contact_number = home_contact_number
                existing_record.address = address
                existing_record.work_phone_number = work_phone_number
                existing_record.gridRadiosvaccine = gridRadiosvaccine
                existing_record.gridRadiosBooster = gridRadiosBooster
                existing_record.medical_problem1 = medical_problem1
                existing_record.medical_problem2 = medical_problem2
                existing_record.medical_problem3 = medical_problem3
                existing_record.medical_problem4 = medical_problem4
                existing_record.medical_problem5 = medical_problem5
                existing_record.medical_problem6 = medical_problem6
                existing_record.q1 = q1
                existing_record.q2 = q2
                existing_record.q3 = q3
            else:
                # FacultyId does not exist, add a new record
                new_record = FISMedicalInformation(
                    FacultyId=current_user.FacultyId,
                    contact_person_name=contact_person_name,
                    home_contact_number=home_contact_number,
                    address=address,
                    work_phone_number=work_phone_number,
                    gridRadiosvaccine=gridRadiosvaccine,
                    gridRadiosBooster=gridRadiosBooster,
                    medical_problem1=medical_problem1,
                    medical_problem2=medical_problem2,
                    medical_problem3=medical_problem3,
                    medical_problem4=medical_problem4,
                    medical_problem5=medical_problem5,
                    medical_problem6=medical_problem6,
                    q1=q1,
                    q2=q2,
                    q3=q3
                )
                db.session.add(new_record)

            db.session.commit()

            return redirect(url_for('MI.MI_H'))
        
        # Access weight by iterating over the FISPDS_PersonalDetails relationship
        
        if username.FISPDS_PersonalDetails:
            for personal_details in username.FISPDS_PersonalDetails:
                weight = personal_details.weight
                height = personal_details.height
                break  # Assuming you want to get the weight from the first entry only
        else:
            weight = 0
            height = 0
            
        if username.FISMedicalInformation:
            record = username.FISMedicalInformation[0]  # Assuming you want to get the data from the first entry only

            contact_person_name = record.contact_person_name
            home_contact_number = record.home_contact_number
            address = record.address
            work_phone_number = record.work_phone_number

            # Check and conditionally exclude True/False values
            gridRadiosvaccine = record.gridRadiosvaccine if record.gridRadiosvaccine else "False"
            gridRadiosBooster = record.gridRadiosBooster if record.gridRadiosBooster else "False"

            medical_problem1 = record.medical_problem1
            medical_problem2 = record.medical_problem2
            medical_problem3 = record.medical_problem3
            medical_problem4 = record.medical_problem4
            medical_problem5 = record.medical_problem5
            medical_problem6 = record.medical_problem6

            # Check and conditionally exclude True/False values
            q1 = str(record.q1) if record.q1 is not None else "False"
            q2 = str(record.q2) if record.q2 is not None else "False"
            q3 = str(record.q3) if record.q3 is not None else "False"
        else:
            contact_person_name = ""
            home_contact_number = ""
            address = ""
            work_phone_number = ""
            gridRadiosvaccine = "False"
            gridRadiosBooster = "False"
            medical_problem1 = ""
            medical_problem2 = ""
            medical_problem3 = ""
            medical_problem4 = ""
            medical_problem5 = ""
            medical_problem6 = ""
            q1 = "False"
            q2 = "False"
            q3 = "False"

        return render_template("Faculty-Home-Page/Medical-Information/index.html", 
                                User=username.FirstName + " " + username.LastName,
                                faculty_code=username.FacultyCode,
                                user=current_user,
                                weight=weight,
                                height=height,
                                contact_person_name=contact_person_name,
                                home_contact_number=home_contact_number,
                                address=address,
                                work_phone_number=work_phone_number,
                                gridRadiosvaccine=gridRadiosvaccine,
                                gridRadiosBooster=gridRadiosBooster,
                                medical_problem1=medical_problem1,
                                medical_problem2=medical_problem2,
                                medical_problem3=medical_problem3,
                                medical_problem4=medical_problem4,
                                medical_problem5=medical_problem5,
                                medical_problem6=medical_problem6,
                                q1=q1,
                                q2=q2,
                                q3=q3,
                                profile_pic=ProfilePic)
        
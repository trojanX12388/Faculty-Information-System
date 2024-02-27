from flask import Flask, Blueprint, redirect, render_template, request, url_for, flash, jsonify, abort
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

load_dotenv()

# DATABASE CONNECTION
from website.models import db
from sqlalchemy import update

# LOADING MODEL CLASSES
from website.models import FISFaculty, FISMandatoryRequirements, FISUser_Notifications

# LOADING FUNCTION CHECK TOKEN
from website.Token.token_check import Check_Token

# WEB AUTH ROUTES URL
MR = Blueprint('MR', __name__)

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


#                                                    MANDATORY REQUIREMENTS ROUTE
        
# ------------------------------- MANDATORY REQUIREMENTS ----------------------------  

@MR.route("/Mandatory-Requirements", methods=['GET', 'POST'])
@login_required
@Check_Token
def MR_H():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISFaculty.query.filter_by(FacultyId=current_user.FacultyId).first() 
        from sqlalchemy import desc

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
           
        
        # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.FISMandatoryRequirements:
        
            record = FISMandatoryRequirements.query.filter_by(FacultyId=current_user.FacultyId, year=str(datetime.now().year)).order_by(desc(FISMandatoryRequirements.id)).first()

            classrecord = record.classrecord
            gradingsheet = record.gradingsheet
            exams = record.exams
            classrecord_status = record.classrecord_status
            gradingsheet_status = record.gradingsheet_status
            exams_status = record.exams_status
            year = record.year

  
            records = {
                            'classrecord': classrecord,
                            'gradingsheet': gradingsheet,
                            'exams': exams,
                            'classrecord_status': classrecord_status,
                            'gradingsheet_status': gradingsheet_status,
                            'exams_status': exams_status,
                            'year': year,
              
                        }
            
        else:
            records = {
                            'classrecord': "",
                            'gradingsheet': "",
                            'exams': "",
                            'classrecord_status': "None",
                            'gradingsheet_status': "None",
                            'exams_status': "None",
                            'year': str(datetime.now().year),

                        }
                    
            
        if request.method == 'POST':
        
            select = request.form.get('select')
            record = FISMandatoryRequirements.query.filter_by(FacultyId=current_user.FacultyId, id=select).first()

            classrecord = record.classrecord
            gradingsheet = record.gradingsheet
            exams = record.exams
            classrecord_status = record.classrecord_status
            gradingsheet_status = record.gradingsheet_status
            exams_status = record.exams_status
            year = record.year

  
            records = {
                            'classrecord': classrecord,
                            'gradingsheet': gradingsheet,
                            'exams': exams,
                            'classrecord_status': classrecord_status,
                            'gradingsheet_status': gradingsheet_status,
                            'exams_status': exams_status,
                            'year': year,
              
                        }
        
        return render_template("Faculty-Home-Page/Mandatory-Requirements/index.html", 
                               User= username.FirstName + " " + username.LastName,
                               faculty_code= username.FacultyCode,
                               user= current_user,
                               records = records,
                               profile_pic=ProfilePic)
        

   
@MR.route("/Mandatory-Requirements/upload-classrecord", methods=['GET', 'POST'])
@login_required
def MR_add_classrecord():
         
        year = request.form.get('year')
        
        namefile = str(current_user.FacultyId) + "_" + "classrecord"+ "_" + "year: "+ str(year)
        
        file =  request.form.get('base64')
        ext = request.files.get('fileup')
        ext = ext.filename
        
       # CAPSTONE FOLDER ID
        folder = '1aqdjGSNXMBFR9iZH3Nej8sCX4vQx8ynP'
        
        if FISMandatoryRequirements.query.filter_by(FacultyId=current_user.FacultyId,year=year).first():
            id = FISMandatoryRequirements.query.filter_by(FacultyId=current_user.FacultyId,year=year).first()
            try:
                
                url = """data:application/pdf;base64,{}""".format(file)
                        
                filename, m = urlretrieve(url)
            
                file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
                try:
                    for file1 in file_list:
                        if file1['title'] == str(namefile):
                            file1.Delete()                
                except:
                    pass
                # CONFIGURE FILE FORMAT AND NAME
                file1 = drive.CreateFile(metadata={
                    "title": ""+ str(namefile),
                    "parents": [{"id": folder}],
                    "mimeType": "application/pdf"
                    })
                
                # GENERATE FILE AND UPLOAD
                file1.SetContentFile(filename)
                file1.Upload()
                
                u = update(FISMandatoryRequirements)
                u = u.values({
                            "classrecord": '%s'%(file1['id']),
                            "year": year,
                            "classrecord_status": "Pending",
                            })
                u = u.where(FISMandatoryRequirements.id == id.id)
                db.session.execute(u)
                db.session.commit()
                
                add_notif = FISUser_Notifications(
                AdminId='10001',
                Status= "pending",
                Type= "notif",
                notif_by = current_user.FacultyId,
                notifier_type = "Faculty",
                Notification = "Updated Class Record for year : " + year,
                )
                
                db.session.add(add_notif)
                db.session.commit()
                
                db.session.close()
                
                flash('successfully updated!', category='success')
                return redirect(url_for('MR.MR_H'))
            except:
                flash('Unsuccessfully updated. Please try again...', category='error')
                return redirect(url_for('MR.MR_H'))
        else:       
            try:
                
                url = """data:application/pdf;base64,{}""".format(file)
                        
                filename, m = urlretrieve(url)
            
                file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
                try:
                    for file1 in file_list:
                        if file1['title'] == str(namefile):
                            file1.Delete()                
                except:
                    pass
                # CONFIGURE FILE FORMAT AND NAME
                file1 = drive.CreateFile(metadata={
                    "title": ""+ str(namefile),
                    "parents": [{"id": folder}],
                    "mimeType": "application/pdf"
                    })
                
                # GENERATE FILE AND UPLOAD
                file1.SetContentFile(filename)
                file1.Upload()
                
                add_record = FISMandatoryRequirements(
                                                        classrecord='%s'%(file1['id']),
                                                        year=year,
                                                        classrecord_status="Pending",
                                                        FacultyId = current_user.FacultyId,
                                                        )
                
                db.session.add(add_record)
                db.session.commit()
                
                add_notif = FISUser_Notifications(
                AdminId='10001',
                Status= "pending",
                Type= "notif",
                notif_by = current_user.FacultyId,
                notifier_type = "Faculty",
                Notification = "Uploaded Class Record for year : " + year,
                )
                
                db.session.add(add_notif)
                db.session.commit()
                
                db.session.close()
                flash('successfully uploaded!', category='success')
                return redirect(url_for('MR.MR_H'))
            except:
                flash('Unsuccessfully uploaded. Please try again...', category='error')
                return redirect(url_for('MR.MR_H'))   
           


   
@MR.route("/Mandatory-Requirements/upload-gradingsheet", methods=['GET', 'POST'])
@login_required
def MR_add_gradingsheet():
         
        year = request.form.get('year')
        
        namefile = str(current_user.FacultyId) + "_" + "gradingsheet"+ "_" + "year: "+ str(year)
        
        file =  request.form.get('base642')
        ext = request.files.get('fileup2')
        ext = ext.filename
        
       # CAPSTONE FOLDER ID
        folder = '1_C2MenZ0Dq13peaD9_OdIBAQLvQKJkG6'
        
        if FISMandatoryRequirements.query.filter_by(FacultyId=current_user.FacultyId,year=year).first():
            id = FISMandatoryRequirements.query.filter_by(FacultyId=current_user.FacultyId,year=year).first()
            try:
                
                url = """data:application/pdf;base64,{}""".format(file)
                        
                filename, m = urlretrieve(url)
            
                file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
                try:
                    for file1 in file_list:
                        if file1['title'] == str(namefile):
                            file1.Delete()                
                except:
                    pass
                # CONFIGURE FILE FORMAT AND NAME
                file1 = drive.CreateFile(metadata={
                    "title": ""+ str(namefile),
                    "parents": [{"id": folder}],
                    "mimeType": "application/pdf"
                    })
                
                # GENERATE FILE AND UPLOAD
                file1.SetContentFile(filename)
                file1.Upload()
                
                u = update(FISMandatoryRequirements)
                u = u.values({
                            "gradingsheet": '%s'%(file1['id']),
                            "year": year,
                            "gradingsheet_status": "Pending",
                            })
                u = u.where(FISMandatoryRequirements.id == id.id)
                db.session.execute(u)
                db.session.commit()
                
                add_notif = FISUser_Notifications(
                AdminId='10001',
                Status= "pending",
                Type= "notif",
                notif_by = current_user.FacultyId,
                notifier_type = "Faculty",
                Notification = "Updated Grading Sheet for year : " + year,
                )
                
                db.session.add(add_notif)
                db.session.commit()
                
                db.session.close()
                
                flash('successfully updated!', category='success')
                return redirect(url_for('MR.MR_H'))
            except:
                flash('Unsuccessfully updated. Please try again...', category='error')
                return redirect(url_for('MR.MR_H'))
        else:       
            try:
                
                url = """data:application/pdf;base64,{}""".format(file)
                        
                filename, m = urlretrieve(url)
            
                file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
                try:
                    for file1 in file_list:
                        if file1['title'] == str(namefile):
                            file1.Delete()                
                except:
                    pass
                # CONFIGURE FILE FORMAT AND NAME
                file1 = drive.CreateFile(metadata={
                    "title": ""+ str(namefile),
                    "parents": [{"id": folder}],
                    "mimeType": "application/pdf"
                    })
                
                # GENERATE FILE AND UPLOAD
                file1.SetContentFile(filename)
                file1.Upload()
                
                add_record = FISMandatoryRequirements(
                                                        gradingsheet='%s'%(file1['id']),
                                                        year=year,
                                                        gradingsheet_status="Pending",
                                                        FacultyId = current_user.FacultyId,
                                                        )
                
                db.session.add(add_record)
                db.session.commit()
                
                add_notif = FISUser_Notifications(
                AdminId='10001',
                Status= "pending",
                Type= "notif",
                notif_by = current_user.FacultyId,
                notifier_type = "Faculty",
                Notification = "Uploaded Grading Sheet for year : " + year,
                )
                
                db.session.add(add_notif)
                db.session.commit()
                
                db.session.close()
                flash('successfully uploaded!', category='success')
                return redirect(url_for('MR.MR_H'))
            except:
                flash('Unsuccessfully uploaded. Please try again...', category='error')
                return redirect(url_for('MR.MR_H'))   
           



   
@MR.route("/Mandatory-Requirements/upload-exams", methods=['GET', 'POST'])
@login_required
def MR_add_exams():
         
        year = request.form.get('year')
        
        namefile = str(current_user.FacultyId) + "_" + "exams"+ "_" + "year: "+ str(year)
        
        file =  request.form.get('base643')
        ext = request.files.get('fileup3')
        ext = ext.filename
        
       # CAPSTONE FOLDER ID
        folder = '1ZblfxAzuYSx6QJCKCffrVwE2scNlRKx2'
        
        if FISMandatoryRequirements.query.filter_by(FacultyId=current_user.FacultyId,year=year).first():
            id = FISMandatoryRequirements.query.filter_by(FacultyId=current_user.FacultyId,year=year).first()
            try:
                
                url = """data:application/pdf;base64,{}""".format(file)
                        
                filename, m = urlretrieve(url)
            
                file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
                try:
                    for file1 in file_list:
                        if file1['title'] == str(namefile):
                            file1.Delete()                
                except:
                    pass
                # CONFIGURE FILE FORMAT AND NAME
                file1 = drive.CreateFile(metadata={
                    "title": ""+ str(namefile),
                    "parents": [{"id": folder}],
                    "mimeType": "application/pdf"
                    })
                
                # GENERATE FILE AND UPLOAD
                file1.SetContentFile(filename)
                file1.Upload()
                
                u = update(FISMandatoryRequirements)
                u = u.values({
                            "exams": '%s'%(file1['id']),
                            "year": year,
                            "exams_status": "Pending",
                            })
                u = u.where(FISMandatoryRequirements.id == id.id)
                db.session.execute(u)
                db.session.commit()
                
                add_notif = FISUser_Notifications(
                AdminId='10001',
                Status= "pending",
                Type= "notif",
                notif_by = current_user.FacultyId,
                notifier_type = "Faculty",
                Notification = "Updated Exams for year : " + year,
                )
                
                db.session.add(add_notif)
                db.session.commit()
                
                db.session.close()
                
                flash('successfully updated!', category='success')
                return redirect(url_for('MR.MR_H'))
            except:
                flash('Unsuccessfully updated. Please try again...', category='error')
                return redirect(url_for('MR.MR_H'))
        else:       
            try:
                
                url = """data:application/pdf;base64,{}""".format(file)
                        
                filename, m = urlretrieve(url)
            
                file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
                try:
                    for file1 in file_list:
                        if file1['title'] == str(namefile):
                            file1.Delete()                
                except:
                    pass
                # CONFIGURE FILE FORMAT AND NAME
                file1 = drive.CreateFile(metadata={
                    "title": ""+ str(namefile),
                    "parents": [{"id": folder}],
                    "mimeType": "application/pdf"
                    })
                
                # GENERATE FILE AND UPLOAD
                file1.SetContentFile(filename)
                file1.Upload()
                
                add_record = FISMandatoryRequirements(
                                                        exams='%s'%(file1['id']),
                                                        year=year,
                                                        exams_status="Pending",
                                                        FacultyId = current_user.FacultyId,
                                                        )
                
                db.session.add(add_record)
                db.session.commit()
                
                add_notif = FISUser_Notifications(
                AdminId='10001',
                Status= "pending",
                Type= "notif",
                notif_by = current_user.FacultyId,
                notifier_type = "Faculty",
                Notification = "Uploaded Exams for year : " + year,
                )
                
                db.session.add(add_notif)
                db.session.commit()
                
                db.session.close()
                flash('successfully uploaded!', category='success')
                return redirect(url_for('MR.MR_H'))
            except:
                flash('Unsuccessfully uploaded. Please try again...', category='error')
                return redirect(url_for('MR.MR_H'))   
           






  
@MR.route('/Mandatory-Requirements/api/get-record', methods=['GET', 'POST'])
@login_required
@Check_Token
def MR_api_record():
    
    # Fetch all data from FISRequests
    year = str(datetime.now().year)
    requests = FISMandatoryRequirements.query.filter_by(FacultyId=current_user.FacultyId,year=year).first()
    isnotified = FISUser_Notifications.query.filter_by(FacultyId=current_user.FacultyId, Type='mandatory').all()
    
    # Create a list to store the selected fields for each log entry
    formatted_requests = []
    # print("pass1")
    if requests:
        # print("pass2")
        if isnotified:  
            # print("notified")
            if requests.classrecord is None:  # If no record exists in database yet
                required_notifications = [
            "You Have no requirements for Class Record in year : " + year,]

                for required_notification in required_notifications:
                    existing_notification = FISUser_Notifications.query.filter_by(
                        FacultyId=current_user.FacultyId,
                        Notification=required_notification
                    ).first()

                    if not existing_notification:
                        # print(f"Notification does not exist, adding: {required_notification}")
                        add_notif = FISUser_Notifications(
                            FacultyId=current_user.FacultyId,
                            Status="pending",
                            Type="mandatory",
                            notif_by=None,
                            notifier_type="System",
                            Notification=required_notification,
                        )

                        db.session.add(add_notif)

                db.session.commit()
                db.session.close()

                # Create a dictionary with the required data
                formatted_request = {
                    'year': None,
                    'FacultyId': None,
                }

                formatted_requests.append(formatted_request)
                
            
            elif requests.gradingsheet is None:  # If no record exists in database yet
                # print("has notif but no grading sheet")
                required_notifications = ["You Have no requirements for Grading Sheet in year : " + year,]

                for required_notification in required_notifications:
                    existing_notification = FISUser_Notifications.query.filter_by(
                        FacultyId=current_user.FacultyId,
                        Notification=required_notification
                    ).first()

                    if not existing_notification:
                        # print(f"Notification does not exist, adding: {required_notification}")
                        add_notif = FISUser_Notifications(
                            FacultyId=current_user.FacultyId,
                            Status="pending",
                            Type="mandatory",
                            notif_by=None,
                            notifier_type="System",
                            Notification=required_notification,
                        )

                        db.session.add(add_notif)

                db.session.commit()
                db.session.close()

                # Create a dictionary with the required data
                formatted_request = {
                    'year': None,
                    'FacultyId': None,
                }

                formatted_requests.append(formatted_request)
                
            elif requests.exams is None:  # If no record exists in database yet
                # print("has notif but no exam")
                required_notifications = ["You Have no requirements for Exams in year : " + year,]

                for required_notification in required_notifications:
                    existing_notification = FISUser_Notifications.query.filter_by(
                        FacultyId=current_user.FacultyId,
                        Notification=required_notification
                    ).first()

                    if not existing_notification:
                        # print(f"Notification does not exist, adding: {required_notification}")
                        add_notif = FISUser_Notifications(
                            FacultyId=current_user.FacultyId,
                            Status="pending",
                            Type="mandatory",
                            notif_by=None,
                            notifier_type="System",
                            Notification=required_notification,
                        )

                        db.session.add(add_notif)

                db.session.commit()
                db.session.close()

                # Create a dictionary with the required data
                formatted_request = {
                    'year': None,
                    'FacultyId': None,
                }

                formatted_requests.append(formatted_request)
                
            else:               # If there are records in the database
                # print("has notif and requirements")
                year = requests.year 
                facultyid = requests.FacultyId 

                # Create a dictionary with the required data
                formatted_request = {
                    'year': year, 
                    'FacultyId': facultyid, 
                }
                
                formatted_requests.append(formatted_request)
                
        else:  # If there are records in the database
            # print("notnotified")
            if requests.classrecord is None:  # If no record exists in database yet
                # print("not notif but no record")
                add_notif = FISUser_Notifications(
                FacultyId=current_user.FacultyId,
                Status= "pending",
                Type= "mandatory",
                notif_by = None,
                notifier_type = "System",
                Notification = "You Have no requirements for Class Record in year : " + year,
                )
                
                db.session.add(add_notif)
                db.session.commit()
                db.session.close()
                
                # Create a dictionary with the required data
                formatted_request = {
                    'year': None, 
                    'FacultyId': None, 
                }
                
                formatted_requests.append(formatted_request)
            
            elif requests.gradingsheet is None:  # If no record exists in database yet
                # print("not notif but no grading sheet")
                add_notif = FISUser_Notifications(
                FacultyId=current_user.FacultyId,
                Status= "pending",
                Type= "mandatory",
                notif_by = None,
                notifier_type = "System",
                Notification = "You Have no requirements for Grading Sheet in year : " + year,
                )
                
                db.session.add(add_notif)
                db.session.commit()
                db.session.close()
                
                # Create a dictionary with the required data
                formatted_request = {
                    'year': None, 
                    'FacultyId': None, 
                }
                
                formatted_requests.append(formatted_request)
                
            elif requests.exams is None:  # If no record exists in database yet
                # print("not notif but no exam")
                add_notif = FISUser_Notifications(
                FacultyId=current_user.FacultyId,
                Status= "pending",
                Type= "mandatory",
                notif_by = None,
                notifier_type = "System",
                Notification = "You Have no requirements for Exams in year : " + year,
                )
                
                db.session.add(add_notif)
                db.session.commit()
                db.session.close()
                
                # Create a dictionary with the required data
                formatted_request = {
                    'year': None, 
                    'FacultyId': None, 
                }
                
                formatted_requests.append(formatted_request)
                
            else:               # If there are records in the database
                # print("not notif and has requirements")
                year = requests.year 
                facultyid = requests.FacultyId 

                # Create a dictionary with the required data
                formatted_request = {
                    'year': year, 
                    'FacultyId': facultyid, 
                }
                
                formatted_requests.append(formatted_request)
            
    elif isnotified:
        required_notifications = [
            "You Have no requirements for Class Record in year : " + year,
            "You Have no requirements for Grading Sheet in year : " + year,
            "You Have no requirements for Exams in year : " + year,
        ]

        for required_notification in required_notifications:
            existing_notification = FISUser_Notifications.query.filter_by(
                FacultyId=current_user.FacultyId,
                Notification=required_notification
            ).first()

            if not existing_notification:
                # print(f"Notification does not exist, adding: {required_notification}")
                add_notif = FISUser_Notifications(
                    FacultyId=current_user.FacultyId,
                    Status="pending",
                    Type="mandatory",
                    notif_by=None,
                    notifier_type="System",
                    Notification=required_notification,
                )

                db.session.add(add_notif)

        db.session.commit()
        db.session.close()

        # Create a dictionary with the required data
        formatted_request = {
            'year': None,
            'FacultyId': None,
        }

        formatted_requests.append(formatted_request)
    else:
        # print("notified to all requirements")
        
        add_notif1 = FISUser_Notifications(
        FacultyId=current_user.FacultyId,
        Status= "pending",
        Type= "mandatory",
        notif_by = None,
        notifier_type = "System",
        Notification = "You Have no requirements for Class Record in year : " + year,
        )
        
        db.session.add(add_notif1)
        db.session.commit()
        
        add_notif2 = FISUser_Notifications(
        FacultyId=current_user.FacultyId,
        Status= "pending",
        Type= "mandatory",
        notif_by = None,
        notifier_type = "System",
        Notification = "You Have no requirements for Grading Sheet in year : " + year,
        )
        
        db.session.add(add_notif2)
        db.session.commit()
        
        add_notif3 = FISUser_Notifications(
        FacultyId=current_user.FacultyId,
        Status= "pending",
        Type= "mandatory",
        notif_by = None,
        notifier_type = "System",
        Notification = "You Have no requirements for Exams in year : " + year,
        )
        
        db.session.add(add_notif3)
        db.session.commit()
        
        db.session.close()
        
        # Create a dictionary with the required data
        formatted_request = {
            'year': None, 
            'FacultyId': None, 
        }
        
        formatted_requests.append(formatted_request)    
        
    # print("pass9")
    
    # Create a dictionary with the required data
    api_response_data = {
        'record': formatted_requests
    }

    # print("pass10")
    
    # Return the data as JSON using Flask's jsonify
    return jsonify(api_response_data)
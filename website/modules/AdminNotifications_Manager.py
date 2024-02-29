from flask import Flask, Blueprint, abort, flash, json, make_response, redirect, render_template, request, jsonify, url_for
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from flask_login import login_user,login_required, logout_user, current_user, LoginManager
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from flask_mail import Mail,Message
from datetime import datetime, timedelta, timezone

import os,requests

from sqlalchemy.exc import IntegrityError  # Import this for catching database integrity errors
import traceback 


load_dotenv()

# IMPORT LOCAL FUNCTIONS
from website.API.authentication import *
from website.Token.token_gen import *
from website.Token.token_check import Check_Token, SysCheck_Token

# IMPORT SMTP EMAILING FUNCTIONS

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

# DATABASE CONNECTION
from website.models import db
from sqlalchemy import update

# LOADING MODEL CLASSES
from website.models import FISAdmin, FISAdmin, FISAdmin_Notifications, FISSystemAdmin, FISUser_Notifications, FISFaculty


# LOAD JWT MODULE
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, decode_token

# EXECUTING DATABASE

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

engine=create_engine(os.getenv('DATABASE_URI'), pool_pre_ping=True, pool_size=10, max_overflow=20, pool_recycle=1800)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------------------------------------------------------------

# SMTP CONFIGURATION

app.config["MAIL_SERVER"]=os.getenv("MAILSERVER") 
app.config["MAIL_PORT"]=os.getenv("MAILPORT") 
app.config["MAIL_USERNAME"] = os.getenv("FISGMAIL")     
app.config['MAIL_PASSWORD'] = os.getenv("FISGMAILPASS")       
app.config['MAIL_DEFAULT_SENDER'] = 'PUPQC FIS'     
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True


# -------------------------------------------------------------

# PYDRIVE AUTH CONFIGURATION
gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# Default Profile Pic
profile_default='14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08'

# -------------------------------------------------------------
# WEB AUTH ROUTES URL
adminnotification = Blueprint('adminnotification', __name__)

# -------------------------------------------------------------

# ADMIN NOTIFICATIONS 

       
# ------------------------------- ADMIN NOTIFICATIONS ----------------------------  

@adminnotification.route("/Admin-Notifications", methods=['GET', 'POST'])
@login_required
@Check_Token
def AN_H():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
        
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
         
        done = 0
        decline = 0
        notifs = 0
        read = 0
        update = 0
        pending = 0
        mandatory = 0
        trash = 0

        all_notif = FISAdmin_Notifications.query.all() 

        unique_notif_ids = set()
        
        all_faculties = FISFaculty.query.all() 
        
        # Iterate through current_user notifications
        for notif in current_user.FISAdmin_Notifications:
            unique_notif_ids.add(notif.id)  # Add unique notif IDs
            if notif.Type == 'done':
                done += 1
            elif notif.Type == 'pending':
                pending += 1
            elif notif.Type == 'read':
                read += 1
            elif notif.Type == 'update':
                update += 1
            elif notif.Type == 'mandatory':
                mandatory += 1
            elif notif.Type == 'trash':
                trash += 1
            elif notif.Type == 'decline':
                decline += 1
            else:
                notifs += 1

        # Iterate through faculty notifications
        faculty_notifs = FISAdmin_Notifications.query.filter_by(notifier_type='Faculty').all()
        for notif in faculty_notifs:
            if notif.id not in unique_notif_ids:
                unique_notif_ids.add(notif.id)  # Add unique notif IDs
                if notif.Type == 'done':
                    done += 1
                elif notif.Type == 'pending':
                    pending += 1
                elif notif.Type == 'read':
                    read += 1
                elif notif.Type == 'update':
                    update += 1
                elif notif.Type == 'mandatory':
                    mandatory += 1
                elif notif.Type == 'trash':
                    trash += 1
                elif notif.Type == 'decline':
                    decline += 1
                else:
                    notifs += 1
        
        return render_template("Admin-Home-Page/Notifications/index.html", 
                               User= username.FirstName + " " + username.LastName,
                               user= current_user,
                               done=done,
                                notifs=notifs,
                                read=read,
                                update=update,
                                pending=pending,
                                mandatory=mandatory,
                                trash=trash,
                                unique_notif_ids = unique_notif_ids,
                                all_notif = all_notif,
                                decline = decline,
                                all_faculties = all_faculties,
                                
                            #    records = records,
                               profile_pic=ProfilePic)
        
        

@adminnotification.route("/Admin-Notifications/read", methods=['GET', 'POST'])
@login_required
@Check_Token
def AN_R():
   # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            id = request.form.get('id')

            u = update(FISAdmin_Notifications)
            u = u.values({"Type": 'read',"Status": 'read',})
            
            u = u.where(FISAdmin_Notifications.id == id)
            
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            
            return redirect(url_for('adminnotification.AN_H'))
        


@adminnotification.route("/Admin-Notifications/unread", methods=['GET', 'POST'])
@login_required
@Check_Token
def AN_UR():
   # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            id = request.form.get('id')

            u = update(FISAdmin_Notifications)
            u = u.values({"Type": 'notif',"Status": 'read',})
            
            u = u.where(FISAdmin_Notifications.id == id)
            
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            
            return redirect(url_for('adminnotification.AN_H'))
        



@adminnotification.route("/Admin-Notifications/decline", methods=['GET', 'POST'])
@login_required
@Check_Token
def AN_DE():
   # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            id = request.form.get('id')
            facultyid = request.form.get('facultyid')
            notif = request.form.get('notif')

            u = update(FISAdmin_Notifications)
            u = u.values({"Type": 'decline',"Status": 'decline',})
            
            u = u.where(FISAdmin_Notifications.id == id)
            
            db.session.execute(u)
            db.session.commit()
            
            add_notif = FISUser_Notifications(
            FacultyId=facultyid,
            Status= "pending",
            Type= "notif",
            notif_by = int(current_user.AdminId),
            notifier_type = "Admin",
            Notification = "Admin declined your "+notif+".",
            )
            
            db.session.add(add_notif)
            db.session.commit()
            
            db.session.close()
            
            return redirect(url_for('adminnotification.AN_H'))




@adminnotification.route("/Admin-Notifications/done", methods=['GET', 'POST'])
@login_required
@Check_Token
def AN_DONE():
   # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            id = request.form.get('id')
            facultyid = request.form.get('facultyid')
            notif = request.form.get('notif')

            u = update(FISAdmin_Notifications)
            u = u.values({"Type": 'done',"Status": 'done',})
            
            u = u.where(FISAdmin_Notifications.id == id)
            
            db.session.execute(u)
            db.session.commit()
            
            add_notif = FISUser_Notifications(
            FacultyId=facultyid,
            Status= "pending",
            Type= "done",
            notif_by = int(current_user.AdminId),
            notifier_type = "Admin",
            Notification = "Admin approved your "+notif+".",
            )
            
            db.session.add(add_notif)
            db.session.commit()
            
            db.session.close()
            
            return redirect(url_for('adminnotification.AN_H'))



@adminnotification.route("/Admin-Notifications/trash", methods=['GET', 'POST'])
@login_required
@Check_Token
def AN_T():
    # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            id = request.form.get('id')

            u = update(FISAdmin_Notifications)
            u = u.values({"Type": 'trash', "Status": 'trash',})
            
            u = u.where(FISAdmin_Notifications.id == id)
            
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminnotification.AN_H'))
        
        
      

@adminnotification.route("/Admin-Notifications/delete", methods=['GET', 'POST'])
@login_required
@Check_Token
def AN_D():
    # DELETE RECORD
         
        id = request.form.get('id')
        
        data = FISAdmin_Notifications.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminnotification.AN_H'))

  



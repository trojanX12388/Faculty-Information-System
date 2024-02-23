from flask import Flask, Blueprint, redirect, render_template, request, url_for, flash
from dotenv import load_dotenv
from flask_login import login_required, current_user
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from urllib.request import urlretrieve
from cryptography.fernet import Fernet
import rsa

import requests
import base64

import os
import os.path

load_dotenv()

# DATABASE CONNECTION
from website.models import db
from sqlalchemy import update

# LOADING MODEL CLASSES
from website.models import FISAdmin

# LOADING MODEL PDS_TABLES
from website.models import FISPDS_PersonalDetails, FISPDS_ContactDetails, FISPDS_FamilyBackground, FISPDS_EducationalBackground, FISPDS_Eligibity, FISPDS_WorkExperience, FISPDS_VoluntaryWork, FISPDS_TrainingSeminars, FISPDS_OutstandingAchievements, FISPDS_OfficeShipsMemberships, FISPDS_AgencyMembership, FISPDS_TeacherInformation, FISPDS_AdditionalQuestions, FISPDS_CharacterReference,FISPDS_Signature
   
# LOADING FUNCTION CHECK TOKEN
from website.Token.token_check import Check_Token

adminPDM = Blueprint('adminPDM', __name__)

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

# calculate age in years
from datetime import date
 
def calculateAge(born):
    today = date.today()
    try: 
        birthday = born.replace(year = today.year)
 
    # raised when birth date is February 29
    # and the current year is not a leap year
    except ValueError: 
        birthday = born.replace(year = today.year,
                  month = born.month + 1, day = 1)
 
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year
         
# -------------------------------------------------------------


#                                                    FACULTY PERSONAL DATA MANAGEMENT ROUTE


# ------------------------------- adminPDM BASIC DETAILS ----------------------------  

@adminPDM.route("/adminPDM-Basic-Details", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_BD():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
        

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
           
        
        # UPDATE PROFILE BASIC DETAILS
        
        if request.method == 'POST':

            # UPDATE BASIC DETAILS
            # VALUES
            FacultyCode = request.form.get('faculty_code')
            Honorific = request.form.get('honorific')
            LastName = request.form.get('last_name')
            FirstName = request.form.get('first_name')
            MiddleName = request.form.get('middle_name')
            MiddleInitial = request.form.get('middle_initial')
            NameExtension = request.form.get('name_extension')
            BirthDate = request.form.get('birth_date')
            DateHired = request.form.get('date_hired')
            Remarks = request.form.get('remarks')
            calcBirthDate = {"year": int(BirthDate[:-6]), "month": int(BirthDate[5:-3]), "day": int(BirthDate[8:])}
            
            # Create a date object from the input format
            birth_date_object = date(calcBirthDate["year"], calcBirthDate["month"], calcBirthDate["day"])
            # Calculate age using the calculateAge function
            age = calculateAge(birth_date_object)
            
            u = update(FISAdmin)
            u = u.values({"FacultyCode": FacultyCode,
                          "Honorific": Honorific,
                          "LastName": LastName,
                          "FirstName": FirstName,
                          "MiddleName": MiddleName,
                          "MiddleInitial": MiddleInitial,
                          "NameExtension": NameExtension,
                          "BirthDate": BirthDate,
                          "DateHired": DateHired,
                          "Age": age,
                          "Remarks": Remarks,
                          })
            u = u.where(FISAdmin.AdminId == current_user.AdminId)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_BD')) 
                      
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Basic-Details.html", 
                               User= username.FirstName + " " + username.LastName,
                               adminPDM= "show",
                               user= current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               profile_pic=ProfilePic,
                               activate_BD= "active")


# UPDATE PIC

@adminPDM.route("/adminPDM-Basic-Details-Update-Pic", methods=['POST'])
@login_required
def adminPDM_BDUP():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
        id = username.AdminId
        
        # UPDATE PROFILE PIC
        
        file =  request.form.get('base64')
        ext = request.files.get('fileup')
        ext = ext.filename
        
        # FACULTY FIS PROFILE PIC FOLDER ID
        folder = '1DvP4vzilz3Ozq4SxHphkl2eYcwPdGZw7'
        
        
        url = """{}""".format(file)
                
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
            "mimeType": "image/png"
            })
        
        # GENERATE FILE AND UPLOAD
        file1.SetContentFile(filename)
        file1.Upload()
        
        u = update(FISAdmin)
        u = u.values({"ProfilePic": '%s'%(file1['id'])})
        u = u.where(FISAdmin.AdminId == current_user.AdminId)
        db.session.execute(u)
        db.session.commit()
        db.session.close()
        
        return redirect(url_for('adminPDM.adminPDM_BD')) 
    
    
# CLEAR PIC
    
@adminPDM.route("/adminPDM-Basic-Details-Clear-Pic")
@login_required
def adminPDM_BDCP():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
        id = username.AdminId
        
        # FACULTY FIS PROFILE PIC FOLDER ID
        folder = '1mT1alkWJ-akPnPyB9T7vtumNutwqRK0S'
       
        # CLEAR PROFILE PIC
        file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%(folder)}).GetList()
        try:
            for file1 in file_list:
                if file1['title'] == str(id):
                    file1.Delete()                
        except:
            pass

        # UPDATE USER PROFILE PIC ID
        
        u = update(FISAdmin)
        u = u.values({"ProfilePic": profile_default})
        u = u.where(FISAdmin.AdminId == current_user.AdminId)
        db.session.execute(u)
        db.session.commit()
        db.session.close()
        
        return redirect(url_for('adminPDM.adminPDM_BD')) 


# ------------------------------- END adminPDM BASIC DETAILS ----------------------------  


# ------------------------------- adminPDM PERSONAL DETAILS ----------------------------  

@adminPDM.route("/adminPDM-Personal-Details", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_PD():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 

        # CHECKING IF PROFILE PIC EXIST
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic   
             
        # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.FISPDS_PersonalDetails:
            data = current_user
        else:
            data =  {'FISPDS_PersonalDetails':
                    {'sex':"",
                    'gender':"",
                    'height':"",
                    'weight':"",
                    'religion':"",
                    'civil_status':"",
                    'blood_type':"",
                    'pronoun':"",
                    'country':"",
                    'city':"",
                    'citizenship':"",
                    'dual_citizenship':"",
                    'Remarks':"",
                    }
                    }
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
            sex = request.form.get('sex')
            gender = request.form.get('gender')
            height = request.form.get('height')
            weight = request.form.get('weight')
            religion = request.form.get('religion')
            civil_status = request.form.get('civil_status')
            blood_type = request.form.get('blood_type')
            pronoun = request.form.get('pronoun')
            country = request.form.get('country')
            city = request.form.get('city')
            citizenship = request.form.get('citizenship')
            dual_citizenship = request.form.get('dual_citizenship')
            Remarks = request.form.get('remarks')
           

            if FISPDS_PersonalDetails.query.filter_by(AdminId=current_user.AdminId).first():
                u = update(FISPDS_PersonalDetails)
                u = u.values({"sex": sex,
                            "gender": gender,
                            "height": height,
                            "weight": weight,
                            "religion": religion,
                            "civil_status": civil_status,
                            "blood_type": blood_type,
                            "pronoun": pronoun,
                            "country": country,
                            "city": city,
                            "citizenship": citizenship,
                            "dual_citizenship": dual_citizenship,
                            "Remarks": Remarks,
                            })
                u = u.where(FISPDS_PersonalDetails.AdminId == current_user.AdminId)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                return redirect(url_for('adminPDM.adminPDM_PD'))
            
            else:
                add_record = FISPDS_PersonalDetails(  sex = sex,
                                                    gender = gender,
                                                    height = height,
                                                    weight = weight,
                                                    religion = religion,
                                                    civil_status = civil_status,
                                                    blood_type = blood_type,
                                                    pronoun = pronoun,
                                                    country = country,
                                                    city = city,
                                                    citizenship = citizenship,
                                                    dual_citizenship = dual_citizenship,
                                                    Remarks = Remarks,
                                                    AdminId = current_user.AdminId)
            
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('adminPDM.adminPDM_PD'))
            
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Personal-Details.html", 
                               User=username.FirstName + " " + username.LastName,
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               data = data,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_PD="active")

# ------------------------------- END adminPDM PERSONAL DETAILS ----------------------------  


# ------------------------------- adminPDM CONTACT DETAILS ----------------------------  

@adminPDM.route("/adminPDM-Contact-Details", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_CD():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
       
        # CHECKING IF PROFILE PIC EXIST
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic   
             
        # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.FISPDS_ContactDetails:
            data = current_user
        else:
            data =  {'FISPDS_ContactDetails':
                    {'email':"",
                     'mobile_number':"",
                     'perm_country':"",
                     'perm_region':"",
                     'perm_province':"",
                     'perm_city':"",
                     'perm_address':"",
                     'perm_zip_code':"",
                     'perm_phone_number':"",
                     'res_country':"",
                     'res_region':"",
                     'res_province':"",
                     'res_city':"",
                     'res_address':"",
                     'res_zip_code':"",
                     'res_phone_number':"",
                    'Remarks':"",
                    }
                    }
        
         # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
            email = request.form.get('email')
            mobile_number = request.form.get('mobile_number')
            perm_country = request.form.get('perm_country')
            perm_region = request.form.get('perm_region')
            perm_province = request.form.get('perm_province')
            perm_city = request.form.get('perm_city')
            perm_address = request.form.get('perm_address')
            perm_zip_code = request.form.get('perm_zip_code')
            perm_phone_number = request.form.get('perm_phone_number')
            res_country = request.form.get('res_country')
            res_region = request.form.get('res_region')
            res_province = request.form.get('res_province')
            res_city = request.form.get('res_city')
            res_address = request.form.get('res_address')
            res_zip_code = request.form.get('res_zip_code')
            res_phone_number = request.form.get('res_phone_number')
            Remarks = request.form.get('remarks')

            if FISPDS_ContactDetails.query.filter_by(AdminId=current_user.AdminId).first():
                u = update(FISPDS_ContactDetails)
                u = u.values({"Email": email,
                            "mobile_number": mobile_number,
                            "perm_country": perm_country,
                            "perm_region": perm_region,
                            "perm_province": perm_province,
                            "perm_city": perm_city,
                            "perm_address": perm_address,
                            "perm_zip_code": perm_zip_code,
                            "perm_phone_number": perm_phone_number,
                            "res_country": res_country,
                            "res_region": res_region,
                            "res_province": res_province,
                            "res_city": res_city,
                            "res_address": res_address,
                            "res_zip_code": res_zip_code,
                            "res_phone_number": res_phone_number,
                            "Remarks": Remarks
                            })
                u = u.where(FISPDS_ContactDetails.AdminId == current_user.AdminId)
                db.session.execute(u)
                db.session.commit()
                
                u = update(FISAdmin)
                u = u.values({"Email": email,
                            "MobileNumber": mobile_number,
                            "ResidentialAddress": res_address,
                            })
                u = u.where(FISAdmin.AdminId == current_user.AdminId)
                db.session.execute(u)
                db.session.commit()
                
                db.session.close()
                return redirect(url_for('adminPDM.adminPDM_CD'))
            
            else:
                
                add_record = FISPDS_ContactDetails(  Email = email,
                                                    mobile_number = mobile_number,
                                                    perm_country = perm_country,
                                                    perm_region = perm_region,
                                                    perm_province = perm_province,
                                                    perm_city = perm_city,
                                                    perm_address = perm_address,
                                                    perm_zip_code = perm_zip_code,
                                                    perm_phone_number = perm_phone_number,
                                                    res_country = res_country,
                                                    res_region = res_region,
                                                    res_province = res_province,
                                                    res_city = res_city,
                                                    res_address = res_address,
                                                    res_zip_code = res_zip_code,
                                                    res_phone_number = res_phone_number,
                                                    Remarks = Remarks,
                                                    AdminId = current_user.AdminId)
                db.session.add(add_record)
                db.session.commit()
                
                u = update(FISAdmin)
                u = u.values({"Email": email,
                            "MobileNumber": mobile_number,
                            "ResidentialAddress": res_address,
                            })
                u = u.where(FISAdmin.AdminId == current_user.AdminId)
                db.session.execute(u)
                db.session.commit()
                
                db.session.close()
                return redirect(url_for('adminPDM.adminPDM_CD'))
        
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Contact-Details.html", 
                               User=username.FirstName + " " + username.LastName,
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               data = data,
                               activate_CD="active")
        
        
# ------------------------------- END adminPDM CONTACT DETAILS ----------------------------  


# ------------------------------- adminPDM FAMILY BACKGROUNDS ----------------------------  

@adminPDM.route("/adminPDM-Family-Background", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_FB():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
            
         # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            full_name = request.form.get('full_name')
            relationship = request.form.get('relationship')
            id = request.form.get('id')

            u = update(FISPDS_FamilyBackground)
            u = u.values({"full_name": full_name,
                          "relationship": relationship
                          })
            u = u.where(FISPDS_FamilyBackground.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_FB'))
            
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Family-Background.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_FB="active")
 
@adminPDM.route("/adminPDM-Family-Background/add-record", methods=['GET', 'POST'])
@login_required
def adminPDM_FBadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            full_name = request.form.get('full_name')
            relationship = request.form.get('relationship')
           
            add_record = FISPDS_FamilyBackground(full_name=full_name,relationship=relationship,AdminId = current_user.AdminId)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_FB'))

@adminPDM.route("/adminPDM-Family-Background/delete-record", methods=['GET', 'POST'])
@login_required
def adminPDM_FBdel():

         # DELETE RECORD
         
        # def delete(self, item_id):
        # item = ItemModel.query.get_or_404(item_id)
        # db.session.delete(item)
        # db.session.commit()
        # return {"message": "Item deleted."}

        id = request.form.get('id')
        

        data = FISPDS_FamilyBackground.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_FB'))
 
# ------------------------------- END OF adminPDM FAMILY BACKGROUNDS ---------------------------- 

 
# ------------------------------- adminPDM EDUCATIONAL BACKGROUNDS ------------------------------  

@adminPDM.route("/adminPDM-Educational-Background", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_EB():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
            
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            school_name = request.form.get('school_name')
            level = request.form.get('level')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            id = request.form.get('id')

            u = update(FISPDS_EducationalBackground)
            u = u.values({"school_name": school_name,
                          "level": level,
                          "from_date": from_date,
                          "to_date": to_date
                          })
            
            u = u.where(FISPDS_EducationalBackground.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_EB'))    
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Educational-Background.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_EB="active")


@adminPDM.route("/adminPDM-Educational-Background/add-record", methods=['GET', 'POST'])
@login_required
def adminPDM_EBadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            school_name = request.form.get('school_name')
            level = request.form.get('level')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
           
            add_record = FISPDS_EducationalBackground(school_name=school_name,
                                                    level=level,
                                                    from_date=from_date,
                                                    to_date=to_date,
                                                    AdminId = current_user.AdminId)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_EB'))

@adminPDM.route("/adminPDM-Educational-Background/delete-record", methods=['GET', 'POST'])
@login_required
def adminPDM_EBdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        

        data = FISPDS_EducationalBackground.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_EB'))


# ------------------------------- END OF adminPDM EDUCATIONAL BACKGROUNDS ----------------------------
 
# ------------------------------- adminPDM ELIGIBITIES -----------------------------------------------

@adminPDM.route("/adminPDM-Eligibities", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_E():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
       
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
            
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            eligibity = request.form.get('eligibity')
            rating = request.form.get('rating')
            id = request.form.get('id')

            u = update(FISPDS_Eligibity)
            u = u.values({"eligibity": eligibity,
                          "rating": rating
                          })
            
            u = u.where(FISPDS_Eligibity.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_E'))    
            
            
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Eligibities.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_E="active")

@adminPDM.route("/adminPDM-Eligibities/add-record", methods=['GET', 'POST'])
@login_required
def adminPDM_Eadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            eligibity = request.form.get('eligibity')
            rating = request.form.get('rating')
           
            add_record = FISPDS_Eligibity(eligibity=eligibity,rating=rating,AdminId = current_user.AdminId)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_E'))

@adminPDM.route("/adminPDM-Eligibities/delete-record", methods=['GET', 'POST'])
@login_required
def adminPDM_Edel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = FISPDS_Eligibity.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_E'))
  

# ------------------------------- END OF adminPDM ELIGIBITIES  ---------------------------- 

 
# ------------------------------- adminPDM WORK EXPERIENCE ------------------------------



@adminPDM.route("/adminPDM-Work-Experience", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_WE():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic 
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            position = request.form.get('position')
            company_name = request.form.get('company_name')
            status = request.form.get('status')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            id = request.form.get('id')

            u = update(FISPDS_WorkExperience)
            u = u.values({"position": position,
                          "company_name": company_name,
                          "status": status,
                          "from_date": from_date,
                          "to_date": to_date
                          })
            
            u = u.where(FISPDS_WorkExperience.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_WE'))
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Work-Experience.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_WE="active")
  
@adminPDM.route("/adminPDM-Work-Experience/add-record", methods=['GET', 'POST'])
@login_required
def adminPDM_WEadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            position = request.form.get('position')
            company_name = request.form.get('company_name')
            status = request.form.get('status')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
           
            add_record = FISPDS_WorkExperience(position=position,
                                             company_name=company_name,
                                             status=status,
                                             from_date=from_date,
                                             to_date=to_date,
                                             AdminId = current_user.AdminId)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_WE'))

@adminPDM.route("/adminPDM-Work-Experience/delete-record", methods=['GET', 'POST'])
@login_required
def adminPDM_WEdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = FISPDS_WorkExperience.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_WE'))
    
# ------------------------------- END OF adminPDM WORK EXPERIENCE  ---------------------------- 

 
# ------------------------------- adminPDM VOLUNTARY WORKS ------------------------------
  
@adminPDM.route("/adminPDM-Voluntary-Works", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_VW():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            organization = request.form.get('organization')
            position = request.form.get('position')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            id = request.form.get('id')

            u = update(FISPDS_VoluntaryWork)
            u = u.values({"position": position,
                          "organization": organization,
                          "from_date": from_date,
                          "to_date": to_date
                          })
            
            u = u.where(FISPDS_VoluntaryWork.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_VW'))
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Voluntary-Works.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_VW="active")


@adminPDM.route("/adminPDM-Voluntary-Works/add-record", methods=['GET', 'POST'])
@login_required
def adminPDM_VWadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            organization = request.form.get('organization')
            position = request.form.get('position')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
           
            add_record = FISPDS_VoluntaryWork(organization=organization,
                                            position=position,
                                            from_date=from_date,
                                            to_date=to_date,
                                            AdminId = current_user.AdminId)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_VW'))

@adminPDM.route("/adminPDM-Voluntary-Works/delete-record", methods=['GET', 'POST'])
@login_required
def adminPDM_VWdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = FISPDS_VoluntaryWork.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_VW'))
  
    
# ------------------------------- END OF adminPDM VOLUNTARY WORKS  ---------------------------- 

 
# ------------------------------- adminPDM TRAINING SEMINARS ------------------------------

@adminPDM.route("/adminPDM-Training-Seminars", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_TS():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 

        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            title = request.form.get('title')
            level = request.form.get('level')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            id = request.form.get('id')

            u = update(FISPDS_TrainingSeminars)
            u = u.values({"title": title,
                          "level": level,
                          "from_date": from_date,
                          "to_date": to_date
                          })
            
            u = u.where(FISPDS_TrainingSeminars.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_TS'))
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Training-Seminars.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_TS="active")
        

@adminPDM.route("/adminPDM-Training-Seminars/add-record", methods=['GET', 'POST'])
@login_required
def adminPDM_TSadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            title = request.form.get('title')
            level = request.form.get('level')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
           
            add_record = FISPDS_TrainingSeminars(title=title,
                                                level=level,
                                                from_date=from_date,
                                                to_date=to_date,
                                                AdminId = current_user.AdminId)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_TS'))

@adminPDM.route("/adminPDM-Training-Seminars/delete-record", methods=['GET', 'POST'])
@login_required
def adminPDM_TSdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = FISPDS_TrainingSeminars.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_TS'))
       
  
# ------------------------------- END OF adminPDM TRAINING SEMINARS  ---------------------------- 

 
# ------------------------------- adminPDM OUTSTANDING ACHIEVEMENTS ------------------------------


@adminPDM.route("/adminPDM-Outstanding-Achievements", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_OA():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
       
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
            
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            achievement = request.form.get('achievement')
            level = request.form.get('level')
            from_date = request.form.get('date')
            id = request.form.get('id')

            u = update(FISPDS_OutstandingAchievements)
            u = u.values({"achievement": achievement,
                          "level": level,
                          "date": from_date
                          })
            
            u = u.where(FISPDS_OutstandingAchievements.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_OA'))
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Outstanding-Achievements.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_OA="active")


@adminPDM.route("/adminPDM-Outstanding-Achievements/add-record", methods=['GET', 'POST'])
@login_required
def adminPDM_OAadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            achievement = request.form.get('achievement')
            level = request.form.get('level')
            date = request.form.get('date')
           
            add_record = FISPDS_OutstandingAchievements(achievement=achievement,
                                                    level=level,
                                                    date=date,
                                                    AdminId = current_user.AdminId)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_OA'))

@adminPDM.route("/adminPDM-Outstanding-Achievements/delete-record", methods=['GET', 'POST'])
@login_required
def adminPDM_OAdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = FISPDS_OutstandingAchievements.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_OA'))

# ------------------------------- END OF adminPDM OUTSTANDING ACHIEVEMENTS  ---------------------------- 

 
# ------------------------------- adminPDM OFFICESHIPS MEMBERSHIPS ------------------------------
 
@adminPDM.route("/adminPDM-Officeships-Memberships", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_OSM():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
      
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            organization = request.form.get('organization')
            position = request.form.get('position')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            id = request.form.get('id')

            u = update(FISPDS_OfficeShipsMemberships)
            u = u.values({"position": position,
                          "organization": organization,
                          "from_date": from_date,
                          "to_date": to_date
                          })
            
            u = u.where(FISPDS_OfficeShipsMemberships.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_OSM')) 
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Officeships-Memberships.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_OSM="active")

@adminPDM.route("/adminPDM-Officeships-Memberships/add-record", methods=['GET', 'POST'])
@login_required
def adminPDM_OSMadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            organization = request.form.get('organization')
            position = request.form.get('position')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
           
            add_record = FISPDS_OfficeShipsMemberships(organization=organization,
                                            position=position,
                                            from_date=from_date,
                                            to_date=to_date,
                                            AdminId = current_user.AdminId)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_OSM'))

@adminPDM.route("/adminPDM-Officeships-Memberships/delete-record", methods=['GET', 'POST'])
@login_required
def adminPDM_OSMdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = FISPDS_OfficeShipsMemberships.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_OSM'))
  
    
# ------------------------------- END OF adminPDM OFFICESHIPS MEMBERSHIPS  ---------------------------- 

 
# ------------------------------- adminPDM AGENCY MEMBERSHIP ------------------------------
 
@adminPDM.route("/adminPDM-Agency-Membership", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_AM():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
      
        # CHECKING IF PROFILE PIC EXIST
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic   
        
        # Generate a Fernet key
        key_bytes = os.getenv('Symmetric_Key').encode('utf-8')
        fernet_key = (key_bytes)
        cipher = Fernet(fernet_key)
  
        # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.FISPDS_AgencyMembership:
            data = current_user
            fetch = FISPDS_AgencyMembership.query.filter_by(AdminId=current_user.AdminId).first()
            
            # Decrypt the sensitive data
            GSIShex_bytes = bytes.fromhex(fetch.GSIS[2:])
            PAGIBIGhex_bytes = bytes.fromhex(fetch.PAGIBIG[2:])
            PHILHEALTHhex_bytes = bytes.fromhex(fetch.PAGIBIG[2:])
            SSShex_bytes = bytes.fromhex(fetch.PAGIBIG[2:])
            TINhex_bytes = bytes.fromhex(fetch.PAGIBIG[2:])
        
            # Decrypt the ciphertext
            GSISdecrypted_data = cipher.decrypt(GSIShex_bytes)
            PAGIBIGdecrypted_data = cipher.decrypt(PAGIBIGhex_bytes)
            PHILHEALTHdecrypted_data = cipher.decrypt(PHILHEALTHhex_bytes)
            SSSdecrypted_data = cipher.decrypt(SSShex_bytes)
            TINdecrypted_data = cipher.decrypt(TINhex_bytes)
            
            # Decode the decrypted data to utf-8
            decrypted_GSIS = GSISdecrypted_data.decode('utf-8')
            decrypted_PAGIBIG = PAGIBIGdecrypted_data.decode('utf-8')
            decrypted_PHILHEALTH = PHILHEALTHdecrypted_data.decode('utf-8')
            decrypted_SSS = SSSdecrypted_data.decode('utf-8')
            decrypted_TIN = TINdecrypted_data.decode('utf-8')
            
        else:
            data =  {'FISPDS_AgencyMembership':
                    {
                    'Remarks':""
                    }
                    }
            # Decrypt the sensitive data
            decrypted_GSIS = ""
            decrypted_PAGIBIG = ""
            decrypted_PHILHEALTH = ""
            decrypted_SSS = ""
            decrypted_TIN = ""
        
        # UPDATE 
        
        if request.method == 'POST':
            # Values
            GSIS = request.form.get('GSIS')
            PAGIBIG = request.form.get('PAGIBIG')
            PHILHEALTH = request.form.get('PHILHEALTH')
            SSS = request.form.get('SSS')
            TIN = request.form.get('TIN')
            Remarks = request.form.get('remarks')

            # Encrypt sensitive data
            
            encrypted_GSIS = cipher.encrypt(GSIS.encode('utf-8'))
            encrypted_PAGIBIG = cipher.encrypt(PAGIBIG.encode('utf-8'))
            encrypted_PHILHEALTH = cipher.encrypt(PHILHEALTH.encode('utf-8'))
            encrypted_SSS = cipher.encrypt(SSS.encode('utf-8'))
            encrypted_TIN = cipher.encrypt(TIN.encode('utf-8'))
           
           

            if FISPDS_AgencyMembership.query.filter_by(AdminId=current_user.AdminId).first():
                u = update(FISPDS_AgencyMembership)
                u = u.values({  "GSIS": encrypted_GSIS,
                                "PAGIBIG": encrypted_PAGIBIG,
                                "PHILHEALTH": encrypted_PHILHEALTH,
                                "SSS": encrypted_SSS,
                                "TIN": encrypted_TIN,
                                "Remarks": Remarks,
                            })
                u = u.where(FISPDS_AgencyMembership.AdminId == current_user.AdminId)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                return redirect(url_for('adminPDM.adminPDM_AM'))
            
            else:
                add_record = FISPDS_AgencyMembership( GSIS = encrypted_GSIS,
                                                    PAGIBIG = encrypted_PAGIBIG,
                                                    PHILHEALTH = encrypted_PHILHEALTH,
                                                    SSS = encrypted_SSS,
                                                    TIN = encrypted_TIN,
                                                    Remarks = Remarks,
                                                    AdminId = current_user.AdminId)
            
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('adminPDM.adminPDM_AM'))
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Agency-Membership.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               data = data,
                               decrypted_GSIS = decrypted_GSIS,
                               decrypted_PAGIBIG = decrypted_PAGIBIG,
                               decrypted_PHILHEALTH = decrypted_PHILHEALTH,
                               decrypted_SSS = decrypted_SSS,
                               decrypted_TIN = decrypted_TIN,
                               activate_AM="active")  

# ------------------------------- END OF adminPDM AGENCY MEMBERSHIP  ---------------------------- 
 
# ------------------------------- adminPDM TEACHER INFORMATION ------------------------------

@adminPDM.route("/adminPDM-Teacher-Information", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_TI():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
      
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            information = request.form.get('information')
            type = request.form.get('type')
            id = request.form.get('id')

            u = update(FISPDS_TeacherInformation)
            u = u.values({"information": information,
                          "type": type
                          })
            
            u = u.where(FISPDS_TeacherInformation.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_TI'))
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Teacher-Information.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_TI="active")  

@adminPDM.route("/adminPDM-Teacher-Information/add-record", methods=['GET', 'POST'])
@login_required
def adminPDM_TIadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            information = request.form.get('information')
            type = request.form.get('type')
           
            add_record = FISPDS_TeacherInformation(information=information,
                                                type=type,
                                                AdminId = current_user.AdminId)
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_TI'))

@adminPDM.route("/adminPDM-Teacher-Information/delete-record", methods=['GET', 'POST'])
@login_required
def adminPDM_TIdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = FISPDS_TeacherInformation.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_TI'))

# ------------------------------- END OF adminPDM TEACHER INFORMATION  ---------------------------- 
 
# ------------------------------- adminPDM CHARACTER REFERENCE ------------------------------

@adminPDM.route("/adminPDM-Character-Reference", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_CR():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
      
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            full_name = request.form.get('full_name')
            id = request.form.get('id')

            u = update(FISPDS_CharacterReference)
            u = u.values({"full_name": full_name})
            
            u = u.where(FISPDS_CharacterReference.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_CR')) 
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Character-Reference.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_CR="active")

@adminPDM.route("/adminPDM-Character-Reference/add-record", methods=['GET', 'POST'])
@login_required
def adminPDM_CRadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
            full_name = request.form.get('full_name')

            add_record = FISPDS_CharacterReference(full_name=full_name,
                                                AdminId = current_user.AdminId)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_CR'))

@adminPDM.route("/adminPDM-Character-Reference/delete-record", methods=['GET', 'POST'])
@login_required
def adminPDM_CRdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = FISPDS_CharacterReference.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('adminPDM.adminPDM_CR'))

# ------------------------------- END OF adminPDM CHARACTER REFERENCE  ---------------------------- 
 
# ------------------------------- adminPDM SIGNATURE ------------------------------

@adminPDM.route("/adminPDM-Signature", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_S():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
        id = username.AdminId
        
        # CHECKING IF PROFILE PIC EXIST
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic   
        
         # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.FISPDS_Signature:
            data = current_user
            
            # FETCHING USER ENCRYPTED SIGNATURE DATA
            fetch = FISPDS_Signature.query.filter_by(AdminId=current_user.AdminId).first()
            
            # FETCHING USER ENCRYPTED SIGNATURE DATA
            wet_signature = fetch.wet_signature
            
            if fetch.dict_certificate:
                dict_cert = fetch.dict_certificate
            else:
                dict_cert = "1bQcZE3rlJWhNXkMy7yjdWLNTxaKSDArL"
        else:
            # FETCHING DEFAULT BLANK IMAGE
            wet_signature = "1JIS5J0SPU_V5aOPAHACBxZ5hjhkHFfY4"
            dict_cert = "1bQcZE3rlJWhNXkMy7yjdWLNTxaKSDArL"
            
        # FETCHING STRING DATA FROM CLOUD    
        
        # FACULTY FIS WET SIGNATURE FOLDER ID
        folder = '1oLWdZCvLVTbhRc5XcXBqlw5H5wkqnBLu'
        file7 = drive.CreateFile(metadata={"parents": [{"id": folder}],'id': ''+ str(wet_signature)})
        
        signature_StringData = file7.GetContentString(''+ str(wet_signature))
        
        # DECRYPTING DATA TO CONVERT INTO IMAGE
        decrypted_signature = fernet.decrypt(signature_StringData[2:-1])
        
         # FACULTY FIS DICT CERTIFICATE FOLDER ID
        folder1 = '1KrXqzGYLm9ET4D6bPLwrP_QJGtCufkly'
        file7 = drive.CreateFile(metadata={"parents": [{"id": folder1}],'id': ''+ str(dict_cert)})
        
        dict_cert_StringData = file7.GetContentString(''+ str(dict_cert))
        
        # DECRYPTING DATA TO CONVERT INTO IMAGE
        decrypted_dict_cert = fernet.decrypt(dict_cert_StringData[2:-1])
        
        # UPDATE 
        
        if request.method == 'POST':
            file =  request.form.get('base64')
            
            # API BACKGROUND REMOVER 
            api_key = os.getenv('BGR_api_key')
            
            # Convert the base64 string to bytes
            image_data = base64.b64decode(file[22:])

            response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': image_data},
            data={'size': 'auto'},
            headers={'X-Api-Key': api_key}
            )

            base64_data = base64.b64encode(response.content)
            
            # ENCRYPTING IMAGE DATA
            encrypted = fernet.encrypt(base64_data)
            
            data = """{}""".format(encrypted)
 
            if FISPDS_Signature.query.filter_by(AdminId=current_user.AdminId).first():
                
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
                    "mimeType": "text/plain"
                    })
                
                # GENERATE FILE AND UPLOAD
                file1.SetContentString(data)
                file1.Upload()
                
                u = update(FISPDS_Signature)
                u = u.values({"wet_signature": '%s'%(file1['id'])})
                u = u.where(FISPDS_Signature.AdminId == current_user.AdminId)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                
                return redirect(url_for('adminPDM.adminPDM_S')) 
            
            else:
                # CONFIGURE FILE FORMAT AND NAME
                file1 = drive.CreateFile(metadata={
                    "title": ""+ str(id),
                    "parents": [{"id": folder}],
                    "mimeType": "text/plain"
                    })
                
                # GENERATE FILE AND UPLOAD
                file1.SetContentString(data)
                file1.Upload()
                
                add_record = FISPDS_Signature( wet_signature = '%s'%(file1['id']),
                                            AdminId = current_user.AdminId)
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('adminPDM.adminPDM_S'))
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Signature.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               signature = "data:image/png;base64," + decrypted_signature.decode('utf-8'),
                               dict_cert = decrypted_dict_cert.decode('utf-8'),
                               activate_Sig="active")
        
@adminPDM.route("/adminPDM-Signature/Submit_DICT", methods=['GET', 'POST'])
@login_required
def adminPDM_SS():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
        id = username.AdminId

        # FACULTY FIS DICT CERTIFICATE FOLDER ID
        folder = '1KrXqzGYLm9ET4D6bPLwrP_QJGtCufkly'
        
        # UPDATE 
        
        if request.method == 'POST':
            file =  request.form.get('base64_dict')
            
            # ENCRYPTING IMAGE DATA
            encrypted = fernet.encrypt(file.encode('utf-8'))
            
            data = """{}""".format(encrypted)
 
            if FISPDS_Signature.query.filter_by(AdminId=current_user.AdminId).first():
                
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
                    "mimeType": "text/plain"
                    })
                
                # GENERATE FILE AND UPLOAD
                file1.SetContentString(data)
                file1.Upload()
                
                u = update(FISPDS_Signature)
                u = u.values({"dict_certificate": '%s'%(file1['id'])})
                u = u.where(FISPDS_Signature.AdminId == current_user.AdminId)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                
                return redirect(url_for('adminPDM.adminPDM_S')) 
            
            else:
                # CONFIGURE FILE FORMAT AND NAME
                file1 = drive.CreateFile(metadata={
                    "title": ""+ str(id),
                    "parents": [{"id": folder}],
                    "mimeType": "text/plain"
                    })
                
                # GENERATE FILE AND UPLOAD
                file1.SetContentString(data)
                file1.Upload()
                
                add_record = FISPDS_Signature( dict_certificate = '%s'%(file1['id']),
                                            AdminId = current_user.AdminId)
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('adminPDM.adminPDM_S'))

# ------------------------------- END OF adminPDM SIGNATURE  ---------------------------- 
 
# ------------------------------- adminPDM ADDITIONAL QUESTIONS ------------------------------
  
@adminPDM.route("/adminPDM-Additional-Questions", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_AQ():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
       
        # CHECKING IF PROFILE PIC EXIST
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic   
             
        # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.FISPDS_AdditionalQuestions:
            data = current_user
        else:
            data =  {'FISPDS_AdditionalQuestions':
                    {'q1_a':"",
                    'q1_a_details':"",
                    
                    'q1_b':"",
                    'q1_b_details':"",
                    
                    'q2_a':"",
                    'q2_a_details':"",
                    
                    'q2_b':"",
                    'q2_b_details':"",
                    
                    'q3':"",
                    'q3_details':"",
                    
                    'q4':"",
                    'q4_details':"",
                    
                    'q5_a':"",
                    'q5_a_details':"",
                    
                    'q5_b':"",
                    'q5_b_details':"",
                    
                    'q6':"",
                    'q6_details':"",
                    
                    'q7_a':"",
                    'q7_a_details':"",
                    
                    'q7_b':"",
                    'q7_b_details':"",
                    
                    'q7_c':"",
                    'q7_c_details':""
                    }
                    }
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
            q1_a = request.form.get('q1_a')
            q1_a_details = request.form.get('q1_a_details')
            
            q1_b = request.form.get('q1_b')
            q1_b_details = request.form.get('q1_b_details')
            
            q2_a = request.form.get('q2_a')
            q2_a_details = request.form.get('q2_a_details')
            
            q2_b = request.form.get('q2_b')
            q2_b_details = request.form.get('q2_b_details')
            
            q3 = request.form.get('q3')
            q3_details = request.form.get('q3_details')
            
            q4 = request.form.get('q4')
            q4_details = request.form.get('q4_details')
            
            q5_a = request.form.get('q5_a')
            q5_a_details = request.form.get('q5_a_details')
            
            q5_b = request.form.get('q5_b')
            q5_b_details = request.form.get('q5_b_details')
            
            q6 = request.form.get('q6')
            q6_details = request.form.get('q6_details')
            
            q7_a = request.form.get('q7_a')
            q7_a_details = request.form.get('q7_a_details')
            
            q7_b = request.form.get('q7_b')
            q7_b_details = request.form.get('q7_b_details')
            
            q7_c = request.form.get('q7_c')
            q7_c_details = request.form.get('q7_c_details')
           

            if FISPDS_AdditionalQuestions.query.filter_by(AdminId=current_user.AdminId).first():
                u = update(FISPDS_AdditionalQuestions)
                u = u.values({
                            "q1_a": q1_a,
                            "q1_a_details": q1_a_details,
                            
                            "q1_b": q1_b,
                            "q1_b_details": q1_b_details,
                            
                            "q2_a": q2_a,
                            "q2_a_details": q2_a_details,
                            
                            "q2_b": q2_b,
                            "q2_b_details": q2_b_details,
                            
                            "q3": q3,
                            "q3_details": q3_details,
                            
                            "q4": q4,
                            "q4_details": q4_details,
                            
                            "q5_a": q5_a,
                            "q5_a_details": q5_a_details,
                            
                            "q5_b": q5_b,
                            "q5_b_details": q5_b_details,
                            
                            "q6": q6,
                            "q6_details": q6_details,
                            
                            "q7_a": q7_a,
                            "q7_a_details": q7_a_details,
                            
                            "q7_b": q7_b,
                            "q7_b_details": q7_b_details,
                            
                            "q7_c": q7_c,
                            "q7_c_details": q7_c_details
                            })
                u = u.where(FISPDS_AdditionalQuestions.AdminId == current_user.AdminId)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                return redirect(url_for('adminPDM.adminPDM_AQ'))
            
            else:
                add_record = FISPDS_AdditionalQuestions(  
                                                    q1_a = q1_a,
                                                    q1_a_details= q1_a_details,
                                                    
                                                    q1_b = q1_b,
                                                    q1_b_details = q1_b_details,
                                                    
                                                    q2_a = q2_a,
                                                    q2_a_details = q2_a_details,
                                                    
                                                    q2_b = q2_b,
                                                    q2_b_details = q2_b_details,
                                                    
                                                    q3 = q3,
                                                    q3_details = q3_details,
                                                    
                                                    q4 = q4,
                                                    q4_details = q4_details,
                                                    
                                                    q5_a = q5_a,
                                                    q5_a_details = q5_a_details,
                                                    
                                                    q5_b = q5_b,
                                                    q5_b_details = q5_b_details,
                                                    
                                                    q6 = q6,
                                                    q6_details = q6_details,
                                                    
                                                    q7_a = q7_a,
                                                    q7_a_details = q7_a_details,
                                                    
                                                    q7_b = q7_b,
                                                    q7_b_details = q7_b_details,
                                                    
                                                    q7_c = q7_c,
                                                    q7_c_details= q7_c_details,
                                                    AdminId = current_user.AdminId)
            
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('adminPDM.adminPDM_AQ'))
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Additional-Questions.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               data = data,
                               activate_AQ="active")
  
# ------------------------------- END OF adminPDM ADDITIONAL QUESTIONS  ---------------------------- 
 
# ------------------------------- adminPDM PERSONAL DATA REPORTS ------------------------------
   
  
@adminPDM.route("/adminPDM-Personal-Data-Reports")
@login_required
@Check_Token
def adminPDM_PDR():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
      
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/adminPDM-Personal-Data-Reports.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               adminPDM="show",
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               activate_PDR="active")
    
# ------------------------------- END OF adminPDM PERSONAL DATA REPORTS  ---------------------------- 
 
# ------------------------------------------------------------- 



# ------------------------------- SETTINGS ------------------------------

@adminPDM.route("/Admin-Settings", methods=['GET', 'POST'])
@login_required
@Check_Token
def adminPDM_Settings():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
    
        username = FISAdmin.query.filter_by(AdminId=current_user.AdminId).first() 
      
        if username.ProfilePic == None:
            ProfilePic=profile_default
        else:
            ProfilePic=username.ProfilePic
        
        # UPDATE 
        
        if request.method == 'POST':
            from werkzeug.security import generate_password_hash
            from werkzeug.security import check_password_hash
         
            # VALUES
           
            password = request.form.get('password')
            newpassword = request.form.get('newpassword')
            renewpassword = request.form.get('renewpassword')
            
            if check_password_hash(current_user.Password, password):

                if newpassword == renewpassword:
                    Password=generate_password_hash(newpassword)
                    
                    u = update(FISAdmin)
                    u = u.values({"Password": Password})
                    
                    u = u.where(FISAdmin.AdminId == current_user.AdminId)
                    db.session.execute(u)
                    db.session.commit()
                    db.session.close()
                    
                    flash('Password successfully updated!', category='success')
                    return redirect(url_for('adminPDM.adminPDM_Settings'))
                 
                else:
                    flash('Invalid input! Password does not match...', category='error')
                    return redirect(url_for('adminPDM.adminPDM_Settings')) 
            else:
                flash('Invalid input! Password does not match...', category='error')
                return redirect(url_for('adminPDM.adminPDM_Settings')) 
                                
        return render_template("Admin-Home-Page/Personal-Data-Management-Page/Settings.html", 
                               User=username.FirstName + " " + username.LastName, 
                               profile_pic=ProfilePic,
                               user = current_user,
                               age = str(calculateAge(date(current_user.BirthDate.year, current_user.BirthDate.month, current_user.BirthDate.day))),
                               )
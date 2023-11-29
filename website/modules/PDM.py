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

# LOADING MODEL PDS_TABLES
from website.models import PDS_Personal_Details, PDS_Contact_Details, PDS_Family_Background, PDS_Educational_Background, PDS_Eligibity, PDS_Work_Experience, PDS_Voluntary_Work, PDS_Training_Seminars, PDS_Outstanding_Achievements, PDS_OfficeShips_Memberships, PDS_Agency_Membership, PDS_Teacher_Information, PDS_Additional_Questions, PDS_Character_Reference,PDS_Signature
   

PDM = Blueprint('PDM', __name__)

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




#                                                    FACULTY PERSONAL DATA MANAGEMENT ROUTE


# ------------------------------- PDM BASIC DETAILS ----------------------------  

@PDM.route("/PDM-Basic-Details", methods=['GET', 'POST'])
@login_required
def PDM_BD():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
        

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
           
        
        # UPDATE PROFILE BASIC DETAILS
        
        if request.method == 'POST':

            # UPDATE BASIC DETAILS
            # VALUES
            faculty_code = request.form.get('faculty_code')
            honorific = request.form.get('honorific')
            last_name = request.form.get('last_name')
            first_name = request.form.get('first_name')
            middle_name = request.form.get('middle_name')
            middle_initial = request.form.get('middle_initial')
            name_extension = request.form.get('name_extension')
            birth_date = request.form.get('birth_date')
            date_hired = request.form.get('date_hired')
            remarks = request.form.get('remarks')
            name = first_name + " " + last_name

            u = update(Faculty_Profile)
            u = u.values({"faculty_code": faculty_code,
                          "honorific": honorific,
                          "last_name": last_name,
                          "first_name": first_name,
                          "middle_name": middle_name,
                          "middle_initial": middle_initial,
                          "name_extension": name_extension,
                          "birth_date": birth_date,
                          "date_hired": date_hired,
                          "remarks": remarks,
                          "name": name
                          })
            u = u.where(Faculty_Profile.faculty_account_id == current_user.faculty_account_id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_BD')) 
                      
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Basic-Details.html", 
                               User= username.first_name + " " + username.last_name,
                               PDM= "show",
                               faculty_code= username.faculty_code,
                               first_name= username.first_name,
                               last_name= username.last_name,
                               middle_name= username.middle_name,
                               middle_initial= username.middle_initial,
                               name_extension= username.name_extension,
                               birth_date= username.birth_date,
                               date_hired= username.date_hired,
                               remarks= username.remarks,
                               honorific= username.honorific,
                               user= current_user,
                               profile_pic=profile_pic,
                               activate_BD= "active")


# UPDATE PIC

@PDM.route("/PDM-Basic-Details-Update-Pic", methods=['POST'])
@login_required
def PDM_BDUP():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
        id = username.faculty_account_id
        
        # UPDATE PROFILE PIC
        
        file =  request.form.get('base64')
        ext = request.files.get('fileup')
        ext = ext.filename
        
        # FACULTY FIS PROFILE PIC FOLDER ID
        folder = '1mT1alkWJ-akPnPyB9T7vtumNutwqRK0S'
        
        
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
        
        u = update(Faculty_Profile)
        u = u.values({"profile_pic": '%s'%(file1['id'])})
        u = u.where(Faculty_Profile.faculty_account_id == current_user.faculty_account_id)
        db.session.execute(u)
        db.session.commit()
        db.session.close()
        
        return redirect(url_for('PDM.PDM_BD')) 
    
    
# CLEAR PIC
    
@PDM.route("/PDM-Basic-Details-Clear-Pic")
@login_required
def PDM_BDCP():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
        id = username.faculty_account_id
        
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
        
        u = update(Faculty_Profile)
        u = u.values({"profile_pic": profile_default})
        u = u.where(Faculty_Profile.faculty_account_id == current_user.faculty_account_id)
        db.session.execute(u)
        db.session.commit()
        db.session.close()
        
        return redirect(url_for('PDM.PDM_BD')) 


# ------------------------------- END PDM BASIC DETAILS ----------------------------  


# ------------------------------- PDM PERSONAL DETAILS ----------------------------  

@PDM.route("/PDM-Personal-Details", methods=['GET', 'POST'])
@login_required
def PDM_PD():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 

        # CHECKING IF PROFILE PIC EXIST
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic   
             
        # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.PDS_Personal_Details:
            data = current_user
        else:
            data =  {'PDS_Personal_Details':
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
                    'remarks':"",
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
            remarks = request.form.get('remarks')
           

            if PDS_Personal_Details.query.filter_by(faculty_account_id=current_user.faculty_account_id).first():
                u = update(PDS_Personal_Details)
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
                            "remarks": remarks,
                            })
                u = u.where(PDS_Personal_Details.faculty_account_id == current_user.faculty_account_id)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                return redirect(url_for('PDM.PDM_PD'))
            
            else:
                add_record = PDS_Personal_Details(  sex = sex,
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
                                                    remarks = remarks,
                                                    faculty_account_id = current_user.faculty_account_id)
            
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('PDM.PDM_PD'))
            
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Personal-Details.html", 
                               User=username.first_name + " " + username.last_name,
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               data = data,
                               activate_PD="active")

# ------------------------------- END PDM PERSONAL DETAILS ----------------------------  


# ------------------------------- PDM CONTACT DETAILS ----------------------------  

@PDM.route("/PDM-Contact-Details", methods=['GET', 'POST'])
@login_required
def PDM_CD():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
       
        # CHECKING IF PROFILE PIC EXIST
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic   
             
        # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.PDS_Contact_Details:
            data = current_user
        else:
            data =  {'PDS_Contact_Details':
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
                    'remarks':"",
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
            remarks = request.form.get('remarks')

            if PDS_Contact_Details.query.filter_by(faculty_account_id=current_user.faculty_account_id).first():
                u = update(PDS_Contact_Details)
                u = u.values({"email": email,
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
                            "remarks": remarks
                            })
                u = u.where(PDS_Contact_Details.faculty_account_id == current_user.faculty_account_id)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                return redirect(url_for('PDM.PDM_CD'))
            
            else:
                
                add_record = PDS_Contact_Details(  email = email,
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
                                                    remarks = remarks,
                                                    faculty_account_id = current_user.faculty_account_id)
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('PDM.PDM_CD'))
        
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Contact-Details.html", 
                               User=username.first_name + " " + username.last_name,
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               data = data,
                               activate_CD="active")
        
        
# ------------------------------- END PDM CONTACT DETAILS ----------------------------  


# ------------------------------- PDM FAMILY BACKGROUNDS ----------------------------  

@PDM.route("/PDM-Family-Background", methods=['GET', 'POST'])
@login_required
def PDM_FB():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
            
         # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            full_name = request.form.get('full_name')
            relationship = request.form.get('relationship')
            id = request.form.get('id')

            u = update(PDS_Family_Background)
            u = u.values({"full_name": full_name,
                          "relationship": relationship
                          })
            u = u.where(PDS_Family_Background.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_FB'))
            
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Family-Background.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_FB="active")
 
@PDM.route("/PDM-Family-Background/add-record", methods=['GET', 'POST'])
@login_required
def PDM_FBadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            full_name = request.form.get('full_name')
            relationship = request.form.get('relationship')
           
            add_record = PDS_Family_Background(full_name=full_name,relationship=relationship,faculty_account_id = current_user.faculty_account_id)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_FB'))

@PDM.route("/PDM-Family-Background/delete-record", methods=['GET', 'POST'])
@login_required
def PDM_FBdel():

         # DELETE RECORD
         
        # def delete(self, item_id):
        # item = ItemModel.query.get_or_404(item_id)
        # db.session.delete(item)
        # db.session.commit()
        # return {"message": "Item deleted."}

        id = request.form.get('id')
        

        data = PDS_Family_Background.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_FB'))
 
# ------------------------------- END OF PDM FAMILY BACKGROUNDS ---------------------------- 

 
# ------------------------------- PDM EDUCATIONAL BACKGROUNDS ------------------------------  

@PDM.route("/PDM-Educational-Background", methods=['GET', 'POST'])
@login_required
def PDM_EB():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
            
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            school_name = request.form.get('school_name')
            level = request.form.get('level')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            id = request.form.get('id')

            u = update(PDS_Educational_Background)
            u = u.values({"school_name": school_name,
                          "level": level,
                          "from_date": from_date,
                          "to_date": to_date
                          })
            
            u = u.where(PDS_Educational_Background.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_EB'))    
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Educational-Background.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_EB="active")


@PDM.route("/PDM-Educational-Background/add-record", methods=['GET', 'POST'])
@login_required
def PDM_EBadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            school_name = request.form.get('school_name')
            level = request.form.get('level')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
           
            add_record = PDS_Educational_Background(school_name=school_name,
                                                    level=level,
                                                    from_date=from_date,
                                                    to_date=to_date,
                                                    faculty_account_id = current_user.faculty_account_id)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_EB'))

@PDM.route("/PDM-Educational-Background/delete-record", methods=['GET', 'POST'])
@login_required
def PDM_EBdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        

        data = PDS_Educational_Background.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_EB'))


# ------------------------------- END OF PDM EDUCATIONAL BACKGROUNDS ----------------------------
 
# ------------------------------- PDM ELIGIBITIES -----------------------------------------------

@PDM.route("/PDM-Eligibities", methods=['GET', 'POST'])
@login_required
def PDM_E():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
       
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
            
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            eligibity = request.form.get('eligibity')
            rating = request.form.get('rating')
            id = request.form.get('id')

            u = update(PDS_Eligibity)
            u = u.values({"eligibity": eligibity,
                          "rating": rating
                          })
            
            u = u.where(PDS_Eligibity.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_E'))    
            
            
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Eligibities.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_E="active")

@PDM.route("/PDM-Eligibities/add-record", methods=['GET', 'POST'])
@login_required
def PDM_Eadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            eligibity = request.form.get('eligibity')
            rating = request.form.get('rating')
           
            add_record = PDS_Eligibity(eligibity=eligibity,rating=rating,faculty_account_id = current_user.faculty_account_id)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_E'))

@PDM.route("/PDM-Eligibities/delete-record", methods=['GET', 'POST'])
@login_required
def PDM_Edel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = PDS_Eligibity.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_E'))
  

# ------------------------------- END OF PDM ELIGIBITIES  ---------------------------- 

 
# ------------------------------- PDM WORK EXPERIENCE ------------------------------



@PDM.route("/PDM-Work-Experience", methods=['GET', 'POST'])
@login_required
def PDM_WE():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic 
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            position = request.form.get('position')
            company_name = request.form.get('company_name')
            status = request.form.get('status')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            id = request.form.get('id')

            u = update(PDS_Work_Experience)
            u = u.values({"position": position,
                          "company_name": company_name,
                          "status": status,
                          "from_date": from_date,
                          "to_date": to_date
                          })
            
            u = u.where(PDS_Work_Experience.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_WE'))
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Work-Experience.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_WE="active")
  
@PDM.route("/PDM-Work-Experience/add-record", methods=['GET', 'POST'])
@login_required
def PDM_WEadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            position = request.form.get('position')
            company_name = request.form.get('company_name')
            status = request.form.get('status')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
           
            add_record = PDS_Work_Experience(position=position,
                                             company_name=company_name,
                                             status=status,
                                             from_date=from_date,
                                             to_date=to_date,
                                             faculty_account_id = current_user.faculty_account_id)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_WE'))

@PDM.route("/PDM-Work-Experience/delete-record", methods=['GET', 'POST'])
@login_required
def PDM_WEdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = PDS_Work_Experience.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_WE'))
    
# ------------------------------- END OF PDM WORK EXPERIENCE  ---------------------------- 

 
# ------------------------------- PDM VOLUNTARY WORKS ------------------------------
  
@PDM.route("/PDM-Voluntary-Works", methods=['GET', 'POST'])
@login_required
def PDM_VW():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            organization = request.form.get('organization')
            position = request.form.get('position')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            id = request.form.get('id')

            u = update(PDS_Voluntary_Work)
            u = u.values({"position": position,
                          "organization": organization,
                          "from_date": from_date,
                          "to_date": to_date
                          })
            
            u = u.where(PDS_Voluntary_Work.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_VW'))
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Voluntary-Works.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_VW="active")


@PDM.route("/PDM-Voluntary-Works/add-record", methods=['GET', 'POST'])
@login_required
def PDM_VWadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            organization = request.form.get('organization')
            position = request.form.get('position')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
           
            add_record = PDS_Voluntary_Work(organization=organization,
                                            position=position,
                                            from_date=from_date,
                                            to_date=to_date,
                                            faculty_account_id = current_user.faculty_account_id)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_VW'))

@PDM.route("/PDM-Voluntary-Works/delete-record", methods=['GET', 'POST'])
@login_required
def PDM_VWdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = PDS_Voluntary_Work.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_VW'))
  
    
# ------------------------------- END OF PDM VOLUNTARY WORKS  ---------------------------- 

 
# ------------------------------- PDM TRAINING SEMINARS ------------------------------

@PDM.route("/PDM-Training-Seminars", methods=['GET', 'POST'])
@login_required
def PDM_TS():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            title = request.form.get('title')
            level = request.form.get('level')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            id = request.form.get('id')

            u = update(PDS_Training_Seminars)
            u = u.values({"title": title,
                          "level": level,
                          "from_date": from_date,
                          "to_date": to_date
                          })
            
            u = u.where(PDS_Training_Seminars.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_TS'))
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Training-Seminars.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_TS="active")
        

@PDM.route("/PDM-Training-Seminars/add-record", methods=['GET', 'POST'])
@login_required
def PDM_TSadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            title = request.form.get('title')
            level = request.form.get('level')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
           
            add_record = PDS_Training_Seminars(title=title,
                                                level=level,
                                                from_date=from_date,
                                                to_date=to_date,
                                                faculty_account_id = current_user.faculty_account_id)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_TS'))

@PDM.route("/PDM-Training-Seminars/delete-record", methods=['GET', 'POST'])
@login_required
def PDM_TSdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = PDS_Training_Seminars.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_TS'))
       
  
# ------------------------------- END OF PDM TRAINING SEMINARS  ---------------------------- 

 
# ------------------------------- PDM OUTSTANDING ACHIEVEMENTS ------------------------------


@PDM.route("/PDM-Outstanding-Achievements", methods=['GET', 'POST'])
@login_required
def PDM_OA():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
       
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
            
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            achievement = request.form.get('achievement')
            level = request.form.get('level')
            date = request.form.get('date')
            id = request.form.get('id')

            u = update(PDS_Outstanding_Achievements)
            u = u.values({"achievement": achievement,
                          "level": level,
                          "date": date
                          })
            
            u = u.where(PDS_Outstanding_Achievements.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_OA'))
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Outstanding-Achievements.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_OA="active")


@PDM.route("/PDM-Outstanding-Achievements/add-record", methods=['GET', 'POST'])
@login_required
def PDM_OAadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            achievement = request.form.get('achievement')
            level = request.form.get('level')
            date = request.form.get('date')
           
            add_record = PDS_Outstanding_Achievements(achievement=achievement,
                                                    level=level,
                                                    date=date,
                                                    faculty_account_id = current_user.faculty_account_id)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_OA'))

@PDM.route("/PDM-Outstanding-Achievements/delete-record", methods=['GET', 'POST'])
@login_required
def PDM_OAdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = PDS_Outstanding_Achievements.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_OA'))

# ------------------------------- END OF PDM OUTSTANDING ACHIEVEMENTS  ---------------------------- 

 
# ------------------------------- PDM OFFICESHIPS MEMBERSHIPS ------------------------------
 
@PDM.route("/PDM-Officeships-Memberships", methods=['GET', 'POST'])
@login_required
def PDM_OSM():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
      
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            organization = request.form.get('organization')
            position = request.form.get('position')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            id = request.form.get('id')

            u = update(PDS_OfficeShips_Memberships)
            u = u.values({"position": position,
                          "organization": organization,
                          "from_date": from_date,
                          "to_date": to_date
                          })
            
            u = u.where(PDS_OfficeShips_Memberships.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_OSM')) 
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Officeships-Memberships.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_OSM="active")

@PDM.route("/PDM-Officeships-Memberships/add-record", methods=['GET', 'POST'])
@login_required
def PDM_OSMadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            organization = request.form.get('organization')
            position = request.form.get('position')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
           
            add_record = PDS_OfficeShips_Memberships(organization=organization,
                                            position=position,
                                            from_date=from_date,
                                            to_date=to_date,
                                            faculty_account_id = current_user.faculty_account_id)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_OSM'))

@PDM.route("/PDM-Officeships-Memberships/delete-record", methods=['GET', 'POST'])
@login_required
def PDM_OSMdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = PDS_OfficeShips_Memberships.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_OSM'))
  
    
# ------------------------------- END OF PDM OFFICESHIPS MEMBERSHIPS  ---------------------------- 

 
# ------------------------------- PDM AGENCY MEMBERSHIP ------------------------------
 
@PDM.route("/PDM-Agency-Membership", methods=['GET', 'POST'])
@login_required
def PDM_AM():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
      
        # CHECKING IF PROFILE PIC EXIST
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic   
             
        # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.PDS_Agency_Membership:
            data = current_user
        else:
            data =  {'PDS_Agency_Membership':
                    {'GSIS':"",
                    'PAGIBIG':"",
                    'PHILHEALTH':"",
                    'SSS':"",
                    'TIN':"",
                    'remarks':""
                    }
                    }
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
            GSIS = request.form.get('GSIS')
            PAGIBIG = request.form.get('PAGIBIG')
            PHILHEALTH = request.form.get('PHILHEALTH')
            SSS = request.form.get('SSS')
            TIN = request.form.get('TIN')
            remarks = request.form.get('remarks')
           

            if PDS_Agency_Membership.query.filter_by(faculty_account_id=current_user.faculty_account_id).first():
                u = update(PDS_Agency_Membership)
                u = u.values({  "GSIS": GSIS,
                                "PAGIBIG": PAGIBIG,
                                "PHILHEALTH": PHILHEALTH,
                                "SSS": SSS,
                                "TIN": TIN,
                                "remarks": remarks,
                            })
                u = u.where(PDS_Agency_Membership.faculty_account_id == current_user.faculty_account_id)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                return redirect(url_for('PDM.PDM_AM'))
            
            else:
                add_record = PDS_Agency_Membership( GSIS = GSIS,
                                                    PAGIBIG = PAGIBIG,
                                                    PHILHEALTH = PHILHEALTH,
                                                    SSS = SSS,
                                                    TIN = TIN,
                                                    remarks = remarks,
                                                    faculty_account_id = current_user.faculty_account_id)
            
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('PDM.PDM_AM'))
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Agency-Membership.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               data = data,
                               activate_AM="active")  

# ------------------------------- END OF PDM AGENCY MEMBERSHIP  ---------------------------- 
 
# ------------------------------- PDM TEACHER INFORMATION ------------------------------

@PDM.route("/PDM-Teacher-Information", methods=['GET', 'POST'])
@login_required
def PDM_TI():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
      
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            information = request.form.get('information')
            type = request.form.get('type')
            id = request.form.get('id')

            u = update(PDS_Teacher_Information)
            u = u.values({"information": information,
                          "type": type
                          })
            
            u = u.where(PDS_Teacher_Information.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_TI'))
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Teacher-Information.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_TI="active")  

@PDM.route("/PDM-Teacher-Information/add-record", methods=['GET', 'POST'])
@login_required
def PDM_TIadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
           
            information = request.form.get('information')
            type = request.form.get('type')
           
            add_record = PDS_Teacher_Information(information=information,
                                                type=type,
                                                faculty_account_id = current_user.faculty_account_id)
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_TI'))

@PDM.route("/PDM-Teacher-Information/delete-record", methods=['GET', 'POST'])
@login_required
def PDM_TIdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = PDS_Teacher_Information.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_TI'))

# ------------------------------- END OF PDM TEACHER INFORMATION  ---------------------------- 
 
# ------------------------------- PDM CHARACTER REFERENCE ------------------------------

@PDM.route("/PDM-Character-Reference", methods=['GET', 'POST'])
@login_required
def PDM_CR():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
      
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
        
        # UPDATE 
        
        if request.method == 'POST':
         
            # VALUES
           
            full_name = request.form.get('full_name')
            id = request.form.get('id')

            u = update(PDS_Character_Reference)
            u = u.values({"full_name": full_name})
            
            u = u.where(PDS_Character_Reference.id == id)
            db.session.execute(u)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_CR')) 
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Character-Reference.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_CR="active")

@PDM.route("/PDM-Character-Reference/add-record", methods=['GET', 'POST'])
@login_required
def PDM_CRadd():

         # INSERT RECORD
        
        if request.method == 'POST':
         
            # VALUES
            full_name = request.form.get('full_name')

            add_record = PDS_Character_Reference(full_name=full_name,
                                                faculty_account_id = current_user.faculty_account_id)
            
            db.session.add(add_record)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_CR'))

@PDM.route("/PDM-Character-Reference/delete-record", methods=['GET', 'POST'])
@login_required
def PDM_CRdel():

        # DELETE RECORD
         
        id = request.form.get('id')
        
        data = PDS_Character_Reference.query.filter_by(id=id).first() 
        
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_CR'))

# ------------------------------- END OF PDM CHARACTER REFERENCE  ---------------------------- 
 
# ------------------------------- PDM SIGNATURE ------------------------------

@PDM.route("/PDM-Signature", methods=['GET', 'POST'])
@login_required
def PDM_S():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
        id = username.faculty_account_id
        
        # CHECKING IF PROFILE PIC EXIST
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic   
        
        
             
         # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.PDS_Signature:
            data = current_user
            
            # FETCHING USER ENCRYPTED SIGNATURE DATA
            fetch = PDS_Signature.query.filter_by(faculty_account_id=current_user.faculty_account_id).first()
            
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
            
            # ENCRYPTING IMAGE DATA
            encrypted = fernet.encrypt(file.encode('utf-8'))
            
            data = """{}""".format(encrypted)
 
            if PDS_Signature.query.filter_by(faculty_account_id=current_user.faculty_account_id).first():
                
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
                
                u = update(PDS_Signature)
                u = u.values({"wet_signature": '%s'%(file1['id'])})
                u = u.where(PDS_Signature.faculty_account_id == current_user.faculty_account_id)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                
                return redirect(url_for('PDM.PDM_S')) 
            
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
                
                add_record = PDS_Signature( wet_signature = '%s'%(file1['id']),
                                            faculty_account_id = current_user.faculty_account_id)
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('PDM.PDM_S'))
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Signature.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               signature = decrypted_signature.decode('utf-8'),
                               dict_cert = decrypted_dict_cert.decode('utf-8'),
                               activate_S="active")
        
@PDM.route("/PDM-Signature/Submit_DICT", methods=['GET', 'POST'])
@login_required
def PDM_SS():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
        id = username.faculty_account_id

        # FACULTY FIS DICT CERTIFICATE FOLDER ID
        folder = '1KrXqzGYLm9ET4D6bPLwrP_QJGtCufkly'
        
        # UPDATE 
        
        if request.method == 'POST':
            file =  request.form.get('base64_dict')
            
            # ENCRYPTING IMAGE DATA
            encrypted = fernet.encrypt(file.encode('utf-8'))
            
            data = """{}""".format(encrypted)
 
            if PDS_Signature.query.filter_by(faculty_account_id=current_user.faculty_account_id).first():
                
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
                
                u = update(PDS_Signature)
                u = u.values({"dict_certificate": '%s'%(file1['id'])})
                u = u.where(PDS_Signature.faculty_account_id == current_user.faculty_account_id)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                
                return redirect(url_for('PDM.PDM_S')) 
            
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
                
                add_record = PDS_Signature( dict_certificate = '%s'%(file1['id']),
                                            faculty_account_id = current_user.faculty_account_id)
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('PDM.PDM_S'))

# ------------------------------- END OF PDM SIGNATURE  ---------------------------- 
 
# ------------------------------- PDM ADDITIONAL QUESTIONS ------------------------------
  
@PDM.route("/PDM-Additional-Questions", methods=['GET', 'POST'])
@login_required
def PDM_AQ():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
       
        # CHECKING IF PROFILE PIC EXIST
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic   
             
        # VERIFYING IF DATA OF CURRENT USER EXISTS
        if current_user.PDS_Additional_Questions:
            data = current_user
        else:
            data =  {'PDS_Additional_Questions':
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
           

            if PDS_Additional_Questions.query.filter_by(faculty_account_id=current_user.faculty_account_id).first():
                u = update(PDS_Additional_Questions)
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
                u = u.where(PDS_Additional_Questions.faculty_account_id == current_user.faculty_account_id)
                db.session.execute(u)
                db.session.commit()
                db.session.close()
                return redirect(url_for('PDM.PDM_AQ'))
            
            else:
                add_record = PDS_Additional_Questions(  
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
                                                    faculty_account_id = current_user.faculty_account_id)
            
                db.session.add(add_record)
                db.session.commit()
                db.session.close()
                return redirect(url_for('PDM.PDM_AQ'))
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Additional-Questions.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               data = data,
                               activate_AQ="active")
  
# ------------------------------- END OF PDM ADDITIONAL QUESTIONS  ---------------------------- 
 
# ------------------------------- PDM PERSONAL DATA REPORTS ------------------------------
   
  
@PDM.route("/PDM-Personal-Data-Reports")
@login_required
def PDM_PDR():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
      
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Personal-Data-Reports.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_PDR="active")
    
# ------------------------------- END OF PDM PERSONAL DATA REPORTS  ---------------------------- 
 
# ------------------------------------------------------------- 
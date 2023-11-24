from flask import Flask, Blueprint, redirect, render_template, request, url_for
from dotenv import load_dotenv
from flask_login import login_required, current_user
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from urllib.request import urlretrieve

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

# Default Profile Pic
profile_default='14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08'


# FACULTY PERSONAL DATA MANAGEMENT ROUTE

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
        
        print(data)
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_FB'))
 
# ------------------------------- END OF PDM FAMILY BACKGROUNDS ---------------------------- 

 
# ------------------------------- PDM EDUCATIONAL BACKGROUNDS ----------------------------  

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
         
        # def delete(self, item_id):
        # item = ItemModel.query.get_or_404(item_id)
        # db.session.delete(item)
        # db.session.commit()
        # return {"message": "Item deleted."}

        id = request.form.get('id')
        

        data = PDS_Educational_Background.query.filter_by(id=id).first() 
        
        print(data)
        if data:
            db.session.delete(data)
            db.session.commit()
            db.session.close()
            return redirect(url_for('PDM.PDM_EB'))


# ------------------------------- END OF PDM EDUCATIONAL BACKGROUNDS ----------------------------


@PDM.route("/PDM-Eligibities")
@login_required
def PDM_E():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
       
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Eligibities.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_E="active")
  


@PDM.route("/PDM-Work-Experience")
@login_required
def PDM_WE():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic 
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Work-Experience.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_WE="active")
  
  

@PDM.route("/PDM-Voluntary-Works")
@login_required
def PDM_VW():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Voluntary-Works.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_VW="active")
  

@PDM.route("/PDM-Training-Seminars")
@login_required
def PDM_TS():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 

        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Training-Seminars.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_TS="active")
  

@PDM.route("/PDM-Outstanding-Achievements")
@login_required
def PDM_OA():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
       
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Outstanding-Achievements.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_OA="active")

 
@PDM.route("/PDM-Officeships-Memberships")
@login_required
def PDM_OSM():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
      
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Officeships-Memberships.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_OSM="active")

 
@PDM.route("/PDM-Agency-Membership")
@login_required
def PDM_AM():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
      
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Agency-Membership.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_AM="active")  


@PDM.route("/PDM-Teacher-Information")
@login_required
def PDM_TI():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
      
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Teacher-Information.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_TI="active")  


@PDM.route("/PDM-Character-Reference")
@login_required
def PDM_CR():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
      
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Character-Reference.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_CR="active")


@PDM.route("/PDM-Signature")
@login_required
def PDM_S():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
    
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Signature.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_S="active")
   
  
@PDM.route("/PDM-Additional-Questions")
@login_required
def PDM_AQ():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT    
        username = Faculty_Profile.query.filter_by(faculty_account_id=current_user.faculty_account_id).first() 
       
        if username.profile_pic == None:
            profile_pic=profile_default
        else:
            profile_pic=username.profile_pic
                                
        return render_template("Faculty-Home-Page/Personal-Data-Management-Page/PDM-Additional-Questions.html", 
                               User=username.first_name + " " + username.last_name, 
                               profile_pic=profile_pic,
                               PDM="show",
                               user = current_user,
                               activate_AQ="active")
  
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
    

# ------------------------------------------------------------- 
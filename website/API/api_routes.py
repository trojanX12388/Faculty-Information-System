from flask import Blueprint, json, make_response, request, jsonify
from flask_restx import Api, Resource
from dotenv import load_dotenv
from .authentication import *

# DATABASE PLUGINS

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect,update, values
from sqlalchemy.orm.attributes import flag_modified

from sqlalchemy import create_engine,inspect,update, values
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import sessionmaker

import ast
import os


# LOADING MODEL CLASSES

load_dotenv()


# EXECUTING DATABASE

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine=create_engine(os.getenv('DATABASE_URI'), pool_pre_ping=True, pool_size=10, max_overflow=20, pool_recycle=1800)
session=sessionmaker(bind= engine)()

# Access API keys from environment variables

API_KEYS = ast.literal_eval(os.environ["API_KEYS"])

# JSON DATA API

API = Blueprint('API', __name__)

api = Api(API, version="2.0")

# ---------------------------------------------------------

# MAIN API V1

# FACULTY DATA 
     
@API.route("/api/all/faculty_data", methods=['GET'])
@admin_token_required # Get the API key from the request header
def faculty_data():
    
    token = request.args.get('token')  # Get the API key from the request header
    
    key = jwt.decode(token, app.config['SECRET_KEY'])
    
    key = key['key']
    
    if not key in API_KEYS.values():
         return jsonify(message="Invalid key you cant have an access"), 403
    
    else:
         
        f = '"'
        faculty = str("Faculty_Profile")
        postgreSQL_select_Query = "SELECT * FROM" f'{f}'f'{faculty}'f'{f}'
        # DATABASE CURSOR
        
        cursor=session.connection().connection.cursor()
        cursor.execute(postgreSQL_select_Query)

        faculty_data = cursor.fetchall()
        
        jsontable = {'FIS_data':[]}
        faculty_primary = {'faculty':[]}
        
        for data in faculty_data:
            
            # FACULTY DATA
            
            jsonprimarydata = {
            'name': data[1],
            str(data[0]):[]
        }
            # BASIC DATA
            jsondata = {
            'first_name': data[2],
            'last_name': data[3],
            'middle_name': data[4],
            'middle_initial': data[5],
            'name_extension': data[6],
            'birth_date': data[7],
            'date_hired': data[8],
            'remarks': data[9],
            'faculty_code': data[10],
            'employee_no': data[0],
            'honorific': data[11],
            'age': data[12],
            'email': data[13],
            'profile_pic': 'https://drive.google.com/file/d/'+str(data[15])+'/view',
            'is_active': data[16],
            # PDS DATA
            'PDS_Data':{
                'PDS_Personal_Details':[],
                'PDS_Contact_Details':[],
                'PDS_Family_Background':[],
                'PDS_Educational_Background':[],
                'PDS_Eligibity':[],
                'PDS_Work_Experience':[],
                'PDS_Voluntary_Work':[],
                'PDS_Training_Seminars':[],
                'PDS_Outstanding_Achievements':[],
                'PDS_OfficeShips_Memberships':[],
                'PDS_Agency_Membership':[],
                'PDS_Teacher_Information':[],
                'PDS_Additional_Questions':[],
                'PDS_Character_Reference':[],
                'PDS_Signature':[],
                }
            }
            jsonprimarydata[str(data[0])].append(dict(jsondata))
            faculty_primary["faculty"].append(dict(jsonprimarydata)) 
            
            # FETCHING PDS PERSONAL DETAILS DATA
            
            faculty1 = str("PDS_Personal_Details")
            postgreSQL_select_Query1 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor1=session.connection().connection.cursor()
            cursor1.execute(postgreSQL_select_Query1)

            PDS_Personal_Details = cursor1.fetchall()
            for data1 in PDS_Personal_Details:
                json_pds_PD_data = {
                    'sex': data1[2],
                    'gender': data1[3],
                    'height': data1[4],
                    'weight': data1[5],
                    'religion': data1[6],
                    'civil_status': data1[7],
                    'blood_type': data1[8],
                    'pronoun': data1[9],
                    'country': data1[10],
                    'city': data1[11],
                    'citizenship': data1[12],
                    'dual_citizenship': data1[13],
                    'remarks': data1[14],
                    'is_active': data1[15],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Personal_Details"].append(dict(json_pds_PD_data))
                cursor1.close()
                
            # FETCHING PDS CONTACT DETAILS DATA
        
            faculty1 = str("PDS_Contact_Details")
            postgreSQL_select_Query1 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor2=session.connection().connection.cursor()
            cursor2.execute(postgreSQL_select_Query1)

            PDS_Personal_Details = cursor2.fetchall()
            for data1 in PDS_Personal_Details:
                json_pds_PD_data = {
                    'email': data1[2],
                    'mobile_number': data1[3],
                    'perm_country': data1[4],
                    'perm_region': data1[5],
                    'perm_province': data1[6],
                    'perm_city': data1[7],
                    'perm_address': data1[8],
                    'perm_zip_code': data1[9],
                    'perm_phone_number': data1[10],
                    'res_country': data1[11],
                    'res_region': data1[12],
                    'res_province': data1[13],
                    'res_city': data1[14],
                    'res_address': data1[15],
                    'res_zip_code': data1[16],
                    'res_phone_number': data1[17],
                    'remarks': data1[18],
                    'is_active': data1[19]
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Contact_Details"].append(dict(json_pds_PD_data))
                cursor2.close()
            
            # FETCHING PDS FAMILY BACKGROUND
        
            faculty1 = str("PDS_Family_Background")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor3=session.connection().connection.cursor()
            cursor3.execute(postgreSQL_select_Query2)

            PDS_Family_Background = cursor3.fetchall()
            for data1 in PDS_Family_Background:
                json_pds_PD_data = {
                    'full_name': data1[2],
                    'relationship': data1[3],
                    'is_delete': data1[4]
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Family_Background"].append(dict(json_pds_PD_data))
                cursor3.close()
            
            # FETCHING PDS Educational Background  
        
            faculty1 = str("PDS_Educational_Background")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor4=session.connection().connection.cursor()
            cursor4.execute(postgreSQL_select_Query2)

            PDS_Educational_Background = cursor4.fetchall()
            for data1 in PDS_Educational_Background:
                json_pds_PD_data = {
                    'school_name': data1[2],
                    'level': data1[3],
                    'from_date': data1[4],
                    'to_date': data1[5],
                    'is_delete': data1[6],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Educational_Background"].append(dict(json_pds_PD_data))
                cursor4.close()
            
            # FETCHING PDS Eligibity   
        
            faculty1 = str("PDS_Eligibity")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor5=session.connection().connection.cursor()
            cursor5.execute(postgreSQL_select_Query2)

            PDS_Eligibity = cursor5.fetchall()
            for data1 in PDS_Eligibity:
                json_pds_PD_data = {
                    'eligibity': data1[2],
                    'rating': data1[3],
                    'is_delete': data1[4],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Eligibity"].append(dict(json_pds_PD_data))
                cursor5.close()
            
            # FETCHING PDS Work Experience  
        
            faculty1 = str("PDS_Work_Experience")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor6=session.connection().connection.cursor()
            cursor6.execute(postgreSQL_select_Query2)

            PDS_Work_Experience = cursor6.fetchall()
            for data1 in PDS_Work_Experience:
                json_pds_PD_data = {
                    'position': data1[2],
                    'company_name': data1[3],
                    'status': data1[4],
                    'from_date': data1[5],
                    'to_date': data1[6],
                    'is_delete': data1[7],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Eligibity"].append(dict(json_pds_PD_data))
                cursor6.close()
            
            # FETCHING PDS Voluntary Work 
        
            faculty1 = str("PDS_Voluntary_Work")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor7=session.connection().connection.cursor()
            cursor7.execute(postgreSQL_select_Query2)

            PDS_Voluntary_Work = cursor7.fetchall()
            for data1 in PDS_Voluntary_Work:
                json_pds_PD_data = {
                    'organization': data1[2],
                    'position': data1[3],
                    'status': data1[4],
                    'from_date': data1[5],
                    'to_date': data1[6],
                    'is_delete': data1[7],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Voluntary_Work"].append(dict(json_pds_PD_data))
                cursor7.close()
            
            # FETCHING PDS Training & Seminars 
        
            faculty1 = str("PDS_Training_Seminars")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor8=session.connection().connection.cursor()
            cursor8.execute(postgreSQL_select_Query2)

            PDS_Training_Seminars = cursor8.fetchall()
            for data1 in PDS_Training_Seminars:
                json_pds_PD_data = {
                    'title': data1[2],
                    'level': data1[3],
                    'from_date': data1[4],
                    'to_date': data1[5],
                    'is_delete': data1[6],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Training_Seminars"].append(dict(json_pds_PD_data))
                cursor8.close()
            
            # FETCHING PDS Outstanding Achievements
            
            faculty1 = str("PDS_Outstanding_Achievements")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor9=session.connection().connection.cursor()
            cursor9.execute(postgreSQL_select_Query2)

            PDS_Outstanding_Achievements = cursor9.fetchall()
            for data1 in PDS_Outstanding_Achievements:
                json_pds_PD_data = {
                    'achievement': data1[2],
                    'level': data1[3],
                    'date': data1[4],
                    'is_delete': data1[5],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Outstanding_Achievements"].append(dict(json_pds_PD_data))
                cursor9.close()
            
            # FETCHING PDS OfficeShips/Memberships
            
            faculty1 = str("PDS_OfficeShips_Memberships")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor10=session.connection().connection.cursor()
            cursor10.execute(postgreSQL_select_Query2)

            PDS_OfficeShips_Memberships = cursor10.fetchall()
            for data1 in PDS_OfficeShips_Memberships:
                json_pds_PD_data = {
                    'organization': data1[2],
                    'position': data1[3],
                    'from_date': data1[4],
                    'to_date': data1[5],
                    'is_delete': data1[6],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_OfficeShips_Memberships"].append(dict(json_pds_PD_data))
                cursor10.close()
            
            # FETCHING PDS Agency Membership
            
            faculty1 = str("PDS_Agency_Membership")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor11=session.connection().connection.cursor()
            cursor11.execute(postgreSQL_select_Query2)

            PDS_Agency_Membership = cursor11.fetchall()
            for data1 in PDS_Agency_Membership:
                json_pds_PD_data = {
                    'GSIS': data1[2],
                    'PAGIBIG': data1[3],
                    'PHILHEALTH': data1[4],
                    'SSS': data1[5],
                    'TIN': data1[6],
                    'remarks': data1[7],
                    'is_delete': data1[8],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Agency_Membership"].append(dict(json_pds_PD_data))
                cursor11.close()
                
            # FETCHING PDS Teacher Information
            
            faculty1 = str("PDS_Teacher_Information")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor12=session.connection().connection.cursor()
            cursor12.execute(postgreSQL_select_Query2)

            PDS_Teacher_Information = cursor12.fetchall()
            for data1 in PDS_Teacher_Information:
                json_pds_PD_data = {
                    'information': data1[2],
                    'type': data1[3],
                    'is_delete': data1[4],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Teacher_Information"].append(dict(json_pds_PD_data))
                cursor12.close()
                
            # FETCHING PDS Additional Questions
            
            faculty1 = str("PDS_Additional_Questions")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor13=session.connection().connection.cursor()
            cursor13.execute(postgreSQL_select_Query2)

            PDS_Additional_Questions = cursor13.fetchall()
            for data1 in PDS_Additional_Questions:
                json_pds_PD_data = {
                    'q1_a': data1[2],
                    'q1_a_details': data1[3],
                    
                    'q1_b': data1[4],
                    'q1_b_details': data1[5],
                    
                    'q2_a': data1[6],
                    'q2_a_details': data1[7],
                    
                    'q2_b': data1[8],
                    'q2_b_details': data1[9],
                    
                    'q3': data1[10],
                    'q3_details': data1[11],
                    
                    'q4': data1[12],
                    'q4_details': data1[13],
                    
                    'q5_a': data1[14],
                    'q5_a_details': data1[15],
                    
                    'q5_b': data1[16],
                    'q5_b_details': data1[17],
                    
                    'q6': data1[18],
                    'q6_details': data1[19],
                    
                    'q7_a': data1[20],
                    'q7_a_details': data1[21],
                    
                    'q7_b': data1[22],
                    'q7_b_details': data1[23],
                    
                    'q7_c': data1[24],
                    'q7_c_details': data1[25],
                    
                    'is_delete': data1[26],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Additional_Questions"].append(dict(json_pds_PD_data))
                cursor13.close()
            
            # FETCHING PDS Character Reference
            
            faculty1 = str("PDS_Character_Reference")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor14=session.connection().connection.cursor()
            cursor14.execute(postgreSQL_select_Query2)

            PDS_Character_Reference = cursor14.fetchall()
            for data1 in PDS_Character_Reference:
                json_pds_PD_data = {
                    'full_name': data1[2],
                    'is_delete': data1[3],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Character_Reference"].append(dict(json_pds_PD_data))
                cursor14.close()
                
             # FETCHING PDS Signature
            
            faculty1 = str("PDS_Signature")
            postgreSQL_select_Query2 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor15=session.connection().connection.cursor()
            cursor15.execute(postgreSQL_select_Query2)

            PDS_Signature = cursor15.fetchall()
            for data1 in PDS_Signature:
                json_pds_PD_data = {
                    'wet_signature': data1[2],
                    'dict_certificate': data1[3],
                    'is_delete': data1[4],
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Signature"].append(dict(json_pds_PD_data))
                cursor15.close()
            
            cursor.close()
            session.close()
            
        jsontable["FIS_data"].append(dict(faculty_primary))
        
        return jsonify(jsontable), 200
        

# ---------------------------------------------------------
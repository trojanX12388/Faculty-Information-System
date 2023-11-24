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

# JSON UNSORTING DATA FUNCTION

def make_unsorted_response(results_dict: dict, status_code: int):
    resp = make_response({}, status_code)
    j_string = json.dumps(results_dict, separators=(',', ':'))
    resp.set_data(value=j_string)
    return resp

# -------------------------------------------------------------

# TESTING UNSORTING JSON FUNCTION

@api.route('/test', endpoint='test')
@api.doc(params={}, description="test")
class Health(Resource):
    def get(self):
        my_dict = {'z': 'z value',
                   'w': 'w value',
                   'p': 'p value'}
        results_dict = {"results": my_dict}
        return make_unsorted_response(results_dict, 200)

# -------------------------------------------------------------


# JSON DATA SAMPLE FROM GET "user_id"

@API.route("/get-user/<user_id>")
def get_user(user_id):
    user_data = {
        # TABLE NAME
        "User_Data":
        {
        # API DATA 
        "user_id": user_id,
        "name": "Alma Matter",
        "email": "alma123@gmail.com",
        "username": "alma123",
        "gender": "female",
        "age": "35"
        }
    }
        
    
    extra = request.args.get("extra")
    if extra:
        user_data["extra"] = extra
   
    return jsonify(user_data), 200


# JSON POST METHOD

@API.route("/create-user", methods=["POST"])
def create_user():
    data = request.get_json()
    
    return jsonify(data), 201






# API ROUTES
     
@API.route("/api/all/faculty", methods=['GET'])
def adminP():
    key = request.args.get('key')  # Get the API key from the request header

    if not key:
        return make_response({"message":"No API Key provided"},406)
    
    elif not key in API_KEYS.values():
         return jsonify(message="Invalid key you cant have an access")
    else:
       
        user_data = {
            # TABLE NAME
            "Faculty_Data":
            {
            # API DATA 
            "user_id": '2020-0001',
            "name": "Alma Matter",
            "email": "alma123@gmail.com",
            "username": "alma123",
            "gender": "female",
            "age": "35"
            }
        }
            
        
        extra = request.args.get("extra")
        if extra:
            user_data["extra"] = extra
    
        return jsonify(user_data), 200


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
            # PDS DATA
            'PDS_Data':{
                'PDS_Personal_Details':[],
                'PDS_Contact_Details':[],
                }
            }
            jsonprimarydata[str(data[0])].append(dict(jsondata))
            faculty_primary["faculty"].append(dict(jsonprimarydata)) 
            
            # FETCHIN PDS PERSONAL DETAILS DATA
            
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
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Personal_Details"].append(dict(json_pds_PD_data))
                cursor1.close()
                
            # FETCHIN PDS CONTACT DETAILS DATA
        
            faculty1 = str("PDS_Contact_Details")
            postgreSQL_select_Query1 = "SELECT * FROM" f'{f}'f'{faculty1}'f'{f}'"WHERE faculty_account_id = '{}';".format(data[0])
            
            # DATABASE CURSOR
        
            cursor1=session.connection().connection.cursor()
            cursor1.execute(postgreSQL_select_Query1)

            PDS_Personal_Details = cursor1.fetchall()
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
                    'remarks': data1[18]
                }
                jsonprimarydata[str(data[0])][0]["PDS_Data"]["PDS_Contact_Details"].append(dict(json_pds_PD_data))
                cursor1.close()

            cursor.close()
            session.close()
            
        jsontable["FIS_data"].append(dict(faculty_primary))
        
        return jsonify(jsontable), 200
        

# ---------------------------------------------------------
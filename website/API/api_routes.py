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
        
        session.begin()
        
        cursor=session.connection().connection.cursor()
        cursor.execute(postgreSQL_select_Query)

        faculty_data = cursor.fetchall()
        
        jsontable = {'FIS_data':[]}
        faculty_primary = {'faculty':[]}
        
        for data in faculty_data:
            jsonprimarydata = {
            str(data[0]):[]
        }
            jsondata = {
            'first_name': data[3],
            'last_name': data[4],
            'middle_name': data[5],
            'middle_initial': data[6],
            'name_extension': data[7],
            'birth_date': data[8],
            'date_hired': data[9],
            'remarks': data[10],
            'employee_code': data[1],
            'honorific': data[12],
            'age': data[13],
            'email': data[14],
            'profile_pic': 'https://drive.google.com/file/d/'+str(data[16])+'/view'
            }
            
            jsonprimarydata[""+str(data[0])].append(dict(jsondata))
            faculty_primary["faculty"].append(dict(jsonprimarydata))   
            
            cursor.close()
            session.close()
        jsontable["FIS_data"].append(dict(faculty_primary))
        
        return jsonify(jsontable), 200
        

# ---------------------------------------------------------
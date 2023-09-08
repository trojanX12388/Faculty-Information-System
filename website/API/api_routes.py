from flask import Blueprint, json, make_response, request, jsonify
from flask_restx import Api, Resource
from dotenv import load_dotenv
from .authentication import *

import ast
import os

load_dotenv()

# Access API keys from environment variables

API_KEYS = ast.literal_eval(os.environ["API_KEY"])

# JSON DATA API

API = Blueprint('API', __name__)

api = Api(API)

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
            "User_Data":
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

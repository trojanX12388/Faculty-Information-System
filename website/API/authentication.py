from flask import Flask, jsonify, session, request
from functools import wraps
import datetime

import jwt
import os,ast,random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['REFRESH_TOKEN_SECRET'] = os.getenv('REFRESH_TOKEN_SECRET')

API_KEYS = ast.literal_eval(os.environ["API_KEYS"])

# TOKEN VERIFICATION FUNCTION

def admin_token_required(func):
    # decorator factory which invoks update_wrapper() method and passes decorated function as an argument
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401

        try:

            data = jwt.decode(token, app.config['SECRET_KEY'])
        # You can use the JWT errors in exception
        # except jwt.InvalidTokenError:
        #     return 'Invalid token. Please log in again.'
        except:
            return jsonify({'Message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated

# ---------------------------------------------------------------

# # Get a random item (key-value pair) from the dictionary
# random_item = random.choice(list(API_KEYS.items()))

# # Assign the random item to variables (key and value)
# token_key, token_value = random_item

# # TOKEN REFRESH AND GENERATE FUNCTION

# # Function to generate access token
# def generate_access_token(user_id):
#     access_token_payload = {
#         'user_id'  : user_id,
#         'token_name': token_key,
#         'key': token_value,
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Token expiration time (30 minutes)
#     }
#     access_token = jwt.encode(access_token_payload, app.config['SECRET_KEY'], algorithm='HS256')
#     return access_token.decode('UTF-8')

# # Function to generate refresh token
# def generate_refresh_token(user_id):
#     refresh_token_payload = {
#         'user_id'  : user_id,
#         'token_name': token_key,
#         'key': token_value,
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Refresh token expiration time (1 day)
#     }
#     refresh_token = jwt.encode(refresh_token_payload, app.config['REFRESH_TOKEN_SECRET'], algorithm='HS256')
#     return refresh_token.decode('UTF-8')
         

# # Route for token refresh using refresh token
# @app.route('/api/token/refresh', methods=['POST'])
# def refresh_token():
#     refresh_token = request.json.get('refresh_token')

#     if not refresh_token:
#         return jsonify({'message': 'Refresh token is missing'}), 401

#     try:
#         decoded_refresh_token = jwt.decode(refresh_token, app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
#         user_id = decoded_refresh_token['user_id']

#         new_access_token = generate_access_token(user_id)
#         return jsonify({'access_token': new_access_token}), 200
#     except jwt.ExpiredSignatureError:
#         return jsonify({'message': 'Refresh token has expired'}), 401
#     except jwt.InvalidTokenError:
#         return jsonify({'message': 'Invalid refresh token'}), 401
    
# # Route for user login and JWT generation
# @app.route('/login', methods=['POST'])
# def login():
#     auth = request.authorization
#     if not auth or not auth.username or not auth.password:
#         return jsonify({'message': 'Invalid username or password'}), 401

#     username = auth.username
#     password = auth.password

#     if users.get(username) == password:
#         access_token = generate_access_token(username)
#         refresh_token = generate_refresh_token(username)
#         return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200
#     else:
#         return jsonify({'message': 'Invalid username or password'}), 401

   
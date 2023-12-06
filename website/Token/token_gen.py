from flask import Flask
import datetime

import jwt
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['REFRESH_TOKEN_SECRET'] = os.getenv('REFRESH_TOKEN_SECRET')


# TOKEN REFRESH AND GENERATE FUNCTION

# Function to generate access token
def generate_access_token(user_id):
    access_token_payload = {
        'user_id'  : user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Token expiration time (30 minutes)
    }
    access_token = jwt.encode(access_token_payload, app.config['SECRET_KEY'], algorithm='HS256')
    return access_token

# Function to generate refresh token
def generate_refresh_token(user_id):
    refresh_token_payload = {
        'user_id'  : user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=15)  # Refresh token expiration time (1 day)
    }
    refresh_token = jwt.encode(refresh_token_payload, app.config['REFRESH_TOKEN_SECRET'], algorithm='HS256')
    return refresh_token



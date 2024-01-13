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

            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
        # You can use the JWT errors in exception
        # except jwt.InvalidTokenError:
        #     return 'Invalid token. Please log in again.'
        except:
            return jsonify({'Message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated

# ---------------------------------------------------------------
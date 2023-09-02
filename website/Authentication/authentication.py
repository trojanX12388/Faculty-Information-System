from flask import Flask, jsonify, session
from functools import wraps
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'db8ec40dda154bd4a75b85021b1708a0'

# TOKEN VERIFICATION FUNCTION

def admin_token_required(func):
    # decorator factory which invoks update_wrapper() method and passes decorated function as an argument
    @wraps(func)
    def decorated(*args, **kwargs):
        token = session['admin_token']
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401

        try:

            data = jwt.decode(token, app.config['SECRET_KEY'])
        # You can use the JWT errors in exception
        # except jwt.InvalidTokenError:
        #     return 'Invalid token. Please log in again.'
        except:
            session['admin_logged_in'] = False
            return jsonify({'Message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated

         
   
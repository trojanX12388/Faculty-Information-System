from flask import Flask, request, session
from datetime import datetime, timedelta
import jwt,os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# SECRET KEY GEN:

def admin_token_gen():
        session['logged_in'] = True
        token = jwt.encode({
        'user': request.form['username'],
        'exp': (datetime.utcnow() + timedelta(seconds=10))
        },
            app.config['SECRET_KEY']) 
        session['admin_token'] = token.decode('utf-8')
            
             


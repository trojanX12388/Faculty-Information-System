from flask import Flask, request, session
from datetime import datetime, timedelta
import jwt,os


app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")



# SECRET KEY GEN:

def admin_token_gen():
        session['logged_in'] = True
        token = jwt.encode({
        'key': ''
        },
            app.config['SECRET_KEY']) 
        session['key'] = token.decode('utf-8')
            
             


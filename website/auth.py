from flask import Flask, Blueprint, flash, json, make_response, redirect, render_template, request, jsonify, url_for, session
from flask_restx import Api, Resource
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

# IMPORT LOCAL FUNCTIONS

from .Authentication.authentication import *
#--TOKEN GENERATOR FUNCTION
from .Token.token_gen import *


# DATABASE CONNECTION

HOST = os.getenv("HOST")
DB = os.getenv("DB")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

conn = psycopg2.connect(host=f"{HOST}", dbname=f"{DB}", user=f"{USER}",
                                password=f"{PASSWORD}", port=5432)
# -------------------------------------------------------------

# 




# -------------------------------------------------------------


# WEB AUTH ROUTES URL

auth = Blueprint('auth', __name__)

@auth.route("/admin-login-auth", methods=['GET', 'POST'])
def adminLA():
    if request.method == 'POST':
        if request.form['username'] and request.form['password'] == '123456':
            admin_token_gen()
            return redirect(url_for('auth.adminP'))
        else:            
            return make_response('Unable to verify', 403, {'WWW-Authenticate' : 'Basic realm:"Authentication Failed!'})     
    else:
        return 'Login First!'    
        

@auth.route("/admin-page", methods=['GET', 'POST'])
@admin_token_required
def adminP():
    session['admin_logged_in'] = True
    return 'JWT is verified. Welcome to your dashboard !  '
   

@auth.route('/faculty-login', methods=['GET', 'POST'])
def facultyL():

    email = request.form.get('email')
    password = request.form.get('password')


    cur = conn.cursor()
    query = "SELECT * FROM faculty_account WHERE email = %s"
    cur.execute(query,[email])

    result = cur.fetchall()
    
    # CHECKING IF ENTERED EMAIL IS NOT IN THE DATABASE
    if request.method == 'POST':
        checkemail = result
        if len(checkemail) == 0:
            flash('Entered Email is not found in the system. Please try again.', category='error')  

    # USER ACCOUNT VERIFICATION
    if result:
        for i in result:
            cemail = str(i[3])
            cpass = str(i[4])
            
            if email == cemail and password != cpass:
                flash('Incorrect Password.', category='error') 
            elif email == cemail and password == cpass:
                session['user'] = request.form.get('email')
                session['faculty_logged_in'] = True
                return redirect(url_for('auth.facultyH'))   
                
    return render_template("Faculty-Login-Page/index.html")


@auth.route("/faculty-home-page")
def facultyH():
    # INITIALIZING DATA FROM USER LOGGED IN ACCOUNT
        if session:
            if session['user']:
                user = session['user']
                        
                cur = conn.cursor()
                query = "SELECT * FROM faculty_account WHERE email = %s"
                cur.execute(query,[user])
                            
                result = cur.fetchall()
                            
                if result:
                    for i in result:
                        username = str(i[1])
                                
                message = 'Welcome! ' + str(username)
                                
                flash(message, category='success') 
                return render_template("Faculty-Home-Page/home.html")
        
        else:
            flash('Session Expired. Login to enter', category='error') 
            return redirect(url_for('auth.facultyL')) 



@auth.route("/faculty-forgot-pass")
def facultyF():
    return ("<title>Forgot Faculty Password</title><h1>Forgot Password</h1>")


@auth.route("/logout")
def Logout():
    session.pop('user', None)
    session.pop('faculty_logged_in', None)
    flash('Logged Out Successfully!.', category='success')
    return redirect(url_for('auth.facultyL')) 
     
   


@auth.route("/sign-up")
def signUp():
    return ("<h1>Sign Up</h1>")


# -------------------------------------------------------------

# JSON DATA API


# JSON UNSORTING DATA FUNCTION

api = Api(auth)

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


@auth.route("/get-user/<user_id>")
def get_user(user_id):
    user_data = {
        "user_id": user_id,
        "name": "Alma Matter",
        "email": "alma123@gmail.com"
        }
    
    extra = request.args.get("extra")
    if extra:
        user_data["extra"] = extra
   
    return jsonify(user_data), 200


# JSON POST METHOD

@auth.route("/create-user", methods=["POST"])
def create_user():
    data = request.get_json()
    
    return jsonify(data), 201

# -------------------------------------------------------------
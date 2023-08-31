from flask import Blueprint, flash, json, make_response, redirect, render_template, request, jsonify, url_for, session
from flask_restx import Api, Resource
import psycopg2


# DATABASE CONNECTION

conn = psycopg2.connect(host="34.72.164.60", dbname="FIS", user="postgres",
                                password="plazma12388", port=5432)

# -------------------------------------------------------------

# GLOBAL VARIABLES



# -------------------------------------------------------------

# WEB AUTH ROUTES URL

auth = Blueprint('auth', __name__)

@auth.route("/admin-login", methods=['GET', 'POST'])
def adminL():
    return ("<h1>Admin Login</h1>")


@auth.route('/faculty-login', methods=['GET', 'POST'])
def facultyL():

    global email
    
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
            flash('Sign In First to enter Faculty Home Page.', category='error') 
            return redirect(url_for('auth.facultyL')) 



@auth.route("/faculty-forgot-pass")
def facultyF():
    return ("<title>Forgot Faculty Password</title><h1>Forgot Password</h1>")


@auth.route("/logout")
def Logout():
    session.pop('user', None)
    return ("<h1>Logged Out</h1>")


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
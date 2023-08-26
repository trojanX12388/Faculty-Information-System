from flask import Blueprint, flash, redirect, render_template, request, jsonify, url_for
import psycopg2

# DATABASE CONNECTION

conn = psycopg2.connect(host="34.72.164.60", dbname="FIS", user="postgres",
                                password="plazma12388", port=5432)

# -------------------------------------------------------------

# WEB AUTH ROUTES URL

auth = Blueprint('auth', __name__)

@auth.route("/admin-login", methods=['GET', 'POST'])
def adminL():
    return ("<h1>Admin Login</h1>")


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
            print(cemail)
            
            if email == cemail and password != cpass:
                flash('Incorrect Password.', category='error') 
            elif email == cemail and password == cpass:
                return redirect(url_for('auth.facultyH'))   
                
      
    return render_template("Faculty-Login-Page/index.html")


@auth.route("/faculty-home-page", methods=['GET', 'POST'])
def facultyH():
    return render_template("Faculty-Home-Page/home.html")


@auth.route("/faculty-forgot-pass")
def facultyF():
    return ("<h1>Forgot Password</h1>")


@auth.route("/logout")
def Logout():
    return ("<h1>Logged Out</h1>")


@auth.route("/sign-up")
def signUp():
    return ("<h1>Sign Up</h1>")


# -------------------------------------------------------------

# JSON DATA API

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
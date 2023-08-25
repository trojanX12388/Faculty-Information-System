from flask import Blueprint, flash, redirect, render_template, request, url_for
import psycopg2
conn = psycopg2.connect(host="34.72.164.60", dbname="FIS", user="postgres",
                                password="plazma12388", port=5432)

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
    if result:
        for i in result:
            cemail = str(i[3])
            cpass = str(i[4])
            print(cpass)
            if email == cemail and password == cpass:
                return redirect(url_for('auth.facultyH'))
      
    return render_template("Faculty-Login-Page/index.html")


@auth.route("/faculty-home-page", methods=['GET', 'POST'])
def facultyH():
    return render_template("Faculty-Home-Page/home.html")


@auth.route("/logout")
def Logout():
    return ("<h1>Logged Out</h1>")


@auth.route("/sign-up")
def signUp():
    return ("<h1>Sign Up</h1>")
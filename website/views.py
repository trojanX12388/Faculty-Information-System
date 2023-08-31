from flask import Blueprint, render_template, session, flash, redirect, url_for
import psycopg2

views = Blueprint('views', __name__)

conn = psycopg2.connect(host="34.72.164.60", dbname="FIS", user="postgres",
                                password="plazma12388", port=5432)

@views.route("/")
def home():
    if session:
            if session['user']:
                return redirect(url_for('auth.facultyH'))
            
    return render_template("base.html")

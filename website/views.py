from flask import Blueprint, render_template, session, flash, redirect, url_for

views = Blueprint('views', __name__)

@views.route("/", methods=['GET', 'POST'])
def home():
    # CHECKING ACTIVE SESSIONS
    if session.get('faculty_logged_in'):      
        return redirect(url_for('auth.facultyH'))
    
    elif session.get('admin_logged_in'): 
        return redirect(url_for('auth.adminP'))
    
    # IF NO ACTIVE SESSION, REDIRECT TO MAIN PAGE
    else:
        return render_template("base.html")


@views.route("/admin-login", methods=['GET', 'POST'])
def adminL():
    return render_template("Admin-Login-Page/index.html")
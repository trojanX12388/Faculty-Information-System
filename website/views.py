from flask import Blueprint, render_template, session, flash, redirect, url_for
from flask_login import current_user

views = Blueprint('views', __name__)



# MAIN PAGE
@views.route("/")
def home():
    # CHECKING ACTIVE SESSIONS
    if current_user.__class__.__name__ == "FISFaculty":     
        return redirect(url_for('auth.facultyH'))
    
    elif current_user.__class__.__name__ == "FISAdmin":     
        return redirect(url_for('auth.adminH'))
    
    # IF NO ACTIVE SESSION, REDIRECT TO MAIN PAGE
    else:
        return render_template("base.html")

# FACULTY LOGIN PAGE
@views.route("/faculty-login")
def facultyL():
    # CHECKING ACTIVE SESSIONS
    if current_user.__class__.__name__ == "FISFaculty":     
        return redirect(url_for('auth.facultyH'))
    
    elif current_user.__class__.__name__ == "FISAdmin":     
        return redirect(url_for('auth.adminH'))
    
    # IF NO ACTIVE SESSION, REDIRECT TO MAIN PAGE
    else:
        return render_template("Faculty-Login-Page/index.html")

# ADMIN PAGE

@views.route("/admin-login")
def adminL():
    # CHECKING ACTIVE SESSIONS
    if current_user.__class__.__name__ == "FISFaculty":     
        return redirect(url_for('auth.facultyH'))
    
    elif current_user.__class__.__name__ == "FISAdmin":     
        return redirect(url_for('auth.adminH'))
    
    # IF NO ACTIVE SESSION, REDIRECT TO MAIN PAGE
    else:
        return render_template("Admin-Login-Page/index.html")
    
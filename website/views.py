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
        return redirect(url_for('admin.adminH'))
    
    elif current_user.__class__.__name__ == "FISSystemAdmin":     
        return redirect(url_for('sysadmin.sysadminH'))
    
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
        return redirect(url_for('admin.adminH'))
    
    elif current_user.__class__.__name__ == "FISSystemAdmin":     
        return redirect(url_for('sysadmin.sysadminH'))
    
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
        return redirect(url_for('admin.adminH'))
    
    elif current_user.__class__.__name__ == "FISSystemAdmin":     
        return redirect(url_for('sysadmin.sysadminH'))
    
    # IF NO ACTIVE SESSION, REDIRECT TO MAIN PAGE
    else:
        return render_template("Admin-Login-Page/index.html")
    

# SYSTEM ADMIN PAGE

@views.route("/auth/sysadmin/login")
def sysadminL():
    # CHECKING ACTIVE SESSIONS
    session['otp_gained'] = False
    session['sysadminid'] = None
    
    if current_user.__class__.__name__ == "FISFaculty":     
        return redirect(url_for('auth.facultyH'))
    
    elif current_user.__class__.__name__ == "FISAdmin":     
        return redirect(url_for('admin.adminH'))
    
    elif current_user.__class__.__name__ == "FISSystemAdmin":     
        return redirect(url_for('sysadmin.sysadminH'))
    
    # IF NO ACTIVE SESSION, REDIRECT TO MAIN PAGE
    else:
        return render_template("System-Admin-Page/index.html")
    

@views.route("/auth/sysadmin/otp-verification")
def sysadminOTP():
    is_otp_gained = session['otp_gained']
    id = session['sysadminid'] 
    
    if is_otp_gained == True and  id != None :
        # CHECKING ACTIVE SESSIONS
        if current_user.__class__.__name__ == "FISFaculty":     
            return redirect(url_for('auth.facultyH'))
        
        elif current_user.__class__.__name__ == "FISAdmin":     
            return redirect(url_for('admin.adminH'))
        
        elif current_user.__class__.__name__ == "FISSystemAdmin":     
            return redirect(url_for('sysadmin.sysadminH'))
        
        # IF NO ACTIVE SESSION, REDIRECT TO MAIN PAGE
        else:
            return render_template("System-Admin-Page/otp-verification.html")
    
    else:
        return redirect(url_for('views.sysadminL'))
    
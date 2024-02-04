from flask import Flask, redirect, url_for, flash, session, request
from datetime import datetime
import jwt
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['REFRESH_TOKEN_SECRET'] = os.getenv('REFRESH_TOKEN_SECRET')

from website.models import FISLoginToken, FISSystemAdmin
from .token_gen import generate_access_token
from flask_login import current_user

# DATABASE CONNECTION
from website.models import db
from sqlalchemy import update


# CHECK TOKEN EXPIRATION

def Check_Token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        session['previous_url'] = request.url
        
        if current_user.__class__.__name__ == "FISFaculty":
            user_token = FISLoginToken.query.filter_by(FacultyId=current_user.FacultyId).first()
        elif current_user.__class__.__name__ == "FISAdmin":
            user_token = FISLoginToken.query.filter_by(AdminId=current_user.AdminId).first()
        elif not current_user.__class__.__name__ == "FISFaculty":
            # Handle other user types here if needed
            flash('Unknown user type.', category='error')
            return redirect(url_for('auth.Logout'))
        else:
            # Handle other user types here if needed
            flash('Unknown user type.', category='error')
            return redirect(url_for('auth.adminLogout'))

        try:
            decoded = jwt.decode(user_token.access_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            expiration_time = datetime.utcfromtimestamp(decoded['exp'])
            
            if datetime.utcnow() <= expiration_time:
                return func(*args, **kwargs)
            else:
                refresh_token(user_token)
                previous_url = session.pop('previous_url', None)
                if current_user.__class__.__name__ == "FISFaculty":
                    return redirect(previous_url or url_for('auth.facultyH'))
                else:
                    return redirect(previous_url or url_for('auth.adminH'))
        
        except jwt.ExpiredSignatureError:
            try:
                decoded_refresh = jwt.decode(user_token.refresh_token, app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
                refresh_expiration_time = datetime.utcfromtimestamp(decoded_refresh['exp'])
                
                if datetime.utcnow() >= refresh_expiration_time:
                    flash('Session Expired. Please Login again.', category='error')
                    if current_user.__class__.__name__ == "FISFaculty":
                        return redirect(url_for('auth.Logout'))
                    else:
                        return redirect(url_for('auth.adminLogout'))
                else:
                    refresh_token(user_token)
                    previous_url = session.pop('previous_url', None)
                    if current_user.__class__.__name__ == "FISFaculty":
                        return redirect(previous_url or url_for('auth.facultyH'))
                    else:
                        return redirect(previous_url or url_for('auth.adminH'))
            
            except jwt.ExpiredSignatureError:
                flash('Session Expired. Please Login again.', category='error')
                if current_user.__class__.__name__ == "FISFaculty":
                    return redirect(url_for('auth.Logout'))
                else:
                    return redirect(url_for('auth.adminLogout'))
            
            except jwt.InvalidTokenError:
                flash('Invalid Token. Please Login again.', category='error')
                if current_user.__class__.__name__ == "FISFaculty":
                    return redirect(url_for('auth.Logout'))
                else:
                    return redirect(url_for('auth.adminLogout'))
        
        except Exception as e:
            print(f'Error: {str(e)}')
            if current_user.__class__.__name__ == "FISFaculty":
                return redirect(url_for('views.home'))
            else:
                return redirect(url_for('views.home'))
    
    return decorated


# REFRESH TOKEN
def refresh_token(user_token):
    refresh_token = user_token.refresh_token
    try:
        decoded_refresh_token = jwt.decode(refresh_token, app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
        user_id = decoded_refresh_token['user_id']

        new_access_token = generate_access_token(user_id)
        
        if current_user.__class__.__name__ == "FISFaculty":
            u = update(FISLoginToken)
            u = u.values({"access_token": new_access_token})
            u = u.where(FISLoginToken.FacultyId == current_user.FacultyId)
            db.session.execute(u)
        elif current_user.__class__.__name__ == "FISAdmin":
            u = update(FISLoginToken)
            u = u.values({"access_token": new_access_token})
            u = u.where(FISLoginToken.AdminId == current_user.AdminId)
            db.session.execute(u)
        else:
            # Handle other user types here if needed
            flash('Unknown user type.', category='error')
            if current_user.__class__.__name__ == "FISFaculty":
                return redirect(url_for('auth.Logout'))
            else:
                return redirect(url_for('auth.adminLogout'))
        
        db.session.commit()
        db.session.close()
        
    except jwt.ExpiredSignatureError:
        if current_user.__class__.__name__ == "FISFaculty":
            return redirect(url_for('auth.Logout'))
        else:
            return redirect(url_for('auth.adminLogout'))
    except jwt.InvalidTokenError:
        flash('Invalid User Token. Please Login again.', category='error')
        if current_user.__class__.__name__ == "FISFaculty":
            return redirect(url_for('auth.Logout'))
        else:
            return redirect(url_for('auth.adminLogout'))
        

# ---------------------------------------------------------

# SYSTEM ADMIN CHECK TOKEN EXPIRATION

def SysCheck_Token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        session['previous_url'] = request.url
        
        if current_user.__class__.__name__ == "FISSystemAdmin":
            user_token = FISSystemAdmin.query.filter_by(SystemAdminId=current_user.SystemAdminId).first()
        else:
            # Handle other user types here if needed
            flash('Unknown user type.', category='error')
            return redirect(url_for('views.home'))

        try:
            decoded = jwt.decode(user_token.access_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            expiration_time = datetime.utcfromtimestamp(decoded['exp'])
            
            if datetime.utcnow() <= expiration_time:
                return func(*args, **kwargs)
            else:
                Sysrefresh_token(user_token)
                previous_url = session.pop('previous_url', None)
                if current_user.__class__.__name__ == "FISSystemAdmin":
                    return redirect(previous_url or url_for('auth.sysadminH'))
                else:
                    return redirect(previous_url or url_for('auth.sysadminL'))
        
        except jwt.ExpiredSignatureError:
            try:
                decoded_refresh = jwt.decode(user_token.refresh_token, app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
                refresh_expiration_time = datetime.utcfromtimestamp(decoded_refresh['exp'])
                
                if datetime.utcnow() >= refresh_expiration_time:
                    flash('Session Expired. Please Login again.', category='error')
                    if current_user.__class__.__name__ == "FISSystemAdmin":
                        return redirect(url_for('views.home'))
                    
                else:
                    Sysrefresh_token(user_token)
                    previous_url = session.pop('previous_url', None)
                    if current_user.__class__.__name__ == "FISSystemAdmin":
                        return redirect(previous_url or url_for('auth.sysadminH'))
            
            except jwt.ExpiredSignatureError:
                flash('Session Expired. Please Login again.', category='error')
                if current_user.__class__.__name__ == "FISSystemAdmin":
                    return redirect(url_for('views.home'))
            
            except jwt.InvalidTokenError:
                flash('Invalid Token. Please Login again.', category='error')
                if current_user.__class__.__name__ == "FISSystemAdmin":
                    return redirect(url_for('views.home'))
        
        except Exception as e:
            print(f'Error: {str(e)}')
            if current_user.__class__.__name__ == "FISSystemAdmin":
                return redirect(url_for('views.home'))
    
    return decorated


# REFRESH TOKEN
def Sysrefresh_token(user_token):
    refresh_token = user_token.refresh_token
    try:
        decoded_refresh_token = jwt.decode(refresh_token, app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
        user_id = decoded_refresh_token['user_id']

        new_access_token = generate_access_token(user_id)
        
        if current_user.__class__.__name__ == "FISSystemAdmin":
            u = update(FISSystemAdmin)
            u = u.values({"access_token": new_access_token})
            u = u.where(FISSystemAdmin.SystemAdminId == current_user.SystemAdminId)
            db.session.execute(u)
        else:
            # Handle other user types here if needed
            flash('Unknown user type.', category='error')
            if current_user.__class__.__name__ == "FISSystemAdmin":
                return redirect(url_for('views.home'))
        
        db.session.commit()
        db.session.close()
        
    except jwt.ExpiredSignatureError:
        if current_user.__class__.__name__ == "FISSystemAdmin":
            return redirect(url_for('views.home'))
    
    except jwt.InvalidTokenError:
        flash('Invalid User Token. Please Login again.', category='error')
        if current_user.__class__.__name__ == "FISSystemAdmin":
            return redirect(url_for('views.home'))

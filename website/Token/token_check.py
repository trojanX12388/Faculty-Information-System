from flask import Flask, redirect, url_for, flash, session, request
from datetime import datetime
import jwt
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['REFRESH_TOKEN_SECRET'] = os.getenv('REFRESH_TOKEN_SECRET')

from website.models import Login_Token
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
        user_token = Login_Token.query.filter_by(faculty_account_id=current_user.faculty_account_id).first()
        try:
            decoded = jwt.decode(user_token.access_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            expiration_time = datetime.utcfromtimestamp(decoded['exp'])
            if datetime.utcnow() <= expiration_time:
                # print(expiration_time)
                # print(datetime.utcnow())
                return func(*args, **kwargs)
            else:
                refresh_token(user_token)
                # print("TOKEN REFRESHED")
                previous_url = session.pop('previous_url', None)
                return redirect(previous_url or url_for('auth.facultyH'))
        except jwt.ExpiredSignatureError:
            try:
                decoded_refresh = jwt.decode(user_token.refresh_token, app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
                refresh_expiration_time = datetime.utcfromtimestamp(decoded_refresh['exp'])
                if datetime.utcnow() >= refresh_expiration_time:
                    # Both access and refresh tokens are expired
                    # Invalidating user's authentication or logging them out
                    
                    # flash('Tokens Expired. Please Login again.', category='error')
                    flash('Session Expired. Please Login again.', category='error')
                    return redirect(url_for('auth.Logout'))
                else:
                    refresh_token(user_token)
                    # print("ACCESS TOKEN EXPIRED, REFRESHED")
                    previous_url = session.pop('previous_url', None)
                    return redirect(previous_url or url_for('auth.facultyH'))
            except jwt.ExpiredSignatureError:
                # Both access and refresh tokens are expired
                # Invalidating user's authentication or logging them out
                flash('Session Expired. Please Login again.', category='error')
                return redirect(url_for('auth.Logout'))
            except jwt.InvalidTokenError:
                # Invalid refresh token
                flash('Invalid Token. Please Login again.', category='error')
                return redirect(url_for('auth.Logout'))
    return decorated


# REFRESH TOKEN
def refresh_token(user_token):
    refresh_token = user_token.refresh_token
    try:
        decoded_refresh_token = jwt.decode(refresh_token, app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
        user_id = decoded_refresh_token['user_id']

        new_access_token = generate_access_token(user_id)
        # print(new_access_token)
        
        u = update(Login_Token)
        u = u.values({"access_token": new_access_token})
        u = u.where(Login_Token.faculty_account_id == current_user.faculty_account_id)
        db.session.execute(u)
        db.session.commit()
        db.session.close()
        
    except jwt.ExpiredSignatureError:
        return redirect(url_for('auth.Logout'))
    except jwt.InvalidTokenError:
        flash('Invalid User Token. Please Login again.', category='error')
        return redirect(url_for('auth.Logout'))
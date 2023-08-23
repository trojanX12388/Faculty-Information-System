from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)


@auth.route("/admin-login")
def adminL():
    return ("<h1>Admin Login</h1>")


@auth.route("/faculty-login")
def facultyL():
    return ("<h1>Faculty Login</h1>")


@auth.route("/logout")
def Logout():
    return ("<h1>Logged Out</h1>")


@auth.route("/sign-up")
def signUp():
    return ("<h1>Sign Up</h1>")
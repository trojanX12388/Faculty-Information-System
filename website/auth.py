from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)


@auth.route("/")
def home():
    return render_template("Welcome-Page/index.html", name="Andrew")
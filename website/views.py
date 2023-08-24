from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route("/", methods=['GET', 'POST'])
def home():
    return render_template("Welcome-Page/index.html")


@views.route("/faculty-home-page", methods=['GET', 'POST'])
def facultyH():
    return render_template("Faculty-Home-Page/home.html")
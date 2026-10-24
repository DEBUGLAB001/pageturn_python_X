from flask import Blueprint, render_template

view_bp = Blueprint("view", __name__)

@view_bp.route("/")
def index():
    return render_template("index.html")

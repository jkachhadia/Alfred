from flask import render_template,jsonify,request
from . import main


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

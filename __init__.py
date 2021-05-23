from flask import Flask
from datetime import timedelta
import main

def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    app.secret_key = "tan the man"
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.config["MAX_CONTENT_LENGTH"] = 10000000
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)
    app.register_blueprint(main.main)
    return app

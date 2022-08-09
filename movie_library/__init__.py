import os
from flask import Flask 
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect
from movie_library.routes import pages

load_dotenv()



def create_app():
    app = Flask(__name__)
    
    app.config['RECAPTCHA_PUBLIC_KEY']  = os.environ.get("RECAPTCHA_PUBLIC_KEY")
    app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get("RECAPTCHA_PRIVATE_KEY")
    app.config['RECAPTCHA_OPTIONS']= {'theme':'black'}
    app.config['TESTING']= False
    
    app.config["MONGODB_URI"]   = os.environ.get("MONGODB_URI")
    app.config["SECRET_KEY"]    =   os.environ.get(
        "SECRET_KEY", os.environ.get("A_SECRET_KEY")
    )
    app.db  =   MongoClient(app.config["MONGODB_URI"]).get_default_database()
    
    csrf = CSRFProtect(app)
    csrf.init_app(app)
    
    app.register_blueprint(pages)
    
    return app
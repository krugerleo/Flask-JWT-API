from flask import Flask
import os
from src.database import db
from src.auth import auth
from flask_jwt_extended import JWTManager
def create_app(config=None):
    app = Flask(__name__,instance_relative_config=True)   

    if config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
        )
    else:
        app.config.from_mapping(config)

    db.app=app        
    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth)

    return app
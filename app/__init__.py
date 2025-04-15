from flask import Flask
from app.config import Config
from app.models import db, bcrypt
from app.routes.auth_routes import auth_bp
from flask_jwt_extended import JWTManager
from app.routes.event_routes import events_bp
from flask_mail import Mail
from flask_cors import CORS
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    # Mail.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(events_bp, url_prefix='/api/events')

    return app

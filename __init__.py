"""
AI-Powered Chatbot for Customer Support
Application factory.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    default_db_uri = "sqlite:///" + os.path.join(basedir, "instance", "chatbot.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", default_db_uri)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

    db.init_app(app)

    from app.chat_routes import chat_bp
    from app.admin_routes import admin_bp

    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app

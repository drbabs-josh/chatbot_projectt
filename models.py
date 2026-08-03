"""
Database models corresponding to the ERD described in Chapter Four:
USER, KNOWLEDGE_BASE, RESPONSE (interaction log), ADMIN_LOG.
"""
from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="admin")  # admin / staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class KnowledgeBase(db.Model):
    __tablename__ = "knowledge_base"

    id = db.Column(db.Integer, primary_key=True)
    intent_label = db.Column(db.String(60), nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), nullable=False)  # Billing, Technical, Account, General
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # MySQL ON UPDATE CURRENT_TIMESTAMP equivalent, portable across SQLite/MySQL via SQLAlchemy
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Response(db.Model):
    """Interaction log: one row per chatbot exchange."""
    __tablename__ = "response"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(80), nullable=False, index=True)
    query_text = db.Column(db.Text, nullable=False)
    intent_label = db.Column(db.String(60))
    confidence_score = db.Column(db.Float)
    response_text = db.Column(db.Text)
    escalated = db.Column(db.Boolean, default=False)
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5, nullable if not rated
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class AdminLog(db.Model):
    __tablename__ = "admin_log"

    id = db.Column(db.Integer, primary_key=True)
    admin_username = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

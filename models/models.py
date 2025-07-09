"""
Database models for the application.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class RequestedUser(db.Model):
    """
    Model for requested GitHub users.
    """
    __tablename__ = 'requested_users'
    
    username = db.Column(db.String(80), primary_key=True, nullable=False)
    year = db.Column(db.Integer, primary_key=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<RequestedUser {self.username}:{self.year}>'


class UserContext(db.Model):
    """
    Model for storing user context data.
    """
    __tablename__ = 'user_contexts'
    
    username = db.Column(db.String(80), primary_key=True, nullable=False)
    year = db.Column(db.Integer, primary_key=True, nullable=False)
    context = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<UserContext {self.username}:{self.year}>'

from models.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SMTPConfig(db.Model):
    """SMTP configuration model"""
    __tablename__ = 'smtp_config'
    
    id = db.Column(db.Integer, primary_key=True)
    smtp_server = db.Column(db.String(255), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    use_tls = db.Column(db.Boolean, default=True)
    sender_email = db.Column(db.String(255), nullable=False)
    sender_password = db.Column(db.String(255), nullable=False)
    timeout = db.Column(db.Integer, default=30)
    retry_times = db.Column(db.Integer, default=3)
    default_recipients = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailTemplate(db.Model):
    """Email template model"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    variables = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used = db.Column(db.DateTime)


class SendRecord(db.Model):
    """Send record model"""
    __tablename__ = 'send_records'
    
    id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(255))
    recipients = db.Column(db.Text, nullable=False)
    cc = db.Column(db.Text)
    bcc = db.Column(db.Text)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    error_msg = db.Column(db.Text)
    trigger_source = db.Column(db.String(50))
    variables_used = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer)


class SystemLog(db.Model):
    """System log model"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
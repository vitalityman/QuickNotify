from flask import Blueprint, request, jsonify, session
from models.database import db
from models.models import SMTPConfig
from utils.crypto import CryptoHandler
from utils.mail_sender import MailSender
import json
import logging

config_bp = Blueprint('config', __name__)
logger = logging.getLogger(__name__)
crypto = CryptoHandler()

def login_required(f):
    """Login required decorator"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function


@config_bp.route('/smtp', methods=['GET'])
@login_required
def get_smtp_config():
    """Get SMTP configuration"""
    config = SMTPConfig.query.first()
    
    if not config:
        return jsonify({'message': 'No configuration found'}), 200
    
    return jsonify({
        'id': config.id,
        'smtp_server': config.smtp_server,
        'smtp_port': config.smtp_port,
        'use_tls': config.use_tls,
        'sender_email': config.sender_email,
        'timeout': config.timeout,
        'retry_times': config.retry_times,
        'default_recipients': json.loads(config.default_recipients or '[]'),
        'updated_at': config.updated_at.isoformat()
    }), 200


@config_bp.route('/smtp', methods=['POST'])
@login_required
def update_smtp_config():
    """Update SMTP configuration"""
    data = request.get_json()
    
    try:
        config = SMTPConfig.query.first()
        
        if not config:
            config = SMTPConfig()
        
        config.smtp_server = data.get('smtp_server')
        config.smtp_port = data.get('smtp_port')
        config.use_tls = data.get('use_tls', True)
        config.sender_email = data.get('sender_email')
        
        password = data.get('sender_password')
        if password:
            config.sender_password = crypto.encrypt(password)
        
        config.timeout = data.get('timeout', 30)
        config.retry_times = data.get('retry_times', 3)
        config.default_recipients = json.dumps(data.get('default_recipients', []))
        
        db.session.add(config)
        db.session.commit()
        
        logger.info(f'SMTP config updated by user {session.get("username")}')
        return jsonify({'message': 'SMTP configuration saved'}), 200
    
    except Exception as e:
        logger.error(f'Error updating SMTP config: {str(e)}')
        return jsonify({'error': f'Save failed: {str(e)}'}), 500


@config_bp.route('/smtp/test', methods=['POST'])
@login_required
def test_smtp_connection():
    """Test SMTP connection"""
    config = SMTPConfig.query.first()
    
    if not config:
        return jsonify({'error': 'SMTP not configured'}), 400
    
    decrypted_password = crypto.decrypt(config.sender_password)
    config.sender_password = decrypted_password
    
    sender = MailSender(config)
    result = sender.test_connection()
    
    logger.info(f'SMTP test by user {session.get("username")}: {result["message"]}')
    return jsonify(result), 200 if result['success'] else 400
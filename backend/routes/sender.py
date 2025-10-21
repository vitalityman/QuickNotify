from flask import Blueprint, request, jsonify, session
from models.database import db
from models.models import SendRecord, EmailTemplate, SMTPConfig
from utils.mail_sender import MailSender
from utils.crypto import CryptoHandler
from datetime import datetime
import json
import logging

sender_bp = Blueprint('sender', __name__)
logger = logging.getLogger(__name__)
crypto = CryptoHandler()

def login_required(f):
    """Login required decorator"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function


@sender_bp.route('/send', methods=['POST'])
@login_required
def send_email():
    """Send email directly"""
    data = request.get_json()
    
    recipients = data.get('recipients', [])
    cc = data.get('cc', [])
    bcc = data.get('bcc', [])
    subject = data.get('subject', '')
    content = data.get('content', '')
    template_name = data.get('template_name')
    
    if not recipients or not subject or not content:
        return jsonify({'error': 'Recipients, subject, and content required'}), 400
    
    smtp_config = SMTPConfig.query.first()
    if not smtp_config:
        return jsonify({'error': 'SMTP not configured'}), 400
    
    decrypted_password = crypto.decrypt(smtp_config.sender_password)
    smtp_config.sender_password = decrypted_password
    
    sender = MailSender(smtp_config)
    result = sender.send_email(
        recipients=recipients,
        subject=subject,
        content=content,
        cc=cc or None,
        bcc=bcc or None,
        is_markdown=True
    )
    
    record = SendRecord(
        template_name=template_name,
        recipients=json.dumps(recipients),
        cc=json.dumps(cc) if cc else None,
        bcc=json.dumps(bcc) if bcc else None,
        subject=subject,
        content=content,
        status='success' if result['success'] else 'failed',
        error_msg=result.get('message') if not result['success'] else None,
        trigger_source='web',
        variables_used=json.dumps({}),
        sent_at=result.get('timestamp') if result['success'] else None,
        duration=result.get('duration')
    )
    
    db.session.add(record)
    db.session.commit()
    
    logger.info(f'Email sent: {result["message"]}')
    
    return jsonify({
        'message': result['message'],
        'success': result['success'],
        'record_id': record.id,
        'duration': result.get('duration')
    }), 200 if result['success'] else 500


@sender_bp.route('/send-from-template', methods=['POST'])
@login_required
def send_from_template():
    """Send email using template"""
    data = request.get_json()
    
    template_id = data.get('template_id')
    recipients = data.get('recipients', [])
    cc = data.get('cc', [])
    bcc = data.get('bcc', [])
    variables = data.get('variables', {})
    
    if not template_id or not recipients:
        return jsonify({'error': 'Template ID and recipients required'}), 400
    
    template = EmailTemplate.query.get(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    mail_sender_temp = MailSender.__new__(MailSender)
    subject = mail_sender_temp.replace_variables(template.subject, variables)
    content = mail_sender_temp.replace_variables(template.content, variables)
    
    smtp_config = SMTPConfig.query.first()
    if not smtp_config:
        return jsonify({'error': 'SMTP not configured'}), 400
    
    decrypted_password = crypto.decrypt(smtp_config.sender_password)
    smtp_config.sender_password = decrypted_password
    
    sender = MailSender(smtp_config)
    result = sender.send_email(
        recipients=recipients,
        subject=subject,
        content=content,
        cc=cc or None,
        bcc=bcc or None,
        is_markdown=True
    )
    
    record = SendRecord(
        template_name=template.name,
        recipients=json.dumps(recipients),
        cc=json.dumps(cc) if cc else None,
        bcc=json.dumps(bcc) if bcc else None,
        subject=subject,
        content=content,
        status='success' if result['success'] else 'failed',
        error_msg=result.get('message') if not result['success'] else None,
        trigger_source='web',
        variables_used=json.dumps(variables),
        sent_at=result.get('timestamp') if result['success'] else None,
        duration=result.get('duration')
    )
    
    db.session.add(record)
    db.session.commit()
    
    template.last_used = datetime.utcnow()
    db.session.commit()
    
    logger.info(f'Email sent from template {template.name}')
    
    return jsonify({
        'message': result['message'],
        'success': result['success'],
        'record_id': record.id,
        'duration': result.get('duration')
    }), 200 if result['success'] else 500
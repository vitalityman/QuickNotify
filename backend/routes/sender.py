from flask import Blueprint, request, jsonify, session
from models.database import db
from models.models import SendRecord, EmailTemplate, SMTPConfig
from utils.mail_sender import MailSender
from utils.crypto import CryptoHandler
from utils.decorators import login_required
from datetime import datetime
import json
import logging

sender_bp = Blueprint('sender', __name__)
logger = logging.getLogger(__name__)
crypto = CryptoHandler()

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
    
    try:
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
            sent_at=datetime.utcnow() if result['success'] else None,
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
        }), 200 if result['success'] else 400
    
    except Exception as e:
        logger.error(f'Error sending email: {str(e)}')
        return jsonify({'error': f'Error: {str(e)}'}), 500


@sender_bp.route('/send-from-template', methods=['POST'])
@login_required
def send_from_template():
    """Send email using template"""
    try:
        data = request.get_json()
        logger.info(f'Send from template request: {data}')
        
        template_id = data.get('template_id')
        recipients = data.get('recipients', [])
        cc = data.get('cc', [])
        bcc = data.get('bcc', [])
        variables = data.get('variables', {})
        
        logger.info(f'Parameters - template_id: {template_id}, recipients: {recipients}')
        
        if not template_id or not recipients:
            logger.warning('Missing template_id or recipients')
            return jsonify({'error': 'Template ID and recipients required'}), 400
        
        # 获取模板
        template = EmailTemplate.query.get(template_id)
        if not template:
            logger.warning(f'Template not found: {template_id}')
            return jsonify({'error': 'Template not found'}), 404
        
        logger.info(f'Template found: {template.name}')
        
        # 替换变量
        subject = template.subject
        content = template.content
        
        logger.info(f'Original subject: {subject}')
        logger.info(f'Variables: {variables}')
        
        # 替换主题中的变量
        for key, value in variables.items():
            subject = subject.replace(f'{{{{{key}}}}}', str(value))
            content = content.replace(f'{{{{{key}}}}}', str(value))
        
        logger.info(f'Replaced subject: {subject}')
        
        # 获取SMTP配置
        smtp_config = SMTPConfig.query.first()
        if not smtp_config:
            logger.error('SMTP not configured')
            return jsonify({'error': 'SMTP not configured'}), 400
        
        # 发送邮件
        try:
            decrypted_password = crypto.decrypt(smtp_config.sender_password)
            smtp_config.sender_password = decrypted_password
            
            sender = MailSender(smtp_config)
            result = sender.send_email(
                recipients=recipients,
                subject=subject,
                content=content,
                cc=cc if cc else None,
                bcc=bcc if bcc else None,
                is_markdown=True
            )
            
            logger.info(f'Send result: {result}')
            
            # 保存记录
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
                sent_at=datetime.utcnow() if result['success'] else None,
                duration=result.get('duration')
            )
            
            db.session.add(record)
            db.session.commit()
            
            logger.info(f'Record saved: {record.id}')
            
            return jsonify({
                'message': result['message'],
                'success': result['success'],
                'record_id': record.id,
                'duration': result.get('duration')
            }), 200 if result['success'] else 400
        
        except Exception as send_error:
            logger.error(f'Error in send_email: {str(send_error)}')
            
            # 即使发送出错，也尝试保存记录
            try:
                record = SendRecord(
                    template_name=template.name,
                    recipients=json.dumps(recipients),
                    cc=json.dumps(cc) if cc else None,
                    bcc=json.dumps(bcc) if bcc else None,
                    subject=subject,
                    content=content,
                    status='failed',
                    error_msg=str(send_error),
                    trigger_source='web',
                    variables_used=json.dumps(variables),
                    duration=0
                )
                db.session.add(record)
                db.session.commit()
            except Exception as record_error:
                logger.error(f'Error saving record: {str(record_error)}')
            
            raise
    
    except Exception as error:
        logger.error(f'Error in send_from_template: {str(error)}')
        logger.error(f'Error type: {type(error).__name__}')
        import traceback
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(error)
        }), 500
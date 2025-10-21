from flask import Blueprint, request, jsonify, session
from models.database import db
from models.models import SMTPConfig
from utils.crypto import CryptoHandler
from utils.mail_sender import MailSender
from utils.decorators import login_required
import json
import logging

config_bp = Blueprint('config', __name__)
logger = logging.getLogger(__name__)
crypto = CryptoHandler()

@config_bp.route('/smtp', methods=['GET'])
@login_required
def get_smtp_config():
    """Get SMTP configuration"""
    try:
        config = SMTPConfig.query.first()
        
        if not config:
            logger.info('No SMTP configuration found')
            return jsonify({'message': 'No configuration found'}), 200
        
        logger.info('SMTP configuration retrieved')
        return jsonify({
            'id': config.id,
            'smtp_server': config.smtp_server,
            'smtp_port': config.smtp_port,
            'use_tls': config.use_tls,
            'sender_email': config.sender_email,
            'timeout': config.timeout,
            'retry_times': config.retry_times,
            'updated_at': config.updated_at.isoformat() if config.updated_at else None
        }), 200
    except Exception as e:
        logger.error(f'Error getting SMTP config: {str(e)}')
        return jsonify({'error': f'Error: {str(e)}'}), 500


@config_bp.route('/smtp', methods=['POST'])
@login_required
def update_smtp_config():
    """Update SMTP configuration"""
    try:
        data = request.get_json()
        logger.info(f'Updating SMTP config with data: {data}')
        
        # 验证必填字段
        if not data.get('smtp_server') or not data.get('smtp_port') or not data.get('sender_email'):
            logger.warning('Missing required SMTP fields')
            return jsonify({'error': 'Missing required fields: smtp_server, smtp_port, sender_email'}), 400
        
        if not data.get('sender_password'):
            logger.warning('Missing sender password')
            return jsonify({'error': 'sender_password is required'}), 400
        
        # 获取或创建SMTP配置
        config = SMTPConfig.query.first()
        
        if not config:
            config = SMTPConfig()
            logger.info('Creating new SMTP configuration')
        
        # 更新配置
        config.smtp_server = data.get('smtp_server')
        config.smtp_port = data.get('smtp_port')
        config.use_tls = data.get('use_tls', True)
        config.sender_email = data.get('sender_email')
        config.timeout = data.get('timeout', 30)
        config.retry_times = data.get('retry_times', 3)
        
        # 加密并保存密码
        password = data.get('sender_password')
        if password:
            config.sender_password = crypto.encrypt(password)
            logger.info('Password encrypted and saved')
        
        # 保存到数据库
        db.session.add(config)
        db.session.commit()
        
        logger.info(f'SMTP config updated successfully by user {session.get("username")}')
        return jsonify({'message': 'SMTP configuration saved successfully'}), 200
    
    except Exception as e:
        logger.error(f'Error updating SMTP config: {str(e)}')
        db.session.rollback()
        return jsonify({'error': f'Save failed: {str(e)}'}), 500


@config_bp.route('/smtp/test', methods=['POST'])
@login_required
def test_smtp_connection():
    """Test SMTP connection"""
    try:
        logger.info('Testing SMTP connection...')
        
        config = SMTPConfig.query.first()
        
        if not config:
            logger.warning('SMTP configuration not found for test')
            return jsonify({
                'success': False,
                'message': 'SMTP configuration not configured yet'
            }), 400
        
        # 验证配置完整性
        if not config.smtp_server or not config.smtp_port or not config.sender_email:
            logger.warning('SMTP configuration incomplete')
            return jsonify({
                'success': False,
                'message': 'SMTP configuration is incomplete'
            }), 400
        
        # 解密密码
        try:
            decrypted_password = crypto.decrypt(config.sender_password)
        except Exception as e:
            logger.error(f'Error decrypting password: {str(e)}')
            return jsonify({
                'success': False,
                'message': 'Error decrypting SMTP password'
            }), 400
        
        # 创建临时配置对象用于测试
        config.sender_password = decrypted_password
        
        # 测试连接
        sender = MailSender(config)
        result = sender.test_connection()
        
        logger.info(f'SMTP test result: {result}')
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'SMTP connection successful ✅'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'SMTP connection failed')
            }), 400
    
    except Exception as e:
        logger.error(f'Error testing SMTP connection: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Connection test failed: {str(e)}'
        }), 500
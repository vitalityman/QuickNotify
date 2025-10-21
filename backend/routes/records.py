from flask import Blueprint, request, jsonify, session
from models.database import db
from models.models import SendRecord
from utils.decorators import login_required
from datetime import datetime, timedelta
import json
import logging

records_bp = Blueprint('records', __name__)
logger = logging.getLogger(__name__)

# 删除 login_required 定义

@records_bp.route('/', methods=['GET'])
@login_required
def list_records():
    """Get send records list"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', 'all', type=str)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    search = request.args.get('search', '', type=str)
    
    query = SendRecord.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(SendRecord.created_at >= start)
    
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(SendRecord.created_at < end)
    
    if search:
        query = query.filter(
            (SendRecord.recipients.like(f'%{search}%')) |
            (SendRecord.subject.like(f'%{search}%'))
        )
    
    query = query.order_by(SendRecord.created_at.desc())
    paginated = query.paginate(page=page, per_page=per_page)
    
    records = [{
        'id': r.id,
        'template_name': r.template_name,
        'recipients': json.loads(r.recipients or '[]'),
        'subject': r.subject,
        'status': r.status,
        'trigger_source': r.trigger_source,
        'created_at': r.created_at.isoformat(),
        'sent_at': r.sent_at.isoformat() if r.sent_at else None,
        'duration': r.duration,
        'error_msg': r.error_msg
    } for r in paginated.items]
    
    return jsonify({
        'records': records,
        'total': paginated.total,
        'page': page,
        'per_page': per_page
    }), 200


@records_bp.route('/<int:record_id>', methods=['GET'])
@login_required
def get_record_detail(record_id):
    """Get send record detail"""
    record = SendRecord.query.get(record_id)
    
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    
    return jsonify({
        'id': record.id,
        'template_name': record.template_name,
        'recipients': json.loads(record.recipients or '[]'),
        'cc': json.loads(record.cc or '[]'),
        'bcc': json.loads(record.bcc or '[]'),
        'subject': record.subject,
        'content': record.content,
        'status': record.status,
        'error_msg': record.error_msg,
        'trigger_source': record.trigger_source,
        'variables_used': json.loads(record.variables_used or '{}'),
        'created_at': record.created_at.isoformat(),
        'sent_at': record.sent_at.isoformat() if record.sent_at else None,
        'duration': record.duration
    }), 200


@records_bp.route('/<int:record_id>/retry', methods=['POST'])
@login_required
def retry_send(record_id):
    """Retry failed send"""
    from models.models import SMTPConfig
    from utils.mail_sender import MailSender
    from utils.crypto import CryptoHandler
    
    record = SendRecord.query.get(record_id)
    
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    
    if record.status == 'success':
        return jsonify({'error': 'Success record cannot be retried'}), 400
    
    smtp_config = SMTPConfig.query.first()
    if not smtp_config:
        return jsonify({'error': 'SMTP not configured'}), 400
    
    crypto = CryptoHandler()
    decrypted_password = crypto.decrypt(smtp_config.sender_password)
    smtp_config.sender_password = decrypted_password
    
    sender = MailSender(smtp_config)
    result = sender.send_email(
        recipients=json.loads(record.recipients),
        subject=record.subject,
        content=record.content,
        cc=json.loads(record.cc or '[]') or None,
        bcc=json.loads(record.bcc or '[]') or None,
        is_markdown=True
    )
    
    if result['success']:
        record.status = 'success'
        record.sent_at = datetime.utcnow()
        record.duration = result['duration']
        record.error_msg = None
    else:
        record.status = 'failed'
        record.error_msg = result['message']
    
    db.session.commit()
    
    logger.info(f'Record {record_id} retry: {result["message"]}')
    return jsonify(result), 200 if result['success'] else 500


@records_bp.route('/<int:record_id>', methods=['DELETE'])
@login_required
def delete_record(record_id):
    """Delete send record"""
    record = SendRecord.query.get(record_id)
    
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    
    db.session.delete(record)
    db.session.commit()
    
    logger.info(f'Record {record_id} deleted')
    return jsonify({'message': 'Record deleted'}), 200


@records_bp.route('/stats', methods=['GET'])
@login_required
def get_statistics():
    """Get send statistics"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    today_total = SendRecord.query.filter(
        SendRecord.created_at >= today_start,
        SendRecord.created_at < today_end
    ).count()
    
    today_success = SendRecord.query.filter(
        SendRecord.status == 'success',
        SendRecord.created_at >= today_start,
        SendRecord.created_at < today_end
    ).count()
    
    today_failed = today_total - today_success
    
    week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    week_total = SendRecord.query.filter(
        SendRecord.created_at >= week_start
    ).count()
    
    week_success = SendRecord.query.filter(
        SendRecord.status == 'success',
        SendRecord.created_at >= week_start
    ).count()
    
    total_all = SendRecord.query.count()
    total_success = SendRecord.query.filter_by(status='success').count()
    total_failed = total_all - total_success
    
    return jsonify({
        'today': {
            'total': today_total,
            'success': today_success,
            'failed': today_failed,
            'success_rate': (today_success / today_total * 100) if today_total > 0 else 0
        },
        'week': {
            'total': week_total,
            'success': week_success,
            'failed': week_total - week_success,
            'success_rate': (week_success / week_total * 100) if week_total > 0 else 0
        },
        'total': {
            'total': total_all,
            'success': total_success,
            'failed': total_failed,
            'success_rate': (total_success / total_all * 100) if total_all > 0 else 0
        }
    }), 200
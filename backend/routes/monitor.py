from flask import Blueprint, request, jsonify, session, send_file
from models.models import SendRecord
from datetime import datetime, timedelta
import psutil
import os
import logging
import io

monitor_bp = Blueprint('monitor', __name__)
logger = logging.getLogger(__name__)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function


@monitor_bp.route('/status', methods=['GET'])
@login_required
def get_system_status():
    """Get system running status"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        current_process = psutil.Process(os.getpid())
        process_memory = current_process.memory_info().rss / (1024 * 1024)
        process_cpu = current_process.cpu_percent(interval=1)
        
        return jsonify({
            'status': 'running',
            'cpu_percent': cpu_percent,
            'memory': {
                'total': memory.total / (1024 ** 3),
                'used': memory.used / (1024 ** 3),
                'percent': memory.percent
            },
            'process': {
                'memory_mb': process_memory,
                'cpu_percent': process_cpu
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f'Error getting system status: {str(e)}')
        return jsonify({'error': f'Failed to get system status: {str(e)}'}), 500


@monitor_bp.route('/logs', methods=['GET'])
@login_required
def get_system_logs():
    """Get system logs"""
    level = request.args.get('level', 'ALL', type=str)
    lines = request.args.get('lines', 100, type=int)
    
    log_file = 'logs/app.log'
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                all_logs = f.readlines()
            
            if level != 'ALL':
                all_logs = [log for log in all_logs if level in log]
            
            logs = all_logs[-lines:]
            
            return jsonify({
                'logs': logs,
                'total_lines': len(logs),
                'level': level
            }), 200
        else:
            return jsonify({'logs': [], 'total_lines': 0}), 200
    
    except Exception as e:
        logger.error(f'Error reading logs: {str(e)}')
        return jsonify({'error': f'Failed to read logs: {str(e)}'}), 500


@monitor_bp.route('/stats/daily', methods=['GET'])
@login_required
def get_daily_stats():
    """Get daily statistics"""
    days = request.args.get('days', 7, type=int)
    
    stats = []
    for i in range(days - 1, -1, -1):
        date = (datetime.utcnow() - timedelta(days=i)).date()
        date_start = datetime.combine(date, datetime.min.time())
        date_end = date_start + timedelta(days=1)
        
        total = SendRecord.query.filter(
            SendRecord.created_at >= date_start,
            SendRecord.created_at < date_end
        ).count()
        
        success = SendRecord.query.filter(
            SendRecord.status == 'success',
            SendRecord.created_at >= date_start,
            SendRecord.created_at < date_end
        ).count()
        
        stats.append({
            'date': date.isoformat(),
            'total': total,
            'success': success,
            'failed': total - success,
            'success_rate': (success / total * 100) if total > 0 else 0
        })
    
    return jsonify({'stats': stats}), 200


@monitor_bp.route('/stats/sources', methods=['GET'])
@login_required
def get_trigger_sources_stats():
    """Get trigger sources statistics"""
    sources = {}
    
    for record in SendRecord.query.all():
        source = record.trigger_source or 'unknown'
        if source not in sources:
            sources[source] = {'total': 0, 'success': 0}
        
        sources[source]['total'] += 1
        if record.status == 'success':
            sources[source]['success'] += 1
    
    stats = []
    for source, data in sources.items():
        stats.append({
            'source': source,
            'total': data['total'],
            'success': data['success'],
            'failed': data['total'] - data['success'],
            'success_rate': (data['success'] / data['total'] * 100) if data['total'] > 0 else 0
        })
    
    return jsonify({'stats': stats}), 200
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import config
from models.database import db, init_db
from models import User
from routes.auth import auth_bp, init_default_user
from routes.config import config_bp
from routes.template import template_bp
from routes.sender import sender_bp
from routes.records import records_bp
from routes.monitor import monitor_bp
from utils import setup_logging
import os
import logging
from datetime import datetime

# 获取配置环境
config_env = os.environ.get('FLASK_ENV', 'development')
app_config = config[config_env]

# 创建Flask应用
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config.from_object(app_config)

# 初始化CORS
CORS(app, supports_credentials=True)

# 初始化数据库
db.init_app(app)

# 设置日志
logger = setup_logging(app)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(config_bp, url_prefix='/api/config')
app.register_blueprint(template_bp, url_prefix='/api/template')
app.register_blueprint(sender_bp, url_prefix='/api/sender')
app.register_blueprint(records_bp, url_prefix='/api/records')
app.register_blueprint(monitor_bp, url_prefix='/api/monitor')

# 应用上下文
with app.app_context():
    try:
        db.create_all()
        init_default_user()
        logger.info('Database initialized successfully')
    except Exception as e:
        logger.error(f'Error initializing database: {str(e)}')


# ============ 主页路由 ============
@app.route('/')
@app.route('/index.html')
def index():
    """Serve index page"""
    return send_from_directory('../frontend', 'index.html')


# ============ 静态文件路由 ============
@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    return send_from_directory('../frontend/css', filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    return send_from_directory('../frontend/js', filename)


# ============ API健康检查 ============
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'QuickNotify is running'
    }), 200


# ============ 错误处理 ============
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not Found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({'error': 'Method Not Allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f'Internal server error: {error}')
    return jsonify({'error': 'Internal Server Error'}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions"""
    logger.error(f'Unhandled exception: {str(e)}')
    return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = app_config.DEBUG
    
    logger.info(f'Starting QuickNotify on port {port} (DEBUG={debug})')
    app.run(host='0.0.0.0', port=port, debug=debug)
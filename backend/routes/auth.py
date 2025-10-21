from flask import Blueprint, request, jsonify, session
from models.database import db
from models.models import User
import os
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def login_required(f):
    """Login required decorator"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        logger.warning(f'Failed login attempt for user: {username}')
        return jsonify({'error': 'Invalid username or password'}), 401
    
    session.permanent = True
    session['user_id'] = user.id
    session['username'] = user.username
    
    logger.info(f'User {username} logged in successfully')
    return jsonify({'message': 'Login successful', 'username': username}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check authentication status"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'username': session.get('username')
        }), 200
    return jsonify({'authenticated': False}), 401


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'error': 'Old and new password required'}), 400
    
    user = User.query.get(session['user_id'])
    
    if not user.check_password(old_password):
        return jsonify({'error': 'Old password incorrect'}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    logger.info(f'User {user.username} changed password')
    return jsonify({'message': 'Password changed successfully'}), 200


def init_default_user():
    """Initialize default user"""
    init_user = os.environ.get('INIT_USER', 'admin')
    init_pwd = os.environ.get('INIT_PWD', '123456')
    
    existing_user = User.query.filter_by(username=init_user).first()
    
    if not existing_user:
        user = User(username=init_user)
        user.set_password(init_pwd)
        db.session.add(user)
        db.session.commit()
        logger.info(f'Default user {init_user} created')
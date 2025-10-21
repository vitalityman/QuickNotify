from flask import jsonify, session
from functools import wraps

def login_required(f):
    """Login required decorator - shared across all routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function
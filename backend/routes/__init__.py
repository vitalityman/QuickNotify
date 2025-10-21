from .auth import auth_bp
from .config import config_bp
from .template import template_bp
from .sender import sender_bp
from .records import records_bp
from .monitor import monitor_bp

__all__ = [
    'auth_bp',
    'config_bp',
    'template_bp',
    'sender_bp',
    'records_bp',
    'monitor_bp'
]
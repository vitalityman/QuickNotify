from flask import Blueprint, request, jsonify, session
from models.database import db
from models.models import EmailTemplate
from utils.decorators import login_required
import json
import logging
import re
from datetime import datetime

template_bp = Blueprint('template', __name__)
logger = logging.getLogger(__name__)

# 删除 login_required 定义

def extract_variables(text):
    """Extract variable names from template text"""
    pattern = r'\{\{(\w+)\}\}'
    return list(set(re.findall(pattern, text)))


@template_bp.route('/', methods=['GET'])
@login_required
def list_templates():
    """Get all email templates"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    
    query = EmailTemplate.query
    
    if search:
        query = query.filter(EmailTemplate.name.like(f'%{search}%'))
    
    paginated = query.paginate(page=page, per_page=per_page)
    
    templates = [{
        'id': t.id,
        'name': t.name,
        'subject': t.subject,
        'created_at': t.created_at.isoformat(),
        'updated_at': t.updated_at.isoformat(),
        'last_used': t.last_used.isoformat() if t.last_used else None,
        'variables': json.loads(t.variables or '[]')
    } for t in paginated.items]
    
    return jsonify({
        'templates': templates,
        'total': paginated.total,
        'page': page,
        'per_page': per_page
    }), 200


@template_bp.route('/<int:template_id>', methods=['GET'])
@login_required
def get_template(template_id):
    """Get single template details"""
    template = EmailTemplate.query.get(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    return jsonify({
        'id': template.id,
        'name': template.name,
        'subject': template.subject,
        'content': template.content,
        'variables': json.loads(template.variables or '[]'),
        'created_at': template.created_at.isoformat(),
        'updated_at': template.updated_at.isoformat()
    }), 200


@template_bp.route('/', methods=['POST'])
@login_required
def create_template():
    """Create new template"""
    data = request.get_json()
    
    name = data.get('name')
    subject = data.get('subject')
    content = data.get('content')
    
    if not name or not subject or not content:
        return jsonify({'error': 'Name, subject, and content required'}), 400
    
    existing = EmailTemplate.query.filter_by(name=name).first()
    if existing:
        return jsonify({'error': 'Template name already exists'}), 400
    
    variables = extract_variables(subject + ' ' + content)
    
    template = EmailTemplate(
        name=name,
        subject=subject,
        content=content,
        variables=json.dumps(variables)
    )
    
    db.session.add(template)
    db.session.commit()
    
    logger.info(f'Template created: {name}')
    return jsonify({
        'message': 'Template created successfully',
        'id': template.id
    }), 201


@template_bp.route('/<int:template_id>', methods=['PUT'])
@login_required
def update_template(template_id):
    """Update template"""
    template = EmailTemplate.query.get(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        existing = EmailTemplate.query.filter(
            EmailTemplate.name == data['name'],
            EmailTemplate.id != template_id
        ).first()
        if existing:
            return jsonify({'error': 'Template name already exists'}), 400
        template.name = data['name']
    
    if 'subject' in data:
        template.subject = data['subject']
    
    if 'content' in data:
        template.content = data['content']
    
    variables = extract_variables(template.subject + ' ' + template.content)
    template.variables = json.dumps(variables)
    
    db.session.commit()
    
    logger.info(f'Template updated: {template.name}')
    return jsonify({'message': 'Template updated'}), 200


@template_bp.route('/<int:template_id>', methods=['DELETE'])
@login_required
def delete_template(template_id):
    """Delete template"""
    template = EmailTemplate.query.get(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    template_name = template.name
    db.session.delete(template)
    db.session.commit()
    
    logger.info(f'Template deleted: {template_name}')
    return jsonify({'message': 'Template deleted'}), 200
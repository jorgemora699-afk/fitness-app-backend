from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.templates.template_use_cases import (
    CreateTemplateUseCase,
    GetMyTemplatesUseCase,
    GetTemplateByIdUseCase,
    UpdateTemplateUseCase,
    DeleteTemplateUseCase,
    AssignTemplateToUserUseCase
)

template_bp = Blueprint('templates', __name__, url_prefix='/api/templates')

def get_role():
    return get_jwt().get('role')

# ── Entrenador: crear plantilla ──
@template_bp.route('/', methods=['POST'])
@jwt_required()
def create_template():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    result, status = CreateTemplateUseCase().execute(trainer_id, data)
    return jsonify(result), status

# ── Entrenador: ver todas sus plantillas ──
@template_bp.route('/', methods=['GET'])
@jwt_required()
def get_templates():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = GetMyTemplatesUseCase().execute(trainer_id)
    return jsonify(result), status

# ── Entrenador: ver una plantilla específica ──
@template_bp.route('/<int:template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = GetTemplateByIdUseCase().execute(template_id, trainer_id)
    return jsonify(result), status

# ── Entrenador: actualizar plantilla ──
@template_bp.route('/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    result, status = UpdateTemplateUseCase().execute(template_id, trainer_id, data)
    return jsonify(result), status

# ── Entrenador: eliminar plantilla ──
@template_bp.route('/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = DeleteTemplateUseCase().execute(template_id, trainer_id)
    return jsonify(result), status

# ── Entrenador: asignar plantilla a uno o varios usuarios ──
@template_bp.route('/<int:template_id>/assign', methods=['POST'])
@jwt_required()
def assign_template(template_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('user_ids') or not data.get('dates'):
        return jsonify({'error': 'Se requieren user_ids y dates'}), 400
    result, status = AssignTemplateToUserUseCase().execute(template_id, trainer_id, data)
    return jsonify(result), status
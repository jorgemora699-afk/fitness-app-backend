from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.progress.progress_use_cases import (
    AddBodyRecordUseCase,
    GetBodyProgressUseCase,
    GetExerciseProgressUseCase,
    GetUserProgressAsTrainerUseCase,
    GetIMCUseCase, 
    DeleteBodyRecordUseCase
)

progress_bp = Blueprint('progress', __name__, url_prefix='/api/progress')

def get_role():
    return get_jwt().get('role')

# ── Usuario: agregar registro de peso corporal ──
@progress_bp.route('/body', methods=['POST'])
@jwt_required()
def add_body_record():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('weight'):
        return jsonify({'error': 'El peso es requerido'}), 400
    result, status = AddBodyRecordUseCase().execute(user_id, data)
    return jsonify(result), status

# ── Usuario: ver su progreso de peso corporal ──
@progress_bp.route('/body/me', methods=['GET'])
@jwt_required()
def get_my_body_progress():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    result, status = GetBodyProgressUseCase().execute(user_id)
    return jsonify(result), status

# ── Usuario: ver su progreso en un ejercicio específico ──
@progress_bp.route('/exercise/me', methods=['GET'])
@jwt_required()
def get_my_exercise_progress():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    exercise_name = request.args.get('name')
    if not exercise_name:
        return jsonify({'error': 'Se requiere el parámetro name'}), 400
    result, status = GetExerciseProgressUseCase().execute(user_id, exercise_name)
    return jsonify(result), status

# ── Usuario: ver su IMC ──
@progress_bp.route('/imc/me', methods=['GET'])
@jwt_required()
def get_my_imc():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    result, status = GetIMCUseCase().execute(user_id)
    return jsonify(result), status

# ── Entrenador: ver progreso completo de un usuario ──
@progress_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_progress(user_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = GetUserProgressAsTrainerUseCase().execute(user_id, trainer_id)
    return jsonify(result), status

# ── Entrenador: ver IMC de un usuario ──
@progress_bp.route('/imc/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_imc(user_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    user = __import__('domain.entities.user', fromlist=['User']).User
    from domain.entities.user import User
    u = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
    if not u:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    result, status = GetIMCUseCase().execute(user_id)
    return jsonify(result), status

# ── Usuario: eliminar registro de peso ──
@progress_bp.route('/body/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_body_record(record_id):
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    result, status = DeleteBodyRecordUseCase().execute(user_id, record_id)
    return jsonify(result), status
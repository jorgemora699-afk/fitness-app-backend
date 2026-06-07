from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.users.user_use_cases import (
    GetMyUsersUseCase,
    GetUserByIdUseCase,
    UpdateUserUseCase,
    AssignTrainerUseCase,
    GetUserProfileUseCase
)

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

def trainer_required():
    claims = get_jwt()
    if claims.get('role') != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    return None

def user_required():
    claims = get_jwt()
    if claims.get('role') != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    return None

# ── Entrenador: ver todos sus usuarios ──
@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_users():
    error = trainer_required()
    if error: return error
    trainer_id = int(get_jwt_identity())
    result, status = GetMyUsersUseCase().execute(trainer_id)
    return jsonify(result), status

# ── Entrenador: ver un usuario específico ──
@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    error = trainer_required()
    if error: return error
    trainer_id = int(get_jwt_identity())
    result, status = GetUserByIdUseCase().execute(user_id, trainer_id)
    return jsonify(result), status

# ── Entrenador: actualizar info de un usuario ──
@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    error = trainer_required()
    if error: return error
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    result, status = UpdateUserUseCase().execute(user_id, trainer_id, data)
    return jsonify(result), status

# ── Entrenador: asignar usuario a su cuenta ──
@user_bp.route('/<int:user_id>/assign', methods=['POST'])
@jwt_required()
def assign_trainer(user_id):
    error = trainer_required()
    if error: return error
    trainer_id = int(get_jwt_identity())
    result, status = AssignTrainerUseCase().execute(user_id, trainer_id)
    return jsonify(result), status

# ── Usuario: ver su propio perfil ──
@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    error = user_required()
    if error: return error
    user_id = int(get_jwt_identity())
    result, status = GetUserProfileUseCase().execute(user_id)
    return jsonify(result), status
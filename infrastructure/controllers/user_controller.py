from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.users.user_use_cases import (
    GetMyUsersUseCase,
    GetUserByIdUseCase,
    UpdateUserUseCase,
    AssignTrainerUseCase,
    GetUserProfileUseCase,
    ChangePasswordUseCase,
    SavePushTokenUseCase,
    ApproveUserUseCase,
    RejectUserUseCase
)
from domain.entities.user import User
from infrastructure.database.db import db

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

# ── Usuario: cambiar contraseña ──
@user_bp.route('/me/password', methods=['PUT'])
@jwt_required()
def change_password():
    error = user_required()
    if error: return error
    user_id = int(get_jwt_identity())
    data = request.get_json()
    result, status = ChangePasswordUseCase().execute(user_id, data)
    return jsonify(result), status

# ── Usuario: guardar push token ──
@user_bp.route('/me/push-token', methods=['POST'])
@jwt_required()
def save_push_token():
    error = user_required()
    if error: return error
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('push_token'):
        return jsonify({'error': 'push_token requerido'}), 400
    result, status = SavePushTokenUseCase().execute(user_id, data['push_token'])
    return jsonify(result), status


@user_bp.route('/me/photo', methods=['POST'])
@jwt_required()
def upload_user_photo():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    if 'photo' not in request.files:
        return jsonify({'error': 'No se envió foto'}), 400

    import cloudinary
    import cloudinary.uploader
    import os
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )
    file = request.files['photo']
    upload = cloudinary.uploader.upload(file, folder='fitness/profiles')
    user.profile_photo = upload.get('secure_url')
    db.session.commit()
    return jsonify({'message': 'Foto actualizada', 'user': user.to_dict()}), 200

@user_bp.route('/me/photo', methods=['DELETE'])
@jwt_required()
def delete_user_photo():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    user.profile_photo = None
    db.session.commit()
    return jsonify({'message': 'Foto eliminada', 'user': user.to_dict()}), 200

@user_bp.route('/<int:user_id>/approve', methods=['PUT'])
@jwt_required()
def approve_user(user_id):

    error = trainer_required()
    if error:
        return error

    trainer_id = int(get_jwt_identity())

    result, status = ApproveUserUseCase().execute(
        user_id,
        trainer_id
    )

    return jsonify(result), status

@user_bp.route('/<int:user_id>/reject', methods=['PUT'])
@jwt_required()
def reject_user(user_id):

    error = trainer_required()
    if error:
        return error

    trainer_id = int(get_jwt_identity())

    result, status = RejectUserUseCase().execute(
        user_id,
        trainer_id
    )

    return jsonify(result), status
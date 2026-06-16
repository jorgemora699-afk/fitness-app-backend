from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from application.use_cases.auth.auth_use_cases import (
    RegisterUserUseCase,
    LoginUserUseCase,
    LoginTrainerUseCase,
    CreateTrainerUseCase, 
    ResetPasswordUseCase,
    SendResetCodeTrainerUseCase,
    ResetPasswordTrainerUseCase
)
from domain.entities.trainer import Trainer
from infrastructure.database.db import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data or not all(k in data for k in ['name', 'last_name', 'email', 'password', 'phone', 'trainer_code']):
        return jsonify({'error': 'Faltan campos requeridos: name, last_name, email, password, phone, trainer_code'}), 400

    result, status = RegisterUserUseCase().execute(data)
    if status == 201:
        token = create_access_token(identity=str(result['user']['id']), additional_claims={'role': 'user'})
        result['token'] = token
    return jsonify(result), status

@auth_bp.route('/login/user', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    result, status = LoginUserUseCase().execute(data['email'], data['password'])
    if status == 200:
        token = create_access_token(identity=str(result['user']['id']), additional_claims={'role': 'user'})
        result['token'] = token
    return jsonify(result), status

@auth_bp.route('/login/trainer', methods=['POST'])
def login_trainer():
    data = request.get_json()
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    result, status = LoginTrainerUseCase().execute(data['email'], data['password'])
    if status == 200:
        token = create_access_token(identity=str(result['trainer']['id']), additional_claims={'role': 'trainer'})
        result['token'] = token
    return jsonify(result), status

@auth_bp.route('/create/trainer', methods=['POST'])
def create_trainer():
    data = request.get_json()
    if not data or not all(k in data for k in ['name', 'email', 'password']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    result, status = CreateTrainerUseCase().execute(data)
    if status == 201:
        token = create_access_token(identity=str(result['trainer']['id']), additional_claims={'role': 'trainer'})
        result['token'] = token
    return jsonify(result), status

@auth_bp.route('/trainers/me', methods=['PUT'])
@jwt_required()
def update_trainer_profile():
    claims = get_jwt()
    if claims.get('role') != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403

    trainer_id = int(get_jwt_identity())
    trainer = Trainer.query.get(trainer_id)
    if not trainer:
        return jsonify({'error': 'Entrenador no encontrado'}), 404

    data = request.get_json()
    trainer.name = data.get('name', trainer.name)
    trainer.phone = data.get('phone', trainer.phone)

    db.session.commit()
    return jsonify({'trainer': trainer.to_dict()}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    result, status = ResetPasswordUseCase().execute(data)
    return jsonify(result), status

# ── Entrenador: solicitar código de recuperación ──
@auth_bp.route('/trainer/forgot-password', methods=['POST'])
def trainer_forgot_password():
    data = request.get_json()
    if not data.get('email'):
        return jsonify({'error': 'El email es requerido'}), 400
    result, status = SendResetCodeTrainerUseCase().execute(data['email'])
    return jsonify(result), status


# ── Entrenador: resetear contraseña con código ──
@auth_bp.route('/trainer/reset-password', methods=['POST'])
def trainer_reset_password():
    data = request.get_json()
    result, status = ResetPasswordTrainerUseCase().execute(data)
    return jsonify(result), status

@auth_bp.route('/trainers/me/photo', methods=['POST'])
@jwt_required()
def upload_trainer_photo():
    claims = get_jwt()
    if claims.get('role') != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    trainer = Trainer.query.get(trainer_id)
    if not trainer:
        return jsonify({'error': 'Entrenador no encontrado'}), 404
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
    trainer.profile_photo = upload.get('secure_url')
    db.session.commit()
    return jsonify({'message': 'Foto actualizada', 'trainer': trainer.to_dict()}), 200
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from application.use_cases.auth.auth_use_cases import (
    RegisterUserUseCase,
    LoginUserUseCase,
    LoginTrainerUseCase,
    CreateTrainerUseCase
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data or not all(k in data for k in ['name', 'last_name', 'email', 'password', 'phone']):
        return jsonify({'error': 'Faltan campos requeridos: name, last_name, email, password, phone'}), 400

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
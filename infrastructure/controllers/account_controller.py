from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.account_use_cases import (
    DeleteUserAccountUseCase,
    DeleteTrainerAccountUseCase
)

account_bp = Blueprint('account', __name__, url_prefix='/api/account')


@account_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_account():
    identity = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    if role == 'trainer':
        result, status = DeleteTrainerAccountUseCase().execute(identity)
    elif role == 'user':
        result, status = DeleteUserAccountUseCase().execute(identity)
    else:
        return jsonify({'error': 'Rol no reconocido'}), 400

    return jsonify(result), status
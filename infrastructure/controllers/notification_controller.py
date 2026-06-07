from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from application.use_cases.notifications.notification_use_cases import (
    GetExpiringMembershipsUseCase
)

notification_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

def get_role():
    return get_jwt().get('role')

# ── Entrenador: ver usuarios con membresía próxima a vencer + links WhatsApp ──
@notification_bp.route('/expiring', methods=['GET'])
@jwt_required()
def get_expiring():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    result, status = GetExpiringMembershipsUseCase().execute()
    return jsonify(result), status
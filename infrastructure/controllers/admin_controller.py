from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from application.use_cases.admin.admin_use_cases import (
    LoginAdminUseCase,
    GetAllTrainersUseCase,
    ToggleTrainerStatusUseCase,
    ResetTrainerPasswordUseCase,
    GetAdminStatsUseCase,
    CreateSubscriptionUseCase,
    GetTrainerSubscriptionsUseCase,
    ConfirmPaymentUseCase,
    GetSubscriptionsSummaryUseCase
)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Acceso solo para administradores'}), 403
    return None

# ── Admin: login ──
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    result, status = LoginAdminUseCase().execute(data['email'], data['password'])
    if status == 200:
        token = create_access_token(
            identity=str(result['admin']['id']),
            additional_claims={'role': 'admin'}
        )
        result['token'] = token
    return jsonify(result), status


# ── Admin: estadísticas generales ──
@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    error = admin_required()
    if error: return error
    result, status = GetAdminStatsUseCase().execute()
    return jsonify(result), status


# ── Admin: ver todos los entrenadores ──
@admin_bp.route('/trainers', methods=['GET'])
@jwt_required()
def get_trainers():
    error = admin_required()
    if error: return error
    result, status = GetAllTrainersUseCase().execute()
    return jsonify(result), status


# ── Admin: activar/desactivar entrenador ──
@admin_bp.route('/trainers/<int:trainer_id>/toggle', methods=['PUT'])
@jwt_required()
def toggle_trainer(trainer_id):
    error = admin_required()
    if error: return error
    result, status = ToggleTrainerStatusUseCase().execute(trainer_id)
    return jsonify(result), status


# ── Admin: resetear contraseña de entrenador ──
@admin_bp.route('/trainers/<int:trainer_id>/reset-password', methods=['PUT'])
@jwt_required()
def reset_trainer_password(trainer_id):
    error = admin_required()
    if error: return error
    data = request.get_json()
    if not data.get('new_password'):
        return jsonify({'error': 'Nueva contraseña requerida'}), 400
    result, status = ResetTrainerPasswordUseCase().execute(trainer_id, data['new_password'])
    return jsonify(result), status

# ── Admin: resumen de pagos de todos los entrenadores ──
@admin_bp.route('/subscriptions/summary', methods=['GET'])
@jwt_required()
def get_subscriptions_summary():
    error = admin_required()
    if error: return error
    result, status = GetSubscriptionsSummaryUseCase().execute()
    return jsonify(result), status


# ── Admin: ver suscripciones de un entrenador ──
@admin_bp.route('/trainers/<int:trainer_id>/subscriptions', methods=['GET'])
@jwt_required()
def get_trainer_subscriptions(trainer_id):
    error = admin_required()
    if error: return error
    result, status = GetTrainerSubscriptionsUseCase().execute(trainer_id)
    return jsonify(result), status


# ── Admin: crear suscripción para un entrenador ──
@admin_bp.route('/trainers/<int:trainer_id>/subscriptions', methods=['POST'])
@jwt_required()
def create_subscription(trainer_id):
    error = admin_required()
    if error: return error
    data = request.get_json()
    if not all(k in data for k in ['amount', 'due_date']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    result, status = CreateSubscriptionUseCase().execute(trainer_id, data)
    return jsonify(result), status


# ── Admin: confirmar pago de suscripción ──
@admin_bp.route('/subscriptions/<int:subscription_id>/confirm', methods=['PUT'])
@jwt_required()
def confirm_payment(subscription_id):
    error = admin_required()
    if error: return error
    result, status = ConfirmPaymentUseCase().execute(subscription_id)
    return jsonify(result), status
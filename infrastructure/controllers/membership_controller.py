from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.memberships.membership_use_cases import (
    CreateMembershipUseCase,
    ConfirmPaymentUseCase,
    GetMembershipHistoryUseCase,
    GetActiveMembershipUseCase,
    GetExpiringMembershipsUseCase,
    GetMonthlyFinancesUseCase
)
import cloudinary
import cloudinary.uploader
import os

membership_bp = Blueprint('memberships', __name__, url_prefix='/api/memberships')

def trainer_required():
    claims = get_jwt()
    if claims.get('role') != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    return None

# ── Entrenador: crear membresía a un usuario ──
@membership_bp.route('/', methods=['POST'])
@jwt_required()
def create_membership():
    error = trainer_required()
    if error: return error
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    if not all(k in data for k in ['user_id', 'start_date', 'end_date']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    result, status = CreateMembershipUseCase().execute(trainer_id, data)
    return jsonify(result), status

# ── Entrenador: confirmar pago (con o sin comprobante) ──
@membership_bp.route('/<int:membership_id>/confirm', methods=['POST'])
@jwt_required()
def confirm_payment(membership_id):
    error = trainer_required()
    if error: return error
    trainer_id = int(get_jwt_identity())

    receipt_url = None

    # Si viene con archivo (comprobante de transferencia)
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        file = request.files.get('receipt')
        if file:
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET')
            )
            upload = cloudinary.uploader.upload(file, folder='fitness/receipts')
            receipt_url = upload.get('secure_url')
    else:
        data = request.get_json()

    if not data.get('payment_method'):
        return jsonify({'error': 'Método de pago requerido'}), 400

    result, status = ConfirmPaymentUseCase().execute(membership_id, trainer_id, data, receipt_url)
    return jsonify(result), status

# ── Entrenador: ver historial de pagos de un usuario ──
@membership_bp.route('/user/<int:user_id>/history', methods=['GET'])
@jwt_required()
def get_history(user_id):
    error = trainer_required()
    if error: return error
    trainer_id = int(get_jwt_identity())
    result, status = GetMembershipHistoryUseCase().execute(user_id, trainer_id)
    return jsonify(result), status

# ── Entrenador: ver membresías próximas a vencer ──
@membership_bp.route('/expiring', methods=['GET'])
@jwt_required()
def get_expiring():
    error = trainer_required()
    if error: return error
    trainer_id = int(get_jwt_identity())
    result, status = GetExpiringMembershipsUseCase().execute(trainer_id)
    return jsonify(result), status

# ── Entrenador: finanzas por mes ──
@membership_bp.route('/finances', methods=['GET'])
@jwt_required()
def get_finances():
    error = trainer_required()
    if error: return error
    trainer_id = int(get_jwt_identity())
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    if not year or not month:
        return jsonify({'error': 'Se requiere year y month como query params'}), 400
    result, status = GetMonthlyFinancesUseCase().execute(trainer_id, year, month)
    return jsonify(result), status

# ── Usuario: ver su membresía activa ──
@membership_bp.route('/me/active', methods=['GET'])
@jwt_required()
def get_active():
    user_id = int(get_jwt_identity())
    result, status = GetActiveMembershipUseCase().execute(user_id)
    return jsonify(result), status
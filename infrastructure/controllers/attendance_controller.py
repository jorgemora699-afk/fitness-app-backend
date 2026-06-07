from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.attendance.attendance_use_cases import (
    RegisterAttendanceUseCase,
    GetUserAttendanceUseCase,
    GetMyAttendanceUseCase,
    GetInactiveUsersUseCase,
    GetAllUsersAttendanceSummaryUseCase
)

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

def get_role():
    return get_jwt().get('role')

# ── Entrenador: registrar asistencia de un usuario ──
@attendance_bp.route('/', methods=['POST'])
@jwt_required()
def register_attendance():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('user_id'):
        return jsonify({'error': 'user_id es requerido'}), 400
    result, status = RegisterAttendanceUseCase().execute(trainer_id, data)
    return jsonify(result), status

# ── Entrenador: ver asistencia de un usuario (con filtro por mes/año) ──
@attendance_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_attendance(user_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    result, status = GetUserAttendanceUseCase().execute(user_id, trainer_id, month, year)
    return jsonify(result), status

# ── Entrenador: ver resumen de asistencia de todos sus usuarios ──
@attendance_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    result, status = GetAllUsersAttendanceSummaryUseCase().execute(trainer_id, month, year)
    return jsonify(result), status

# ── Entrenador: ver usuarios inactivos + link WhatsApp ──
@attendance_bp.route('/inactive', methods=['GET'])
@jwt_required()
def get_inactive():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    days = request.args.get('days', default=7, type=int)
    result, status = GetInactiveUsersUseCase().execute(trainer_id, days)
    return jsonify(result), status

# ── Usuario: ver su propia asistencia ──
@attendance_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_attendance():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    result, status = GetMyAttendanceUseCase().execute(user_id, month, year)
    return jsonify(result), status
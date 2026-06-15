from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.schedule.schedule_use_cases import (
    CreateScheduleUseCase,
    GetTrainerScheduleUseCase,
    ConfirmScheduleUseCase,
    DeleteScheduleUseCase,
    SendWhatsAppConfirmationUseCase,
    CancelScheduleAsUserUseCase,
    CancelScheduleAsTrainerUseCase,
    UpdateScheduleUseCase,
    NotifyScheduleUseCase,
    RespondScheduleUseCase,
    MarkAttendanceUseCase,
    GetPendingSchedulesUseCase
)

schedule_bp = Blueprint('schedules', __name__, url_prefix='/api/schedules')

def get_role():
    return get_jwt().get('role')


# ── Entrenador: crear horario ──
@schedule_bp.route('/', methods=['POST'])
@jwt_required()
def create_schedule():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    print('DATA RECIBIDA:', data)
    if not all(k in data for k in ['user_id', 'date', 'start_time', 'end_time']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    result, status = CreateScheduleUseCase().execute(trainer_id, data)
    return jsonify(result), status

# ── Entrenador: ver su calendario (todos o por día) ──
@schedule_bp.route('/', methods=['GET'])
@jwt_required()
def get_schedule():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    date_str = request.args.get('date')
    user_id = request.args.get('user_id', type=int)
    result, status = GetTrainerScheduleUseCase().execute(trainer_id, date_str, user_id)
    return jsonify(result), status

@schedule_bp.route('/<int:schedule_id>', methods=['PUT'])
@jwt_required()
def update_schedule(schedule_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    result, status = UpdateScheduleUseCase().execute(schedule_id, trainer_id, data)
    return jsonify(result), status

# ── Entrenador: confirmar asistencia manualmente ──
@schedule_bp.route('/<int:schedule_id>/confirm', methods=['POST'])
@jwt_required()
def confirm_schedule(schedule_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = ConfirmScheduleUseCase().execute(schedule_id, trainer_id)
    return jsonify(result), status

# ── Entrenador: eliminar horario ──
@schedule_bp.route('/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
def delete_schedule(schedule_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = DeleteScheduleUseCase().execute(schedule_id, trainer_id)
    return jsonify(result), status

# ── Entrenador: obtener link de WhatsApp para confirmar asistencia ──
@schedule_bp.route('/<int:schedule_id>/whatsapp', methods=['GET'])
@jwt_required()
def send_whatsapp(schedule_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = SendWhatsAppConfirmationUseCase().execute(schedule_id, trainer_id)
    return jsonify(result), status


# ── Usuario: ver su calendario ──
@schedule_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_schedule():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    date_str = request.args.get('date')

    from domain.entities.schedule import Schedule
    query = Schedule.query.filter_by(user_id=user_id)
    if date_str:
        from datetime import date
        query = query.filter_by(date=date.fromisoformat(date_str))
    schedules = query.order_by(Schedule.date, Schedule.start_time).all()

    return jsonify({'schedules': [s.to_dict() for s in schedules]}), 200

# ── Usuario: cancelar su entrenamiento ──
@schedule_bp.route('/<int:schedule_id>/cancel/user', methods=['POST'])
@jwt_required()
def cancel_as_user(schedule_id):
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    reason = data.get('reason')
    result, status = CancelScheduleAsUserUseCase().execute(schedule_id, user_id, reason)
    return jsonify(result), status

# ── Entrenador: cancelar entrenamiento de un usuario ──
@schedule_bp.route('/<int:schedule_id>/cancel/trainer', methods=['POST'])
@jwt_required()
def cancel_as_trainer(schedule_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json() or {}
    reason = data.get('reason')
    result, status = CancelScheduleAsTrainerUseCase().execute(schedule_id, trainer_id, reason)
    return jsonify(result), status

# ── Entrenador: enviar notificación push ──
@schedule_bp.route('/<int:schedule_id>/notify', methods=['POST'])
@jwt_required()
def notify_schedule(schedule_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = NotifyScheduleUseCase().execute(schedule_id, trainer_id)
    return jsonify(result), status

# ── Usuario: responder si va a asistir ──
@schedule_bp.route('/<int:schedule_id>/respond', methods=['POST'])
@jwt_required()
def respond_schedule(schedule_id):
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    data = request.get_json()
    result, status = RespondScheduleUseCase().execute(schedule_id, user_id, data.get('response'))
    return jsonify(result), status

# ── Entrenador: marcar si el usuario asistió ──
@schedule_bp.route('/<int:schedule_id>/attendance', methods=['POST'])
@jwt_required()
def mark_attendance(schedule_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    result, status = MarkAttendanceUseCase().execute(schedule_id, trainer_id, data.get('attended'))
    return jsonify(result), status

# ── Usuario: ver entrenamientos pendientes de confirmar ──
@schedule_bp.route('/me/pending', methods=['GET'])
@jwt_required()
def get_pending_schedules():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    result, status = GetPendingSchedulesUseCase().execute(user_id)
    return jsonify(result), status
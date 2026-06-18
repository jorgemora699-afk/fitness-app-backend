from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.routines.workout_session_use_cases import (
    StartWorkoutSessionUseCase,
    LogExerciseInSessionUseCase,
    FinishWorkoutSessionUseCase,
    GetSessionByScheduleUseCase,
    GetSessionHistoryByUserUseCase
)
from domain.entities.WorkoutSession import WorkoutSession
from domain.entities.WorkoutSession import WorkoutSession
from domain.entities.schedule import Schedule
from datetime import datetime

session_bp = Blueprint('workout_sessions', __name__, url_prefix='/api/sessions')

def get_role():
    return get_jwt().get('role')


# ── Entrenador: iniciar sesión desde un schedule ──
@session_bp.route('/start', methods=['POST'])
@jwt_required()
def start_session():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('schedule_id'):
        return jsonify({'error': 'schedule_id es requerido'}), 400
    result, status = StartWorkoutSessionUseCase().execute(data['schedule_id'], trainer_id)
    return jsonify(result), status


# ── Entrenador o usuario: registrar ejercicio en sesión ──
@session_bp.route('/<int:session_id>/log', methods=['POST'])
@jwt_required()
def log_exercise(session_id):
    role = get_role()
    if role not in ['trainer', 'user']:
        return jsonify({'error': 'No autorizado'}), 403

    identity = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('exercise_id'):
        return jsonify({'error': 'exercise_id es requerido'}), 400

    result, status = LogExerciseInSessionUseCase().execute(session_id, role, identity, data)
    return jsonify(result), status


# ── Entrenador: finalizar sesión ──
@session_bp.route('/<int:session_id>/finish', methods=['PUT'])
@jwt_required()
def finish_session(session_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = FinishWorkoutSessionUseCase().execute(session_id, trainer_id)
    return jsonify(result), status


# ── Entrenador: obtener sesión de un schedule ──
@session_bp.route('/by-schedule/<int:schedule_id>', methods=['GET'])
@jwt_required()
def get_session_by_schedule(schedule_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = GetSessionByScheduleUseCase().execute(schedule_id, trainer_id)
    return jsonify(result), status


# ── Entrenador: historial de sesiones de un usuario ──
@session_bp.route('/user/<int:user_id>/history', methods=['GET'])
@jwt_required()
def get_session_history(user_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = GetSessionHistoryByUserUseCase().execute(user_id, trainer_id)
    return jsonify(result), status

# ── Usuario: obtener sesión de un schedule ──
@session_bp.route('/me/by-schedule/<int:schedule_id>', methods=['GET'])
@jwt_required()
def get_my_session_by_schedule(schedule_id):
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())

    session = WorkoutSession.query.filter_by(
        schedule_id=schedule_id,
        user_id=user_id
    ).first()

    if not session:
        return jsonify({'session': None}), 200

    return jsonify({'session': session.to_dict()}), 200

# ── Usuario: iniciar su propia sesión ──
@session_bp.route('/me/start', methods=['POST'])
@jwt_required()
def start_my_session():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('schedule_id'):
        return jsonify({'error': 'schedule_id es requerido'}), 400
    result, status = StartWorkoutSessionUseCase().execute(
        data['schedule_id'],
        user_id=user_id
    )
    return jsonify(result), status

# ── Usuario: finalizar su propia sesión ──
@session_bp.route('/me/<int:session_id>/finish', methods=['PUT'])
@jwt_required()
def finish_my_session(session_id):
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())

    session = WorkoutSession.query.filter_by(
        id=session_id,
        user_id=user_id
    ).first()

    if not session:
        return jsonify({'error': 'Sesión no encontrada'}), 404

    if session.status == 'completed':
        return jsonify({'error': 'Esta sesión ya fue completada'}), 400

    session.status = 'completed'
    session.finished_at = datetime.utcnow()

    schedule = Schedule.query.get(session.schedule_id)
    if schedule:
        schedule.confirmed = True

    from infrastructure.database.db import db
    db.session.commit()

    return jsonify({'message': 'Sesión finalizada', 'session': session.to_dict()}), 200
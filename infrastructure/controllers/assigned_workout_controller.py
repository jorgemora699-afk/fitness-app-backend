from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.assigned_workouts.assigned_workout_use_cases import (
    GetAssignedWorkoutsForUserUseCase,
    GetMyAssignedWorkoutsUseCase
)

assigned_workout_bp = Blueprint('assigned_workouts', __name__, url_prefix='/api/assigned-workouts')

def get_role():
    return get_jwt().get('role')


# ── Entrenador: ver asignaciones de un usuario ──
@assigned_workout_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_assigned_workouts(user_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = GetAssignedWorkoutsForUserUseCase().execute(user_id, trainer_id)
    return jsonify(result), status


# ── Usuario: ver sus propias asignaciones ──
@assigned_workout_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_assigned_workouts():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    result, status = GetMyAssignedWorkoutsUseCase().execute(user_id)
    return jsonify(result), status
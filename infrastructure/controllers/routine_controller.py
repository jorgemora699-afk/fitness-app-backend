from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.routines.routine_use_cases import (
    CreateRoutineUseCase,
    GetRoutinesByUserUseCase,
    GetRoutineByDateUseCase,
    UpdateExerciseUseCase,
    UpdateExerciseAsTrainerUseCase,
    DeleteRoutineUseCase,
    UpdateRoutineUseCase,
    AddExerciseToRoutineUseCase,
    DeleteExerciseUseCase,
    CopyRoutineToUserUseCase,
    LogExerciseUseCase,
    GetWorkoutHistoryUseCase
)

routine_bp = Blueprint('routines', __name__, url_prefix='/api/routines')

def get_role():
    return get_jwt().get('role')

# ── Entrenador: crear rutina a un usuario ──
@routine_bp.route('/', methods=['POST'])
@jwt_required()
def create_routine():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    if not all(k in data for k in ['user_id', 'name']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    result, status = CreateRoutineUseCase().execute(trainer_id, data)
    return jsonify(result), status

# ── Entrenador: ver todas las rutinas de un usuario ──
@routine_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_routines_by_user(user_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = GetRoutinesByUserUseCase().execute(user_id, trainer_id)
    return jsonify(result), status

@routine_bp.route('/user/<int:user_id>/history', methods=['GET'])
@jwt_required()
def get_workout_history(user_id):

    if get_role() != 'trainer':
        return jsonify({
            'error': 'Acceso solo para entrenadores'
        }), 403

    trainer_id = int(get_jwt_identity())

    result, status = GetWorkoutHistoryUseCase().execute(
        user_id,
        trainer_id
    )

    return jsonify(result), status

# ── Usuario: ver su rutina del día ──
@routine_bp.route('/me/day', methods=['GET'])
@jwt_required()
def get_my_routine_by_date():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Se requiere el parámetro date (YYYY-MM-DD)'}), 400
    result, status = GetRoutineByDateUseCase().execute(user_id, date_str)
    return jsonify(result), status

# ── Usuario: editar un ejercicio (peso y reps) ──
@routine_bp.route('/exercise/<int:exercise_id>', methods=['PUT'])
@jwt_required()
def update_exercise(exercise_id):
    role = get_role()
    data = request.get_json()
    identity = int(get_jwt_identity())

    if role == 'user':
        result, status = UpdateExerciseUseCase().execute(exercise_id, identity, data)
    elif role == 'trainer':
        result, status = UpdateExerciseAsTrainerUseCase().execute(exercise_id, identity, data)
    else:
        return jsonify({'error': 'No autorizado'}), 403

    return jsonify(result), status


@routine_bp.route('/exercise/<int:exercise_id>/log', methods=['POST'])
@jwt_required()
def log_exercise(exercise_id):

    if get_role() != 'user':
        return jsonify({'error': 'Solo usuarios'}), 403

    user_id = int(get_jwt_identity())

    data = request.get_json()

    result, status = LogExerciseUseCase().execute(
        exercise_id,
        user_id,
        data
    )

    return jsonify(result), status

# ── Entrenador: eliminar una rutina ──
@routine_bp.route('/<int:routine_id>', methods=['DELETE'])
@jwt_required()
def delete_routine(routine_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = DeleteRoutineUseCase().execute(routine_id, trainer_id)
    return jsonify(result), status

# ── Entrenador: editar rutina (nombre, notas, fecha) ──
@routine_bp.route('/<int:routine_id>', methods=['PUT'])
@jwt_required()
def update_routine(routine_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    result, status = UpdateRoutineUseCase().execute(routine_id, trainer_id, data)
    return jsonify(result), status

# ── Entrenador: agregar ejercicio a rutina existente ──
@routine_bp.route('/<int:routine_id>/exercises', methods=['POST'])
@jwt_required()
def add_exercise(routine_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'El nombre del ejercicio es requerido'}), 400
    result, status = AddExerciseToRoutineUseCase().execute(routine_id, trainer_id, data)
    return jsonify(result), status

# ── Entrenador: eliminar ejercicio de rutina ──
@routine_bp.route('/exercise/<int:exercise_id>', methods=['DELETE'])
@jwt_required()
def delete_exercise(exercise_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = DeleteExerciseUseCase().execute(exercise_id, trainer_id)
    return jsonify(result), status

# ── Entrenador: copiar rutina a otro usuario ──
@routine_bp.route('/<int:routine_id>/copy', methods=['POST'])
@jwt_required()
def copy_routine(routine_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    result, status = CopyRoutineToUserUseCase().execute(routine_id, trainer_id, data)
    return jsonify(result), status

# ── Usuario: ver todas sus rutinas ──
@routine_bp.route('/me/all', methods=['GET'])
@jwt_required()
def get_my_routines():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    from domain.entities.routine import Routine
    routines = Routine.query.filter_by(user_id=user_id).all()
    return jsonify({'routines': [r.to_dict() for r in routines]}), 200

@routine_bp.route('/me/exercise-names', methods=['GET'])
@jwt_required()
def get_my_exercise_names():
    from domain.entities.routine import Routine, Exercise
    user_id = int(get_jwt_identity())
    routines = Routine.query.filter_by(user_id=user_id).all()
    routine_ids = [r.id for r in routines]
    exercises = Exercise.query.filter(
        Exercise.routine_id.in_(routine_ids)
    ).all()
    names = list(set([e.name for e in exercises]))
    names.sort()
    return jsonify({'names': names}), 200
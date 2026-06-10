from domain.entities.routine import Routine, Exercise
from domain.entities.user import User
from infrastructure.database.db import db

class CreateRoutineUseCase:
    def execute(self, trainer_id, data):
        user = User.query.filter_by(id=data['user_id'], trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        routine = Routine(
            user_id=data['user_id'],
            trainer_id=trainer_id,
            name=data['name'],
            notes=data.get('notes')
        )
        db.session.add(routine)
        db.session.flush()

        for ex in data.get('exercises', []):
            exercise = Exercise(
                routine_id=routine.id,
                name=ex['name'],
                sets=ex.get('sets'),
                reps=ex.get('reps'),
                weight=ex.get('weight'),
                notes=ex.get('notes')
            )
            db.session.add(exercise)

        db.session.commit()
        return {'message': 'Rutina creada', 'routine': routine.to_dict()}, 201


class GetRoutinesByUserUseCase:
    def execute(self, user_id, trainer_id):
        user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        routines = Routine.query.filter_by(user_id=user_id).order_by(
            Routine.created_at.desc()
        ).all()
        return {'routines': [r.to_dict() for r in routines]}, 200


class GetRoutineByDateUseCase:
    def execute(self, user_id, date_str):
        # Ya no aplica, pero se deja para no romper imports
        return {'error': 'No disponible'}, 404


class UpdateExerciseUseCase:
    def execute(self, exercise_id, user_id, data):
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return {'error': 'Ejercicio no encontrado'}, 404

        routine = Routine.query.filter_by(
            id=exercise.routine_id,
            user_id=user_id
        ).first()
        if not routine:
            return {'error': 'No autorizado'}, 403

        exercise.sets = data.get('sets', exercise.sets)
        exercise.reps = data.get('reps', exercise.reps)
        exercise.weight = data.get('weight', exercise.weight)
        exercise.notes = data.get('notes', exercise.notes)

        db.session.commit()
        return {'message': 'Ejercicio actualizado', 'exercise': exercise.to_dict()}, 200


class UpdateExerciseAsTrainerUseCase:
    def execute(self, exercise_id, trainer_id, data):
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return {'error': 'Ejercicio no encontrado'}, 404

        routine = Routine.query.filter_by(
            id=exercise.routine_id,
            trainer_id=trainer_id
        ).first()
        if not routine:
            return {'error': 'No autorizado'}, 403

        exercise.sets = data.get('sets', exercise.sets)
        exercise.reps = data.get('reps', exercise.reps)
        exercise.weight = data.get('weight', exercise.weight)
        exercise.notes = data.get('notes', exercise.notes)

        db.session.commit()
        return {'message': 'Ejercicio actualizado', 'exercise': exercise.to_dict()}, 200


class DeleteRoutineUseCase:
    def execute(self, routine_id, trainer_id):
        routine = Routine.query.filter_by(
            id=routine_id,
            trainer_id=trainer_id
        ).first()
        if not routine:
            return {'error': 'Rutina no encontrada'}, 404
        

        Exercise.query.filter_by(routine_id=routine_id).delete(synchronize_session=False)
        db.session.delete(routine)
        db.session.commit()
        return {'message': 'Rutina eliminada'}, 200


class UpdateRoutineUseCase:
    def execute(self, routine_id, trainer_id, data):
        routine = Routine.query.filter_by(
            id=routine_id,
            trainer_id=trainer_id
        ).first()
        if not routine:
            return {'error': 'Rutina no encontrada'}, 404

        routine.name = data.get('name', routine.name)
        routine.notes = data.get('notes', routine.notes)

        db.session.commit()
        return {'message': 'Rutina actualizada', 'routine': routine.to_dict()}, 200


class AddExerciseToRoutineUseCase:
    def execute(self, routine_id, trainer_id, data):
        routine = Routine.query.filter_by(
            id=routine_id,
            trainer_id=trainer_id
        ).first()
        if not routine:
            return {'error': 'Rutina no encontrada'}, 404

        exercise = Exercise(
            routine_id=routine_id,
            name=data['name'],
            sets=data.get('sets'),
            reps=data.get('reps'),
            weight=data.get('weight'),
            notes=data.get('notes')
        )
        db.session.add(exercise)
        db.session.commit()
        return {'message': 'Ejercicio agregado', 'exercise': exercise.to_dict()}, 201


class DeleteExerciseUseCase:
    def execute(self, exercise_id, trainer_id):
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return {'error': 'Ejercicio no encontrado'}, 404

        routine = Routine.query.filter_by(
            id=exercise.routine_id,
            trainer_id=trainer_id
        ).first()
        if not routine:
            return {'error': 'No autorizado'}, 403

        db.session.delete(exercise)
        db.session.commit()
        return {'message': 'Ejercicio eliminado'}, 200


class CopyRoutineToUserUseCase:
    def execute(self, routine_id, trainer_id, data):
        routine = Routine.query.filter_by(
            id=routine_id,
            trainer_id=trainer_id
        ).first()
        if not routine:
            return {'error': 'Rutina no encontrada'}, 404

        target_user_id = data.get('user_id')
        if not target_user_id:
            return {'error': 'user_id es requerido'}, 400

        target_user = User.query.filter_by(
            id=target_user_id,
            trainer_id=trainer_id
        ).first()
        if not target_user:
            return {'error': 'Usuario no encontrado'}, 404

        new_routine = Routine(
            user_id=target_user_id,
            trainer_id=trainer_id,
            name=routine.name,
            notes=routine.notes
        )
        db.session.add(new_routine)
        db.session.flush()

        for ex in routine.exercises:
            new_exercise = Exercise(
                routine_id=new_routine.id,
                name=ex.name,
                sets=ex.sets,
                reps=ex.reps,
                weight=ex.weight,
                notes=ex.notes
            )
            db.session.add(new_exercise)

        db.session.commit()
        return {
            'message': f'Rutina copiada a {target_user.name} {target_user.last_name}',
            'routine': new_routine.to_dict()
        }, 201
    
class LogExerciseUseCase:
    def execute(self, exercise_id, user_id, data):
        return {'error': 'Función no disponible temporalmente'}, 501


class GetWorkoutHistoryUseCase:
    def execute(self, user_id, trainer_id):
        return {'error': 'Función no disponible temporalmente'}, 501

from domain.entities.routine import Routine, Exercise
from domain.entities.user import User
from infrastructure.database.db import db
from domain.entities.routine_template import AssignedWorkout, ExerciseLog
from domain.entities.WorkoutSession import SessionExerciseLog

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
    def execute(self, user_id, trainer_id, active_only=False):
        user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        active_routines = Routine.query.filter_by(
            user_id=user_id,
            is_archived=False
        ).order_by(
            Routine.created_at.desc()
        ).all()

        if active_only:
            return {'routines': [r.to_dict() for r in active_routines]}, 200

        archived_routines = Routine.query.filter_by(
            user_id=user_id,
            is_archived=True
        ).order_by(
            Routine.created_at.desc()
        ).all()

        all_routines = active_routines + archived_routines
        return {'routines': [r.to_dict() for r in all_routines]}, 200


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

        # Validar si algún ejercicio tiene registros
        for exercise in routine.exercises:

            has_logs = SessionExerciseLog.query.filter_by(
                exercise_id=exercise.id
            ).first()

            if has_logs:
                return {
                    'error': 'No se puede eliminar esta rutina porque ya tiene sesiones registradas'
                }, 400

        # Eliminar ejercicios
        for exercise in routine.exercises:
            db.session.delete(exercise)

        # Eliminar rutina
        db.session.delete(routine)

        db.session.commit()

        return {
            'message': 'Rutina eliminada'
        }, 200


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


        log = SessionExerciseLog.query.filter_by(
            exercise_id=exercise.id
        ).first()

        if log:
            return {
                'error': 'No se puede eliminar este ejercicio porque ya tiene registros de entrenamiento asociados'
            }, 400
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

        workouts = AssignedWorkout.query.filter_by(
            user_id=user_id
        ).order_by(
            AssignedWorkout.created_at.desc()
        ).all()

        history = []

        for w in workouts:

            day_exercises = []

            for template_ex in (w.template.exercises or []):

                logs = ExerciseLog.query.filter_by(
                    assigned_workout_id=w.id,
                    exercise_id=template_ex.id
                ).all()

                # 🔹 tomamos el último log (resumen por ejercicio)
                last_log = logs[-1] if logs else None

                day_exercises.append({
                    "name": template_ex.name,
                    "planned": {
                        "sets": template_ex.sets,
                        "reps": template_ex.reps,
                        "weight": template_ex.weight
                    },
                    "actual": {
                        "sets": last_log.performed_sets if last_log else None,
                        "reps": last_log.performed_reps if last_log else None,
                        "weight": last_log.performed_weight if last_log else None
                    }
                })

            history.append({
                "date": w.created_at.isoformat(),
                "workout": w.template.name if w.template else None,
                "status": w.status,
                "exercises": day_exercises
            })

        return {
            "history": history
        }, 200
    
class ArchiveRoutineUseCase:
    def execute(self, routine_id, trainer_id):
        routine = Routine.query.filter_by(
            id=routine_id,
            trainer_id=trainer_id
        ).first()

        if not routine:
            return {'error': 'Rutina no encontrada'}, 404

        routine.is_archived = True

        db.session.commit()

        return {
            'message': 'Rutina archivada'
        }, 200


class RestoreRoutineUseCase:
    def execute(self, routine_id, trainer_id):
        routine = Routine.query.filter_by(
            id=routine_id,
            trainer_id=trainer_id
        ).first()

        if not routine:
            return {'error': 'Rutina no encontrada'}, 404

        routine.is_archived = False

        db.session.commit()

        return {
            'message': 'Rutina restaurada'
        }, 200
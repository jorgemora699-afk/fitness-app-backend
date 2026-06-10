from domain.entities.routine_template import AssignedWorkout, RoutineTemplate
from domain.entities.user import User


class GetAssignedWorkoutsForUserUseCase:
    """Para que el entrenador vea las asignaciones de un usuario"""
    def execute(self, user_id, trainer_id):
        user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        workouts = AssignedWorkout.query.filter_by(user_id=user_id).order_by(
            AssignedWorkout.assigned_date.desc()
        ).all()

        return {'assigned_workouts': [self._serialize(w) for w in workouts]}, 200

    def _serialize(self, w):
        data = w.to_dict()
        data['exercises'] = [e.to_dict() for e in w.template.exercises] if w.template else []
        return data


class GetMyAssignedWorkoutsUseCase:
    """Para que el usuario vea sus propias asignaciones"""
    def execute(self, user_id):
        workouts = AssignedWorkout.query.filter_by(user_id=user_id).order_by(
            AssignedWorkout.assigned_date.desc()
        ).all()

        return {'assigned_workouts': [self._serialize(w) for w in workouts]}, 200

    def _serialize(self, w):
        data = w.to_dict()
        data['exercises'] = [e.to_dict() for e in w.template.exercises] if w.template else []
        return data
from domain.entities.routine_template import AssignedWorkout, RoutineTemplate
from domain.entities.user import User


class GetAssignedWorkoutsForUserUseCase:
    def execute(self, user_id, trainer_id):

        user = User.query.filter_by(
            id=user_id,
            trainer_id=trainer_id
        ).first()

        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        workouts = AssignedWorkout.query.filter_by(
            user_id=user_id
        ).order_by(
            AssignedWorkout.created_at.desc()
        ).all()

        return {
            'assigned_workouts': [
                self._serialize(w) for w in workouts
            ]
        }, 200

    def _serialize(self, w):
        return {
            **w.to_dict(),
            "exercises": [
                e.to_dict() for e in (w.template.exercises or [])
            ] if w.template else []
        }


class GetMyAssignedWorkoutsUseCase:
    def execute(self, user_id):

        workouts = AssignedWorkout.query.filter_by(
            user_id=user_id
        ).order_by(
            AssignedWorkout.created_at.desc()
        ).all()

        return {
            'assigned_workouts': [
                self._serialize(w) for w in workouts
            ]
        }, 200

    def _serialize(self, w):
        return {
            **w.to_dict(),
            "exercises": [
                e.to_dict() for e in (w.template.exercises or [])
            ] if w.template else []
        }
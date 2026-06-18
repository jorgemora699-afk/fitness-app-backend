from domain.entities.WorkoutSession import WorkoutSession, SessionExerciseLog
from domain.entities.schedule import Schedule
from domain.entities.routine import Exercise
from infrastructure.database.db import db
from datetime import datetime


class StartWorkoutSessionUseCase:
    def execute(self, schedule_id, trainer_id=None, user_id=None):

        from domain.entities.schedule import Schedule

        if trainer_id:
            schedule = Schedule.query.filter_by(
                id=schedule_id,
                trainer_id=trainer_id
            ).first()
        else:
            schedule = Schedule.query.filter_by(
                id=schedule_id,
                user_id=user_id
            ).first()

        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        if schedule.cancelled:
            return {'error': 'Este horario fue cancelado'}, 400

        if not schedule.routine_id:
            return {'error': 'Este horario no tiene rutina asignada'}, 400

        existing = WorkoutSession.query.filter_by(
            schedule_id=schedule_id,
            status='in_progress'
        ).first()

        if existing:
            return {
                'message': 'Sesión ya iniciada',
                'session': existing.to_dict()
            }, 200

        session = WorkoutSession(
            schedule_id=schedule_id,
            user_id=schedule.user_id,
            trainer_id=schedule.trainer_id,
            status='in_progress'
        )

        db.session.add(session)
        db.session.commit()

        return {
            'message': 'Sesión iniciada',
            'session': session.to_dict()
        }, 201


class LogExerciseInSessionUseCase:
    def execute(self, session_id, editor_role, editor_id, data):
        from datetime import date, timedelta

        if editor_role == 'trainer':
            session = WorkoutSession.query.filter_by(
                id=session_id,
                trainer_id=editor_id
            ).first()
        else:
            session = WorkoutSession.query.filter_by(
                id=session_id,
                user_id=editor_id
            ).first()

        if not session:
            return {'error': 'Sesión no encontrada'}, 404

        if session.status == 'completed':
            return {'error': 'Esta sesión ya fue completada'}, 400

        # Validar ventana de tiempo basada en la fecha del schedule
        schedule = Schedule.query.get(session.schedule_id)
        if schedule:
            today = date.today()
            schedule_date = schedule.date

            if today < schedule_date:
                return {'error': 'No puedes registrar antes del día del entrenamiento'}, 403

            if editor_role == 'user':
                if today > schedule_date + timedelta(days=2):
                    return {'error': 'El plazo para registrar tu entrenamiento ha vencido (48 horas)'}, 403
            elif editor_role == 'trainer':
                if today > schedule_date + timedelta(days=7):
                    return {'error': 'El plazo para registrar este entrenamiento ha vencido (7 días)'}, 403

        exercise = Exercise.query.get(data.get('exercise_id'))
        if not exercise:
            return {'error': 'Ejercicio no encontrado'}, 404

        log = SessionExerciseLog(
            session_id=session_id,
            exercise_id=data['exercise_id'],
            performed_sets=data.get('performed_sets'),
            performed_reps=data.get('performed_reps'),
            performed_weight=data.get('performed_weight'),
            notes=data.get('notes')
        )

        db.session.add(log)
        db.session.commit()

        return {
            'message': 'Ejercicio registrado',
            'log': log.to_dict()
        }, 201


class FinishWorkoutSessionUseCase:
    def execute(self, session_id, trainer_id):

        session = WorkoutSession.query.filter_by(
            id=session_id,
            trainer_id=trainer_id
        ).first()

        if not session:
            return {'error': 'Sesión no encontrada'}, 404

        if session.status == 'completed':
            return {'error': 'Esta sesión ya fue completada'}, 400

        session.status = 'completed'
        session.finished_at = datetime.utcnow()

        # Marcar el schedule como confirmado
        schedule = Schedule.query.get(session.schedule_id)
        if schedule:
            schedule.confirmed = True

        db.session.commit()

        return {
            'message': 'Sesión finalizada',
            'session': session.to_dict()
        }, 200


class GetSessionByScheduleUseCase:
    def execute(self, schedule_id, trainer_id):

        schedule = Schedule.query.filter_by(
            id=schedule_id,
            trainer_id=trainer_id
        ).first()

        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        session = WorkoutSession.query.filter_by(
            schedule_id=schedule_id
        ).first()

        if not session:
            return {'session': None}, 200

        return {'session': session.to_dict()}, 200


class GetSessionHistoryByUserUseCase:
    def execute(self, user_id, trainer_id):

        sessions = WorkoutSession.query.filter_by(
            user_id=user_id,
            trainer_id=trainer_id
        ).order_by(WorkoutSession.started_at.desc()).all()

        return {
            'sessions': [s.to_dict() for s in sessions]
        }, 200
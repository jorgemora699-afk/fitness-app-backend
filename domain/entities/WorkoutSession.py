from infrastructure.database.db import db
from datetime import datetime

class WorkoutSession(db.Model):
    __tablename__ = 'workout_sessions'

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed

    logs = db.relationship(
        'SessionExerciseLog',
        backref='session',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'user_id': self.user_id,
            'trainer_id': self.trainer_id,
            'started_at': self.started_at.isoformat(),
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'status': self.status,
            'logs': [log.to_dict() for log in self.logs]
        }


class SessionExerciseLog(db.Model):
    __tablename__ = 'session_exercise_logs'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('workout_sessions.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)

    performed_sets = db.Column(db.Integer, nullable=True)
    performed_reps = db.Column(db.String(20), nullable=True)
    performed_weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)

    exercise = db.relationship('Exercise', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'exercise_id': self.exercise_id,
            'exercise_name': self.exercise.name if self.exercise else None,
            'performed_sets': self.performed_sets,
            'performed_reps': self.performed_reps,
            'performed_weight': self.performed_weight,
            'notes': self.notes,
            'logged_at': self.logged_at.isoformat()
        }
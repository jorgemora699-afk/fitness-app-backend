from infrastructure.database.db import db
from datetime import datetime


class ExerciseLog(db.Model):
    __tablename__ = 'exercise_logs'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey('exercises.id'),
        nullable=False
    )

    performed_sets = db.Column(db.Integer)
    performed_reps = db.Column(db.Integer)
    performed_weight = db.Column(db.Float)

    performed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_id': self.exercise_id,
            'performed_sets': self.performed_sets,
            'performed_reps': self.performed_reps,
            'performed_weight': self.performed_weight,
            'performed_at': self.performed_at.isoformat()
        }
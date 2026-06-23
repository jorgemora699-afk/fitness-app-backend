from infrastructure.database.db import db
from datetime import datetime

class Routine(db.Model):
    __tablename__ = 'routines'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    is_archived = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exercises = db.relationship('Exercise', backref='routine', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trainer_id': self.trainer_id,
            'name': self.name,
            'notes': self.notes,
            'is_archived': self.is_archived,
            'exercises': [e.to_dict() for e in self.exercises],
            'created_at': self.created_at.isoformat()
        }


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routines.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(500),nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'routine_id': self.routine_id,
            'name': self.name,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight,
            'notes': self.notes,
            'video_url': self.video_url,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
from infrastructure.database.db import db
from datetime import datetime, date

class AssignedWorkout(db.Model):
    __tablename__ = 'assigned_workouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('routine_templates.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, skipped
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    template = db.relationship('RoutineTemplate', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'template_id': self.template_id,
            'template_name': self.template.name if self.template else None,
            'status': self.status,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
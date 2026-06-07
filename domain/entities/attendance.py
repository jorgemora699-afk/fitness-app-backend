from infrastructure.database.db import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    attended = db.Column(db.Boolean, default=True)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trainer_id': self.trainer_id,
            'date': self.date.isoformat(),
            'attended': self.attended,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
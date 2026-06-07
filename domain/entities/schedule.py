from infrastructure.database.db import db
from datetime import datetime

class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    cancelled = db.Column(db.Boolean, default=False)
    cancel_reason = db.Column(db.String(255), nullable=True)
    cancelled_by = db.Column(db.String(20), nullable=True)  # 'user' o 'trainer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'confirmed': self.confirmed,
            'cancelled': self.cancelled,
            'cancel_reason': self.cancel_reason,
            'cancelled_by': self.cancelled_by,
            'created_at': self.created_at.isoformat()
        }
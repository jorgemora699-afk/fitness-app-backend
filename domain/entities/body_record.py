from infrastructure.database.db import db
from datetime import datetime

class BodyRecord(db.Model):
    __tablename__ = 'body_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    body_fat = db.Column(db.Float, nullable=True)   # % grasa corporal
    muscle_mass = db.Column(db.Float, nullable=True) # % masa muscular
    recorded_at = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'weight': self.weight,
            'body_fat': self.body_fat,
            'muscle_mass': self.muscle_mass,
            'recorded_at': self.recorded_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }
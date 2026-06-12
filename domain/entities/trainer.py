from infrastructure.database.db import db
from datetime import datetime
import random
import string

def generate_trainer_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class Trainer(db.Model):
    __tablename__ = 'trainers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    trainer_code = db.Column(db.String(8), unique=True, nullable=False, default=generate_trainer_code)
    is_active = db.Column(db.Boolean, default=True)
    reset_code = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='trainer', lazy=True)
    schedules = db.relationship('Schedule', backref='trainer', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'trainer_code': self.trainer_code,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
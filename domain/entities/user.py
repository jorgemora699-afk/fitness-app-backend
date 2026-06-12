from infrastructure.database.db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(150), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=False)  # requerido para WhatsApp
    age = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    goal = db.Column(db.String(255), nullable=True)
    body_fat = db.Column(db.Float, nullable=True)    # % grasa corporal
    muscle_mass = db.Column(db.Float, nullable=True)  # % masa muscular
    profile_photo = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    push_token = db.Column(db.String(255), nullable=True)

    memberships = db.relationship('Membership', backref='user', lazy=True)
    routines = db.relationship('Routine', backref='user', lazy=True)
    progress_photos = db.relationship('ProgressPhoto', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'age': self.age,
            'weight': self.weight,
            'height': self.height,
            'goal': self.goal,
            'body_fat': self.body_fat,
            'muscle_mass': self.muscle_mass,
            'profile_photo': self.profile_photo,
            'is_active': self.is_active,
            'trainer_id': self.trainer_id,
            'created_at': self.created_at.isoformat()
        }
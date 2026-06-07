from infrastructure.database.db import db
from datetime import datetime

class ProgressPhoto(db.Model):
    __tablename__ = 'progress_photos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    photo_url = db.Column(db.String(255), nullable=False)
    angle = db.Column(db.String(20), nullable=False)  # 'frontal', 'lateral', 'trasera'
    taken_at = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'photo_url': self.photo_url,
            'angle': self.angle,
            'taken_at': self.taken_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }
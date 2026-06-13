from infrastructure.database.db import db
from datetime import datetime

class TrainerSubscription(db.Model):
    __tablename__ = 'trainer_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    payment_method = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trainer = db.relationship('Trainer', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'trainer_name': self.trainer.name if self.trainer else None,
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'is_paid': self.is_paid,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
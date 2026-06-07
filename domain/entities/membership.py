from infrastructure.database.db import db
from datetime import datetime

class Membership(db.Model):
    __tablename__ = 'memberships'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    payment_method = db.Column(db.String(50), nullable=True)  # 'cash', 'transfer'
    receipt_url = db.Column(db.String(255), nullable=True)    # comprobante
    amount = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'is_paid': self.is_paid,
            'payment_method': self.payment_method,
            'receipt_url': self.receipt_url,
            'amount': self.amount,
            'created_at': self.created_at.isoformat()
        }
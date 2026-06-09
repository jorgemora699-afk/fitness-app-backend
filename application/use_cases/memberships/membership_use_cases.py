from domain.entities.membership import Membership
from domain.entities.user import User
from infrastructure.database.db import db
from datetime import date, timedelta

class CreateMembershipUseCase:
    def execute(self, trainer_id, data):
        # Verificar que el usuario pertenece al entrenador
        user = User.query.filter_by(id=data['user_id'], trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        start_date = date.fromisoformat(data['start_date'])
        end_date = date.fromisoformat(data['end_date'])

        membership = Membership(
            user_id=data['user_id'],
            start_date=start_date,
            end_date=end_date,
            is_paid=False,
            amount=data.get('amount')
        )
        db.session.add(membership)
        db.session.commit()
        return {'message': 'Membresía creada', 'membership': membership.to_dict()}, 201


class ConfirmPaymentUseCase:
    def execute(self, membership_id, trainer_id, data, receipt_url=None):
        membership = Membership.query.get(membership_id)
        if not membership:
            return {'error': 'Membresía no encontrada'}, 404

        # Verificar que el usuario pertenece al entrenador
        user = User.query.filter_by(id=membership.user_id, trainer_id=trainer_id).first()
        if not user:
            return {'error': 'No autorizado'}, 403

        membership.is_paid = True
        membership.payment_method = data.get('payment_method')  # 'cash' o 'transfer'
        if receipt_url:
            membership.receipt_url = receipt_url

        db.session.commit()
        return {'message': 'Pago confirmado', 'membership': membership.to_dict()}, 200


class GetMembershipHistoryUseCase:
    def execute(self, user_id, trainer_id):
        user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        memberships = Membership.query.filter_by(user_id=user_id).order_by(
            Membership.start_date.desc()
        ).all()
        return {'memberships': [m.to_dict() for m in memberships]}, 200


class GetActiveMembershipUseCase:
    def execute(self, user_id):
        today = date.today()
        membership = Membership.query.filter_by(
            user_id=user_id,
            is_paid=True
        ).filter(
            Membership.end_date >= today
        ).first()

        if not membership:
            return {'error': 'No hay membresía activa'}, 404
        return {'membership': membership.to_dict()}, 200


class GetExpiringMembershipsUseCase:
    def execute(self, trainer_id):
        today = date.today()
        in_5_days = today + timedelta(days=5)

        # Usuarios del entrenador
        user_ids = [u.id for u in User.query.filter_by(trainer_id=trainer_id).all()]

        expiring = Membership.query.filter(
            Membership.user_id.in_(user_ids),
            Membership.is_paid == True,
            Membership.end_date >= today,
            Membership.end_date <= in_5_days
        ).all()

        result = []
        for m in expiring:
            user = User.query.get(m.user_id)
            result.append({
                'membership': m.to_dict(),
                'user': user.to_dict()
            })

        return {'expiring_memberships': result}, 200


class GetMonthlyFinancesUseCase:
    def execute(self, trainer_id, year, month):
        user_ids = [u.id for u in User.query.filter_by(trainer_id=trainer_id).all()]

        memberships = Membership.query.filter(
            Membership.user_id.in_(user_ids),
            Membership.is_paid == True,
            db.extract('year', Membership.start_date) == year,
            db.extract('month', Membership.start_date) == month
        ).all()

        total = sum(m.amount or 0 for m in memberships)

        payments = []
        for m in memberships:
            user = User.query.get(m.user_id)
            payment_data = m.to_dict()
            payment_data['user_name'] = f"{user.name} {user.last_name}" if user else f"Usuario #{m.user_id}"
            payments.append(payment_data)

        return {
            'year': year,
            'month': month,
            'total_collected': total,
            'payments': [m.to_dict() for m in memberships],
            'count': len(memberships)
        }, 200
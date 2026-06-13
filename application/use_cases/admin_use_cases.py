from domain.entities.trainer_subscription import TrainerSubscription
from datetime import date

class CreateSubscriptionUseCase:
    def execute(self, trainer_id, data):
        trainer = Trainer.query.get(trainer_id)
        if not trainer:
            return {'error': 'Entrenador no encontrado'}, 404

        subscription = TrainerSubscription(
            trainer_id=trainer_id,
            amount=data['amount'],
            payment_date=date.fromisoformat(data['payment_date']),
            due_date=date.fromisoformat(data['due_date']),
            is_paid=data.get('is_paid', False),
            payment_method=data.get('payment_method'),
            notes=data.get('notes')
        )
        db.session.add(subscription)
        db.session.commit()
        return {'message': 'Suscripción creada', 'subscription': subscription.to_dict()}, 201


class GetTrainerSubscriptionsUseCase:
    def execute(self, trainer_id):
        trainer = Trainer.query.get(trainer_id)
        if not trainer:
            return {'error': 'Entrenador no encontrado'}, 404

        subscriptions = TrainerSubscription.query.filter_by(
            trainer_id=trainer_id
        ).order_by(TrainerSubscription.due_date.desc()).all()

        return {
            'trainer': trainer.to_dict(),
            'subscriptions': [s.to_dict() for s in subscriptions]
        }, 200


class ConfirmPaymentUseCase:
    def execute(self, subscription_id):
        subscription = TrainerSubscription.query.get(subscription_id)
        if not subscription:
            return {'error': 'Suscripción no encontrada'}, 404

        subscription.is_paid = True
        subscription.payment_date = date.today()
        db.session.commit()
        return {'message': 'Pago confirmado', 'subscription': subscription.to_dict()}, 200


class GetSubscriptionsSummaryUseCase:
    def execute(self):
        today = date.today()

        trainers = Trainer.query.filter_by(is_active=True).all()
        result = []

        for trainer in trainers:
            latest = TrainerSubscription.query.filter_by(
                trainer_id=trainer.id
            ).order_by(TrainerSubscription.due_date.desc()).first()

            status = 'sin_registro'
            days_until_due = None

            if latest:
                days_until_due = (latest.due_date - today).days
                if latest.is_paid and days_until_due >= 0:
                    status = 'al_dia'
                elif not latest.is_paid and days_until_due < 0:
                    status = 'vencido'
                elif not latest.is_paid:
                    status = 'pendiente'
                else:
                    status = 'vencido'

            result.append({
                'trainer': trainer.to_dict(),
                'latest_subscription': latest.to_dict() if latest else None,
                'status': status,
                'days_until_due': days_until_due
            })

        return {'summary': result}, 200
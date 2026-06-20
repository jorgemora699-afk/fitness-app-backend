from werkzeug.security import check_password_hash, generate_password_hash
from domain.entities.admin import Admin
from domain.entities.trainer import Trainer
from domain.entities.user import User
from infrastructure.database.db import db
from domain.entities.trainer_subscription import TrainerSubscription
from datetime import date


class LoginAdminUseCase:
    def execute(self, email, password):
        admin = Admin.query.filter_by(email=email).first()
        if not admin:
            return {'error': 'Credenciales inválidas'}, 401

        if not check_password_hash(admin.password_hash, password):
            return {'error': 'Credenciales inválidas'}, 401

        if not admin.is_active:
            return {'error': 'Cuenta de admin inactiva'}, 403

        return {'admin': admin.to_dict()}, 200


class GetAllTrainersUseCase:
    def execute(self):
        trainers = Trainer.query.order_by(Trainer.created_at.desc()).all()
        result = []
        for t in trainers:
            user_count = User.query.filter_by(trainer_id=t.id).count()
            result.append({
                **t.to_dict(),
                'user_count': user_count
            })
        return {'trainers': result}, 200


class ToggleTrainerStatusUseCase:
    def execute(self, trainer_id):
        trainer = Trainer.query.get(trainer_id)
        if not trainer:
            return {'error': 'Entrenador no encontrado'}, 404

        trainer.is_active = not trainer.is_active
        db.session.commit()
        return {
            'message': f'Entrenador {"activado" if trainer.is_active else "desactivado"}',
            'trainer': trainer.to_dict()
        }, 200


class ResetTrainerPasswordUseCase:
    def execute(self, trainer_id, new_password):
        if not new_password or len(new_password) < 6:
            return {'error': 'La contraseña debe tener al menos 6 caracteres'}, 400

        trainer = Trainer.query.get(trainer_id)
        if not trainer:
            return {'error': 'Entrenador no encontrado'}, 404

        trainer.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return {'message': 'Contraseña actualizada correctamente'}, 200


class GetAdminStatsUseCase:
    def execute(self):
        total_trainers = Trainer.query.count()
        active_trainers = Trainer.query.filter_by(is_active=True).count()
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()

        return {
            'stats': {
                'total_trainers': total_trainers,
                'active_trainers': active_trainers,
                'inactive_trainers': total_trainers - active_trainers,
                'total_users': total_users,
                'active_users': active_users,
            }
        }, 200
    


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
    
class CreateTrainerAsAdminUseCase:
    def execute(self, data):
        from werkzeug.security import generate_password_hash

        if not data.get('name') or not data.get('email') or not data.get('password'):
            return {'error': 'Nombre, email y contraseña son requeridos'}, 400

        existing = Trainer.query.filter_by(email=data['email']).first()
        if existing:
            return {'error': 'Ya existe un entrenador con ese correo'}, 400

        if len(data['password']) < 6:
            return {'error': 'La contraseña debe tener al menos 6 caracteres'}, 400

        trainer = Trainer(
            name=data['name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            phone=data.get('phone')
        )
        db.session.add(trainer)
        db.session.commit()

        return {
            'message': 'Entrenador creado correctamente',
            'trainer': trainer.to_dict()
        }, 201
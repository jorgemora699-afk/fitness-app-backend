from werkzeug.security import check_password_hash, generate_password_hash
from domain.entities.admin import Admin
from domain.entities.trainer import Trainer
from domain.entities.user import User
from infrastructure.database.db import db


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
from datetime import datetime
from infrastructure.database.db import db
from domain.entities.user import User
from domain.entities.trainer import Trainer


class DeleteUserAccountUseCase:
    def execute(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        if user.is_deleted:
            return {'error': 'La cuenta ya fue eliminada'}, 400

        timestamp = int(datetime.utcnow().timestamp())

        user.name = 'Usuario eliminado'
        user.last_name = ''
        user.email = f'deleted_user_{user.id}_{timestamp}@fittrack.deleted'
        user.password_hash = None
        user.google_id = None
        user.phone = 'N/A'
        user.profile_photo = None
        user.push_token = None
        user.is_active = False
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()

        db.session.commit()
        return {'message': 'Cuenta eliminada correctamente'}, 200


class DeleteTrainerAccountUseCase:
    def execute(self, trainer_id):
        trainer = Trainer.query.get(trainer_id)
        if not trainer:
            return {'error': 'Entrenador no encontrado'}, 404

        if trainer.is_deleted:
            return {'error': 'La cuenta ya fue eliminada'}, 400

        timestamp = int(datetime.utcnow().timestamp())

        # Desvincular automáticamente a los usuarios asignados
        User.query.filter_by(trainer_id=trainer.id).update({'trainer_id': None})

        trainer.name = 'Entrenador eliminado'
        trainer.email = f'deleted_trainer_{trainer.id}_{timestamp}@fittrack.deleted'
        trainer.password_hash = generate_unusable_hash()
        trainer.phone = None
        trainer.profile_photo = None
        trainer.trainer_code = f'DEL{timestamp}'[:8]
        trainer.reset_code = None
        trainer.is_active = False
        trainer.is_deleted = True
        trainer.deleted_at = datetime.utcnow()

        db.session.commit()
        return {'message': 'Cuenta eliminada correctamente'}, 200


def generate_unusable_hash():
    from werkzeug.security import generate_password_hash
    import secrets
    return generate_password_hash(secrets.token_hex(32))
from domain.entities.user import User
from domain.entities.membership import Membership
from infrastructure.database.db import db
from datetime import date

class GetMyUsersUseCase:
    def execute(self, trainer_id):

        users = User.query.filter_by(
            trainer_id=trainer_id
        ).all()

        pending = []
        approved = []
        rejected = []

        for user in users:

            if user.trainer_status == 'pending':
                pending.append(user.to_dict())

            elif user.trainer_status == 'approved':
                approved.append(user.to_dict())

            elif user.trainer_status == 'rejected':
                rejected.append(user.to_dict())

        return {
            'users': [u.to_dict() for u in users]
        }, 200
    
class ApproveUserUseCase:
    def execute(self, user_id, trainer_id):

        user = User.query.filter_by(
            id=user_id,
            trainer_id=trainer_id
        ).first()

        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        user.trainer_status = 'approved'

        db.session.commit()

        return {
            'message': 'Usuario aprobado correctamente',
            'user': user.to_dict()
        }, 200

class RejectUserUseCase:
    def execute(self, user_id, trainer_id):

        user = User.query.filter_by(
            id=user_id,
            trainer_id=trainer_id
        ).first()

        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        user.trainer_status = 'rejected'

        db.session.commit()

        return {
            'message': 'Usuario rechazado'
        }, 200


class GetUserByIdUseCase:
    def execute(self, user_id, trainer_id):
        user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404
        return {'user': user.to_dict()}, 200


class UpdateUserUseCase:
    def execute(self, user_id, trainer_id, data):
        user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        user.name = data.get('name', user.name)
        user.last_name = data.get('last_name', user.last_name)
        user.phone = data.get('phone', user.phone)
        user.age = data.get('age', user.age)
        user.weight = data.get('weight', user.weight)
        user.height = data.get('height', user.height)
        user.goal = data.get('goal', user.goal)
        user.body_fat = data.get('body_fat', user.body_fat)
        user.muscle_mass = data.get('muscle_mass', user.muscle_mass)

        db.session.commit()
        return {'message': 'Usuario actualizado', 'user': user.to_dict()}, 200


class AssignTrainerUseCase:
    def execute(self, user_id, trainer_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        user.trainer_id = trainer_id
        db.session.commit()
        return {'message': 'Entrenador asignado correctamente', 'user': user.to_dict()}, 200


class GetUserProfileUseCase:
    def execute(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        today = date.today()
        active_membership = Membership.query.filter_by(
            user_id=user_id,
            is_paid=True
        ).filter(
            Membership.end_date >= today
        ).first()

        return {
            'user': user.to_dict(),
            'membership': active_membership.to_dict() if active_membership else None
        }, 200
    
class ChangePasswordUseCase:
    def execute(self, user_id, data):
        from werkzeug.security import check_password_hash, generate_password_hash
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        if not check_password_hash(user.password_hash, data.get('current_password', '')):
            return {'error': 'Contraseña actual incorrecta'}, 400

        if not data.get('new_password'):
            return {'error': 'Nueva contraseña requerida'}, 400

        if len(data['new_password']) < 6:
            return {'error': 'La contraseña debe tener al menos 6 caracteres'}, 400

        user.password_hash  = generate_password_hash(data['new_password'])
        db.session.commit()
        return {'message': 'Contraseña actualizada correctamente'}, 200
    
class SavePushTokenUseCase:
    def execute(self, user_id, push_token):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        user.push_token = push_token
        db.session.commit()
        return {'message': 'Token guardado'}, 200
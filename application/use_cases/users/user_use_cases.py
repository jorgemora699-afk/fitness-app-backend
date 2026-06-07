from domain.entities.user import User
from domain.entities.membership import Membership
from infrastructure.database.db import db
from datetime import date

class GetMyUsersUseCase:
    def execute(self, trainer_id):
        users = User.query.filter_by(trainer_id=trainer_id).all()
        return {'users': [u.to_dict() for u in users]}, 200


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
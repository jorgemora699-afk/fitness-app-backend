from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from domain.entities.user import User
from domain.entities.trainer import Trainer
from domain.entities.membership import Membership
from infrastructure.database.db import db

class RegisterUserUseCase:
    def execute(self, data):
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            return {'error': 'El correo ya está registrado'}, 400

        # Validar código del entrenador
        trainer_code = data.get('trainer_code')
        if not trainer_code:
            return {'error': 'El código del entrenador es requerido'}, 400

        trainer = Trainer.query.filter_by(trainer_code=trainer_code.upper()).first()
        if not trainer:
            return {'error': 'Código de entrenador inválido'}, 404

        user = User(
            name=data['name'],
            last_name=data['last_name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            phone=data['phone'],
            age=data.get('age'),
            weight=data.get('weight'),
            height=data.get('height'),
            goal=data.get('goal'),
            trainer_id=trainer.id  # asignar automáticamente
        )
        db.session.add(user)
        db.session.commit()
        return {'message': 'Usuario registrado exitosamente', 'user': user.to_dict()}, 201


class LoginUserUseCase:
    def execute(self, email, password):
        user = User.query.filter_by(email=email).first()
        if not user:
            return {'error': 'Credenciales inválidas'}, 401

        if not check_password_hash(user.password_hash, password):
            return {'error': 'Credenciales inválidas'}, 401

        # Verificar membresía activa (sin bloquear el login)
        today = date.today()
        active_membership = Membership.query.filter_by(
            user_id=user.id,
            is_paid=True
        ).filter(
            Membership.end_date >= today
        ).first()

        return {
            'user': user.to_dict(),
            'membership': active_membership.to_dict() if active_membership else None
        }, 200


class LoginTrainerUseCase:
    def execute(self, email, password):
        trainer = Trainer.query.filter_by(email=email).first()
        if not trainer:
            return {'error': 'Credenciales inválidas'}, 401

        if not check_password_hash(trainer.password_hash, password):
            return {'error': 'Credenciales inválidas'}, 401

        return {'trainer': trainer.to_dict()}, 200


class CreateTrainerUseCase:
    def execute(self, data):
        existing = Trainer.query.filter_by(email=data['email']).first()
        if existing:
            return {'error': 'El correo ya está registrado'}, 400

        trainer = Trainer(
            name=data['name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            phone=data.get('phone')
        )
        db.session.add(trainer)
        db.session.commit()
        return {'message': 'Entrenador creado exitosamente', 'trainer': trainer.to_dict()}, 201
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
    
class ResetPasswordUseCase:
    def execute(self, data):
        email = data.get('email')
        trainer_code = data.get('trainer_code')
        new_password = data.get('new_password')

        if not email or not trainer_code or not new_password:
            return {'error': 'Email, código del entrenador y nueva contraseña son requeridos'}, 400

        if len(new_password) < 6:
            return {'error': 'La contraseña debe tener al menos 6 caracteres'}, 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        trainer = Trainer.query.filter_by(
            trainer_code=trainer_code.upper(),
            id=user.trainer_id
        ).first()

        if not trainer:
            return {'error': 'Código del entrenador incorrecto'}, 400

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        return {'message': 'Contraseña actualizada correctamente'}, 200
    
class SendResetCodeTrainerUseCase:
    def execute(self, email):
        import random
        import resend
        from flask import current_app

        trainer = Trainer.query.filter_by(email=email).first()
        if not trainer:
            return {'error': 'Entrenador no encontrado'}, 404

        code = str(random.randint(100000, 999999))
        trainer.reset_code = code
        db.session.commit()

        try:
            resend.api_key = current_app.config['RESEND_API_KEY']
            resend.Emails.send({
                'from': 'onboarding@resend.dev',
                'to': 'expopro39@gmail.com',
                'subject': 'Código de recuperación - FitTracker',
                'html': f'''
                    <h2>Recuperación de contraseña</h2>
                    <p>Hola {trainer.name},</p>
                    <p>Tu código de recuperación es:</p>
                    <h1 style="letter-spacing: 8px; color: #333;">{code}</h1>
                    <p>Este código es válido por 15 minutos.</p>
                    <p>Si no solicitaste este código, ignora este mensaje.</p>
                '''
            })
        except Exception as e:
            return {'error': f'No se pudo enviar el email: {str(e)}'}, 500

        return {'message': 'Código enviado al correo', 'code': code}, 200


class ResetPasswordTrainerUseCase:
    def execute(self, data):
        email = data.get('email')
        code = data.get('code')
        new_password = data.get('new_password')

        if not email or not code or not new_password:
            return {'error': 'Email, código y nueva contraseña son requeridos'}, 400

        if len(new_password) < 6:
            return {'error': 'La contraseña debe tener al menos 6 caracteres'}, 400

        trainer = Trainer.query.filter_by(email=email).first()
        if not trainer:
            return {'error': 'Entrenador no encontrado'}, 404

        if not trainer.reset_code or trainer.reset_code != code:
            return {'error': 'Código incorrecto'}, 400

        trainer.password_hash = generate_password_hash(new_password)
        trainer.reset_code = None
        db.session.commit()

        return {'message': 'Contraseña actualizada correctamente'}, 200
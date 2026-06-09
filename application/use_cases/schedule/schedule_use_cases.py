from domain.entities.schedule import Schedule
from domain.entities.user import User
from infrastructure.database.db import db
from datetime import date, datetime
import urllib.parse

class CreateScheduleUseCase:
    def execute(self, trainer_id, data):
        user = User.query.filter_by(id=data['user_id'], trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        schedule = Schedule(
            trainer_id=trainer_id,
            user_id=data['user_id'],
            date=date.fromisoformat(data['date']),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
            routine_id=data.get('routine_id'),
        )
        db.session.add(schedule)
        db.session.commit()
        return {'message': 'Horario creado', 'schedule': schedule.to_dict()}, 201


class GetTrainerScheduleUseCase:
    def execute(self, trainer_id, date_str=None):
        query = Schedule.query.filter_by(trainer_id=trainer_id)

        if date_str:
            query = query.filter_by(date=date.fromisoformat(date_str))

        schedules = query.order_by(Schedule.date, Schedule.start_time).all()

        result = []
        for s in schedules:
            user = User.query.get(s.user_id)
            result.append({
                'schedule': s.to_dict(),
                'user': user.to_dict() if user else None
            })

        return {'schedules': result}, 200
    
class UpdateScheduleUseCase:
    def execute(self, schedule_id, trainer_id, data):
        schedule = Schedule.query.filter_by(
            id=schedule_id,
            trainer_id=trainer_id
        ).first()
        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        if 'date' in data:
            schedule.date = date.fromisoformat(data['date'])
        if 'start_time' in data:
            schedule.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        if 'end_time' in data:
            schedule.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        if 'routine_id' in data:
            schedule.routine_id = data['routine_id']

        db.session.commit()
        return {'message': 'Horario actualizado', 'schedule': schedule.to_dict()}, 200


class ConfirmScheduleUseCase:
    def execute(self, schedule_id, trainer_id):
        schedule = Schedule.query.filter_by(
            id=schedule_id,
            trainer_id=trainer_id
        ).first()
        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        schedule.confirmed = True
        db.session.commit()
        return {'message': 'Asistencia confirmada', 'schedule': schedule.to_dict()}, 200


class DeleteScheduleUseCase:
    def execute(self, schedule_id, trainer_id):
        schedule = Schedule.query.filter_by(
            id=schedule_id,
            trainer_id=trainer_id
        ).first()
        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        db.session.delete(schedule)
        db.session.commit()
        return {'message': 'Horario eliminado'}, 200


class SendWhatsAppConfirmationUseCase:
    def execute(self, schedule_id, trainer_id):
        schedule = Schedule.query.filter_by(
            id=schedule_id,
            trainer_id=trainer_id
        ).first()
        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        user = User.query.get(schedule.user_id)
        if not user or not user.phone:
            return {'error': 'El usuario no tiene número de teléfono registrado'}, 400

        # Limpiar número de teléfono (solo dígitos)
        phone = ''.join(filter(str.isdigit, user.phone))

        # Si el número es colombiano y no tiene código de país, agregar 57
        if len(phone) == 10:
            phone = '57' + phone

        message = (
            f"Hola {user.name} 👋, te recuerdo que tienes entrenamiento "
            f"el {schedule.date} a las {schedule.start_time.strftime('%H:%M')}. "
            f"¿Vas a asistir? Por favor confírmame 💪"
        )

        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"

        return {
            'whatsapp_url': whatsapp_url,
            'user': user.to_dict(),
            'schedule': schedule.to_dict()
        }, 200
    
class CancelScheduleAsUserUseCase:
    def execute(self, schedule_id, user_id, reason=None):
        schedule = Schedule.query.filter_by(
            id=schedule_id,
            user_id=user_id
        ).first()
        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        if schedule.cancelled:
            return {'error': 'Este horario ya fue cancelado'}, 400

        schedule.cancelled = True
        schedule.cancel_reason = reason
        schedule.cancelled_by = 'user'
        db.session.commit()

        # Generar link de WhatsApp al entrenador
        from domain.entities.trainer import Trainer
        trainer = Trainer.query.get(schedule.trainer_id)
        user = User.query.get(user_id)

        whatsapp_url = None
        if trainer and trainer.phone:
            phone = ''.join(filter(str.isdigit, trainer.phone))
            if len(phone) == 10:
                phone = '57' + phone

            message = (
                f"Hola, soy {user.name} {user.last_name} 👋. "
                f"Lamentablemente debo cancelar mi entrenamiento "
                f"del {schedule.date} a las {schedule.start_time.strftime('%H:%M')}. "
                f"Motivo: {reason or 'Sin motivo especificado'}. "
                f"Disculpa los inconvenientes 🙏"
            )
            encoded = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{phone}?text={encoded}"

        return {
            'message': 'Entrenamiento cancelado',
            'schedule': schedule.to_dict(),
            'whatsapp_url': whatsapp_url
        }, 200


class CancelScheduleAsTrainerUseCase:
    def execute(self, schedule_id, trainer_id, reason=None):
        schedule = Schedule.query.filter_by(
            id=schedule_id,
            trainer_id=trainer_id
        ).first()
        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        if schedule.cancelled:
            return {'error': 'Este horario ya fue cancelado'}, 400

        schedule.cancelled = True
        schedule.cancel_reason = reason
        schedule.cancelled_by = 'trainer'
        db.session.commit()

        # Generar link de WhatsApp al usuario
        user = User.query.get(schedule.user_id)

        whatsapp_url = None
        if user and user.phone:
            phone = ''.join(filter(str.isdigit, user.phone))
            if len(phone) == 10:
                phone = '57' + phone

            message = (
                f"Hola {user.name} 👋, lamentablemente debo cancelar "
                f"tu entrenamiento del {schedule.date} "
                f"a las {schedule.start_time.strftime('%H:%M')}. "
                f"Motivo: {reason or 'Sin motivo especificado'}. "
                f"Pronto te reagendo 💪"
            )
            encoded = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{phone}?text={encoded}"

        return {
            'message': 'Entrenamiento cancelado',
            'schedule': schedule.to_dict(),
            'whatsapp_url': whatsapp_url
        }, 200
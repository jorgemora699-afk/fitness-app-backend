from domain.entities.schedule import Schedule
from domain.entities.user import User
from infrastructure.database.db import db
from datetime import date, datetime, timedelta
import urllib.parse
import requests

class CreateScheduleUseCase:
    def execute(self, trainer_id, data):
        user = User.query.filter_by(
            id=data['user_id'],
            trainer_id=trainer_id
        ).first()

        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        start_date = date.fromisoformat(data['date'])

        repeat_days = data.get('repeat_days', [])
        repeat_until = data.get('repeat_until')

        start_time = datetime.strptime(
            data['start_time'],
            '%H:%M'
        ).time()

        end_time = datetime.strptime(
            data['end_time'],
            '%H:%M'
        ).time()

        created = []

        # Sin repetición
        if not repeat_days:

            exists = Schedule.query.filter_by(
                user_id=data['user_id'],
                date=start_date,
                start_time=start_time
            ).first()

            if exists:
                return {
                    'error': 'Este usuario ya tiene un entrenamiento programado en esa fecha y hora'
                }, 400

            schedule = Schedule(
                trainer_id=trainer_id,
                user_id=data['user_id'],
                date=start_date,
                start_time=start_time,
                end_time=end_time,
                routine_id=data.get('routine_id'),
                session_type=data.get('session_type', 'Entrenamiento'),
            )

            db.session.add(schedule)
            created.append(schedule)

        # Con repetición semanal
        else:

            end_date = date.fromisoformat(repeat_until)

            current = start_date

            while current <= end_date:

                python_days = [(d - 1) % 7 for d in repeat_days]

                if current.weekday() in python_days:

                    exists = Schedule.query.filter_by(
                        user_id=data['user_id'],
                        date=current,
                        start_time=start_time
                    ).first()

                    if not exists:

                        schedule = Schedule(
                            trainer_id=trainer_id,
                            user_id=data['user_id'],
                            date=current,
                            start_time=start_time,
                            end_time=end_time,
                            routine_id=data.get('routine_id'),
                            session_type=data.get('session_type', 'Entrenamiento'),
                        )

                        db.session.add(schedule)
                        created.append(schedule)

                current += timedelta(days=1)

        db.session.commit()

        if len(created) == 0:
            return {
                'error': 'Todos los horarios seleccionados ya existen'
            }, 400

        return {
            'message': f'{len(created)} horarios creados'
        }, 201


class GetTrainerScheduleUseCase:
    def execute(self, trainer_id, date_str=None, user_id=None):
        query = Schedule.query.filter_by(trainer_id=trainer_id)

        if date_str:
            query = query.filter_by(date=date.fromisoformat(date_str))

        if user_id:
            query = query.filter_by(user_id=user_id)

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

        new_date = (
            date.fromisoformat(data['date'])
            if 'date' in data
            else schedule.date
        )

        new_start_time = (
            datetime.strptime(
                data['start_time'],
                '%H:%M'
            ).time()
            if 'start_time' in data
            else schedule.start_time
        )

        exists = Schedule.query.filter(
            Schedule.id != schedule.id,
            Schedule.user_id == schedule.user_id,
            Schedule.date == new_date,
            Schedule.start_time == new_start_time
        ).first()

        if exists:
            return {
                'error': 'Este usuario ya tiene un entrenamiento programado en esa fecha y hora'
            }, 400

        if 'date' in data:
            schedule.date = new_date

        if 'start_time' in data:
            schedule.start_time = new_start_time

        if 'end_time' in data:
            schedule.end_time = datetime.strptime(
                data['end_time'],
                '%H:%M'
            ).time()

        if 'routine_id' in data:
            schedule.routine_id = data['routine_id']
        
        if 'session_type' in data:
            schedule.session_type = data['session_type']

        db.session.commit()

        return {
            'message': 'Horario actualizado',
            'schedule': schedule.to_dict()
        }, 200


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
    
class NotifyScheduleUseCase:
    def execute(self, schedule_id, trainer_id):
        schedule = Schedule.query.filter_by(
            id=schedule_id,
            trainer_id=trainer_id
        ).first()
        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        user = User.query.get(schedule.user_id)
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        if not user.push_token:
            return {'error': 'El usuario no tiene notificaciones activadas'}, 400

        message = {
            'to': user.push_token,
            'sound': 'default',
            'title': 'Entrenamiento programado 💪',
            'body': f'Tienes entrenamiento el {schedule.date} a las {schedule.start_time.strftime("%H:%M")}. ¿Vas a asistir?',
            'data': {
                'type': 'schedule_confirmation',
                'schedule_id': schedule.id
            }
        }

        try:
            response = requests.post(
                'https://exp.host/--/api/v2/push/send',
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
        except Exception as e:
            return {'error': f'Error enviando notificación: {str(e)}'}, 500

        schedule.notified = True
        schedule.user_response = 'pending'
        db.session.commit()

        return {'message': 'Notificación enviada', 'schedule': schedule.to_dict()}, 200


class RespondScheduleUseCase:
    def execute(self, schedule_id, user_id, response):
        if response not in ['confirmed', 'declined']:
            return {'error': 'Respuesta inválida'}, 400

        schedule = Schedule.query.filter_by(
            id=schedule_id,
            user_id=user_id
        ).first()
        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        schedule.user_response = response
        if response == 'confirmed':
            schedule.confirmed = True

        db.session.commit()
        return {'message': 'Respuesta registrada', 'schedule': schedule.to_dict()}, 200


class MarkAttendanceUseCase:
    def execute(self, schedule_id, trainer_id, attended):
        schedule = Schedule.query.filter_by(
            id=schedule_id,
            trainer_id=trainer_id
        ).first()
        if not schedule:
            return {'error': 'Horario no encontrado'}, 404

        schedule.attended = attended
        db.session.commit()

        # Registrar en la tabla de asistencia
        from domain.entities.attendance import Attendance
        existing = Attendance.query.filter_by(
            user_id=schedule.user_id,
            date=schedule.date
        ).first()

        if existing:
            existing.attended = attended
        else:
            attendance = Attendance(
                user_id=schedule.user_id,
                trainer_id=trainer_id,
                date=schedule.date,
                attended=attended
            )
            db.session.add(attendance)

        db.session.commit()
        return {'message': 'Asistencia registrada', 'schedule': schedule.to_dict()}, 200


class GetPendingSchedulesUseCase:
    def execute(self, user_id):
        schedules = Schedule.query.filter_by(
            user_id=user_id,
            user_response='pending',
            cancelled=False
        ).filter(Schedule.notified == True).all()

        return {'schedules': [s.to_dict() for s in schedules]}, 200
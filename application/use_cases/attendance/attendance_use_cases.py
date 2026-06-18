from domain.entities.attendance import Attendance
from domain.entities.user import User
from infrastructure.database.db import db
from datetime import date, timedelta
import urllib.parse

class RegisterAttendanceUseCase:
    def execute(self, trainer_id, data):
        user = User.query.filter_by(id=data['user_id'], trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        attendance_date = date.fromisoformat(data['date']) if data.get('date') else date.today()

        # Verificar si ya existe registro para ese día
        existing = Attendance.query.filter_by(
            user_id=data['user_id'],
            date=attendance_date
        ).first()
        if existing:
            return {'error': 'Ya existe un registro de asistencia para este día'}, 400

        attendance = Attendance(
            user_id=data['user_id'],
            trainer_id=trainer_id,
            date=attendance_date,
            attended=data.get('attended', True),
            notes=data.get('notes')
        )
        db.session.add(attendance)
        db.session.commit()
        return {'message': 'Asistencia registrada', 'attendance': attendance.to_dict()}, 201


class GetUserAttendanceUseCase:
    def execute(self, user_id, trainer_id, month=None, year=None):
        user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        query = Attendance.query.filter_by(user_id=user_id)

        if month and year:
            query = query.filter(
                db.extract('month', Attendance.date) == month,
                db.extract('year', Attendance.date) == year
            )

        attendances = query.order_by(Attendance.date.desc()).all()

        total = len(attendances)
        attended = sum(1 for a in attendances if a.attended)
        missed = total - attended

        return {
            'user': user.to_dict(),
            'attendances': [a.to_dict() for a in attendances],
            'summary': {
                'total': total,
                'attended': attended,
                'missed': missed,
                'attendance_rate': round((attended / total * 100), 2) if total > 0 else 0
            }
        }, 200


class GetMyAttendanceUseCase:
    def execute(self, user_id, month=None, year=None):
        query = Attendance.query.filter_by(user_id=user_id)

        if month and year:
            query = query.filter(
                db.extract('month', Attendance.date) == month,
                db.extract('year', Attendance.date) == year
            )

        attendances = query.order_by(Attendance.date.desc()).all()

        total = len(attendances)
        attended = sum(1 for a in attendances if a.attended)

        return {
            'attendances': [a.to_dict() for a in attendances],
            'summary': {
                'total': total,
                'attended': attended,
                'missed': total - attended,
                'attendance_rate': round((attended / total * 100), 2) if total > 0 else 0
            }
        }, 200


class GetInactiveUsersUseCase:
    def execute(self, trainer_id, days=7):
        today = date.today()
        threshold = today - timedelta(days=days)

        users = User.query.filter_by(trainer_id=trainer_id).all()

        inactive = []
        for user in users:
            last_attendance = Attendance.query.filter_by(
                user_id=user.id,
                attended=True
            ).order_by(Attendance.date.desc()).first()

            if not last_attendance or last_attendance.date <= threshold:
                days_absent = (today - last_attendance.date).days if last_attendance else None

                # Generar link de WhatsApp
                whatsapp_url = None
                if user.phone:
                    phone = ''.join(filter(str.isdigit, user.phone))
                    if len(phone) == 10:
                        phone = '57' + phone

                    if days_absent:
                        message = (
                            f"Hola {user.name}, espero que estés bien. "
                            f"Quería hacerte un seguimiento ya que han pasado {days_absent} día(s) "
                            f"desde tu último entrenamiento registrado. "
                            f"Si necesitas reprogramar tu sesión o ajustar tu plan, con gusto te ayudo. "
                            f"Quedo atento."
                        )
                    else:
                        message = (
                            f"Hola {user.name}, te escribo para darle seguimiento al inicio de tu plan de entrenamiento. "
                            f"Cuando tengas disponibilidad, podemos coordinar tu primera sesión. "
                            f"Quedo atento."
                        )

                    encoded = urllib.parse.quote(message)
                    whatsapp_url = f"https://wa.me/{phone}?text={encoded}"

                inactive.append({
                    'user': user.to_dict(),
                    'last_attendance': last_attendance.to_dict() if last_attendance else None,
                    'days_absent': days_absent,
                    'whatsapp_url': whatsapp_url
                })

        return {
            'inactive_users': inactive,
            'total': len(inactive),
            'days_threshold': days
        }, 200


class GetAllUsersAttendanceSummaryUseCase:
    def execute(self, trainer_id, month=None, year=None):
        today = date.today()
        month = month or today.month
        year = year or today.year

        users = User.query.filter_by(trainer_id=trainer_id).all()

        summary = []
        for user in users:
            attendances = Attendance.query.filter(
                Attendance.user_id == user.id,
                db.extract('month', Attendance.date) == month,
                db.extract('year', Attendance.date) == year
            ).all()

            total = len(attendances)
            attended = sum(1 for a in attendances if a.attended)

            summary.append({
                'user': user.to_dict(),
                'total': total,
                'attended': attended,
                'missed': total - attended,
                'attendance_rate': round((attended / total * 100), 2) if total > 0 else 0
            })

        return {
            'month': month,
            'year': year,
            'users': summary
        }, 200
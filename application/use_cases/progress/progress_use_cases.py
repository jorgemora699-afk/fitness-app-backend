from domain.entities.body_record import BodyRecord
from domain.entities.routine import Routine, Exercise
from domain.entities.user import User
from infrastructure.database.db import db
from datetime import date
from sqlalchemy import func

class AddBodyRecordUseCase:
    def execute(self, user_id, data):
        from datetime import date
        today = date.today()
        recorded_at = date.fromisoformat(data['recorded_at']) if data.get('recorded_at') else today

        # Evitar duplicado en el mismo segundo
        existing = BodyRecord.query.filter_by(
            user_id=user_id,
            weight=data['weight'],
            recorded_at=recorded_at
        ).first()

        if existing:
            return {'message': 'Registro ya existe', 'record': existing.to_dict()}, 200

        record = BodyRecord(
            user_id=user_id,
            weight=data['weight'],
            body_fat=data.get('body_fat'),
            muscle_mass=data.get('muscle_mass'),
            recorded_at=date.fromisoformat(data['recorded_at']) if data.get('recorded_at') else date.today()
        )
        db.session.add(record)
        # Actualizar peso en el perfil del usuario
        user = User.query.get(user_id)
        if user:
            user.weight = data['weight']
            if data.get('body_fat'):
                user.body_fat = data['body_fat']
            if data.get('muscle_mass'):
                user.muscle_mass = data['muscle_mass']
        db.session.commit()
        return {'message': 'Registro agregado', 'record': record.to_dict()}, 201


class GetBodyProgressUseCase:
    def execute(self, user_id):
        records = BodyRecord.query.filter_by(user_id=user_id).order_by(
            BodyRecord.recorded_at.asc()
        ).all()

        if not records:
            return {'records': [], 'summary': None}, 200

        weights = [r.weight for r in records]
        summary = {
            'initial_weight': weights[0],
            'current_weight': weights[-1],
            'difference': round(weights[-1] - weights[0], 2),
            'min_weight': min(weights),
            'max_weight': max(weights),
            'total_records': len(records)
        }

        return {
            'records': [r.to_dict() for r in records],
            'summary': summary
        }, 200


class GetExerciseProgressUseCase:
    def execute(self, user_id, exercise_name):
        routines = Routine.query.filter_by(user_id=user_id).order_by(
            Routine.created_at.asc()
        ).all()

        progress = []
        for routine in routines:
            exercises = Exercise.query.filter(
                Exercise.routine_id == routine.id,
                Exercise.name.ilike(f'%{exercise_name}%')
            ).all()

            for ex in exercises:
                if ex.weight or ex.reps:
                    volume = (ex.sets or 0) * (ex.reps or 0) * (ex.weight or 0)
                    progress.append({
                        'date': routine.created_at.isoformat(),
                        'exercise': ex.to_dict(),
                        'volume': round(volume, 2)
                    })

        if not progress:
            return {'error': f'No hay datos para el ejercicio: {exercise_name}'}, 404

        weights = [p['exercise']['weight'] for p in progress if p['exercise']['weight']]
        summary = {
            'exercise_name': exercise_name,
            'total_sessions': len(progress),
            'initial_weight': weights[0] if weights else None,
            'current_weight': weights[-1] if weights else None,
            'max_weight': max(weights) if weights else None,
            'improvement': round(weights[-1] - weights[0], 2) if len(weights) > 1 else 0
        }

        return {
            'progress': progress,
            'summary': summary
        }, 200


class GetUserProgressAsTrainerUseCase:
    def execute(self, user_id, trainer_id):
        user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        records = BodyRecord.query.filter_by(user_id=user_id).order_by(
            BodyRecord.recorded_at.asc()
        ).all()

        weights = [r.weight for r in records]
        body_summary = None
        if weights:
            body_summary = {
                'initial_weight': weights[0],
                'current_weight': weights[-1],
                'difference': round(weights[-1] - weights[0], 2),
                'total_records': len(records)
            }

        total_routines = Routine.query.filter_by(user_id=user_id).count()

        return {
            'user': user.to_dict(),
            'body_progress': {
                'records': [r.to_dict() for r in records],
                'summary': body_summary
            },
            'routines_this_month': total_routines
        }, 200


class GetIMCUseCase:
    def execute(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        if not user.weight or not user.height:
            return {'error': 'El usuario no tiene peso y altura registrados'}, 400

        height_m = user.height / 100 if user.height > 3 else user.height
        imc = round(user.weight / (height_m ** 2), 2)

        if imc < 18.5:
            category = 'Bajo peso'
        elif imc < 25:
            category = 'Peso normal'
        elif imc < 30:
            category = 'Sobrepeso'
        else:
            category = 'Obesidad'

        return {
            'imc': imc,
            'category': category,
            'weight': user.weight,
            'height': user.height
        }, 200
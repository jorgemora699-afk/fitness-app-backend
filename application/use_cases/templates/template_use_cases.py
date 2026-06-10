from domain.entities.routine_template import RoutineTemplate, TemplateExercise, AssignedWorkout
from domain.entities.user import User
from infrastructure.database.db import db
from datetime import datetime


class CreateTemplateUseCase:
    def execute(self, trainer_id, data):
        template = RoutineTemplate(
            trainer_id=trainer_id,
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(template)
        db.session.flush()

        for ex in data.get('exercises', []):
            exercise = TemplateExercise(
                template_id=template.id,
                name=ex['name'],
                sets=ex.get('sets'),
                reps=ex.get('reps'),
                weight=ex.get('weight'),
                notes=ex.get('notes')
            )
            db.session.add(exercise)

        db.session.commit()
        return {'message': 'Plantilla creada', 'template': template.to_dict()}, 201


class GetMyTemplatesUseCase:
    def execute(self, trainer_id):
        templates = RoutineTemplate.query.filter_by(trainer_id=trainer_id).order_by(
            RoutineTemplate.created_at.desc()
        ).all()
        return {'templates': [t.to_dict() for t in templates]}, 200


class GetTemplateByIdUseCase:
    def execute(self, template_id, trainer_id):
        template = RoutineTemplate.query.filter_by(
            id=template_id,
            trainer_id=trainer_id
        ).first()
        if not template:
            return {'error': 'Plantilla no encontrada'}, 404
        return {'template': template.to_dict()}, 200


class UpdateTemplateUseCase:
    def execute(self, template_id, trainer_id, data):
        template = RoutineTemplate.query.filter_by(
            id=template_id,
            trainer_id=trainer_id
        ).first()
        if not template:
            return {'error': 'Plantilla no encontrada'}, 404

        template.name = data.get('name', template.name)
        template.description = data.get('description', template.description)

        if 'exercises' in data:
            for ex in template.exercises:
                db.session.delete(ex)
            db.session.flush()

            for ex in data['exercises']:
                exercise = TemplateExercise(
                    template_id=template.id,
                    name=ex['name'],
                    sets=ex.get('sets'),
                    reps=ex.get('reps'),
                    weight=ex.get('weight'),
                    notes=ex.get('notes')
                )
                db.session.add(exercise)

        db.session.commit()
        return {'message': 'Plantilla actualizada', 'template': template.to_dict()}, 200


class DeleteTemplateUseCase:
    def execute(self, template_id, trainer_id):
        template = RoutineTemplate.query.filter_by(
            id=template_id,
            trainer_id=trainer_id
        ).first()
        if not template:
            return {'error': 'Plantilla no encontrada'}, 404

        db.session.delete(template)
        db.session.commit()
        return {'message': 'Plantilla eliminada'}, 200


class AssignTemplateToUserUseCase:
    def execute(self, template_id, trainer_id, data):
        template = RoutineTemplate.query.filter_by(
            id=template_id,
            trainer_id=trainer_id
        ).first()
        if not template:
            return {'error': 'Plantilla no encontrada'}, 404

        user_ids = data.get('user_ids', [])
        dates = data.get('dates', [])

        if not user_ids or not dates:
            return {'error': 'Se requieren user_ids y dates'}, 400

        users = User.query.filter(
            User.id.in_(user_ids),
            User.trainer_id == trainer_id
        ).all()

        if len(users) != len(user_ids):
            return {'error': 'Uno o más usuarios no encontrados'}, 404

        created = []

        for user_id in user_ids:
            for date_str in dates:
                try:
                    assigned_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'error': f'Fecha inválida: {date_str}'}, 400

                assigned = AssignedWorkout(
                    user_id=user_id,
                    template_id=template.id,
                    assigned_date=assigned_date,
                    status='pending'
                )
                db.session.add(assigned)
                created.append(assigned)

        db.session.commit()

        return {
            'message': f'Plantilla asignada correctamente ({len(created)} registros creados)',
            'assigned_workouts': [a.to_dict() for a in created]
        }, 201
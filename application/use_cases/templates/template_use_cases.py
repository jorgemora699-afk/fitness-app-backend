from domain.entities.routine_template import RoutineTemplate, TemplateExercise
from domain.entities.routine import Routine, Exercise
from domain.entities.user import User
from infrastructure.database.db import db
from datetime import date

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

        # Si vienen ejercicios nuevos, reemplazar los anteriores
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

        # Verificar que todos los usuarios pertenecen al entrenador
        user_ids = data.get('user_ids', [])
        dates = data.get('dates', [])

        if not user_ids or not dates:
            return {'error': 'Se requieren user_ids y dates'}, 400

        routines_created = []

        for user_id in user_ids:
            user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
            if not user:
                continue

            for date_str in dates:
                # Verificar si ya existe rutina en esa fecha para ese usuario
                existing = Routine.query.filter_by(
                    user_id=user_id,
                    date=date.fromisoformat(date_str)
                ).first()
                if existing:
                    continue

                routine = Routine(
                    user_id=user_id,
                    trainer_id=trainer_id,
                    date=date.fromisoformat(date_str),
                    name=template.name,
                    notes=template.description
                )
                db.session.add(routine)
                db.session.flush()

                for tex in template.exercises:
                    exercise = Exercise(
                        routine_id=routine.id,
                        name=tex.name,
                        sets=tex.sets,
                        reps=tex.reps,
                        weight=tex.weight,
                        notes=tex.notes
                    )
                    db.session.add(exercise)

                routines_created.append({
                    'user': user.to_dict(),
                    'date': date_str,
                    'routine': routine.to_dict()
                })

        db.session.commit()
        return {
            'message': f'{len(routines_created)} rutina(s) creada(s) desde la plantilla',
            'routines': routines_created
        }, 201
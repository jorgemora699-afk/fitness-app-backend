from domain.entities.trainer_note import TrainerNote
from domain.entities.user import User
from infrastructure.database.db import db

class CreateNoteUseCase:
    def execute(self, trainer_id, data):
        user = User.query.filter_by(id=data['user_id'], trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        note = TrainerNote(
            trainer_id=trainer_id,
            user_id=data['user_id'],
            title=data['title'],
            content=data['content'],
            category=data.get('category', 'otro')
        )
        db.session.add(note)
        db.session.commit()
        return {'message': 'Nota creada', 'note': note.to_dict()}, 201


class GetNotesByUserUseCase:
    def execute(self, trainer_id, user_id, category=None):
        user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
        if not user:
            return {'error': 'Usuario no encontrado'}, 404

        query = TrainerNote.query.filter_by(
            trainer_id=trainer_id,
            user_id=user_id
        )
        if category:
            query = query.filter_by(category=category)

        notes = query.order_by(TrainerNote.created_at.desc()).all()
        return {
            'user': user.to_dict(),
            'notes': [n.to_dict() for n in notes],
            'total': len(notes)
        }, 200


class UpdateNoteUseCase:
    def execute(self, note_id, trainer_id, data):
        note = TrainerNote.query.filter_by(
            id=note_id,
            trainer_id=trainer_id
        ).first()
        if not note:
            return {'error': 'Nota no encontrada'}, 404

        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        note.category = data.get('category', note.category)

        db.session.commit()
        return {'message': 'Nota actualizada', 'note': note.to_dict()}, 200


class DeleteNoteUseCase:
    def execute(self, note_id, trainer_id):
        note = TrainerNote.query.filter_by(
            id=note_id,
            trainer_id=trainer_id
        ).first()
        if not note:
            return {'error': 'Nota no encontrada'}, 404

        db.session.delete(note)
        db.session.commit()
        return {'message': 'Nota eliminada'}, 200


class GetAllNotesUseCase:
    def execute(self, trainer_id, category=None):
        query = TrainerNote.query.filter_by(trainer_id=trainer_id)
        if category:
            query = query.filter_by(category=category)

        notes = query.order_by(TrainerNote.created_at.desc()).all()

        # Agrupar por usuario
        grouped = {}
        for note in notes:
            user_id = note.user_id
            if user_id not in grouped:
                user = User.query.get(user_id)
                grouped[user_id] = {
                    'user': user.to_dict() if user else None,
                    'notes': []
                }
            grouped[user_id]['notes'].append(note.to_dict())

        return {
            'notes_by_user': list(grouped.values()),
            'total': len(notes)
        }, 200
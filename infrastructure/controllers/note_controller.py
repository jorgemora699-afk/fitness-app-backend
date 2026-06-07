from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.notes.note_use_cases import (
    CreateNoteUseCase,
    GetNotesByUserUseCase,
    UpdateNoteUseCase,
    DeleteNoteUseCase,
    GetAllNotesUseCase
)

note_bp = Blueprint('notes', __name__, url_prefix='/api/notes')

def get_role():
    return get_jwt().get('role')

# ── Entrenador: crear nota sobre un usuario ──
@note_bp.route('/', methods=['POST'])
@jwt_required()
def create_note():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    if not all(k in data for k in ['user_id', 'title', 'content']):
        return jsonify({'error': 'Faltan campos requeridos: user_id, title, content'}), 400
    result, status = CreateNoteUseCase().execute(trainer_id, data)
    return jsonify(result), status

# ── Entrenador: ver todas sus notas agrupadas por usuario ──
@note_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_notes():
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    category = request.args.get('category')
    result, status = GetAllNotesUseCase().execute(trainer_id, category)
    return jsonify(result), status

# ── Entrenador: ver notas de un usuario específico ──
@note_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_notes_by_user(user_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    category = request.args.get('category')
    result, status = GetNotesByUserUseCase().execute(trainer_id, user_id, category)
    return jsonify(result), status

# ── Entrenador: actualizar una nota ──
@note_bp.route('/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    data = request.get_json()
    result, status = UpdateNoteUseCase().execute(note_id, trainer_id, data)
    return jsonify(result), status

# ── Entrenador: eliminar una nota ──
@note_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    if get_role() != 'trainer':
        return jsonify({'error': 'Acceso solo para entrenadores'}), 403
    trainer_id = int(get_jwt_identity())
    result, status = DeleteNoteUseCase().execute(note_id, trainer_id)
    return jsonify(result), status
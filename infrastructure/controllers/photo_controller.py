from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from application.use_cases.photos.photo_use_cases import (
    UploadProgressPhotoUseCase,
    GetMyPhotosUseCase,
    GetPhotosByDateUseCase,
    DeletePhotoUseCase,
    GetPhotosByMonthUseCase,
    ComparePhotosUseCase,
    GetAvailableMonthsUseCase
)

photo_bp = Blueprint('photos', __name__, url_prefix='/api/photos')

def get_role():
    return get_jwt().get('role')

# ── Usuario: subir foto de progreso ──
@photo_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_photo():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())

    file = request.files.get('photo')
    if not file:
        return jsonify({'error': 'No se envió ninguna foto'}), 400

    angle = request.form.get('angle')
    if not angle:
        return jsonify({'error': 'El ángulo es requerido (frontal, lateral, trasera)'}), 400

    taken_at = request.form.get('taken_at')
    result, status = UploadProgressPhotoUseCase().execute(user_id, file, angle, taken_at)
    return jsonify(result), status

# ── Usuario: ver todas sus fotos (opcionalmente filtrar por ángulo) ──
@photo_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_photos():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    angle = request.args.get('angle')
    result, status = GetMyPhotosUseCase().execute(user_id, angle)
    return jsonify(result), status

# ── Usuario: ver fotos por fecha ──
@photo_bp.route('/me/date', methods=['GET'])
@jwt_required()
def get_photos_by_date():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Se requiere el parámetro date (YYYY-MM-DD)'}), 400
    result, status = GetPhotosByDateUseCase().execute(user_id, date_str)
    return jsonify(result), status

# ── Usuario: eliminar una foto ──
@photo_bp.route('/<int:photo_id>', methods=['DELETE'])
@jwt_required()
def delete_photo(photo_id):
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    result, status = DeletePhotoUseCase().execute(photo_id, user_id)
    return jsonify(result), status

# ── Usuario: ver fotos agrupadas por mes ──
@photo_bp.route('/me/months', methods=['GET'])
@jwt_required()
def get_photos_by_month():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    result, status = GetPhotosByMonthUseCase().execute(user_id)
    return jsonify(result), status

# ── Usuario: ver meses disponibles para comparar ──
@photo_bp.route('/me/available-months', methods=['GET'])
@jwt_required()
def get_available_months():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())
    result, status = GetAvailableMonthsUseCase().execute(user_id)
    return jsonify(result), status

# ── Usuario: comparar fotos entre dos meses ──
@photo_bp.route('/me/compare', methods=['GET'])
@jwt_required()
def compare_photos():
    if get_role() != 'user':
        return jsonify({'error': 'Acceso solo para usuarios'}), 403
    user_id = int(get_jwt_identity())

    month1 = request.args.get('month1', type=int)
    year1 = request.args.get('year1', type=int)
    month2 = request.args.get('month2', type=int)
    year2 = request.args.get('year2', type=int)

    if not all([month1, year1, month2, year2]):
        return jsonify({'error': 'Se requieren month1, year1, month2, year2'}), 400

    result, status = ComparePhotosUseCase().execute(user_id, month1, year1, month2, year2)
    return jsonify(result), status
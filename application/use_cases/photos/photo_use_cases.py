from domain.entities.progress_photo import ProgressPhoto
from infrastructure.database.db import db
from datetime import date
import cloudinary
import cloudinary.uploader
import os

def configure_cloudinary():
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )

class UploadProgressPhotoUseCase:
    def execute(self, user_id, file, angle, taken_at=None):
        if angle not in ['frontal', 'lateral', 'trasera']:
            return {'error': 'El ángulo debe ser frontal, lateral o trasera'}, 400

        configure_cloudinary()
        upload = cloudinary.uploader.upload(
            file,
            folder=f'fitness/progress/{user_id}',
            transformation=[
                {'width': 800, 'height': 1200, 'crop': 'limit'},
                {'quality': 'auto'}
            ]
        )

        photo = ProgressPhoto(
            user_id=user_id,
            photo_url=upload.get('secure_url'),
            angle=angle,
            taken_at=date.fromisoformat(taken_at) if taken_at else date.today()
        )
        db.session.add(photo)
        db.session.commit()
        return {'message': 'Foto subida exitosamente', 'photo': photo.to_dict()}, 201


class GetMyPhotosUseCase:
    def execute(self, user_id, angle=None):
        query = ProgressPhoto.query.filter_by(user_id=user_id)
        if angle:
            query = query.filter_by(angle=angle)
        photos = query.order_by(ProgressPhoto.taken_at.desc()).all()
        return {'photos': [p.to_dict() for p in photos]}, 200


class GetPhotosByDateUseCase:
    def execute(self, user_id, date_str):
        photo_date = date.fromisoformat(date_str)
        photos = ProgressPhoto.query.filter_by(
            user_id=user_id,
            taken_at=photo_date
        ).all()
        return {'photos': [p.to_dict() for p in photos]}, 200


class DeletePhotoUseCase:
    def execute(self, photo_id, user_id):
        photo = ProgressPhoto.query.filter_by(
            id=photo_id,
            user_id=user_id
        ).first()
        if not photo:
            return {'error': 'Foto no encontrada'}, 404

        # Eliminar de Cloudinary
        configure_cloudinary()
        public_id = photo.photo_url.split('/')[-1].split('.')[0]
        folder = f'fitness/progress/{user_id}'
        cloudinary.uploader.destroy(f'{folder}/{public_id}')

        db.session.delete(photo)
        db.session.commit()
        return {'message': 'Foto eliminada'}, 200
    
class GetPhotosByMonthUseCase:
    def execute(self, user_id):
        photos = ProgressPhoto.query.filter_by(user_id=user_id).order_by(
            ProgressPhoto.taken_at.asc()
        ).all()

        if not photos:
            return {'months': []}, 200

        # Agrupar por mes y año
        grouped = {}
        for photo in photos:
            key = f"{photo.taken_at.year}-{str(photo.taken_at.month).zfill(2)}"
            if key not in grouped:
                grouped[key] = {
                    'year': photo.taken_at.year,
                    'month': photo.taken_at.month,
                    'photos': {
                        'frontal': None,
                        'lateral': None,
                        'trasera': None
                    }
                }
            grouped[key]['photos'][photo.angle] = photo.to_dict()

        return {
            'months': list(grouped.values()),
            'total_months': len(grouped)
        }, 200


class ComparePhotosUseCase:
    def execute(self, user_id, month1, year1, month2, year2):
        def get_photos_for_month(y, m):
            photos = ProgressPhoto.query.filter(
                ProgressPhoto.user_id == user_id,
                db.extract('year', ProgressPhoto.taken_at) == y,
                db.extract('month', ProgressPhoto.taken_at) == m
            ).all()
            result = {'frontal': None, 'lateral': None, 'trasera': None}
            for p in photos:
                result[p.angle] = p.to_dict()
            return result

        period1 = get_photos_for_month(year1, month1)
        period2 = get_photos_for_month(year2, month2)

        if not any(period1.values()):
            return {'error': f'No hay fotos para {year1}-{str(month1).zfill(2)}'}, 404
        if not any(period2.values()):
            return {'error': f'No hay fotos para {year2}-{str(month2).zfill(2)}'}, 404

        return {
            'comparison': {
                'period_1': {
                    'year': year1,
                    'month': month1,
                    'photos': period1
                },
                'period_2': {
                    'year': year2,
                    'month': month2,
                    'photos': period2
                }
            }
        }, 200


class GetAvailableMonthsUseCase:
    def execute(self, user_id):
        photos = ProgressPhoto.query.filter_by(user_id=user_id).order_by(
            ProgressPhoto.taken_at.asc()
        ).all()

        months = {}
        for photo in photos:
            key = f"{photo.taken_at.year}-{str(photo.taken_at.month).zfill(2)}"
            if key not in months:
                months[key] = {
                    'year': photo.taken_at.year,
                    'month': photo.taken_at.month,
                    'angles': []
                }
            if photo.angle not in months[key]['angles']:
                months[key]['angles'].append(photo.angle)

        return {
            'available_months': list(months.values()),
            'total': len(months)
        }, 200
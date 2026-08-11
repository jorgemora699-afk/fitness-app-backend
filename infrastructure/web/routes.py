from infrastructure.controllers.auth_controller import auth_bp
from infrastructure.controllers.user_controller import user_bp
from infrastructure.controllers.membership_controller import membership_bp
from infrastructure.controllers.routine_controller import routine_bp
from infrastructure.controllers.schedule_controller import schedule_bp
from infrastructure.controllers.photo_controller import photo_bp
from infrastructure.controllers.notification_controller import notification_bp
from infrastructure.controllers.template_controller import template_bp
from infrastructure.controllers.progress_controller import progress_bp
from infrastructure.controllers.attendance_controller import attendance_bp
from infrastructure.controllers.note_controller import note_bp
from infrastructure.controllers.assigned_workout_controller import assigned_workout_bp
from infrastructure.controllers.workout_session_controller import session_bp
from infrastructure.controllers.admin_controller import admin_bp
from infrastructure.controllers.account_controller import account_bp

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from datetime import date

def check_trainer_subscription(app):
    @app.before_request
    def verify_subscription():
        from flask import request
        
        if not request.path.startswith('/api/') or request.path.startswith('/api/auth') or request.path.startswith('/api/admin'):
            return
        
        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            if claims.get('role') != 'trainer':
                return
            
            trainer_id = int(get_jwt_identity())
            
            from domain.entities.trainer import Trainer
            trainer = Trainer.query.get(trainer_id)
            
            if not trainer or not trainer.is_active:
                return jsonify({
                    'error': 'Tu cuenta ha sido desactivada. Contacta al administrador.',
                    'code': 'ACCOUNT_DEACTIVATED'
                }), 403
            
            from domain.entities.trainer_subscription import TrainerSubscription
            today = date.today()
            
            latest = TrainerSubscription.query.filter_by(
                trainer_id=trainer_id
            ).order_by(TrainerSubscription.due_date.desc()).first()
            
            if latest and latest.due_date < today:
                return jsonify({
                    'error': 'Tu suscripción ha vencido.',
                    'code': 'SUBSCRIPTION_EXPIRED'
                }), 403
                
        except Exception:
            return

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(membership_bp)
    app.register_blueprint(routine_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(photo_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(template_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(note_bp)
    app.register_blueprint(assigned_workout_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(admin_bp)
    check_trainer_subscription(app)
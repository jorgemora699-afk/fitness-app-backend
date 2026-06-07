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

def register_routes(app):
    app.register_blueprint(auth_bp)
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
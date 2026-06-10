from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import Config
from infrastructure.database.db import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    JWTManager(app)

    db.init_app(app)
    Migrate(app, db)

    from domain.entities.user import User
    from domain.entities.trainer import Trainer
    from domain.entities.routine import Routine, Exercise
    from domain.entities.membership import Membership
    from domain.entities.schedule import Schedule
    from domain.entities.progress_photo import ProgressPhoto
    from domain.entities.routine_template import RoutineTemplate, TemplateExercise
    from domain.entities.body_record import BodyRecord
    from domain.entities.attendance import Attendance
    from domain.entities.trainer_note import TrainerNote
    from domain.entities.routine_template import ExerciseLog
    from domain.entities.WorkoutSession import WorkoutSession, SessionExerciseLog

    from infrastructure.web.routes import register_routes
    register_routes(app)

    # Iniciar scheduler
    from infrastructure.web.scheduler import init_scheduler
    init_scheduler(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
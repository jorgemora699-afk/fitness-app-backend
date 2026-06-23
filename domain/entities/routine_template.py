from infrastructure.database.db import db
from datetime import datetime

class RoutineTemplate(db.Model):
    __tablename__ = 'routine_templates'

    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exercises = db.relationship('TemplateExercise', backref='template', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'name': self.name,
            'description': self.description,
            'exercises': [e.to_dict() for e in self.exercises],
            'created_at': self.created_at.isoformat()
        }


class TemplateExercise(db.Model):
    __tablename__ = 'template_exercises'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('routine_templates.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(500),nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'name': self.name,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight,
            'notes': self.notes,
            'video_url': self.video_url
        }
    
class AssignedWorkout(db.Model):
    __tablename__ = 'assigned_workouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('routine_templates.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, skipped
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    template = db.relationship('RoutineTemplate', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'template_id': self.template_id,
            'template_name': self.template.name if self.template else None,
            'status': self.status,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class ExerciseLog(db.Model):
    __tablename__ = 'exercise_logs'

    id = db.Column(db.Integer, primary_key=True)
    assigned_workout_id = db.Column(db.Integer, db.ForeignKey('assigned_workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('template_exercises.id'), nullable=False)
    performed_sets = db.Column(db.Integer)
    performed_reps = db.Column(db.Integer)
    performed_weight = db.Column(db.Float)
    performed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'assigned_workout_id': self.assigned_workout_id,
            'exercise_id': self.exercise_id,
            'performed_sets': self.performed_sets,
            'performed_reps': self.performed_reps,
            'performed_weight': self.performed_weight,
            'performed_at': self.performed_at.isoformat()
        }
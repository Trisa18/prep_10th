from app import db
from datetime import datetime
import json

class QuizSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    score_percentage = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    
    # Relationship to questions
    questions = db.relationship('Question', backref='quiz_session', lazy=True, cascade='all, delete-orphan')
    
    def calculate_score(self):
        if self.total_questions > 0:
            self.score_percentage = (self.correct_answers / self.total_questions) * 100
        else:
            self.score_percentage = 0.0
        return self.score_percentage
    
    def get_duration_minutes(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return round(duration.total_seconds() / 60, 2)
        return 0

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_session_id = db.Column(db.Integer, db.ForeignKey('quiz_session.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options_json = db.Column(db.Text, nullable=False)  # JSON string of options
    correct_answer = db.Column(db.String(10), nullable=False)  # A, B, C, or D
    student_answer = db.Column(db.String(10))  # A, B, C, D, or None
    is_correct = db.Column(db.Boolean, default=False)
    question_number = db.Column(db.Integer, nullable=False)
    
    def get_options(self):
        try:
            return json.loads(self.options_json)
        except:
            return {}
    
    def set_options(self, options_dict):
        self.options_json = json.dumps(options_dict)
    
    def check_answer(self, answer):
        self.student_answer = answer
        self.is_correct = (answer == self.correct_answer)
        return self.is_correct

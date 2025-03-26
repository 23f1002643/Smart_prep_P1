from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import declarative_base
from datetime import datetime

db = SQLAlchemy()  
# Base = declarative_base()

class Account(db.Model):
    __tablename__ = 'Users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    f_name = db.Column(db.String(80), nullable=False)
    l_name = db.Column(db.String(80), nullable=False)
    pwd = db.Column(db.String(130), nullable=False)
    edu_qul = db.Column(db.String(120), nullable=False)
    mobile_no = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(100), default="user")
    active = db.Column(db.Boolean, default=True)
    
    # Relationship with Score table
    scores = db.relationship('ExamPerformance', back_populates='user', cascade='all, delete-orphan')

class Courses(db.Model):
    __tablename__ = 'Course_Area' #Subject
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    s_name = db.Column(db.String(80), nullable=False)
    remarks = db.Column(db.Text, nullable=False)
    
    # Relationship with Chapter table
    chapters = db.relationship('CourseModule', back_populates='course', cascade="all, delete-orphan")

class CourseModule(db.Model):
    __tablename__ = 'Chapters'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('Course_Area.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Relationships
    course = db.relationship('Courses', back_populates='chapters')
    quizzes = db.relationship('Assessment', back_populates='chapter', cascade="all, delete-orphan")

class Assessment(db.Model):
    __tablename__ = 'Quiz_Table'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    q_name = db.Column(db.String(80), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('Chapters.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.String(8), nullable=False)  # Format: HH:MM
    remarks = db.Column(db.Text)
    # Relationships
    questions = db.relationship('AssessmentProblem', back_populates='quiz', cascade="all, delete-orphan")
    scores = db.relationship('ExamPerformance', back_populates='quiz', cascade="all, delete-orphan")
    chapter = db.relationship('CourseModule', back_populates='quizzes')

class AssessmentProblem(db.Model):
    __tablename__ = 'Question_Table'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('Quiz_Table.id'), nullable=False)
    statement = db.Column(db.String(200), nullable=False)
    opt1 = db.Column(db.String(150), nullable=False)
    opt2 = db.Column(db.String(150), nullable=False)
    opt3 = db.Column(db.String(150), nullable=False)
    opt4 = db.Column(db.String(150), nullable=False)
    cor_opt = db.Column(db.Integer, nullable=False)
    
    # Relationship
    quiz = db.relationship('Assessment', back_populates='questions')

class ExamPerformance(db.Model):
    __tablename__ = 'Scores'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('Quiz_Table.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    time_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    user = db.relationship('Account', back_populates='scores')
    quiz = db.relationship('Assessment', back_populates='scores')

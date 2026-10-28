from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120))
    avatar_color = db.Column(db.String(7), default='#6366f1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    projects = db.relationship('Project', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='assignee', lazy='dynamic', foreign_keys='Task.assignee_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#6366f1')
    status = db.Column(db.String(20), default='active')  # active, completed, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def task_count(self):
        return self.tasks.count()
    
    @property
    def completed_count(self):
        return self.tasks.filter_by(status='completed').count()
    
    @property
    def progress(self):
        total = self.task_count
        if total == 0:
            return 0
        return int((self.completed_count / total) * 100)
    
    def __repr__(self):
        return f'<Project {self.name}>'


class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, completed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<Task {self.title}>'

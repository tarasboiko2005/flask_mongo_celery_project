from app.extensions import db
from datetime import datetime
from flask_login import UserMixin

class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.String(32), nullable=False, default="pending")
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filename = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True)

    def __repr__(self):
        return f"<Job {self.job_id} status={self.status} progress={self.progress}>"

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    picture = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    jobs = db.relationship("Job", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.name} ({self.email})>"
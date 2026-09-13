from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import Column, Integer, String
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates


#Initialize ORM
db = SQLAlchemy()
bcrypt = Bcrypt()

#Define Tables/Relationships
#user model
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(120), nullable=False)
    workouts = db.relationship("Workout", back_populates="user", cascade="all, delete-orphan")

    #password management
    #hash and store the user's password
    def set_password(self, password):
        self.hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    # check whether the given password is correct
    def check_password(self, password):
        return bcrypt.check_password_hash(self.hashed_password,password)

    #Representation
    def __repr__(self):
        return f"<User {self.username}>"

    #Dictionary Representation
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
        }
    
#Workout model
class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", back_populates="workouts")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    #Database constraints
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='check_duration_positive'),)

    #Duration validation
    @validates('duration_minutes')
    def validate_duration(self, key, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("The Duration must be a positive integer.")
        if value > 1440:
            raise ValueError("The Duration cannot exceed 1440 minutes (24 hours).")
        return value

    #Representation
    def __repr__(self):
        return f"<Workout {self.id} - {self.date}>"

    #Dictionary Representation
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'duration_minutes': self.duration_minutes,
            'notes': self.notes,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
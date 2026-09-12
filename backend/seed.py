from datetime import datetime
from app import app
from models import db, User, Workout
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():
    db.drop_all()
    db.create_all()

    user1 = User(username="user1", hashed_password=bcrypt.generate_password_hash("password123").decode('utf-8'))
    user2 = User(username="user2", hashed_password=bcrypt.generate_password_hash("password246").decode('utf-8'))
    user3 = User(username="user3", hashed_password=bcrypt.generate_password_hash("password369").decode('utf-8'))
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()

    workouts = [
        Workout(date=datetime(2026, 9, 1).date(), duration_minutes=60, notes="Morning run", user_id=user1.id),
        Workout(date=datetime(2026, 9, 2).date(), duration_minutes=45, notes="Evening walk", user_id=user1.id),
        Workout(date=datetime(2026, 9, 3).date(), duration_minutes=30, notes="Full body workout", user_id=user2.id),
        Workout(date=datetime(2026, 9, 4).date(), duration_minutes=90, notes="Cycling", user_id=user2.id),
        Workout(date=datetime(2026, 9, 5).date(), duration_minutes=120, notes="Upper body workout", user_id=user3.id),
        Workout(date=datetime(2026, 9, 6).date(), duration_minutes=75, notes="Abs workout", user_id=user3.id),
    ]

    db.session.add_all(workouts)
    db.session.commit()

    print("Database seeded successfully.")
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import ValidationError
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Workout
from schemas import SignupSchema, LoginSchema, UserSchema, WorkoutSchema
from dotenv import load_dotenv

#load .env files in os
load_dotenv()

#App config
app = Flask(__name__)

port = os.getenv("PORT", 5000)
is_app_debug = os.getenv("APP_DEBUG", True)

#Database configuration 
db_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url

# Token configs
jwt_secret = os.getenv("JWT_SECRET_KEY")
if not jwt_secret:
    raise RuntimeError("CRITICAL: `JWT_SECRET_KEY` variable not set.")

#JWT configuration
app.config["JWT_SECRET_KEY"] = jwt_secret 

#Extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

#Schemas
signup_schema = SignupSchema()
login_schema = LoginSchema()
user_schema = UserSchema()
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)


#Home route
@app.route('/')
def home():
    return {"message": "Welcome to the Workout Productivity API!"}


#Authentication routes
#Add the signup route 
@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json() or {}
    if not data.get("username") or not data.get("password") or not data.get("password_confirmation"):
        return {"message": "Username, password, and password confirmation are required"}, 422
    
    if data['password'] != data['password_confirmation']:
        return {"message": "Passwords do not match"}, 400

    username = data['username']
    password = data['password']

    #Retrieve the user from the database to check if the username already exists
    existing_user = db.session.scalars(db.select(User).where(User.username == data['username'])).first()
    if existing_user:
        return {"message": "Username already exists"}, 409

    #Instantiate a new User object and add it to the database
    new_user = User(username=username)
    new_user.set_password(password)

    #Perform insert action to db
    db.session.add(new_user)
    #Commit the transaction to the database
    db.session.commit()
    return {"message": "User created successfully"}, 201

#Add the login route
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    if not data.get("username") or not data.get("password"):
        return {"message": "Username and password are required"}, 422

    username = data['username']
    password = data['password']

    existing_user = db.session.scalars(db.select(User).where(User.username == data['username'])).first()
    if not existing_user or not existing_user.check_password(data['password']):
        return {"message": "Invalid credentials"}, 403

    #Generate a JWT token for the authenticated user
    access_token = create_access_token(identity=str(existing_user.id))
    return {"user": {"id": existing_user.id, "username": existing_user.username}, "token": access_token}, 200

#Authorization routes --> User Profile
@app.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user =db.session.get(User, int(user_id))
    return {"user": user_schema.dump(user)}, 200

#Current User (/me) endpoint
@app.route("/me", methods=["GET"])
@jwt_required()
def get_self():
    user_id = get_jwt_identity()
    #Retrieve the user from the database using the user_id obtained from the JWT token
    user =db.session.get(User, int(user_id))
    if not user:
        return {"message": "User not found"}, 404
    #Return the user's information as a JSON response using the UserSchema to serialize the data
    return {"user": user_schema.dump(user)}, 200

#Workout routes
#Retrieve all workouts for the authenticated user
@app.route("/workouts", methods=["GET"])
@jwt_required()
def get_workouts():
    user_id = get_jwt_identity()

    #pagination parameters
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=5, type=int)

    #validate page
    if page < 1:
        return {"message": "Page number must be at least 1"}, 400

    #validate per_page
    if per_page < 1 or per_page > 100:
        return {"message": "per_page must be between 1 and 100"}, 400

    #count total workouts belonging to the authenticated user
    total_items = db.session.scalar(db.select(db.func.count()).select_from(Workout).where(Workout.user_id == user_id))
    
    #Calculate total pages
    total_pages = ((total_items + per_page - 1) // per_page 
    if total_items else 0)


    #Retrieve the workouts for the authenticated user on the requested page
    workouts = db.session.scalars(db.select(Workout).where(Workout.user_id == user_id).order_by(Workout.date.desc()).offset((page - 1) * per_page).limit(per_page)).all()

    return {
        "workouts": workouts_schema.dump(workouts),
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_items": total_items,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }, 200
    
#Retrieve a specific workout by ID for the authenticated user
@app.route("/workouts/<int:workout_id>", methods=["GET"])
@jwt_required()
def get_workout(workout_id):
    user_id = get_jwt_identity()

    #Retrieve the workout only if it belongs to the authenticated user
    workout = db.session.scalar(db.select(Workout).where(Workout.id == workout_id,Workout.user_id == user_id))
    if not workout:
        return {"message": "Workout not found"}, 404
    
    #Return the workout's information as a JSON response using the WorkoutSchema to serialize the data
    return {"workout": workout_schema.dump(workout)}, 200

#Add a new workout for the authenticated user
@app.route("/workouts", methods=["POST"])
@jwt_required()
def create_workout():
    user_id = get_jwt_identity()
    try:
        data = workout_schema.load(request.get_json())
    except ValidationError as error:
        return {"message": "Validation failed", "errors": error.messages}, 400

    #Instantiate a new Workout object and add it to the database
    new_workout = Workout(
        date=data['date'],
        duration_minutes=data['duration_minutes'],
        notes=data.get('notes'),
        user_id=user_id
    )
    #Perform insert action to db
    db.session.add(new_workout)
    #Commit the transaction to the database
    db.session.commit()
    return {"message": "Workout created successfully"}, 201

#Update an existing workout for the authenticated user
@app.route("/workouts/<int:workout_id>", methods=["PATCH"])
@jwt_required()
def update_workout(workout_id):
    user_id = get_jwt_identity()

    #Retrieve the workout for the authenticated user by ID
    workout = db.session.scalar(db.select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id))
    if not workout:
        return {"message": "Workout not found"}, 404

    try:
        data = workout_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as error:
        return {"message": "Validation failed", "errors": error.messages}, 400
    
    #Update the workout's attributes with the provided data
    if 'date' in data:
        workout.date = data['date']
    if 'duration_minutes' in data:
        workout.duration_minutes = data['duration_minutes']
    if 'notes' in data:
        workout.notes = data['notes']

    db.session.commit()
    return {"message": "Workout updated successfully"}, 200

#Delete a specific workout by ID for the authenticated user
@app.route("/workouts/<int:workout_id>", methods=["DELETE"])
@jwt_required()
def delete_workout(workout_id):
    user_id = get_jwt_identity()

    #Retrieve the workout for the authenticated user by ID
    workout = db.session.scalar(db.select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id))
    if not workout:
        return {"message": "Workout not found"}, 404

    #Delete the workout from the database
    db.session.delete(workout)
    db.session.commit()
    return {"message": "Workout deleted successfully"}, 200

if __name__ == '__main__':
    app.run(debug=is_app_debug, port=port)
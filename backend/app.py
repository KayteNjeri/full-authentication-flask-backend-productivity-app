from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#JWT configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure key in production

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/')
def home():
    return {"message": "Welcome to the Workout Productivity API!"}


#Authentication routes
#Add the signup route
@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = signup_schema.load(request.get_json())
    except ValidationError as error:
        return {"message": "Validation failed", "errors": error.messages}, 400

    if data['password'] != data['password_confirmation']:
        return {"message": "Passwords do not match"}, 400

    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return {"message": "Username already exists"}, 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], hashed_password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return {"message": "User created successfully"}, 201

#Add the login route
@app.route("/login", methods=["POST"])
def login():
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as error:
        return {"message": "Validation failed", "errors": error.messages}, 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not bcrypt.check_password_hash(user.hashed_password, data['password']):
        return {"message": "Invalid username or password"}, 401

    access_token = create_access_token(identity=str(user.id))
    return {"access_token": access_token, "username": user.username}, 200

#Retrieve the authenticated user's information
@app.route("/self", methods=["GET"])
@jwt_required()
def get_self():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404
    return user_schema.dump(user), 200

#Workout routes
#Retrieve all workouts for the authenticated user
@app.route("/workouts", methods=["GET"])
@jwt_required()
def get_workouts():
    user_id = get_jwt_identity()
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=5, type=int)
    if page < 1:
        return {"message": "Page number must be at least 1"}, 400
    if per_page < 1 or per_page > 100:
        return {"message": "per_page must be between 1 and 100"}, 400
    pagination = Workout.query.filter_by(user_id=user_id).order_by(Workout.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return {
        "workouts": workouts_schema.dump(pagination.items),
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }, 200
    
#Retrieve a specific workout by ID for the authenticated user
@app.route("/workouts/<int:workout_id>", methods=["GET"])
@jwt_required()
def get_workout(workout_id):
    user_id = get_jwt_identity()
    workout = Workout.query.filter_by(id=workout_id, user_id=user_id).first()
    if not workout:
        return {"message": "Workout not found"}, 404
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

    new_workout = Workout(
        date=data['date'],
        duration_minutes=data['duration_minutes'],
        notes=data.get('notes'),
        user_id=user_id
    )
    db.session.add(new_workout)
    db.session.commit()
    return {"message": "Workout created successfully"}, 201

#Update an existing workout for the authenticated user
@app.route("/workouts/<int:workout_id>", methods=["PATCH"])
@jwt_required()
def update_workout(workout_id):
    user_id = get_jwt_identity()
    workout = Workout.query.filter_by(id=workout_id, user_id=user_id).first()
    if not workout:
        return {"message": "Workout not found"}, 404

    try:
        data = workout_schema.load(request.get_json(), partial=True)
    except ValidationError as error:
        return {"message": "Validation failed", "errors": error.messages}, 400

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
    workout = Workout.query.filter_by(id=workout_id, user_id=user_id).first()
    if not workout:
        return {"message": "Workout not found"}, 404

    db.session.delete(workout)
    db.session.commit()
    return {"message": "Workout deleted successfully"}, 200

if __name__ == '__main__':
    app.run(port=5555,debug=True)
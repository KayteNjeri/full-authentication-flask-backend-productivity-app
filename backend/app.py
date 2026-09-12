from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
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

if __name__ == '__main__':
    app.run(port=5555,debug=True)
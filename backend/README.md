# 🏋️ Flask Backend-Productivity Workout App

## 📖 Project Description

The **Flask Backend-Productivity Workout App** is a Flask App that allows authenticated users to manage their personal workout records. Users can create accounts, log in securely using JWT authentication, and perform CRUD operations on their own workouts.

The API uses **Flask, SQLAlchemy, SQLite, Marshmallow, Flask-Bcrypt, Flask-JWT-Extended, and Flask-Migrate**.

## ✨ Features

* JWT-based authentication
* User registration and login
* Protected API endpoints
* Create, read, update, and delete workouts
* User-specific workout ownership
* Pagination for workout listings
* Input validation with Marshmallow
* Password hashing with Flask-Bcrypt
* SQLite database
* Database migrations with Flask-Migrate
* API testing with Postman and pytest

## 🛠️ Technologies Used

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Migrate
* Flask-JWT-Extended
* Flask-Bcrypt
* Marshmallow
* SQLite
* Pytest
* Gunicorn

## 📁 Project Structure

```text
full-authentication-flask-backend-productivity-app/
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── schemas.py
│   ├── seed.py
│   ├── Pipfile
│   ├── Pipfile.lock
│   ├── README.md
│   ├── .gitignore
│   │
│   ├── instance/
│   │   └── app.db
│   │
│   ├── migrations/
│   │
│   └── tests/
│       ├── test_auth.py
│       └── test_workouts.py
│
└── frontend/
    └── client-with-jwt/
        ├── src/
        ├── public/
        ├── package.json
        ├── package-lock.json
        └── ...
```

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/KayteNjeri/full-authentication-flask-backend-productivity-app
cd full-authentication-flask-backend-productivity-app
```

### 2️⃣ Set up the Backend & Install Dependencies

Navigate to the backend directory:

```bash
cd backend
```

Install the Python dependencies:

```bash
pipenv install
```

Activate the virtual environment:

```bash
pipenv shell
```

## 🗄️ Set up the Database

Initialize the database migrations:

```bash
flask db init
```

Create the initial migration:

```bash
flask db migrate -m "Initial migration"
```

Apply the migration:

```bash
flask db upgrade
```

### 🌱 Seed the Database

Run:

```bash
python seed.py
```

The seed script creates sample users and workout records.

⚠️ **Note:** The seed script uses `db.drop_all()` before recreating the database. Running it will delete existing database data.

## ▶️ Running the Backend Application

From the `backend/` directory, start the Flask development server:

```bash
python app.py
```

The API will be available at:

```text
http://127.0.0.1:5000
```

## 🔐 Authentication

The API uses **JWT (JSON Web Tokens)** for authentication.

After logging in successfully, the API returns an `access_token`.

For protected endpoints, include the token in the request header:

```text
Authorization: Bearer <JWT_TOKEN>
```

## 🔑 Authentication Endpoints

| Method  | Endpoint  | Description                                   |
| ------- | --------- | --------------------------------------------- |
| 🟢 POST | `/signup` | Register a new user                           |
| 🟢 POST | `/login`  | Log in and receive a JWT                      |
| 🔵 GET  | `/self`   | Retrieve the authenticated user's information |

## 🏋️ Workout Endpoints

| Method    | Endpoint                 | Description                                |
| --------- | ------------------------ | ------------------------------------------ |
| 🔵 GET    | `/workouts`              | Retrieve the authenticated user's workouts |
| 🟢 POST   | `/workouts`              | Create a new workout                       |
| 🔵 GET    | `/workouts/<workout_id>` | Retrieve a specific workout                |
| 🟡 PATCH  | `/workouts/<workout_id>` | Update a workout                           |
| 🔴 DELETE | `/workouts/<workout_id>` | Delete a workout                           |

## 📄 Pagination

The `GET /workouts` endpoint supports pagination.

Example:

```text
GET /workouts?page=1&per_page=2
```

Available pagination parameters:

* `page` — page number, starting from `1`
* `per_page` — number of workouts per page
* Maximum `per_page` value is `100`

Example response:

```json
{
  "workouts": [],
  "pagination": {
    "page": 1,
    "per_page": 2,
    "total_pages": 3,
    "total_items": 6,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🔒 User Data Ownership

Each workout belongs to the authenticated user through the `user_id` foreign key.

Protected workout queries always filter by both the workout ID and the authenticated user's ID.

This prevents one user from accessing, updating, or deleting another user's workouts.

For example:

```python
Workout.query.filter_by(
    id=workout_id,
    user_id=user_id
).first()
```

If a workout does not belong to the authenticated user, the API returns:

```json
{
  "message": "Workout not found"
}
```

with a `404` status code.

## 🧪 Testing with Postman

The API can be tested using Postman.

### 1️⃣ Register

Send:

```text
POST /signup
```

with:

```json
{
  "username": "user8",
  "password": "password123",
  "password_confirmation": "password123"
}
```

### 2️⃣ Login

Send:

```text
POST /login
```

with:

```json
{
  "username": "user8",
  "password": "password123"
}
```

Copy the returned `access_token`.

### 3️⃣ Authorize Requests

For protected endpoints, paste the access token on Token:

```text
Authorization: Bearer: <Token>
```

### 4️⃣ Test Workouts

You can then test:

* `GET /workouts`
* `POST /workouts`
* `GET /workouts/<id>`
* `PATCH /workouts/<id>`
* `DELETE /workouts/<id>`

## 📦 Sample Workout

Example request for creating a workout:

```json
{
  "date": "2026-09-13",
  "duration_minutes": 60,
  "notes": "Chest workout"
}
```

## 🌱 Seed Users

The seed script creates the following users:

| Username | Hashed_Password      |
| -------- | ------------- |
| `user1`  | `$2b$12$6CHht.dwMI749dif0uw7qOqm4FCogm4l7ZngNbZFfIUa29W/HWWy6` |
| `user2`  | `$2b$12$EKHgGlLjzqlQKBzLr9DWmu8rq2E75m81RkdAusQo6b/vIcHvQc0HC` |
| `user3`  | `$2b$12$r5waUs/LTf0KAoWAu6gPxuCCW4q5lpe7HnGdnsw4.IzPvWn4E5a/2` |

⚠️ These credentials are for development/testing only.

## 🧰 Useful Commands

Install dependencies:

```bash
pipenv install
```

Activate environment:

```bash
pipenv shell
```

Create migration:

```bash
flask db migrate -m "Migration message"
```

Apply migration:

```bash
flask db upgrade
```

Seed database:

```bash
python seed.py
```

Run application:

```bash
python app.py
```

Run tests:

```bash
pytest
```

## 🚀 Deployment

The application can be deployed as a Flask Web Service on **Render**.

For production deployment:

* Use Gunicorn as the application server.
* Set `JWT_SECRET_KEY` as an environment variable.
* Configure the service to bind to `0.0.0.0`.
* Because this project uses SQLite, persistent storage must be configured if the SQLite database needs to survive deployments and restarts.

Example start command:

```bash
gunicorn app:app
```

## 📜 License

This project is licensed under the **MIT License**.

## 👩‍💻 Author

Built as a backend development project using Python, Flask, SQLAlchemy, JWT authentication, and SQLite.

# PathMatch Backend

Flask-based REST API for the PathMatch mentorship platform.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration values, especially:
- `SECRET_KEY` - Generate a secure random key
- `JWT_SECRET_KEY` - Generate another secure random key
- `DATABASE_URL` - Your database connection string

### 4. Initialize Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Run Development Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Mentors
- `GET /api/mentors` - Get all available mentors
- `GET /api/mentors/<id>` - Get specific mentor
- `POST /api/mentors/profile` - Create/update mentor profile
- `GET /api/mentors/profile` - Get own mentor profile
- `PUT /api/mentors/availability` - Update availability status

### Mentees
- `POST /api/mentees/profile` - Create/update mentee profile
- `GET /api/mentees/profile` - Get own mentee profile

### Matching
- `POST /api/matches/find` - Find compatible mentors
- `POST /api/matches` - Create a match
- `GET /api/matches/my-matches` - Get user's matches
- `PUT /api/matches/<id>/status` - Update match status

## Database Models

- **User** - Base authentication and user information
- **Mentor** - Mentor profile and availability
- **Mentee** - Mentee profile and needs
- **Match** - Mentor-mentee matches with compatibility scores
- **SurveyResponse** - Survey data for matching algorithm

## Project Structure

```
backend/
├── app.py                 # Flask application setup
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── routes/               # API route handlers
│   ├── auth.py
│   ├── mentors.py
│   ├── mentees.py
│   └── matching.py
└── services/             # Business logic
    └── matching_algorithm.py
```

## Database Schema

### Users Table
Core user authentication and profile data.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| net_id | String(20) | Cornell NetID (unique) |
| email | String(120) | User email (unique) |
| password_hash | String(255) | Hashed password |
| name | String(100) | Full name |
| role | String(20) | 'mentor' or 'mentee' |
| created_at | DateTime | Account creation timestamp |

### Mentors Table
Mentor profiles and availability.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users |
| graduating_year | Integer | Year of graduation |
| professional_experiences | Text (JSON) | Array of roles/experiences |
| postgrad_plans | String(100) | 'industry', 'grad_school', 'other' |
| info_concentration | String(100) | IS concentration |
| technical_courses | Text (JSON) | Array of courses taken |
| calendly_link | String(255) | Calendly scheduling URL |
| availability_status | String(20) | 'available', 'dnd', 'unavailable' |
| ratings_feedback | Text (JSON) | Array of feedback |

### Mentees Table
Mentee profiles and needs.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users |
| graduating_year | Integer | Expected graduation year |
| looking_for_career_advice | Boolean | Seeking career guidance |
| careers_interested_in | Text (JSON) | Array of career paths |
| looking_for_major_advice | Boolean | Seeking major/concentration advice |
| concentrations_interested_in | Text (JSON) | Array of concentrations |
| technical_courses_taken | Text (JSON) | Array of completed courses |

### Matches Table
Mentor-mentee pairings with compatibility scores.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| mentor_id | Integer | Foreign key to mentors |
| mentee_id | Integer | Foreign key to mentees |
| compatibility_score | Float | Algorithm-calculated score (0-100) |
| status | String(20) | 'pending', 'confirmed', 'completed', 'cancelled' |
| meeting_scheduled | Boolean | Whether meeting is booked |
| meeting_date | DateTime | Scheduled meeting time |

### Survey Responses Table
Stores detailed survey data for matching.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| mentor_id | Integer | Foreign key to mentors (nullable) |
| mentee_id | Integer | Foreign key to mentees (nullable) |
| question_id | String(50) | Survey question identifier |
| response_data | Text (JSON) | Survey response data |

## Matching Algorithm

The matching algorithm (`services/matching_algorithm.py`) calculates compatibility based on:

1. **Career Path Alignment (40 points)**
   - Matches mentee's career interests with mentor's professional experiences
   - Weighs overlap between desired career paths and mentor's background

2. **Concentration/Major Alignment (30 points)**
   - Compares mentee's concentration interests with mentor's actual concentration
   - Helps students get advice from those who've taken similar academic paths

3. **Technical Course Overlap (30 points)**
   - Uses Jaccard similarity to compare course histories
   - Ensures mentors can advise on specific technical courses

**Score Range:** 0-100, with higher scores indicating better compatibility.

## Authentication Flow

1. **Register:** `POST /api/auth/register`
   - Creates user account with NetID and password
   - Returns JWT access and refresh tokens

2. **Login:** `POST /api/auth/login`
   - Authenticates with NetID/password
   - Returns JWT tokens

3. **Protected Routes:**
   - Include `Authorization: Bearer <access_token>` header
   - Tokens expire after 1 hour (configurable)

4. **Token Refresh:** `POST /api/auth/refresh`
   - Use refresh token to get new access token
   - Refresh tokens valid for 30 days

## Development Workflow

### Adding New API Endpoints

1. Create route in appropriate file under `routes/`
2. Import required models from `models.py`
3. Use `@jwt_required()` decorator for protected routes
4. Return JSON responses with appropriate status codes

Example:
```python
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import Mentor

@bp.route('/mentors', methods=['GET'])
@jwt_required()
def get_mentors():
    mentors = Mentor.query.all()
    return jsonify({'mentors': [m.to_dict() for m in mentors]}), 200
```

### Database Migrations

When modifying models:

```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback if needed
flask db downgrade
```

### Testing API Endpoints

Use tools like Postman, curl, or httpie:

```bash
# Register a user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "net_id": "abc123",
    "email": "abc123@cornell.edu",
    "password": "securepass",
    "name": "John Doe",
    "role": "mentee"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "net_id": "abc123",
    "password": "securepass"
  }'

# Access protected route
curl -X GET http://localhost:5000/api/mentors \
  -H "Authorization: Bearer <your_access_token>"
```

## Environment Variables

Key environment variables (see `env.example`):

- `FLASK_ENV` - Set to 'development' or 'production'
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Flask secret key (must be random in production)
- `JWT_SECRET_KEY` - JWT signing key (must be random in production)
- `CORS_ORIGINS` - Comma-separated list of allowed origins

## Production Deployment Checklist

- [ ] Change `SECRET_KEY` and `JWT_SECRET_KEY` to secure random values
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper CORS origins
- [ ] Set up HTTPS/SSL
- [ ] Use a production WSGI server (gunicorn included in requirements)
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Implement rate limiting
- [ ] Add input validation and sanitization

## Future Enhancements

- [ ] Cornell CAS authentication integration
- [ ] Email notifications for new matches
- [ ] Calendly API integration for automated scheduling
- [ ] Advanced matching algorithm with ML
- [ ] Admin dashboard for platform management
- [ ] Analytics and reporting
- [ ] Real-time chat between matches
- [ ] Mobile app support

## Development Notes

- The matching algorithm is in `services/matching_algorithm.py`
- JWT tokens are used for authentication
- CORS is enabled for frontend integration
- Database migrations are handled by Flask-Migrate
- All JSON fields in models store serialized data (parse with `json.loads()`)
- Foreign key relationships use SQLAlchemy ORM
- Use `db.session.commit()` after modifying database objects


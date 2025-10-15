# PathMatch Quick Start Guide

Get PathMatch up and running in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser

## 🚀 Quick Setup

### 1. Clone and Navigate

```bash
cd path-match
```

### 2. Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start the server
python run.py
```

✅ Backend running at `http://localhost:5000`

### 3. Frontend Setup (30 seconds)

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Start local server
python -m http.server 8000
```

✅ Frontend running at `http://localhost:8000`

Open your browser and go to `http://localhost:8000`

## 🎯 Testing the API

### Register a User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "net_id": "test123",
    "email": "test123@cornell.edu",
    "password": "testpass123",
    "name": "Test User",
    "role": "mentee"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "net_id": "test123",
    "password": "testpass123"
  }'
```

Copy the `access_token` from the response.

### Create Mentee Profile

```bash
curl -X POST http://localhost:5000/api/mentees/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "graduating_year": 2026,
    "looking_for_career_advice": true,
    "careers_interested_in": "[\"Software Engineering\", \"Product Management\"]",
    "looking_for_major_advice": true,
    "concentrations_interested_in": "[\"Data Science\", \"UX Design\"]",
    "technical_courses_taken": "[\"INFO 2950\", \"CS 2110\"]"
  }'
```

## 📁 Project Structure

```
path-match/
├── frontend/          # Static landing page
│   ├── index.html     # Main page
│   └── styles.css     # Styling
│
└── backend/           # Flask API
    ├── app.py         # Main app
    ├── models.py      # Database models
    ├── routes/        # API endpoints
    └── services/      # Business logic
```

## 🔧 Common Commands

### Backend

```bash
# Start server
python run.py

# Initialize/reset database
python init_db.py

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

### Frontend

```bash
# Serve frontend
python -m http.server 8000
```

## 📚 Next Steps

1. **Read the Documentation**
   - [Backend API Documentation](./backend/README.md)
   - [Frontend Documentation](./frontend/README.md)
   - [Main README](./README.md)

2. **Configure Environment**
   - Copy `backend/env.example` to `backend/.env`
   - Update with your settings

3. **Explore the API**
   - Use Postman or similar tool
   - Check out all endpoints in backend README

4. **Customize the Frontend**
   - Edit `frontend/index.html` and `frontend/styles.css`
   - Add interactivity with JavaScript

## 🐛 Troubleshooting

### Backend won't start
- Make sure virtual environment is activated
- Check Python version: `python --version` (need 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt`

### Database errors
- Delete `backend/pathmatch.db` and run `python init_db.py` again
- Check DATABASE_URL in `.env`

### CORS errors
- Ensure backend CORS_ORIGINS includes your frontend URL
- Check `backend/.env` or `backend/config.py`

### Import errors
- Make sure you're in the backend directory
- Virtual environment must be activated

## 💡 Tips

- Keep both backend and frontend terminals open
- Backend changes require server restart
- Frontend changes just need browser refresh
- Use `http://localhost:5000/health` to check backend status
- Check `http://localhost:5000/` for API info

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [JWT Authentication](https://flask-jwt-extended.readthedocs.io/)
- [REST API Best Practices](https://restfulapi.net/)

## 📞 Need Help?

Check out the detailed documentation:
- [Main README](./README.md) - Project overview
- [Backend README](./backend/README.md) - API details
- [Frontend README](./frontend/README.md) - UI information

---

**Happy coding! 🎉**

Built for Cornell CIS by students, for students.


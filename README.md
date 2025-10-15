# PathMatch

> Connecting Cornell CIS underclassmen with graduating seniors for personalized career guidance and course planning.

---

## The Problem

Underclassmen in Cornell's CIS Information Science and ISST majors face challenges accessing effective career guidance. 

**The Numbers:**
- ~140 undergraduates earned Information Science or ISST degrees in 2023
- **Nearly 10%** were unemployed or seeking employment at graduation
- *Source: Cornell University reports, 2023*

### Current Challenges

The existing advising system, facilitated primarily through Zoom meetings with a limited number of CIS career advisors, falls short in several ways:

- **Outdated Resources** — Information doesn't reflect current industry trends
- **Generic Guidance** — Advice is too broad to address specific career questions  
- **Late Realization** — Students discover they've taken the wrong courses too late in their undergraduate career
- **Industry Gap** — Advisors lack up-to-date experience with evolving tech sectors

---

## Our Mission

We aim to **improve access to personalized, relevant career guidance** for undergraduate students in Cornell's Information Science and ISST majors. 

By connecting students with up-to-date advice, resources, and peer experiences that better reflect the realities of the tech and information fields, we empower them to make informed academic and career decisions early in their undergraduate journey.

---

## Social Impact

### Why This Matters

**For Students:**
- Make informed decisions before entering the workforce
- Avoid unnecessary course trial-and-error
- Graduate with clear career direction and relevant skills

**For Society:**
- **Reduced Career Turnover** — Better-informed graduates commit longer to roles
- **Stronger Workforce** — Employers gain prepared, aligned talent
- **Resource Efficiency** — Less strain on academic services and corporate training

---

## Our Solution

PathMatch is a **web application** that intelligently connects CIS underclassmen with graduating seniors through a survey-based matching system.

### Key Features

| Feature | Description |
|---------|-------------|
| **Dual Role System** | Separate interfaces for mentees seeking guidance and mentors offering experience |
| **Smart Matching Algorithm** | Correlates mentee needs with mentor expertise using survey responses |
| **Calendly Integration** | Seamless scheduling for immediate first contact |
| **Do Not Disturb Mode** | Mentors control availability to prevent meeting overload |

### Who We Serve

**Primary Audience**  
Undergraduate CIS students seeking advice on:
- Career trajectory planning
- Course selection strategies
- Industry-specific guidance
- Graduate school preparation

**Secondary Audience**  
Graduating seniors with defined paths (grad school or industry) ready to mentor

---

## Project Objectives

By the end of **beta testing**, PathMatch will deliver:

- A platform connecting underclassmen with graduating seniors  
- Personalized advice on career trajectories, courses, and graduate programs  
- Clear semester-by-semester course planning guidance  
- Efficient mentor-mentee pairing based on compatibility

---

## Timeline

**Deadline: Thanksgiving**

### Deliverables

1. Mentor survey design
2. Mentee survey design
3. Pairing algorithm
4. Front-end website (draft)
5. Back-end architecture (draft)
6. Calendly integration

### Key Milestones

- **Milestone 1:** Front-end development completion
- **Milestone 2:** Back-end development completion
- **Mini Milestone:** Pairing algorithm implementation

---

## Architecture

### Frontend Components

```
├── Survey Design Interface
├── Partner Matches Display
├── Partner Confirmation System
└── Calendly Plugin Integration
```

### Backend Components

```
├── Matching Algorithm
├── Survey Data Storage
└── User Authentication & Profiles
```

---

## Getting Started

### Project Structure

```
path-match/
├── frontend/              # Landing page and UI
│   ├── index.html
│   ├── styles.css
│   └── README.md
│
├── backend/              # Flask REST API
│   ├── app.py           # Main application
│   ├── database.py      # Database configuration
│   ├── models.py        # Database models
│   ├── config.py        # App configuration
│   ├── run.py           # Quick start script
│   ├── init_db.py       # Database initialization
│   ├── requirements.txt
│   ├── env.example      # Environment variables template
│   │
│   ├── routes/          # API endpoints
│   │   ├── auth.py
│   │   ├── mentors.py
│   │   ├── mentees.py
│   │   └── matching.py
│   │
│   └── services/        # Business logic
│       └── matching_algorithm.py
│
└── README.md            # This file
```

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run the server**
   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Open in browser**
   
   Simply open `index.html` in your browser, or use a local server:
   
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx http-server -p 8000
   ```
   
   Then navigate to `http://localhost:8000`

### API Documentation

See [Backend README](./backend/README.md) for detailed API endpoint documentation.

---

## Contributing

This project is currently under development for Cornell CIS students. Contribution guidelines will be added as the project progresses.

---

## License

*To be determined.*

---

<div align="center">

**PathMatch** is developed to serve the Cornell CIS community  
*Improving career outcomes for Information Science and ISST majors*

</div>

"""
Quick start script for PathMatch backend

Usage:
    python run.py
"""

from app import app, db
import os

if __name__ == '__main__':
    # Check if database exists
    db_path = 'pathmatch.db'
    if not os.path.exists(db_path) and app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        print("Database not found. Creating tables...")
        with app.app_context():
            db.create_all()
        print("✓ Database initialized!")
    
    print("\n" + "="*50)
    print("PathMatch Backend Server")
    print("="*50)
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Server: http://localhost:{os.getenv('FLASK_PORT', 5000)}")
    print("="*50 + "\n")
    
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )


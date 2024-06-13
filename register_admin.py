from flask_bcrypt import generate_password_hash
from db import db, app
from model import Admin

def register_admin(email, password):
    with app.app_context():
        hashed_password = generate_password_hash(password).decode('utf-8')
        new_admin = Admin(email=email, password_hash=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin {email} registered successfully!")

if __name__ == '__main__':
    # Replace with your desired email and password
    email = 'jacobbolarin@gmail.com'
    password = 'funke1328'
    register_admin(email, password)

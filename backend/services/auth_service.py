from ..models.user import User
from flask_jwt_extended import create_access_token

def register_user(username, email, password):
    # Check if user already exists
    if User.find_by_email(email):
        return {'error': 'Email already registered'}, 409
    
    # Create new user
    new_user = User(username, email, password)
    new_user.save()
    
    return {'message': 'User registered successfully'}, 201

def login_user(email, password):
    user = User.find_by_email(email)
    
    if not user or not User.check_password(user, password):
        return {'error': 'Invalid email or password'}, 401
    
    access_token = create_access_token(identity=str(user['_id']))
    return {'access_token': access_token, 'username': user['username']}, 200
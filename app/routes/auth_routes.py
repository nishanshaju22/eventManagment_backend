from flask import Blueprint, request, jsonify
from app.models import db, User
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    print("entered")
    data = request.get_json()

    # Check if user already exists
    if User.query.filter((User.email == data['email']) | (User.username == data['username'])).first():
        return jsonify({'message': 'User already exists'}), 400

    # Get the role from request data; default to 'user'
    role = data.get('role', 'user')
    is_admin = True if role.lower() == 'admin' else False

    # Create user and set password
    user = User(
        username=data['username'],
        email=data['email'],
        is_admin=is_admin
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': f'{role.capitalize()} registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
        return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if not user:
        return jsonify({'message': 'Email not found'}), 404

    user.generate_reset_token()
    db.session.commit()

    # Ideally send email with the reset token here.
    return jsonify({
        'message': 'Password reset token generated.',
        'reset_token': user.reset_token  # In production, don't send this directly.
    })

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('reset_token')
    new_password = data.get('new_password')

    user = User.query.filter_by(reset_token=token).first()

    if not user or user.reset_token_expiry < datetime.utcnow():
        return jsonify({'message': 'Invalid or expired token'}), 400

    user.set_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()

    return jsonify({'message': 'Password has been reset successfully'})

from flask_jwt_extended import jwt_required, get_jwt_identity

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    return jsonify({
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin
    })


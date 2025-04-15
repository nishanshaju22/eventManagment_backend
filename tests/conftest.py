import pytest
from app import create_app
from app.models import db as _db
from flask_jwt_extended import create_access_token
from app.models import User
import sys
from pathlib import Path

# Add the backend directory to the PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'backend'))

@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret',
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db(app):
    return _db

@pytest.fixture
def create_user(db):
    def _create_user(username, email, password, is_admin=False):
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    return _create_user

@pytest.fixture
def auth_header(create_user):
    user = create_user("testuser", "test@example.com", "password123")
    token = create_access_token(identity=user.id)
    return {'Authorization': f'Bearer {token}'}
import pytest
from app.db.session import SessionLocal
from app.models import Department, Collaborator
from app.auth.auth import create_token, hash_password

@pytest.fixture(scope="session")
def db():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="session")
def create_user(db):
    def _create_user(email, first_name, last_name, password, department_name):
        dept = db.query(Department).filter_by(name=department_name).first()
        if not dept:
            dept = Department(name=department_name)
            db.add(dept)
            db.commit()
        user = db.query(Collaborator).filter_by(email=email).first()
        if user:
            return user
        user = Collaborator(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hash_password(password),
            department_id=dept.id
        )
        db.add(user)
        db.commit()
        return user
    return _create_user


@pytest.fixture
def sales_token(create_user):
    user = create_user("sales@test.com", "Sales", "User", "pass1234", "Sales")
    return create_token(user.id)


@pytest.fixture
def support_token(create_user):
    user = create_user("support@test.com", "Support", "User", "pass1234", "Support")
    return create_token(user.id)


@pytest.fixture
def manager_token(create_user):
    user = create_user("manager@test.com", "Manager", "User", "pass1234", "gestion")
    return create_token(user.id)

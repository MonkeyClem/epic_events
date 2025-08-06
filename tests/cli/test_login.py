import pytest
from click.testing import CliRunner
from app.cli.main import login
from app.auth.auth import create_token
from app.db.session import SessionLocal
from app.models.collaborator import Collaborator
from app.auth.auth import hash_password

@pytest.fixture
def fake_user():
    """Ajoute un utilisateur de test à la base"""
    session = SessionLocal()
    user = Collaborator(
        first_name="Test",
        last_name="User",
        email="test@login.com",
        password=hash_password("test123"),
        department_id=1
    )
    session.add(user)
    session.commit()
    yield user
    session.delete(user)
    session.commit()
    session.close()

def test_login_success(fake_user):
    runner = CliRunner()
    result = runner.invoke(login, input="test@login.com\ntest123\n")

    assert result.exit_code == 0
    assert "Authentification réussie. Token :" in result.output

def test_login_invalid_password(fake_user):
    runner = CliRunner()
    result = runner.invoke(login, input="test@login.com\nwrongpassword\n")

    assert result.exit_code == 0
    assert "Mot de passe incorrect" in result.output

def test_login_user_not_found():
    runner = CliRunner()
    result = runner.invoke(login, input="notfound@email.com\nirrelevant\n")

    assert result.exit_code == 0
    assert "Utilisateur non trouvé" in result.output

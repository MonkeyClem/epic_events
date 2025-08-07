import pytest
from click.testing import CliRunner
from app.cli.client import create_client, update_client
from app.cli.main import login
from app.auth.auth import create_token
from app.db.session import SessionLocal
from app.models.client import Client
from app.models.collaborator import Collaborator
from app.auth.auth import hash_password


@pytest.fixture
def fake_sales_user():
    session = SessionLocal()
    user = Collaborator(
        first_name="Jean",
        last_name="Commercial",
        email="sales@test.com",
        password=hash_password("test123"),
        department_id=2,  # Département commercial
    )
    session.add(user)
    session.commit()
    yield user

    clients = session.query(Client).filter_by(commercial_contact_id=user.id).all()
    for client in clients:
        session.delete(client)
    session.commit()

    session.delete(user)
    session.commit()
    session.close()


@pytest.fixture
def existing_client(fake_sales_user):
    session = SessionLocal()
    client = Client(
        first_name="Alice",
        last_name="Client",
        email="alice@old.com",
        phone="0000000000",
        company_name="OldCorp",
        commercial_contact_id=fake_sales_user.id,
    )
    session.add(client)
    session.commit()
    yield client
    session.delete(client)
    session.commit()
    session.close()


@pytest.fixture
def fake_support_user():
    session = SessionLocal()
    user = Collaborator(
        first_name="Lucie",
        last_name="Support",
        email="support@test.com",
        password=hash_password("test123"),
        department_id=3,  # Département support
    )
    session.add(user)
    session.commit()
    yield user
    session.delete(user)
    session.commit()
    session.close()


@pytest.fixture
def another_client():
    session = SessionLocal()
    client = Client(
        first_name="Bob",
        last_name="Blocked",
        email="bob@client.com",
        phone="0707070707",
        company_name="NoAccessCorp",
        commercial_contact_id=9,
    )
    session.add(client)
    session.commit()
    yield client
    session.delete(client)
    session.commit()
    session.close()


def test_create_client_success(fake_sales_user):
    runner = CliRunner()

    token = create_token(fake_sales_user.id)

    test_input = (
        "\n".join(
            [
                token,
                "ClientFirst",
                "ClientLast",
                "client@example.com",
                "+1234567890",
                "TestCorp",
            ]
        )
        + "\n"
    )

    result = runner.invoke(create_client, input=test_input)

    assert result.exit_code == 0
    assert "Client ClientFirst ClientLast ajouté avec succès." in result.output


def test_create_client_failed(fake_support_user):
    runner = CliRunner()

    token = create_token(fake_support_user.id)

    test_input = (
        "\n".join(
            [
                token,
                "ClientFirst",
                "ClientLast",
                "client@example.com",
                "+1234567890",
                "TestCorp",
            ]
        )
        + "\n"
    )

    result = runner.invoke(create_client, input=test_input)

    assert result.exit_code == 0
    assert (
        "Accès refusé : cette action est réservée au(x) département(s) : commercial"
        in result.output
    )


def test_update_client_success(fake_sales_user, existing_client):
    runner = CliRunner()
    token = create_token(fake_sales_user.id)

    input_data = f"{token}\n{existing_client.id}\nAlice\nUpdated\nalice@new.com\n0606060606\nNewCorp\n"
    result = runner.invoke(update_client, input=input_data)

    assert result.exit_code == 0
    assert "Client mis à jour avec succès" in result.output

    # Vérification en base
    session = SessionLocal()
    updated = session.get(Client, existing_client.id)
    assert updated.last_name == "Updated"
    assert updated.email == "alice@new.com"
    session.close()


def test_update_client_unauthorized(fake_support_user, another_client):
    runner = CliRunner()
    token = create_token(fake_support_user.id)

    input_data = (
        f"{token}\n{another_client.id}\nNew\nName\nnew@mail.com\n0000000000\nNewCorp\n"
    )
    result = runner.invoke(update_client, input=input_data)

    assert result.exit_code == 0
    assert (
        "Accès refusé : cette action est réservée au(x) département(s) : commercial"
        in result.output
    )


# TODO : Implémenter le test pour un commercial qui n'est pas celui attitré

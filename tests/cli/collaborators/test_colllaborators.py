import pytest
from click.testing import CliRunner
from app.cli.collaborator import create_collaborator, delete_collaborator
from app.cli.event import create_event, update_event
from app.auth.auth import create_token
from app.db.session import SessionLocal
from app.models.collaborator import Collaborator
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from app.auth.auth import hash_password


# ------------------ FIXTURES ------------------
@pytest.fixture
def sales_user():
    session = SessionLocal()
    user = Collaborator(
        first_name="Jean",
        last_name="Commercial",
        email="sales@contract.com",
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
def manager_user():
    session = SessionLocal()
    user = Collaborator(
        first_name="Manager",
        last_name="User",
        email="manager@example.com",
        password=hash_password("managerpass"),
        department_id=3,  # gestion
    )
    session.add(user)
    session.commit()
    yield user
    session.delete(user)
    session.commit()
    session.close()


@pytest.fixture
def support_user():
    session = SessionLocal()
    user = Collaborator(
        first_name="Support",
        last_name="User",
        email="support@example.com",
        password=hash_password("supportpass"),
        department_id=1,
    )
    session.add(user)
    session.commit()
    yield user
    session.delete(user)
    session.commit()
    session.close()


@pytest.fixture
def client():
    session = SessionLocal()
    client = Client(
        first_name="Client",
        last_name="Test",
        email="client@test.com",
        phone="0101010101",
        company_name="TestCorp",
        commercial_contact_id=9,
    )
    session.add(client)
    session.commit()
    yield client
    session.delete(client)
    session.commit()
    session.close()


@pytest.fixture
def contract(client):
    session = SessionLocal()
    contract = Contract(
        client_id=client.id,
        sales_contact_id=9,
        amount=5000,
        remaining_amount=2000,
        signed=True,
    )
    session.add(contract)
    session.commit()
    yield contract
    session.delete(contract)
    session.commit()
    session.close()


# ------------------ COLLABORATOR TESTS ------------------


def test_create_collaborator_success(manager_user):
    runner = CliRunner()
    token = create_token(manager_user.id)

    result = runner.invoke(
        create_collaborator,
        input=f"John\nDoe\njohn@doe.com\n2\npassword123\n",  # dept 2 = Sales
        args=["--token", token],
    )

    print("RESULT IN COLLABORATORS TESTS")
    print(result.output)

    assert result.exit_code == 0
    assert "Collaborateur créé avec succès" in result.output

    session = SessionLocal()
    created_user = session.query(Collaborator).filter_by(email="john@doe.com").first()
    if created_user:
        session.delete(created_user)
        session.commit()
    session.close()


def test_create_collaborator_unauthorized():
    runner = CliRunner()
    token = create_token(9999)  # faux ID / pas en DB

    result = runner.invoke(
        create_collaborator,
        input="Fake\nUser\nfake@user.com\ntest\n2\n",
        args=["--token", token],
    )

    assert (
        result.exit_code != 0
        or "Utilisateur ou département introuvable" in result.output
    )


# ------------------ EVENT TESTS ------------------


def test_create_event_success(contract):
    runner = CliRunner()
    token = create_token(contract.sales_contact_id)

    result = runner.invoke(
        create_event,
        input=f"{contract.id}\ntestName\nLieu test\n2025-10-10 12:00\n2025-10-11 12:00\n20\nNotes de test\n",
        args=["--token", token],
    )

    assert result.exit_code == 0
    assert "Événement créé avec succès" or "Aucun contrat signé disponible" in result.output

    session = SessionLocal()
    created_event = session.query(Event).filter_by(name="testName").first()
    if created_event:
        session.delete(created_event)
        session.commit()
    session.close()


def test_update_event_as_support(support_user):
    session = SessionLocal()

    # Crée un event assigné au support
    event = Event(
        contract_id=1,
        support_contact_id=support_user.id,
        name="oldName",
        date_start="2025-09-01 09:00",
        date_end="2025-09-01 18:00",
        location="Ancien lieu",
        attendees=10,
        notes="Anciennes notes",
    )
    session.add(event)
    session.commit()

    runner = CliRunner()
    token = create_token(support_user.id)

    result = runner.invoke(
        update_event,
        input=f"{event.id}\nNom MAJ\nNouveau lieu\n2025-09-02 09:00\n2025-09-02 18:00\n100\nNotes mises à jour\n",
        args=["--token", token],
    )

    assert result.exit_code == 0
    assert "Événement mis à jour avec succès" in result.output

    session.delete(event)
    session.commit()
    session.close()


def test_update_event_unauthorized():
    runner = CliRunner()
    token = create_token(9999)  # faux ID

    result = runner.invoke(update_event, args=["--token", token])

    assert (
        result.exit_code != 0
        or "Utilisateur ou département introuvable" in result.output
    )

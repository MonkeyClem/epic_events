import pytest
from app.db.session import SessionLocal
from app.models import Collaborator
from app.auth.auth import hash_password
from app.models.client import Client
from app.models.contract import Contract


@pytest.fixture
def fake_user():
    """Ajoute un utilisateur de test à la base"""
    session = SessionLocal()
    user = Collaborator(
        first_name="Test",
        last_name="User",
        email="test@login.com",
        password=hash_password("test123"),
        department_id=1,
    )
    session.add(user)
    session.commit()
    yield user
    session.delete(user)
    session.commit()
    session.close()


@pytest.fixture
def fake_manager_user():
    session = SessionLocal()
    user = Collaborator(
        first_name="Lisa",
        last_name="Gestion",
        email="manager@contract.com",
        password=hash_password("test123"),
        department_id=3,  # Département gestion
    )
    session.add(user)
    session.commit()
    yield user
    try:
        session.delete(user)
        session.commit()
    except Exception as e:
        print(f"Erreur lors de la suppression du user: {e}")
    finally:
        session.close()


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
        # Si un contrat existe pour ce client, le supprimer avant de supprimer le client
        contracts = session.query(Contract).filter_by(client_id=client.id).all()
        for contract in contracts:
            session.delete(contract)
        session.commit()

        session.delete(client)
        session.commit()
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
def contract(existing_client):
    session = SessionLocal()
    contract = Contract(
        client_id=existing_client.id,
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

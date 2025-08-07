import pytest
from click.testing import CliRunner
from app.cli.contract import create_contract, update_contract
from app.auth.auth import hash_password, create_token
from app.models import Collaborator, Client, Contract
from app.db.session import SessionLocal


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
        first_name="Lisa",
        last_name="Gestion",
        email="manager@contract.com",
        password=hash_password("test123"),
        department_id=3,  # Département gestion
    )
    session.add(user)
    session.commit()
    yield user
    session.delete(user)
    session.commit()
    session.close()


@pytest.fixture
def client(sales_user):
    session = SessionLocal()
    client = Client(
        first_name="Bob",
        last_name="Client",
        email="bob@client.com",
        phone="0600000000",
        company_name="ClientCorp",
        commercial_contact_id=sales_user.id,
    )
    session.add(client)
    session.commit()
    yield client

    contracts = session.query(Contract).filter_by(client_id=client.id).all()
    for contract in contracts:
        session.delete(contract)

    session.delete(client)
    session.commit()
    session.close()


def test_create_contract_success(manager_user, client):
    runner = CliRunner()
    token = create_token(manager_user.id)

    result = runner.invoke(
        create_contract, args=["--token", token], input=f"{client.id}\n5000\n1000\nN\n"
    )
    assert result.exit_code == 0
    assert "Contrat créé avec succès." in result.output


def test_create_contract_unauthorized(sales_user, client):
    runner = CliRunner()
    token = create_token(sales_user.id)  # Commercials can't create contracts

    result = runner.invoke(create_contract, input=f"{token}\n{client.id}\n3000\nN\n")

    assert result.exit_code == 0
    assert "Accès refusé" in result.output


def test_update_contract_success(manager_user, client):
    session = SessionLocal()

    contract = Contract(
        client_id=client.id,
        amount=1000,
        remaining_amount=1000,
        signed=False,
        sales_contact_id=client.commercial_contact_id,
    )
    session.add(contract)
    session.commit()

    runner = CliRunner()
    token = create_token(manager_user.id)

    result = runner.invoke(
        update_contract, input=f"{token}\n{contract.id}\n1000\n0\nN\n"
    )

    assert result.exit_code == 0
    assert "Contrat mis à jour avec succès" in result.output

    session.delete(contract)
    session.commit()
    session.close()


def test_update_contract_not_found(manager_user):
    runner = CliRunner()
    token = create_token(manager_user.id)

    result = runner.invoke(update_contract, input=f"{token}\n9999\n2000\nN\n")

    assert result.exit_code == 0
    assert "Contrat introuvable" in result.output


def test_update_contract_unauthorized_user(sales_user, client):
    session = SessionLocal()

    contract = Contract(
        client_id=client.id,
        amount=1500,
        remaining_amount=1500,
        signed=False,
        sales_contact_id=sales_user.id,
    )
    session.add(contract)
    session.commit()

    runner = CliRunner()
    token = create_token(5)

    result = runner.invoke(
        update_contract, input=f"{token}\n{contract.id}\n2000\n1500\nN\n"
    )

    # Ce commercial ne doit pas pouvoir modifier le contrat
    assert result.exit_code == 0
    assert "Vous n’êtes pas autorisé à modifier ce contrat" in result.output

    session.delete(contract)
    session.commit()
    session.close()

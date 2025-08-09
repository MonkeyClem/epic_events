from click.testing import CliRunner
from app.cli.contract import create_contract, update_contract
from app.auth.auth import create_token
from app.models import Contract
from app.db.session import SessionLocal


def test_create_contract_success(fake_manager_user, existing_client):
    runner = CliRunner()
    token = create_token(fake_manager_user.id)

    result = runner.invoke(
        create_contract, input=f"{token}\n{existing_client.id}\n5000\n1000\nN\n"
    )
    assert result.exit_code == 0
    assert "Contrat créé avec succès." in result.output


def test_create_contract_unauthorized(fake_sales_user, existing_client):
    runner = CliRunner()
    token = create_token(fake_sales_user.id)

    result = runner.invoke(
        create_contract, input=f"{token}\n{existing_client.id}\n3000\nN\n"
    )

    assert result.exit_code == 0
    assert "Accès refusé" in result.output


def test_update_contract_success(fake_manager_user, existing_client):
    session = SessionLocal()

    contract = Contract(
        client_id=existing_client.id,
        amount=1000,
        remaining_amount=1000,
        signed=False,
        sales_contact_id=existing_client.commercial_contact_id,
    )
    session.add(contract)
    session.commit()

    runner = CliRunner()
    token = create_token(fake_manager_user.id)

    result = runner.invoke(
        update_contract, input=f"{token}\n{contract.id}\n1000\n0\nN\n"
    )

    assert result.exit_code == 0
    assert "Contrat mis à jour avec succès" in result.output

    session.delete(contract)
    session.commit()
    session.close()


def test_update_contract_not_found(fake_manager_user):
    runner = CliRunner()
    token = create_token(fake_manager_user.id)

    result = runner.invoke(update_contract, input=f"{token}\n9999\n2000\nN\n")

    assert result.exit_code == 0
    assert "Contrat introuvable" or "Aucun contrat disponible" in result.output


def test_update_contract_unauthorized_user(fake_sales_user, existing_client):
    session = SessionLocal()

    contract = Contract(
        client_id=existing_client.id,
        amount=1500,
        remaining_amount=1500,
        signed=False,
        sales_contact_id=fake_sales_user.id,
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

from click.testing import CliRunner
from app.cli.client import create_client, update_client
from app.auth.auth import create_token
from app.db.session import SessionLocal
from app.models.client import Client


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

from click.testing import CliRunner
from app.cli.collaborator import (
    create_collaborator,
    update_collaborator,
    delete_collaborator,
)
from app.auth.auth import create_token
from app.db.session import SessionLocal
from app.models.collaborator import Collaborator
from app.auth.auth import hash_password


def test_create_collaborator_success(fake_manager_user):
    runner = CliRunner()
    token = create_token(fake_manager_user.id)

    result = runner.invoke(
        create_collaborator,
        input="John\nDoe\njohn@doe.com\n2\npassword123\n",
        args=["--token", token],
    )

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


def test_update_collaborator_success(fake_manager_user, fake_sales_user):
    runner = CliRunner()
    token = create_token(fake_manager_user.id)

    result = runner.invoke(
        update_collaborator,
        args=["--token", token],
        input=f"{fake_sales_user.id}\nJean\nUpdated\nupdated@email.com\n2\nupdatedpassword\n",
    )

    assert result.exit_code == 0
    assert "Collaborateur mis à jour avec succès" in result.output


def test_update_collaborator_not_found(fake_manager_user):
    runner = CliRunner()
    token = create_token(fake_manager_user.id)

    result = runner.invoke(
        update_collaborator,
        args=["--token", token],
        input="9999\nJean\nDoe\nnotfound@email.com\n2\npass\n",
    )

    assert result.exit_code == 0
    assert "Collaborateur introuvable." in result.output


def test_delete_collaborator_success(fake_manager_user):
    runner = CliRunner()
    token = create_token(fake_manager_user.id)

    # Création d'un utilisateur temporaire à supprimer
    session = SessionLocal()
    temp_user = Collaborator(
        first_name="Temp",
        last_name="Delete",
        email="tempdelete@email.com",
        password=hash_password("temp123"),
        department_id=2,
    )
    session.add(temp_user)
    session.commit()

    result = runner.invoke(
        delete_collaborator, args=["--token", token], input=f"{temp_user.id}\nY\n"
    )

    session.close()

    assert result.exit_code == 0
    assert "Collaborateur supprimé avec succès." in result.output


def test_delete_collaborator_not_found(fake_manager_user):
    runner = CliRunner()
    token = create_token(fake_manager_user.id)

    result = runner.invoke(delete_collaborator, args=["--token", token], input="9999\n")

    assert result.exit_code == 0
    assert "Collaborateur introuvable." in result.output

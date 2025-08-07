import click
import sentry_sdk
from app.auth.permissions import check_permission
from app.cli.messages import INVALID_TOKEN_MESSAGE
from app.db.session import SessionLocal
from app.models.client import Client
from app.auth.auth import verify_token
from app.models.collaborator import Collaborator
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@click.command("list-clients")
@click.option("--token", prompt=True, help="Jeton d'authentification JWT")
def list_clients(token):
    verify_token(token)
    session = SessionLocal()
    clients = session.query(Client).all()

    if not clients:
        click.echo("Aucun client trouvé.")
        return

    for client in clients:
        click.echo(
            f"{client.id} - {client.first_name} {client.last_name} ({client.email})"
        )


@click.command("create-client")
@click.option("--token", prompt=True, help="Token d'authentification JWT")
@check_permission(["commercial"])
def create_client(token):
    user_id = verify_token(token)
    if not user_id:
        logger.info("Tentative de création de client avec un token invalide ou expiré")
        click.echo(INVALID_TOKEN_MESSAGE)
        return

    try:
        first_name = click.prompt("Prénom du client")
        last_name = click.prompt("Nom du client")
        email = click.prompt("Email")
        phone = click.prompt("Téléphone")
        company_name = click.prompt("Nom de l’entreprise")
        commercial_contact_id = user_id

        session = SessionLocal()
        client = Client(
            first_name=first_name,
            last_name=last_name,
            commercial_contact_id=commercial_contact_id,
            email=email,
            phone=phone,
            company_name=company_name,
        )
        session.add(client)
        session.commit()
        logger.info(
            f"Création du client {first_name} {last_name}, pour l'entreprise {company_name} ajouté avec succès."
        )
        click.echo(f"Client {first_name} {last_name} ajouté avec succès.")

    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de la création du client : {e}")


@click.command("update-client")
@click.option("--token", prompt=True, help="Jeton d'authentification JWT")
@check_permission(["commercial"])
def update_client(token):
    user_id = verify_token(token)
    if not user_id:
        logger.info("Tentaive de mise à jour de clients avec un token non valide")
        click.echo(INVALID_TOKEN_MESSAGE)
        return

    session = SessionLocal()
    try:
        user = session.get(Collaborator, user_id)
        clients = session.query(Client).all()
        for c in clients:
            click.echo(f"{c.id} - {c.first_name} {c.last_name} ({c.email})")

        client_id = click.prompt("ID du client à modifier", type=int)
        client = session.get(Client, client_id)

        if not client:
            click.echo("Client introuvable.")
            sentry_sdk.capture_exception(
                Exception("Tentative de mise à jour d'un client inexistant")
            )
            return

        if (
            user.department.name == "commercial"
            and client.commercial_contact_id != user.id
        ):
            sentry_sdk.capture_exception(
                Exception(
                    "Tentative de mise à jour de client par un commercial non autorisé"
                )
            )
            click.echo(
                "Les informations d'un client ne peuvent être mises à jour que par le commercial qui lui est attitré"
            )
            return

        client.first_name = click.prompt("Prénom", default=client.first_name)
        client.last_name = click.prompt("Nom", default=client.last_name)
        client.email = click.prompt("Email", default=client.email)
        client.phone = click.prompt("Téléphone", default=client.phone)
        client.company_name = click.prompt("Entreprise", default=client.company_name)

        session.commit()
        logger.info(
            f"Client {client_id} mis à jour avec succès par l'utiisateur {user_id}"
        )
        click.echo("Client mis à jour avec succès.")

    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de la mise à jour du client : {e}")

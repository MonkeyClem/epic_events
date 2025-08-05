import click
import sentry_sdk
from app.auth.permissions import check_permission
from app.db.session import SessionLocal
from app.models.client import Client
from app.auth.auth import verify_token
from app.models.collaborator import Collaborator


INVALID_TOKEN_MESSAGE = "Token invalide ou expiré"

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
        click.echo(f"{client.id} - {client.first_name} {client.last_name} ({client.email})")



@click.command("create-client")
@click.option("--token", prompt=True, help="Token d'authentification JWT")
@check_permission(["commercial"])
def create_client(token):
    user_id = verify_token(token)
    if not user_id:
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
            company_name=company_name
        )
        session.add(client)
        session.commit()
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
        click.echo("Token invalide ou expiré.")
        return

    session = SessionLocal()
    try:
        user = session.query(Collaborator).get(user_id)
        clients = session.query(Client).all()
        for c in clients:
            click.echo(f"{c.id} - {c.first_name} {c.last_name} ({c.email})")

        client_id = click.prompt("ID du client à modifier", type=int)
        client = session.query(Client).get(client_id)

        if not client:
            click.echo("Client introuvable.")
            return

        if user.department.name == "commercial" and client.commercial_contact_id != user.id:
            click.echo("Les informations d'un client ne peuvent être mises à jour que par le commercial qui lui est attitré")
            return

        client.first_name = click.prompt("Prénom", default=client.first_name)
        client.last_name = click.prompt("Nom", default=client.last_name)
        client.email = click.prompt("Email", default=client.email)
        client.phone = click.prompt("Téléphone", default=client.phone)
        client.company_name = click.prompt("Entreprise", default=client.company_name)

        session.commit()
        click.echo("Client mis à jour avec succès.")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de la mise à jour du client : {e}")
import click
from app.db.session import SessionLocal
from app.models.client import Client
from app.auth.auth import verify_token

@click.command("list-clients")
@click.option("--token", prompt=True, help="Jeton d'authentification JWT")
def list_clients(token):
    user_id = verify_token(token)  
    session = SessionLocal()
    clients = session.query(Client).all()

    if not clients:
        click.echo("Aucun client trouvé.")
        return

    for client in clients:
        click.echo(f"{client.id} - {client.first_name} {client.last_name} ({client.email})")



@click.command("create-client")
@click.option("--token", prompt=True, help="Token d'authentification JWT")
def create_client(token):
    user_id = verify_token(token)
    if not user_id:
        click.echo("Token invalide ou expiré.")
        return


    first_name = click.prompt("Prénom")
    last_name = click.prompt("Nom")
    email = click.prompt("Email")
    phone = click.prompt("Téléphone")
    company_name = click.prompt("Nom de l’entreprise")

    session = SessionLocal()
    client = Client(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name
    )
    session.add(client)
    session.commit()
    click.echo(f"Client {first_name} {last_name} ajouté avec succès.")

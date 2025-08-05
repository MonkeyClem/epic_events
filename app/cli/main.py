import click
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config import DATABASE_URL
from app.models.collaborator import Collaborator
from app.auth.auth import verify_password, create_token
from app.cli.client import list_clients, create_client, update_client
from app.cli.contract import list_contracts, create_contract, update_contract, filter_contracts
from app.cli.event import assign_support_to_event, list_events, create_event, update_event, list_unassigned_events
from app.cli.collaborator import create_collaborator, update_collaborator, delete_collaborator, list_collaborators
from app.logging.sentry import init_sentry

init_sentry()

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@click.group()
def cli():
    pass

cli.add_command(list_clients)
cli.add_command(create_client)
cli.add_command(list_contracts)
cli.add_command(create_contract)
cli.add_command(filter_contracts)
cli.add_command(list_events)
cli.add_command(list_unassigned_events)
cli.add_command(create_event)
cli.add_command(update_event)
cli.add_command(assign_support_to_event)
cli.add_command(update_client)
cli.add_command(update_contract)
cli.add_command(create_collaborator)
cli.add_command(update_collaborator)
cli.add_command(delete_collaborator)
cli.add_command(list_collaborators)


@cli.command()

@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def login(email, password):
    """Authentifie un utilisateur et retourne un token JWT"""
    session = Session()
    user = session.query(Collaborator).filter_by(email=email).first()

    if not user:
        click.echo("Utilisateur non trouvé.")
        return

    if not verify_password(password, user.password):
        click.echo("Mot de passe incorrect.")
        return

    token = create_token(user.id)
    click.echo(f"Authentification réussie. Token :\n{token}")

if __name__ == "__main__":
    cli()
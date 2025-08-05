import click
from datetime import datetime
from app.auth.permissions import check_permission
from app.models.collaborator import Collaborator
from app.models.event import Event
from app.models.contract import Contract
import sentry_sdk
from app.db.session import SessionLocal
from app.auth.auth import verify_token

@click.command("list-events")
@click.option("--token", prompt=True, help="Jeton d’authentification JWT")
def list_events(token):
    """Affiche la liste des événements"""
    try:
        verify_token(token)
    except Exception as e:
        click.echo(f"Erreur d’authentification : {str(e)}")
        return

    session = SessionLocal()
    events = session.query(Event).all()

    if not events:
        click.echo("Aucun événement trouvé.")
        return

    for e in events:
        click.echo(f"{e.id} - {e.name} (Du {e.date_start} au {e.date_end}) à {e.location}")

    session.close()



@click.command("create-event")
@click.option("--token", prompt=True, help="Jeton JWT d'authentification")
@check_permission(["Sales"])
def create_event(token):
    user_id = verify_token(token)
    session = SessionLocal()

    contracts = session.query(Contract).filter(
        Contract.signed == True,
        Contract.event == None
    ).all()
    

    if not contracts:
        click.echo("Aucun contrat signé disponible.")
        return

    click.echo("Contrats signés disponibles :")
    for contract in contracts:
        click.echo(f"{contract.id} - Client ID: {contract.client_id}, Montant: {contract.amount}")

    contract_id = click.prompt("ID du contrat à lier à l’événement", type=int)
    if contract.client.commercial_contact_id != user_id:
        click.echo("Vous n’êtes pas autorisé à créer un événement pour ce contrat.")
        return


    name = click.prompt("Nom de l’événement")
    location = click.prompt("Lieu")
    
    # Date et heure : format strict
    date_start_str = click.prompt("Date et heure de début (YYYY-MM-DD HH:MM)")
    date_end_str = click.prompt("Date et heure de fin (YYYY-MM-DD HH:MM)")

    try:
        date_start = datetime.strptime(date_start_str, "%Y-%m-%d %H:%M")
        date_end = datetime.strptime(date_end_str, "%Y-%m-%d %H:%M")
    except ValueError:
        click.echo("Format de date invalide. Utilise YYYY-MM-DD HH:MM.")
        return

    attendees = click.prompt("Nombre de participants", type=int)
    notes = click.prompt("Notes", default="")

    event = Event(
        name=name,
        location=location,
        date_start=date_start,
        date_end=date_end,
        attendees=attendees,
        notes=notes,
        contract_id=contract_id,
        support_contact_id=user_id
    )

    session.add(event)
    session.commit()
    click.echo("Événement créé avec succès.")




@click.command("update-event")
@click.option("--token", prompt=True, help="Token JWT")
@check_permission(["support", "gestion"])
def update_event(token):
    """Met à jour un événement (support ou gestion)"""
    user_id = verify_token(token)
    if not user_id:
        click.echo("Token invalide ou expiré.")
        return

    session = SessionLocal()
    try:
        user = session.query(Collaborator).get(user_id)
        if not user:
            click.echo("Utilisateur introuvable.")
            return

        if user.department.name.lower() == "support":
            # Le support ne peut voir que SES événements
            events = session.query(Event).filter_by(support_contact_id=user_id).all()
        else:
            # La gestion peut voir TOUS les événements
            events = session.query(Event).all()

        if not events:
            click.echo("Aucun événement disponible à modifier.")
            return

        click.echo("\n📋 Événements disponibles :")
        for e in events:
            click.echo(f"[{e.id}] {e.name} | Début : {e.date_start} | Lieu : {e.location}")

        event_id = click.prompt("ID de l’événement à modifier", type=int)

        if user.department.name.lower() == "support":
            event = session.query(Event).filter_by(id=event_id, support_contact_id=user_id).first()
        else:
            event = session.query(Event).filter_by(id=event_id).first()

        if not event:
            click.echo("Événement introuvable ou accès non autorisé.")
            return

        # --- Mise à jour des champs ---
        event.name = click.prompt("Nom", default=event.name)
        event.location = click.prompt("Emplacement", default=event.location)

        try:
            date_start_str = click.prompt("Date de début (YYYY-MM-DD HH:MM)", default=str(event.date_start))
            event.date_start = datetime.strptime(date_start_str, "%Y-%m-%d %H:%M")
            date_end_str = click.prompt("Date de fin (YYYY-MM-DD HH:MM)", default=str(event.date_end))
            event.date_end = datetime.strptime(date_end_str, "%Y-%m-%d %H:%M")
        except ValueError:
            click.echo("⛔ Format de date invalide.")
            return

        event.attendees = click.prompt("Participants", type=int, default=event.attendees)
        event.notes = click.prompt("Notes", default=event.notes or "")

        session.commit()
        click.echo("✅ Événement mis à jour avec succès.")

    except Exception as e:
        session.rollback()
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")
    finally:
        session.close()
  
        
@click.command("list-unassigned-events")
@click.option("--token", prompt=True, help="Jeton d’authentification JWT")
@check_permission(["gestion", "support"])
def list_unassigned_events(token):
    """Liste les événements sans collaborateur support assigné."""
    user_id = verify_token(token)
    if not user_id:
        click.echo("Token invalide ou expiré.")
        return

    session = SessionLocal()
    try:
        events = session.query(Event).filter(Event.support_contact_id == None).all()

        if not events:
            click.echo("Tous les événements ont un support assigné.")
            return

        click.echo("Événements sans support :")
        for e in events:
            click.echo(f"[{e.id}] {e.name} | Client ID: {e.client_id} | Début: {e.event_date_start} | Lieu: {e.location}")
    except Exception as e:
        click.echo(f"Erreur lors de la récupération des événements : {e}")
    finally:
        session.close()
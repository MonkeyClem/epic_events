from datetime import datetime
import click
import sentry_sdk
from app.auth.permissions import check_permission
from app.db.session import SessionLocal
from app.models.client import Client
from app.models.collaborator import Collaborator
from app.models.contract import Contract
from app.auth.auth import verify_token


INVALID_TOKEN_MESSAGE = "Token invalide ou expiré"

@click.command("list-contracts")
@click.option('--token', prompt=True, help='Jeton JWT pour authentification')
def list_contracts(token):
    user_id = verify_token(token)
    if not user_id:
        sentry_sdk.capture_message("Tentative de lister les contrats avec un token invalide ou expiré")
        click.echo(INVALID_TOKEN_MESSAGE)
        return

    session = SessionLocal()
    contracts = session.query(Contract).all()

    if not contracts:
        click.echo("Aucun contrats n'existe en base de données")
        return

    for contract in contracts:
        status = "Signé" if contract.signed else "Non signé"
        click.echo(
            f"{contract.id} - Client ID {contract.client_id} | Montant: {contract.amount} | "
            f"Status: {status} | Date de signature: {contract.signed_date}"
        )


@click.command("create-contract")
@click.option("--token", prompt=True, help="Jeton JWT pour authentification")
@check_permission(["gestion"])
def create_contract(token):
    user_id = verify_token(token)
    if not user_id:
        sentry_sdk.capture_message("Tentative de création d'un contrat avec un token invalide ou expiré")
        click.echo("Token invalide ou expiré.")
        return

    session = SessionLocal()
    try:
        client_id = click.prompt("ID du client", type=int)
        client = session.query(Client).filter_by(id=client_id).first()
        if not client:
            click.echo("Client introuvable.")
            return

        # if client.commercial_contact_id != user_id:
        #     click.echo("Vous n’êtes pas autorisé à créer un contrat pour ce client.")
        #     return
        sales_contact_id = client.commercial_contact_id
        
        print("client dans la création de contrat : ", client)

        amount = click.prompt("Montant", type=float)
        already_payed_amount=click.prompt('Si une partie du montant a déjà été réglé, merci de bien vouloir indiquer la somme ici :', type=float)
        signed = click.confirm("Contrat signé ?")
        signed_date = datetime.now() if signed else None

        contract = Contract(
            client_id=client_id,
            sales_contact_id=sales_contact_id,
            amount=amount,
            remaining_amount=amount-already_payed_amount,
            signed=signed,
            signed_date=signed_date
        )

        session.add(contract)
        session.commit()
        sentry_sdk.capture_message(f"Contrat crée avec succès par l'utiisateur {user_id}")
        click.echo("Contrat créé avec succès.")
    except Exception as e:
        session.rollback()
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de la création du contrat : {e}")

@click.command("update-contract")
@click.option("--token", prompt=True, help="Jeton d'authentification JWT")
@check_permission(["commercial", "gestion"])
def update_contract(token):
    """Mise à jour d’un contrat existant si autorisé."""
    try:
        user_id = verify_token(token)
        if not user_id:
            sentry_sdk.capture_message("Tentative de mise à jour d'un contrat avec un token invalide ou expiré")
            click.echo("Token invalide ou expiré.")
            return

        session = SessionLocal()
        user = session.query(Collaborator).get(user_id)

        contracts = session.query(Contract).all()
        if not contracts:
            click.echo("Aucun contrat disponible.")
            return

        for contract in contracts:
            status = "Signé" if contract.signed else "Non signé"
            click.echo(
                f"{contract.id} - Client ID: {contract.client_id}, Montant: {contract.amount}, Statut: {status}"
            )

        contract_id = click.prompt("ID du contrat à modifier", type=int)
        contract = session.query(Contract).get(contract_id)

        if not contract:
            click.echo("Contrat introuvable.")
            return

        # Autorisation : 
        # Sales = uniquement si assigné
        # gestion = tous les contrats
        if user.department.name == "commercial" and contract.sales_contact_id != user.id:
            click.echo("Vous n’êtes pas autorisé à modifier ce contrat.")
            return

        contract.amount = click.prompt("Montant total", default=contract.amount, type=float)
        contract.remaining_amount = click.prompt("Montant restant", default=contract.remaining_amount, type=float)
        contract.signed = click.confirm("Contrat signé ?", default=contract.signed)

        if contract.signed:
            from datetime import datetime
            contract.signed_date = datetime.now()

        session.commit()
        sentry_sdk.capture_message(f"Contrat {contract_id} mis à jour avec succès par l'utiisateur {user_id}")
        click.echo("Contrat mis à jour avec succès.")

    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de la mise à jour du contrat : {e}")
        
        
        
@click.command("filter-contracts")
@click.option("--token", prompt=True, help="Jeton d’authentification JWT")
@check_permission(["commercial", "gestion"])
def filter_contracts(token):
    """Affiche les contrats filtrés (non signés ou non payés)"""
    user_id = verify_token(token)
    if not user_id:
        click.echo("Token invalide ou expiré.")
        return

    click.echo("\n📋 Critères de filtrage disponibles :")
    click.echo("1 - Contrats non signés")
    click.echo("2 - Contrats avec montant restant à payer")
    click.echo("3 - Les deux")

    choix = click.prompt("Sélectionnez un filtre (1, 2 ou 3)", type=int)

    session = SessionLocal()
    try:
        query = session.query(Contract)

        if choix == 1:
            contracts = query.filter(Contract.signed == False).all()
        elif choix == 2:
            contracts = query.filter(Contract.remaining_amount > 0).all()
        elif choix == 3:
            contracts = query.filter(
                (Contract.signed == False) | (Contract.remaining_amount > 0)
            ).all()
        else:
            click.echo("Choix invalide.")
            return

        if not contracts:
            click.echo("Aucun contrat correspondant au filtre.")
            return

        click.echo("\n📄 Contrats filtrés :")
        for c in contracts:
            click.echo(
                f"[{c.id}] Client ID: {c.client_id} | Montant: {c.total_amount} € | Restant: {c.remaining_amount} € | Signé: {'Oui' if c.signed else 'Non'}"
            )

    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors du filtrage : {e}")
    finally:
        session.close()
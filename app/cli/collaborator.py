import click
import sentry_sdk
from app.auth.permissions import check_permission
from app.cli.messages import INVALID_TOKEN_MESSAGE
from app.db.session import SessionLocal
from app.auth.auth import verify_token
from app.models.collaborator import Collaborator
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@click.command("create-collaborator")
@click.option("--token", prompt=True, help="Jeton d’authentification JWT")
@check_permission(["gestion"])
def create_collaborator(token):
    """
    Crée un nouveau collaborateur.

    Vérifie l'authentification avec le jeton JWT fourni et permet à un utilisateur 
    ayant le rôle "gestion" de créer un collaborateur dans la base de données.

    Args:
        token (str): Le jeton JWT d'authentification.

    Returns:
        None
    """
    
    user_id = verify_token(token)
    if not user_id:
        logger.info(
            "Tentative de création de collaborateur avec token invalide ou expiré"
        )
        click.echo(INVALID_TOKEN_MESSAGE)
        return

    session = SessionLocal()
    try:
        collaborator_name = click.prompt("Prénom du collaborateur", type=str)
        collaborator_lastname = click.prompt("Nom du collaborateur", type=str)
        collaborator_email = click.prompt("Adresses email du collaborateur", type=str)
        collaborator_department_id = click.prompt(
            "Identifiants du départements auquel le collaborateur sera rattaché",
            type=int,
        )

        collaborator_password = click.prompt("Mot de passe du nouveau collaborateur")
        from app.auth.auth import hash_password

        hashed_pw = hash_password(collaborator_password)

        collaborator = Collaborator(
            first_name=collaborator_name,
            last_name=collaborator_lastname,
            email=collaborator_email,
            password=hashed_pw,
            # employee_number = Column(String, unique=True, nullable=True)
            department_id=collaborator_department_id,
        )
        session.add(collaborator)
        session.commit()
        logger.info(
            f"Collaborateur {collaborator_name} {collaborator_lastname} ajouté avec succès par l'utiisateur {user_id}"
        )
        click.echo("Collaborateur créé avec succès.")
    except Exception as e:
        session.rollback()
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de la création : {e}")
    finally:
        session.close()


@click.command("update-collaborator")
@click.option("--token", prompt=True, help="Jeton d’authentification JWT")
@check_permission(["gestion"])
def update_collaborator(token):
    """
    Met à jour les informations d'un collaborateur existant.

    Vérifie l'authentification avec le jeton JWT fourni et permet à un utilisateur 
    ayant le rôle "gestion" de mettre à jour les informations d'un collaborateur 
    dans la base de données.

    Args:
        token (str): Le jeton JWT d'authentification.

    Returns:
        None
    """
    
    user_id = verify_token(token)
    if not user_id:
        logger.info(
            "Tentative de mise à jour d'un collaborateur avec un token expiré ou invalide"
        )
        click.echo(INVALID_TOKEN_MESSAGE)
        return

    session = SessionLocal()
    try:
        collab_id = click.prompt("ID du collaborateur à modifier", type=int)
        collaborator = session.query(Collaborator).get(collab_id)

        if not collaborator:
            click.echo("Collaborateur introuvable.")
            return

        # Champs modifiables
        new_first_name = click.prompt("Prénom", default=collaborator.first_name)
        new_last_name = click.prompt("Nom", default=collaborator.last_name)
        new_email = click.prompt("Email", default=collaborator.email)
        new_department_id = click.prompt(
            "Département ID", default=collaborator.department_id, type=int
        )

        collaborator.first_name = new_first_name
        collaborator.last_name = new_last_name
        collaborator.email = new_email
        collaborator.department_id = new_department_id

        session.commit()
        logger.info(
            f"Collaborateur {new_first_name} {new_last_name} mis à jour avec succès par l'utiisateur {user_id}"
        )
        click.echo("Collaborateur mis à jour avec succès.")
    except Exception as e:
        session.rollback()
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")
    finally:
        session.close()


@click.command("delete-collaborator")
@click.option("--token", prompt=True, help="Jeton d’authentification JWT")
@check_permission(["gestion"])
def delete_collaborator(token):
    """
    Supprime un collaborateur.

    Vérifie l'authentification avec le jeton JWT fourni et permet à un utilisateur 
    ayant le rôle "gestion" de supprimer un collaborateur de la base de données 
    après confirmation.

    Args:
        token (str): Le jeton JWT d'authentification.

    Returns:
        None
    """

    user_id = verify_token(token)
    if not user_id:
        logger.info(
            "Tentative de suppression d'un collaborateur avec un token invalide ou expiré"
        )
        click.echo(INVALID_TOKEN_MESSAGE)
        return

    session = SessionLocal()
    try:
        collab_id = click.prompt("ID du collaborateur à supprimer", type=int)
        collaborator = session.query(Collaborator).get(collab_id)

        if not collaborator:
            click.echo("Collaborateur introuvable.")
            return

        confirm = click.confirm(
            f"Confirmer la suppression de {collaborator.email} ?", default=False
        )
        if not confirm:
            click.echo("Suppression annulée.")
            return

        session.delete(collaborator)
        session.commit()
        logger.info(
            f"Collaborateur {collab_id} supprimé avec succès par l'utiisateur {user_id}"
        )
        click.echo("Collaborateur supprimé avec succès.")
    except Exception as e:
        session.rollback()
        click.echo(f"Erreur : {e}")
    finally:
        session.close()


@click.command("list-collaborators")
@click.option("--token", prompt=True, help="Jeton d’authentification JWT")
@check_permission(["gestion"])
def list_collaborators(token):
    """Affiche la liste des collaborateurs (gestion uniquement)"""
    user_id = verify_token(token)
    if not user_id:
        logger.info(
            "Tentative de listing des collaborateurs avec un token invalide ou expiré"
        )
        click.echo(INVALID_TOKEN_MESSAGE)
        return

    session = SessionLocal()
    try:
        collaborators = session.query(Collaborator).all()
        if not collaborators:
            click.echo("Aucun collaborateur trouvé.")
            return

        click.echo("Liste des collaborateurs :")
        for c in collaborators:
            click.echo(
                f"[{c.id}] {c.first_name} {c.last_name} - {c.email} | Département ID: {c.department_id}"
            )
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")
    finally:
        session.close()

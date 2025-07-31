import click
from functools import wraps
from app.db.session import SessionLocal
from app.auth.auth import verify_token
from app.models.collaborator import Collaborator

def check_permission(allowed_departments):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = kwargs.get("token")
            if not token:
                click.echo("Erreur : aucun token fourni.")
                return

            try:
                user_id = verify_token(token)
                session = SessionLocal()
                user = session.query(Collaborator).get(user_id)
                if not user or not user.department:
                    click.echo("Utilisateur ou département introuvable.")
                    return

                if user.department.name not in allowed_departments:
                    click.echo(
                        f"Accès refusé : cette action est réservée au(x) département(s) : {', '.join(allowed_departments)}"
                    )
                    return

                return f(*args, **kwargs)

            except Exception as e:
                click.echo(f"Erreur de permission : {str(e)}")

        return wrapper
    return decorator

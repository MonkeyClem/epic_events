import random
import subprocess
import time
from app.db.session import SessionLocal
from app.models.department import Department
from app.models.collaborator import Collaborator
from app.auth.auth import hash_password
from app.auth.auth import create_token


def create_user_if_not_exists(email, first_name, last_name, password, department_name):
    session = SessionLocal()
    user = session.query(Collaborator).filter_by(email=email).first()
    if user:
        return user

    dept = session.query(Department).filter_by(name=department_name).first()
    if not dept:
        dept = Department(name=department_name)
        session.add(dept)
        session.commit()

    user = Collaborator(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=hash_password(password),
        department=dept,
        # employee_number=random.randint(100000, 999999)
    )
    session.add(user)
    session.commit()
    return user


def generate_token_for_user(user):
    return create_token(user.id)


def run_command_with_token(command_name, token):
    print(f"\n Test commande : {command_name} avec token de {token[:10]}...")
    try:
        result = subprocess.run(
            ["python", "-m", "app.cli.main", command_name, "--token", token],
            capture_output=True,
            text=True,
            input="\n".join([
                "1",                 # ID client ou contrat par défaut
                "test", "test",      # Nom/prénom ou infos fictives
                "test@email.com",
                "0123456789",
                "TestCorp",
                "1000", "oui",       # montant + confirmation signé
                "2025-10-10 12:00",  # dates
                "2025-11-11 12:00",
                "10",                # participants
                "notes de test"      # notes
            ]),
            timeout=5
        )
        print(result.stdout.strip())
        if result.stderr:
            print("⚠️  STDERR:", result.stderr.strip())
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout - la commande a mis trop de temps.")


if __name__ == "__main__":
    print("Initialisation des utilisateurs et des tokens...")

    users = {
        "sales": create_user_if_not_exists(
            "sales@example.com", "Jean", "Vendeur", "test1234", "Sales"
        ),
        "support": create_user_if_not_exists(
            "support@example.com", "Alice", "Support", "test1234", "Support"
        ),
        "manager": create_user_if_not_exists(
            "manager@example.com", "Bob", "Manager", "test1234", "Management"
        ),
    }

    tokens = {role: generate_token_for_user(user) for role, user in users.items()}

    print(" Utilisateurs prêts. Début des tests...")

    tests = [
        ("create-client", ["sales", "manager"]),
        ("update-client", ["sales", "manager"]),
        ("create-contract", ["manager"]),
        ("update-contract", ["manager"]),
        ("create-event", ["sales"]),
        ("update-event", ["support"]),
        ("list-clients", ["sales", "support", "manager"]),
        ("list-contracts", ["sales", "support", "manager"]),
        ("list-events", ["sales", "support", "manager"]),
    ]

    for cmd, roles in tests:
        for role in ["sales", "support", "manager"]:
            token = tokens[role]
            print(f"\n {cmd} — exécuté par {role.upper()}")
            run_command_with_token(cmd, token)
            time.sleep(1)

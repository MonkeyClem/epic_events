
from app.auth.auth import create_token
from app.cli.event import create_event, update_event
from click.testing import CliRunner
from app.db.session import SessionLocal
from app.models.event import Event



def test_create_event_success(contract):
    runner = CliRunner()
    token = create_token(contract.sales_contact_id)

    result = runner.invoke(
        create_event,
        input=f"{contract.id}\ntestName\nLieu test\n2025-10-10 12:00\n2025-10-11 12:00\n20\nNotes de test\n",
        args=["--token", token],
    )

    assert result.exit_code == 0
    assert (
        "Événement créé avec succès"
        or "Aucun contrat signé disponible" in result.output
    )

    session = SessionLocal()
    created_event = session.query(Event).filter_by(name="testName").first()
    if created_event:
        session.delete(created_event)
        session.commit()
    session.close()


def test_update_event_as_support(support_user, contract):
    session = SessionLocal()

    # Crée un event assigné au support
    event = Event(
        contract_id=contract.id,
        support_contact_id=support_user.id,
        name="oldName",
        date_start="2025-09-01 09:00",
        date_end="2025-09-01 18:00",
        location="Ancien lieu",
        attendees=10,
        notes="Anciennes notes",
    )
    session.add(event)
    session.commit()

    runner = CliRunner()
    token = create_token(support_user.id)

    result = runner.invoke(
        update_event,
        input=f"{event.id}\nNom MAJ\nNouveau lieu\n2025-09-02 09:00\n2025-09-02 18:00\n100\nNotes mises à jour\n",
        args=["--token", token],
    )

    assert result.exit_code == 0
    assert "Événement mis à jour avec succès" in result.output

    session.delete(event)
    session.commit()
    session.close()


def test_update_event_unauthorized():
    runner = CliRunner()
    token = create_token(9999)

    result = runner.invoke(update_event, args=["--token", token])

    assert (
        result.exit_code != 0
        or "Utilisateur ou département introuvable" in result.output
    )

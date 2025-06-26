from sqlalchemy import create_engine
from app.config import DATABASE_URL
from app.models.base import Base
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from app.models.collaborator import Collaborator
from app.models.department import Department

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Base de données initialisée.")

if __name__ == "__main__":
    init_db()

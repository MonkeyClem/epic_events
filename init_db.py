from sqlalchemy import create_engine
from app.config import DATABASE_URL
from app.models.base import Base
from app.models.client import Client  # Importez vos autres modèles ici

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Base de données initialisée.")

if __name__ == "__main__":
    init_db()

from sqlalchemy import Column, ForeignKey, Integer, String
from app.models.base import Base
from sqlalchemy.orm import relationship


# class Client(Base):
#     __tablename__ = "clients"

#     id = Column(Integer, primary_key=True)
#     first_name = Column(String, nullable=False)
#     last_name = Column(String, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     phone = Column(String)
#     company_name = Column(String)
#     commercial_contact_id = Column(
#         Integer, ForeignKey("collaborators.id"), nullable=False
#     )

#     contracts = relationship(
#         "Contract", back_populates="client", cascade="all, delete-orphan"
#     )


# app/models/client.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.security.crypto import EncryptedText, blind_index
from sqlalchemy import event

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)

    first_name = Column(EncryptedText, nullable=False)
    last_name  = Column(EncryptedText, nullable=False)
    email      = Column(EncryptedText, nullable=False)
    phone      = Column(EncryptedText, nullable=False)
    company_name = Column(EncryptedText, nullable=False)

    # Blind index pour recherche/unique sur email
    email_bidx = Column(String(64), unique=True, index=True)

    commercial_contact_id = Column(Integer, ForeignKey("collaborators.id"), nullable=False)
    commercial_contact = relationship("Collaborator", back_populates="clients")

# Gère automatiquement l'email_bidx à chaque set / update
@event.listens_for(Client, "before_insert")
def client_before_insert(mapper, connection, target: "Client"):
    target.email_bidx = blind_index(target.email) if target.email else None

@event.listens_for(Client, "before_update")
def client_before_update(mapper, connection, target: "Client"):
    target.email_bidx = blind_index(target.email) if target.email else None

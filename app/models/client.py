from sqlalchemy import Column, ForeignKey, Integer, String
from app.models.base import Base
from sqlalchemy.orm import relationship


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    company_name = Column(String)
    commercial_contact_id = Column(
        Integer, ForeignKey("collaborators.id"), nullable=False
    )

    contracts = relationship("Contract", back_populates="client")

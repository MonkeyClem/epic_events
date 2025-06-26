from sqlalchemy import Column, Integer, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    signed = Column(Boolean, default=False)
    signed_date = Column(Date)
    
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    sales_contact_id = Column(Integer, ForeignKey("collaborators.id"), nullable=False)

    client = relationship("Client", back_populates="contracts")
    sales_contact = relationship("Collaborator", back_populates="contracts")
    event = relationship("Event", back_populates="contract", uselist=False)

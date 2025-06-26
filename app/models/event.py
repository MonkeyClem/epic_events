from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String)
    date = Column(Date, nullable=False)
    attendees = Column(Integer)
    notes = Column(Text)

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    support_contact_id = Column(Integer, ForeignKey("collaborators.id"))

    contract = relationship("Contract", back_populates="event")
    support_contact = relationship("Collaborator", back_populates="events")

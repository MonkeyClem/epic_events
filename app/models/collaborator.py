# app/models/collaborator.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.auth.auth import hash_password

class Collaborator(Base):
    __tablename__ = 'collaborators'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    # employee_number = Column(String, unique=True, nullable=True)

    department_id = Column(Integer, ForeignKey("departments.id"))

    department = relationship("Department", back_populates="collaborators")
    contracts = relationship("Contract", back_populates="sales_contact")
    events = relationship("Event", back_populates="support_contact")

    def set_password(self, plain_password):
        self.password = hash_password(plain_password)

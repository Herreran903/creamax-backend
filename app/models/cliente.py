from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    rut = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    comentarios = Column(String, nullable=True)
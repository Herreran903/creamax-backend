# app/crud/cliente.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.cliente import Cliente


def create_or_update_cliente(db: Session, *, nombre: str, email: str, telefono: str = None,
                             rut: str = None, direccion: str = None, comentarios: str = None):
    """
    Crea o actualiza un Cliente según email.
    Retorna el objeto Cliente persistido.
    """

    try:
        cliente = db.query(Cliente).filter(Cliente.email == email).first()

        if cliente:
            # Actualizar datos existentes
            cliente.nombre = nombre
            if telefono is not None:
                cliente.telefono = telefono
            if rut is not None:
                cliente.rut = rut
            if direccion is not None:
                cliente.direccion = direccion
            if comentarios is not None:
                cliente.comentarios = comentarios

            db.add(cliente)
            db.commit()
            db.refresh(cliente)
            return cliente
        
        # Crear nuevo cliente
        nuevo_cliente = Cliente(
            nombre=nombre,
            email=email,
            telefono=telefono,
            rut=rut,
            direccion=direccion,
            comentarios=comentarios,
        )

        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        return nuevo_cliente

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar cliente: {str(e)}")

# app/schemas/confirmation.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class ConfirmationRequest(BaseModel):
    cotizacion_id: int = Field(..., gt=0)
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    rut: Optional[str] = None
    direccion: Optional[str] = None
    comentarios: Optional[str] = None
    cantidad: Optional[int] = Field(1, gt=0)
    usuario_id: Optional[str] = None  # optional: if present, we won't create/update Cliente

    @validator("nombre")
    def nombre_no_vacio(cls, v):
        if not v or not v.strip():
            raise ValueError("nombre no puede estar vacío")
        return v.strip()

class ConfirmationResponse(BaseModel):
    pedido_id: int
    cotizacion_id: int
    item_personalizado_id: str
    cantidad: int
    estado: str
    fecha_pedido: datetime
    mensaje: str

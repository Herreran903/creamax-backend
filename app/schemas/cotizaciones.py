from pydantic import BaseModel
from typing import Optional

class CotizacionListado(BaseModel):
    id: int
    item_personalizado_id: str
    nombre_personalizado: str
    cantidad: int
    cotizacion_rango: str
    precio_final_unidad: Optional[float]
    precio_total: Optional[float]
    estado: str
    fecha_pedido: str
    moneda: str

    class Config:
        orm_mode = True

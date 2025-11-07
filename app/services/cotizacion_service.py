# app/services/cotizacion_service.py
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Tuple, Dict

#TODO: se puso un placeholder de simulación de cotización. Se debe aplicar lógica real que se vaya a utilizar.
def estimate_price_from_params(parametros: dict, modelo_precio_base: float | None = None) -> Tuple[float, float, Dict]:
    """
    Retorna (min, max, desglose)
    - parámetros: dict con cantidad, material, complejidad_estimacion, etc.
    - modelo_precio_base: precio base tomado de ModeloCatalogo si existe.
    Lógica MVP:
      base = modelo_precio_base or 1000
      material_factor: PLA=1.0, Acrilico=1.2, Metal=2.5 (ejemplo)
      complexity_factor: baja=0.9, media=1.0, alta=1.4
      qty_discount: pequeña reducción por cantidad
      cot_min = base * material_factor * complexity_factor * qty_factor
      cot_max = cot_min * 1.4  (margen)
    """
    base = float(modelo_precio_base) if modelo_precio_base is not None else 1200.0
    cantidad = max(1, int(parametros.get("cantidad", 1)))
    material = (parametros.get("material") or "").lower()
    complexity = (parametros.get("complejidad_estimacion") or "media").lower()

    material_map = {
        "pla": 1.0,
        "acrilico": 1.2,
        "metal": 2.5,
        "resina": 1.6
    }
    material_factor = material_map.get(material, 1.0)

    complexity_map = {"baja": 0.9, "media": 1.0, "alta": 1.4}
    complexity_factor = complexity_map.get(complexity, 1.0)

    # qty factor: descuentos por volumen (simple)
    if cantidad >= 1000:
        qty_factor = 0.6
    elif cantidad >= 500:
        qty_factor = 0.75
    elif cantidad >= 100:
        qty_factor = 0.9
    else:
        qty_factor = 1.0

    unidad = base * material_factor * complexity_factor * qty_factor

    # desglose:
    material_cost = unidad * 0.55
    mano_obra = unidad * 0.30
    energia = unidad * 0.10
    acabado = unidad * 0.05

    cot_min = round(unidad * 0.9, 2)
    cot_max = round(unidad * 1.4, 2)

    desglose = {
        "material": round(material_cost, 2),
        "mano_obra": round(mano_obra, 2),
        "energia": round(energia, 2),
        "acabado": round(acabado, 2)
    }

    return cot_min, cot_max, desglose

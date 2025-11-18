# app/services/cotizacion_service.py
from datetime import datetime, timedelta
from decimal import Decimal
import random
from typing import Tuple, Dict

#TODO: se puso un placeholder de simulación de cotización. Se debe aplicar lógica real que se vaya a utilizar.
def estimate_price_from_params(parametros: dict) -> Tuple[float, float, Dict]:
    """
    Retorna (min, max, desglose)
    - parámetros: dict con costo de material, tiempo de impresión y cambios de filamento.
    """
    
    material_cost = parametros.get("slicer_metrics", {}).get("cost", 0)  # costo del material estimado
    print_time = parametros.get("slicer_metrics", {}).get("time", 0)    # tiempo de impresión en horas
    filament_changes = parametros.get("slicer_metrics", {}).get("tool_changes", 0)  # cambios de herramienta

    # Simulación de cálculo de cotización basado en métricas

    # Si falla conexión con laminador o no se obtienen métricas, usar valores de muestra basados en rangos típicos
    
    if material_cost == 0:
        material_cost = round(random.uniform(500, 1000), 2)
    
    if print_time == 0:
        print_time = round(random.uniform(0.34, 1.34), 2)
    
    gasto_energía = print_time * 0.12  # consumo energético estimado
    costo_energía = gasto_energía * 600  # costo energético
    mantenimiento_impresora = print_time * 769  # mantenimiento de la impresora
    mano_obra = 1000
    costo_cambios_filamento = (723 + 120) * filament_changes / 12  # costo por cambios de filamento
    herraje_llavero = 160

    subtotal = (
        material_cost +
        costo_energía +
        mantenimiento_impresora +
        mano_obra +
        costo_cambios_filamento +
        herraje_llavero
    )

    gastos_generales = subtotal * 0.10  # gastos generales

    if parametros.get("include_nfc", False):
        nfc_cost = 1000  # costo adicional por NFC
    else:
        nfc_cost = 0

    unidad = subtotal + gastos_generales + nfc_cost

    acabado = 0

    cot_min = round(unidad * 1.5, 2)
    cot_max = round(unidad * 2, 2)

    desglose = {
        "material": round(material_cost, 2),
        "mano_obra": round(mano_obra, 2),
        "energia": round(costo_energía, 2),
        "acabado": round(acabado, 2)
    }

    return cot_min, cot_max, desglose

from sqlalchemy.orm import Session
from app.models.nfc_enlace import NfcEnlace
from app.models.nfc_visita import NfcVisita
from sqlalchemy import func
from datetime import date, timedelta


def get_nfc_by_item_id(db: Session, item_id: str):
    return db.query(NfcEnlace).filter(NfcEnlace.item_personalizado_id == item_id).first()


def update_nfc_url(db: Session, nfc: NfcEnlace, new_url: str):
    nfc.url_destino_actual = str(new_url)
    db.commit()
    db.refresh(nfc)
    return nfc


def get_click_stats(db: Session, nfc_id: int):
    # Últimos 7 días
    seven_days_ago = date.today() - timedelta(days=6)

    registros = (
        db.query(NfcVisita.fecha_conteo, NfcVisita.conteo)
        .filter(NfcVisita.nfc_enlace_id == nfc_id)
        .filter(NfcVisita.fecha_conteo >= seven_days_ago)
        .order_by(NfcVisita.fecha_conteo.asc())
        .all()
    )

    return [{"dia": r.fecha_conteo, "clicks": r.conteo} for r in registros]

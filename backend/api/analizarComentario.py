# api/analizarComentario.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.ia.iaCore import NLPAnalyzer
from backend.core.coreServices import guardarAnalisis


router = APIRouter(tags=["Analisis"])

analyzer = NLPAnalyzer()

class AnalizarPayload(BaseModel):
    comentario: str
    meta: dict | None = None

@router.post("/analizar-comentario/")
def analizarComentario(payload: AnalizarPayload, db: Session = Depends(get_db)):
    try:
        result = analyzer.analyze_comment(payload.comentario, meta=payload.meta or {})
        row = guardarAnalisis(db, result)
        return {"status":"ok","id": row.id, "resultado": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analizando: {e}")

# api/analizarLote.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import csv
import io

from backend.config.database import get_db
from backend.ia.iaCore import NLPAnalyzer
from backend.core.coreServices import guardarAnalisisLote


router = APIRouter(tags=["Analisis"])

analyzer = NLPAnalyzer()

class LotePayload(BaseModel):
    datos: List[Dict[str, Any]]

@router.post("/analizar-lote/")
def analizarLote(payload: LotePayload, db: Session = Depends(get_db)):
    try:
        resultados = analyzer.batch_analyze(payload.datos)
        guardados = guardarAnalisisLote(db, resultados)
        return {"status":"ok","procesados": len(resultados), "guardados": guardados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analizando lote: {e}")

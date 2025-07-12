# camara_insights/app/api/v1/deputados.py
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.domain import entidades as schemas
from app.infra.db.crud import entidades as crud
from app.infra.db.session import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/deputados", response_model=List[schemas.DeputadoSchema])
def read_deputados(
    req: Request,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=200, description="Número de registros a retornar"),
    sort: Optional[str] = Query(None, description="Ordena os resultados usando campo:direção, ex: nome:asc,id:desc")
):
    """
    Retorna uma lista de deputados com paginação, ordenação e filtragem dinâmicas.
    """
    filters: Dict[str, Any] = {
        key: value
        for key, value in req.query_params.items()
        if key not in ["skip", "limit", "sort"]
    }
    deputados = crud.get_deputados(
        db,
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort
    )
    return deputados
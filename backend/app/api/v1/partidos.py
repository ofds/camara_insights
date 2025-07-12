# camara_insights/app/api/v1/partidos.py
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

@router.get("/partidos", response_model=List[schemas.PartidoSchema])
def read_partidos(
    req: Request,
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=200, description="Número máximo de itens a retornar"),
    sort: Optional[str] = Query(None, description="Ordena os resultados por campo:direção (ex: nome:asc,id:desc)"),
    db: Session = Depends(get_db)
):
    """
    Retorna uma lista de partidos políticos com opções de paginação, filtragem e ordenação dinâmicas.
    """
    filters: Dict[str, Any] = {
        key: value
        for key, value in req.query_params.items()
        if key not in ["skip", "limit", "sort"]
    }
    partidos = crud.get_partidos(db, skip=skip, limit=limit, filters=filters, sort=sort)
    return partidos
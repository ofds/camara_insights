# camara_insights/app/api/v1/votacoes.py
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.domain import entidades as schemas
from app.infra.db.crud import entidades as crud
from app.infra.db.session import SessionLocal

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/votacoes", response_model=List[schemas.VotacaoSchema])
def read_votacoes(
    req: Request,
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=200, description="Número de registros a retornar"),
    sort: Optional[str] = Query(None, description="Ordena os resultados por campo:direção (ex: dataHoraRegistro:desc,id:asc)"),
    db: Session = Depends(get_db)
):
    """
    Retorna uma lista paginada de votações com ordenação e filtragem dinâmicas.
    """
    # Extrai todos os parâmetros de filtragem da query, excluindo os de paginação e de ordenação
    filters: Dict[str, Any] = {
        key: value
        for key, value in req.query_params.items()
        if key not in ["skip", "limit", "sort"]
    }

    votacoes = crud.get_votacoes(
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort
    )
    return votacoes
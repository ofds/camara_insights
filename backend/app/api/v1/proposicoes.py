# app/api/v1/proposicoes.py
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

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

@router.get("/proposicoes", response_model=List[schemas.ProposicaoSchema])
def read_proposicoes(
    req: Request,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=200, description="Número de registros a retornar"),
    sort: Optional[str] = Query(None, description="Ordena os resultados. Formato: campo:direcao (ex: ano:desc,id:asc)")
):
    """
    Retorna uma lista de proposições com paginação, filtros e ordenação dinâmicos.
    """
    # Extrai todos os parâmetros da query de filtro, exceto aqueles que já estão sendo usados
    filter_exclude_params = {'skip', 'limit', 'sort'}
    filters = {k: v for k, v in req.query_params.items() if k not in filter_exclude_params}

    proposicoes = crud.get_proposicoes(
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort
    )

    return proposicoes
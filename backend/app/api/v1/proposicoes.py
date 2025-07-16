# backend/app/api/v1/proposicoes.py

import asyncio
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import date, timedelta

from app.domain import entidades as schemas
from app.infra.db.crud import entidades as crud
from app.infra.db.session import SessionLocal
from app.infra.camara_api import camara_api_client

router = APIRouter()

# Dependency
def get_db():
    """
    Cria e gerencia uma sessão de banco de dados para cada requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/proposicoes", response_model=schemas.ProposicaoPaginatedResponse)
def read_proposicoes(
    req: Request,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=200, description="Número de registros a retornar"),
    sort: Optional[str] = Query(None, description="Ordena os resultados. Formato: campo:direcao (ex: ano:desc,id:asc)"),
    scored: Optional[bool] = Query(None, description="Filter for scored proposals"),
    data_inicio: Optional[date] = Query(None, description="Data de início para o filtro de data de apresentação"),
    data_fim: Optional[date] = Query(None, description="Data de fim para o filtro de data de apresentação")
):
    """
    Retorna uma lista de proposições com paginação, filtros e ordenação dinâmicos.
    """
    filter_exclude_params = {'skip', 'limit', 'sort', 'scored', 'data_inicio', 'data_fim'}
    filters = {k: v for k, v in req.query_params.items() if k not in filter_exclude_params}

    if data_inicio:
        filters['dataApresentacao__gte'] = data_inicio
    if data_fim:
        # To make the range inclusive, we add one day to the end date and use 'less than'
        filters['dataApresentacao__lte'] = data_fim + timedelta(days=1)

    # Data returned from CRUD function
    crud_result = crud.get_proposicoes(
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort,
        scored=scored
    )

    # Reconstruct the response to match the ProposicaoPaginatedResponse schema
    return {
        "proposicoes": crud_result["proposicoes"],
        "total": crud_result["total_count"],
        "limit": limit,
        "skip": skip
    }


@router.get("/proposicoes/ranking", response_model=List[schemas.ProposicaoSchema])
def read_proposicoes_ranking(
    period: str = Query("daily", enum=["daily", "monthly"]),
    db: Session = Depends(get_db)
):
    """
    Retorna uma lista das proposições de maior impacto, diário ou mensal.
    """
    today = date.today()
    if period == "daily":
        start_date = today
    elif period == "monthly":
        start_date = today - timedelta(days=30)
    else:
        raise HTTPException(status_code=400, detail="Período inválido. Use 'daily' ou 'monthly'.")

    return crud.get_proposicoes_by_impact_and_date(db=db, start_date=start_date)


@router.get("/proposicoes/{proposicao_id}", response_model=schemas.ProposicaoSchema)
def read_proposicao(proposicao_id: int, db: Session = Depends(get_db)):
    """
    Retorna os detalhes de uma única proposição do banco de dados local.
    """
    db_proposicao = crud.get_proposicao_by_id(db, proposicao_id=proposicao_id)
    if db_proposicao is None:
        raise HTTPException(status_code=404, detail="Proposição não encontrada")
    return db_proposicao

@router.get("/proposicoes/{proposicao_id}/details", response_model=dict[str, Any])
async def read_proposicao_details(proposicao_id: int, db: Session = Depends(get_db)):
    """
    Retorna os detalhes completos de uma proposição, combinando dados
    locais com dados em tempo real da API da Câmara.
    """
    # 1. Busca os dados básicos do nosso banco de dados
    db_proposicao = crud.get_proposicao_by_id(db, proposicao_id=proposicao_id)
    if db_proposicao is None:
        raise HTTPException(status_code=404, detail="Proposição não encontrada no banco de dados local.")

    # 2. Em paralelo, busca os dados adicionais da API da Câmara usando seu cliente
    tasks = [
        camara_api_client.get(f"/proposicoes/{proposicao_id}/autores"),
        camara_api_client.get(f"/proposicoes/{proposicao_id}/relacionadas"),
        camara_api_client.get(f"/proposicoes/{proposicao_id}/temas"),
        camara_api_client.get(f"/proposicoes/{proposicao_id}/tramitacoes"),
        camara_api_client.get(f"/proposicoes/{proposicao_id}/votacoes"),
    ]
    
    # Executa todas as chamadas de API concorrentemente
    results = await asyncio.gather(*tasks)
    
    autores_data, relacionadas_data, temas_data, tramitacoes_data, votacoes_data = results

    # 3. Combina todos os dados em uma única resposta
    return {
        "base_data": db_proposicao,
        "autores": autores_data.get("dados", []) if autores_data else [],
        "relacionadas": relacionadas_data.get("dados", []) if relacionadas_data else [],
        "temas": temas_data.get("dados", []) if temas_data else [],
        "tramitacoes": tramitacoes_data.get("dados", []) if tramitacoes_data else [],
        "votacoes": votacoes_data.get("dados", []) if votacoes_data else [],
    }
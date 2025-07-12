# camara_insights/app/infra/db/crud/entidades.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import DateTime, Date, desc, asc, func
from app.infra.db.models import entidades as models
from app.infra.db.models import ai_data as models_ai 
from datetime import datetime, date
from typing import Optional, List, Dict, Any


def _flatten_dict(d, parent_key='', sep='_'):
    """ 'Achata' um dicionário aninhado. Ex: {'a': {'b': 1}} -> {'a_b': 1} """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def _parse_dates(data, model):
    """ Converte strings de data/datetime para os tipos corretos do Python. """
    for key, value in data.items():
        if isinstance(value, str):
            # Acessa o tipo da coluna no modelo SQLAlchemy
            column_type = getattr(model, key).type
            
            if isinstance(column_type, (DateTime)):
                try:
                    # Remove 'Z' e outros caracteres de timezone não padrão
                    clean_value = value.split('.')[0].replace('Z', '')
                    data[key] = datetime.fromisoformat(clean_value)
                except (ValueError, TypeError):
                    data[key] = None
            elif isinstance(column_type, (Date)):
                try:
                    data[key] = date.fromisoformat(value)
                except (ValueError, TypeError):
                    data[key] = None
    return data

def upsert_entidade(db: Session, model, data: dict):
    """
    Função genérica de upsert para as entidades principais.
    Busca pelo ID e insere ou atualiza o registro.
    """
    pk_name = model.__table__.primary_key.columns.values()[0].name
    pk_value = data.get(pk_name)
    if not pk_value:
        return # Não podemos fazer upsert sem uma chave primária

    # Filtra os dados para conter apenas colunas que existem no modelo
    model_columns = {c.name for c in model.__table__.columns}
    flat_data = _flatten_dict(data)
    filtered_data = {k: v for k, v in flat_data.items() if k in model_columns}
    
    # Converte datas/datetimes
    parsed_data = _parse_dates(filtered_data, model)

    db_obj = db.query(model).get(pk_value)

    if db_obj:
        # Atualiza o objeto existente
        for key, value in parsed_data.items():
            setattr(db_obj, key, value)
    else:
        # Cria um novo objeto
        db_obj = model(**parsed_data)
        db.add(db_obj)

def bulk_upsert_entidades(db: Session, model, data_list: list[dict]):
    """
    Realiza o upsert de uma lista de entidades de forma eficiente.
    """
    for item_data in data_list:
        upsert_entidade(db, model, item_data)
    db.commit()

def get_deputados(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[str] = None
):
    """
    Busca uma lista paginada de deputados, com filtros e ordenação dinâmicos.
    """
    from .utils import apply_filters_and_sorting

    # Query inicial
    query = db.query(models.Deputado)

    # Define campos permitidos para ordenação e filtragem
    allowed_sort_fields = {
        "nome": models.Deputado.ultimoStatus_nome,
        "siglaUf": models.Deputado.ultimoStatus_siglaUf,
        "siglaPartido": models.Deputado.ultimoStatus_siglaPartido,
    }

    # Aplica filtros e ordenação dinâmicos
    query_result = apply_filters_and_sorting(
        query,
        model=models.Deputado,
        filters=filters,
        sort=sort,
        allowed_sort_fields=allowed_sort_fields,
        default_sort_field="nome"
    )

    # Aplica paginação e retorna resultados
    return query_result.offset(skip).limit(limit).all()
from .utils import apply_filters_and_sorting

def get_proposicoes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[str] = None
):
    """
    Busca uma lista paginada de proposições, com filtros e ordenação por campo de impacto AI.
    """
    query = db.query(
        models.Proposicao,
        models_ai.ProposicaoAIData.impact_score,
        models_ai.ProposicaoAIData.summary,
        models_ai.ProposicaoAIData.scope,
        models_ai.ProposicaoAIData.magnitude,
        models_ai.ProposicaoAIData.tags
    ).outerjoin(
        models_ai.ProposicaoAIData, models.Proposicao.id == models_ai.ProposicaoAIData.proposicao_id
    )

    # Adiciona lógica de filter dinâmico
    if filters:
        for field, value in filters.items():
            if hasattr(models.Proposicao, field):
                query = query.filter(getattr(models.Proposicao, field) == value)

    # Define allowed fields for sorting and security context awareness
    allowed_sort_fields = {
        "id": models.Proposicao.id,
        "ano": models.Proposicao.ano,
        "dataApresentacao": models.Proposicao.dataApresentacao,
        "impact_score": models_ai.ProposicaoAIData.impact_score
    }

    # Apply dynamic sorting with default fallback
    def default_sort_key(p):
        return (p.Proposicao.dataApresentacao is None, p.Proposicao.dataApresentacao)

    query_result = apply_filters_and_sorting(
        query,
        model=models.Proposicao,
        filters=filters,
        sort=sort,
        allowed_sort_fields=allowed_sort_fields,
        default_sort_field="dataApresentacao"
    )

    # Final response construction
    results = query_result.offset(skip).limit(limit).all()
    proposicoes_list = []
    for p, impact_score, summary, scope, magnitude, tags in results:
        prop_data = {
            'id': p.id,
            'siglaTipo': p.siglaTipo,
            'numero': p.numero,
            'ano': p.ano,
            'urlInteiroTeor': p.urlInteiroTeor,
            'dataApresentacao': p.dataApresentacao,
            'statusProposicao_descricaoSituacao': p.statusProposicao_descricaoSituacao,
            'statusProposicao_descricaoTramitacao': p.statusProposicao_descricaoTramitacao,
            'ementa': p.ementa,
            'impact_score': impact_score or 0.0,   # Ensure non-nullable fields for AI score
            'summary': summary,
            'scope': scope,
            'magnitude': magnitude,
            'tags': tags if tags else [],
                      # Handle potential null lists from AI service
        }
        proposicoes_list.append(prop_data)

    return proposicoes_list

def get_partidos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[str] = None
):
    """
    Busca uma lista paginada de partidos, com ordenação e filtragem dinâmicas.
    """
    from .utils import apply_filters_and_sorting

    # Query inicial
    query = db.query(models.Partido)

    # Define campos permitidos para ordenação e filtragem
    allowed_sort_fields = {
        "sigla": models.Partido.sigla,
        "nome": models.Partido.nome,
    }

    # Aplica filtros e ordenação dinâmicos
    query_result = apply_filters_and_sorting(
        query,
        model=models.Partido,
        filters=filters,
        sort=sort,
        allowed_sort_fields=allowed_sort_fields,
        default_sort_field="sigla"
    )

    # Aplica paginação e retorna resultados
    return query_result.offset(skip).limit(limit).all()

def get_orgaos(db: Session, skip: int = 0, limit: int = 100):
    """
    Busca uma lista paginada de órgãos, ordenados pelo nome, com filtragem e ordenação dinâmicas.
    """
    from .utils import apply_filters_and_sorting

    # Campos permitidos para ordenação e filtragem
    allowed_sort_fields = {
        "nome": models.Orgao.nome,
        "id": models.Orgao.id
    }

    # Inicializa a query com o modelo Orgao
    query = db.query(models.Orgao)

    # Aplica ordenação e filtros dinâmicos (se houver parâmetros na request)
    filters = req.query_params.get('filters', {}) if 'req' in locals() or 'req' in globals() else {}

    query_result = apply_filters_and_sorting(
        query,
        model=models.Orgao,
        filters=filters,
        sort=sort,
        allowed_sort_fields=allowed_sort_fields,
        default_sort_field="nome"
    )

    return query_result.offset(skip).limit(limit).all()

def get_eventos(db: Session, skip: int = 0, limit: int = 100):
    """
    Busca uma lista paginada de eventos, ordenados pelos mais recentes.
    """
    return (
        db.query(models.Evento)
        .order_by(models.Evento.dataHoraInicio.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_votacoes(db: Session, skip: int = 0, limit: int = 100):
    """
    Busca uma lista paginada de votações, ordenadas pelas mais recentes.
    """
    return (
        db.query(models.Votacao)
        .order_by(models.Votacao.dataHoraRegistro.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
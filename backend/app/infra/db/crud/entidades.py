from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import DateTime, Date, desc, asc, func, text
from app.infra.db.models import entidades as models
from app.infra.db.models import ai_data as models_ai 
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
from app.domain.entidades import ProposicaoSchema
from .utils import apply_filters, apply_sorting
import json
from sqlalchemy.dialects.postgresql import aggregate_order_by
from .utils import apply_filters_and_sorting

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
) -> Tuple[List[models.Deputado], int]:
    """
    Busca uma lista paginada de deputados, com filtros e ordenação dinâmicos.
    Retorna os deputados e a contagem total.
    """
    query = db.query(models.Deputado)

    allowed_sort_fields = {
        "nome": models.Deputado.ultimoStatus_nome,
        "siglaUf": models.Deputado.ultimoStatus_siglaUf,
        "siglaPartido": models.Deputado.ultimoStatus_siglaPartido,
        "sexo": models.Deputado.sexo,
        "situacao": models.Deputado.ultimoStatus_situacao,
    }

    # NEW: Modify the filter key for the name to use ilike
    if filters and 'ultimoStatus_nome' in filters:
        filters['ultimoStatus_nome__ilike'] = filters.pop('ultimoStatus_nome')

    # Aplica filtros e ordenação dinâmicos
    query_result = apply_filters_and_sorting(
        query,
        model=models.Deputado,
        filters=filters,
        sort=sort,
        allowed_sort_fields=allowed_sort_fields,
        default_sort_field="nome"
    )

    # Obter a contagem total *após* a filtragem
    total_count = query_result.count()

    # Aplicar paginação e retornar os resultados e a contagem total
    deputados = query_result.offset(skip).limit(limit).all()
    
    return deputados, total_count

def get_deputado_by_id(db: Session, deputado_id: int) -> Optional[models.Deputado]:
    """
    Busca um único deputado pelo ID, incluindo informações detalhadas e proposições associadas.
    """
    deputado = db.query(models.Deputado).filter(models.Deputado.id == deputado_id).first()
    
    if not deputado:
        return None

    # Buscar as proposições associadas a este deputado
    proposicoes = (
        db.query(models.Proposicao)
        .join(models.proposicao_autores, models.Proposicao.id == models.proposicao_autores.c.proposicao_id)
        .filter(models.proposicao_autores.c.deputado_id == deputado_id)
        .all()
    )
    
    # Adicionar a lista de proposições ao objeto do deputado
    # Este campo será preenchido pelo Pydantic ao usar o schema `DeputadoSchemaDetalhado`
    deputado.proposicoes = proposicoes
    
    return deputado

def get_proposicoes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[str] = None,
    scored: Optional[bool] = None
):
    Autor = aliased(models.Deputado)

    author_subquery = (
        db.query(
            models.proposicao_autores.c.proposicao_id.label("pid"),
            func.group_concat(Autor.nomeCivil, ', ').label("autores_db")
        )
        .join(Autor, models.proposicao_autores.c.deputado_id == Autor.id)
        .group_by(models.proposicao_autores.c.proposicao_id)
        .subquery()
    )

    query = db.query(
        models.Proposicao,
        models_ai.ProposicaoAIData.impact_score,
        models_ai.ProposicaoAIData.summary,
        models_ai.ProposicaoAIData.scope,
        models_ai.ProposicaoAIData.magnitude,
        models_ai.ProposicaoAIData.tags,
        author_subquery.c.autores_db
    ).outerjoin(
        models_ai.ProposicaoAIData, models.Proposicao.id == models_ai.ProposicaoAIData.proposicao_id
    ).outerjoin(
        author_subquery, models.Proposicao.id == author_subquery.c.pid
    )

    if filters:
        # Handle author filter separately
        if 'autor' in filters:
            autor_filter_value = f"%{filters['autor']}%"
            query = query.filter(author_subquery.c.autores_db.ilike(autor_filter_value))
            del filters['autor']

        # Handle ProposicaoAIData filters separately
        if 'scope' in filters:
            query = query.filter(models_ai.ProposicaoAIData.scope == filters['scope'])
            del filters['scope']

        if 'magnitude' in filters:
            query = query.filter(models_ai.ProposicaoAIData.magnitude == filters['magnitude'])
            del filters['magnitude']

    if scored:
        query = query.filter(models_ai.ProposicaoAIData.id != None)

    # Apply remaining filters for the Proposicao model
    query = apply_filters(
        query,
        model=models.Proposicao,
        filters=filters
    )

    total_count = query.count()

    allowed_sort_fields = {
        "id": models.Proposicao.id,
        "ano": models.Proposicao.ano,
        "dataApresentacao": models.Proposicao.dataApresentacao,
        "impact_score": models_ai.ProposicaoAIData.impact_score
    }

    query_result = apply_sorting(
        query,
        model=models.Proposicao,
        sort=sort,
        allowed_sort_fields=allowed_sort_fields,
        default_sort_field="dataApresentacao"
    )

    results = query_result.offset(skip).limit(limit).all()
    proposicoes_list = []
    for p, impact_score, summary, scope, magnitude, tags, autores_db in results:
        final_author_name = autores_db or (
            "Poder Executivo" if p.uriAutores and "orgaos" in p.uriAutores else
            p.descricaoTipo if p.descricaoTipo and "Comissão" in p.descricaoTipo else
            "Mesa Diretora" if p.descricaoTipo and "Mesa Diretora" in p.descricaoTipo else
            "Autor não identificado"
        )

        prop_data = {
            'id': p.id,
            'siglaTipo': p.siglaTipo,
            'numero': p.numero,
            'ano': p.ano,
            'ementa': p.ementa,
            'dataApresentacao': p.dataApresentacao.isoformat() if p.dataApresentacao else None,
            'statusProposicao_descricaoSituacao': p.statusProposicao_descricaoSituacao,
            'statusProposicao_descricaoTramitacao': p.statusProposicao_descricaoTramitacao,
            'uriAutores': p.uriAutores,
            'descricaoTipo': p.descricaoTipo,
            'ementaDetalhada': p.ementaDetalhada,
            'keywords': p.keywords,
            'autor': final_author_name,
            'impact_score': impact_score or -1,
            'summary': summary,
            'scope': scope,
            'magnitude': magnitude,
            'tags': tags if tags else [],
        }
        proposicoes_list.append(prop_data)
    return {"proposicoes": proposicoes_list, "total_count": total_count}

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

def get_orgaos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[str] = None
):
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

    # Aplica filtros e ordenação dinâmicos
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

def get_proposicao_by_id(db: Session, proposicao_id: int) -> Optional[ProposicaoSchema]:
    """
    Busca uma única proposição pelo seu ID, juntando os dados de IA.
    """
    # Usamos um 'aliased' para o caso de querermos referenciar a tabela de IA de forma explícita
    ai_data_alias = aliased(models_ai.ProposicaoAIData)

    result = (
        db.query(models.Proposicao, ai_data_alias)
        .outerjoin(ai_data_alias, models.Proposicao.id == ai_data_alias.proposicao_id)
        .filter(models.Proposicao.id == proposicao_id)
        .first()
    )

    if not result:
        return None

    proposicao, ai_data = result
    
    # Monta o objeto de resposta combinando os dados
    prop_data = ProposicaoSchema.from_orm(proposicao)
    if ai_data:
        prop_data.impact_score = ai_data.impact_score
        prop_data.summary = ai_data.summary
        prop_data.scope = ai_data.scope
        prop_data.magnitude = ai_data.magnitude
        prop_data.tags = ai_data.tags

    return prop_data

def get_proposicoes_by_impact_and_date(db: Session, start_date: date, limit: int = 10):
    """
    Busca as proposições com maior impacto dentro de um período de data.
    """
    results = db.query(
        models.Proposicao,
        models_ai.ProposicaoAIData.impact_score
    )\
        .join(models_ai.ProposicaoAIData, models.Proposicao.id == models_ai.ProposicaoAIData.proposicao_id)\
        .filter(models.Proposicao.dataApresentacao >= start_date)\
        .order_by(desc(models_ai.ProposicaoAIData.impact_score))\
        .limit(limit)\
        .all()

    proposicoes_list = []
    for p, impact_score in results:
        prop_data = {
            'id': p.id,
            'siglaTipo': p.siglaTipo,
            'numero': p.numero,
            'ano': p.ano,
            'ementa': p.ementa,
            'dataApresentacao': p.dataApresentacao.isoformat() if p.dataApresentacao else None,
            'statusProposicao_descricaoSituacao': p.statusProposicao_descricaoSituacao,
            'statusProposicao_descricaoTramitacao': p.statusProposicao_descricaoTramitacao,
            'uriAutores': p.uriAutores,
            'descricaoTipo': p.descricaoTipo,
            'ementaDetalhada': p.ementaDetalhada,
            'keywords': p.keywords,
            'impact_score': impact_score or -1,
        }
        proposicoes_list.append(prop_data)

    return proposicoes_list


def get_deputados_ranking_by_impact(db: Session, start_date: date, end_date: date, limit: int = 10):
    """
    Calcula o ranking de deputados com base no impacto total de suas proposições
    em um determinado período.
    """
    # This query will return a list of tuples: (Deputado object, total_impacto)
    ranked_deputados_with_impact = db.query(
        models.Deputado,
        func.sum(models_ai.ProposicaoAIData.impact_score).label('total_impacto')
    ).join(
        models.proposicao_autores, models.Deputado.id == models.proposicao_autores.c.deputado_id
    ).join(
        models.Proposicao, models.proposicao_autores.c.proposicao_id == models.Proposicao.id
    ).join(
        models_ai.ProposicaoAIData, models.Proposicao.id == models_ai.ProposicaoAIData.proposicao_id
    ).filter(
        models.Proposicao.dataApresentacao.between(start_date, end_date)
    ).group_by(
        models.Deputado.id
    ).order_by(
        desc('total_impacto')
    ).limit(limit).all()

    # FastAPI needs a list of objects that match the schema, not tuples.
    # We format the result to match the DeputadoRankingSchema.
    result_list = []
    for deputado, total_impacto in ranked_deputados_with_impact:
        # Create a dictionary from the deputy object
        deputado_data = {c.name: getattr(deputado, c.name) for c in deputado.__table__.columns}
        # Add the calculated total_impacto
        deputado_data['total_impacto'] = total_impacto or 0
        result_list.append(deputado_data)
        
    return result_list


def get_deputados_avg_impact(db: Session, start_date: date, end_date: date) -> float:
    """
    Calcula a média do impacto somado por deputado em um determinado período.
    """
    subquery = db.query(
        func.sum(models_ai.ProposicaoAIData.impact_score).label('total_impacto')
    ).join(
        models.Proposicao, models.Proposicao.id == models_ai.ProposicaoAIData.proposicao_id
    ).join(
        models.proposicao_autores, models.Proposicao.id == models.proposicao_autores.c.proposicao_id
    ).filter(
        models.Proposicao.dataApresentacao.between(start_date, end_date)
    ).group_by(
        models.proposicao_autores.c.deputado_id
    ).subquery()

    result = db.query(func.avg(subquery.c.total_impacto)).scalar()
    return result or 0.0

def get_proposicoes_by_impact_and_date(db: Session, start_date: date, limit: int = 10, scope: Optional[str] = None):
    """
    Busca as proposições com maior impacto dentro de um período de data,
    com um filtro opcional por escopo.
    """
    query = db.query(
        models.Proposicao,
        models_ai.ProposicaoAIData.impact_score
    )\
        .join(models_ai.ProposicaoAIData, models.Proposicao.id == models_ai.ProposicaoAIData.proposicao_id)\
        .filter(models.Proposicao.dataApresentacao >= start_date)

    if scope:
        query = query.filter(models_ai.ProposicaoAIData.scope == scope)

    results = query.order_by(desc(models_ai.ProposicaoAIData.impact_score))\
        .limit(limit)\
        .all()

    proposicoes_list = []
    for p, impact_score in results:
        prop_data = {
            'id': p.id,
            'siglaTipo': p.siglaTipo,
            'numero': p.numero,
            'ano': p.ano,
            'ementa': p.ementa,
            'dataApresentacao': p.dataApresentacao.isoformat() if p.dataApresentacao else None,
            'statusProposicao_descricaoSituacao': p.statusProposicao_descricaoSituacao,
            'statusProposicao_descricaoTramitacao': p.statusProposicao_descricaoTramitacao,
            'uriAutores': p.uriAutores,
            'descricaoTipo': p.descricaoTipo,
            'ementaDetalhada': p.ementaDetalhada,
            'keywords': p.keywords,
            'impact_score': impact_score or -1,
        }
        proposicoes_list.append(prop_data)

    return proposicoes_list

def get_proposal_activity(db: Session, deputado_id: int) -> List[datetime]:
    """
    Fetches the presentation dates of proposals authored by a specific deputy.
    """
    query = (
        db.query(models.Proposicao.dataApresentacao)
        .join(models.proposicao_autores)
        .filter(models.proposicao_autores.c.deputado_id == deputado_id)
        .all()
    )
    # The result will be a list of tuples, so you'll want to extract the dates.
    return [item[0] for item in query]
# camara_insights/app/infra/db/crud/entidades.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import DateTime, Date
from sqlalchemy import desc, asc 
from app.infra.db.models import entidades as models
from app.infra.db.models import ai_data as models_ai 
from datetime import datetime, date
from typing import Optional


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
    sigla_uf: Optional[str] = None,
    sigla_partido: Optional[str] = None
):
    """
    Busca uma lista paginada de deputados, com filtros opcionais por UF e Partido.
    """
    # Começa com a query base
    query = db.query(models.Deputado)

    # Adiciona o filtro de UF se ele for fornecido
    if sigla_uf:
        query = query.filter(models.Deputado.ultimoStatus_siglaUf == sigla_uf.upper())

    # Adiciona o filtro de Partido se ele for fornecido
    if sigla_partido:
        query = query.filter(models.Deputado.ultimoStatus_siglaPartido == sigla_partido.upper())

    # Aplica ordenação, paginação e executa a query
    deputados = query.order_by(models.Deputado.ultimoStatus_nome).offset(skip).limit(limit).all()
    
    return deputados

def get_proposicoes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sigla_tipo: Optional[str] = None,
    ano: Optional[int] = None,
    sort: Optional[str] = None
):
    """
    Busca uma lista paginada de proposições, com filtros e ordenação opcionais.
    """
    # Query base agora une Proposicao com ProposicaoAIData
    query = db.query(
        models.Proposicao.id,
        models.Proposicao.siglaTipo,
        models.Proposicao.numero,
        models.Proposicao.ano,
        models.Proposicao.ementa,
        models.Proposicao.dataApresentacao,
        models.Proposicao.statusProposicao_descricaoSituacao,
        models.Proposicao.statusProposicao_descricaoTramitacao,
        models_ai.ProposicaoAIData.impact_score
    ).outerjoin(
        models_ai.ProposicaoAIData, models.Proposicao.id == models_ai.ProposicaoAIData.proposicao_id
    )


    # Lógica de Filtros
    if sigla_tipo:
        query = query.filter(models.Proposicao.siglaTipo == sigla_tipo.upper())
    if ano:
        query = query.filter(models.Proposicao.ano == ano)

    # Lógica de Ordenação Atualizada
    allowed_sort_fields = {"id", "ano", "dataApresentacao", "impact_score"}
    sort_column = models.Proposicao.ano
    direction_func = desc

    if sort:
        try:
            field_name, direction_str = sort.split(":")
            if field_name in allowed_sort_fields:
                # O campo impact_score pertence ao modelo ProposicaoAIData
                if field_name == "impact_score":
                    sort_column = models_ai.ProposicaoAIData.impact_score
                else:
                    sort_column = getattr(models.Proposicao, field_name)
                
                if direction_str.lower() == "asc":
                    direction_func = asc
        except ValueError:
            pass # Usa o padrão se o formato for inválido

    # Ordenação padrão ou definida
    query = query.order_by(direction_func(sort_column))
    
    # Adicione uma ordenação secundária para garantir resultados consistentes
    if sort_column != models.Proposicao.id:
        query = query.order_by(direction_func(sort_column), desc(models.Proposicao.id))

    results = query.offset(skip).limit(limit).all()

    # O SQLAlchemy retorna uma lista de Tuples, então convertemos para um formato de dicionário
    # para que o Pydantic possa validar e criar o schema de resposta.
    proposicoes_dict = [
        {
            'id': p.id,
            'siglaTipo': p.siglaTipo,
            'numero': p.numero,
            'ano': p.ano,
            'ementa': p.ementa,
            'dataApresentacao': p.dataApresentacao,
            'statusProposicao_descricaoSituacao': p.statusProposicao_descricaoSituacao,
            'statusProposicao_descricaoTramitacao': p.statusProposicao_descricaoTramitacao,
            'impact_score': p.impact_score
        } for p in results
    ]

    return proposicoes_dict

def get_partidos(db: Session, skip: int = 0, limit: int = 100):
    """
    Busca uma lista paginada de partidos, ordenados pela sigla.
    """
    return (
        db.query(models.Partido)
        .order_by(models.Partido.sigla)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_orgaos(db: Session, skip: int = 0, limit: int = 100):
    """
    Busca uma lista paginada de órgãos, ordenados pelo nome.
    """
    return (
        db.query(models.Orgao)
        .order_by(models.Orgao.nome)
        .offset(skip)
        .limit(limit)
        .all()
    )

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
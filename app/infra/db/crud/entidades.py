# camara_insights/app/infra/db/crud/entidades.py
from sqlalchemy.orm import Session
from sqlalchemy import DateTime, Date  # <-- ADICIONAR ESTA LINHA
from app.infra.db.models import entidades as models
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
    query = db.query(models.Proposicao)

    # Lógica de Filtros (como estava antes)
    if sigla_tipo:
        query = query.filter(models.Proposicao.siglaTipo == sigla_tipo.upper())
    if ano:
        query = query.filter(models.Proposicao.ano == ano)

    # --- INÍCIO DA NOVA LÓGICA DE ORDENAÇÃO ---
    allowed_sort_fields = {"id", "ano", "dataApresentacao"}
    if sort:
        # Tenta dividir o parâmetro em campo e direção
        try:
            field_name, direction = sort.split(":")
            if field_name in allowed_sort_fields:
                sort_column = getattr(models.Proposicao, field_name)
                if direction.lower() == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else: # Se o campo não é permitido, usa ordenação padrão
                query = query.order_by(models.Proposicao.ano.desc(), models.Proposicao.id.desc())
        except ValueError: # Se o formato for inválido (ex: "ano" em vez de "ano:asc")
            query = query.order_by(models.Proposicao.ano.desc(), models.Proposicao.id.desc())
    else:
        # Ordenação Padrão
        query = query.order_by(models.Proposicao.ano.desc(), models.Proposicao.id.desc())
    # --- FIM DA NOVA LÓGICA DE ORDENAÇÃO ---
    
    proposicoes = query.offset(skip).limit(limit).all()
    return proposicoes

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
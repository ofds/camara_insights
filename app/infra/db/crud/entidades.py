# camara_insights/app/infra/db/crud/entidades.py
from sqlalchemy.orm import Session
from sqlalchemy import DateTime, Date  # <-- ADICIONAR ESTA LINHA
from app.infra.db.models import entidades as models
from datetime import datetime, date

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
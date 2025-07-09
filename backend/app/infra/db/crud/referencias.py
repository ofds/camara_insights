# camara_insights/app/infra/db/crud/referencias.py
from sqlalchemy.orm import Session
from app.infra.db.models import referencias as models

def upsert_referencia(db: Session, model, data: dict):
    """
    Função genérica para inserir ou atualizar um registro.
    Tenta encontrar o registro pelo campo 'nome' (que é único).
    Se encontrar, ATUALIZA OS DADOS SEM ALTERAR A CHAVE PRIMÁRIA.
    Se não encontrar, cria um novo.
    """
    db_obj = None
    if 'nome' in data:
        db_obj = db.query(model).filter(model.nome == data['nome']).first()

    if db_obj:
        # --- INÍCIO DA CORREÇÃO ---
        # Pega o nome da coluna de chave primária do modelo (ex: 'cod')
        pk_column = model.__table__.primary_key.columns.values()[0].name
        
        # Atualiza todos os campos, EXCETO a chave primária
        for key, value in data.items():
            if key != pk_column:
                setattr(db_obj, key, value)
        # --- FIM DA CORREÇÃO ---
    else:
        # Cria um novo objeto
        db_obj = model(**data)
        db.add(db_obj)

        

def bulk_upsert_referencias(db: Session, model, data_list: list[dict]):
    """
    Realiza o upsert de uma lista de dados de referência de forma eficiente.
    """
    for item_data in data_list:
        # Omitir chaves que não estão no modelo para evitar erros
        fields = {c.name for c in model.__table__.columns}
        filtered_data = {k: v for k, v in item_data.items() if k in fields}
        upsert_referencia(db, model, filtered_data)
    
    db.commit()
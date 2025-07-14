# camara_insights/scripts/sync_all.py
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Type, Tuple
from dateutil.parser import parse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Date, DateTime
from app.infra.db.session import SessionLocal
from app.infra.db.models.entidades import Base
from app.infra.camara_api import camara_api_client
from app.infra.db.models import entidades as models

# --- Funções de Sincronização Principais ---

async def fetch_and_process_paginated_data(endpoint: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    Busca todos os dados de um endpoint paginado da API da Câmara.
    (CORRIGIDO com paginação manual para maior robustez)
    """
    all_data: List[Dict[str, Any]] = []
    page = 1
    
    while True:
        # Copia os parâmetros originais e adiciona/atualiza a página
        current_params = params.copy()
        current_params['pagina'] = page
        
        print(f"Buscando: {endpoint} | Página: {page}")
        api_response = await camara_api_client.get(endpoint=endpoint, params=current_params)
        
        # Verifica se a resposta é válida e contém dados
        if api_response and 'dados' in api_response and api_response['dados']:
            all_data.extend(api_response['dados'])
            
            # Verifica se existe um link 'next' para saber se podemos continuar
            next_link = next((link for link in api_response.get('links', []) if link['rel'] == 'next'), None)
            self_link = next((link for link in api_response.get('links', []) if link['rel'] == 'self'), None)

            # Condição de parada: não há link 'next' ou ele é igual ao 'self'
            if not next_link or (self_link and next_link['href'] == self_link['href']):
                print(f"Fim da paginação para {endpoint}.")
                break
            
            page += 1
        else:
            print(f"Não foram encontrados mais dados ou houve erro para o endpoint {endpoint} na página {page}.")
            break
            
    return all_data

def upsert_entidade(db: Session, model: Type[Base], data: Dict[str, Any]):
    """
    Realiza o 'upsert' (insert ou update) de uma única entidade no banco de dados.
    Aprimorado para lidar com relacionamentos e conversão de tipos de dados.
    """
    pk_name = model.__mapper__.primary_key[0].name
    pk_value = data.get(pk_name)
    
    if not pk_value:
        print(f"Alerta: Dado para {model.__tablename__} sem chave primária '{pk_name}'. Dado: {data}")
        return

    model_columns = {c.name: c.type for c in model.__table__.columns}
    filtered_data = {k: v for k, v in data.items() if k in model_columns}

    # --- CORREÇÃO: Conversão de Tipos de Dados ---
    for key, value in filtered_data.items():
        if value is None:
            continue
        
        column_type = model_columns.get(key)
        
        # Converte strings para objetos date/datetime
        if isinstance(column_type, (Date, DateTime)) and isinstance(value, str):
            try:
                parsed_datetime = parse(value)
                if isinstance(column_type, Date):
                    filtered_data[key] = parsed_datetime.date()
                else:
                    filtered_data[key] = parsed_datetime
            except (ValueError, TypeError):
                print(f"Aviso: Não foi possível converter a string '{value}' para data na coluna '{key}'. Usando Nulo.")
                filtered_data[key] = None
    
    # --- NOVO: Lida com o relacionamento Votacao -> Proposicao ---
    if model == models.Votacao and data.get('proposicao') and data['proposicao'].get('id'):
        filtered_data['proposicao_id'] = data['proposicao']['id']


    stmt = insert(model.__table__).values(**filtered_data)
    update_dict = {k: v for k, v in filtered_data.items() if k != pk_name}
    
    if not update_dict:
        stmt = stmt.on_conflict_do_nothing(index_elements=[pk_name])
    else:
        stmt = stmt.on_conflict_do_update(
            index_elements=[pk_name],
            set_=update_dict
        )
    
    db.execute(stmt)

    db_item = db.query(model).options(
        joinedload('*')
    ).filter_by(**{pk_name: pk_value}).one_or_none()

    if not db_item:
        return

    if model == models.Proposicao and 'autores' in data and data['autores']:
        db_item.autores.clear()
        for autor_info in data['autores']:
            autor_uri = autor_info.get('uri')
            if autor_uri:
                autor_id = int(autor_uri.split('/')[-1])
                autor_db = db.query(models.Deputado).get(autor_id)
                if autor_db:
                    db_item.autores.append(autor_db)
    
    if model == models.Evento and 'deputados' in data.get('localCamara', {}):
        db_item.participantes.clear()
        for deputado_info in data['localCamara']['deputados']:
            deputado_uri = deputado_info.get('uri')
            if deputado_uri:
                deputado_id = int(deputado_uri.split('/')[-1])
                deputado_db = db.query(models.Deputado).get(deputado_id)
                if deputado_db:
                    db_item.participantes.append(deputado_db)

async def sync_entidade_com_detalhes(db: Session, model: Type[Base], endpoint: str, params: Dict[str, Any] = {}):
    """
    Função genérica para sincronizar entidades que seguem o padrão lista -> detalhes.
    """
    print(f"Iniciando sincronização com detalhes para {model.__tablename__}...")
    
    summary_data = await fetch_and_process_paginated_data(endpoint, params)
    
    if not summary_data:
        print(f"Nenhum item encontrado para {model.__tablename__}.")
        return

    print(f"{len(summary_data)} itens descobertos para {model.__tablename__}. Buscando detalhes...")
    
    tasks = []
    for item in summary_data:
        if 'uri' in item:
            detail_endpoint = item['uri'].replace(camara_api_client.base_url, "")
            tasks.append(camara_api_client.get(endpoint=detail_endpoint))

    batch_size = 10
    for i in range(0, len(tasks), batch_size):
        batch_tasks = tasks[i:i + batch_size]
        responses = await asyncio.gather(*batch_tasks)
        for response in responses:
            if response and 'dados' in response:
                upsert_entidade(db, model, response['dados'])
        db.commit()
        print(f"Lote {i//batch_size + 1} de {len(tasks)//batch_size + 1} para {model.__tablename__} processado.")
        
    print(f"Sincronização com detalhes para {model.__tablename__} concluída.")

async def sync_child_entidade(db: Session, parent_model: Type[Base], child_model: Type[Base], endpoint_template: str, child_fk_name: str, params: Dict[str, Any] = {}):
    """
    Sincroniza uma entidade 'filha' que depende de uma 'pai'.
    """
    print(f"Iniciando sincronização de entidade filha: {child_model.__tablename__}")
    parent_ids: List[Tuple[Any]] = db.query(parent_model.id).all()

    tasks = []
    for (parent_id,) in parent_ids:
        endpoint = endpoint_template.format(id=parent_id)
        tasks.append(fetch_and_process_paginated_data(endpoint, params))

    batch_size = 20
    for i in range(0, len(tasks), batch_size):
        batch_tasks = tasks[i:i+batch_size]
        results = await asyncio.gather(*batch_tasks)
        
        all_child_data = []
        for idx, child_data_list in enumerate(results):
            current_parent_id = parent_ids[i+idx][0]
            for child_data in child_data_list:
                child_data[child_fk_name] = current_parent_id
                child_data.pop('id', None) 
                all_child_data.append(child_data)
        
        if all_child_data:
            # A conversão de tipos também é necessária aqui
            for child_data in all_child_data:
                model_columns = {c.name: c.type for c in child_model.__table__.columns}
                for key, value in child_data.items():
                    if value is None: continue
                    column_type = model_columns.get(key)
                    if isinstance(column_type, (Date, DateTime)) and isinstance(value, str):
                        try:
                            parsed_datetime = parse(value)
                            if isinstance(column_type, Date):
                                child_data[key] = parsed_datetime.date()
                            else:
                                child_data[key] = parsed_datetime
                        except (ValueError, TypeError):
                            child_data[key] = None
            
            db.bulk_insert_mappings(child_model, all_child_data)
            db.commit()
            print(f"Lote {i//batch_size + 1} para {child_model.__tablename__} processado. {len(all_child_data)} registros inseridos.")

# --- Função Principal ---

async def main():
    db = SessionLocal()
    try:
        start_date = "2025-06-01"
        current_year = str(datetime.now().year)

        # 1. Sincronizar Entidades Principais (com detalhes)
        await sync_entidade_com_detalhes(db, models.Deputado, "/deputados", params={'itens': 100})
        await sync_entidade_com_detalhes(db, models.Partido, "/partidos", params={'itens': 100})
        await sync_entidade_com_detalhes(db, models.Orgao, "/orgaos", params={'itens': 100})
        await sync_entidade_com_detalhes(db, models.Proposicao, "/proposicoes", 
                                       params={'dataApresentacaoInicio': start_date, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
        await sync_entidade_com_detalhes(db, models.Evento, "/eventos", 
                                       params={'dataInicio': start_date, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
        await sync_entidade_com_detalhes(db, models.Votacao, "/votacoes", 
                                       params={'dataInicio': start_date, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
        
        # 2. Sincronizar Novas Entidades de Nível Superior
        print("Sincronizando Frentes, Blocos e Grupos...")
        frentes_data = await fetch_and_process_paginated_data("/frentes", {'itens': 100})
        for item in frentes_data: upsert_entidade(db, models.Frente, item)
        
        blocos_data = await fetch_and_process_paginated_data("/blocos", {'itens': 100})
        for item in blocos_data: upsert_entidade(db, models.Bloco, item)

        grupos_data = await fetch_and_process_paginated_data("/grupos", {'itens': 100})
        for item in grupos_data: upsert_entidade(db, models.Grupo, item)
        db.commit()
        print("Frentes, Blocos e Grupos sincronizados.")

        # 3. Sincronizar Entidades Filhas
        print("Limpando dados de entidades filhas antes da sincronização...")
        db.execute(models.Despesa.__table__.delete())
        db.execute(models.Discurso.__table__.delete())
        db.execute(models.Tramitacao.__table__.delete())
        db.execute(models.Voto.__table__.delete())
        db.commit()

        await sync_child_entidade(db, models.Deputado, models.Despesa, "/deputados/{id}/despesas", "deputado_id", params={'ano': current_year, 'itens': 100})
        await sync_child_entidade(db, models.Deputado, models.Discurso, "/deputados/{id}/discursos", "deputado_id", params={'dataInicio': start_date, 'itens': 100})
        
        # CORREÇÃO: Removido o parâmetro 'itens' que não é suportado pela API de tramitações e votos.
        await sync_child_entidade(db, models.Proposicao, models.Tramitacao, "/proposicoes/{id}/tramitacoes", "proposicao_id")
        await sync_child_entidade(db, models.Votacao, models.Voto, "/votacoes/{id}/votos", "votacao_id")

    finally:
        db.close()

if __name__ == "__main__":
    print("--- INICIANDO SINCRONIZAÇÃO GERAL (COM ENRIQUECIMENTO E DADOS ANINHADOS) ---")
    asyncio.run(main())
    print("--- SINCRONIZAÇÃO GERAL CONCLUÍDA ---")
# camara_insights/scripts/sync_all.py
import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infra.camara_api import camara_api_client
from app.infra.db.session import SessionLocal
from app.infra.db.crud.entidades import bulk_upsert_entidades
from app.infra.db.models import entidades as models

async def sync_entidade(db, model, endpoint, params={}):
    """ Função genérica para sincronizar uma entidade paginada. """
    print(f"Iniciando sincronização para {model.__tablename__}...")
    
    all_data = []
    next_url = f"{camara_api_client.base_url}{endpoint}"
    current_params = params.copy()
    
    while next_url:
        print(f"Buscando dados de: {next_url.split('?')[0]} com params: {current_params}")
        
        clean_endpoint = next_url.replace(camara_api_client.base_url, '')
        api_response = await camara_api_client.get(endpoint=clean_endpoint)
        
        if api_response and 'dados' in api_response:
            all_data.extend(api_response['dados'])
            
            self_link = next((link for link in api_response.get('links', []) if link['rel'] == 'self'), None)
            next_link = next((link for link in api_response.get('links', []) if link['rel'] == 'next'), None)
            
            if next_link and self_link and next_link['href'] == self_link['href']:
                print("Detectado link 'next' para a própria página. Finalizando paginação.")
                next_url = None
            else:
                next_url = next_link['href'] if next_link else None

            current_params = {}
        else:
            print(f"Não foram encontrados mais dados ou houve erro para {model.__tablename__} em {next_url}.")
            break
            
    if all_data:
        # --- INÍCIO DA NOVA CORREÇÃO ---
        # De-duplica a lista de dados com base na chave primária 'id' antes de salvar.
        # Isso protege contra o bug da API que retorna o mesmo item em páginas diferentes.
        print(f"Total de {len(all_data)} registros brutos encontrados. Removendo duplicatas...")
        seen_ids = set()
        unique_data = []
        # Itera na ordem inversa para manter a ocorrência mais recente em caso de duplicatas
        for item in reversed(all_data):
            item_id = item.get('id')
            if item_id is not None and item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_data.insert(0, item) # Insere no início para manter a ordem original
        
        print(f"{len(unique_data)} registros únicos encontrados para {model.__tablename__}. Salvando no banco...")
        bulk_upsert_entidades(db, model, unique_data)
        # --- FIM DA NOVA CORREÇÃO ---
        print(f"Registros de {model.__tablename__} salvos com sucesso.")
    else:
        print(f"Nenhum registro encontrado para {model.__tablename__}.")

async def main():
    db = SessionLocal()
    try:
        start_date = "2023-01-01" 

        # Sincroniza Deputados
        await sync_entidade(db, models.Deputado, "/deputados")
        
        # Sincroniza Partidos (com a sua sugestão de `itens=100`)
        await sync_entidade(db, models.Partido, "/partidos", params={'itens': 100})

        # Sincroniza Órgãos
        await sync_entidade(db, models.Orgao, "/orgaos", params={'itens': 100})

        # Sincroniza Proposições por período
        await sync_entidade(db, models.Proposicao, "/proposicoes", 
                            params={'dataApresentacaoInicio': start_date, 'itens':100, 'ordem': 'ASC', 'ordenarPor': 'id'})

        # Sincroniza Eventos por período
        await sync_entidade(db, models.Evento, "/eventos", 
                            params={'dataInicio': start_date, 'itens':100, 'ordem': 'ASC', 'ordenarPor': 'id'})
                            
        # Sincroniza Votações por período
        await sync_entidade(db, models.Votacao, "/votacoes", 
                            params={'dataInicio': start_date, 'itens':100, 'ordem': 'ASC', 'ordenarPor': 'id'})

    finally:
        db.close()

if __name__ == "__main__":
    print("--- INICIANDO SINCRONIZAÇÃO GERAL DAS ENTIDADES ---")
    asyncio.run(main())
    print("--- SINCRONIZAÇÃO GERAL CONCLUÍDA ---")
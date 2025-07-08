# camara_insights/scripts/sync_referencias.py
import asyncio
import sys
import os

# Adiciona o diretório raiz do projeto ao path do Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infra.camara_api import camara_api_client
from app.infra.db.session import SessionLocal
from app.infra.db.crud.referencias import bulk_upsert_referencias
from app.infra.db.models import referencias as models

# Mapeia os endpoints da API para os modelos do banco de dados
ENDPOINTS_E_MODELOS = {
    "/referencias/tiposProposicao": models.TiposProposicao,
    "/referencias/proposicoes/codTema": models.ProposicaoTemas,
    "/referencias/situacoesProposicao": models.ProposicaoSituacoes,
    "/referencias/tiposTramitacao": models.TiposTramitacao,
    "/referencias/tiposAutor": models.TiposAutor,
    "/referencias/situacoesDeputado": models.DeputadoSituacoes,
    "/referencias/situacoesEvento": models.EventoSituacoes,
    "/referencias/tiposEvento": models.TiposEvento,
    "/referencias/tiposOrgao": models.TiposOrgao,
    "/referencias/uf": models.UFs,
}

async def sync_all_referencias():
    db = SessionLocal()
    try:
        for endpoint, model in ENDPOINTS_E_MODELOS.items():
            print(f"Sincronizando {model.__tablename__} a partir de {endpoint}...")
            
            api_data = await camara_api_client.get(endpoint)
            
            if api_data and 'dados' in api_data:
                data_list = api_data['dados']
                
                # Generaliza a conversão de 'id' para 'cod'
                for item in data_list:
                    if 'id' in item and 'cod' not in item:
                        item['cod'] = item.pop('id')
                
                # --- INÍCIO DA NOVA CORREÇÃO ---
                # Remove o 'cod' se ele for uma string vazia, para que o DB
                # possa autoincrementar a chave primária.
                for item in data_list:
                    if item.get('cod') == '':
                        del item['cod']
                # --- FIM DA NOVA CORREÇÃO ---

                bulk_upsert_referencias(db, model, data_list)
                print(f"{len(data_list)} registros sincronizados para {model.__tablename__}.")
            else:
                print(f"Não foram encontrados dados ou houve um erro ao buscar em {endpoint}")
    finally:
        db.close()

        
if __name__ == "__main__":
    print("Iniciando a sincronização de todas as tabelas de referência...")
    asyncio.run(sync_all_referencias())
    print("Sincronização concluída.")
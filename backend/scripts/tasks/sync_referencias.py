"""
Refactored sync_referencias.py using SOLID principles.
This script now acts as a simple entry point that delegates to DataSyncService.
"""

import asyncio
import sys
import os
from typing import Dict

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.infra.db.session import SessionLocal
from src.services.data_sync_service import DataSyncService
from app.infra.db.models import entidades as models


async def sync_references() -> Dict[str, int]:
    """Sync all reference tables from Câmara API."""
    session = SessionLocal()
    try:
        service = DataSyncService(session)
        
        print("--- Starting synchronization of reference tables ---")
        
        # Define endpoint to model mapping
        endpoint_model_mapping = {
            "/referencias/tiposProposicao": models.TipoProposicao,
            "/referencias/tiposOrgao": models.TipoOrgao,
            "/referencias/situacoesProposicao": models.SituacaoProposicao,
            "/referencias/situacoesEvento": models.SituacaoEvento,
            "/referencias/tiposEvento": models.TipoEvento,
            "/referencias/tiposDiscurso": models.TipoDiscurso,
            "/referencias/tiposTramitacao": models.TipoTramitacao,
            "/referencias/tiposVoto": models.TipoVoto,
            "/referencias/uf": models.UF,
            "/referencias/tiposFuncao": models.TipoFuncao,
            "/referencias/tiposAutor": models.TipoAutor,
            "/referencias/cargosOrgao": models.CargoOrgao,
            "/referencias/periodos": models.Periodo,
            "/referencias/meses": models.Mes,
            "/referencias/sexos": models.Sexo,
            "/referencias/tiposProposicao": models.TipoProposicao,
        }
        
        # Sync all references
        results = await service.sync_references(endpoint_model_mapping)
        
        print("\n--- Reference synchronization completed! ---")
        for table_name, count in results.items():
            print(f"  {table_name}: {count} records")
        
        return results
        
    finally:
        session.close()


async def main():
    """Main entry point for sync_referencias."""
    print("--- EXECUTING REFERENCE SYNCHRONIZATION ---")
    await sync_references()
    print("\n--- SYNCHRONIZATION COMPLETED ---")


if __name__ == "__main__":
    asyncio.run(main())
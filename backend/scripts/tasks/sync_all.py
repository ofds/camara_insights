"""
Refactored sync_all.py using SOLID principles.
This script now acts as a simple entry point that delegates to DataSyncService.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.infra.db.session import SessionLocal
from src.services.data_sync_service import DataSyncService
from app.infra.db.models import entidades as models


async def sync_all_data(year: int = 2023) -> None:
    """Sync all data from Câmara API."""
    session = SessionLocal()
    try:
        service = DataSyncService(session, concurrency_limit=10, batch_size=50)
        
        print(f"--- Starting general synchronization since {year} ---")
        
        # Sync main entities
        await service.sync_entity_with_details(
            models.Deputado, 
            "/deputados",
            params={"itens": 100, "ordem": "ASC", "ordenarPor": "nome"}
        )
        
        await service.sync_entity_with_details(
            models.Partido, 
            "/partidos",
            params={"itens": 100, "ordem": "ASC", "ordenarPor": "sigla"}
        )
        
        await service.sync_entity_with_details(
            models.Orgao, 
            "/orgaos",
            params={"itens": 100, "ordem": "ASC", "ordenarPor": "sigla"}
        )
        
        await service.sync_entity_with_details(
            models.Proposicao, 
            "/proposicoes",
            params={"ano": year, "itens": 100, "ordem": "ASC", "ordenarPor": "id"}
        )
        
        await service.sync_entity_with_details(
            models.Evento, 
            "/eventos",
            params={"dataInicio": f"{year}-01-01", "itens": 100, "ordem": "ASC", "ordenarPor": "dataHoraInicio"}
        )
        
        # Sync child entities
        await service.sync_child_entities(
            models.Deputado, 
            models.Discurso, 
            "/deputados/{id}/discursos", 
            "deputado_id",
            params={"dataInicio": f"{year}-01-01", "itens": 100}
        )
        
        await service.sync_child_entities(
            models.Proposicao, 
            models.Tramitacao, 
            "/proposicoes/{id}/tramitacoes", 
            "proposicao_id",
            paginated=False
        )
        
        await service.sync_child_entities(
            models.Votacao, 
            models.Voto, 
            "/votacoes/{id}/votos", 
            "votacao_id",
            paginated=False
        )
        
        print("\n--- General synchronization completed ---")
        
    finally:
        session.close()
        await camara_api_client.close()


async def main():
    """Main entry point for sync_all."""
    print("--- STARTING GENERAL SYNCHRONIZATION (OPTIMIZED) ---")
    await sync_all_data()
    print("\n--- GENERAL SYNCHRONIZATION COMPLETED ---")


if __name__ == "__main__":
    asyncio.run(main())
"""
Refactored sync_authors_only.py using SOLID principles.
This script now acts as a simple entry point that delegates to DataSyncService.
"""

import asyncio
import sys
import os
from typing import Dict, List, Tuple

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.infra.db.session import SessionLocal
from src.services.data_sync_service import DataSyncService
from app.infra.db.models import entidades as models


async def sync_proposition_authors() -> int:
    """Sync only the authors of propositions."""
    session = SessionLocal()
    try:
        service = DataSyncService(session, concurrency_limit=10, batch_size=50)
        
        print("--- Starting synchronization of proposition authors ---")
        
        # Get propositions with author URIs
        from src.data.repository import ProposicaoRepository
        repository = ProposicaoRepository(session, models.Proposicao)
        
        propositions = repository.get_with_autor_uris()
        print(f"Found {len(propositions)} propositions with author URIs")
        
        # Process authors in batches
        semaphore = asyncio.Semaphore(service.concurrency_limit)
        
        async def fetch_authors_batch(proposition_ids):
            async with semaphore:
                all_authors = []
                for prop_id, uri_autores in proposition_ids:
                    if uri_autores:
                        authors_data = await service._fetch_paginated_data(
                            uri_autores.replace(service._get_base_url(), ""),
                            params={"itens": 100}
                        )
                        for author in authors_data:
                            author['proposicao_id'] = prop_id
                            all_authors.append(author)
                return all_authors
        
        # Process in batches
        total_authors = 0
        batch_size = 100
        
        for i in range(0, len(propositions), batch_size):
            batch = propositions[i:i + batch_size]
            authors_data = await fetch_authors_batch(batch)
            
            if authors_data:
                # Handle author relationships through the many-to-many table
                from sqlalchemy import insert
                from sqlalchemy.dialects.postgresql import insert as pg_insert
                
                # Prepare data for the relationship table
                relationship_data = []
                for author in authors_data:
                    if 'uri' in author and 'proposicao_id' in author:
                        # Extract deputado_id from URI
                        deputado_id = int(author['uri'].split('/')[-1])
                        relationship_data.append({
                            'proposicao_id': author['proposicao_id'],
                            'deputado_id': deputado_id
                        })
                
                if relationship_data:
                    # Use bulk insert for the relationship table
                    stmt = pg_insert(models.proposicao_autores).values(relationship_data)
                    stmt = stmt.on_conflict_do_nothing()
                    session.execute(stmt)
                    session.commit()
                    total_authors += len(relationship_data)
            
            print(f"Processed batch {i//batch_size + 1}/{(len(propositions)//batch_size) + 1}")
        
        print(f"--- Synchronization of proposition authors completed! {total_authors} authors processed ---")
        return total_authors
        
    finally:
        session.close()
        await service._get_api_client().close()


async def main():
    """Main entry point for sync_authors_only."""
    print("--- EXECUTING SCRIPT TO SYNC ONLY PROPOSITION AUTHORS (IN BATCHES) ---")
    await sync_proposition_authors()
    print("\n--- PROCESS COMPLETED ---")


if __name__ == "__main__":
    asyncio.run(main())
"""
Data synchronization service implementing business logic for syncing data from Câmara API.
This service follows SOLID principles by separating concerns and using dependency injection.
"""

import asyncio
from typing import List, Dict, Any, Type, Optional, Tuple
from datetime import datetime
from collections.abc import MutableMapping
from dateutil.parser import parse
from sqlalchemy.orm import Session
from sqlalchemy import Date, DateTime

from app.infra.camara_api import camara_api_client
from src.data.repository import BaseRepository, ProposicaoRepository
from app.infra.db.models.entidades import Base, Proposicao, Tramitacao


class DataSyncService:
    """Service responsible for synchronizing data from Câmara API to database."""
    
    def __init__(self, session: Session, concurrency_limit: int = 10, batch_size: int = 50):
        self.session = session
        self.concurrency_limit = concurrency_limit
        self.batch_size = batch_size
    
    @staticmethod
    def _flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten a nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, MutableMapping):
                items.extend(DataSyncService._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def _transform_data_for_model(data: Dict[str, Any], model: Type[Base]) -> Dict[str, Any]:
        """Transform API data to match database model structure."""
        flattened_data = DataSyncService._flatten_dict(data)
        model_columns = {c.name: c.type for c in model.__table__.columns}
        filtered_data = {k: v for k, v in flattened_data.items() if k in model_columns}
        
        # Handle date/datetime parsing
        for key, value in filtered_data.items():
            if value is None:
                continue
            column_type = model_columns.get(key)
            if isinstance(column_type, (Date, DateTime)) and isinstance(value, str):
                try:
                    parsed_datetime = parse(value)
                    filtered_data[key] = parsed_datetime.date() if isinstance(column_type, Date) else parsed_datetime
                except (ValueError, TypeError):
                    filtered_data[key] = None
        
        # Handle special cases
        if model.__name__ == 'Votacao' and flattened_data.get('proposicao_id'):
            filtered_data['proposicao_id'] = flattened_data['proposicao_id']
        
        return filtered_data
    
    async def _fetch_paginated_data(self, endpoint: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        """Fetch all paginated data from an API endpoint."""
        all_data = []
        page = 1
        
        param_str = '&'.join([f"{k}={v}" for k, v in params.items() if k != 'pagina'])
        print(f"Fetching: {endpoint}?{param_str}...")
        
        while True:
            current_params = params.copy()
            current_params['pagina'] = page
            
            print(f"  - Page: {page}")
            api_response = await camara_api_client.get(endpoint=endpoint, params=current_params)
            
            if api_response and 'dados' in api_response and api_response['dados']:
                all_data.extend(api_response['dados'])
                
                next_link = next((link for link in api_response.get('links', []) if link['rel'] == 'next'), None)
                if not next_link:
                    print(f"End of pagination for {endpoint}.")
                    break
                
                page += 1
            else:
                print(f"No more data found or error for endpoint {endpoint} on page {page}.")
                break
                
        return all_data
    
    async def _fetch_with_semaphore(self, semaphore: asyncio.Semaphore, endpoint: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Wrapper for API calls with concurrency control."""
        async with semaphore:
            return await camara_api_client.get(endpoint=endpoint, params=params)
    
    async def sync_entity_with_details(self, model: Type[Base], endpoint: str, params: Dict[str, Any] = {}) -> List[int]:
        """Sync entities with detailed information and return their IDs."""
        param_str = ', '.join([f"{k}: {v}" for k, v in params.items()])
        print(f"\n--- Starting sync for {model.__tablename__} with filters: [{param_str}] ---")
        
        summary_data = await self._fetch_paginated_data(endpoint, params)
        
        if not summary_data:
            print(f"No items found for {model.__tablename__} with applied filters.")
            return []
        
        print(f"{len(summary_data)} items discovered. Fetching details...")
        
        repository = BaseRepository(self.session, model)
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        all_tasks = []
        processed_ids = []

        pk_name = model.__mapper__.primary_key[0].name
        
        for item in summary_data:
            if 'uri' in item and item['uri']:
                detail_endpoint = item['uri'].replace(camara_api_client.base_url, "")
                all_tasks.append(self._fetch_with_semaphore(semaphore, detail_endpoint))
        
        for i in range(0, len(all_tasks), self.batch_size):
            batch_tasks = all_tasks[i:i + self.batch_size]
            responses = await asyncio.gather(*batch_tasks)
            
            all_data_to_upsert = []
            for response in responses:
                if not (response and 'dados' in response):
                    continue
                
                transformed_data = self._transform_data_for_model(response['dados'], model)
                all_data_to_upsert.append(transformed_data)
                if pk_name in transformed_data:
                    processed_ids.append(transformed_data[pk_name])

            if all_data_to_upsert:
                repository.bulk_upsert(all_data_to_upsert)
            
            print(f"Batch {i//self.batch_size + 1}/{(len(all_tasks)//self.batch_size) + 1} for {model.__tablename__} processed.")
        
        print(f"Sync with details for {model.__tablename__} completed. {len(processed_ids)} records processed.")
        return processed_ids
    
    async def sync_child_entities(self, parent_model: Type[Base], child_model: Type[Base], 
                                endpoint_template: str, child_fk_name: str, 
                                params: Dict[str, Any] = {}, paginated: bool = True,
                                parent_ids_list: Optional[List[int]] = None) -> int:
        """Sync child entities for a parent entity."""
        param_str = ', '.join([f"{k}: {v}" for k, v in params.items()])
        print(f"\n--- Syncing child entity: {child_model.__tablename__} with filters: [{param_str}] ---")
        
        if parent_ids_list:
            parent_ids = parent_ids_list
        else:
            parent_ids = [pid[0] for pid in self.session.query(parent_model.id).all()]

        if not parent_ids:
            print(f"No parent IDs provided or found for {parent_model.__tablename__}.")
            return 0

        semaphore = asyncio.Semaphore(self.concurrency_limit)
        
        async def fetch_child_data(parent_id):
            endpoint = endpoint_template.format(id=parent_id)
            if paginated:
                return await self._fetch_paginated_data(endpoint, params)
            else:
                response = await self._fetch_with_semaphore(semaphore, endpoint)
                return response.get('dados', []) if response else []
        
        all_child_data = []
        for i in range(0, len(parent_ids), self.batch_size):
            parent_batch = parent_ids[i:i + self.batch_size]
            tasks = [fetch_child_data(pid) for pid in parent_batch]
            results = await asyncio.gather(*tasks)
            
            for idx, child_data_list in enumerate(results):
                if not child_data_list:
                    continue
                current_parent_id = parent_batch[idx]
                for child_data in child_data_list:
                    child_data[child_fk_name] = current_parent_id
                    child_data.pop('id', None)
                    all_child_data.append(child_data)
            
            print(f"Parent batch {i//self.batch_size + 1}/{(len(parent_ids)//self.batch_size) + 1} for {child_model.__tablename__} processed.")
        
        if all_child_data:
            repository = BaseRepository(self.session, child_model)
            repository.bulk_insert(all_child_data)
            print(f"Bulk insert of {len(all_child_data)} records for {child_model.__tablename__} completed.")
        
        print(f"Sync of {child_model.__tablename__} completed.")
        return len(all_child_data)
    
    async def sync_references(self, endpoint_model_mapping: Dict[str, Type[Base]]) -> Dict[str, int]:
        """Sync all reference tables."""
        results = {}
        
        for endpoint, model in endpoint_model_mapping.items():
            print(f"Syncing {model.__tablename__} from {endpoint}...")
            
            api_data = await camara_api_client.get(endpoint)
            
            if api_data and 'dados' in api_data:
                data_list = api_data['dados']
                
                # Generalize the conversion of 'id' to 'cod'
                for item in data_list:
                    if 'id' in item and 'cod' not in item:
                        item['cod'] = item.pop('id')
                    
                    # Remove empty 'cod' values for auto-increment
                    if item.get('cod') == '':
                        del item['cod']
                
                repository = BaseRepository(self.session, model)
                count = repository.bulk_upsert(data_list)
                results[model.__tablename__] = count
                print(f"{count} records synced for {model.__tablename__}.")
            else:
                print(f"No data found or error fetching from {endpoint}")
                results[model.__tablename__] = 0
        
        return results
    
    def cleanup_relationship_tables(self, tables: List[Type[Base]]) -> Dict[str, int]:
        """Clean up relationship tables before syncing."""
        results = {}
        for table in tables:
            repository = BaseRepository(self.session, table)
            count = repository.delete_all()
            results[table.__tablename__] = count
            print(f"Cleaned {count} records from {table.__tablename__}")
        return results
    
    async def sync_propositions(self, params: Dict[str, Any] = None, batch_size: int = 50) -> List[int]:
        """Sync propositions with given parameters and return their IDs."""
        return await self.sync_entity_with_details(Proposicao, "/proposicoes", params or {})
    
    async def sync_proposition_authors(self, proposition_ids: Optional[List[int]] = None) -> int:
        """Sync proposition authors, optionally for a specific list of propositions."""
        from app.infra.db.models.entidades import proposicao_autores
        
        print("\n--- Syncing proposition authors ---")
        
        repository = ProposicaoRepository(self.session, Proposicao)
        
        if proposition_ids:
            propositions_query = self.session.query(Proposicao).filter(Proposicao.id.in_(proposition_ids))
        else:
            propositions_query = self.session.query(Proposicao)

        propositions = propositions_query.all()

        if not propositions:
            print("No propositions to sync authors for.")
            return 0
        
        total_authors = 0
        
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        
        async def fetch_authors_for_proposition(proposition):
            async with semaphore:
                endpoint = f"/proposicoes/{proposition.id}/autores"
                response = await camara_api_client.get(endpoint)
                if response and 'dados' in response:
                    authors = response['dados']
                    relationship_data = []
                    for author in authors:
                        if 'uri' in author and '/deputados/' in author['uri']:
                            try:
                                deputado_id = int(author['uri'].split('/')[-1])
                                relationship_data.append({
                                    'proposicao_id': proposition.id,
                                    'deputado_id': deputado_id
                                })
                            except (ValueError, IndexError):
                                pass # Ignore if ID is not found
                    return relationship_data
                return []
        
        # Process in batches
        for i in range(0, len(propositions), self.batch_size):
            batch = propositions[i:i + self.batch_size]
            tasks = [fetch_authors_for_proposition(prop) for prop in batch]
            results = await asyncio.gather(*tasks)
            
            # Flatten results and insert
            all_relationships = [item for sublist in results for item in sublist]
            
            if all_relationships:
                from sqlalchemy.dialects.postgresql import insert as pg_insert
                stmt = pg_insert(proposicao_autores).values(all_relationships)
                stmt = stmt.on_conflict_do_nothing()
                self.session.execute(stmt)
                self.session.commit()
                total_authors += len(all_relationships)
            
            print(f"Processed batch {i//self.batch_size + 1}/{(len(propositions)//self.batch_size) + 1}")
        
        print(f"Sync of proposition authors completed. {total_authors} relationships processed.")
        return total_authors
    
    async def sync_tramitacoes(self, proposition_ids: Optional[List[int]] = None) -> int:
        """Sync status updates (tramitações) for propositions."""
        return await self.sync_child_entities(
            Proposicao,
            Tramitacao,
            "/proposicoes/{id}/tramitacoes",
            "proposicao_id",
            paginated=False,
            parent_ids_list=proposition_ids
        )
    
    async def sync_related_propositions(self) -> int:
        """Sync related propositions."""
        return await self.sync_child_entities(
            Proposicao,
            Proposicao,
            "/proposicoes/{id}/relacionadas",
            "proposicao_id",
            paginated=False
        )
    
    async def sync_events(self, params: Dict[str, Any] = None, batch_size: int = 50) -> int:
        """Sync events with given parameters."""
        from app.infra.db.models.entidades import Evento
        processed_ids = await self.sync_entity_with_details(Evento, "/eventos", params or {})
        return len(processed_ids)
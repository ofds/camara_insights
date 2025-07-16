"""
Repository layer implementing the Repository pattern for data access.
This provides an abstraction over the database operations, following SOLID principles.
"""

from typing import List, Dict, Any, Type, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import DateTime, Date, desc, asc, func, text
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository class providing common database operations."""
    
    def __init__(self, session: Session, model: Type):
        self.session = session
        self.model = model
        self.pk_name = model.__mapper__.primary_key[0].name
    
    def get_by_id(self, id: Any) -> Optional[Any]:
        """Get a single record by ID."""
        return self.session.get(self.model, id)
    
    def get_all(self, limit: Optional[int] = None) -> List[Any]:
        """Get all records with optional limit."""
        query = select(self.model)
        if limit:
            query = query.limit(limit)
        return self.session.execute(query).scalars().all()
    
    def bulk_upsert(self, data_list: List[Dict[str, Any]]) -> int:
        """Bulk upsert records using PostgreSQL's ON CONFLICT."""
        if not data_list:
            return 0
            
        stmt = insert(self.model).values(data_list)
        update_columns = {
            c.name: getattr(stmt.excluded, c.name) 
            for c in self.model.__table__.columns 
            if c.name != self.pk_name
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=[self.pk_name],
            set_=update_columns
        )
        
        result = self.session.execute(stmt)
        self.session.commit()
        return len(data_list)
    
    def bulk_insert(self, data_list: List[Dict[str, Any]], ignore_conflicts: bool = True) -> int:
        """Bulk insert records."""
        if not data_list:
            return 0
            
        stmt = insert(self.model).values(data_list)
        if ignore_conflicts:
            stmt = stmt.on_conflict_do_nothing()
        
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount
    
    def delete_all(self) -> int:
        """Delete all records from the table."""
        result = self.session.execute(delete(self.model))
        self.session.commit()
        return result.rowcount


class ProposicaoRepository(BaseRepository):
    """Repository for Proposicao entity with specific queries."""
    
    def get_unscored(self, limit: int = 10) -> List[Any]:
        """Get propositions that haven't been scored by AI yet."""
        from app.infra.db.models.ai_data import ProposicaoAIData
        
        query = (
            select(self.model)
            .outerjoin(ProposicaoAIData, self.model.id == ProposicaoAIData.proposicao_id)
            .where(ProposicaoAIData.proposicao_id.is_(None))
            .order_by(desc(self.model.dataApresentacao))\
            .limit(limit)
        )
        return self.session.execute(query).scalars().all()
    
    def get_with_autor_uris(self) -> List[Tuple[int, str]]:
        """Get propositions with their author URIs."""
        query = (
            select(self.model.id, self.model.uriAutores)
            .where(self.model.uriAutores.isnot(None))
        )
        return self.session.execute(query).all()


class AIDataRepository(BaseRepository):
    """Repository for AI analysis data."""
    
    def get_latest_results(self, limit: int = 10) -> List[Tuple[Any, Any]]:
        """Get latest AI analysis results with proposition data."""
        from app.infra.db.models.entidades import Proposicao
        
        query = (
            select(self.model, Proposicao)
            .join(Proposicao, self.model.proposicao_id == Proposicao.id)
            .order_by(self.model.created_at.desc())
            .limit(limit)
        )
        return self.session.execute(query).all()


class ReferenceRepository(BaseRepository):
    """Repository for reference tables."""
    
    def sync_references(self, endpoint: str, data_list: List[Dict[str, Any]]) -> int:
        """Sync reference data with special handling for 'id' to 'cod' conversion."""
        # Generalize the conversion of 'id' to 'cod'
        for item in data_list:
            if 'id' in item and 'cod' not in item:
                item['cod'] = item.pop('id')
            
            # Remove empty 'cod' values for auto-increment
            if item.get('cod') == '':
                del item['cod']
        
        return self.bulk_upsert(data_list)
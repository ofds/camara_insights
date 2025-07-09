# app/infra/db/models/ai_data.py
from sqlalchemy import (Column, Integer, String, Text, Date, DateTime,
                        ForeignKey, JSON, Float)
from sqlalchemy.orm import relationship
from datetime import datetime
from .referencias import Base

class ProposicaoAIData(Base):
    __tablename__ = "proposicao_ai_data"

    id = Column(Integer, primary_key=True, index=True)
    proposicao_id = Column(Integer, ForeignKey("proposicoes.id"), unique=True, nullable=False)
    
    # Classificações diretas do LLM
    summary = Column(Text, nullable=True)
    scope = Column(String, nullable=True)
    magnitude = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    llm_impact_estimate = Column(Integer, nullable=True)
    
    # Nosso score final, calculado
    impact_score = Column(Integer, nullable=True) 
    
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    proposicao = relationship("Proposicao")
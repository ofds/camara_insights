import logging

# camara_insights/app/infra/db/models/referencias.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TiposProposicao(Base):
    __tablename__ = "tipos_proposicao"
    cod = Column(Integer, primary_key=True, index=True)
    sigla = Column(String, index=True)
    nome = Column(String)
    descricao = Column(Text, nullable=True)

class ProposicaoTemas(Base):
    __tablename__ = "proposicao_temas"
    cod = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    descricao = Column(Text, nullable=True)

class ProposicaoSituacoes(Base):
    __tablename__ = "proposicao_situacoes"
    cod = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    descricao = Column(Text, nullable=True)

class TiposTramitacao(Base):
    __tablename__ = "tipos_tramitacao"
    cod = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    descricao = Column(Text, nullable=True)

class TiposAutor(Base):
    __tablename__ = "tipos_autor"
    cod = Column(Integer, primary_key=True, index=True)
    nome = Column(String)

class DeputadoSituacoes(Base):
    __tablename__ = "deputado_situacoes"
    cod = Column(Integer, primary_key=True, index=True)
    nome = Column(String)

class EventoSituacoes(Base):
    __tablename__ = "evento_situacoes"
    cod = Column(Integer, primary_key=True, index=True)
    nome = Column(String)

class TiposEvento(Base):
    __tablename__ = "tipos_evento"
    cod = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    sigla = Column(String, nullable=True)
    descricao = Column(Text, nullable=True)

class TiposOrgao(Base):
    __tablename__ = "tipos_orgao"
    cod = Column(Integer, primary_key=True, index=True)
    sigla = Column(String)
    nome = Column(String)
    descricao = Column(Text, nullable=True)

class UFs(Base):
    __tablename__ = "ufs"
    cod = Column(Integer, primary_key=True, index=True)
    sigla = Column(String, index=True)
    nome = Column(String)
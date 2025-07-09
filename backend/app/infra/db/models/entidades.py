# camara_insights/app/infra/db/models/entidades.py
from sqlalchemy import (Column, Integer, String, Text, Date, DateTime,
                        ForeignKey, JSON)
from sqlalchemy.orm import relationship
from .referencias import Base

class Deputado(Base):
    __tablename__ = "deputados"
    id = Column(Integer, primary_key=True, index=True)
    uri = Column(String, unique=True)
    nomeCivil = Column(String)
    cpf = Column(String(11), index=True, nullable=True)
    sexo = Column(String(1))
    dataNascimento = Column(Date, nullable=True)
    dataFalecimento = Column(Date, nullable=True)
    ufNascimento = Column(String(2), nullable=True)
    municipioNascimento = Column(String, nullable=True)
    escolaridade = Column(String, nullable=True)
    urlWebsite = Column(String, nullable=True)
    redeSocial = Column(JSON, nullable=True)
    # Campos do 'ultimoStatus'
    ultimoStatus_nome = Column(String)
    ultimoStatus_siglaPartido = Column(String)
    ultimoStatus_uriPartido = Column(String, nullable=True)
    ultimoStatus_siglaUf = Column(String)
    ultimoStatus_idLegislatura = Column(Integer)
    ultimoStatus_urlFoto = Column(String)
    ultimoStatus_email = Column(String, nullable=True)
    ultimoStatus_data = Column(Date, nullable=True)
    ultimoStatus_nomeEleitoral = Column(String)
    ultimoStatus_situacao = Column(String, nullable=True)
    ultimoStatus_condicaoEleitoral = Column(String, nullable=True)

class Proposicao(Base):
    __tablename__ = "proposicoes"
    id = Column(Integer, primary_key=True, index=True)
    uri = Column(String, unique=True)
    siglaTipo = Column(String, index=True)
    codTipo = Column(Integer, ForeignKey('tipos_proposicao.cod'))
    numero = Column(Integer, index=True)
    ano = Column(Integer, index=True)
    ementa = Column(Text, nullable=True)
    dataApresentacao = Column(DateTime)
    # Campos do 'statusProposicao'
    statusProposicao_dataHora = Column(DateTime, nullable=True)
    statusProposicao_sequencia = Column(Integer, nullable=True)
    statusProposicao_siglaOrgao = Column(String, nullable=True)
    statusProposicao_uriOrgao = Column(String, nullable=True)
    statusProposicao_descricaoTramitacao = Column(String, nullable=True)
    statusProposicao_codTipoTramitacao = Column(String, nullable=True)
    statusProposicao_descricaoSituacao = Column(String, nullable=True)
    statusProposicao_codSituacao = Column(Integer, nullable=True)
    statusProposicao_despacho = Column(Text, nullable=True)
    statusProposicao_url = Column(String, nullable=True)
    urlInteiroTeor = Column(String, nullable=True)

class Partido(Base):
    __tablename__ = "partidos"
    id = Column(Integer, primary_key=True, index=True)
    sigla = Column(String, index=True)
    nome = Column(String)
    uri = Column(String, unique=True)
    # Campos do 'status'
    status_situacao = Column(String, nullable=True)
    status_totalPosse = Column(Integer, nullable=True)
    status_totalMembros = Column(Integer, nullable=True)
    status_uriMembros = Column(String, nullable=True)
    status_lider_nome = Column(String, nullable=True)
    numeroEleitoral = Column(Integer, nullable=True)
    urlLogo = Column(String, nullable=True)

class Orgao(Base):
    __tablename__ = "orgaos"
    id = Column(Integer, primary_key=True, index=True)
    uri = Column(String, unique=True)
    sigla = Column(String, index=True)
    nome = Column(String)
    apelido = Column(String)
    codTipoOrgao = Column(Integer, ForeignKey('tipos_orgao.cod'))
    tipoOrgao = Column(String)
    nomePublicacao = Column(String)
    dataInicio = Column(Date, nullable=True)
    dataFim = Column(Date, nullable=True)

class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, index=True)
    uri = Column(String, unique=True)
    dataHoraInicio = Column(DateTime)
    dataHoraFim = Column(DateTime, nullable=True)
    situacao = Column(String)
    descricaoTipo = Column(String)
    descricao = Column(Text, nullable=True)
    localExterno = Column(String, nullable=True)
    localCamara_nome = Column(String, nullable=True)

class Votacao(Base):
    __tablename__ = "votacoes"
    id = Column(String, primary_key=True, index=True)
    uri = Column(String, unique=True)
    data = Column(Date)
    dataHoraRegistro = Column(DateTime)
    siglaOrgao = Column(String)
    uriOrgao = Column(String)
    uriEvento = Column(String, nullable=True)
    descricao = Column(Text, nullable=True)
    aprovacao = Column(Integer, nullable=True)
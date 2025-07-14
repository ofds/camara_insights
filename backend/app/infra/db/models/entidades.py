# camara_insights/app/infra/db/models/entidades.py
from sqlalchemy import (Column, Integer, String, Text, Date, DateTime,
                        ForeignKey, JSON, Float, Table)
from sqlalchemy.orm import relationship
from .referencias import Base

proposicao_autores = Table('proposicao_autores', Base.metadata,
    Column('proposicao_id', Integer, ForeignKey('proposicoes.id'), primary_key=True),
    Column('deputado_id', Integer, ForeignKey('deputados.id'), primary_key=True)
)

evento_deputados = Table('evento_deputados', Base.metadata,
    Column('evento_id', Integer, ForeignKey('eventos.id'), primary_key=True),
    Column('deputado_id', Integer, ForeignKey('deputados.id'), primary_key=True)
)

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

    partido_id = Column(Integer, ForeignKey('partidos.id'))
    partido = relationship("Partido")

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
    uriOrgaoNumerador = Column(String, nullable=True)
    uriAutores = Column(String, nullable=True)
    descricaoTipo = Column(String, nullable=True)
    ementaDetalhada = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    uriPropPrincipal = Column(String, nullable=True)
    uriPropAnterior = Column(String, nullable=True)
    uriPropPosterior = Column(String, nullable=True)
    urlInteiroTeor = Column(String, nullable=True)
    urnFinal = Column(String, nullable=True)
    texto = Column(Text, nullable=True)
    justificativa = Column(Text, nullable=True)
    
    # Campos do 'statusProposicao'
    statusProposicao_dataHora = Column(DateTime, nullable=True)
    statusProposicao_sequencia = Column(Integer, nullable=True)
    statusProposicao_siglaOrgao = Column(String, nullable=True)
    statusProposicao_uriOrgao = Column(String, nullable=True)
    statusProposicao_uriUltimoRelator = Column(String, nullable=True)
    statusProposicao_regime = Column(String, nullable=True)
    statusProposicao_descricaoTramitacao = Column(String, nullable=True)
    statusProposicao_codTipoTramitacao = Column(String, nullable=True)
    statusProposicao_descricaoSituacao = Column(String, nullable=True)
    statusProposicao_codSituacao = Column(Integer, nullable=True)
    statusProposicao_despacho = Column(Text, nullable=True)
    statusProposicao_url = Column(String, nullable=True)
    statusProposicao_ambito = Column(String, nullable=True)
    statusProposicao_apreciacao = Column(String, nullable=True)

    autores = relationship("Deputado", secondary=proposicao_autores, backref="proposicoes_autoradas")
    votacoes = relationship("Votacao", back_populates="proposicao")
    

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

    participantes = relationship("Deputado", secondary=evento_deputados, backref="eventos_participados")

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
    proposicao_id = Column(Integer, ForeignKey('proposicoes.id'), nullable=True, index=True)

    # Adicione o back_populates para completar o relacionamento
    proposicao = relationship("Proposicao", back_populates="votacoes")


class Despesa(Base):
    __tablename__ = "despesas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    deputado_id = Column(Integer, ForeignKey('deputados.id'), index=True)
    ano = Column(Integer, index=True)
    mes = Column(Integer, index=True)
    tipoDespesa = Column(String)
    dataDocumento = Column(Date, nullable=True)
    valorDocumento = Column(Float)
    valorLiquido = Column(Float)
    nomeFornecedor = Column(String)
    cnpjCpfFornecedor = Column(String, index=True)
    urlDocumento = Column(String, nullable=True)

    deputado = relationship("Deputado")

class Discurso(Base):
    __tablename__ = "discursos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    deputado_id = Column(Integer, ForeignKey('deputados.id'), index=True)
    dataHoraInicio = Column(DateTime)
    siglaTipoDiscurso = Column(String)
    keywords = Column(Text, nullable=True)
    sumario = Column(Text, nullable=True)

    deputado = relationship("Deputado")

class Voto(Base):
    __tablename__ = "votos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    votacao_id = Column(String, ForeignKey('votacoes.id'), index=True)
    deputado_id = Column(Integer, ForeignKey('deputados.id'), index=True)
    voto = Column(String) # Ex: 'Sim', 'Não', 'Abstenção'
    
    votacao = relationship("Votacao")
    deputado = relationship("Deputado")

class Tramitacao(Base):
    __tablename__ = "tramitacoes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    proposicao_id = Column(Integer, ForeignKey('proposicoes.id'), index=True)
    dataHora = Column(DateTime)
    sequencia = Column(Integer)
    siglaOrgao = Column(String)
    descricaoTramitacao = Column(String)
    despacho = Column(Text)

    proposicao = relationship("Proposicao")
    
class Frente(Base):
    __tablename__ = "frentes"
    id = Column(Integer, primary_key=True)
    uri = Column(String, unique=True, index=True)
    titulo = Column(String)
    idLegislatura = Column(Integer)

class Bloco(Base):
    __tablename__ = "blocos"
    id = Column(String, primary_key=True)
    nome = Column(String)
    idLegislatura = Column(Integer)

class Grupo(Base):
    __tablename__ = "grupos"
    id = Column(Integer, primary_key=True)
    uri = Column(String, unique=True, index=True)
    nome = Column(String)
    sigla = Column(String, nullable=True)
    dataInicio = Column(Date, nullable=True)
    dataFim = Column(Date, nullable=True)
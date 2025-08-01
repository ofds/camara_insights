import logging

# backend/app/domain/entidades.py

from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime

# Schema simplificado para a lista de deputados
class DeputadoSchema(BaseModel):
    id: int
    nomeCivil: Optional[str] = None
    sexo: Optional[str] = None  # Added
    ultimoStatus_nome: Optional[str] = None
    ultimoStatus_siglaPartido: Optional[str] = None
    ultimoStatus_siglaUf: Optional[str] = None
    ultimoStatus_urlFoto: Optional[str] = None
    ultimoStatus_email: Optional[str] = None
    ultimoStatus_situacao: Optional[str] = None # Added

    class Config:
        from_attributes = True

# Schema detalhado para a página de um deputado específico
class DeputadoSchemaDetalhado(DeputadoSchema):
    uri: Optional[str] = None
    cpf: Optional[str] = None
    dataNascimento: Optional[date] = None
    dataFalecimento: Optional[date] = None
    ufNascimento: Optional[str] = None
    municipioNascimento: Optional[str] = None
    escolaridade: Optional[str] = None
    urlWebsite: Optional[str] = None
    redeSocial: Optional[List[str]] = None
    
    # Campos aninhados de 'ultimoStatus'
    ultimoStatus_id: Optional[int] = None
    ultimoStatus_uri: Optional[str] = None
    ultimoStatus_uriPartido: Optional[str] = None
    ultimoStatus_idLegislatura: Optional[int] = None
    ultimoStatus_data: Optional[date] = None
    ultimoStatus_nomeEleitoral: Optional[str] = None
    ultimoStatus_gabinete_nome: Optional[str] = None
    ultimoStatus_gabinete_predio: Optional[str] = None
    ultimoStatus_gabinete_sala: Optional[str] = None
    ultimoStatus_gabinete_andar: Optional[str] = None
    ultimoStatus_gabinete_telefone: Optional[str] = None
    ultimoStatus_gabinete_email: Optional[str] = None
    # ultimoStatus_situacao is already in the base schema
    ultimoStatus_condicaoEleitoral: Optional[str] = None
    ultimoStatus_descricaoStatus: Optional[str] = None

    class Config:
        from_attributes = True

    @field_validator('redeSocial', mode='before')
    @classmethod
    def empty_list_to_none(cls, v):
        if isinstance(v, list) and not v:
            return None
        return v
class ProposicaoSchema(BaseModel):
    id: int
    siglaTipo: Optional[str] = None
    numero: Optional[int] = None
    ano: Optional[int] = None
    ementa: Optional[str] = None
    dataApresentacao: Optional[datetime] = None
    statusProposicao_descricaoSituacao: Optional[str] = None
    statusProposicao_descricaoTramitacao: Optional[str] = None
    impact_score: Optional[int] = None
    summary: Optional[str] = None
    scope: Optional[str] = None
    magnitude: Optional[str] = None
    tags: Optional[List[str]] = None
    urlInteiroTeor: Optional[str] = None
    uriAutores: Optional[str] = None
    descricaoTipo: Optional[str] = None
    ementaDetalhada: Optional[str] = None
    keywords: Optional[str] = None
    autor: Optional[str] = None

    class Config:
        from_attributes = True

class PartidoSchema(BaseModel):
    id: int
    sigla: Optional[str] = None
    nome: Optional[str] = None
    status_lider_nome: Optional[str] = None
    status_totalMembros: Optional[int] = None
    urlLogo: Optional[str] = None

    class Config:
        from_attributes = True

class OrgaoSchema(BaseModel):
    id: int
    sigla: Optional[str] = None
    nome: Optional[str] = None
    apelido: Optional[str] = None
    tipoOrgao: Optional[str] = None

    class Config:
        from_attributes = True

class EventoSchema(BaseModel):
    id: int
    dataHoraInicio: Optional[datetime] = None
    dataHoraFim: Optional[datetime] = None
    situacao: Optional[str] = None
    descricaoTipo: Optional[str] = None
    descricao: Optional[str] = None
    localCamara_nome: Optional[str] = None

    class Config:
        from_attributes = True

class VotacaoSchema(BaseModel):
    id: str
    data: Optional[date] = None
    dataHoraRegistro: Optional[datetime] = None
    siglaOrgao: Optional[str] = None
    descricao: Optional[str] = None

    class Config:
        from_attributes = True

# --- Novos Schemas ---

class DespesaSchema(BaseModel):
    id: int
    deputado_id: int
    ano: Optional[int] = None
    mes: Optional[int] = None
    tipoDespesa: Optional[str] = None
    dataDocumento: Optional[date] = None
    valorLiquido: Optional[float] = None
    nomeFornecedor: Optional[str] = None
    urlDocumento: Optional[str] = None

    class Config:
        from_attributes = True

class DiscursoSchema(BaseModel):
    id: int
    deputado_id: int
    dataHoraInicio: Optional[datetime] = None
    siglaTipoDiscurso: Optional[str] = None
    keywords: Optional[str] = None
    sumario: Optional[str] = None

    class Config:
        from_attributes = True

class VotoSchema(BaseModel):
    id: int
    votacao_id: str
    deputado_id: int
    voto: Optional[str] = None
    # Opcional: Adicionar um schema simplificado do deputado para mostrar nome/partido
    # deputado: Optional[DeputadoSchema] = None

    class Config:
        from_attributes = True

class TramitacaoSchema(BaseModel):
    id: int
    proposicao_id: int
    dataHora: Optional[datetime] = None
    sequencia: Optional[int] = None
    siglaOrgao: Optional[str] = None
    descricaoTramitacao: Optional[str] = None
    despacho: Optional[str] = None

    class Config:
        from_attributes = True

class FrenteSchema(BaseModel):
    id: int
    titulo: Optional[str] = None
    idLegislatura: Optional[int] = None

    class Config:
        from_attributes = True

class BlocoSchema(BaseModel):
    id: str
    nome: Optional[str] = None
    idLegislatura: Optional[int] = None

    class Config:
        from_attributes = True

class GrupoSchema(BaseModel):
    id: int
    nome: Optional[str] = None
    sigla: Optional[str] = None
    dataInicio: Optional[date] = None
    dataFim: Optional[date] = None

    class Config:
        from_attributes = True


class ProposicaoPaginatedResponse(BaseModel):
    proposicoes: List[ProposicaoSchema]
    total_count: int

class DeputadoRankingSchema(DeputadoSchema):
    total_impacto: float
    total_propostas: int

class ProposicaoPaginatedResponse(BaseModel):
    proposicoes: List[ProposicaoSchema]
    total: int
    limit: int
    skip: int

class ProposicaoImpactoAvgSchema(BaseModel):
    period: str
    average_impact: float
    start_date: date
    end_date: date

class DeputadoImpactoAvgSchema(BaseModel):
    period: str
    average_impact: float
    start_date: date
    end_date: date

class PropostaActivitySchema(BaseModel):
    activity: List[datetime]

class HealthCheckResponse(BaseModel):
    api_status: str
    db_status: str
    camara_api_status: str
    openrouter_api_status: str
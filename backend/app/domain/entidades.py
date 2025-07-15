# camara_insights/app/domain/entidades.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

# --- Schemas Existentes ---

class DeputadoSchema(BaseModel):
    id: int
    nomeCivil: Optional[str] = None
    ultimoStatus_nome: Optional[str] = None
    ultimoStatus_siglaPartido: Optional[str] = None
    ultimoStatus_siglaUf: Optional[str] = None
    ultimoStatus_urlFoto: Optional[str] = None
    ultimoStatus_email: Optional[str] = None
    
    class Config:
        from_attributes = True

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
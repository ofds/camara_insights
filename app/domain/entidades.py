# camara_insights/app/domain/entidades.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class DeputadoSchema(BaseModel):
    id: int
    # --- INÍCIO DA CORREÇÃO ---
    # Marcamos os campos que podem ser nulos no banco de dados como Opcionais.
    nomeCivil: Optional[str] = None
    ultimoStatus_nome: Optional[str] = None
    ultimoStatus_siglaPartido: Optional[str] = None
    ultimoStatus_siglaUf: Optional[str] = None
    ultimoStatus_urlFoto: Optional[str] = None
    ultimoStatus_email: Optional[str] = None
    # --- FIM DA CORREÇÃO ---

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
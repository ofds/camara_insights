// src/types/deputado.ts

export interface ApiRankedDeputy {
  id: number;
  nomeCivil: string;
  ultimoStatus_nome: string;
  ultimoStatus_siglaPartido: string;
  ultimoStatus_siglaUf: string;
  ultimoStatus_urlFoto: string;
  ultimoStatus_email: string | null;
  total_impacto: number;
}
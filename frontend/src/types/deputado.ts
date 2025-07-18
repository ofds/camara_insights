// src/types/deputado.ts

// This type likely already exists and is used by the ranking component
export interface ApiRankedDeputy {
  id: number;
  nome: string;
  sigla_partido: string;
  sigla_uf: string;
  url_foto: string;
  total_impacto: number;
  total_propostas: number;
}

// NEW: Simplified type for the main deputies table
export interface Deputado {
  id: number;
  nomeCivil: string | null;
  sexo: string | null;
  ultimoStatus_nome: string | null;
  ultimoStatus_siglaPartido: string | null;
  ultimoStatus_siglaUf: string | null;
  ultimoStatus_urlFoto: string | null;
  ultimoStatus_email: string | null;
  ultimoStatus_situacao: string | null;
}

// NEW: Type for propositions, used in the detailed view
export interface Proposicao {
    id: number;
    siglaTipo: string;
    numero: number;
    ano: number;
    ementa: string | null;
}

// NEW: Detailed type for the individual deputy page
export interface DeputadoDetalhado extends Deputado {
  uri: string | null;
  cpf: string | null;
  dataNascimento: string | null; // Dates are transmitted as strings in JSON
  dataFalecimento: string | null;
  ufNascimento: string | null;
  municipioNascimento: string | null;
  escolaridade: string | null;
  urlWebsite: string | null;
  redeSocial: Record<string, any> | null;
  ultimoStatus_id: number | null;
  ultimoStatus_uri: string | null;
  ultimoStatus_uriPartido: string | null;
  ultimoStatus_idLegislatura: number | null;
  ultimoStatus_data: string | null;
  ultimoStatus_nomeEleitoral: string | null;
  ultimoStatus_gabinete_nome: string | null;
  ultimoStatus_gabinete_predio: string | null;
  ultimoStatus_gabinete_sala: string | null;
  ultimoStatus_gabinete_andar: string | null;
  ultimoStatus_gabinete_telefone: string | null;
  ultimoStatus_gabinete_email: string | null;
  ultimoStatus_condicaoEleitoral: string | null;
  ultimoStatus_descricaoStatus: string | null;
  proposicoes?: Proposicao[];
}
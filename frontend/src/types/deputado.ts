// src/types/deputado.ts

export interface ApiRankedDeputy {
  id: number;
  nome: string;
  sigla_partido: string | null;
  sigla_uf: string | null;
  url_foto: string | null;
  total_impacto: number;
}
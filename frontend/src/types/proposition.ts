// frontend/src/types/proposition.ts

/**
 * Represents the data structure for a proposal as displayed in the main table.
 */
export interface Proposal {
  id: string;
  title: string;
  status: string;
  author: string;
  createdAt: Date;
  siglaTipo: string;
  numero: number;
  ano: number;
  impact_score: number;
}

/**
 * Represents the full data structure for a proposal received from the backend API.
 */
export interface ApiProposal {
  id: number;
  siglaTipo: string;
  numero: number;
  ano: number;
  ementa: string;
  dataApresentacao: string;
  statusProposicao_descricaoSituacao: string;
  statusProposicao_descricaoTramitacao: string;
  impact_score: number;
  summary: string | null;
  scope: string | null;
  magnitude: string | null;
  tags: string[] | null;
}

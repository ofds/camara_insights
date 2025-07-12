// frontend/src/services/proposicoes.service.ts

import type { ApiProposal } from '@/types/proposition';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

// --- Nova Interface para os Detalhes Completos ---
// Esta interface corresponde à estrutura de resposta do nosso novo endpoint /details.
export interface ProposalDetails {
  base_data: ApiProposal;
  autores: any[]; // Estes tipos podem ser refinados mais tarde se necessário
  relacionadas: any[];
  temas: any[];
  tramitacoes: any[];
  votacoes: any[];
}


/**
 * Fetches a list of propositions from the backend API with support for pagination, sorting, and dynamic filters.
 * @param params - The query parameters for the request.
 * @param params.limit - The number of records to return.
 * @param params.skip - The number of records to skip.
 * @param params.sort - The sorting order for the results.
 * @param params.filters - The dynamic filters to apply.
 * @returns A promise that resolves to an array of proposals.
 */
export async function getPropositions({
  limit,
  skip,
  sort,
  filters,
}: {
  limit: number;
  skip: number;
  sort: string;
  filters: { [key: string]: string | number };
}): Promise<ApiProposal[]> {
  const params = new URLSearchParams();
  params.append('limit', String(limit));
  params.append('skip', String(skip));
  if (sort) {
    params.append('sort', sort);
  }

  for (const key in filters) {
    if (Object.prototype.hasOwnProperty.call(filters, key)) {
      params.append(key, String(filters[key]));
    }
  }

  const response = await fetch(`${API_BASE_URL}/proposicoes?${params.toString()}`);

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  const data = await response.json();
  return data;
}


export const getHighImpactPropositions = async (filters: { [key: string]: string | number } = {}): Promise<ApiProposal[]> => {
  return getPropositions({
    limit: 5,
    sort: 'impact_score:desc',
    skip: 0,
    filters,
  });
};

/**
 * Fetches a single proposal by its ID from the backend API.
 * @param id - The ID of the proposal.
 * @returns A promise that resolves to the proposal data.
 */
export async function getPropositionById(id: number): Promise<ApiProposal> {
  const response = await fetch(`${API_BASE_URL}/proposicoes/${id}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Proposição não encontrada');
    }
    throw new Error('Falha na resposta da rede');
  }

  const data = await response.json();
  return data;
}

/**
 * --- NOVA FUNÇÃO ---
 * Busca os detalhes completos de uma proposição, incluindo dados da API da Câmara.
 * @param id - O ID da proposição.
 * @returns Uma promessa que resolve para os detalhes completos da proposição.
 */
export async function getPropositionDetailsById(id: number): Promise<ProposalDetails> {
  // Note que estamos chamando o novo endpoint que termina em /details
  const response = await fetch(`${API_BASE_URL}/proposicoes/${id}/details`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Proposição não encontrada');
    }
    throw new Error('Falha na resposta da rede ao buscar detalhes');
  }

  const data = await response.json();
  return data;
}
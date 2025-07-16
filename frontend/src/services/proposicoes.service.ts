// frontend/src/services/proposicoes.service.ts

import type { ApiProposal as ApiProposition } from '@/types/proposition'; // Renamed for clarity

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

// --- Interfaces ---
export interface ProposalDetails {
  base_data: ApiProposition;
  autores: any[]; 
  relacionadas: any[];
  temas: any[];
  tramitacoes: any[];
  votacoes: any[];
}

export interface PaginatedProposals {
  proposicoes: ApiProposition[];
  total: number;
}

// --- NEW FUNCTION ---
/**
 * Fetches ranked propositions based on a period (daily or monthly).
 * @param period - The time period for the ranking ('daily' | 'monthly').
 * @returns A promise that resolves to an array of ApiProposition.
 */
export async function getRankedPropositions(period: 'daily' | 'monthly'): Promise<ApiProposition[]> {
    const params = new URLSearchParams({ period });
    const response = await fetch(`${API_BASE_URL}/proposicoes/ranking?${params.toString()}`);

    if (!response.ok) {
        throw new Error(`Failed to fetch ranked propositions for period: ${period}`);
    }
    return response.json();
}

// --- EXISTING FUNCTIONS (Unchanged) ---

export async function getPropositions({
  limit,
  skip,
  sort,
  filters,
}: {
  limit: number;
  skip: number;
  sort: string;
  filters: { [key: string]: string | number | boolean };
}): Promise<PaginatedProposals> {
  const params = new URLSearchParams();
  params.append('limit', String(limit));
  params.append('skip', String(skip));
  if (sort) {
    params.append('sort', sort);
  }

  for (const key in filters) {
    if (Object.prototype.hasOwnProperty.call(filters, key)) {
      const value = filters[key];
      if (typeof value === 'boolean') {
        if (value) {
          params.append(key, String(value));
        }
      } else {
        params.append(key, String(value));
      }
    }
  }

  const response = await fetch(`${API_BASE_URL}/proposicoes?${params.toString()}`);

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  const data: PaginatedProposals = await response.json();
  return data;
}

export async function getPropositionById(id: number): Promise<ApiProposition> {
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

export async function getPropositionDetailsById(id: number): Promise<ProposalDetails> {
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
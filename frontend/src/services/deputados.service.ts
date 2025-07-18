// src/services/deputados.service.ts

import { type ApiRankedDeputy, type Deputado, type DeputadoDetalhado, type PropostaActivity } from '@/types/deputado';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Fetches ranked deputies from the API.
 * The backend query returns a list of deputy objects,
 * so we process it to match the expected schema for the frontend.
 * @returns A promise that resolves to an array of ApiRankedDeputy.
 */
export async function getRankedDeputies(): Promise<ApiRankedDeputy[]> {
  const response = await fetch(`${API_BASE_URL}/deputados/ranking`);

  if (!response.ok) {
    throw new Error("Não foi possível buscar o ranking de deputados.");
  }

  const data = await response.json();

  // The backend returns a list of objects with a different shape than
  // what the application's components expect. We map the API response
  // to the ApiRankedDeputy type here.
  return data.map((apiDeputy: any) => {
    return {
      id: apiDeputy.id,
      nome: apiDeputy.ultimoStatus_nome,
      sigla_partido: apiDeputy.ultimoStatus_siglaPartido,
      sigla_uf: apiDeputy.ultimoStatus_siglaUf,
      url_foto: apiDeputy.ultimoStatus_urlFoto,
      total_impacto: apiDeputy.total_impacto,
      total_propostas: apiDeputy.total_propostas || 0, // Ensure total_propostas is defined
    };
  });
}

/**
 * Fetches a paginated, filterable, and sortable list of deputies.
 * @param params - The query parameters for the request.
 * @returns A promise that resolves to an object containing the list of deputies and the total count.
 */
export async function getDeputados(params: {
  skip: number;
  limit: number;
  sort?: string;
  filters?: Record<string, string | undefined>;
}): Promise<{ data: Deputado[]; total: number }> {
  const urlParams = new URLSearchParams({
    skip: String(params.skip),
    limit: String(params.limit),
  });

  if (params.sort) {
    urlParams.append('sort', params.sort);
  }

  if (params.filters) {
    for (const key in params.filters) {
      if (Object.prototype.hasOwnProperty.call(params.filters, key)) {
        const value = params.filters[key];
        // Ensure we only append parameters that have a defined, non-empty value
        if (value) {
          urlParams.append(key, value);
        }
      }
    }
  }

  const response = await fetch(`${API_BASE_URL}/deputados?${urlParams.toString()}`);

  if (!response.ok) {
    throw new Error('Não foi possível buscar os deputados.');
  }

  // NOTE: This assumes the backend API returns the total number of items
  // in a custom 'X-Total-Count' header for pagination to work correctly.
  // A change may be required in your backend to add this header.
  const total = parseInt(response.headers.get('X-Total-Count') || '0', 10);
  const data: Deputado[] = await response.json();

  return { data, total };
}

/**
 * Fetches the detailed information for a single deputy by their ID.
 * @param id - The ID of the deputy to fetch.
 * @returns A promise that resolves to the detailed deputy object.
 */
export async function getDeputadoById(id: number): Promise<DeputadoDetalhado> {
  const response = await fetch(`${API_BASE_URL}/deputados/${id}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Deputado não encontrado.');
    }
    throw new Error('Não foi possível buscar os detalhes do deputado.');
  }

  return response.json();
}

/**
 * Fetches the proposal presentation activity for a single deputy by their ID.
 * @param id - The ID of the deputy.
 * @returns A promise that resolves to the proposal activity data.
 */
export async function getDeputadoProposalActivity(id: number): Promise<PropostaActivity> {
  const response = await fetch(`${API_BASE_URL}/deputados/${id}/activity/proposals`);

  if (!response.ok) {
    if (response.status === 404) {
      // Return an empty activity list if no data is found, which is an expected case.
      return { activity: [] };
    }
    throw new Error("Não foi possível buscar os dados de atividade de propostas.");
  }

  return response.json();
}
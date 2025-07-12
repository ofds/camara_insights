// src/services/proposicoes.service.ts

export interface ApiProposition {
  id: number;
  siglaTipo: string;
  numero: number;
  ano: number;
  ementa: string;
  dataApresentacao: string; // Corrected from data_apresentacao
  statusProposicao_descricaoSituacao: string;
  statusProposicao_descricaoTramitacao: string;
  impact_score: number | null;
  summary: string | null;
  scope: string | null;
  magnitude: string | null;
  tags: string[] | null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Busca as 5 proposições com maior pontuação de impacto.
 * @returns Uma promessa que resolve para um array de proposições.
 */
interface GetPropositionsParams {
  limit?: number;
  skip?: number;
  sort?: string;
  filters?: { [key: string]: string | number };
}

/**
 * Busca proposições da API com filtros, ordenação e paginação dinâmicos.
 * @param params - Objeto com parâmetros para a query (limit, skip, sort, filters).
 * @returns Uma promessa que resolve para um array de proposições.
 */
export const getPropositions = async (params: GetPropositionsParams = {}): Promise<ApiProposition[]> => {
  const { limit = 10, skip = 0, sort, filters = {} } = params;

  // URLSearchParams gerencia a codificação dos parâmetros da URL de forma segura
  const queryParams = new URLSearchParams({
    limit: String(limit),
    skip: String(skip),
  });

  if (sort) {
    queryParams.append('sort', sort);
  }

  // Adiciona os filtros dinâmicos
  for (const key in filters) {
    if (Object.prototype.hasOwnProperty.call(filters, key)) {
      queryParams.append(key, String(filters[key]));
    }
  }

  try {
    const response = await fetch(`${API_BASE_URL}/proposicoes?${queryParams.toString()}`);

    if (!response.ok) {
      throw new Error(`Erro na API: ${response.statusText}`);
    }

    const data: ApiProposition[] = await response.json();
    return data;

  } catch (error) {
    console.error("Falha ao buscar proposições:", error);
    return [];
  }
};

/**
 * Busca as 5 proposições com maior pontuação de impacto. (Mantido para retrocompatibilidade)
 * Esta função agora pode usar a nova função genérica.
 * @returns Uma promessa que resolve para um array de proposições.
 */
export const getHighImpactPropositions = async (): Promise<ApiProposition[]> => {
  return getPropositions({
    limit: 5,
    sort: 'impact_score:desc',
  });
};
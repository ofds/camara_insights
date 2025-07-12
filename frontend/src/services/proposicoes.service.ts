// src/services/proposicoes.service.ts

// Interface que define a estrutura de uma proposição vinda da API
export interface ApiProposition {
  id: number;
  sigla_tipo: string;
  numero: number;
  ano: number;
  ementa: string; // Esta é a descrição/resumo
  data_apresentacao: string;
  impact_score: number | null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Busca as 5 proposições com maior pontuação de impacto.
 * @returns Uma promessa que resolve para um array de proposições.
 */
export const getHighImpactPropositions = async (): Promise<ApiProposition[]> => {
  try {
    // URL corrigida para usar 'sort=impact_score:desc'
    const response = await fetch(`${API_BASE_URL}/proposicoes?sort=impact_score:desc&limit=5`);

    if (!response.ok) {
      throw new Error(`Erro na API: ${response.statusText}`);
    }

    const data: ApiProposition[] = await response.json();
    return data;

  } catch (error) {
    console.error("Falha ao buscar proposições de alto impacto:", error);
    return [];
  }
};
// src/services/eventos.service.ts

// 1. Interface atualizada para corresponder 100% à API
export interface ApiEvent {
  id: number;
  dataHoraInicio: string; // <-- Nome corrigido e é uma string
  dataHoraFim: string | null;
  situacao: string;
  descricaoTipo: string;
  descricao: string;
  localCamara_nome: string | null;
}

const API_BASE_URL =  'http://localhost:8000/api/v1';

/**
 * Busca a lista de eventos da Câmara na API.
 * @returns Uma promessa que resolve para um array de eventos.
 */
export const getEventosDaSemana = async (): Promise<ApiEvent[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/eventos`);

    if (!response.ok) {
      throw new Error(`Erro na API: ${response.statusText}`);
    }

    const data: ApiEvent[] = await response.json();
    return data;

  } catch (error) {
    console.error("Falha ao buscar eventos:", error);
    return [];
  }
};
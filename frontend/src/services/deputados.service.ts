// src/services/deputados.service.ts

import { type ApiRankedDeputy } from '@/types/deputado';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Fetches ranked deputies from the API.
 * The backend query returns a list of tuples [Deputado, total_impacto], 
 * so we process it to match the expected schema.
 * @returns A promise that resolves to an array of ApiRankedDeputy.
 */
export async function getRankedDeputies(): Promise<ApiRankedDeputy[]> {
  const response = await fetch(`${API_BASE_URL}/deputados/ranking`);

  if (!response.ok) {
    throw new Error("Não foi possível buscar o ranking de deputados.");
  }

  const data = await response.json();

  // The backend returns a list of tuples: [deputyObject, totalImpact].
  // We map this to a clean array of objects.
  return data.map((item: [any, number]) => {
    const deputy = item[0];
    const total_impacto = item.total_impacto; // Access the named total_impacto field

    return {
      ...deputy,
      total_impacto: total_impacto
    };
  });
}
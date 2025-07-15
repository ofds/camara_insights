// src/services/deputados.service.ts

import { type ApiRankedDeputy } from '@/types/deputado';

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
    };
  });
}
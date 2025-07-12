// frontend/src/services/proposicoes.service.ts

import type { ApiProposal } from '@/types/proposition';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';


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


export const getHighImpactPropositions = async (): Promise<ApiProposal[]> => {
  return getPropositions({
    limit: 5,
    sort: 'impact_score:desc',
    skip: 0,
  });
};
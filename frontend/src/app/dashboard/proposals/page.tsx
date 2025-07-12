// frontend/src/app/dashboard/proposals/page.tsx

'use client';

import * as React from 'react';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { useCallback, useEffect, useState } from 'react';

import { ProposalsFilters } from '@/components/dashboard/proposal/proposals-filters';
import { ProposalsTable } from '@/components/dashboard/proposal/proposals-table';
import { getPropositions } from '@/services/proposicoes.service';
import type { ApiProposal, Proposal } from '@/types/proposition';

export default function Page(): React.JSX.Element {
  const [rawProposals, setRawProposals] = useState<ApiProposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [filters, setFilters] = useState<{ [key: string]: string | number }>({});
  const [sort, setSort] = useState<{ property: string; order: 'asc' | 'desc' }>({
    property: 'dataApresentacao',
    order: 'desc',
  });

  const fetchProposals = useCallback(async () => {
    try {
      setLoading(true);
      const sortString = `${sort.property}:${sort.order}`;
      const response = await getPropositions({
        limit: rowsPerPage,
        skip: page * rowsPerPage,
        sort: sortString,
        filters,
      });

      setRawProposals(response);
      setTotalCount(100); // Using a placeholder for total count as the API doesn't provide it
      setError(null);
    } catch (error_) {
      setError('Falha ao carregar as propostas');
      console.error(error_);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, sort, filters]);

  useEffect(() => {
    fetchProposals();
  }, [fetchProposals]);

  const displayRows = React.useMemo((): Proposal[] => {
    return rawProposals.map((prop) => ({
      id: prop.id.toString(),
      title: prop.ementa,
      status: prop.statusProposicao_descricaoSituacao || 'Em análise',
      author: 'Autor desconhecido', // Temporarily hardcoded
      createdAt: new Date(prop.dataApresentacao),
      siglaTipo: prop.siglaTipo,
      numero: prop.numero,
      ano: prop.ano,
      impact_score: prop.impact_score,
    }));
  }, [rawProposals]);

  const handlePageChange = (event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(Number.parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSort = (property: string) => {
    const isAsc = sort.property === property && sort.order === 'asc';
    setSort({ property, order: isAsc ? 'desc' : 'asc' });
  };

  const handleFilterChange = (newFilters: { [key: string]: string | number }) => {
    setFilters(newFilters);
  };

  return (
    <Stack spacing={2}>
      <Stack direction="row" spacing={3}>
        <Stack spacing={1} sx={{ flex: '1 1 auto' }}>
          <Typography variant="h5">Propostas</Typography>
          {error && <Typography color="error">{error}</Typography>}
        </Stack>
      </Stack>
      <ProposalsFilters onFilterChange={handleFilterChange} />
      <ProposalsTable
        count={totalCount}
        page={page}
        rows={displayRows}
        rawRows={rawProposals}
        rowsPerPage={rowsPerPage}
        onPageChange={handlePageChange}
        onRowsPerPageChange={handleRowsPerPageChange}
        onSort={handleSort}
        order={sort.order}
        orderBy={sort.property}
        loading={loading}
      />
    </Stack>
  );
}

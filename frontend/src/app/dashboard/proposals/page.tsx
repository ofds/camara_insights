'use client';

import * as React from 'react';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { PlusIcon } from '@phosphor-icons/react/dist/ssr/Plus';
import { useCallback, useEffect, useState } from 'react';
import { ProposalsTable } from '@/components/dashboard/proposal/proposals-table';
import type { Proposal } from '@/types/proposition';
import { getPropositions } from '@/services/proposicoes.service';

export default function Page(): React.JSX.Element {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  const fetchProposals = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getPropositions({
        limit: rowsPerPage,
        skip: page * rowsPerPage,
        sort: 'dataApresentacao:desc'
      });
      
      setProposals(response.map((prop) => ({
        id: prop.id.toString(),
        title: prop.ementa,
        status: prop.statusProposicao_descricaoSituacao || 'Em análise',
        author: 'Autor desconhecido', // Temporarily hardcoded until backend provides author info
        createdAt: new Date(prop.dataApresentacao)
      })));
      
      // Note: The API currently doesn't return total count
      // We'll use a placeholder value for now
      setTotalCount(100);
      setError(null);
    } catch (error_) {
      setError('Falha ao carregar as propostas');
      console.error(error_);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage]);

  useEffect(() => {
    fetchProposals();
  }, [fetchProposals]);

  const handlePageChange = (event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(Number.parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Stack spacing={3}>
      <Stack direction="row" spacing={3}>
        <Stack spacing={1} sx={{ flex: '1 1 auto' }}>
          <Typography variant="h4">Propostas</Typography>
          {error && <Typography color="error">{error}</Typography>}
        </Stack>
        <div>
          <Button startIcon={<PlusIcon fontSize="var(--icon-fontSize-md)" />} variant="contained">
            Adicionar
          </Button>
        </div>
      </Stack>
      <ProposalsTable
        count={totalCount}
        page={page}
        rows={proposals}
        rowsPerPage={rowsPerPage}
        onPageChange={handlePageChange}
        onRowsPerPageChange={handleRowsPerPageChange}
        loading={loading}
      />
    </Stack>
  );
}
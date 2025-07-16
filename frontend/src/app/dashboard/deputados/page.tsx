// frontend/src/app/dashboard/deputados/page.tsx

'use client';

import * as React from 'react';
import { Box, Typography, Stack, Container } from '@mui/material';

import type { Deputado } from '@/types/deputado';
import { DeputadosFilters } from '@/components/dashboard/deputados/deputados-filters';
import { DeputadosTable } from '@/components/dashboard/deputados/deputados-table';
import { getDeputados } from '@/services/deputados.service';

export default function DeputadosPage(): React.JSX.Element {
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(10);
  const [deputados, setDeputados] = React.useState<Deputado[]>([]);
  const [totalDeputados, setTotalDeputados] = React.useState(0);
  const [sort, setSort] = React.useState('nome:asc');
  const [filters, setFilters] = React.useState<Record<string, string | undefined>>({});
  const [loading, setLoading] = React.useState(true); // Add loading state

  const handleFetchDeputados = React.useCallback(async () => {
    setLoading(true); // Set loading to true before fetching
    try {
      const { data, total } = await getDeputados({
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        sort,
        filters,
      });
      setDeputados(data);
      setTotalDeputados(total);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false); // Set loading to false after fetching is complete
    }
  }, [page, rowsPerPage, sort, filters]);

  React.useEffect(() => {
    handleFetchDeputados();
  }, [handleFetchDeputados]);

  return (
    <Box component="main" sx={{ flexGrow: 1, py: 8 }}>
      <Container maxWidth="lg">
        <Stack spacing={3}>
          <div>
            <Typography variant="h4">Deputados</Typography>
          </div>
          <DeputadosFilters onFilterChange={setFilters} />
          <DeputadosTable
            count={totalDeputados}
            items={deputados}
            onPageChange={(event, newPage) => setPage(newPage)}
            onRowsPerPageChange={(event) => {
              setRowsPerPage(parseInt(event.target.value, 10));
              setPage(0); // Reset to first page when rows per page changes
            }}
            onSortChange={setSort}
            page={page}
            rowsPerPage={rowsPerPage}
            sort={sort}
            loading={loading} // Pass loading state to table
          />
        </Stack>
      </Container>
    </Box>
  );
}
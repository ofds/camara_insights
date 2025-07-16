// frontend/src/components/dashboard/deputados/deputados-table.tsx

import * as React from 'react';
import {
  Avatar,
  Box,
  Card,
  Link,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  Skeleton, // Import Skeleton
  Divider, // Import Divider
} from '@mui/material';

import type { Deputado } from '@/types/deputado';
import { paths } from '@/paths';

interface DeputadosTableProps {
  count?: number;
  items?: Deputado[];
  onPageChange?: (event: unknown, newPage: number) => void;
  onRowsPerPageChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onSortChange: (sort: string) => void;
  page?: number;
  rowsPerPage?: number;
  sort: string;
  loading?: boolean; // Add loading prop
}

export function DeputadosTable({
  count = 0,
  items = [],
  onPageChange,
  onRowsPerPageChange,
  onSortChange,
  page = 0,
  rowsPerPage = 0,
  sort,
  loading = false, // Destructure loading prop
}: DeputadosTableProps): React.JSX.Element {
  const [sortField, sortDirection] = sort.split(':');

  const handleSort = (field: string) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    onSortChange(`${field}:${isAsc ? 'desc' : 'asc'}`);
  };

  const sortableFields = [
    { id: 'nome', label: 'Nome' },
    { id: 'siglaPartido', label: 'Partido' },
    { id: 'siglaUf', label: 'UF' },
    { id: 'situacao', label: 'Situação' },
  ];

  return (
    <Card>
      <Box sx={{ overflowX: 'auto' }}>
        <Table sx={{ minWidth: '800px' }}>
          <TableHead>
            <TableRow>
              <TableCell>Foto</TableCell>
              {sortableFields.map((field) => (
                <TableCell key={field.id} sortDirection={sortField === field.id ? (sortDirection as 'asc' | 'desc') : false}>
                  <TableSortLabel active={sortField === field.id} direction={sortDirection as 'asc' | 'desc'} onClick={() => handleSort(field.id)}>
                    {field.label}
                  </TableSortLabel>
                </TableCell>
              ))}
              <TableCell>Email</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              // Show skeleton rows while loading
              Array.from({ length: rowsPerPage }).map((_, index) => (
                <TableRow key={index}>
                  <TableCell colSpan={6}>
                    <Skeleton variant="text" sx={{ width: '100%' }} />
                  </TableCell>
                </TableRow>
              ))
            ) : (
              // Show data rows when not loading
              items.map((deputado) => (
                <TableRow hover key={deputado.id}>
                  <TableCell><Avatar src={deputado.ultimoStatus_urlFoto} /></TableCell>
                  <TableCell>
                    {/* Correctly use the dynamic path function */}
                    <Link href={paths.dashboard.deputado(deputado.id)} underline="hover">
                      {deputado.ultimoStatus_nome}
                    </Link>
                  </TableCell>
                  <TableCell>{deputado.ultimoStatus_siglaPartido}</TableCell>
                  <TableCell>{deputado.ultimoStatus_siglaUf}</TableCell>
                  <TableCell>{deputado.ultimoStatus_situacao}</TableCell>
                  <TableCell>{deputado.ultimoStatus_email}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Box>
      <Divider />
      <TablePagination
        component="div"
        count={count}
        onPageChange={onPageChange}
        onRowsPerPageChange={onRowsPerPageChange}
        page={page}
        rowsPerPage={rowsPerPage}
        rowsPerPageOptions={[5, 10, 25, 50]}
        labelRowsPerPage="Linhas por página:"
      />
    </Card>
  );
}
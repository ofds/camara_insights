// frontend/src/components/dashboard/deputados/deputados-table.tsx

import * as React from 'react';
import {
  Avatar,
  Box,
  Card,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TablePagination,
  TableRow,
  Link,
  TableSortLabel,
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
}: DeputadosTableProps): React.JSX.Element {
  const [sortField, sortDirection] = sort.split(':');

  const handleSort = (field: string) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    onSortChange(`${field}:${isAsc ? 'desc' : 'asc'}`);
  };

  return (
    <Card>
      <Box sx={{ overflowX: 'auto' }}>
        <Table sx={{ minWidth: '800px' }}>
          <TableHead>
            <TableRow>
              <TableCell>Foto</TableCell>
              <TableCell sortDirection={sortField === 'nome' ? (sortDirection as 'asc' | 'desc') : false}>
                <TableSortLabel active={sortField === 'nome'} direction={sortDirection as 'asc' | 'desc'} onClick={() => handleSort('nome')}>
                  Nome
                </TableSortLabel>
              </TableCell>
              <TableCell sortDirection={sortField === 'siglaPartido' ? (sortDirection as 'asc' | 'desc') : false}>
                <TableSortLabel active={sortField === 'siglaPartido'} direction={sortDirection as 'asc' | 'desc'} onClick={() => handleSort('siglaPartido')}>
                  Partido
                </TableSortLabel>
              </TableCell>
              <TableCell sortDirection={sortField === 'siglaUf' ? (sortDirection as 'asc' | 'desc') : false}>
                <TableSortLabel active={sortField === 'siglaUf'} direction={sortDirection as 'asc' | 'desc'} onClick={() => handleSort('siglaUf')}>
                  UF
                </TableSortLabel>
              </TableCell>
              <TableCell>Email</TableCell>
              <TableCell sortDirection={sortField === 'situacao' ? (sortDirection as 'asc' | 'desc') : false}>
                 <TableSortLabel active={sortField === 'situacao'} direction={sortDirection as 'asc' | 'desc'} onClick={() => handleSort('situacao')}>
                  Situação
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((deputado) => (
              <TableRow hover key={deputado.id}>
                <TableCell>
                  <Avatar src={deputado.ultimoStatus_urlFoto} />
                </TableCell>
                <TableCell>
                   <Link href={`${paths.dashboard.deputados}/${deputado.id}`} underline="hover">
                    {deputado.ultimoStatus_nome}
                   </Link>
                </TableCell>
                <TableCell>{deputado.ultimoStatus_siglaPartido}</TableCell>
                <TableCell>{deputado.ultimoStatus_siglaUf}</TableCell>
                <TableCell>{deputado.ultimoStatus_email}</TableCell>
                <TableCell>{deputado.ultimoStatus_situacao}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Box>
      <TablePagination
        component="div"
        count={count}
        onPageChange={onPageChange}
        onRowsPerPageChange={onRowsPerPageChange}
        page={page}
        rowsPerPage={rowsPerPage}
        rowsPerPageOptions={[5, 10, 25]}
      />
    </Card>
  );
}
// frontend/src/components/dashboard/proposal/proposals-table.tsx

'use client';

import * as React from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Checkbox from '@mui/material/Checkbox';
import Divider from '@mui/material/Divider';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import dayjs from 'dayjs';
import Skeleton from '@mui/material/Skeleton';
import { TableSortLabel } from '@mui/material';

import { useSelection } from '@/hooks/use-selection';
import type { Proposal } from '@/types/proposition';

interface ProposalsTableProps {
  count: number;
  page: number;
  rows: Proposal[];
  rowsPerPage: number;
  onPageChange: (event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) => void;
  onRowsPerPageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onSort: (property: keyof Proposal) => void;
  order: 'asc' | 'desc';
  orderBy: keyof Proposal;
  loading?: boolean;
}

export function ProposalsTable({
  count,
  rows,
  page,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange,
  onSort,
  order,
  orderBy,
  loading = false,
}: ProposalsTableProps): React.JSX.Element {
  const rowIds = React.useMemo(() => {
    return rows.map((proposal) => proposal.id);
  }, [rows]);

  const { selectAll, deselectAll, selectOne, deselectOne, selected } = useSelection(rowIds);

  const selectedSome = (selected?.size ?? 0) > 0 && (selected?.size ?? 0) < rows.length;
  const selectedAll = rows.length > 0 && selected?.size === rows.length;

  return (
    <Card>
      <Box sx={{ overflowX: 'auto' }}>
        <Table sx={{ minWidth: '1200px', '& .MuiTableCell-root': { fontSize: '0.875rem' } }}>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedAll}
                  indeterminate={selectedSome}
                  onChange={(event) => {
                    if (event.target.checked) {
                      selectAll();
                    } else {
                      deselectAll();
                    }
                  }}
                />
              </TableCell>
              <TableCell sortDirection={orderBy === 'title' ? order : false}>
                <TableSortLabel active={orderBy === 'title'} direction={orderBy === 'title' ? order : 'asc'} onClick={() => onSort('title')}>
                  Title
                </TableSortLabel>
              </TableCell>
              <TableCell sortDirection={orderBy === 'status' ? order : false}>
                <TableSortLabel active={orderBy === 'status'} direction={orderBy === 'status' ? order : 'asc'} onClick={() => onSort('status')}>
                  Status
                </TableSortLabel>
              </TableCell>
              <TableCell sortDirection={orderBy === 'author' ? order : false}>
                <TableSortLabel active={orderBy === 'author'} direction={orderBy === 'author' ? order : 'asc'} onClick={() => onSort('author')}>
                  Author
                </TableSortLabel>
              </TableCell>
              <TableCell sortDirection={orderBy === 'createdAt' ? order : false}>
                <TableSortLabel active={orderBy === 'createdAt'} direction={orderBy === 'createdAt' ? order : 'asc'} onClick={() => onSort('createdAt')}>
                  Created
                </TableSortLabel>
              </TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Number</TableCell>
              <TableCell>Year</TableCell>
              <TableCell sortDirection={orderBy === 'impact_score' ? order : false}>
                 <TableSortLabel active={orderBy === 'impact_score'} direction={orderBy === 'impact_score' ? order : 'asc'} onClick={() => onSort('impact_score')}>
                  Impact Score
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              Array.from({ length: rowsPerPage }).map((_, index) => (
                <TableRow key={index}>
                  <TableCell padding="checkbox">
                    <Skeleton variant="rectangular" width={24} height={24} />
                  </TableCell>
                  <TableCell colSpan={8}>
                    <Skeleton variant="text" />
                  </TableCell>
                </TableRow>
              ))
            ) : (
              rows.map((row) => {
                const isSelected = selected?.has(row.id);

                return (
                  <TableRow hover key={row.id} selected={isSelected}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={isSelected}
                        onChange={(event) => {
                          if (event.target.checked) {
                            selectOne(row.id);
                          } else {
                            deselectOne(row.id);
                          }
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="subtitle2" noWrap sx={{ maxWidth: '300px' }}>{row.title}</Typography>
                    </TableCell>
                    <TableCell>{row.status}</TableCell>
                    <TableCell>{row.author}</TableCell>
                    <TableCell>{dayjs(row.createdAt).format('MMM D, YYYY')}</TableCell>
                    <TableCell>{row.siglaTipo}</TableCell>
                    <TableCell>{row.numero}</TableCell>
                    <TableCell>{row.ano}</TableCell>
                    <TableCell>{row.impact_score}</TableCell>
                  </TableRow>
                );
              })
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
        rowsPerPageOptions={[5, 10, 25]}
      />
    </Card>
  );
}
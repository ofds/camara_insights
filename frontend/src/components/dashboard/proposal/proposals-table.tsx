'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Chip from '@mui/material/Chip';
import Collapse from '@mui/material/Collapse';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import Skeleton from '@mui/material/Skeleton';
import Stack from '@mui/material/Stack';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import Typography from '@mui/material/Typography';
import { KeyboardArrowDown as KeyboardArrowDownIcon, KeyboardArrowUp as KeyboardArrowUpIcon } from '@mui/icons-material';
import dayjs from 'dayjs';

import type { ApiProposal, Proposal } from '@/types/proposition';
import { paths } from '@/paths';

interface ProposalsTableProps {
  count: number;
  page: number;
  rows: Proposal[];
  rawRows: ApiProposal[];
  rowsPerPage: number;
  onPageChange: (event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) => void;
  onRowsPerPageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onSort: (property: string) => void;
  order: 'asc' | 'desc';
  orderBy: string;
  loading?: boolean;
}

function ProposalRow(props: { row: Proposal; rawRow: ApiProposal }) {
  const { row, rawRow } = props;
  const [open, setOpen] = React.useState(false);
  const router = useRouter();

  const handleRowClick = () => {
    router.push(`${paths.dashboard.proposals}/${row.id}`);
  };

  return (
    <React.Fragment>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' }, cursor: 'pointer' }} onClick={handleRowClick}>
        <TableCell>
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={(e) => {
              e.stopPropagation(); // Impede que o clique no ícone acione o clique na linha
              setOpen(!open);
            }}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>
          <Typography variant="body2" noWrap sx={{ maxWidth: '250px' }}>
            {row.title}
          </Typography>
        </TableCell>
        <TableCell>{row.status}</TableCell>
        <TableCell>{row.author}</TableCell>
        <TableCell>{dayjs(row.createdAt).format('DD/MM/YYYY')}</TableCell>
        <TableCell>{row.siglaTipo}</TableCell>
        <TableCell>{row.numero}</TableCell>
        <TableCell>{row.ano}</TableCell>
        <TableCell>{row.impact_score}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={9}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1, padding: 2, backgroundColor: 'rgba(0, 0, 0, 0.02)', borderRadius: 1 }}>
              <Typography variant="subtitle1" gutterBottom component="div" sx={{ fontWeight: 'bold' }}>
                Detalhes da Proposta
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    Resumo:
                  </Typography>
                  <Typography variant="body2">{rawRow.summary || 'Não disponível'}</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    Escopo:
                  </Typography>
                  <Typography variant="body2">{rawRow.scope || 'Não disponível'}</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    Magnitude:
                  </Typography>
                  <Typography variant="body2">{rawRow.magnitude || 'Não disponível'}</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    Tramitação:
                  </Typography>
                  <Typography variant="body2">{rawRow.statusProposicao_descricaoTramitacao || 'Não disponível'}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    Tags:
                  </Typography>
                  {rawRow.tags && rawRow.tags.length > 0 ? (
                    <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1 }}>
                      {rawRow.tags.map((tag) => (
                        <Chip key={tag} label={tag} size="small" />
                      ))}
                    </Stack>
                  ) : (
                    <Typography variant="body2">Nenhuma tag</Typography>
                  )}
                </Grid>
              </Grid>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
}

export function ProposalsTable({
  count,
  rows,
  rawRows,
  page,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange,
  onSort,
  order,
  orderBy,
  loading = false,
}: ProposalsTableProps): React.JSX.Element {
  const sortableFields: { id: string; label: string }[] = [
    { id: 'title', label: 'Título' },
    { id: 'statusProposicao_descricaoSituacao', label: 'Status' },
    { id: 'author', label: 'Autor' },
    { id: 'dataApresentacao', label: 'Criação' },
    { id: 'siglaTipo', label: 'Tipo' },
    { id: 'numero', label: 'Número' },
    { id: 'ano', label: 'Ano' },
    { id: 'impact_score', label: 'Pontuação de Impacto' },
  ];

  return (
    <Card>
      <Box sx={{ overflowX: 'auto' }}>
        <Table sx={{ minWidth: '1000px', '& .MuiTableCell-root': { fontSize: '0.75rem', padding: '12px' } }}>
          <TableHead>
            <TableRow>
              <TableCell />
              {sortableFields.map((field) => (
                <TableCell key={field.id} sortDirection={orderBy === field.id ? order : false}>
                  <TableSortLabel
                    active={orderBy === field.id}
                    direction={orderBy === field.id ? order : 'asc'}
                    onClick={() => onSort(field.id)}
                    disabled={field.id === 'author'} // Desabilita ordenação em campo com valor fixo
                  >
                    {field.label}
                  </TableSortLabel>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              Array.from({ length: rowsPerPage }).map((_, index) => (
                <TableRow key={index}>
                  <TableCell colSpan={9}>
                    <Skeleton variant="text" />
                  </TableCell>
                </TableRow>
              ))
            ) : (
              rows.map((row) => {
                const rawRow = rawRows.find((r) => r.id.toString() === row.id);
                return rawRow ? <ProposalRow key={row.id} row={row} rawRow={rawRow} /> : null;
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
        rowsPerPageOptions={[5, 10, 25, 50]}
        labelRowsPerPage="Linhas por página:"
      />
    </Card>
  );
}
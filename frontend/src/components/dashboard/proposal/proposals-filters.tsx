'use client';

import * as React from 'react';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import Card from '@mui/material/Card';
import InputAdornment from '@mui/material/InputAdornment';
import OutlinedInput from '@mui/material/OutlinedInput';
import { MagnifyingGlassIcon } from '@phosphor-icons/react/dist/ssr/MagnifyingGlass';
import {
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  TextField,
  FormControlLabel,
  Switch,
} from '@mui/material';

// Tipos de proposições
const proposalTypes = [
  { sigla: 'MPV', nome: 'Medida Provisória' },
  { sigla: 'PDC', nome: 'Projeto de Decreto Legislativo' },
  { sigla: 'PEC', nome: 'Proposta de Emenda à Constituição' },
  { sigla: 'PL', nome: 'Projeto de Lei' },
  { sigla: 'PLP', nome: 'Projeto de Lei Complementar' },
  { sigla: 'PLV', nome: 'Projeto de Lei de Conversão' },
  { sigla: 'PRC', nome: 'Projeto de Resolução' },
  { sigla: 'RCP', nome: 'Requerimento de Instituição de CPI' },
  { sigla: 'REC', nome: 'Recurso' },
  { sigla: 'REQ', nome: 'Requerimento' },
];

export function ProposalsFilters({
  rawFilters,
  setRawFilters,
}: {
  rawFilters: { [key: string]: string | number | boolean };
  setRawFilters: (filters: { [key: string]: string | number | boolean }) => void;
}): React.JSX.Element {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [filters, setFilters] = React.useState<{ [key: string]: string | number | boolean }>(rawFilters);

  React.useEffect(() => {
    setFilters(rawFilters);
  }, [rawFilters]);

  const handleChange = (key: string, value: string | number | boolean) => {
    const newFilters = { ...filters, [key]: value };
    if (value === '' || value === false) {
      delete newFilters[key];
    }
    setFilters(newFilters);
    setRawFilters(newFilters);

    if (key === 'search') {
      const current = new URLSearchParams(Array.from(searchParams.entries())); // Use a mutable copy

      if (!value) {
        current.delete("search");
      } else {
        current.set("search", String(value));
      }

      const search = current.toString();
      const query = search ? `?${search}` : "";

      router.push(`${pathname}${query}`);
    }
  };

  return (
    <Card sx={{ p: 2, display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
      <OutlinedInput
        value={filters.search || ''}
        placeholder="Buscar por palavras-chave..."
        size="small"
        startAdornment={
          <InputAdornment position="start">
            <MagnifyingGlassIcon fontSize="var(--icon-fontSize-md)" />
          </InputAdornment>
        }
        sx={{ flexGrow: 1, minWidth: '200px' }}
        onChange={(e) => handleChange('search', e.target.value)}
      />
      <FormControl sx={{ minWidth: 100 }} size="small">
        <InputLabel>Tipo</InputLabel>
        <Select
          onChange={(e) => handleChange('siglaTipo', e.target.value as string)}
          label="Tipo"
          value={filters.siglaTipo || ''}
        >
          <MenuItem value="">
            <em>Todos</em>
          </MenuItem>
          {proposalTypes.map((type) => (
            <MenuItem key={type.sigla} value={type.sigla} title={type.nome}>
              {type.sigla}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl sx={{ minWidth: 120 }} size="small">
        <InputLabel>Escopo</InputLabel>
        <Select
          onChange={(e) => handleChange('scope', e.target.value as string)}
          label="Escopo"
          value={filters.scope || ''}
        >
          <MenuItem value="">Todos</MenuItem>
          <MenuItem value="Nacional">Nacional</MenuItem>
          <MenuItem value="Estadual">Estadual</MenuItem>
          <MenuItem value="Municipal">Municipal</MenuItem>
        </Select>
      </FormControl>
      <FormControl sx={{ minWidth: 120 }} size="small">
        <InputLabel>Magnitude</InputLabel>
        <Select
          onChange={(e) => handleChange('magnitude', e.target.value as string)}
          label="Magnitude"
          value={filters.magnitude || ''}
        >
          <MenuItem value="">Todas</MenuItem>
          <MenuItem value="Baixo">Baixo</MenuItem>
          <MenuItem value="Médio">Médio</MenuItem>
          <MenuItem value="Alto">Alto</MenuItem>
          <MenuItem value="Setorial Específico">Setorial Específico</MenuItem>
          <MenuItem value="População Geral">População Geral</MenuItem>
        </Select>
      </FormControl>
      <TextField
        label="Data Início"
        type="date"
        size="small"
        InputLabelProps={{
          shrink: true,
        }}
        onChange={(e) => handleChange('data_inicio', e.target.value)}
      />
      <TextField
        label="Data Fim"
        type="date"
        size="small"
        InputLabelProps={{
          shrink: true,
        }}
        onChange={(e) => handleChange('data_fim', e.target.value)}
      />
      <TextField
        label="Autor"
        variant="outlined"
        size="small"
        sx={{ minWidth: 120 }}
        onChange={(e) => handleChange('autor', e.target.value)}
      />
      <TextField
        label="Número"
        variant="outlined"
        type="number"
        size="small"
        sx={{ minWidth: 90, maxWidth: '100px' }}
        onChange={(e) => handleChange('numero', e.target.value)}
      />
      <TextField
        label="Ano"
        variant="outlined"
        type="number"
        defaultValue="2025"
        size="small"
        sx={{ minWidth: 90, maxWidth: '100px' }}
        onChange={(e) => handleChange('ano', e.target.value)}
      />
      <FormControlLabel
        control={
          <Switch
            checked={!!filters.scored}
            onChange={(e) => handleChange('scored', e.target.checked)}
          />
        }
        label="Analizado"
      />
    </Card>
  );
}

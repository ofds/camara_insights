// frontend/src/components/dashboard/deputados/deputados-filters.tsx

import * as React from 'react';
import { Card, CardContent, Grid, TextField, InputAdornment } from '@mui/material';
import { MagnifyingGlass as MagnifyingGlassIcon } from '@phosphor-icons/react/dist/ssr/MagnifyingGlass';
import { useDebounce } from 'use-debounce';

interface DeputadosFiltersProps {
  onFilterChange: (filters: Record<string, string | undefined>) => void;
}

export function DeputadosFilters({ onFilterChange }: DeputadosFiltersProps): React.JSX.Element {
  const [nome, setNome] = React.useState('');
  const [partido, setPartido] = React.useState('');
  const [uf, setUf] = React.useState('');

  const [debouncedNome] = useDebounce(nome, 500);
  const [debouncedPartido] = useDebounce(partido, 500);
  const [debouncedUf] = useDebounce(uf, 500);

  React.useEffect(() => {
    onFilterChange({
      // MODIFIED: Ensure the filter key matches what the backend expects
      ultimoStatus_nome__ilike: debouncedNome || undefined,
      ultimoStatus_siglaPartido: debouncedPartido || undefined,
      ultimoStatus_siglaUf: debouncedUf || undefined,
    });
  }, [debouncedNome, debouncedPartido, debouncedUf, onFilterChange]);

  return (
    <Card>
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Nome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <MagnifyingGlassIcon fontSize="var(--icon-fontSize-md)" />
                  </InputAdornment>
                ),
              }}
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Partido (Sigla)"
              value={partido}
              onChange={(e) => setPartido(e.target.value)}
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="UF (Sigla)"
              value={uf}
              onChange={(e) => setUf(e.target.value)}
              variant="outlined"
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
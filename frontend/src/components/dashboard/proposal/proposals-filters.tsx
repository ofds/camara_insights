// frontend/src/components/dashboard/proposal/proposals-filters.tsx

import * as React from 'react';
import Card from '@mui/material/Card';
import InputAdornment from '@mui/material/InputAdornment';
import OutlinedInput from '@mui/material/OutlinedInput';
import { MagnifyingGlassIcon } from '@phosphor-icons/react/dist/ssr/MagnifyingGlass';
import { Select, MenuItem, InputLabel, FormControl, TextField, FormControlLabel, Switch } from '@mui/material';

export function ProposalsFilters({
  onFilterChange,
}: {
  onFilterChange: (filters: { [key: string]: string | number | boolean }) => void;
}): React.JSX.Element {
  const [filters, setFilters] = React.useState<{ [key: string]: string | number | boolean }>({});

  const handleChange = (key: string, value: string | number | boolean) => {
    const newFilters = { ...filters, [key]: value };
    if (value === '' || value === false) {
      delete newFilters[key];
    }
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  return (
    <Card sx={{ p: 2, display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
      <OutlinedInput
        defaultValue=""
        placeholder="Buscar por título"
        size="small"
        startAdornment={
          <InputAdornment position="start">
            <MagnifyingGlassIcon fontSize="var(--icon-fontSize-md)" />
          </InputAdornment>
        }
        sx={{ flexGrow: 1, minWidth: '300px' }}
        onChange={(e) => handleChange('ementa', e.target.value)}
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
          <MenuItem value="PEC">PEC</MenuItem>
          <MenuItem value="PL">PL</MenuItem>
          <MenuItem value="PLP">PLP</MenuItem>
          <MenuItem value="MPV">MPV</MenuItem>
          <MenuItem value="REQ">REQ</MenuItem>
        </Select>
      </FormControl>
      <TextField
        label="Tags"
        variant="outlined"
        size="small"
        sx={{ minWidth: 120 }}
        onChange={(e) => handleChange('tags', e.target.value)}
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
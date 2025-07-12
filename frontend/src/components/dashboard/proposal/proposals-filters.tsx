// frontend/src/components/dashboard/proposal/proposals-filters.tsx

import * as React from 'react';
import Card from '@mui/material/Card';
import InputAdornment from '@mui/material/InputAdornment';
import OutlinedInput from '@mui/material/OutlinedInput';
import { MagnifyingGlassIcon } from '@phosphor-icons/react/dist/ssr/MagnifyingGlass';
import { Select, MenuItem, InputLabel, FormControl } from '@mui/material';

export function ProposalsFilters({
  onFilterChange,
  onSiglaTipoChange,
}: {
  onFilterChange: (value: string) => void;
  onSiglaTipoChange: (value: string) => void;
}): React.JSX.Element {
  return (
    <Card sx={{ p: 2, display: 'flex', gap: 2 }}>
      <OutlinedInput
        defaultValue=""
        fullWidth
        placeholder="Search proposal by title"
        startAdornment={
          <InputAdornment position="start">
            <MagnifyingGlassIcon fontSize="var(--icon-fontSize-md)" />
          </InputAdornment>
        }
        sx={{ maxWidth: '500px' }}
        onChange={(e) => onFilterChange(e.target.value)}
      />
      <FormControl sx={{ minWidth: 120 }}>
        <InputLabel>Tipo</InputLabel>
        <Select
          onChange={(e) => onSiglaTipoChange(e.target.value as string)}
          label="Tipo"
        >
          <MenuItem value="">
            <em>Todos</em>
          </MenuItem>
          <MenuItem value="PEC">PEC</MenuItem>
          <MenuItem value="PL">PL</MenuItem>
        </Select>
      </FormControl>
    </Card>
  );
}
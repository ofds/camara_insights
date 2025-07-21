
'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputAdornment from '@mui/material/InputAdornment';
import { MagnifyingGlassIcon } from '@phosphor-icons/react/dist/ssr/MagnifyingGlass';

export function MainNavSearch(): React.JSX.Element {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = React.useState('');

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleSearch = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && searchTerm.trim() !== '') {
      router.push(`/dashboard/proposals?search=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  return (
    <OutlinedInput
      value={searchTerm}
      onChange={handleSearchChange}
      onKeyDown={handleSearch}
      placeholder="Buscar por palavras-chave..."
      size="small"
      startAdornment={
        <InputAdornment position="start">
          <MagnifyingGlassIcon fontSize="var(--icon-fontSize-md)" />
        </InputAdornment>
      }
      sx={{ flexGrow: 1, minWidth: '200px' }}
    />
  );
}

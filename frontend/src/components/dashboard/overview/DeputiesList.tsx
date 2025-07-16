// src/components/dashboard/overview/DeputiesList.tsx

import React from 'react';
import { List, ListItem, ListItemText, Avatar, Typography, Divider, Box, ListItemButton } from '@mui/material';
import { type ApiRankedDeputy } from '@/types/deputado';
import { useRouter } from 'next/navigation';
import { paths } from '@/paths';

interface DeputiesListProps {
  deputies: ApiRankedDeputy[];
}

export default function DeputiesList({ deputies }: DeputiesListProps) {
  const router = useRouter();

  if (!deputies || deputies.length === 0) {
    return <Typography sx={{ p: 2 }}>Nenhum deputado encontrado no ranking.</Typography>;
  }

  const handleItemClick = (deputyId: number) => {
    router.push(paths.dashboard.deputado(deputyId));
  };

  return (
    <List disablePadding>
      {deputies.map((deputy, index) => (
        <React.Fragment key={deputy.id}>
          <ListItemButton onClick={() => handleItemClick(deputy.id)}>
            <ListItem>
              <Avatar src={deputy.url_foto} sx={{ mr: 2 }} />
              <ListItemText
                primary={deputy.nome}
                secondary={`${deputy.sigla_partido} - ${deputy.sigla_uf}`}
              />
              <Box sx={{ textAlign: 'right' }}>
                <Typography variant="body1" fontWeight="bold">
                  {deputy.total_impacto.toFixed(2)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Impacto Total
                </Typography>
              </Box>
            </ListItem>
          </ListItemButton>
          {index < deputies.length - 1 && <Divider component="li" />}
        </React.Fragment>
      ))}
    </List>
  );
}
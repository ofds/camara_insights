// src/components/dashboard/overview/DeputiesList.tsx

import React from 'react';
import { List, ListItem, ListItemText, Avatar, Typography, Divider, Box } from '@mui/material';
import { type ApiRankedDeputy } from '@/types/deputado';

interface DeputiesListProps {
  deputies: ApiRankedDeputy[];
}

export default function DeputiesList({ deputies }: DeputiesListProps) {
  if (!deputies || deputies.length === 0) {
    return <Typography sx={{ p: 2 }}>Nenhum deputado encontrado no ranking.</Typography>;
  }

  return (
    <List disablePadding>
      {deputies.map((deputy, index) => (
        <React.Fragment key={deputy.id}>
          <ListItem>
            {/* Use the new, clean property name */}
            <Avatar src={deputy.url_foto} sx={{ mr: 2 }} />
            <ListItemText
              // Use the new, clean property names
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
          {index < deputies.length - 1 && <Divider component="li" variant="inset" />}
        </React.Fragment>
      ))}
    </List>
  );
}
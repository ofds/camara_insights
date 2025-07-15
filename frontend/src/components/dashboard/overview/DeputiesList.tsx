// src/components/dashboard/overview/DeputiesList.tsx

import { List, ListItem, ListItemText, Avatar, Typography, Divider, Box } from '@mui/material';
import { type ApiRankedDeputy } from '@/types/deputado';

interface DeputiesListProps {
  deputies: ApiRankedDeputy[];
}

export default function DeputiesList({ deputies }: DeputiesListProps) {
  if (deputies.length === 0) {
    return <Typography sx={{ p: 2 }}>Nenhum deputado encontrado no ranking.</Typography>;
  }

  return (
    <List disablePadding>
      {deputies.map((deputy, index) => (
        <div key={deputy.id}>
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
          {index < deputies.length - 1 && <Divider component="li" variant="inset" />}
        </div>
      ))}
    </List>
  );
}
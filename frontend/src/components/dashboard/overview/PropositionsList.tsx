// src/components/dashboard/overview/PropositionsList.tsx

import { List, ListItem, ListItemText, Typography, Divider, Chip, Box } from '@mui/material';
import { type ApiProposition } from '@/types/proposition';

interface PropositionsListProps {
  propositions: ApiProposition[];
}

export default function PropositionsList({ propositions }: PropositionsListProps) {
  if (propositions.length === 0) {
    return <Typography sx={{ p: 2 }}>Nenhuma proposição de alto impacto encontrada.</Typography>;
  }

  return (
    <List disablePadding>
      {propositions.map((prop, index) => (
        <div key={prop.id}>
          <ListItem alignItems="flex-start">
            <ListItemText
              primary={`${prop.siglaTipo} ${prop.numero}/${prop.ano}`}
              secondary={
                <>
                  <Typography
                    sx={{ display: 'block' }}
                    component="span"
                    variant="body2"
                    color="text.primary"
                  >
                    {prop.ementa}
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    <Chip label={`Impacto: ${prop.impact_score || 'N/A'}`} size="small" />
                    {prop.dataApresentacao && <Chip label={`Apresentada em: ${new Date(prop.dataApresentacao).toLocaleDateString()}`} size="small" sx={{ ml: 1 }} />}
                  </Box>
                </>
              }
            />
          </ListItem>
          {index < propositions.length - 1 && <Divider component="li" />}
        </div>
      ))}
    </List>
  );
}
// frontend/src/components/dashboard/HighImpactPropositionsCard.tsx

'use client';

import React from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText, Divider, Chip, Stack } from '@mui/material';
import type { ApiProposition } from '@/services/proposicoes.service';
import dayjs from 'dayjs';

interface HighImpactPropositionsProps {
  propositions: ApiProposition[];
}

export default function HighImpactPropositionsCard({ propositions }: HighImpactPropositionsProps) {
  return (
    <Paper elevation={3} sx={{ p: 2, mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Proposições de Maior Impacto
      </Typography>
      <List disablePadding>
        {propositions.map((prop, index) => (
          <React.Fragment key={prop.id}>
            <ListItem disableGutters sx={{ alignItems: 'flex-start' }}>
              <ListItemText
                primary={
                  <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                    {`${prop.sigla_tipo} ${prop.numero}/${prop.ano}`}
                  </Typography>
                }
                secondary={
                  <>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        display: '-webkit-box',
                        WebkitBoxOrient: 'vertical',
                        WebkitLineClamp: 2,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        mb: 1
                      }}
                    >
                      {prop.ementa}
                    </Typography>
                    <Stack direction="row" spacing={1}>
                      {prop.tags?.map((tag) => (
                        <Chip key={tag} label={tag} size="small" variant="outlined" />
                      ))}
                    </Stack>
                  </>
                }
              />
              <Box sx={{ ml: 2, textAlign: 'right', flexShrink: 0 }}>
                  <Chip label={`Impacto: ${prop.impact_score?.toFixed(0)}`} color="primary" variant="outlined" size="small"/>
                  {prop.magnitude && (
                    <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                     Magnitude: {prop.magnitude}
                    </Typography>
                  )}
                  <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                    {dayjs(prop.data_apresentacao).format('DD/MM/YYYY')}
                  </Typography>
              </Box>
            </ListItem>
            {index < propositions.length - 1 && <Divider component="li" sx={{ my: 1 }} />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
}
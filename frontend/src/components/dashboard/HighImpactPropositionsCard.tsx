// src/components/dashboard/HighImpactPropositionsCard.tsx
'use client';

import React from 'react';

import { Box, Typography, Paper, List, ListItem, ListItemText, Divider, Chip } from '@mui/material';
import type { ApiProposition } from '@/services/proposicoes.service';
import dayjs from 'dayjs';

interface HighImpactPropositionsProps {
  propositions: ApiProposition[];
}

export default function HighImpactPropositionsCard({ propositions }: HighImpactPropositionsProps) {
  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Proposições de Maior Impacto
      </Typography>
      <List disablePadding>
        {propositions.map((prop, index) => (
          <React.Fragment key={prop.id}>
            <ListItem disableGutters>
              <ListItemText
                primary={
                  <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                    {`${prop.sigla_tipo} ${prop.numero}/${prop.ano}`}
                  </Typography>
                }
                secondary={
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      display: '-webkit-box',
                      WebkitBoxOrient: 'vertical',
                      WebkitLineClamp: 2, // Limita o texto a 2 linhas
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {prop.ementa}
                  </Typography>
                }
              />
              <Box sx={{ ml: 2, textAlign: 'right' }}>
                  <Chip label={`Impacto: ${prop.impact_score?.toFixed(2)}`} color="primary" variant="outlined" size="small"/>
                  <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                    {dayjs(prop.data_apresentacao).format('DD/MM/YYYY')}
                  </Typography>
              </Box>
            </ListItem>
            {index < propositions.length - 1 && <Divider component="li" />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
}
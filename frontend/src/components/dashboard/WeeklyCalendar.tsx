// src/components/dashboard/WeeklyCalendar.tsx
'use client';

import React from 'react';
import { Box, Typography, Paper, Chip } from '@mui/material';
import dayjs from 'dayjs';
import 'dayjs/locale/pt-br';
dayjs.locale('pt-br');

import type { ApiEvent } from '@/services/eventos.service';

interface WeeklyCalendarProps {
  events: ApiEvent[];
}

const MAX_EVENTS_VISIBLE = 2; // Reduzi para 2 para um visual mais limpo

export default function WeeklyCalendar({ events }: WeeklyCalendarProps) {
  const today = dayjs();
  // Começa a semana na Segunda-feira (padrão mais comum no Brasil)
  const startOfWeek = today.startOf('week').add(1, 'day'); 
  const weekDays = Array.from({ length: 7 }, (_, i) => startOfWeek.add(i, 'day'));

  const eventsByDay = new Map<string, ApiEvent[]>();
  events.forEach((event) => {
    const eventDate = dayjs(event.dataHoraInicio).format('YYYY-MM-DD');
    if (!eventsByDay.has(eventDate)) {
      eventsByDay.set(eventDate, []);
    }
    eventsByDay.get(eventDate)?.push(event);
  });

  return (
    // O Paper foi removido daqui e o Box principal assume o controle
    <Box sx={{ display: 'flex', flexDirection: 'row', gap: 1.5, width: '100%' }}>
      {weekDays.map((day) => {
        const dayKey = day.format('YYYY-MM-DD');
        const todaysEvents = eventsByDay.get(dayKey) || [];
        const remainingEventsCount = todaysEvents.length - MAX_EVENTS_VISIBLE;

        return (
          <Box
            key={dayKey}
            sx={{
              flex: 1, // Cada dia ocupa o mesmo espaço, sem forçar overflow
              minWidth: 0, // Essencial para o flexbox encolher os itens corretamente
              display: 'flex',
              flexDirection: 'column',
              border: '1px solid',
              borderColor: 'var(--mui-palette-divider)',
              borderRadius: '12px',
              p: 1.5,
              height: '220px', // Altura fixa para alinhar todas as colunas
            }}
          >
            {/* Cabeçalho do dia */}
            <Box sx={{ textAlign: 'center', mb: 1, flexShrink: 0 }}>
              <Typography
                variant="caption"
                sx={{
                  fontWeight: day.isSame(today, 'day') ? 700 : 500,
                  color: day.isSame(today, 'day') ? 'var(--mui-palette-primary-main)' : 'var(--mui-palette-text-secondary)',
                  textTransform: 'capitalize'
                }}
              >
                {day.format('ddd')}
              </Typography>
              <Typography
                variant="h6"
                sx={{ lineHeight: 1.2, color: day.isSame(today, 'day') ? 'var(--mui-palette-primary-main)' : 'inherit' }}
              >
                {day.format('DD')}
              </Typography>
            </Box>

            {/* Lista de eventos */}
            <Box sx={{ flexGrow: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 1 }}>
              {todaysEvents.slice(0, MAX_EVENTS_VISIBLE).map((event) => (
                <Paper
                  key={event.id}
                  title={`${dayjs(event.dataHoraInicio).format('HH:mm')} - ${event.descricao}`}
                  elevation={0}
                  sx={{
                    p: 1,
                    bgcolor: 'var(--mui-palette-background-level1)',
                    borderLeft: '3px solid',
                    borderColor: 'var(--mui-palette-primary-main)',
                    overflow: 'hidden',
                    cursor: 'pointer'
                  }}
                >
                  <Typography variant="caption" noWrap sx={{ fontWeight: 600, display: 'block' }}>
                    {event.descricaoTipo}
                  </Typography>
                </Paper>
              ))}
              
              {/* Indicador de mais eventos */}
              {remainingEventsCount > 0 && (
                <Chip label={`+ ${remainingEventsCount} mais`} size="small" sx={{ mt: 'auto' }} />
              )}
            </Box>
          </Box>
        );
      })}
    </Box>
  );
}
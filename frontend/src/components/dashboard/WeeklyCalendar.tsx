// src/components/dashboard/WeeklyCalendar.tsx
'use client';

import React, { useState } from 'react'; // Importamos o useState
import { Box, Typography, Paper, Chip, IconButton, Button } from '@mui/material';
import { Timeline, TimelineItem, TimelineSeparator, TimelineConnector, TimelineContent, TimelineDot, TimelineOppositeContent } from '@mui/lab';
import ArrowBackIcon from '@mui/icons-material/ArrowBack'; // Ícone para o botão "Voltar"
import dayjs from 'dayjs';
import 'dayjs/locale/pt-br';
dayjs.locale('pt-br');

import type { ApiEvent } from '@/services/eventos.service';

interface WeeklyCalendarProps {
  events: ApiEvent[];
}

const MAX_EVENTS_VISIBLE = 5;

export default function WeeklyCalendar({ events }: WeeklyCalendarProps) {
  // 1. Estados para controlar a visualização
  const [viewMode, setViewMode] = useState<'week' | 'day'>('week');
  const [selectedDay, setSelectedDay] = useState<dayjs.Dayjs | null>(null);

  const today = dayjs();
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
  
  // 2. Função para mudar para a visão de dia
  const handleDayClick = (day: dayjs.Dayjs) => {
    setSelectedDay(day);
    setViewMode('day');
  };

  // 3. Função para voltar para a visão de semana
  const handleBackToWeekView = () => {
    setSelectedDay(null);
    setViewMode('week');
  };


  // 4. Renderização condicional baseada no viewMode
  if (viewMode === 'day' && selectedDay) {
    // ---- UI DA AGENDA DO DIA COM TIMELINE AGRUPADA ----
    const dayKey = selectedDay.format('YYYY-MM-DD');
    const todaysEvents = (eventsByDay.get(dayKey) || []).sort((a, b) => 
      dayjs(a.dataHoraInicio).diff(dayjs(b.dataHoraInicio))
    );

    // 1. Agrupa os eventos por horário
    const eventsByTime = new Map<string, ApiEvent[]>();
    todaysEvents.forEach((event) => {
      const eventTime = dayjs(event.dataHoraInicio).format('HH:mm');
      if (!eventsByTime.has(eventTime)) {
        eventsByTime.set(eventTime, []);
      }
      eventsByTime.get(eventTime)?.push(event);
    });

    // Converte o Map para um Array para facilitar a iteração
    const groupedEvents = Array.from(eventsByTime.entries());

    return (
      <Paper elevation={3} sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <IconButton onClick={handleBackToWeekView} edge="start" sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6">
            Agenda para {selectedDay.format('dddd, DD [de] MMMM')}
          </Typography>
        </Box>
        
        <Timeline position="right" sx={{p: 0}}>
          {groupedEvents.length > 0 ? (
            // 2. Itera sobre os horários agrupados
            groupedEvents.map(([time, eventsInTime], index) => (
              <TimelineItem key={time}>
                <TimelineOppositeContent sx={{ flex: 0.2, minWidth: '90px' }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    {time}
                  </Typography>
                </TimelineOppositeContent>
                <TimelineSeparator>
                  <TimelineDot color="primary" />
                  {index < groupedEvents.length - 1 && <TimelineConnector />}
                </TimelineSeparator>
                <TimelineContent>
                  {/* 3. Itera sobre os eventos DENTRO de cada horário */}
                  {eventsInTime.map(event => (
                    <Paper 
                      key={event.id} 
                      elevation={0} 
                      sx={{ p: 1.5, mb: 1, bgcolor: 'var(--mui-palette-background-level1)' }}
                    >
                      <Typography sx={{ fontWeight: 600 }}>{event.descricaoTipo}</Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        {event.descricao.split('\n')[0]}
                      </Typography>
                    </Paper>
                  ))}
                </TimelineContent>
              </TimelineItem>
            ))
          ) : (
            <Typography sx={{ textAlign: 'center', py: 4 }}>
              Nenhum evento agendado para este dia.
            </Typography>
          )}
        </Timeline>
      </Paper>
    );
  }

  // ---- UI DO CALENDÁRIO DA SEMANA (código anterior com leves ajustes) ----
  return (
    <Box sx={{ display: 'flex', flexDirection: 'row', width: '100%', ml: '-1px' }}>
      {weekDays.map((day) => {
        const dayKey = day.format('YYYY-MM-DD');
        const todaysEvents = eventsByDay.get(dayKey) || [];
        const remainingEventsCount = todaysEvents.length - MAX_EVENTS_VISIBLE;

        return (
          <Box key={dayKey} sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', border: '1px solid', borderColor: 'var(--mui-palette-divider)', p: 1, height: '250px' }}>
            {/* Header do dia */}
            <Box sx={{ textAlign: 'center', mb: 1, flexShrink: 0 }}>
              <Typography variant="caption" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>{day.format('ddd')}</Typography>
              <Typography variant="h6" sx={{ lineHeight: 1.2 }}>{day.format('DD')}</Typography>
            </Box>
            {/* Lista de eventos */}
            <Box sx={{ flexGrow: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              {todaysEvents.slice(0, MAX_EVENTS_VISIBLE).map((event) => (
                <Paper key={event.id} title={event.descricao} elevation={0} sx={{ p: 0.5, bgcolor: 'var(--mui-palette-background-level1)', borderLeft: '2px solid', borderColor: 'var(--mui-palette-primary-main)', overflow: 'hidden', cursor: 'pointer' }}>
                  <Typography noWrap sx={{ fontSize: '0.7rem', fontWeight: 600 }}>{event.descricaoTipo}</Typography>
                </Paper>
              ))}
              {/* Indicador para ver mais */}
              {remainingEventsCount > 0 && (
                // 5. Adicionando o onClick ao Chip
                <Chip onClick={() => handleDayClick(day)} label={`+ ${remainingEventsCount}`} size="small" sx={{ mt: 'auto', alignSelf: 'center', cursor: 'pointer' }} />
              )}
            </Box>
          </Box>
        );
      })}
    </Box>
  );
}
// src/components/dashboard/WeeklyCalendar.tsx
'use client';

import React, { useState } from 'react';
import { Box, Typography, Paper, Chip, IconButton } from '@mui/material';
import {
  Timeline, TimelineItem, TimelineSeparator, TimelineConnector,
  TimelineContent, TimelineDot, TimelineOppositeContent
} from '@mui/lab';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { motion, AnimatePresence } from 'framer-motion';
import dayjs from 'dayjs';
import 'dayjs/locale/pt-br';

import type { ApiEvent } from '@/services/eventos.service';

dayjs.locale('pt-br');

interface WeeklyCalendarProps {
  events: ApiEvent[];
}

const MAX_EVENTS_VISIBLE = 5;

const variants = {
  initial: { opacity: 0, x: 50 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -50 },
  transition: { duration: 0.4 },
};

export default function WeeklyCalendar({ events }: WeeklyCalendarProps) {
  const [viewMode, setViewMode] = useState<'week' | 'day'>('week');
  const [selectedDay, setSelectedDay] = useState<dayjs.Dayjs | null>(null);

  const today = dayjs();
  const startOfWeek = today.startOf('week').add(1, 'day');
  const weekDays = Array.from({ length: 7 }, (_, i) => startOfWeek.add(i, 'day'));

  const eventsByDay = events.reduce((map, event) => {
    const key = dayjs(event.dataHoraInicio).format('YYYY-MM-DD');
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(event);
    return map;
  }, new Map<string, ApiEvent[]>());

  const handleDayClick = (day: dayjs.Dayjs) => {
    setSelectedDay(day);
    setViewMode('day');
  };

  const handleBackToWeekView = () => {
    setSelectedDay(null);
    setViewMode('week');
  };

  return (
    <AnimatePresence mode="wait">
      {viewMode === 'day' && selectedDay ? (
        <motion.div
          key="day"
          initial="initial"
          animate="animate"
          exit="exit"
          transition={variants.transition}
          variants={variants}
        >
          <Paper elevation={3} sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <IconButton onClick={handleBackToWeekView} sx={{ mr: 1 }}>
                <ArrowBackIcon />
              </IconButton>
              <Typography variant="h6">
                Agenda para {selectedDay.format('dddd, DD [de] MMMM')}
              </Typography>
            </Box>

            <Timeline position="right" sx={{ p: 0 }}>
              {(() => {
                const dayKey = selectedDay.format('YYYY-MM-DD');
                const todaysEvents = (eventsByDay.get(dayKey) || []).sort((a, b) =>
                  dayjs(a.dataHoraInicio).diff(dayjs(b.dataHoraInicio))
                );

                const grouped = todaysEvents.reduce((map, event) => {
                  const time = dayjs(event.dataHoraInicio).format('HH:mm');
                  if (!map.has(time)) map.set(time, []);
                  map.get(time)!.push(event);
                  return map;
                }, new Map<string, ApiEvent[]>());

                const groupedArray = Array.from(grouped.entries());

                if (!groupedArray.length) {
                  return <Typography sx={{ textAlign: 'center', py: 4 }}>Nenhum evento agendado.</Typography>;
                }

                return groupedArray.map(([time, items], i) => (
                  <TimelineItem key={time}>
                    <TimelineOppositeContent sx={{ flex: 0.2, minWidth: 80 }}>
                      <Typography variant="subtitle2" color="text.secondary">{time}</Typography>
                    </TimelineOppositeContent>
                    <TimelineSeparator>
                      <TimelineDot color="primary" />
                      {i < groupedArray.length - 1 && <TimelineConnector />}
                    </TimelineSeparator>
                    <TimelineContent>
                      {items.map(event => (
                        <Paper key={event.id} elevation={1} sx={{
                          p: 1.5,
                          mb: 1,
                          bgcolor: 'background.paper',
                          borderLeft: '3px solid',
                          borderColor: 'primary.main'
                        }}>
                          <Typography sx={{ fontWeight: 600 }}>{event.descricaoTipo}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {event.descricao.split('\n')[0]}
                          </Typography>
                        </Paper>
                      ))}
                    </TimelineContent>
                  </TimelineItem>
                ));
              })()}
            </Timeline>
          </Paper>
        </motion.div>
      ) : (
        <motion.div
          key="week"
          initial="initial"
          animate="animate"
          exit="exit"
          transition={variants.transition}
          variants={variants}
        >
          <Box sx={{ display: 'flex', width: '100%' }}>
            {weekDays.map((day) => {
              const key = day.format('YYYY-MM-DD');
              const dayEvents = eventsByDay.get(key) || [];
              const remaining = dayEvents.length - MAX_EVENTS_VISIBLE;

              return (
                <Box
                  key={key}
                  sx={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    border: '1px solid',
                    borderColor: 'divider',
                    p: 1,
                    height: 250,
                    minWidth: 0,
                  }}
                >
                  <Box sx={{ textAlign: 'center', mb: 1 }}>
                    <Typography variant="caption" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>
                      {day.format('ddd')}
                    </Typography>
                    <Typography variant="h6">{day.format('DD')}</Typography>
                  </Box>

                  <Box sx={{ flexGrow: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    {dayEvents.slice(0, MAX_EVENTS_VISIBLE).map((event) => (
                      <Paper
                        key={event.id}
                        title={event.descricao}
                        onClick={() => handleDayClick(day)}
                        elevation={0}
                        sx={{
                          p: 0.5,
                          bgcolor: 'background.level1',
                          borderLeft: '2px solid',
                          borderColor: 'primary.main',
                          cursor: 'pointer',
                          '&:hover': { bgcolor: 'background.default' },
                        }}
                      >
                        <Typography noWrap sx={{ fontSize: '0.7rem', fontWeight: 600 }}>
                          {event.descricaoTipo}
                        </Typography>
                      </Paper>
                    ))}
                    {remaining > 0 && (
                      <Chip
                        label={`+ ${remaining}`}
                        onClick={() => handleDayClick(day)}
                        size="small"
                        sx={{ mt: 'auto', alignSelf: 'center', cursor: 'pointer' }}
                      />
                    )}
                  </Box>
                </Box>
              );
            })}
          </Box>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

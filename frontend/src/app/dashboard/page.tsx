'use client'; 

import { useState, useEffect } from 'react';
import { Box, CircularProgress, Alert } from '@mui/material';

import WeeklyCalendar from '@/components/dashboard/overview/WeeklyCalendar';
import { getEventosDaSemana, type ApiEvent } from '@/services/eventos.service';
import { getHighImpactPropositions, type ApiProposition } from '@/services/proposicoes.service';
import HighImpactPropositionsCard from '@/components/dashboard/overview/HighImpactPropositionsCard';

function DashboardPage() {
  const [eventos, setEventos] = useState<ApiEvent[]>([]);
  const [propositions, setPropositions] = useState<ApiProposition[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEventos = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const [eventosData, proposicoesData] = await Promise.all([
          getEventosDaSemana(),
          getHighImpactPropositions()
        ]);
        setEventos(eventosData);
        setPropositions(proposicoesData.proposicoes);
      } catch (e: any) {
        setError(e.message || "Ocorreu um erro desconhecido.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchEventos();
  }, []);

  return (
    <Box sx={{ width: '100%' }}>
      {isLoading && <CircularProgress />}
      {error && <Alert severity="error">Falha ao carregar dados: {error}</Alert>}
      {!isLoading && !error && (
        <>
          <WeeklyCalendar events={eventos} />
          <HighImpactPropositionsCard propositions={propositions} />
        </>
      )}
    </Box>
  );
}

export default DashboardPage;

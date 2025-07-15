'use client';

import { useState, useEffect } from 'react';
import { Box, CircularProgress, Alert, Grid } from '@mui/material'; // Ensure Grid is imported

import WeeklyCalendar from '@/components/dashboard/overview/WeeklyCalendar';
import ImpactTabs from '@/components/dashboard/overview/ImpactTabs';
import { getEventosDaSemana, type ApiEvent } from '@/services/eventos.service';
import { getRankedPropositions } from '@/services/proposicoes.service';
import { getRankedDeputies, type ApiRankedDeputy } from '@/services/deputados.service';
import type { ApiProposal as ApiProposition } from '@/types/proposition';

function DashboardPage() {
  const [eventos, setEventos] = useState<ApiEvent[]>([]);
  const [dailyPropositions, setDailyPropositions] = useState<ApiProposition[]>([]);
  const [monthlyPropositions, setMonthlyPropositions] = useState<ApiProposition[]>([]);
  const [monthlyDeputies, setMonthlyDeputies] = useState<ApiRankedDeputy[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const [
          eventosData, 
          dailyPropositionsData, 
          monthlyPropositionsData,
          monthlyDeputiesData
        ] = await Promise.all([
          getEventosDaSemana(),
          getRankedPropositions('daily'),
          getRankedPropositions('monthly'),
          getRankedDeputies()
        ]);

        setEventos(eventosData);
        setDailyPropositions(dailyPropositionsData);
        setMonthlyPropositions(monthlyPropositionsData);
        setMonthlyDeputies(monthlyDeputiesData);

      } catch (e: any) {
        setError(e.message || "Ocorreu um erro desconhecido.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <Box sx={{ width: '100%' }}>
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}
      {error && <Alert severity="error">Falha ao carregar dados: {error}</Alert>}
      {!isLoading && !error && (
        // --- CORRECTED GRID LAYOUT ---
        // We use a Grid container with vertical spacing.
        // Each direct child is a Grid item that spans the full width (xs={12}).
        <Grid container spacing={3}>
          <Grid item xs={12} sx={{ width: '100%' }} >
            <WeeklyCalendar events={eventos} />
          </Grid>
          <Grid item xs={12} sx={{ width: '100%' }}>
            <ImpactTabs 
              dailyPropositions={dailyPropositions}
              monthlyPropositions={monthlyPropositions}
              monthlyDeputies={monthlyDeputies}
            />
          </Grid>
        </Grid>
      )}
    </Box>
  );
}

export default DashboardPage;
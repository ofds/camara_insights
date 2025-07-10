// src/app/dashboard/page.tsx
'use client'; 

import { useState, useEffect } from 'react';
import { Box, CircularProgress, Alert } from '@mui/material';

// Componente e serviço que já criamos
import WeeklyCalendar from '@/components/dashboard/WeeklyCalendar';
import { getEventosDaSemana, type ApiEvent } from '@/services/eventos.service';

function DashboardPage() {
  const [eventos, setEventos] = useState<ApiEvent[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // A lógica para buscar os dados continua a mesma
    const fetchEventos = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const dados = await getEventosDaSemana();
        setEventos(dados);
      } catch (e: any) {
        setError(e.message || "Ocorreu um erro desconhecido.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchEventos();
  }, []);

  // O retorno agora é muito mais simples
  return (
    <Box sx={{ width: '100%' }}> {/* Garante que o contêiner principal ocupe toda a largura */}
      {isLoading && <CircularProgress />}
      {error && <Alert severity="error">Falha ao carregar dados: {error}</Alert>}
      {!isLoading && !error && (
        <WeeklyCalendar events={eventos} />
      )}
    </Box>
  );
}

export default DashboardPage;
'use client';

// Import only the main heatmap CSS
import 'cal-heatmap/cal-heatmap.css';

import { Box, Card, CardContent, CardHeader, Divider, Typography, CircularProgress } from '@mui/material';
import CalHeatmap from 'cal-heatmap';
// Import the Tooltip plugin
import Tooltip from 'cal-heatmap/plugins/Tooltip';
import { useEffect, useRef, useState } from 'react';

import { getDeputadoProposalActivity } from '@/services/deputados.service';

interface ProposalActivityHeatmapProps {
  deputadoId: number;
}

const ProposalActivityHeatmap = ({ deputadoId }: ProposalActivityHeatmapProps) => {
  const heatmapRef = useRef<HTMLDivElement>(null);
  const calHeatmapInstance = useRef<CalHeatmap | null>(null);
  const [status, setStatus] = useState<'loading' | 'error' | 'success' | 'empty'>('loading');

  useEffect(() => {
    // --- FIX: A more robust cleanup and effect logic ---
    const currentHeatmapRef = heatmapRef.current;
    if (!currentHeatmapRef) {
      return;
    }

    // Flag to prevent race conditions
    let isSubscribed = true;

    const fetchAndRenderActivity = async () => {
      // Don't run if the component has been unmounted
      if (!isSubscribed) return;
      
      setStatus('loading');
      
      try {
        const data = await getDeputadoProposalActivity(deputadoId);
        
        if (!isSubscribed) return;

        if (!data.activity || data.activity.length === 0) {
          setStatus('empty');
          return;
        }

        // --- Critical Step: Ensure the container is empty before painting ---
        currentHeatmapRef.innerHTML = '';

        const processedData = data.activity.reduce((acc: { [key: string]: number }, timestamp: string) => {
          const day = new Date(timestamp).toISOString().slice(0, 10);
          acc[day] = (acc[day] || 0) + 1;
          return acc;
        }, {});

        const calendarData = Object.keys(processedData).map(date => ({
          date: date,
          value: processedData[date]
        }));

        // Create and store the new instance
        calHeatmapInstance.current = new CalHeatmap();

        // Paint the heatmap
        calHeatmapInstance.current.paint({
          data: { source: calendarData, x: 'date', y: 'value' },
          date: { start: new Date(new Date().setFullYear(new Date().getFullYear() - 1)) },
          range: 12,
          scale: {
            color: {
              type: 'threshold',
              range: ['#c6e48b', '#7bc96f', '#239a3b', '#196127'],
              domain: [1, 2, 4, 6],
            },
          },
          domain: { type: 'month', gutter: 4, label: { text: 'MMM', textAlign: 'start', position: 'top' } },
          subDomain: { type: 'ghDay', radius: 2, width: 11, height: 11, gutter: 4 },
          itemSelector: currentHeatmapRef,
        }, [
          [
            Tooltip,
            {
              text: function (timestamp, value, dayjsDate) {
                const count = value || 0;
                if (count === 0) {
                  return 'Nenhuma proposta neste dia';
                }
                const plural = count > 1 ? 's' : '';
                const dateString = dayjsDate.format('D [de] MMMM [de] YYYY');
                return `${count} proposta${plural} em ${dateString}`;
              },
            },
          ],
        ]);
        setStatus('success');
      } catch (error) {
        if (isSubscribed) {
          console.error("Error fetching or rendering heatmap:", error);
          setStatus('error');
        }
      }
    };

    fetchAndRenderActivity();

    // --- Definitive Cleanup Function ---
    return () => {
      isSubscribed = false;
      if (calHeatmapInstance.current) {
        // Use a timeout of 0 to push the destroy call to the end of the event queue.
        // This ensures that any pending paint operations are finished before we destroy.
        setTimeout(() => {
          if (calHeatmapInstance.current) {
            calHeatmapInstance.current.destroy();
            calHeatmapInstance.current = null;
          }
        }, 0);
      }
    };
  }, [deputadoId]);

  return (
    <Card sx={{
      '& .ch-tooltip': {
        background: '#374151',
        color: 'white',
        padding: '6px 12px',
        borderRadius: '4px',
        fontSize: '0.875rem',
        zIndex: 9999,
        boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
        '&[data-popper-arrow]::before': {
          display: 'none',
        },
      },
    }}>
      <CardHeader title="Atividade de Propostas no Último Ano" />
      <Divider />
      <CardContent sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 150, overflowX: 'auto', p: 3 }}>
        {status === 'loading' && <CircularProgress />}
        {status === 'error' && <Typography color="error">Não foi possível carregar os dados.</Typography>}
        {status === 'empty' && (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 4 }}>
            Nenhuma atividade de proposta encontrada para este deputado no último ano.
          </Typography>
        )}
        <Box ref={heatmapRef} sx={{ display: status === 'success' ? 'block' : 'none' }} />
      </CardContent>
    </Card>
  );
};

export default ProposalActivityHeatmap;
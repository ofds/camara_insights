'use client';

import * as React from 'react';
import { useParams } from 'next/navigation';
import {
  Alert,
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  Stack,
  Step,
  StepContent,
  StepLabel,
  Stepper,
  Typography,
  Link,
  Button,
  ListItemButton,
} from '@mui/material';
import { ArrowLeft as ArrowLeftIcon } from '@phosphor-icons/react';
import dayjs from 'dayjs';

import type { ProposalDetails } from '@/services/proposicoes.service';
import { getPropositionDetailsById } from '@/services/proposicoes.service';
import { paths } from '@/paths';

// Componente para a linha do tempo de tramitações
function TramitacoesStepper({ tramitacoes }: { tramitacoes: any[] }) {
  if (!tramitacoes || tramitacoes.length === 0) {
    return <Typography>Nenhuma tramitação encontrada.</Typography>;
  }

  // Ordena as tramitações da mais antiga para a mais recente
  const sortedTramitacoes = [...tramitacoes].sort((a, b) => new Date(a.dataHora).getTime() - new Date(b.dataHora).getTime());

  return (
    <Stepper orientation="vertical">
      {sortedTramitacoes.map((tramitacao, index) => (
        <Step key={index} active>
          <StepLabel
            optional={<Typography variant="caption">{dayjs(tramitacao.dataHora).format('DD/MM/YYYY HH:mm')}</Typography>}
          >
            {tramitacao.descricaoSituacao} ({tramitacao.siglaOrgao})
          </StepLabel>
          <StepContent>
            <Typography>{tramitacao.despacho}</Typography>
          </StepContent>
        </Step>
      ))}
    </Stepper>
  );
}

// Componente principal da página
export default function ProposalDetailsPage(): React.JSX.Element {
  const { id } = useParams<{ id: string }>();
  const [details, setDetails] = React.useState<ProposalDetails | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (id) {
      const fetchDetails = async () => {
        try {
          setLoading(true);
          const data = await getPropositionDetailsById(Number(id));
          setDetails(data);
        } catch (err: any) {
          setError(err.message || 'Falha ao carregar detalhes da proposta.');
        } finally {
          setLoading(false);
        }
      };
      fetchDetails();
    }
  }, [id]);

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}><CircularProgress /></Box>;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!details) {
    return <Alert severity="warning">Detalhes da proposta não encontrados.</Alert>;
  }

  const { base_data: proposal, autores, relacionadas, temas, tramitacoes, votacoes } = details;

  return (
    <Stack spacing={3}>
      {/* Cabeçalho */}
      <Stack direction="row" spacing={3} sx={{ alignItems: 'center' }}>
        <Button component="a" href={paths.dashboard.proposals} startIcon={<ArrowLeftIcon />} variant="outlined">
          Voltar
        </Button>
        <Typography variant="h4">{`${proposal.siglaTipo} ${proposal.numero}/${proposal.ano}`}</Typography>
      </Stack>

      {/* Grid Principal */}
      <Grid container spacing={3}>
        {/* Coluna da Esquerda (Informações Principais e Tramitação) */}
        <Grid item xs={12} md={8}>
          <Stack spacing={3}>
            {/* Card de Informações Gerais */}
            <Card>
              <CardHeader title="Informações Gerais" />
              <CardContent>
                <Typography variant="h6" gutterBottom>Ementa</Typography>
                <Typography variant="body1" paragraph>{proposal.ementa}</Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>Resumo Analítico (IA)</Typography>
                <Typography variant="body1" paragraph>
                  {proposal.summary || 'Resumo não disponível.'}
                </Typography>
                 <Typography variant="body2" color="text.secondary" paragraph>
                   {proposal.ementaDetalhada}
                 </Typography>
              </CardContent>
              <Divider />
               <CardContent>
                 <Typography variant="h6" gutterBottom>Documentos</Typography>
                 <Link href={proposal.urlInteiroTeor} target="_blank" rel="noopener noreferrer">Ver Inteiro Teor da Proposição</Link>
               </CardContent>
            </Card>

            {/* Card de Tramitações */}

          </Stack>
        </Grid>

        {/* Coluna da Direita (Metadados e Listas) */}
        <Grid item xs={12} md={4}>
          <Stack spacing={3}>
             {/* Card de Metadados */}
            <Card>
                <CardHeader title="Metadados" />
                <CardContent>
                    <Typography variant="body2"><strong>Data:</strong> {dayjs(proposal.dataApresentacao).format('DD/MM/YYYY')}</Typography>
                    <Typography variant="body2"><strong>Situação:</strong> {proposal.statusProposicao_descricaoSituacao}</Typography>
                    <Typography variant="body2"><strong>Escopo (IA):</strong> {proposal.scope || 'N/A'}</Typography>
                    <Typography variant="body2"><strong>Magnitude (IA):</strong> {proposal.magnitude || 'N/A'}</Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      <strong>Score de Impacto (IA):</strong>
                      <Chip label={proposal.impact_score?.toFixed(0)} color="primary" sx={{ ml: 1 }} />
                    </Typography>
                </CardContent>
            </Card>

            {/* Card de Autores */}
<Card>
  <CardHeader title="Autores" />
  <List dense>
    {autores.length > 0 ? (
      autores.map((autor) => {
        const deputyId = autor.uri.split('/').pop();
        return (
          <ListItemButton key={autor.uri} component="a" href={paths.dashboard.deputado(deputyId)}>
            <ListItemText primary={autor.nome} secondary={autor.tipo} />
          </ListItemButton>
        );
      })
    ) : (
      <ListItem>
        <ListItemText primary="Nenhum autor encontrado." />
      </ListItem>
    )}
  </List>
</Card>

            {/* Card de Temas */}
            <Card>
              <CardHeader title="Temas" />
              <CardContent>
                {temas.length > 0 ? (
                    <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                      {temas.map(tema => <Chip key={tema.codTema} label={tema.tema} />)}
                    </Stack>
                ) : <Typography variant="body2">Nenhum tema associado.</Typography>}
              </CardContent>
            </Card>

            {/* Card de Votações */}
            <Card>
              <CardHeader title="Votações Relacionadas" />
               <List dense>
                {votacoes.length > 0 ? votacoes.map(votacao => (
                  <ListItem key={votacao.id}>
                    <ListItemText primary={votacao.siglaOrgao} secondary={`${dayjs(votacao.data).format('DD/MM/YYYY')} - ${votacao.descricao}`} />
                  </ListItem>
                )) : <ListItem><ListItemText primary="Nenhuma votação encontrada." /></ListItem>}
              </List>
            </Card>
            
             {/* Card de Proposições Relacionadas */}
            <Card>
              <CardHeader title="Proposições Relacionadas" />
               <List dense>
                {relacionadas.length > 0 ? relacionadas.map(rel => (
                  <ListItem key={rel.id} button component="a" href={`/dashboard/proposals/${rel.id}`}>
                    <ListItemText primary={`${rel.siglaTipo} ${rel.numero}/${rel.ano}`} secondary={rel.ementa.substring(0, 100) + '...'} />
                  </ListItem>
                )) : <ListItem><ListItemText primary="Nenhuma proposição relacionada." /></ListItem>}
              </List>
            </Card>

                        <Card>
              <CardHeader title="Histórico de Tramitação" />
              <CardContent>
                <TramitacoesStepper tramitacoes={tramitacoes} />
              </CardContent>
            </Card>

            
          </Stack>
        </Grid>
      </Grid>
    </Stack>
  );
}

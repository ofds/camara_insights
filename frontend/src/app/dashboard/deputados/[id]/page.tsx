// frontend/src/app/dashboard/deputados/[id]/page.tsx

'use client';

import * as React from 'react';
import { notFound, useParams } from 'next/navigation';
import {
  Avatar,
  Box,
  Card,
  CardContent,
  CardHeader,
  Container,
  Divider,
  Grid,
  Link,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography,
  CircularProgress,
  Alert
} from '@mui/material';
import { paths } from '@/paths';
import { getDeputadoById } from '@/services/deputados.service';
import type { DeputadoDetalhado, Proposicao } from '@/types/deputado';

// Helper component to display a piece of information
function InfoItem({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <Grid item xs={12} md={6}>
      <Typography variant="subtitle2" gutterBottom>
        {label}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {value || 'Não informado'}
      </Typography>
    </Grid>
  );
}

// Component to display the list of propositions
function ProposicoesList({ proposicoes }: { proposicoes: Proposicao[] }) {
  if (!proposicoes || proposicoes.length === 0) {
    return <Typography>Nenhuma proposição encontrada para este deputado.</Typography>;
  }

  return (
    <Card>
      <CardHeader title="Proposições de Autoria" />
      <Divider />
      <List disablePadding>
        {proposicoes.map((prop, index) => (
          <React.Fragment key={prop.id}>
            <ListItem>
              <ListItemText
                primary={
                  <Link href={paths.dashboard.proposals_id(prop.id)} underline="hover">
                    {`${prop.siglaTipo} ${prop.numero}/${prop.ano}`}
                  </Link>
                }
                secondary={prop.ementa}
                secondaryTypographyProps={{
                    noWrap: true,
                    textOverflow: 'ellipsis',
                    overflow: 'hidden',
                    component: 'p',
                }}
              />
            </ListItem>
            {index < proposicoes.length - 1 && <Divider component="li" />}
          </React.Fragment>
        ))}
      </List>
    </Card>
  );
}


export default function DeputadoDetailPage(): React.JSX.Element {
  const { id } = useParams<{ id: string }>();
  const [deputado, setDeputado] = React.useState<DeputadoDetalhado | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (id) {
      const fetchDeputado = async () => {
        try {
          setLoading(true);
          const data = await getDeputadoById(parseInt(id, 10));
          setDeputado(data);
        } catch (err) {
          setError((err as Error).message);
          if ((err as Error).message.includes('não encontrado')) {
            notFound();
          }
        } finally {
          setLoading(false);
        }
      };

      fetchDeputado();
    }
  }, [id]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!deputado) {
    return notFound();
  }

  return (
    <Box component="main" sx={{ flexGrow: 1, py: 8 }}>
      <Container maxWidth="lg">
        <Stack spacing={4}>
          {/* Header */}
          <Stack spacing={3} direction="row" alignItems="center">
            <Avatar src={deputado.ultimoStatus_urlFoto} sx={{ width: 100, height: 100 }} />
            <Box>
              <Typography variant="h4">{deputado.ultimoStatus_nomeEleitoral}</Typography>
              <Typography variant="body1" color="text.secondary">
                {deputado.nomeCivil}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {deputado.ultimoStatus_siglaPartido} - {deputado.ultimoStatus_siglaUf}
              </Typography>
            </Box>
          </Stack>

          {/* Personal and Status Info */}
          <Card>
            <CardHeader title="Informações Pessoais e de Mandato" />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <InfoItem label="Nome Civil" value={deputado.nomeCivil} />
                <InfoItem label="CPF" value={deputado.cpf} />
                <InfoItem label="Email" value={<Link href={`mailto:${deputado.ultimoStatus_email}`}>{deputado.ultimoStatus_email}</Link>} />
                <InfoItem label="Sexo" value={deputado.sexo === 'M' ? 'Masculino' : 'Feminino'} />
                <InfoItem label="Data de Nascimento" value={deputado.dataNascimento ? new Date(deputado.dataNascimento).toLocaleDateString('pt-BR') : null} />
                <InfoItem label="Município de Nascimento" value={`${deputado.municipioNascimento} - ${deputado.ufNascimento}`} />
                <InfoItem label="Escolaridade" value={deputado.escolaridade} />
                <InfoItem label="Situação" value={deputado.ultimoStatus_situacao} />
                <InfoItem label="Condição Eleitoral" value={deputado.ultimoStatus_condicaoEleitoral} />
                <InfoItem label="Website" value={deputado.urlWebsite ? <Link href={deputado.urlWebsite} target="_blank" rel="noopener noreferrer">Visitar</Link> : null} />
              </Grid>
            </CardContent>
          </Card>

          {/* Gabinete Info */}
          <Card>
            <CardHeader title="Gabinete" />
            <Divider />
            <CardContent>
               <Grid container spacing={3}>
                  <InfoItem label="Nome" value={deputado.ultimoStatus_gabinete_nome} />
                  <InfoItem label="Prédio" value={deputado.ultimoStatus_gabinete_predio} />
                  <InfoItem label="Sala" value={deputado.ultimoStatus_gabinete_sala} />
                  <InfoItem label="Andar" value={deputado.ultimoStatus_gabinete_andar} />
                  <InfoItem label="Telefone" value={deputado.ultimoStatus_gabinete_telefone ? <Link href={`tel:${deputado.ultimoStatus_gabinete_telefone}`}>{deputado.ultimoStatus_gabinete_telefone}</Link> : null} />
                  <InfoItem label="Email do Gabinete" value={deputado.ultimoStatus_gabinete_email ? <Link href={`mailto:${deputado.ultimoStatus_gabinete_email}`}>{deputado.ultimoStatus_gabinete_email}</Link> : null} />
               </Grid>
            </CardContent>
          </Card>
          
          {/* Proposições */}
          {deputado.proposicoes && <ProposicoesList proposicoes={deputado.proposicoes} />}

        </Stack>
      </Container>
    </Box>
  );
}
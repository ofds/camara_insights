// frontend/src/components/dashboard/overview/ImpactTabs.tsx

'use client';

import { useState, SyntheticEvent } from 'react';
import {
  Box,
  Tab,
  Tabs,
  Card,
  CardContent
} from '@mui/material';
import { type ApiProposition } from '@/types/proposition';
import { type ApiRankedDeputy } from '@/types/deputado';
import PropositionsList from './PropositionsList';
import DeputiesList from './DeputiesList';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`impact-tabpanel-${index}`}
      aria-labelledby={`impact-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3, minHeight: '450px' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

interface ImpactTabsProps {
  dailyPropositions: ApiProposition[];
  monthlyPropositions: ApiProposition[];
  monthlyDeputies: ApiRankedDeputy[];
  municipalPropositions: ApiProposition[];
  estadualPropositions: ApiProposition[];
}

export default function ImpactTabs({
  dailyPropositions,
  monthlyPropositions,
  monthlyDeputies,
  municipalPropositions,
  estadualPropositions
}: ImpactTabsProps) {
  const [value, setValue] = useState(0);

  const handleChange = (_event: SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Card elevation={3} sx={{ width: '100%' }}>
        <CardContent>
          <Box sx={{ width: '100%' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs
                value={value}
                onChange={handleChange}
                aria-label="abas de impacto"
                variant="scrollable"
                scrollButtons="auto"
              >
                <Tab label="Impacto Hoje" id="impact-tab-0" aria-controls="impact-tabpanel-0" />
                <Tab label="Impacto no Mês" id="impact-tab-1" aria-controls="impact-tabpanel-1" />
                <Tab label="Deputados do Mês" id="impact-tab-2" aria-controls="impact-tabpanel-2" />
                <Tab label="Impacto Municipal" id="impact-tab-3" aria-controls="impact-tabpanel-3" />
                <Tab label="Impacto Estadual" id="impact-tab-4" aria-controls="impact-tabpanel-4" />
              </Tabs>
            </Box>

            <TabPanel value={value} index={0}>
              <PropositionsList propositions={dailyPropositions} />
            </TabPanel>
            <TabPanel value={value} index={1}>
              <PropositionsList propositions={monthlyPropositions} />
            </TabPanel>
            <TabPanel value={value} index={2}>
              <DeputiesList deputies={monthlyDeputies} />
            </TabPanel>
            <TabPanel value={value} index={3}>
                <PropositionsList propositions={municipalPropositions} />
            </TabPanel>
            <TabPanel value={value} index={4}>
                <PropositionsList propositions={estadualPropositions} />
            </TabPanel>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
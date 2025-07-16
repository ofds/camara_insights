import type { NavItemConfig } from '@/types/nav';
import { paths } from '@/paths';

export const navItems = [
  { key: 'novidades', title: 'Novidades', href: paths.dashboard.overview, icon: 'chart-pie' },
  { key: 'propostas', title: 'Propostas', href: paths.dashboard.proposals, icon: 'users' },
  { key: 'deputados', title: 'Deputados', href: paths.dashboard.deputados, icon: 'users' }, // Add this line
  { key: 'transparency', title: 'Transparência', href: paths.dashboard.transparency, icon: 'plugs-connected' },
  { key: 'integrations', title: 'Integrations', href: paths.dashboard.integrations, icon: 'plugs-connected' },
  { key: 'settings', title: 'Settings', href: paths.dashboard.settings, icon: 'gear-six' },
  { key: 'account', title: 'Account', href: paths.dashboard.account, icon: 'user' },
  { key: 'error', title: 'Error', href: paths.errors.notFound, icon: 'x-square' },
] satisfies NavItemConfig[];

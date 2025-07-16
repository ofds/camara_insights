import type { Icon } from '@phosphor-icons/react/dist/lib/types';
import { ChartPieIcon } from '@phosphor-icons/react/dist/ssr/ChartPie';
import { EyeIcon } from '@phosphor-icons/react/dist/ssr/Eye';
import { FileTextIcon } from '@phosphor-icons/react/dist/ssr/FileText';
import { GavelIcon } from '@phosphor-icons/react/dist/ssr/Gavel';
import { GearSixIcon } from '@phosphor-icons/react/dist/ssr/GearSix';
import { NewspaperIcon } from '@phosphor-icons/react/dist/ssr/Newspaper';
import { PlugsConnectedIcon } from '@phosphor-icons/react/dist/ssr/PlugsConnected';
import { UserIcon } from '@phosphor-icons/react/dist/ssr/User';
import { UsersIcon } from '@phosphor-icons/react/dist/ssr/Users';
import { XSquare } from '@phosphor-icons/react/dist/ssr/XSquare';

export const navIcons = {
  'chart-pie': ChartPieIcon,
  eye: EyeIcon,
  'file-text': FileTextIcon,
  gavel: GavelIcon,
  'gear-six': GearSixIcon,
  newspaper: NewspaperIcon,
  'plugs-connected': PlugsConnectedIcon,
  'x-square': XSquare,
  user: UserIcon,
  users: UsersIcon,
} as Record<string, Icon>;
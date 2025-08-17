import { Biotech, ViewColumn, Search } from '@mui/icons-material';
import type { ModuleDefinition } from './shared/types/module';

// Import modules
import { AntibodyAnnotationTool } from './antibody-annotation/components/AntibodyAnnotationTool';
import { MSAViewerTool } from './msa-viewer/components/MSAViewerTool';
import { BlastViewerTool } from './blast-viewer/components/BlastViewerTool';

export const MODULES: ModuleDefinition[] = [
  {
    id: 'antibody-annotation',
    name: 'Antibody Sequence Annotation',
    description: 'Analyze and annotate individual antibody sequences',
    icon: Biotech,
    component: AntibodyAnnotationTool,
    route: '/antibody-annotation',
    enabled: true,
    order: 1
  },
  {
    id: 'blast-viewer',
    name: 'BLAST Sequence Search',
    description: 'Search sequences against databases and perform antibody analysis',
    icon: Search,
    component: BlastViewerTool,
    route: '/blast-viewer',
    enabled: true,
    order: 2
  },
  {
    id: 'msa-viewer',
    name: 'Multiple Sequence Alignment',
    description: 'Create and visualize MSA with region annotations',
    icon: ViewColumn,
    component: MSAViewerTool,
    route: '/msa-viewer',
    enabled: true,
    order: 3
  }
];

export const getModuleById = (id: string): ModuleDefinition | undefined => {
  return MODULES.find(module => module.id === id);
};

export const getEnabledModules = (): ModuleDefinition[] => {
  return MODULES.filter(module => module.enabled);
};

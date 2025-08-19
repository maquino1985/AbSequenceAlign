import { Biotech, ViewColumn, Search, Science } from '@mui/icons-material';
import type { ModuleDefinition } from './shared/types/module';

// Import modules
import { AntibodyAnnotationTool } from './antibody-annotation/components/AntibodyAnnotationTool';
import { MSAViewerTool } from './msa-viewer/components/MSAViewerTool';
import { BlastViewerTool } from './blast-viewer/components/BlastViewerTool';
import { IgBlastTool } from './antibody-annotation/components/IgBlastTool';

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
    id: 'igblast-tool',
    name: 'IgBLAST Analysis',
    description: 'Perform immunoglobulin gene analysis with database selection',
    icon: Science,
    component: IgBlastTool,
    route: '/igblast-tool',
    enabled: true,
    order: 2
  },
  {
    id: 'blast-viewer',
    name: 'BLAST Sequence Search',
    description: 'Search sequences against databases and perform antibody analysis',
    icon: Search,
    component: BlastViewerTool,
    route: '/blast-viewer',
    enabled: true,
    order: 3
  },
  {
    id: 'msa-viewer',
    name: 'Multiple Sequence Alignment',
    description: 'Create and visualize MSA with region annotations',
    icon: ViewColumn,
    component: MSAViewerTool,
    route: '/msa-viewer',
    enabled: true,
    order: 4
  }
];

export const getModuleById = (id: string): ModuleDefinition | undefined => {
  return MODULES.find(module => module.id === id);
};

export const getEnabledModules = (): ModuleDefinition[] => {
  return MODULES.filter(module => module.enabled);
};

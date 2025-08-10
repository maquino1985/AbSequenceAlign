import { Biotech, ViewColumn, Analytics, Settings } from '@mui/icons-material';

export const DEFAULT_MODULES = [
  {
    id: 'antibody-annotation',
    name: 'Antibody Annotation',
    description: 'Annotate antibody sequences with domain regions',
    icon: Biotech,
    component: () => import('../../antibody-annotation/pages/SequenceAnnotation'),
    route: '/antibody-annotation',
    enabled: true,
    order: 1,
  },
  {
    id: 'msa-viewer',
    name: 'MSA Viewer',
    description: 'Multiple sequence alignment visualization',
    icon: ViewColumn,
    component: () => import('../../msa-viewer/components/MSAViewerTool'),
    route: '/msa-viewer',
    enabled: true,
    order: 2,
  },
  {
    id: 'analysis',
    name: 'Analysis',
    description: 'Advanced sequence analysis tools',
    icon: Analytics,
    component: () => import('../../antibody-annotation/pages/SequenceAnnotation'), // Placeholder
    route: '/analysis',
    enabled: false,
    order: 3,
  },
  {
    id: 'settings',
    name: 'Settings',
    description: 'Application configuration',
    icon: Settings,
    component: () => import('../../antibody-annotation/pages/SequenceAnnotation'), // Placeholder
    route: '/settings',
    enabled: false,
    order: 4,
  },
];



export interface ModuleDefinition {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<Record<string, unknown>>;
  component: React.ComponentType<Record<string, never>>;
  route: string;
  enabled: boolean;
  order: number;
}

export interface ModuleState {
  currentModule: string;
  modules: ModuleDefinition[];
}

export interface ModuleContextType {
  modules: ModuleDefinition[];
  currentModule: string;
  setCurrentModule: (moduleId: string) => void;
  getCurrentModule: () => ModuleDefinition | undefined;
}

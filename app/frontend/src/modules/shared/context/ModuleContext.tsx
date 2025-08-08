import React, { createContext, useContext, useState, useCallback } from 'react';
import type { ModuleContextType, ModuleDefinition } from '../types/module';

const ModuleContext = createContext<ModuleContextType | undefined>(undefined);

interface ModuleProviderProps {
  children: React.ReactNode;
  modules: ModuleDefinition[];
  defaultModule?: string;
}

export const ModuleProvider: React.FC<ModuleProviderProps> = ({ 
  children, 
  modules, 
  defaultModule 
}) => {
  const [currentModule, setCurrentModuleState] = useState(
    defaultModule || modules[0]?.id || ''
  );

  const setCurrentModule = useCallback((moduleId: string) => {
    const module = modules.find(m => m.id === moduleId);
    if (module && module.enabled) {
      setCurrentModuleState(moduleId);
    }
  }, [modules]);

  const getCurrentModule = useCallback(() => {
    return modules.find(m => m.id === currentModule);
  }, [modules, currentModule]);

  const value: ModuleContextType = {
    modules,
    currentModule,
    setCurrentModule,
    getCurrentModule,
  };

  return (
    <ModuleContext.Provider value={value}>
      {children}
    </ModuleContext.Provider>
  );
};

export const useModuleContext = (): ModuleContextType => {
  const context = useContext(ModuleContext);
  if (!context) {
    throw new Error('useModuleContext must be used within a ModuleProvider');
  }
  return context;
};

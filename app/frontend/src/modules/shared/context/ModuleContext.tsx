import React, { useState, useCallback } from 'react';
import type { ModuleContextType, ModuleDefinition } from '../types/module';
import { ModuleContext } from './ModuleContextInstance';

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





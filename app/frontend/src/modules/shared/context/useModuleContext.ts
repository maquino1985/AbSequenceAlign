import { useContext } from 'react';
import type { ModuleContextType } from '../types/module';
import { ModuleContext } from './ModuleContextInstance';

export const useModuleContext = (): ModuleContextType => {
  const context = useContext(ModuleContext);
  if (!context) {
    throw new Error('useModuleContext must be used within a ModuleProvider');
  }
  return context;
};

import { createContext } from 'react';
import type { ModuleContextType } from '../types/module';

export const ModuleContext = createContext<ModuleContextType | undefined>(undefined);

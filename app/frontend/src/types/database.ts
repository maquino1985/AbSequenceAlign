/**
 * Database-related TypeScript types for the frontend
 */

export interface DatabaseOption {
  name: string;
  path: string;
  description: string;
  organism: string;
  gene_type: 'V' | 'D' | 'J' | 'C';
}

export interface DatabaseSelection {
  v_db: string;
  d_db?: string;
  j_db?: string;
  c_db?: string;
}

export interface IgBlastRequest {
  query_sequence: string;
  v_db: string;
  d_db?: string;
  j_db?: string;
  c_db?: string;
  blast_type: 'igblastn' | 'igblastp';
  use_airr_format: boolean;
}

export interface IgBlastResponse {
  success: boolean;
  result: any;
  databases_used: DatabaseSelection;
  total_hits: number;
}

export interface DatabaseDiscoveryResponse {
  success: boolean;
  databases: {
    [organism: string]: {
      [geneType: string]: DatabaseOption;
    };
  };
  organisms: string[];
  gene_types: string[];
}

export interface DatabaseValidationResponse {
  success: boolean;
  is_valid: boolean;
  db_path: string;
}

export interface DatabaseSuggestionResponse {
  success: boolean;
  suggestion: DatabaseOption;
}

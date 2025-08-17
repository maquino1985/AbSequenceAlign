/**
 * API Type Validator
 * 
 * This utility validates that API responses match the expected TypeScript interfaces.
 * It helps identify type mismatches between backend responses and frontend expectations.
 */

import type { 
  IgBlastSearchResponse, 
  BlastSearchResponse, 
  IgBlastHit, 
  BlastHit,
  AIRRRearrangement 
} from '../types/apiV2';

export interface TypeValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  missingFields: string[];
  extraFields: string[];
  typeMismatches: Array<{
    field: string;
    expected: string;
    actual: string;
    value: any;
  }>;
}

export class APITypeValidator {
  private static instance: APITypeValidator;
  
  private constructor() {}
  
  static getInstance(): APITypeValidator {
    if (!APITypeValidator.instance) {
      APITypeValidator.instance = new APITypeValidator();
    }
    return APITypeValidator.instance;
  }

  /**
   * Validate IgBLAST search response against the expected interface
   */
  validateIgBlastResponse(data: any): TypeValidationResult {
    const result: TypeValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      missingFields: [],
      extraFields: [],
      typeMismatches: []
    };

    try {
      // Check top-level structure
      this.validateRequiredFields(data, ['success', 'message', 'data'], result);
      
      if (!data.success) {
        return result; // Error responses may have different structure
      }

      // Validate data structure
      const responseData = data.data;
      this.validateRequiredFields(responseData, ['results'], result);

      if (responseData.results) {
        this.validateIgBlastResult(responseData.results, result);
      }

      // Validate optional fields
      this.validateOptionalFields(responseData, [
        'query_info', 'analysis_summary', 'total_hits', 
        'airr_result', 'summary', 'cdr3_info', 'gene_assignments'
      ], result);

      // Validate summary structure if present
      if (responseData.summary) {
        this.validateSummary(responseData.summary, result);
      }

      // Validate AIRR result if present
      if (responseData.airr_result) {
        this.validateAIRRResult(responseData.airr_result, result);
      }

      // Validate gene assignments if present
      if (responseData.gene_assignments) {
        this.validateGeneAssignments(responseData.gene_assignments, result);
      }

    } catch (error) {
      result.isValid = false;
      result.errors.push(`Validation error: ${error}`);
    }

    return result;
  }

  /**
   * Validate standard BLAST search response
   */
  validateBlastResponse(data: any): TypeValidationResult {
    const result: TypeValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      missingFields: [],
      extraFields: [],
      typeMismatches: []
    };

    try {
      // Check top-level structure
      this.validateRequiredFields(data, ['success', 'message', 'data'], result);
      
      if (!data.success) {
        return result;
      }

      // Validate data structure
      const responseData = data.data;
      this.validateRequiredFields(responseData, ['results'], result);

      if (responseData.results) {
        this.validateBlastResult(responseData.results, result);
      }

    } catch (error) {
      result.isValid = false;
      result.errors.push(`Validation error: ${error}`);
    }

    return result;
  }

  /**
   * Validate IgBLAST result structure
   */
  private validateIgBlastResult(result: any, validation: TypeValidationResult) {
    this.validateRequiredFields(result, ['blast_type', 'query_info', 'hits', 'analysis_summary', 'total_hits'], validation);

    // Validate hits array
    if (Array.isArray(result.hits)) {
      result.hits.forEach((hit: any, index: number) => {
        this.validateIgBlastHit(hit, validation, `hits[${index}]`);
      });
    } else {
      validation.errors.push('hits field must be an array');
    }

    // Validate analysis summary
    if (result.analysis_summary) {
      this.validateAnalysisSummary(result.analysis_summary, validation);
    }

    // Validate optional AIRR result
    if (result.airr_result) {
      this.validateAIRRResult(result.airr_result, validation);
    }
  }

  /**
   * Validate standard BLAST result structure
   */
  private validateBlastResult(result: any, validation: TypeValidationResult) {
    this.validateRequiredFields(result, ['blast_type', 'query_info', 'hits', 'total_hits'], validation);

    // Validate hits array
    if (Array.isArray(result.hits)) {
      result.hits.forEach((hit: any, index: number) => {
        this.validateBlastHit(hit, validation, `hits[${index}]`);
      });
    } else {
      validation.errors.push('hits field must be an array');
    }
  }

  /**
   * Validate IgBLAST hit structure
   */
  private validateIgBlastHit(hit: any, validation: TypeValidationResult, prefix: string = '') {
    const requiredFields = [
      'query_id', 'subject_id', 'identity', 'alignment_length', 
      'mismatches', 'gap_opens', 'query_start', 'query_end',
      'subject_start', 'subject_end', 'evalue', 'bit_score'
    ];

    this.validateRequiredFields(hit, requiredFields, validation, prefix);

    // Validate antibody-specific fields
    const antibodyFields = ['v_gene', 'd_gene', 'j_gene', 'c_gene', 'cdr3_sequence', 'cdr3_start', 'cdr3_end'];
    antibodyFields.forEach(field => {
      if (hit.hasOwnProperty(field)) {
        const fieldPath = prefix ? `${prefix}.${field}` : field;
        this.validateFieldType(hit[field], ['string', 'number', 'null'], fieldPath, validation);
      }
    });

    // Validate optional fields
    const optionalFields = ['productive', 'locus', 'complete_vdj', 'stop_codon', 'vj_in_frame'];
    optionalFields.forEach(field => {
      if (hit.hasOwnProperty(field)) {
        const fieldPath = prefix ? `${prefix}.${field}` : field;
        this.validateFieldType(hit[field], ['boolean', 'string', 'null'], fieldPath, validation);
      }
    });
  }

  /**
   * Validate standard BLAST hit structure
   */
  private validateBlastHit(hit: any, validation: TypeValidationResult, prefix: string = '') {
    const requiredFields = [
      'query_id', 'subject_id', 'identity', 'alignment_length', 
      'mismatches', 'gap_opens', 'query_start', 'query_end',
      'subject_start', 'subject_end', 'evalue', 'bit_score'
    ];

    this.validateRequiredFields(hit, requiredFields, validation, prefix);
  }

  /**
   * Validate analysis summary structure
   */
  private validateAnalysisSummary(summary: any, validation: TypeValidationResult) {
    const requiredFields = ['total_hits'];
    this.validateRequiredFields(summary, requiredFields, validation, 'analysis_summary');

    // Validate optional fields
    const optionalFields = [
      'best_v_gene', 'best_d_gene', 'best_j_gene', 'best_c_gene',
      'cdr3_sequence', 'cdr3_start', 'cdr3_end', 'junction_length',
      'productive_sequences', 'unique_v_genes', 'unique_d_genes', 
      'unique_j_genes', 'locus', 'fwr1_sequence', 'cdr1_sequence',
      'fwr2_sequence', 'cdr2_sequence', 'fwr3_sequence', 'junction_aa'
    ];

    optionalFields.forEach(field => {
      if (summary.hasOwnProperty(field)) {
        const fieldPath = `analysis_summary.${field}`;
        if (field.includes('_genes') && Array.isArray(summary[field])) {
          // Array of strings
          this.validateFieldType(summary[field], ['array'], fieldPath, validation);
        } else if (field.includes('_sequence') || field.includes('_gene')) {
          this.validateFieldType(summary[field], ['string', 'null'], fieldPath, validation);
        } else if (field.includes('_start') || field.includes('_end') || field.includes('_length')) {
          this.validateFieldType(summary[field], ['number', 'null'], fieldPath, validation);
        } else if (field === 'productive_sequences') {
          this.validateFieldType(summary[field], ['number'], fieldPath, validation);
        } else {
          this.validateFieldType(summary[field], ['string', 'number', 'null'], fieldPath, validation);
        }
      }
    });
  }

  /**
   * Validate AIRR result structure
   */
  private validateAIRRResult(airrResult: any, validation: TypeValidationResult) {
    this.validateRequiredFields(airrResult, ['rearrangements'], validation, 'airr_result');

    if (Array.isArray(airrResult.rearrangements)) {
      airrResult.rearrangements.forEach((rearrangement: any, index: number) => {
        this.validateAIRRRearrangement(rearrangement, validation, `airr_result.rearrangements[${index}]`);
      });
    } else {
      validation.errors.push('airr_result.rearrangements must be an array');
    }

    // Validate optional fields
    const optionalFields = ['analysis_metadata', 'total_sequences', 'productive_sequences', 'unique_v_genes', 'unique_j_genes', 'unique_d_genes'];
    this.validateOptionalFields(airrResult, optionalFields, validation, 'airr_result');
  }

  /**
   * Validate AIRR rearrangement structure
   */
  private validateAIRRRearrangement(rearrangement: any, validation: TypeValidationResult, prefix: string = '') {
    const requiredFields = ['sequence_id', 'sequence', 'locus'];
    this.validateRequiredFields(rearrangement, requiredFields, validation, prefix);

    // Validate optional fields
    const optionalFields = [
      'sequence_aa', 'productive', 'stop_codon', 'vj_in_frame', 'v_frameshift',
      'rev_comp', 'complete_vdj', 'd_frame', 'v_call', 'd_call', 'j_call', 'c_call',
      'v_sequence_start', 'v_sequence_end', 'v_germline_start', 'v_germline_end',
      'd_sequence_start', 'd_sequence_end', 'd_germline_start', 'd_germline_end',
      'j_sequence_start', 'j_sequence_end', 'j_germline_start', 'j_germline_end'
    ];

    this.validateOptionalFields(rearrangement, optionalFields, validation, prefix);

    // Validate complex nested objects
    if (rearrangement.v_alignment) {
      this.validateAlignment(rearrangement.v_alignment, validation, `${prefix}.v_alignment`);
    }
    if (rearrangement.d_alignment) {
      this.validateAlignment(rearrangement.d_alignment, validation, `${prefix}.d_alignment`);
    }
    if (rearrangement.j_alignment) {
      this.validateAlignment(rearrangement.j_alignment, validation, `${prefix}.j_alignment`);
    }
    if (rearrangement.junction_region) {
      this.validateJunctionRegion(rearrangement.junction_region, validation, `${prefix}.junction_region`);
    }
  }

  /**
   * Validate alignment structure
   */
  private validateAlignment(alignment: any, validation: TypeValidationResult, prefix: string = '') {
    const requiredFields = ['start', 'end', 'sequence_alignment', 'germline_alignment', 'score', 'identity', 'cigar', 'support'];
    this.validateRequiredFields(alignment, requiredFields, validation, prefix);

    // Validate optional fields
    const optionalFields = ['sequence_alignment_aa', 'germline_alignment_aa'];
    this.validateOptionalFields(alignment, optionalFields, validation, prefix);
  }

  /**
   * Validate junction region structure
   */
  private validateJunctionRegion(junction: any, validation: TypeValidationResult, prefix: string = '') {
    const optionalFields = [
      'junction', 'junction_aa', 'junction_length', 'junction_aa_length',
      'cdr3', 'cdr3_aa', 'cdr3_start', 'cdr3_end', 'np1', 'np1_length', 'np2', 'np2_length'
    ];

    this.validateOptionalFields(junction, optionalFields, validation, prefix);
  }

  /**
   * Validate summary structure
   */
  private validateSummary(summary: any, validation: TypeValidationResult) {
    const requiredFields = ['total_hits', 'best_identity'];
    this.validateRequiredFields(summary, requiredFields, validation, 'summary');

    if (summary.gene_assignments) {
      this.validateGeneAssignments(summary.gene_assignments, validation, 'summary.gene_assignments');
    }

    if (summary.cdr3_info) {
      this.validateCDR3Info(summary.cdr3_info, validation, 'summary.cdr3_info');
    }
  }

  /**
   * Validate gene assignments structure
   */
  private validateGeneAssignments(assignments: any, validation: TypeValidationResult, prefix: string = '') {
    const optionalFields = ['v_gene', 'd_gene', 'j_gene', 'c_gene'];
    this.validateOptionalFields(assignments, optionalFields, validation, prefix);
  }

  /**
   * Validate CDR3 info structure
   */
  private validateCDR3Info(cdr3Info: any, validation: TypeValidationResult, prefix: string = '') {
    const requiredFields = ['sequence', 'start', 'end'];
    this.validateRequiredFields(cdr3Info, requiredFields, validation, prefix);
  }

  /**
   * Validate required fields exist
   */
  private validateRequiredFields(obj: any, fields: string[], validation: TypeValidationResult, prefix: string = '') {
    fields.forEach(field => {
      const fieldPath = prefix ? `${prefix}.${field}` : field;
      if (!obj.hasOwnProperty(field)) {
        validation.missingFields.push(fieldPath);
        validation.isValid = false;
      }
    });
  }

  /**
   * Validate optional fields if they exist
   */
  private validateOptionalFields(obj: any, fields: string[], validation: TypeValidationResult, prefix: string = '') {
    fields.forEach(field => {
      if (obj.hasOwnProperty(field)) {
        const fieldPath = prefix ? `${prefix}.${field}` : field;
        // Basic type checking for optional fields
        if (obj[field] !== null && obj[field] !== undefined) {
          this.validateFieldType(obj[field], ['string', 'number', 'boolean', 'array', 'object'], fieldPath, validation);
        }
      }
    });
  }

  /**
   * Validate field type
   */
  private validateFieldType(value: any, expectedTypes: string[], fieldPath: string, validation: TypeValidationResult) {
    const actualType = this.getTypeOf(value);
    
    if (!expectedTypes.includes(actualType)) {
      validation.typeMismatches.push({
        field: fieldPath,
        expected: expectedTypes.join(' | '),
        actual: actualType,
        value: value
      });
      validation.isValid = false;
    }
  }

  /**
   * Get type of value
   */
  private getTypeOf(value: any): string {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';
    if (Array.isArray(value)) return 'array';
    return typeof value;
  }

  /**
   * Generate a detailed validation report
   */
  generateValidationReport(validation: TypeValidationResult): string {
    let report = `\n🔍 API Type Validation Report\n`;
    report += `================================\n`;
    report += `Overall Status: ${validation.isValid ? '✅ VALID' : '❌ INVALID'}\n\n`;

    if (validation.errors.length > 0) {
      report += `❌ Errors:\n`;
      validation.errors.forEach(error => {
        report += `  - ${error}\n`;
      });
      report += `\n`;
    }

    if (validation.warnings.length > 0) {
      report += `⚠️  Warnings:\n`;
      validation.warnings.forEach(warning => {
        report += `  - ${warning}\n`;
      });
      report += `\n`;
    }

    if (validation.missingFields.length > 0) {
      report += `🔍 Missing Fields:\n`;
      validation.missingFields.forEach(field => {
        report += `  - ${field}\n`;
      });
      report += `\n`;
    }

    if (validation.extraFields.length > 0) {
      report += `➕ Extra Fields:\n`;
      validation.extraFields.forEach(field => {
        report += `  - ${field}\n`;
      });
      report += `\n`;
    }

    if (validation.typeMismatches.length > 0) {
      report += `🔄 Type Mismatches:\n`;
      validation.typeMismatches.forEach(mismatch => {
        report += `  - ${mismatch.field}: expected ${mismatch.expected}, got ${mismatch.actual}\n`;
        report += `    Value: ${JSON.stringify(mismatch.value)}\n`;
      });
      report += `\n`;
    }

    return report;
  }
}

// Export singleton instance
export const apiTypeValidator = APITypeValidator.getInstance();

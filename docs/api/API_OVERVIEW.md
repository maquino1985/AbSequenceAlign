# API Overview

## Introduction

The AbSequenceAlign API is built with FastAPI and provides comprehensive endpoints for antibody sequence analysis, annotation, and alignment. The API follows RESTful principles and uses modern Python patterns including dependency injection and async/await.

## API Structure

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

### API Versions
- **v1**: Legacy API endpoints (deprecated)
- **v2**: Current API with improved structure and domain models

## Core Endpoints

### Sequence Annotation

#### POST `/api/v2/annotate`
Annotate a single antibody sequence.

**Request Body:**
```json
{
  "sequence": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS",
  "name": "antibody_001",
  "numbering_scheme": "imgt"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully annotated",
  "data": {
    "sequence": {
      "name": "antibody_001",
      "biologic_type": "antibody",
      "chains": [
        {
          "name": "H",
          "chain_type": "HEAVY",
          "sequences": [
            {
              "sequence_type": "PROTEIN",
              "sequence_data": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS",
              "domains": [
                {
                  "domain_type": "VARIABLE",
                  "start_position": 1,
                  "end_position": 120,
                  "features": [
                    {
                      "name": "CDR1",
                      "feature_type": "CDR1",
                      "value": "GYTFTNYWMQ",
                      "start_position": 26,
                      "end_position": 35
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  }
}
```

### Multiple Sequence Alignment

#### POST `/api/v2/align`
Align multiple antibody sequences.

**Request Body:**
```json
{
  "sequences": [
    {
      "name": "seq1",
      "sequence": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS"
    },
    {
      "name": "seq2", 
      "sequence": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS"
    }
  ],
  "alignment_method": "clustal"
}
```

### Workflow Processing

#### POST `/api/v2/workflow`
Process multiple sequences through a complete annotation and alignment workflow.

**Request Body:**
```json
{
  "sequences": [
    {
      "name": "antibody_001",
      "sequence": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS"
    }
  ],
  "workflow": {
    "steps": ["validate", "annotate", "align"],
    "options": {
      "numbering_scheme": "imgt",
      "alignment_method": "clustal"
    }
  }
}
```

## Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": "Detailed error message",
  "data": null
}
```

### Common Error Codes
- `400`: Bad Request - Invalid input data
- `422`: Validation Error - Request validation failed
- `500`: Internal Server Error - Server processing error

## Authentication

Currently, the API does not require authentication for development. For production deployment, consider implementing:

- JWT-based authentication
- API key authentication
- OAuth 2.0 integration

## Rate Limiting

The API implements rate limiting to prevent abuse:
- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per minute per user

## Data Models

### Request Models
All request models use Pydantic for validation and serialization:

```python
from pydantic import BaseModel
from typing import List, Optional
from backend.domain.models import NumberingScheme

class SequenceRequest(BaseModel):
    sequence: str
    name: str
    numbering_scheme: NumberingScheme = NumberingScheme.IMGT
```

### Response Models
Response models follow a consistent structure:

```python
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

## Testing the API

### Using curl
```bash
# Annotate a sequence
curl -X POST "http://localhost:8000/api/v2/annotate" \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS",
    "name": "test_antibody"
  }'
```

### Using Python requests
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v2/annotate",
    json={
        "sequence": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS",
        "name": "test_antibody"
    }
)
print(response.json())
```

## OpenAPI Documentation

The API includes automatic OpenAPI documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Versioning Strategy

- **v1**: Legacy endpoints (deprecated, will be removed)
- **v2**: Current stable API
- **v3**: Future API version (planned)

## Migration Guide

### From v1 to v2
1. Update endpoint URLs from `/api/v1/*` to `/api/v2/*`
2. Update request/response models to match new structure
3. Handle new error response format
4. Update client code to use new domain models

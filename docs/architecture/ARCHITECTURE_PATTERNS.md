# Better Architectural Patterns for Service Organization

## Current Problem: God Object Anti-Pattern

The `UnifiedAnnotationService` violates the Single Responsibility Principle by doing:
- Sequence annotation
- Sequence alignment  
- Request processing
- Response formatting
- Data validation
- Region extraction

## Pattern 1: Command Pattern with Pipeline Orchestrator (RECOMMENDED)

### Structure:
```
application/
├── orchestrators/
│   └── annotation_orchestrator.py      # Coordinates the workflow
├── services/
│   ├── annotation_service.py           # Pure annotation logic
│   ├── alignment_service.py            # Pure alignment logic
│   ├── validation_service.py           # Pure validation logic
│   └── response_service.py             # Pure response formatting
├── commands/
│   ├── annotate_sequence_command.py    # Encapsulates annotation request
│   ├── align_sequences_command.py      # Encapsulates alignment request
│   └── process_annotation_command.py   # Encapsulates full workflow
└── handlers/
    ├── annotation_handler.py           # Handles annotation commands
    ├── alignment_handler.py            # Handles alignment commands
    └── workflow_handler.py             # Handles workflow commands
```

### Benefits:
- **Single Responsibility**: Each service has one job
- **Testable**: Easy to test individual services
- **Extensible**: Easy to add new commands/services
- **Maintainable**: Clear separation of concerns

### Example Usage:
```python
# API Endpoint
@router.post("/annotate")
async def annotate_sequences(request: AnnotationRequest):
    command = AnnotateSequenceCommand(request)
    handler = AnnotationHandler(
        annotation_service=AnnotationService(),
        validation_service=ValidationService(),
        response_service=ResponseService()
    )
    return await handler.handle(command)
```

## Pattern 2: Chain of Responsibility with Pipeline

### Structure:
```
application/
├── pipelines/
│   ├── annotation_pipeline.py          # Defines the workflow steps
│   └── pipeline_builder.py             # Builds pipeline instances
├── handlers/
│   ├── validation_handler.py           # Step 1: Validate
│   ├── annotation_handler.py           # Step 2: Annotate
│   ├── alignment_handler.py            # Step 3: Align (if needed)
│   └── response_handler.py             # Step 4: Format response
└── services/
    ├── annotation_service.py           # Pure business logic
    ├── alignment_service.py            # Pure business logic
    └── validation_service.py           # Pure business logic
```

### Benefits:
- **Flexible**: Easy to add/remove/reorder steps
- **Reusable**: Same handlers can be used in different pipelines
- **Testable**: Each step can be tested independently

## Pattern 3: Strategy Pattern with Service Locator

### Structure:
```
application/
├── strategies/
│   ├── annotation_strategy.py          # Interface for annotation
│   ├── alignment_strategy.py           # Interface for alignment
│   └── response_strategy.py            # Interface for response formatting
├── implementations/
│   ├── imgt_annotation_strategy.py     # IMGT-specific annotation
│   ├── kabat_annotation_strategy.py    # Kabat-specific annotation
│   ├── pairwise_alignment_strategy.py  # Pairwise alignment
│   └── multiple_alignment_strategy.py  # Multiple alignment
├── service_locator.py                  # Manages service instances
└── workflow_manager.py                 # Orchestrates strategies
```

### Benefits:
- **Pluggable**: Easy to swap implementations
- **Configurable**: Different strategies for different use cases
- **Extensible**: Easy to add new strategies

## Pattern 4: Facade Pattern with Service Aggregation

### Structure:
```
application/
├── facades/
│   └── annotation_facade.py            # Simple interface for complex subsystem
├── services/
│   ├── annotation_service.py           # Core annotation logic
│   ├── alignment_service.py            # Core alignment logic
│   ├── validation_service.py           # Core validation logic
│   └── response_service.py             # Core response logic
└── aggregators/
    └── service_aggregator.py           # Manages service interactions
```

### Benefits:
- **Simple Interface**: API only sees the facade
- **Loose Coupling**: Services don't know about each other
- **Easy to Use**: Simple API for complex operations

## Pattern 5: Event-Driven Architecture

### Structure:
```
application/
├── events/
│   ├── annotation_requested.py         # Event: annotation requested
│   ├── annotation_completed.py         # Event: annotation completed
│   ├── alignment_requested.py          # Event: alignment requested
│   └── response_ready.py               # Event: response ready
├── handlers/
│   ├── annotation_event_handler.py     # Handles annotation events
│   ├── alignment_event_handler.py      # Handles alignment events
│   └── response_event_handler.py       # Handles response events
├── services/
│   ├── annotation_service.py           # Pure business logic
│   ├── alignment_service.py            # Pure business logic
│   └── response_service.py             # Pure business logic
└── event_bus.py                        # Manages event flow
```

### Benefits:
- **Decoupled**: Services communicate via events
- **Scalable**: Easy to add new event handlers
- **Asynchronous**: Can handle long-running operations

## Recommended Approach: Pattern 1 (Command + Orchestrator)

For your use case, I recommend **Pattern 1: Command Pattern with Pipeline Orchestrator** because:

1. **Clear Separation**: Each service has a single responsibility
2. **Easy Testing**: Each component can be tested independently
3. **Flexible**: Easy to add new commands or modify workflows
4. **Maintainable**: Clear structure that's easy to understand
5. **API-Friendly**: Commands can be easily mapped to API endpoints

### Implementation Steps:
1. **Extract individual services** from UnifiedAnnotationService
2. **Create command objects** for each operation
3. **Create handlers** that coordinate services
4. **Create orchestrator** for complex workflows
5. **Update API endpoints** to use the new structure

Would you like me to implement this pattern?

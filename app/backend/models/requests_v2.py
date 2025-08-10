from typing import List
from pydantic import BaseModel, Field
from backend.models.models import NumberingScheme, SequenceInput


class AnnotationRequestV2(BaseModel):
    sequences: List[SequenceInput] = Field(..., description="Sequences to annotate")
    numbering_scheme: NumberingScheme = Field(default=NumberingScheme.IMGT)

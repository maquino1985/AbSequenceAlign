from typing import List

from backend.models.models import NumberingScheme, SequenceInput
from pydantic import BaseModel, Field


class AnnotationRequestV2(BaseModel):
    sequences: List[SequenceInput] = Field(
        ..., description="Sequences to annotate"
    )
    numbering_scheme: NumberingScheme = Field(default=NumberingScheme.IMGT)

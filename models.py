from pydantic import BaseModel
from typing import List, Dict


class ExtractResponse(BaseModel):

    document_type: str

    issuer: str

    date: str

    totals: Dict[str, float]

    reference_ids: List[str]

    confidence: float

    extraction_method: str

    errors: List[str]
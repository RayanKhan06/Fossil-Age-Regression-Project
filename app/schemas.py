"""Request/response schemas for the fossil age prediction API."""
from pydantic import BaseModel, Field


class FossilFeatures(BaseModel):
    """One fossil record's raw (pre-encoding) features, matching the dataset columns."""
    taxon_name: str = Field(..., examples=["Trilobita sp."])
    class_: str = Field(..., alias="class", examples=["Trilobita"])
    phylum: str = Field(..., examples=["Arthropoda"])
    lithology: str = Field(..., examples=["shale"])
    environment: str = Field(..., examples=["marine indet."])
    latitude: float = Field(..., examples=[40.7128])
    longitude: float = Field(..., examples=[-74.0060])

    model_config = {"populate_by_name": True}


class PredictionResponse(BaseModel):
    predicted_age_myr: float
    model_version: str

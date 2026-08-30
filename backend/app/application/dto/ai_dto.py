from datetime import datetime

from pydantic import BaseModel, Field


class TrainModelsRequest(BaseModel):
    symbol: str
    interval: str = "1min"
    limit: int = Field(default=3000, ge=500, le=5000)
    horizon: int = Field(default=20, ge=5, le=200)
    minimum_samples: int = Field(default=200, ge=50)


class ModelTrainingResult(BaseModel):
    model_name: str
    version: str
    metrics: dict


class TrainModelsResponse(BaseModel):
    symbol: str
    interval: str
    dataset_size: int
    models: list[ModelTrainingResult]


class ModelPrediction(BaseModel):
    model_name: str
    prediction_type: str
    output: dict
    created_at: datetime | None


class PredictMarketResponse(BaseModel):
    symbol: str
    interval: str
    timestamp: datetime
    predictions: list[ModelPrediction]
    note: str


class ModelStatusEntry(BaseModel):
    model_name: str
    trained: bool
    trained_at: str | None
    metrics: dict | None


class ModelStatusResponse(BaseModel):
    symbol: str
    interval: str
    models: list[ModelStatusEntry]
    all_trained: bool

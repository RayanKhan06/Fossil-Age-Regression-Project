"""
FastAPI service wrapping the tuned XGBoost fossil-age model.

Run locally:
    uvicorn app.main:app --reload

Then visit http://127.0.0.1:8000/docs for interactive API docs, or:
    curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
      "taxon_name": "Trilobita sp.",
      "class": "Trilobita",
      "phylum": "Arthropoda",
      "lithology": "shale",
      "environment": "marine indet.",
      "latitude": 40.7128,
      "longitude": -74.0060
    }'
"""
import joblib
import pandas as pd
import yaml
from fastapi import FastAPI, HTTPException

from app.schemas import FossilFeatures, PredictionResponse

app = FastAPI(
    title="Fossil Age Prediction API",
    description="Predicts fossil age (millions of years) from taxonomic and geospatial features.",
    version="1.0.0",
)

with open("config.yaml") as f:
    CONFIG = yaml.safe_load(f)

# Loaded once at startup, reused across requests (not reloaded per-call).
try:
    MODEL = joblib.load(CONFIG["model"]["artifact_path"])
    SCALER = joblib.load(CONFIG["model"]["scaler_path"])
    TRAIN_COLUMNS = joblib.load(CONFIG["model"]["columns_path"])
except FileNotFoundError:
    MODEL = SCALER = TRAIN_COLUMNS = None  # allows the app to start; /predict will error clearly


def encode_input(features: FossilFeatures) -> pd.DataFrame:
    """
    Turn one raw feature record into the same one-hot-encoded, column-aligned
    shape the model was trained on.

    This mirrors src/preprocess.py's encode_categoricals(), but for a single
    row instead of a full training set — so we can't just call
    pd.get_dummies() and expect the same columns to appear (a single row
    won't produce every category the training data had). Instead we encode,
    then reindex against the saved TRAIN_COLUMNS, filling anything missing
    with 0.
    """
    row = pd.DataFrame([{
        "taxon_name": features.taxon_name,
        "class": features.class_,
        "phylum": features.phylum,
        "lithology": features.lithology,
        "environment": features.environment,
        "latitude": features.latitude,
        "longitude": features.longitude,
    }])

    categorical_columns = CONFIG["data"]["categorical_columns"]
    row_encoded = pd.get_dummies(row, columns=categorical_columns, drop_first=True)

    # Align to the exact columns/order seen at training time.
    row_aligned = row_encoded.reindex(columns=TRAIN_COLUMNS, fill_value=0)
    return row_aligned


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": MODEL is not None}


@app.post("/predict", response_model=PredictionResponse)
def predict(features: FossilFeatures):
    if MODEL is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Model artifacts not found. Run `python run_pipeline.py` first "
                "to train and save the model."
            ),
        )

    row_aligned = encode_input(features)
    row_scaled = SCALER.transform(row_aligned)
    prediction = MODEL.predict(row_scaled)[0]

    return PredictionResponse(
        predicted_age_myr=round(float(prediction), 2),
        model_version=CONFIG["mlflow"]["experiment_name"],
    )

# Running with Docker

## Prerequisite
Install Docker Desktop (Windows): https://www.docker.com/products/docker-desktop/
Confirm it's installed and running with:
    docker --version

## Important: train the model BEFORE building the image
This Dockerfile bakes `models/*.pkl` into the image at build time (simplest
approach for now). That means:

    python run_pipeline.py

must have already been run, and `models/xgb_tuned.pkl`, `models/scaler.pkl`,
`models/train_columns.pkl` must exist in your project folder, BEFORE you
build the image. If they're missing, the container will start but
`/health` will report `model_loaded: false`, same as we saw locally.

(Alternative for later: mount `models/` as a volume instead of copying it
in, so you can swap models without rebuilding the image. Worth doing once
we're deploying to the cloud and retraining regularly — not needed yet.)

## Build the image
From the fossil-project folder (where the Dockerfile lives):

    docker build -t fossil-age-api .

## Run the container
    docker run -p 8000:8000 fossil-age-api

## Test it
Same as before, just now it's running inside a container instead of directly
via uvicorn:

    http://127.0.0.1:8000/docs
    http://127.0.0.1:8000/health

## Common issues
- "Cannot connect to the Docker daemon" -> Docker Desktop isn't running, start it first.
- `/health` shows `model_loaded: false` -> you built the image before running
  run_pipeline.py, or models/ was empty at build time. Retrain, then rebuild:
      docker build -t fossil-age-api .
- Port 8000 already in use -> stop your local `uvicorn` process first, or run
  the container on a different host port, e.g. `-p 8001:8000` and use that instead.

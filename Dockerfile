# Slim Python base is enough since we don't need TensorFlow/build tooling for serving.
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so Docker can cache this layer across rebuilds
# (only re-installs if requirements.txt actually changes).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the actual application code + config.
COPY app/ ./app/
COPY src/ ./src/
COPY config.yaml .

# Model artifacts (models/*.pkl) are expected to already exist at build time —
# i.e. run `python run_pipeline.py` locally BEFORE building the image, so the
# trained model gets baked into it. See note in README-docker.md for the
# alternative (mounting models/ as a volume instead).
COPY models/ ./models/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Fossil Age Regression — MLOps Pipeline

Predicting fossil age (millions of years) from taxonomic and geospatial
features, built out from a single Jupyter notebook into a full pipeline:
tracked experiments, a served API, a container, and cloud infrastructure
provisioned as code.

**Model performance:** Tuned XGBoost, R² ≈ 0.99, RMSE ≈ 9.7 Myr on held-out
test data — a significant improvement over Lasso (R² ≈ 0.88) and untuned
XGBoost (R² ≈ 0.99 baseline).

## Architecture

```
Notebook (EDA + model comparison)
        │
        ▼
Modular pipeline (src/, run_pipeline.py)
   ├─ load → clean → encode → split/scale
   ├─ train: baseline, Lasso, XGBoost, tuned XGBoost (RandomizedSearchCV)
   └─ logged to MLflow (params, metrics, model registry)
        │
        ▼
FastAPI service (app/)
   ├─ GET  /health   — model load status
   └─ POST /predict  — fossil features in, predicted age out
        │
        ▼
Docker (Dockerfile)
   — packages the API + trained model into a single container image
        │
        ▼
Terraform (terraform/) → AWS
   ├─ ECR             — container image registry
   ├─ ECS Fargate     — runs the container, no servers to manage
   └─ Application Load Balancer — public HTTP endpoint
```

## Why each layer exists

| Layer | Problem it solves |
|---|---|
| Modular pipeline | Notebook cells aren't reusable, testable, or callable from anywhere else |
| MLflow | Otherwise every run's metrics live only in scrollback, with no way to compare |
| FastAPI | A trained model sitting in a `.pkl` file isn't usable by anything else |
| Docker | "Works on my machine" — a container runs identically anywhere |
| Terraform + AWS | Manual cloud console clicking isn't reproducible or version-controlled |

## Repo structure

```
├── Fossil_Age_Project.ipynb   # original EDA + model comparison notebook
├── config.yaml                # paths, hyperparameter search space, MLflow settings
├── run_pipeline.py            # entry point: trains all 4 models, logs to MLflow
├── requirements.txt           # core pipeline + API dependencies
├── requirements-notebook.txt  # extra deps for the notebook only (plots, TensorFlow)
├── Dockerfile
├── src/
│   ├── data.py                # load_data()
│   ├── preprocess.py          # cleaning, encoding, train/test split, scaling
│   ├── train.py                # baseline, Lasso, XGBoost, tuned XGBoost
│   └── evaluate.py            # MSE / RMSE / R²
├── app/
│   ├── main.py                 # FastAPI app: /health, /predict
│   └── schemas.py              # request/response models
└── terraform/
    ├── main.tf, ecr.tf, network.tf, alb.tf, iam.tf, ecs.tf, outputs.tf
    └── DEPLOY.md               # step-by-step AWS deployment guide
```

## Running it locally

```bash
pip install -r requirements.txt

# Get fossil_data.csv (see data/README.md) and place it at data/fossil_data.csv

python run_pipeline.py              # trains models, logs to MLflow, saves the tuned model
mlflow ui --backend-store-uri sqlite:///mlflow.db   # view experiment history

uvicorn app.main:app --reload       # serve the API locally
# → http://127.0.0.1:8000/docs
```

## Running it in Docker

```bash
docker build -t fossil-age-api .
docker run -p 8000:8000 fossil-age-api
```

## Deploying to AWS

See [`terraform/DEPLOY.md`](terraform/DEPLOY.md) for the full walkthrough
(ECR push, Terraform apply, teardown). Summary: Terraform provisions an ECR
repository and an ECS Fargate service behind an Application Load Balancer;
the Docker image built above gets pushed to ECR and pulled by ECS at
deploy time.

```bash
cd terraform
terraform init
terraform apply -target=aws_ecr_repository.app   # create the registry first
# build, tag, and push the image to it (see DEPLOY.md)
terraform apply                                   # create everything else
terraform output load_balancer_url                # your public URL
```

**Note:** running infrastructure incurs a small hourly cost. Run
`terraform destroy` when not actively demoing the deployment.

## Known limitations / notes

- The one-hot encoding step in `src/preprocess.py` carries over a small bug
  from the original notebook (`lithology` gets filled with `class`'s mode,
  not its own) — kept intentionally so results match the notebook; flagged
  with a `TODO` in code for anyone who wants to fix and re-tune.
- The AWS deployment runs a single ECS task (no redundancy) — fine for a
  portfolio demo, not meant to represent a production-scale setup.
- Dataset is not committed to the repo (see `data/README.md`); the original
  notebook pulled it from a Google Drive link.

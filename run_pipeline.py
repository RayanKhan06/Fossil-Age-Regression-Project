"""
Entry point: load -> preprocess -> train all 4 models -> evaluate -> save the
winner (tuned XGBoost) to disk. Every model's params/metrics/artifact are
logged to MLflow so runs are comparable over time instead of just printed.

Usage:
    python run_pipeline.py

View results:
    mlflow ui --backend-store-uri sqlite:///mlflow.db
    (then open http://127.0.0.1:5000)
"""
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import yaml

from src.data import load_data
from src.preprocess import run_preprocessing
from src.train import train_baseline, train_lasso, train_xgb_baseline, train_xgb_tuned, save_artifacts
from src.evaluate import evaluate


def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    mlflow.set_tracking_uri(config["mlflow"]["tracking_uri"])
    mlflow.set_experiment(config["mlflow"]["experiment_name"])

    df = load_data(config["data"]["raw_path"])

    (X_train, X_test, X_train_scaled, X_test_scaled,
     y_train, y_test, scaler) = run_preprocessing(
        df,
        categorical_columns=config["data"]["categorical_columns"],
        target_column=config["data"]["target_column"],
        test_size=config["split"]["test_size"],
        random_state=config["split"]["random_state"],
    )

    print("=== Baseline (mean) ===")
    with mlflow.start_run(run_name="baseline_mean"):
        baseline_model = train_baseline(X_train, y_train)
        metrics = evaluate(y_test, baseline_model.predict(X_test), label="Baseline")
        mlflow.log_params({"strategy": "mean"})
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(baseline_model, name="model")

    print("\n=== Lasso ===")
    with mlflow.start_run(run_name="lasso"):
        lasso_alpha = 1.0
        lasso_model = train_lasso(X_train_scaled, y_train, alpha=lasso_alpha)
        metrics = evaluate(y_test, lasso_model.predict(X_test_scaled), label="Lasso")
        mlflow.log_params({"alpha": lasso_alpha})
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(lasso_model, name="model")

    print("\n=== XGBoost (baseline params) ===")
    with mlflow.start_run(run_name="xgb_baseline"):
        xgb_model = train_xgb_baseline(X_train_scaled, y_train, config["xgb_baseline"])
        metrics = evaluate(y_test, xgb_model.predict(X_test_scaled), label="XGBoost")
        mlflow.log_params(config["xgb_baseline"])
        mlflow.log_metrics(metrics)
        mlflow.xgboost.log_model(xgb_model, name="model")

    print("\n=== XGBoost (tuned via RandomizedSearchCV) ===")
    with mlflow.start_run(run_name="xgb_tuned") as tuned_run:
        xgb_tuned_model, best_params = train_xgb_tuned(X_train_scaled, y_train, config["xgb_search"])
        metrics = evaluate(y_test, xgb_tuned_model.predict(X_test_scaled), label="Tuned XGBoost")
        print("Best hyperparameters:", best_params)
        mlflow.log_params(best_params)
        mlflow.log_metrics(metrics)
        mlflow.xgboost.log_model(
            xgb_tuned_model,
            name="model",
            registered_model_name="fossil-age-xgb",  # creates/updates entry in the model registry
        )
        tuned_run_id = tuned_run.info.run_id

    save_artifacts(
        model=xgb_tuned_model,
        scaler=scaler,
        train_columns=X_train.columns,
        model_path=config["model"]["artifact_path"],
        scaler_path=config["model"]["scaler_path"],
        columns_path=config["model"]["columns_path"],
    )
    print(f"\nSaved tuned model to {config['model']['artifact_path']}")
    print(f"Tuned run logged to MLflow (run_id={tuned_run_id}); registered as 'fossil-age-xgb'")


if __name__ == "__main__":
    main()

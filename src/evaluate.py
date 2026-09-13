"""Evaluation metrics, matching the notebook's MSE / RMSE / R2 calculations."""
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score


def evaluate(y_true, y_pred, label: str = "") -> dict:
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    if label:
        print(f"{label} Test MSE: {mse:.4f}")
        print(f"{label} Test RMSE: {rmse:.4f}")
        print(f"{label} Test R2: {r2:.4f}")

    return {"mse": mse, "rmse": rmse, "r2": r2}

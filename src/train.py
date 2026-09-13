"""
Train the models from the notebook: baseline (mean), Lasso, XGBoost (baseline
hyperparams), and tuned XGBoost via RandomizedSearchCV. Same models, same
hyperparameter ranges as the notebook — just callable functions instead of
top-to-bottom cells.
"""
import joblib
import numpy as np
from scipy.stats import randint, uniform
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Lasso
from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBRegressor


def train_baseline(X_train, y_train):
    model = DummyRegressor(strategy="mean")
    model.fit(X_train, y_train)
    return model


def train_lasso(X_train_scaled, y_train, alpha: float = 1.0, random_state: int = 42):
    model = Lasso(alpha=alpha, random_state=random_state)
    model.fit(X_train_scaled, y_train)
    return model


def train_xgb_baseline(X_train_scaled, y_train, params: dict):
    model = XGBRegressor(objective="reg:squarederror", **params)
    model.fit(X_train_scaled, y_train)
    return model


def train_xgb_tuned(X_train_scaled, y_train, search_config: dict):
    """RandomizedSearchCV over XGBoost, matching the notebook's search space."""
    pd_cfg = search_config["param_distributions"]
    param_distributions = {
        "n_estimators": randint(pd_cfg["n_estimators"][0], pd_cfg["n_estimators"][1]),
        "learning_rate": uniform(pd_cfg["learning_rate"][0],
                                  pd_cfg["learning_rate"][1] - pd_cfg["learning_rate"][0]),
        "max_depth": randint(pd_cfg["max_depth"][0], pd_cfg["max_depth"][1]),
        "subsample": uniform(pd_cfg["subsample"][0],
                              pd_cfg["subsample"][1] - pd_cfg["subsample"][0]),
        "colsample_bytree": uniform(pd_cfg["colsample_bytree"][0],
                                     pd_cfg["colsample_bytree"][1] - pd_cfg["colsample_bytree"][0]),
    }

    search = RandomizedSearchCV(
        XGBRegressor(objective="reg:squarederror", random_state=search_config["random_state"]),
        param_distributions=param_distributions,
        n_iter=search_config["n_iter"],
        cv=search_config["cv"],
        scoring="neg_mean_squared_error",
        random_state=search_config["random_state"],
    )
    search.fit(X_train_scaled, y_train)
    return search.best_estimator_, search.best_params_


def save_artifacts(model, scaler, train_columns, model_path: str, scaler_path: str, columns_path: str):
    """Persist the trained model + scaler + column order so serving matches training exactly."""
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(list(train_columns), columns_path)

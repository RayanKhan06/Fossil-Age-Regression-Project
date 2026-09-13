"""
Preprocessing steps, extracted 1:1 from the notebook's EDA/cleaning cells.
No logic changes except where noted.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing categorical values with the mode.

    NOTE (bug carried over from the notebook, not fixed here):
    the original code fills `lithology` with `class`'s mode instead of
    `lithology`'s own mode:
        fossil_data['lithology'] = fossil_data['class'].fillna(...)
    Kept as-is so behavior matches your existing R²=0.990 model.
    TODO: change to
        df['lithology'] = df['lithology'].fillna(df['lithology'].mode()[0])
    if you want to fix it (will change results slightly, worth re-tuning after).
    """
    df = df.copy()
    df["class"] = df["class"].fillna(df["class"].mode()[0])
    df["lithology"] = df["class"].fillna(df["class"].mode()[0])  # TODO: see note above
    return df


def encode_categoricals(df: pd.DataFrame, categorical_columns: list) -> pd.DataFrame:
    """One-hot encode categorical columns (same as pd.get_dummies call in notebook)."""
    return pd.get_dummies(df, columns=categorical_columns, drop_first=True)


def split_and_scale(df: pd.DataFrame, target_column: str, test_size: float, random_state: int):
    """Train/test split + StandardScaler, fit only on train (matches notebook)."""
    X = df.drop(columns=[target_column])
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train, X_test, X_train_scaled, X_test_scaled, y_train, y_test, scaler


def run_preprocessing(df: pd.DataFrame, categorical_columns: list, target_column: str,
                       test_size: float, random_state: int):
    """Full preprocessing pipeline: clean -> encode -> split -> scale."""
    df = clean_missing_values(df)
    df = encode_categoricals(df, categorical_columns)
    return split_and_scale(df, target_column, test_size, random_state)

"""
Load the fossil dataset.

Your original notebook read directly from a Google Drive share link on every
run. That's fine for Colab, but fragile for a pipeline (link can expire,
permissions can change, no version history). This module expects a local CSV
instead. See data/README.md for how to get the file there once.
"""
import pandas as pd


def load_data(raw_path: str) -> pd.DataFrame:
    """Load the raw fossil dataset from a local CSV path."""
    return pd.read_csv(raw_path)

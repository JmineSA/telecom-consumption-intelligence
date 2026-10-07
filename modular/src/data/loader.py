"""
Data loading for the forecasting app.

Reads test split + model metadata from data/processed/ and models/.
"""
from pathlib import Path
from typing import Optional

import pandas as pd
import json

from ..config import (
    TEST_PATH, TRAIN_PATH, MODEL_INFO_PATH, PREP_META_PATH,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


def load_test_data(path: Optional[Path] = None) -> pd.DataFrame:
    """Load the time-based test split."""
    p = path or TEST_PATH

    if not p.exists():
        logger.error(f"Test data not found: {p}")
        raise FileNotFoundError(
            f"Test data not found: {p}\n"
            f"Run 'python -m training.core.data_preparation' first."
        )

    df = pd.read_parquet(p)
    logger.info(f"Loaded test data: {df.shape} from {p}")
    return df


def load_train_data(path: Optional[Path] = None) -> pd.DataFrame:
    """Load the training split (used for feature inspection)."""
    p = path or TRAIN_PATH

    if not p.exists():
        logger.error(f"Train data not found: {p}")
        raise FileNotFoundError(f"Train data not found: {p}")

    df = pd.read_parquet(p)
    logger.info(f"Loaded train data: {df.shape}")
    return df


def load_model_info(path: Optional[Path] = None) -> dict:
    """Load model metadata (metrics, features, training date)."""
    p = path or MODEL_INFO_PATH

    if not p.exists():
        logger.warning(f"Model info not found: {p}")
        return {}

    with open(p) as f:
        info = json.load(f)
    logger.info(f"Loaded model info: {info.get('model_type', 'unknown')}")
    return info


def load_prep_metadata(path: Optional[Path] = None) -> dict:
    """Load data preparation metadata."""
    p = path or PREP_META_PATH

    if not p.exists():
        return {}

    with open(p) as f:
        return json.load(f)
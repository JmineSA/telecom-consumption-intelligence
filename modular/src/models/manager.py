"""
Model lifecycle: loading the trained pipeline and running predictions.

The pickle references `training.core.custom_transformers`, which lives at
<repo_root>/training/core/. We make sure the repo root is on sys.path
before unpickling.
"""
import os
import sys
import json
import joblib
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd

from ..config import MODEL_PATH, MODEL_INFO_PATH, PROJECT_ROOT
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Load and serve the trained forecasting pipeline."""

    def __init__(self):
        self.model = None
        self.info: Dict[str, Any] = {}
        self.last_error: Optional[str] = None
        self.last_traceback: Optional[str] = None
        self._load()

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------
    def _load(self):
        # Make sure the repo root is on sys.path so `training.*` resolves
        repo_root = str(PROJECT_ROOT)
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)

        # Pre-import the module the pickle references
        try:
            import training.core.custom_transformers  # noqa: F401
            logger.info("Pre-imported training.core.custom_transformers")
        except Exception as e:
            logger.warning(f"Pre-import failed: {e}")

        # Load pickle
        if not MODEL_PATH.exists():
            self.last_error = f"Model file not found: {MODEL_PATH}"
            logger.error(self.last_error)
            return

        try:
            self.model = joblib.load(MODEL_PATH)
            logger.info(f"Model loaded: {type(self.model).__name__}")
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            self.last_traceback = traceback.format_exc()
            logger.error(f"Failed to load model: {self.last_error}")
            logger.error(self.last_traceback)
            return

        # Load metadata
        if MODEL_INFO_PATH.exists():
            try:
                with open(MODEL_INFO_PATH) as f:
                    self.info = json.load(f)
            except Exception as e:
                logger.warning(f"Could not read model_info.json: {e}")

    # ------------------------------------------------------------------
    # Predict
    # ------------------------------------------------------------------
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Run prediction.

        The saved pipeline handles all preprocessing internally, so we
        pass the DataFrame through. X must include `measurement_date`.
        """
        if self.model is None:
            raise RuntimeError(
                f"Model not loaded. Error: {self.last_error}\n"
                f"{self.last_traceback or ''}"
            )
        return self.model.predict(X)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------
    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    @property
    def model_type(self) -> str:
        if self.model is None:
            return "Not loaded"
        return type(self.model.named_steps["regressor"]).__name__ \
            if hasattr(self.model, "named_steps") else type(self.model).__name__

    @property
    def feature_count(self) -> int:
        return int(self.info.get("n_features", 0))

    @property
    def val_r2(self) -> Optional[float]:
        return self.info.get("val_metrics", {}).get("r2")

    @property
    def train_r2(self) -> Optional[float]:
        return self.info.get("train_metrics", {}).get("r2")

    @property
    def val_mae(self) -> Optional[float]:
        return self.info.get("val_metrics", {}).get("mae")

    @property
    def trained_at(self) -> Optional[str]:
        return self.info.get("trained_at")
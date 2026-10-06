"""
Model lifecycle management — aligned with renamed training package.
"""
import os
import sys

# ===========================================================================
# CRITICAL — runs before any joblib.load call.
# The pickle references `training.core.custom_transformers`, which lives at
# <repo_root>/training/core/. From modular/src/models/manager.py we go up
# FOUR levels to reach the repo root.
# ===========================================================================
_THIS_FILE = os.path.abspath(__file__)                    # .../modular/src/models/manager.py
_SRC_MODELS_DIR = os.path.dirname(_THIS_FILE)             # .../modular/src/models
_SRC_DIR = os.path.dirname(_SRC_MODELS_DIR)               # .../modular/src
_MODULAR_DIR = os.path.dirname(_SRC_DIR)                  # .../modular
_PROJECT_ROOT = os.path.dirname(_MODULAR_DIR)             # repo root

# Repo root FIRST — `training` package lives there
if _PROJECT_ROOT in sys.path:
    sys.path.remove(_PROJECT_ROOT)
sys.path.insert(0, _PROJECT_ROOT)

# modular/ SECOND — app's own `src` package lives there
if _MODULAR_DIR in sys.path:
    sys.path.remove(_MODULAR_DIR)
sys.path.insert(1, _MODULAR_DIR)
# ===========================================================================

import json
import joblib
import traceback
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from sklearn.ensemble import GradientBoostingRegressor

from ..config import CONFIG
from ..constants import EXPECTED_FEATURES, PRICING_BENCHMARKS
from ..data.processor import DataProcessor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Manage model lifecycle: loading, prediction, metadata."""

    MODEL_FILENAME = "mobile_data_consumption_pipeline.pkl"
    PERF_FILENAME = "model_info.json"

    def __init__(self):
        self.config = CONFIG.model
        self.processor = DataProcessor()

        # Resolve project root from modular/src/models/manager.py → up 4 levels
        current_file = os.path.abspath(__file__)
        src_dir = os.path.dirname(current_file)
        models_pkg_dir = os.path.dirname(src_dir)
        modular_dir = os.path.dirname(models_pkg_dir)
        project_dir = os.path.dirname(modular_dir)

        self.project_dir = project_dir
        self.models_dir = os.path.join(project_dir, "models")

        self.model_paths = [
            os.path.join(self.models_dir, self.MODEL_FILENAME),
            os.path.join("models", self.MODEL_FILENAME),
            os.path.join("..", "models", self.MODEL_FILENAME),
            os.path.join("..", "..", "models", self.MODEL_FILENAME),
        ]
        self.perf_paths = [
            os.path.join(self.models_dir, self.PERF_FILENAME),
            os.path.join("models", self.PERF_FILENAME),
            os.path.join("..", "models", self.PERF_FILENAME),
            os.path.join("..", "..", "models", self.PERF_FILENAME),
        ]

        self.last_error: Optional[str] = None
        self.last_traceback: Optional[str] = None

        self.logger = logger
        self.logger.info(f"Project directory: {project_dir}")
        self.logger.info(f"Models directory:  {self.models_dir}")

    # ------------------------------------------------------------------
    # FINDING FILES
    # ------------------------------------------------------------------
    def _find_existing_model(self) -> Tuple[Optional[str], Optional[str]]:
        primary_model = os.path.join(self.models_dir, self.MODEL_FILENAME)
        primary_perf = os.path.join(self.models_dir, self.PERF_FILENAME)

        if os.path.exists(primary_model):
            self.logger.info(f"Found model: {primary_model}")
            perf = primary_perf if os.path.exists(primary_perf) else None
            if perf is None:
                self.logger.warning(f"No metadata at {primary_perf}")
            return primary_model, perf

        for model_path in self.model_paths:
            if os.path.exists(model_path):
                self.logger.info(f"Found model at alternate path: {model_path}")
                for perf_path in self.perf_paths:
                    if os.path.exists(perf_path):
                        return model_path, perf_path
                return model_path, None

        self.logger.warning(f"No model found. Looked in: {self.model_paths}")
        return None, None

    @staticmethod
    def _normalise_performance(perf_raw: dict) -> dict:
        if "r2_score" in perf_raw and isinstance(perf_raw.get("r2_score"), (int, float)):
            return perf_raw

        p = perf_raw.get("performance", {})
        return {
            "r2_score": p.get("test_r2", p.get("val_r2", p.get("train_r2"))),
            "train_r2_score": p.get("train_r2"),
            "val_r2_score": p.get("val_r2"),
            "test_r2_score": p.get("test_r2"),
            "rmse": p.get("test_rmse", p.get("val_rmse")),
            "mae": p.get("test_mae", p.get("val_mae")),
            "mape": p.get("test_mape"),
            "n_features": perf_raw.get("n_features"),
            "training_samples": perf_raw.get("n_train_samples"),
            "test_samples": perf_raw.get("n_test_samples"),
            "target_column": perf_raw.get("target"),
            "model_type": perf_raw.get("model_type"),
            "trained_at": perf_raw.get("trained_at") or perf_raw.get("saved_date"),
        }

    # ------------------------------------------------------------------
    # LOAD — no more src.* purge, pre-import training package
    # ------------------------------------------------------------------
    def load(self, train_df: Optional[pd.DataFrame] = None) -> Optional[Dict[str, Any]]:
        self.last_error = None
        self.last_traceback = None

        try:
            model_path, perf_path = self._find_existing_model()

            if model_path is None:
                self.last_error = "No trained model file found on disk."
                self.logger.error(self.last_error)
                return None

            self.logger.info(f"Loading model from: {model_path}")

            # ---------------------------------------------------------
            # Ensure repo root is on sys.path so `training.*` resolves
            # ---------------------------------------------------------
            _here = os.path.abspath(__file__)
            _repo_root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(_here)
                    )
                )
            )
            if _repo_root not in sys.path:
                sys.path.insert(0, _repo_root)
            self.logger.info(f"_repo_root resolved to: {_repo_root}")

            # ---------------------------------------------------------
            # Pre-import the module the pickle references
            # ---------------------------------------------------------
            try:
                import training.core.custom_transformers  # noqa: F401
                self.logger.info("Pre-imported training.core.custom_transformers")
            except Exception as _e:
                self.logger.warning(f"Pre-import failed: {_e}")

            # ---------------------------------------------------------
            # Actual pickle load
            # ---------------------------------------------------------
            try:
                model = joblib.load(model_path)
            except Exception as e:
                self.last_error = f"{type(e).__name__}: {e}"
                self.last_traceback = traceback.format_exc()
                self.logger.error(f"joblib.load failed: {self.last_error}")
                self.logger.error(self.last_traceback)
                return None

            if perf_path is not None:
                try:
                    with open(perf_path, "r") as f:
                        perf_raw = json.load(f)
                    performance = self._normalise_performance(perf_raw)
                except Exception as e:
                    self.logger.warning(f"Could not read metadata: {e}")
                    performance = {"note": "metadata unreadable"}
            else:
                performance = {"note": "metadata not found"}

            self.logger.info(
                f"Model loaded. Test R² = {performance.get('r2_score', 'N/A')}"
            )

            return {
                "model": model,
                "performance": performance,
                "is_real": True,
                "model_path": model_path,
                "perf_path": perf_path,
            }

        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            self.last_traceback = traceback.format_exc()
            self.logger.error(f"Unexpected error loading model: {self.last_error}")
            self.logger.error(self.last_traceback)
            return None

    # ------------------------------------------------------------------
    # PREDICT
    # ------------------------------------------------------------------
    def predict(self, model, X_input: pd.DataFrame) -> np.ndarray:
        """
        Run prediction.

        The pipeline handles all preprocessing internally, but it needs a
        specific input schema: measurement_date + 10 features (age_group,
        plan_type, network_type, device_type, hours_*, is_*).

        We keep only those columns to protect against callers passing extra
        columns (e.g. one-hot device_type_* variants from older code).
        """
        required_cols = [
            'measurement_date',
            'age_group', 'plan_type', 'network_type', 'device_type',
            'hours_streaming', 'hours_social', 'hours_messaging', 'hours_gaming',
            'is_peak_hour_user', 'is_weekend',
        ]
        # Keep only the columns the pipeline expects, if present
        cols_to_keep = [c for c in required_cols if c in X_input.columns]
        X_input = X_input[cols_to_keep]
        return model.predict(X_input)

    # ------------------------------------------------------------------
    # TRAIN (fallback)
    # ------------------------------------------------------------------
    def train(self, train_df: pd.DataFrame) -> Tuple[GradientBoostingRegressor, Dict]:
        self.logger.info("Starting ad-hoc training...")
        train_df = self.processor.prepare_features(train_df)

        if self.config.target_column not in train_df.columns:
            raise ValueError(
                f"Target column '{self.config.target_column}' not found in data"
            )

        X = train_df[EXPECTED_FEATURES]
        y = train_df[self.config.target_column]

        from sklearn.model_selection import train_test_split
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config.test_size,
            random_state=self.config.random_state,
        )

        model = GradientBoostingRegressor(
            n_estimators=self.config.n_estimators,
            learning_rate=self.config.learning_rate,
            max_depth=self.config.max_depth,
            random_state=self.config.random_state,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_train_pred = model.predict(X_train)

        performance = {
            "r2_score": float(r2_score(y_test, y_pred)),
            "train_r2_score": float(r2_score(y_train, y_train_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "n_features": len(EXPECTED_FEATURES),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "target_column": self.config.target_column,
            "timestamp": datetime.now().isoformat(),
            "dataset_rows": len(train_df),
        }

        self._save_model(model, performance)
        self.logger.info(f"Model trained with R²: {performance['r2_score']:.4f}")
        return model, performance

    def _save_model(self, model, performance: Dict):
        os.makedirs(self.models_dir, exist_ok=True)
        model_path = os.path.join(self.models_dir, self.MODEL_FILENAME)
        perf_path = os.path.join(self.models_dir, self.PERF_FILENAME)
        joblib.dump(model, model_path)
        with open(perf_path, "w") as f:
            json.dump(performance, f, indent=2)
        self.logger.info(f"Model saved to: {model_path}")

    # ------------------------------------------------------------------
    # INTROSPECTION
    # ------------------------------------------------------------------
    def get_feature_importance(self, model) -> pd.DataFrame:
        if hasattr(model, "feature_importances_"):
            importance = model.feature_importances_
            names = EXPECTED_FEATURES[: len(importance)]
            return pd.DataFrame({
                "Feature": names,
                "Importance": importance[: len(EXPECTED_FEATURES)],
            }).sort_values("Importance", ascending=False)

        if hasattr(model, "named_steps") and "regressor" in model.named_steps:
            reg = model.named_steps["regressor"]
            if hasattr(reg, "feature_importances_"):
                importance = reg.feature_importances_
                names = (
                    EXPECTED_FEATURES[: len(importance)]
                    if EXPECTED_FEATURES
                    else [f"f{i}" for i in range(len(importance))]
                )
                return pd.DataFrame({
                    "Feature": names,
                    "Importance": importance,
                }).sort_values("Importance", ascending=False)
        return pd.DataFrame()

    def get_model_info(self) -> Dict[str, Any]:
        try:
            model_path, perf_path = self._find_existing_model()
            if model_path and perf_path:
                with open(perf_path, "r") as f:
                    perf_raw = json.load(f)
                return {
                    "exists": True,
                    "path": model_path,
                    "performance": self._normalise_performance(perf_raw),
                    "file_size": os.path.getsize(model_path),
                    "last_modified": datetime.fromtimestamp(
                        os.path.getmtime(model_path)
                    ).isoformat(),
                }
        except Exception as e:
            self.logger.error(f"Error getting model info: {e}")
        return {"exists": False}


class ModelMetrics:
    """Calculate and manage model metrics."""

    @staticmethod
    def calculate_arpu(usage_gb: float, plan_type) -> float:
        from ..constants import PRICING_BENCHMARKS, REV_PLAN

        if isinstance(plan_type, (int, float, np.integer)):
            plan_name = REV_PLAN.get(int(plan_type), "Prepaid")
        else:
            plan_name = plan_type

        pricing = PRICING_BENCHMARKS.get(plan_name, PRICING_BENCHMARKS["Prepaid"])
        data_charge = usage_gb * pricing["base_rate_per_gb"]
        monthly_fee = pricing["monthly_fee"]

        if usage_gb > 30:
            arpu = (data_charge * 0.75) + monthly_fee
        elif usage_gb > 20:
            arpu = (data_charge * 0.82) + monthly_fee
        elif usage_gb > 10:
            arpu = (data_charge * 0.90) + monthly_fee
        elif usage_gb > 5:
            arpu = data_charge + monthly_fee
        else:
            arpu = (data_charge * 1.15) + monthly_fee

        min_arpu = 29 if "Prepaid" in plan_name else 79
        return round(max(min_arpu, arpu), 2)

    @staticmethod
    def calculate_usage_tier(usage_gb: float) -> str:
        if usage_gb < 2:
            return "low"
        elif usage_gb < 5:
            return "medium"
        return "high"

    @staticmethod
    def get_usage_badge(usage_gb: float) -> Dict[str, str]:
        tier = ModelMetrics.calculate_usage_tier(usage_gb)
        badges = {
            "low": {"label": "Low Usage", "color": "#16a34a", "badge_class": "badge-low"},
            "medium": {"label": "Medium Usage", "color": "#d97706", "badge_class": "badge-medium"},
            "high": {"label": "High Usage", "color": "#dc2626", "badge_class": "badge-high"},
        }
        return badges.get(tier, badges["low"])
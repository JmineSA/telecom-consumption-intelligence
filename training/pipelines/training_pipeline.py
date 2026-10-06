# training/pipelines/training_pipeline.py
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
src_root = project_root / "src"
for path in (str(src_root), str(project_root)):
    if path not in sys.path:
        sys.path.insert(0, path)

from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from training.pipelines.preprocessing_pipeline import build_pipeline


def build_model_pipeline():
    """Build the production model pipeline: preprocessing + HistGradientBoosting."""
    preprocessor = build_pipeline()

    model = HistGradientBoostingRegressor(
        max_iter=400,
        max_depth=6,
        learning_rate=0.05,
        min_samples_leaf=20,
        l2_regularization=1.0,
        random_state=42,
    )

    return Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", model),
    ])
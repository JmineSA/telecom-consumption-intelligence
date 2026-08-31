
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
from src.pipelines.preprocessing_pipeline import build_pipeline

def build_model_pipeline():
    """Build the complete model pipeline with preprocessing and model."""
    
    # Get the preprocessing pipeline
    preprocessor = build_pipeline()
    
    # Create the model
    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    
    # Combine into final pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', model)
    ])
    
    return pipeline
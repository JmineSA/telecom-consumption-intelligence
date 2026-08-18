from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor

from preprocessing_pipeline import build_pipeline


def build_model_pipeline():

    # Existing preprocessing pipeline
    preprocessing = build_pipeline()

    # Best Gradient Boosting model parameters
    model = GradientBoostingRegressor(
        subsample=1.0,
        n_estimators=50,
        min_samples_split=10,
        min_samples_leaf=1,
        max_features=None,
        max_depth=4,
        learning_rate=0.15,
        random_state=42
    )

    # Combine preprocessing + model
    model_pipeline = Pipeline(steps=[
        ('preprocessing', preprocessing),
        ('model', model)
    ])

    return model_pipeline
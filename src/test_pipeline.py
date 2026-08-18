import pandas as pd

from model_pipeline import build_model_pipeline


# Load data
df = pd.read_parquet(
    "data/processed/train_data.parquet"
)

# Separate features and target
X = df.drop(columns=["total_data_gb"])
y = df["total_data_gb"]


print("=" * 60)
print("TESTING COMPLETE MODEL PIPELINE")
print("=" * 60)


# Build complete pipeline
pipeline = build_model_pipeline()


print("\nModel pipeline:")
print(pipeline)


print("\nPipeline steps:")

for name, step in pipeline.steps:
    print(f"  {name}: {type(step).__name__}")


# Use a small sample for testing
X_sample = X.head(100)
y_sample = y.head(100)


print("\nTraining on 100 rows...")

pipeline.fit(
    X_sample,
    y_sample
)


print("Training successful!")


# Test prediction
prediction = pipeline.predict(
    X_sample.head(5)
)


print("\nPredictions:")
print(prediction)


print("\nActual values:")
print(y_sample.head(5).values)


print("\nComplete model pipeline test successful!")
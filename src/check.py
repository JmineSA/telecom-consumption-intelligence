import joblib
from pathlib import Path

model_path = Path(__file__).resolve().parent.parent / "models" / "gradient_boosting_final.pkl"
model = joblib.load(model_path)

print(model)
print("\n--- STEPS ---")
print(model.named_steps)

print("\n--- MODEL FEATURES ---")
print(model.named_steps["model"].n_features_in_)

print("\n--- PREPROCESSED FEATURE NAMES ---")
preprocessor = model.named_steps["preprocessor"]

for i, feature in enumerate(preprocessor.get_feature_names_out(), start=1):
    print(i, feature)
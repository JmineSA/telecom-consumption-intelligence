import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime

# ============================================
# SETUP LOGGING
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================
STAGE_NAME = "curated" 
EDA_FOLDER = "eda"

# Define paths
base_path = Path(r"G:\Study\DATA SCINCE\PROJECTS\POTFOLIO\telecom-consumption-intelligence\data")
curated_path = base_path / STAGE_NAME
eda_path = base_path / EDA_FOLDER

# Create directories
curated_path.mkdir(parents=True, exist_ok=True)
eda_path.mkdir(parents=True, exist_ok=True)
logger.info(f"Created directories: {curated_path}, {eda_path}")

# Load data
data_folder = base_path / "processed"
file_name = "user_activity_data_daily.csv"

try:
    df = pd.read_csv(data_folder / file_name)
    logger.info(f"Loaded {file_name} with {len(df)} rows and {len(df.columns)} columns")
except FileNotFoundError:
    logger.error(f"File not found: {data_folder / file_name}")
    raise

# ============================================
# DATA PREPARATION FUNCTIONS
# ============================================

def convert_mb_to_gb(df, mb_columns=None, drop_original=True):
    """Convert MB to GB using telecom standard (1 GB = 1000 MB)."""
    if mb_columns is None:
        mb_columns = [col for col in df.columns if col.endswith('_mb')]
    
    if not mb_columns:
        logger.warning("No MB columns found to convert")
        return df, []
    
    converted_columns = []
    for col in mb_columns:
        new_col = col.replace('_mb', '_gb')
        df[new_col] = df[col] / 1000
        converted_columns.append(f"{col} -> {new_col}")  # Changed to ASCII
        logger.debug(f"Converted '{col}' -> '{new_col}'")
    
    if drop_original:
        df = df.drop(columns=mb_columns)
        logger.info(f"Dropped {len(mb_columns)} original MB columns")
    
    return df, converted_columns

def convert_date_column(df, date_column='measurement_date'):
    """Convert date column to datetime."""
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    null_count = df[date_column].isnull().sum()
    
    if null_count > 0:
        logger.warning(f"Found {null_count} invalid dates in '{date_column}'")
        df = df.dropna(subset=[date_column])
        logger.info(f"Dropped {null_count} rows with invalid dates")
    else:
        logger.info(f"Successfully converted '{date_column}' to datetime")
    
    return df

# ============================================
# EXECUTE DATA PREPARATION
# ============================================

logger.info("Starting data preparation...")

# 1. Convert MB to GB
df, conversions = convert_mb_to_gb(df)
logger.info(f"Applied {len(conversions)} column conversions")

# 2. Convert date column
df = convert_date_column(df)

# 3. Handle missing values (if any)
null_counts = df.isnull().sum()
if null_counts.sum() > 0:
    logger.info(f"Handling missing values: {null_counts[null_counts > 0].to_dict()}")
    df = df.dropna()
    logger.info(f"Dropped rows with missing values. New shape: {df.shape}")

logger.info(f"Data preparation complete. Final shape: {df.shape}")

# ============================================
# SAVE MULTIPLE VERSIONS
# ============================================

logger.info("Saving curated data...")

# 1. PARQUET
parquet_file = curated_path / "user_activity_curated.parquet"
df.to_parquet(parquet_file, index=False)
logger.info(f"Saved as Parquet: {parquet_file} ({df.memory_usage(deep=True).sum() / 1024**2:.2f} MB)")

# 2. CSV
csv_file = curated_path / "user_activity_curated.csv"
df.to_csv(csv_file, index=False)
logger.info(f"Saved as CSV: {csv_file}")

# 3. Sample for EDA
sample_file = eda_path / "user_activity_sample.csv"
df.sample(min(1000, len(df))).to_csv(sample_file, index=False)
logger.info(f"Saved sample ({min(1000, len(df))} rows) for EDA")

# ============================================
# SAVE METADATA
# ============================================

logger.info("Saving metadata...")

# Detect which columns were converted
converted_columns = {}
for col in df.columns:
    if col.endswith('_gb'):
        original = col.replace('_gb', '_mb')
        converted_columns[original] = col

# Build metadata
metadata = {
    'preparation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'stage': STAGE_NAME,
    'source_file': file_name,
    'source_path': str(data_folder),
    
    'dataset_info': {
        'shape': {
            'rows': df.shape[0],
            'columns': df.shape[1]
        },
        'columns': df.columns.tolist(),
        'dtypes': {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
        'memory_usage_mb': float(df.memory_usage(deep=True).sum() / 1024**2)
    },
    
    'transformations_applied': [
        'Converted MB columns to GB using telecom standard (÷ 1000)',
        'Removed original MB columns after conversion',
        'Converted measurement_date to datetime',
        f'Dropped rows with missing values: {null_counts.sum()} rows' if null_counts.sum() > 0 else 'No rows dropped for missing values'
    ],
    
    'column_conversions': converted_columns,
    
    'date_range': {
        'min': df['measurement_date'].min().strftime('%Y-%m-%d') if 'measurement_date' in df.columns else None,
        'max': df['measurement_date'].max().strftime('%Y-%m-%d') if 'measurement_date' in df.columns else None,
        'total_days': (df['measurement_date'].max() - df['measurement_date'].min()).days if 'measurement_date' in df.columns else None
    },
    
    'target_variable': 'total_data_gb' if 'total_data_gb' in df.columns else None,
    
    'statistics': {
        col: {
            'mean': float(df[col].mean()),
            'median': float(df[col].median()),
            'std': float(df[col].std()),
            'min': float(df[col].min()),
            'max': float(df[col].max())
        } for col in df.select_dtypes(include=[np.number]).columns[:10]
    }
}

# Save metadata as JSON
metadata_file = curated_path / "data_preparation_metadata.json"
with open(metadata_file, 'w', encoding='utf-8') as f:  # Added encoding
    json.dump(metadata, f, indent=4, default=str)
logger.info(f"Saved preparation metadata: {metadata_file}")

# ============================================
# SAVE PREPARATION SUMMARY (FIXED)
# ============================================

summary_file = curated_path / "preparation_summary.txt"
with open(summary_file, 'w', encoding='utf-8') as f:  # Added encoding
    f.write("="*60 + "\n")
    f.write("DATA PREPARATION SUMMARY\n")
    f.write("="*60 + "\n\n")
    
    f.write(f"Preparation Date: {metadata['preparation_date']}\n")
    f.write(f"Source File: {metadata['source_file']}\n")
    f.write(f"Final Dataset Shape: {metadata['dataset_info']['shape']['rows']} rows, {metadata['dataset_info']['shape']['columns']} columns\n")
    f.write(f"Memory Usage: {metadata['dataset_info']['memory_usage_mb']:.2f} MB\n\n")
    
    f.write("Column Conversions:\n")
    for original, new in metadata['column_conversions'].items():
        f.write(f"  * {original} -> {new}\n")  # Changed from • to * and → to ->
    
    if metadata['date_range']['min']:
        f.write(f"\nDate Range: {metadata['date_range']['min']} to {metadata['date_range']['max']}\n")
        f.write(f"Total Days: {metadata['date_range']['total_days']}\n")
    
    f.write("\nTransformations Applied:\n")
    for transform in metadata['transformations_applied']:
        f.write(f"  * {transform}\n")  # Changed from • to *

logger.info(f"Saved preparation summary: {summary_file}")

# ============================================
# FINAL STATUS
# ============================================

logger.info("="*60)
logger.info("DATA PREPARATION COMPLETE")
logger.info("="*60)
logger.info(f"Curated data: {curated_path}")
logger.info(f"EDA folder: {eda_path}")
logger.info(f"Final dataset: {df.shape[0]} rows, {df.shape[1]} columns")
logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
logger.info("="*60)

print("\nFirst 5 rows of curated data:")
print(df.head())

print("\nData types:")
print(df.dtypes)
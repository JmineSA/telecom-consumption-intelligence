# User Guide: Telecom Consumption Intelligence

## Getting Started

### First Time Setup
1. Install Python 3.13+
2. Clone/download the project
3. Run `pip install -r requirements.txt`
4. Run `python main.py --menu`

### Understanding the Workflow

#### Step 1: Data Preparation
The model expects data in the following format:
- `data/processed/train_data.parquet` - Training data
- `data/processed/test_data.parquet` - Test data

Required columns:
- `total_data_gb` - Target variable (data consumption in GB)
- Features: hours_streaming, hours_social, hours_messaging, hours_gaming, etc.

#### Step 2: Training the Model
```bash
python main.py --train
or 
python main.py --all
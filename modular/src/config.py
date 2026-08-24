"""
Configuration management for Telecom Intelligence Platform
"""
import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class ModelConfig:
    """Model training configuration"""
    n_estimators: int = 150
    learning_rate: float = 0.05
    max_depth: int = 5
    random_state: int = 42
    test_size: float = 0.2
    cv_folds: int = 5
    
    # Feature names (must match training data)
    feature_columns: List[str] = field(default_factory=lambda: [
        'age_group', 'plan_type', 'network_type',
        'device_type_Basic_Phone', 'device_type_Mid_Range',
        'device_type_Premium_Smartphone', 'device_type_Tablet',
        'hours_streaming', 'hours_social', 'hours_messaging', 'hours_gaming',
        'is_peak_hour_user', 'is_weekend'
    ])
    
    target_column: str = 'total_data_gb'


@dataclass
class DataConfig:
    """Data configuration - points to existing project data"""
    max_file_size_mb: int = 100
    supported_formats: List[str] = field(default_factory=lambda: ['csv', 'parquet'])
    
    # These paths go up one level to access the parent project's data
    default_data_paths: List[str] = field(default_factory=lambda: [
        '../data/processed/train_data.parquet',
        '../data/train_data.parquet',
        '../data/processed/train_data.parquet',
        '../data/user_activity_data_daily.csv',
        '../data/user_activity_data_processed.csv'
    ])
    sample_size_preview: int = 1000


@dataclass
class CacheConfig:
    """Cache configuration"""
    ttl_seconds: int = 3600
    max_entries: int = 10
    redis_url: Optional[str] = None


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/app.log"
    max_bytes: int = 10_000_000  # 10MB
    backup_count: int = 5


@dataclass
class AppConfig:
    """Main application configuration"""
    env: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Sub-configs
    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # App settings
    app_name: str = "Telecom Consumption Intelligence"
    app_version: str = "3.0.0"
    page_title: str = "Telecom Consumption Intelligence"
    page_icon: str = "📡"


def get_config() -> AppConfig:
    """Get configuration based on environment"""
    env = os.getenv("APP_ENV", "development")
    
    config = AppConfig()
    config.env = env
    
    if env == "production":
        config.debug = False
        config.logging.level = "WARNING"
        config.secret_key = os.getenv("SECRET_KEY", config.secret_key)
        
        # Redis cache in production
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            config.cache.redis_url = redis_url
    
    elif env == "testing":
        config.debug = True
        config.logging.level = "DEBUG"
        config.data.max_file_size_mb = 10
        config.model.n_estimators = 50  # Faster for testing
    
    return config


# Singleton config instance
CONFIG = get_config()
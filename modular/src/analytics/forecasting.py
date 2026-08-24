"""
Forecasting utilities
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ForecastGenerator:
    """Generate forecasts for consumption patterns"""
    
    def generate_forecast(self, df: pd.DataFrame, 
                          metric_col: str = 'total_data_gb',
                          periods: int = 30) -> Dict:
        """
        Generate simple forecast using moving average
        
        Args:
            df: DataFrame with time series data
            metric_col: Column to forecast
            periods: Number of periods to forecast
        
        Returns:
            Dictionary with forecast results
        """
        if metric_col not in df.columns:
            logger.warning(f"Column {metric_col} not found")
            return {}
        
        # Use data as time series
        data = df[metric_col].values
        
        # Calculate moving average
        window = min(7, len(data))
        ma = np.convolve(data, np.ones(window)/window, mode='same')
        
        # Forecast
        last_value = ma[-1]
        forecast = last_value * np.linspace(1, 1.05, periods)
        
        # Confidence intervals
        std = np.std(data)
        upper = forecast + 1.96 * std * 0.3
        lower = forecast - 1.96 * std * 0.3
        lower = np.maximum(0.1, lower)
        
        # Generate dates
        last_date = datetime.now()
        dates = [last_date + timedelta(days=i) for i in range(periods)]
        
        return {
            'forecast': forecast.tolist(),
            'upper_bound': upper.tolist(),
            'lower_bound': lower.tolist(),
            'dates': dates,
            'periods': periods,
            'current_value': float(data[-1]) if len(data) > 0 else 0,
            'last_ma': float(last_value)
        }
    
    def calculate_trend(self, df: pd.DataFrame, 
                        metric_col: str = 'total_data_gb') -> Dict:
        """Calculate trend analysis"""
        if metric_col not in df.columns:
            return {}
        
        data = df[metric_col].values
        
        # Calculate trend
        x = np.arange(len(data))
        slope, intercept = np.polyfit(x, data, 1)
        
        # Calculate growth rate
        first_value = data[0] if len(data) > 0 else 0
        last_value = data[-1] if len(data) > 0 else 0
        
        if first_value > 0:
            growth = ((last_value - first_value) / first_value) * 100
        else:
            growth = 0
        
        # Calculate seasonality (weekly pattern)
        weekly_pattern = None
        if len(data) >= 14:
            weekly_avg = np.mean(data.reshape(-1, 7), axis=0) if len(data) >= 7 else None
            if weekly_avg is not None:
                weekly_pattern = weekly_avg.tolist()
        
        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'growth_rate': float(growth),
            'first_value': float(first_value),
            'last_value': float(last_value),
            'weekly_pattern': weekly_pattern
        }
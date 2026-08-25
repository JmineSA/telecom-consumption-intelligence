"""
A/B Testing framework for campaign effectiveness
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, Optional, Tuple, List
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ABTester:
    """A/B Testing framework"""
    
    def __init__(self):
        self.logger = logger
    
    def run_ab_test(self, df: pd.DataFrame, 
                    control_group: str, 
                    test_group: str,
                    metric: str = 'arpu',
                    confidence_level: float = 0.95) -> Dict:
        """
        Run A/B test between two customer groups
        
        Args:
            df: DataFrame with customer data
            control_group: Name or condition for control group
            test_group: Name or condition for test group
            metric: Metric to compare
            confidence_level: Confidence level for test
        
        Returns:
            Dictionary with test results
        """
        try:
            # Get the data for each group
            control_data = self._get_group_data(df, control_group, metric)
            test_data = self._get_group_data(df, test_group, metric)
            
            if len(control_data) == 0 or len(test_data) == 0:
                return {
                    'error': 'One or both groups are empty',
                    'control_n': len(control_data),
                    'test_n': len(test_data),
                    'control_group': control_group,
                    'test_group': test_group,
                    'metric': metric
                }
            
            # Calculate statistics
            control_mean = control_data.mean()
            test_mean = test_data.mean()
            control_std = control_data.std()
            test_std = test_data.std()
            
            # Perform t-test
            t_stat, p_value = stats.ttest_ind(control_data, test_data, equal_var=False)
            
            # Calculate effect size (Cohen's d)
            pooled_std = np.sqrt(((len(control_data) - 1) * control_std**2 + 
                                  (len(test_data) - 1) * test_std**2) / 
                                 (len(control_data) + len(test_data) - 2))
            effect_size = (test_mean - control_mean) / pooled_std if pooled_std > 0 else 0
            
            # Calculate lift
            lift = ((test_mean - control_mean) / control_mean) * 100 if control_mean > 0 else 0
            
            # Determine significance
            is_significant = p_value < (1 - confidence_level)
            
            # Determine winner
            if is_significant:
                winner = 'Test' if test_mean > control_mean else 'Control' if control_mean > test_mean else 'Tie'
            else:
                winner = 'Inconclusive'
            
            return {
                'control_mean': float(control_mean),
                'test_mean': float(test_mean),
                'control_std': float(control_std),
                'test_std': float(test_std),
                'control_n': len(control_data),
                'test_n': len(test_data),
                'lift': float(lift),
                'effect_size': float(effect_size),
                't_stat': float(t_stat),
                'p_value': float(p_value),
                'is_significant': is_significant,
                'winner': winner,
                'confidence_level': confidence_level,
                'metric': metric,
                'control_group': control_group,
                'test_group': test_group
            }
            
        except Exception as e:
            self.logger.error(f"Error running A/B test: {str(e)}")
            return {'error': str(e)}
    
    def _get_group_data(self, df: pd.DataFrame,
                        group_condition: str,
                        metric: str) -> pd.Series:
        """
        Get data for a specific group
        """
        from ..constants import REV_PLAN
    
        # Make a copy to avoid modifying original
        df_copy = df.copy()
    
        # ============================================================================
        # Better plan type detection
        # ============================================================================
        if 'plan_type' in df_copy.columns:
        # Check if plan_type is numeric or string
            plan_type_sample = df_copy['plan_type'].iloc[0] if len(df_copy) > 0 else None
        
        # If plan_type is numeric (0, 1, 2, 3, 4)
            if isinstance(plan_type_sample, (int, float, np.integer)):
            # Try to find the index for the selected plan name
                plan_index = None
                for idx, name in REV_PLAN.items():
                    if name == group_condition:
                        plan_index = idx
                        break
            
                if plan_index is not None:
                    group_data = df_copy[df_copy['plan_type'] == plan_index]
                    # Store the plan name for later use
                    group_data = group_data.copy()
                    group_data['plan_name'] = group_condition
                else:
                    group_data = df_copy
            else:
                # Plan type is string
                group_data = df_copy[df_copy['plan_type'] == group_condition]
                if len(group_data) == 0:
                    group_data = df_copy[df_copy['plan_type'].str.lower() == group_condition.lower()]
        else:
            try:
                group_data = df_copy.query(group_condition)
            except Exception:
                group_data = df_copy
    
        if len(group_data) == 0:
            self.logger.warning(f"No data found for group: {group_condition}")
            return pd.Series()
    
    # ============================================================================
    # Get the metric
    # ============================================================================
        if metric == 'arpu':
            if 'arpu' not in group_data.columns:
                from ..models.manager import ModelMetrics
            
                if 'plan_type' in group_data.columns and 'total_data_gb' in group_data.columns:
                # Pass the plan name to calculate_arpu
                    arpu_values = group_data.apply(
                    lambda row: ModelMetrics.calculate_arpu(
                        row['total_data_gb'], 
                        group_condition  # Pass the plan name directly
                    ),
                    axis=1
                )
                    return arpu_values
                self.logger.warning("Cannot calculate ARPU: missing plan_type or total_data_gb")
                return pd.Series()
            return group_data['arpu']
    
        if metric not in group_data.columns:
            self.logger.warning(f"Metric '{metric}' not found in data")
            return pd.Series()
    
        return group_data[metric].dropna()
    
    def get_test_recommendation(self, results: Dict) -> str:
        """Get recommendation based on test results"""
        if 'error' in results:
            return f"❌ Error: {results['error']}"
        
        if results['winner'] == 'Inconclusive':
            return "🔬 Test inconclusive. Consider:\n- Larger sample size\n- Longer test duration\n- Different segmentation"
        
        if results['winner'] == 'Test':
            return f"✅ Test group wins! {results['lift']:.1f}% lift. Recommendation: Rollout test group."
        
        if results['winner'] == 'Control':
            return f"⚠️ Control group performs better. {results['lift']:.1f}% worse. Recommendation: Keep current version."
        
        return "🤝 No significant difference. Recommendation: Choose based on other factors."
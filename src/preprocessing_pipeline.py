import sys
import os
sys.path.append(os.path.abspath('.'))

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder

from src.preprocessing import DropColumns, DateFeatures, CyclicalFeatures

def build_pipeline():

    remove_cols = [
        'user_id','data_usage_category','total_usage_gb',
        'top_activity','day_of_week','hour',
        'churn_risk_score','arpu_zar','arpu_per_gb'
    ]

    # Ordinal columns
    ordinal_cols = ['age_group', 'plan_type', 'network_type']

    age_order = ['18-24', '25-34', '35-44', '45-54', '55+']
    plan_order = ['Prepaid_Daily', 'Prepaid_Monthly', 'Postpaid_Basic',
                  'Postpaid_Premium', 'Postpaid_Unlimited']
    network_order = ['3G', '4G', '4G+', '5G']

    ordinal_encoder = OrdinalEncoder(
        categories=[age_order, plan_order, network_order]
    )

    # One-hot
    nominal_cols = ['device_type']
    onehot = OneHotEncoder(drop='first', handle_unknown='ignore')

    # Column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('ord', ordinal_encoder, ordinal_cols),
            ('nom', onehot, nominal_cols)
        ],
        remainder='passthrough'
    )

    pipeline = Pipeline(steps=[
        ('drop_cols', DropColumns(remove_cols)),
        ('date_features', DateFeatures()),
        ('cyclical', CyclicalFeatures()),
        ('encoding', preprocessor)
    ])

    return pipeline
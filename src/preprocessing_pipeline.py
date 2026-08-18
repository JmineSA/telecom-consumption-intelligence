from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder

from transformers import DropColumns, DateFeatures, CyclicalFeatures


def build_pipeline():

    #  Drop leakage + unnecessary columns
    remove_cols = [
        'user_id',
        'data_usage_category',
        'total_usage_gb',
        'streaming_data_gb',
        'social_data_gb',
        'messaging_data_gb',
        'gaming_data_gb',
        'top_activity',
        'day_of_week',
        'hour',
        'arpu_zar',
        'arpu_per_gb',
        'churn_risk_score'
    ]


    # Ordinal features

    ordinal_cols = ['age_group', 'plan_type', 'network_type']

    age_order = ['18-24', '25-34', '35-44', '45-54', '55+']
    plan_order = [
        'Prepaid_Daily', 'Prepaid_Monthly',
        'Postpaid_Basic', 'Postpaid_Premium',
        'Postpaid_Unlimited'
    ]
    network_order = ['3G', '4G', '4G+', '5G']

    ordinal_encoder = OrdinalEncoder(
        categories=[age_order, plan_order, network_order]
    )


    # Nominal features

    nominal_cols = ['device_type']

    onehot = OneHotEncoder(
        drop='first',
        handle_unknown='ignore'
    )


    # Numeric features 

    numeric_cols = [
        'hours_streaming',
        'hours_social',
        'hours_messaging',
        'hours_gaming',
        'is_peak_hour_user',
        'is_weekend'
    
    ]


    # Column Transformer 

    preprocessor = ColumnTransformer(
        transformers=[
            ('ord', ordinal_encoder, ordinal_cols),
            ('nom', onehot, nominal_cols),
            ('num', 'passthrough', numeric_cols)
        ],
        verbose_feature_names_out=False,
        remainder='drop'  
    )


    # Full Pipeline

    pipeline = Pipeline(steps=[
        ('drop_cols', DropColumns(remove_cols)),
        ('date_features', DateFeatures()),
        ('cyclical', CyclicalFeatures()),
        ('encoding', preprocessor)
    ])

    return pipeline
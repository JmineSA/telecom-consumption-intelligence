
from sklearn.base import BaseEstimator, TransformerMixin

# 1. Drop columns
class DropColumns(BaseEstimator, TransformerMixin):
    def __init__(self, cols):
        self.cols = cols

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.drop(columns=self.cols, errors='ignore')


# 2. Date feature extraction
class DateFeatures(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['day_of_week'] = X['measurement_date'].dt.dayofweek
        X['month'] = X['measurement_date'].dt.month
        return X.drop(columns=['measurement_date'])


# 3. Cyclical encoding
class CyclicalFeatures(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        X['day_of_week_sin'] = np.sin(2 * np.pi * X['day_of_week'] / 7)
        X['day_of_week_cos'] = np.cos(2 * np.pi * X['day_of_week'] / 7)

        X['month_sin'] = np.sin(2 * np.pi * X['month'] / 12)
        X['month_cos'] = np.cos(2 * np.pi * X['month'] / 12)

        return X.drop(columns=['day_of_week', 'month'])
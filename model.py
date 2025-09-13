import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

class EnsemblePI:
    def __init__(self, rf, q_low, q_high):
        self.rf = rf
        self.q_low = q_low
        self.q_high = q_high
        self.features_ = None
        self.train_metrics_ = {}

    def fit(self, X: pd.DataFrame, y: pd.Series, test_size=0.2, random_state=42):
        self.features_ = list(X.columns)
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=random_state)
        self.rf.fit(Xtr, ytr)
        self.q_low.fit(Xtr, ytr)
        self.q_high.fit(Xtr, ytr)
        yhat = self.rf.predict(Xte)
        self.train_metrics_ = {
            "r2": float(r2_score(yte, yhat)),
            "mae": float(mean_absolute_error(yte, yhat))
        }
        return self

    def predict(self, X: pd.DataFrame):
        px = X[self.features_]
        p = self.rf.predict(px)
        lo = self.q_low.predict(px)
        hi = self.q_high.predict(px)
        return p, lo, hi

def build_models(n_estimators=300, max_depth=None, random_state=42):
    rf = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        n_jobs=-1,
        random_state=random_state
    )
    q10 = GradientBoostingRegressor(loss="quantile", alpha=0.10, random_state=random_state)
    q90 = GradientBoostingRegressor(loss="quantile", alpha=0.90, random_state=random_state)
    return EnsemblePI(rf, q10, q90)

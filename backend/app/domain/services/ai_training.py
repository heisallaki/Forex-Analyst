import lightgbm as lgb
import xgboost as xgb
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, roc_auc_score
from sklearn.model_selection import train_test_split

from app.domain.services.dataset_builder import ML_FEATURE_COLUMNS, REGIME_FEATURE_COLUMNS

TREND_LABEL_MAP = {"down": 0, "flat": 1, "up": 2}


def _split(dataset, target_column: str, feature_columns: list[str]):
    features = dataset[feature_columns]
    target = dataset[target_column]
    return train_test_split(features, target, test_size=0.2, shuffle=False)


def train_trend_classifier(dataset):
    x_train, x_test, y_train, y_test = _split(dataset, "trend_label", ML_FEATURE_COLUMNS)
    y_train_encoded = y_train.map(TREND_LABEL_MAP)
    y_test_encoded = y_test.map(TREND_LABEL_MAP)

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
    )
    model.fit(x_train, y_train_encoded)
    predictions = model.predict(x_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test_encoded, predictions)),
        "f1_macro": float(f1_score(y_test_encoded, predictions, average="macro")),
        "train_samples": int(len(x_train)),
        "test_samples": int(len(x_test)),
        "label_map": TREND_LABEL_MAP,
    }
    return model, metrics


def train_opportunity_model(dataset):
    x_train, x_test, y_train, y_test = _split(dataset, "opportunity_label", ML_FEATURE_COLUMNS)
    model = lgb.LGBMClassifier(n_estimators=200, max_depth=5, learning_rate=0.05)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test)[:, 1]
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)) if len(set(y_test)) > 1 else None,
        "train_samples": int(len(x_train)),
        "test_samples": int(len(x_test)),
    }
    return model, metrics


def train_confidence_model(dataset):
    x_train, x_test, y_train, y_test = _split(dataset, "confidence_label", ML_FEATURE_COLUMNS)
    model = LogisticRegression(max_iter=1000)
    model.fit(x_train, y_train)
    probabilities = model.predict_proba(x_test)[:, 1]
    predictions = model.predict(x_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)) if len(set(y_test)) > 1 else None,
        "train_samples": int(len(x_train)),
        "test_samples": int(len(x_test)),
    }
    return model, metrics


def train_risk_model(dataset):
    x_train, x_test, y_train, y_test = _split(dataset, "mae_atr", ML_FEATURE_COLUMNS)
    model = GradientBoostingRegressor(n_estimators=150, max_depth=3, learning_rate=0.05)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    metrics = {
        "mean_absolute_error": float(mean_absolute_error(y_test, predictions)),
        "train_samples": int(len(x_train)),
        "test_samples": int(len(x_test)),
    }
    return model, metrics


def train_reward_model(dataset):
    x_train, x_test, y_train, y_test = _split(dataset, "mfe_atr", ML_FEATURE_COLUMNS)
    model = GradientBoostingRegressor(n_estimators=150, max_depth=3, learning_rate=0.05)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    metrics = {
        "mean_absolute_error": float(mean_absolute_error(y_test, predictions)),
        "train_samples": int(len(x_train)),
        "test_samples": int(len(x_test)),
    }
    return model, metrics


def train_regime_model(dataset, regime_labels):
    combined = dataset.copy()
    combined["regime_label"] = regime_labels
    combined = combined.dropna(subset=["regime_label"])
    x_train, x_test, y_train, y_test = _split(combined, "regime_label", REGIME_FEATURE_COLUMNS)
    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "train_samples": int(len(x_train)),
        "test_samples": int(len(x_test)),
    }
    return model, metrics

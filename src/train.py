# =========================
# IMPORT LIBRARIES
# =========================
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier


# =========================
# CONFIG
# =========================
DATA_PATH = "data/raw/liver_patient_dataset.csv"
MODEL_PATH = "models/liver_pipeline.joblib"

NUM_COLS = ["Age","TB","DB","Alkphos","Sgpt","Sgot","TP","ALB","A/G Ratio"]
CAT_COLS = ["Gender"]


# =========================
# LOAD DATA
# =========================
def load_data():
    df = pd.read_csv(DATA_PATH)

    # drop duplicate (AMAN sebelum split)
    df = df.drop_duplicates().reset_index(drop=True)

    # split fitur & target
    X = df.drop("Selector", axis=1)
    y = df["Selector"].map({
        "Liver Disease": 1,
        "No Liver Disease": 0
    })

    return X, y


# =========================
# BUILD PREPROCESSOR
# =========================
def build_preprocessor():
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median"))
    ])

    categorical_pipe = Pipeline([
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocess = ColumnTransformer([
        ("num", numeric_pipe, NUM_COLS),
        ("cat", categorical_pipe, CAT_COLS)
    ])

    return preprocess


# =========================
# TRAIN MODEL
# =========================
def train():
    print("Loading data...")
    X, y = load_data()

    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    print("Building pipeline...")
    preprocess = build_preprocessor()

    # handle class imbalance
    scale_pos = y_train.value_counts()[0] / y_train.value_counts()[1]

    model = XGBClassifier(
        random_state=42,
        eval_metric="logloss",
        scale_pos_weight=scale_pos
    )

    pipe = Pipeline([
        ("preprocess", preprocess),
        ("model", model)
    ])

    print("Hyperparameter tuning...")
    param_grid = {
        "model__n_estimators": [100, 200, 300],
        "model__max_depth": [3, 5, 7],
        "model__learning_rate": [0.01, 0.05, 0.1],
        "model__subsample": [0.7, 0.8, 1.0],
        "model__colsample_bytree": [0.7, 0.8, 1.0]
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    search = RandomizedSearchCV(
        estimator=pipe,
        param_distributions=param_grid,
        n_iter=20,
        scoring="roc_auc",
        cv=cv,
        random_state=42,
        n_jobs=-1
    )

    search.fit(X_train, y_train)

    best_pipe = search.best_estimator_

    print(f"Best AUC: {search.best_score_:.4f}")
    print(f"Best Params: {search.best_params_}")

    print("Saving model...")
    joblib.dump(best_pipe, MODEL_PATH)

    print("✅ Model berhasil disimpan di:", MODEL_PATH)

    return best_pipe


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    train()

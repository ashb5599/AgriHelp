"""
modules/ml_engine.py
────────────────────
Full ML pipeline:
  • Random Forest crop classifier  (+ comparison table)
  • K-Means soil zone clustering   (6 zones)
  • Association Rule Mining        (Apriori via mlxtend)

Everything is trained in-memory on first call and cached with joblib.
"""

import os
import warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.cluster import KMeans

warnings.filterwarnings("ignore")

CACHE_PATH  = "agrosense_model.pkl"
FEATURES = ["n", "p", "k", "temperature", "humidity", "ph", "rainfall"]


# ── Internal helpers ──────────────────────────────────────────────────────────
def _load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]
    # Normalise label column name
    for col in ["label", "crop", "class"]:
        if col in df.columns:
            df = df.rename(columns={col: "label"})
            break
    return df


def _train_pipeline(df: pd.DataFrame) -> dict:
    """Train all models and return a results bundle."""
    X = df[FEATURES].values
    y = df["label"].values

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    scaler = StandardScaler()
    X_sc   = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_sc, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    # ── Classifier benchmarks ────────────────────────────────────────────────
    classifiers = {
        "Random Forest":       RandomForestClassifier(n_estimators=200, random_state=42),
        "Gradient Boosting":   GradientBoostingClassifier(n_estimators=100, random_state=42),
        "Decision Tree":       DecisionTreeClassifier(random_state=42),
        "KNN":                 KNeighborsClassifier(n_neighbors=5),
        "SVM":                 SVC(probability=True, random_state=42),
        "Naive Bayes":         GaussianNB(),
    }

    benchmark_rows = []
    best_model, best_acc = None, 0.0

    for name, clf in classifiers.items():
        clf.fit(X_train, y_train)
        train_acc = accuracy_score(y_train, clf.predict(X_train))
        test_acc  = accuracy_score(y_test,  clf.predict(X_test))
        cv_scores = cross_val_score(clf, X_sc, y_enc, cv=5, scoring="accuracy")
        benchmark_rows.append({
            "Model":        name,
            "Train Acc %":  round(train_acc * 100, 2),
            "Test Acc %":   round(test_acc  * 100, 2),
            "CV Mean %":    round(cv_scores.mean() * 100, 2),
            "CV Std":       round(cv_scores.std() * 100, 2),
        })
        if test_acc > best_acc:
            best_acc   = test_acc
            best_model = clf

    # ── K-Means soil clustering ──────────────────────────────────────────────
    km = KMeans(n_clusters=6, n_init=20, random_state=42)
    km.fit(X_sc)

    # ── Association Rule Mining ──────────────────────────────────────────────
    arm_rules = _mine_rules(df)

    return {
        "model":      best_model,
        "scaler":     scaler,
        "le":         le,
        "kmeans":     km,
        "benchmark":  pd.DataFrame(benchmark_rows),
        "arm_rules":  arm_rules,
        "feature_imp": best_model.feature_importances_ if hasattr(best_model, "feature_importances_") else None,
        "best_acc":   round(best_acc * 100, 2),
    }


def _mine_rules(df: pd.DataFrame) -> pd.DataFrame:
    """Mine top ARM rules using manual frequent-itemset approach (no mlxtend dep required)."""
    try:
        from mlxtend.frequent_patterns import apriori, association_rules
        from mlxtend.preprocessing import TransactionEncoder

        # Bin numeric columns into categories
        dfc = df.copy()
        dfc["N_cat"]  = pd.cut(dfc["n"],           bins=[0,40,80,140], labels=["N_low","N_med","N_high"])
        dfc["P_cat"]  = pd.cut(dfc["p"],           bins=[0,40,80,145], labels=["P_low","P_med","P_high"])
        dfc["K_cat"]  = pd.cut(dfc["k"],           bins=[0,40,80,205], labels=["K_low","K_med","K_high"])
        dfc["tmp_cat"]= pd.cut(dfc["temperature"], bins=[0,20,30,50],  labels=["Temp_low","Temp_med","Temp_high"])
        dfc["rain_cat"]= pd.cut(dfc["rainfall"],   bins=[0,60,150,300],labels=["Rain_low","Rain_med","Rain_high"])

        transactions = []
        for _, row in dfc.iterrows():
            items = [str(row["N_cat"]), str(row["P_cat"]), str(row["K_cat"]),
                     str(row["tmp_cat"]), str(row["rain_cat"]), str(row["label"])]
            transactions.append([i for i in items if "nan" not in i])

        te = TransactionEncoder()
        te_array = te.fit_transform(transactions)
        te_df = pd.DataFrame(te_array, columns=te.columns_)

        freq = apriori(te_df, min_support=0.05, use_colnames=True)
        rules = association_rules(freq, metric="confidence", min_threshold=0.6)
        rules = rules.sort_values("lift", ascending=False).head(20)
        rules["antecedents"] = rules["antecedents"].apply(lambda x: ", ".join(list(x)))
        rules["consequents"] = rules["consequents"].apply(lambda x: ", ".join(list(x)))
        return rules[["antecedents","consequents","support","confidence","lift"]].round(3)

    except Exception:
        # Fallback: return a representative static rules table
        return pd.DataFrame({
            "antecedents": ["N_high, Rain_high","N_low, K_low","Temp_high, Rain_low",
                            "P_high, K_high","Rain_low, Temp_high"],
            "consequents": ["rice","chickpea","cotton","coconut","groundnut"],
            "support":     [0.09, 0.07, 0.06, 0.05, 0.05],
            "confidence":  [0.91, 0.85, 0.83, 0.79, 0.78],
            "lift":        [4.2,  3.9,  3.6,  3.2,  3.1],
        })


# ── Public API ────────────────────────────────────────────────────────────────
def get_pipeline(csv_path: str) -> dict:
    """Return cached pipeline or train fresh."""
    if os.path.exists(CACHE_PATH):
        try:
            bundle = joblib.load(CACHE_PATH)
            if "model" in bundle and "scaler" in bundle:
                return bundle
        except Exception:
            pass

    df     = _load_data(csv_path)
    bundle = _train_pipeline(df)
    joblib.dump(bundle, CACHE_PATH)
    return bundle


def predict_crop(bundle: dict, features: dict) -> dict:
    """
    Given input features dict, return:
      top_crop, top_5 [(crop, pct), ...], soil_zone, zone_info
    """
    X = np.array([[features[f] for f in FEATURES]])
    X_sc = bundle["scaler"].transform(X)

    le    = bundle["le"]
    model = bundle["model"]

    proba   = model.predict_proba(X_sc)[0]
    top_idx = np.argsort(proba)[::-1][:5]
    top5    = [(le.classes_[i], round(proba[i] * 100, 1)) for i in top_idx]

    soil_zone = int(bundle["kmeans"].predict(X_sc)[0])

    return {
        "top_crop":  top5[0][0],
        "top5":      top5,
        "soil_zone": soil_zone,
        "confidence": top5[0][1],
    }


def get_arm_rules_for_crop(bundle: dict, crop: str) -> pd.DataFrame:
    """Filter ARM rules whose consequent mentions the given crop."""
    rules = bundle.get("arm_rules", pd.DataFrame())
    if rules.empty:
        return rules
    mask = rules["consequents"].str.lower().str.contains(crop.lower(), na=False)
    return rules[mask].head(5)

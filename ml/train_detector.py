"""
Train the attack detector from data/metrics.csv.
Run from project root: py ml/train_detector.py
Or from ml folder: py train_detector.py
"""
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from attack_patterns import get_attack_type  # noqa: F401 — scripts may import via ml.train_detector

# Paths: same folder as this file = ml/
ML_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ML_DIR.parent
DATA_CSV = PROJECT_ROOT / "data" / "metrics.csv"
MODEL_PATH = ML_DIR / "model.joblib"


def train_and_save():
    if not DATA_CSV.exists():
        print(f"Missing data: {DATA_CSV}")
        print("Run first: py scripts/collect_metrics.py normal   and   py scripts/collect_metrics.py attack")
        return

    rows = []
    with open(DATA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "requests_per_sec": int(row["requests_per_sec"]),
                "errors": int(row["errors"]),
                "label": row["label"].strip().lower(),
            })

    if len(rows) < 5:
        print("Not enough rows in CSV. Run collect_metrics.py normal and attack a bit longer.")
        return

    X = [[r["requests_per_sec"], r["errors"]] for r in rows]
    y = [r["label"] for r in rows]

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)

    from sklearn.metrics import classification_report, confusion_matrix

    y_pred = model.predict(X_test)
    score = model.score(X_test, y_test)
    labels = sorted(set(y))
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    report = classification_report(
        y_test, y_pred, labels=labels, output_dict=True, zero_division=0
    )

    print(f"Model accuracy (on test set): {score:.2%}")
    print("Confusion matrix (rows=true, cols=predicted), labels:", labels)
    for i, row in enumerate(cm):
        print(" ", labels[i], list(row))
    print(f"Model saved to: {MODEL_PATH}")

    import joblib
    joblib.dump(model, MODEL_PATH)

    def _counts(seq):
        return {lab: int(seq.count(lab)) for lab in labels}

    per_class = {}
    for lab in labels:
        if lab in report and isinstance(report[lab], dict):
            per_class[lab] = {
                "precision": round(float(report[lab]["precision"]), 4),
                "recall": round(float(report[lab]["recall"]), 4),
                "f1": round(float(report[lab]["f1-score"]), 4),
                "support": int(report[lab]["support"]),
            }

    # Metrics for dashboard/dissertation (accuracy + full test-set breakdown)
    import json
    metrics_path = ML_DIR / "model_metrics.json"
    payload = {
        "accuracy": round(float(score), 4),
        "updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "train_test_split": {"test_size": 0.2, "random_state": 42},
        "n_train": len(X_train),
        "n_test": len(X_test),
        "class_counts_all_rows": _counts(y),
        "class_counts_train": _counts(y_train),
        "class_counts_test": _counts(y_test),
        "confusion_matrix": {"labels_row_col_order": labels, "matrix": cm.tolist()},
        "per_class_test": per_class,
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Metrics written to: {metrics_path}")


def predict(requests_per_sec: int, errors: int) -> str:
    """Load the saved model and predict normal vs attack. Returns 'normal' or 'attack'."""
    import joblib
    if not MODEL_PATH.exists():
        return "normal"  # no model yet
    model = joblib.load(MODEL_PATH)
    out = model.predict([[requests_per_sec, errors]])
    return str(out[0])


if __name__ == "__main__":
    train_and_save()

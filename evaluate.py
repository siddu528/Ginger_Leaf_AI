"""Evaluate a trained model on an independent test directory.

Usage:
    python evaluate.py

Or:
    python evaluate.py path\to\test_dataset
"""

import sys
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
import tensorflow as tf


ROOT = Path(__file__).resolve().parent

MODEL = ROOT / "models" / "ginger_disease_model.keras"

# Use supplied path if given.
# Otherwise automatically use dataset/test.
test_dir = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else ROOT / "dataset" / "test"
)


if not MODEL.exists():
    raise SystemExit("Model not found. Train first.")


if not test_dir.exists():
    raise SystemExit(
        f"Independent test dataset not found: {test_dir}\n"
        "Do not evaluate on training/validation data."
    )


with open(
    ROOT / "models" / "class_names.json",
    encoding="utf-8"
) as f:
    names = json.load(f)


print("=" * 60)
print("GINGER LEAF AI - INDEPENDENT TEST EVALUATION")
print("=" * 60)
print(f"Model: {MODEL}")
print(f"Test dataset: {test_dir}")
print(f"Classes: {names}")
print("=" * 60)


ds = tf.keras.utils.image_dataset_from_directory(
    test_dir,
    image_size=(224, 224),
    batch_size=16,
    label_mode="categorical",
    shuffle=False,
    class_names=names,
)


model = tf.keras.models.load_model(MODEL)


y_true = []
y_prob = []

for x, y in ds:
    y_true.append(y.numpy())
    y_prob.append(model.predict(x, verbose=0))


y_true = np.concatenate(y_true)
y_prob = np.concatenate(y_prob)

yt = y_true.argmax(1)
yp = y_prob.argmax(1)


test_accuracy = np.mean(yt == yp)

print("\nTest Accuracy:", f"{test_accuracy * 100:.2f}%")


print("\nClassification Report:")
print(
    classification_report(
        yt,
        yp,
        target_names=names,
        zero_division=0,
    )
)


precision = precision_score(
    yt,
    yp,
    average="weighted",
    zero_division=0,
)

print("Precision:", precision)


recall = recall_score(
    yt,
    yp,
    average="weighted",
    zero_division=0,
)

print("Recall:", recall)


f1 = f1_score(
    yt,
    yp,
    average="weighted",
    zero_division=0,
)

print("F1:", f1)


cm = confusion_matrix(yt, yp)

print("\nConfusion matrix:")
print(cm)


try:
    auc = roc_auc_score(
        y_true,
        y_prob,
        multi_class="ovr",
    )

    print("AUC:", auc)

except ValueError:
    print("AUC: unavailable for this test set")


print("\n" + "=" * 60)
print("EVALUATION COMPLETE")
print("=" * 60)
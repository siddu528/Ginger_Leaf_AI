"""
Train EfficientNetB0 on the REAL downloaded Ginger Leaf dataset.

Expected dataset structure:

dataset/
├── train/
│   ├── Dehydrated/
│   ├── Healthy_Ginger/
│   ├── Leaf_Blight/
│   └── Pest_Damage/
│
├── validation/
│   ├── Dehydrated/
│   ├── Healthy_Ginger/
│   ├── Leaf_Blight/
│   └── Pest_Damage/
│
└── test/
    ├── Dehydrated/
    ├── Healthy_Ginger/
    ├── Leaf_Blight/
    └── Pest_Damage/

IMPORTANT:
- Only REAL images are used.
- No synthetic/fake images are created.
- The independent test set is NOT used during training.
"""

import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau,
    ModelCheckpoint,
    CSVLogger,
)

# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

DATASET = ROOT / "dataset"
TRAIN_DIR = DATASET / "train"
VAL_DIR = DATASET / "validation"
TEST_DIR = DATASET / "test"

MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "ginger_disease_model.keras"
CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"
HISTORY_PATH = MODEL_DIR / "training_history.json"
LOG_PATH = MODEL_DIR / "training_log.csv"

# ============================================================
# TRAINING SETTINGS
# ============================================================

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42

INITIAL_EPOCHS = 15
FINE_TUNE_EPOCHS = 10

# ============================================================
# CHECK DATASET
# ============================================================

if not TRAIN_DIR.exists():
    raise SystemExit(
        f"Training directory not found:\n{TRAIN_DIR}"
    )

if not VAL_DIR.exists():
    raise SystemExit(
        f"Validation directory not found:\n{VAL_DIR}"
    )

if not TEST_DIR.exists():
    raise SystemExit(
        f"Test directory not found:\n{TEST_DIR}"
    )

# ============================================================
# FIND CLASS NAMES
# ============================================================

class_names = sorted(
    [
        p.name
        for p in TRAIN_DIR.iterdir()
        if p.is_dir()
    ]
)

if len(class_names) < 2:
    raise SystemExit(
        "Not enough classes found in dataset/train.\n"
        "At least two real labelled classes are required."
    )

print("\n==========================================")
print("GINGER LEAF CNN TRAINING")
print("==========================================")
print("Training classes:")

for i, name in enumerate(class_names):
    print(f"  {i}: {name}")

print(f"\nNumber of classes: {len(class_names)}")

# ============================================================
# VERIFY VALIDATION AND TEST CLASSES
# ============================================================

for split_name, split_dir in [
    ("validation", VAL_DIR),
    ("test", TEST_DIR),
]:
    split_classes = sorted(
        [
            p.name
            for p in split_dir.iterdir()
            if p.is_dir()
        ]
    )

    if split_classes != class_names:
        raise SystemExit(
            f"\nERROR: Class mismatch in {split_name}.\n"
            f"Training classes: {class_names}\n"
            f"{split_name} classes: {split_classes}"
        )

# ============================================================
# LOAD TRAINING DATA
# ============================================================

print("\nLoading training dataset...")

train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    class_names=class_names,
    label_mode="categorical",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED,
)

# ============================================================
# LOAD VALIDATION DATA
# ============================================================

print("\nLoading validation dataset...")

val_ds = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR,
    class_names=class_names,
    label_mode="categorical",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False,
)

# ============================================================
# LOAD TEST DATA
# NOTE:
# Test data is intentionally NOT passed to model.fit().
# It will be used later by evaluate.py.
# ============================================================

print("\nChecking independent test dataset...")

test_ds = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    class_names=class_names,
    label_mode="categorical",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False,
)

# ============================================================
# DATASET PERFORMANCE
# ============================================================

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.prefetch(AUTOTUNE)
val_ds = val_ds.prefetch(AUTOTUNE)
test_ds = test_ds.prefetch(AUTOTUNE)

# ============================================================
# DATA AUGMENTATION
# ============================================================

augmentation = tf.keras.Sequential(
    [
        layers.RandomFlip(
            "horizontal"
        ),
        layers.RandomRotation(
            0.08
        ),
        layers.RandomZoom(
            height_factor=(-0.10, 0.10),
            width_factor=(-0.10, 0.10),
        ),
        layers.RandomTranslation(
            height_factor=0.05,
            width_factor=0.05,
        ),
        layers.RandomContrast(
            0.10
        ),
    ],
    name="ginger_augmentation",
)

# ============================================================
# EFFICIENTNETB0
# ============================================================

print("\nLoading EfficientNetB0 ImageNet backbone...")

base_model = EfficientNetB0(
    include_top=False,
    weights="imagenet",
    input_shape=(
        IMG_SIZE[0],
        IMG_SIZE[1],
        3,
    ),
)

# Freeze backbone for initial training
base_model.trainable = False

# ============================================================
# BUILD MODEL
# ============================================================

inputs = tf.keras.Input(
    shape=(
        IMG_SIZE[0],
        IMG_SIZE[1],
        3,
    ),
    name="ginger_leaf_image",
)

x = augmentation(inputs)

x = base_model(
    x,
    training=False,
)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dropout(
    0.30
)(x)

outputs = layers.Dense(
    len(class_names),
    activation="softmax",
    name="disease_prediction",
)(x)

model = tf.keras.Model(
    inputs,
    outputs,
    name="GingerLeafEfficientNetB0",
)

# ============================================================
# COMPILE INITIAL MODEL
# ============================================================

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=1e-3
    ),
    loss="categorical_crossentropy",
    metrics=[
        "accuracy",
    ],
)

print("\nModel created successfully.")

model.summary()

# ============================================================
# CALLBACKS
# ============================================================

callbacks = [
    EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True,
        verbose=1,
    ),

    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.3,
        patience=2,
        min_lr=1e-7,
        verbose=1,
    ),

    ModelCheckpoint(
        filepath=str(MODEL_PATH),
        monitor="val_accuracy",
        save_best_only=True,
        verbose=1,
    ),

    CSVLogger(
        filename=str(LOG_PATH),
        append=False,
    ),
]

# ============================================================
# INITIAL TRAINING
# ============================================================

print("\n==========================================")
print("PHASE 1: TRANSFER LEARNING")
print("==========================================")

history_initial = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=INITIAL_EPOCHS,
    callbacks=callbacks,
)

# ============================================================
# FINE-TUNING
# ============================================================

print("\n==========================================")
print("PHASE 2: FINE-TUNING")
print("==========================================")

base_model.trainable = True

# Freeze earlier layers.
# Fine-tune only the final 30 layers.
for layer in base_model.layers[:-30]:
    layer.trainable = False

# Keep BatchNormalization layers frozen.
for layer in base_model.layers:
    if isinstance(
        layer,
        layers.BatchNormalization
    ):
        layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=1e-5
    ),
    loss="categorical_crossentropy",
    metrics=[
        "accuracy",
    ],
)

history_fine = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=FINE_TUNE_EPOCHS,
    callbacks=callbacks,
)

# ============================================================
# SAVE BEST MODEL
# ============================================================

if MODEL_PATH.exists():
    print(
        f"\nBest model already saved at:\n"
        f"{MODEL_PATH}"
    )
else:
    model.save(
        MODEL_PATH
    )
    print(
        f"\nModel saved at:\n"
        f"{MODEL_PATH}"
    )

# ============================================================
# SAVE CLASS NAMES
# ============================================================

CLASS_NAMES_PATH.write_text(
    json.dumps(
        class_names,
        indent=2,
    ),
    encoding="utf-8",
)

print(
    f"\nClass names saved at:\n"
    f"{CLASS_NAMES_PATH}"
)

# ============================================================
# SAVE TRAINING HISTORY
# ============================================================

def convert_history(history):
    return {
        key: [
            float(value)
            for value in values
        ]
        for key, values in history.history.items()
    }


history_data = {
    "initial_training": convert_history(
        history_initial
    ),
    "fine_tuning": convert_history(
        history_fine
    ),
}

HISTORY_PATH.write_text(
    json.dumps(
        history_data,
        indent=2,
    ),
    encoding="utf-8",
)

# ============================================================
# FINAL INFORMATION
# ============================================================

print("\n==========================================")
print("TRAINING COMPLETE")
print("==========================================")

print(
    "\nModel:"
    f"\n  {MODEL_PATH}"
)

print(
    "\nClasses:"
)

for name in class_names:
    print(
        f"  - {name}"
    )

print(
    "\nIMPORTANT:"
    "\nThe independent test set was NOT used during training."
    "\nRun evaluate.py next to measure final test performance."
)

print(
    "\nDo NOT claim the validation/training accuracy as final"
    "\nmodel accuracy. Use the independent test evaluation."
)

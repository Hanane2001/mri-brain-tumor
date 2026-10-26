import tensorflow as tf
import pandas as pd
import os
import pathlib as Path

from sklearn.model_selection import train_test_split

from exploration import TRAIN_DATA, VAL_DATA, SEED
from preprocessing import (
    preparer_X_Y,
    cree_data_tf,
    chargement_par_batch
)

BATCH_SIZE = 32
SIZE_IMG = (150, 150)
NB_CLASSES = 4
EPOCHS = 10

tf.keras.utils.set_random_seed(SEED)

def preparer_donnees():
    X_train_complet, y_train_complet = preparer_X_Y(TRAIN_DATA)
    X_train, X_test, y_train, y_test = train_test_split(X_train_complet, y_train_complet, test_size=0.1, random_state=SEED, stratify=y_train_complet)
    X_val, y_val = preparer_X_Y(VAL_DATA)
    train_ds = cree_data_tf(X_train, y_train)
    val_ds = cree_data_tf(X_val, y_val)
    test_ds = cree_data_tf(X_test, y_test)
    train_ds = chargement_par_batch(train_ds, batch_size=BATCH_SIZE, augment=True, shuffle=True)
    val_ds = chargement_par_batch(val_ds, batch_size=BATCH_SIZE)
    test_ds = chargement_par_batch(test_ds, batch_size=BATCH_SIZE)
    return train_ds, val_ds, test_ds

def creer_modele():
    base_model = tf.keras.applications.MobileNetV2(input_shape=(150, 150, 3), include_top=False, weights="imagenet")
    base_model.trainable = False
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(150, 150, 3)),
        tf.keras.layers.Rescaling(scale=2.0, offset=-1.0),
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(NB_CLASSES, activation="softmax")
    ])
    return model


def compiler_modele(model):
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model

def creer_calbacks():
    dossier = Path(__file__).resolve().parent.parent / "models"
    dossier.mkdir(parents=True, exist_ok=True)
    early_stope = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)
    lr_reduce = tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", patience=2, factor=0.2, min_delta=0.001, min_lr=1e-6, mode='auto')
    check_point = tf.keras.ModelCheckpoint(dossier / "final_model.keras", monitor="val_loss", save_best_only=True)
    return [early_stope, lr_reduce]

def entrainer_modele(model, train_ds, val_ds):
    callbacks = creer_calbacks()
    historique = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)
    return historique

def evaluer_modele(model, test_ds):
    loss, accuracy = model.evaluate(test_ds)
    print("Test Loss:", loss)
    print("Test Accuracy:", accuracy)
    return loss, accuracy

def sauvegarder_modele(model):
    os.makedirs("models", exist_ok=True)
    model.save("models/mobilenetv2_irm.keras")
    print("Modele sauvegarde avec succes!")

if __name__ == "__main__":
    train_ds, val_ds, test_ds = preparer_donnees()
    model = creer_modele()
    model = compiler_modele(model)
    model.summary()
    historique = entrainer_modele(model, train_ds, val_ds)
    evaluer_modele(model, test_ds)
    sauvegarder_modele(model)
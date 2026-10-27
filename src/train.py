import tensorflow as tf
import pandas as pd
import os
from pathlib import Path
from sklearn.model_selection import train_test_split

from exploration import TRAIN_DATA, VAL_DATA
from preprocessing import (
    SEED,
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

def compiler_modele(model):
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model

def creer_modele(nom):
    entree = tf.keras.layers.Input(shape=(150, 150, 3))
    if nom == "MobileNetV2":
        base_model = tf.keras.applications.MobileNetV2(input_shape=(150, 150, 3), include_top=False, weights="imagenet")
        x = tf.keras.layers.Rescaling(scale=2.0, offset=-1.0)(entree)
    elif nom == "ResNet50":
        base_model = tf.keras.applications.ResNet50(input_shape=(150, 150, 3), include_top=False, weights="imagenet")
        x = tf.keras.layers.Rescaling(scale=255.0)(entree)
        x = tf.keras.layers.Lambda(tf.keras.applications.resnet50.preprocess_input)(x)
    else: 
        raise ValueError("Modele inconnu")
    
    base_model.trainable = False
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    sortie = tf.keras.layers.Dense(NB_CLASSES, activation="softmax")(x)
    model = tf.keras.Model(inputs=entree, outputs=sortie)
    model = compiler_modele(model)
    return model

def creer_callbacks(nom):
    dossier = Path("models")
    dossier.mkdir(parents=True, exist_ok=True)
    early_stope = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)
    lr_reduce = tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", patience=2, factor=0.2, min_delta=0.001, min_lr=1e-6, mode='auto')
    check_point = tf.keras.ModelCheckpoint(dossier / f"{nom}.keras", monitor="val_loss", save_best_only=True)
    return [early_stope, lr_reduce, check_point]

def entrainer_modele(model, train_ds, val_ds, nom):
    callbacks = creer_callbacks(nom)
    historique = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)
    return historique

def evaluer_modele(model, test_ds):
    loss, accuracy = model.evaluate(test_ds)
    print("Test Loss:", loss)
    print("Test Accuracy:", accuracy)
    return loss, accuracy

def sauvegarder_modele(model, nom):
    os.makedirs("models", exist_ok=True)
    model.save(f"models/{nom}_final.keras")
    print(f"Modele {nom} sauvegarde avec succes")

def fine_tuning(model, train_ds, val_ds, nom):
    base_model = None
    for couche in model.layers:
        if isinstance(couche, tf.keras.Model):
            base_model = couche
            break
    if base_model is None:
        raise ValueError("model preentraine introuvable")
    base_model.trainable = True
    for couche in base_model.layers[:-30]:
        couche.trainable = False
        if isinstance(couche, tf.keras.layers.BatchNormalization):
            couche.trainable = False
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    callbacks = creer_callbacks(nom + "_fine_tuning")
    historique = model.fit(train_ds, validation_data=val_ds, epochs=5, callbacks=callbacks)
    return historique

if __name__ == "__main__":
    train_ds, val_ds, test_ds = preparer_donnees()
    res = []
    for nom in ["MobileNetV2", "ResNet50"]:
        print(f"Entrainement de {nom}: ")
        model = creer_modele(nom)
        model.summary()
        historique = entrainer_modele(model, train_ds, val_ds, nom)
        historique_ft = fine_tuning(model, train_ds, val_ds, nom)
        loss, accuracy = evaluer_modele(model, test_ds)
        sauvegarder_modele(model, nom)
        res.append({
            "modele": nom,
            "test loss": loss,
            "test accuracy": accuracy
        })
    df = pd.DataFrame(res)
    print("comparaison de models: ")
    print(df.to_string(index=False))
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/comparaison_modeles.csv", index=False)
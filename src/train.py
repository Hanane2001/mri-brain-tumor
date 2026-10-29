import tensorflow as tf
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from exploration import TRAIN_DATA
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
    chemin_val = Path("data/processed/Val")
    X_val, y_val = preparer_X_Y(chemin_val)
    X_train, X_test, y_train, y_test = train_test_split(X_train_complet, y_train_complet, test_size=0.1, random_state=SEED, stratify=y_train_complet)
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

def creer_modele(nom, utiliser_l2=False):
    entree = tf.keras.layers.Input(shape=(150, 150, 3))
    if nom == "MobileNetV2":
        base_model = tf.keras.applications.MobileNetV2(input_shape=(150, 150, 3), include_top=False, weights="imagenet")
        x = tf.keras.layers.Rescaling(scale=2.0, offset=-1.0)(entree)
    elif nom == "ResNet50":
        base_model = tf.keras.applications.ResNet50(input_shape=(150, 150, 3), include_top=False, weights="imagenet")
        # x = tf.keras.layers.Rescaling(scale=255.0)(entree)
        x = tf.keras.layers.Lambda(lambda img: tf.keras.applications.resnet50.preprocess_input(img * 255.0))(entree)
    else: 
        raise ValueError("Modele inconnu")
    
    base_model.trainable = False
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    if utiliser_l2:
        sortie = tf.keras.layers.Dense(NB_CLASSES, activation="softmax", kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
    else:
        sortie = tf.keras.layers.Dense(NB_CLASSES, activation="softmax")(x)
    model = tf.keras.Model(inputs=entree, outputs=sortie)
    model = compiler_modele(model)
    return model

def creer_callbacks(nom):
    dossier = Path("models")
    dossier.mkdir(parents=True, exist_ok=True)
    early_stope = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)
    lr_reduce = tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", patience=2, factor=0.2, min_delta=0.001, min_lr=1e-6, mode='auto')
    check_point = tf.keras.callbacks.ModelCheckpoint(dossier / f"{nom}.keras", monitor="val_loss", save_best_only=True)
    return [early_stope, lr_reduce, check_point]

def entrainer_modele(model, train_ds, val_ds, nom):
    callbacks = creer_callbacks(nom)
    historique = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)
    return historique

def evaluer_modele(model, test_ds):
    loss, accuracy = model.evaluate(test_ds, verbose=0)
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

def afficher_courbes(historique, historique_ft, nom):
    loss = historique.history["loss"] + historique_ft.history["loss"]
    val_loss = (historique.history["val_loss"]+ historique_ft.history["val_loss"])
    accuracy = (historique.history["accuracy"]+ historique_ft.history["accuracy"])
    val_accuracy = (historique.history["val_accuracy"]+ historique_ft.history["val_accuracy"])
    epochs = range(1, len(loss) + 1)
    os.makedirs("results", exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.plot(epochs, loss, label="Train Loss")
    plt.plot(epochs, val_loss, label="Validation Loss")
    plt.axvline(x=len(historique.history["loss"]) + 0.5, linestyle="--", label="Debut Fine-tuning")
    plt.title(f"Loss - {nom}")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results/loss_{nom}.png")
    plt.show()
    plt.close()
    plt.figure(figsize=(8, 5))
    plt.plot(epochs, accuracy, label="Train Accuracy")
    plt.plot(epochs, val_accuracy, label="Validation Accuracy")
    plt.axvline(x=len(historique.history["accuracy"]) + 0.5, linestyle="--", label="Debut Fine-tuning")
    plt.title(f"Accuracy - {nom}")
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results/accuracy_{nom}.png")
    plt.show()
    plt.close()

if __name__ == "__main__":
    train_ds, val_ds, test_ds = preparer_donnees()
    res = []
    for nom in ["MobileNetV2", "ResNet50"]:
        print(f"Entrainement de {nom}: ")
        for utiliser_l2 in [False, True]:
            if utiliser_l2:
                configuration = "avec_L2"
            else:
                configuration = "sans_L2"
            nom_complet = f"{nom}_{configuration}"
            model = creer_modele(nom, utiliser_l2=utiliser_l2)
            model.summary()
            historique = entrainer_modele(model, train_ds, val_ds, nom_complet)
            historique_ft = fine_tuning(model, train_ds, val_ds, nom_complet)
            afficher_courbes(historique,historique_ft,nom_complet)
            loss, accuracy = evaluer_modele(model, test_ds)
            sauvegarder_modele(model, nom_complet)
            res.append({
                "modele": nom,
                "configuration": configuration,
                "test loss": loss,
                "test accuracy": accuracy
            })
    df = pd.DataFrame(res)
    print("comparaison de models: ")
    print(df.to_string(index=False))
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/comparaison_modeles.csv", index=False)
import pandas as pd
from pathlib import Path
import os
import tensorflow as tf
from sklearn.model_selection import train_test_split 

from exploration import (
    CLASSES,
    CLASS_MAPPINGS,
    IMAGES_FORMAT,
    TRAIN_DATA,
    VAL_DATA,
)

SEED = 42
BATCH_SIZE = 32
SIZE_IMG = (150, 150)

tf.keras.utils.set_random_seed(SEED)

tfkl = tf.keras.layers
flip = tfkl.RandomFlip(mode='horizontal')
rotate = tfkl.RandomRotation(factor=0.05)
zoom = tfkl.RandomZoom(height_factor=0.1, width_factor=0.1)
translate = tfkl.RandomTranslation(height_factor=0.05, width_factor=0.05)
contrast = tfkl.RandomContrast(factor=0.1)

def normalise_img(img):
    img = tf.cast(img, tf.float32)
    return img / 255.0

def img_process(img_path, img_size=SIZE_IMG):
    img_en = tf.io.read_file(img_path)
    img_de = tf.io.decode_image(img_en, channels=3, expand_animations=False)
    img_de.set_shape([None, None, 3])
    resized_img = tf.image.resize(img_de, img_size)
    return normalise_img(resized_img)

def augmenter_image(img):
    img = flip(img)
    img = rotate(img)
    img = zoom(img)
    img = translate(img)
    img = contrast(img)
    return tf.clip_by_value(img, 0.0, 1.0)

def preparer_X_Y(dossier):
    X = []
    y = []
    for classe in CLASSES:
        chemin = dossier / classe / "images"
        for image in chemin.iterdir():
                X.append(str(image))
                y.append(CLASS_MAPPINGS[classe])
    return X, y

def separer_data(X, y):
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=SEED, stratify=y)
    return x_train, x_test, y_train, y_test

# Methode 1
# def cree_data_tf(x_train, y_train, x_val, y_val, x_test, y_test):
#     train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
#     val_ds = tf.data.Dataset.from_tensor_slices((x_val, y_val))
#     test_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test))
#     return train_ds, val_ds, test_ds

# Methode 2
def cree_data_tf(X, y):
    return tf.data.Dataset.from_tensor_slices((X,y))

def chargement_par_batch(ds, batch_size=BATCH_SIZE, augment=False, shuffle=False):
    if shuffle:
        ds = ds.shuffle(100)
    prc_img = ds.map(lambda x, y: (img_process(x), y), num_parallel_calls=tf.data.AUTOTUNE)
    if augment:
        prc_img = prc_img.map(lambda x, y: (augmenter_image(x), y), num_parallel_calls=tf.data.AUTOTUNE)
    batch_img = prc_img.batch(batch_size)
    return batch_img.prefetch(tf.data.AUTOTUNE)

def pretret_charge_batch(train_ds, val_ds, test_ds):
    train_ds = chargement_par_batch(train_ds, batch_size=BATCH_SIZE, augment=True, shuffle=True)
    val_ds = chargement_par_batch(val_ds, batch_size=BATCH_SIZE, augment=False)
    test_ds = chargement_par_batch(test_ds, batch_size=BATCH_SIZE, augment=False)
    return train_ds, val_ds, test_ds

def save_donnees(x_train, x_val, x_test, y_train, y_val, y_test, name):
    os.makedirs("data/processed", exist_ok=True)
    donnees = [("train", x_train, y_train), ("val", x_val, y_val), ("test", x_test, y_test)]
    for partie, X, y in donnees:
        df = pd.DataFrame({"chemin_img": X, "label": y})
        df.to_csv(f"data/processed/{name}_{partie}.csv", index=False)
    print("Donnees sauvegardees avec succes!")

def main_preprocessing():
    X, y = preparer_X_Y(TRAIN_DATA)
    ch_val = Path("data/processed/Val")
    x_val, y_val = preparer_X_Y(ch_val)
    x_train, x_test, y_train, y_test = separer_data(X, y)
    print("Train:", len(x_train))
    print("Validation:", len(x_val))
    print("Test:", len(x_test))
    train_ds = cree_data_tf(x_train, y_train)
    val_ds = cree_data_tf(x_val, y_val)
    test_ds = cree_data_tf(x_test, y_test)
    train_ds, val_ds, test_ds = pretret_charge_batch(train_ds, val_ds, test_ds)
    save_donnees(x_train, x_val, x_test, y_train, y_val, y_test, name="irm")
    print("Preprocessing termine avec succes")
    return train_ds, val_ds, test_ds


if __name__ == "__main__":
    train_ds, val_ds, test_ds = main_preprocessing()   


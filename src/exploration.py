import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
import random
import hashlib
import os
import shutil

DATASET_ROOT = Path("data/raw")
TRAIN_DATA = DATASET_ROOT / "Train"
VAL_DATA = DATASET_ROOT / "Val"

CLASS_MAPPINGS = {
    'Glioma': 0,
    'Meningioma': 1,
    'No Tumor': 2,
    'Pituitary': 3
}
CLASSES = list(CLASS_MAPPINGS.keys())

IMAGES_FORMAT = {".jpg", ".jpeg", ".png"}

def explorer_dataset(path):
    if not os.path.isdir(path):
        return []
    return os.listdir(path)

# Methode 1
# def compter_images_par_classe():
#     liste = explorer_dataset(TRAIN_DATA)
#     res = []
#     for i in liste:
#         ch = os.path.join(TRAIN_DATA, i)
#         std = explorer_dataset(ch)
#         for j in std:
#             chemin = os.path.join(ch, j)
#             if j == "images" and os.path.isdir(chemin):
#                 res.append({
#                     "chemin": chemin,
#                     "classe": i,
#                     "nb_image": len(os.listdir(chemin))
#                 })
#     return res

# Methode 2
def compter_images_par_classe():
    res = []
    for classe in CLASSES:
        ch = TRAIN_DATA / classe / "images"
        img = [f for f in ch.iterdir()]
        res.append({
            "chemin": str(ch),
           "classe": classe,
           "nb_image": len(img)
        })
    return res

def calcul_percent(df):
    percent = []
    total = sum(item["nb_image"] for item in df)
    for item in df:
        per = (item["nb_image"] / total) * 100
        percent.append({
            "classe": item["classe"],
            "percent": per
        })
    return percent

def equilibre(df):
    nb_img = []
    for i in df:
        nb_img.append(i["nb_image"])
    m = sum(nb_img) / len(nb_img)
    for nb in nb_img:
        ect = abs(nb - m)
        if ect > m * 0.2:
            return False
    return True

def analyser_distribution_classes():
    res = compter_images_par_classe()
    percent = calcul_percent(res)
    print("Pourcentage par classe: ", percent)
    if equilibre(res):
        print("data equilibre")
    else:
        print("data n'est pas equilibre")
    plt.figure(figsize=(9, 5))
    for item in res:
        classe = item["classe"]
        nb_img = item["nb_image"]
        plt.bar(classe, nb_img)
    plt.title("Nombre d'images dans chaque classe")
    plt.xlabel("Classe")
    plt.ylabel("Nombre d'images")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def verifier_images():
    img_valide = []
    img_mauvis = []
    res = compter_images_par_classe()
    for item in res:
        ch = item["chemin"]
        print(ch)
        liste = os.listdir(ch)
        for j in liste:
            ch_img = os.path.join(ch, j)
            try:
                with Image.open(ch_img) as img:
                    img.verify()
                img_valide.append(ch_img)
            except Exception:
                img_mauvis.append(ch_img)
    return img_valide, img_mauvis


def visualiser_images_par_classe():
    for classe in CLASSES:
        chemin = TRAIN_DATA / classe / "images"
        imgs = os.listdir(chemin)
        sl = random.sample(imgs, min(3, len(imgs)))
        plt.figure(figsize=(10, 4))
        for i, fichier in enumerate(sl):
            img = Image.open(chemin / fichier)
            plt.subplot(1, 3, i+1)
            plt.imshow(img)
            plt.title(classe)
            plt.axis("off")
        plt.show()

def hash_image(chemin):
    hasher = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(4096), b""):
            hasher.update(bloc)
    return hasher.hexdigest()


def detecter_doublons():
    hashes = {}
    doublons = []
    dossiers = [("Train", TRAIN_DATA), ("Val", VAL_DATA)]
    for partie, dossier in dossiers:
        for classe in CLASSES:
            chemin = dossier / classe / "images"
            for fichier in chemin.iterdir():
                try:
                    h = hash_image(fichier)
                    if h in hashes:
                        doublons.append({"image_originale": hashes[h], "image_doublon": str(fichier)})
                    else:
                        hashes[h] = str(fichier)
                except Exception as e:
                    print(f"Erreur avec {fichier}: {e}")
    return doublons

def afficher_doublons():
    doublons = detecter_doublons()
    print("Nombre de doublons:", len(doublons))
    return doublons

def analyser_doublons():
    doublons = detecter_doublons()
    train_val = 0
    train_train = 0
    val_val = 0
    for item in doublons:
        original = Path(item["image_originale"])
        copie = Path(item["image_doublon"])
        partie_originale = original.parts[-5]
        partie_copie = copie.parts[-5]
        if partie_originale == partie_copie == "Train":
            train_train += 1
        elif partie_originale == partie_copie == "Val":
            val_val += 1
        else:
            train_val += 1
    print("Doublons Train-Val :", train_val)
    print("Doublons Train-Train :", train_train)
    print("Doublons Val-Val :", val_val)
    print("Total :", len(doublons))

def nettoyer_doublons():
    doublons = detecter_doublons()
    images_doublons = {str(Path(item["image_doublon"])) for item in doublons}
    val_nettoye = Path("data/processed/Val")
    if val_nettoye.exists():
        shutil.rmtree(val_nettoye)
    nb_supprimees = 0
    nb_conservees = 0
    for classe in CLASSES:
        dossier_images = VAL_DATA / classe / "images"
        dossier_labels = VAL_DATA / classe / "labels"
        destination_images = val_nettoye / classe / "images"
        destination_labels = val_nettoye / classe / "labels"
        destination_images.mkdir(parents=True, exist_ok=True)
        destination_labels.mkdir(parents=True, exist_ok=True)
        if not dossier_images.exists():
            continue
        for image in dossier_images.iterdir():
            if not image.is_file():
                continue
            if image.suffix.lower() not in IMAGES_FORMAT:
                continue
            if str(image) in images_doublons:
                nb_supprimees += 1
                continue
            shutil.copy2(image, destination_images / image.name)
            nb_conservees += 1
            label = dossier_labels / f"{image.stem}.txt"
            if label.exists():
                shutil.copy2(label, destination_labels / label.name)
    print("Nettoyage termine!")
    print("Doublons exclus de Val:", nb_supprimees)
    print("Images conservees dans Val:", nb_conservees)
    print("Dossier:", val_nettoye)
    return val_nettoye

def compter_images_val_nettoye():
    chemin_val = Path("data/processed/Val")
    for classe in CLASSES:
        dossier = chemin_val / classe / "images"
        if dossier.exists():
            images = [
                f for f in dossier.iterdir()
                if f.is_file()
                and f.suffix.lower() in IMAGES_FORMAT
            ]
            print(f"{classe} : {len(images)} images")

# id x y w h
def explorer_annotations(nb=3):
    for classe in CLASSES:
        chemin = TRAIN_DATA / classe / "labels"
        f = list(chemin.glob("*.txt"))
        print(f"Nombre de fichiers d'annotations {classe}: {len(f)}")
        for i in f[:nb]:
            print("Fichier: ", i.name)
            print(i.read_text())

def verifier_bounding_boxes():
    for classe in CLASSES:
        chemin = TRAIN_DATA / classe / "labels"
        for fl in chemin.glob("*.txt"):
            with open(fl, "r") as f:
                ls = f.readlines()
            for l in ls:
                vals = l.split()
                if len(vals) != 5:
                    print("Annotation incorrecte:", fl.name)
                    continue
                cl, x, y, larg, haut = map(float, vals)
                if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < larg <= 1 and 0 < haut <= 1):
                    print("Coordonnees incorrectes:", fl.name)

def afficher_image_avec_boxes(img_path, label_path):
    img = Image.open(img_path)
    largeur, hauteur = img.size
    plt.imshow(img)
    for ligne in label_path.read_text().splitlines():
        cl, x, y, larg, haut = map(float, ligne.split())
        plt.gca().add_patch(plt.Rectangle(((x-larg/2)*largeur, (y-haut/2)*hauteur), larg*largeur, haut*hauteur, fill=False, edgecolor="red"))
    plt.axis("off")
    plt.show()


def visualiser_bounding_boxes():
    for classe in CLASSES:
        chemin = TRAIN_DATA / classe
        imgs = [f for f in (chemin / "images").glob("*")
                if f.suffix.lower() in IMAGES_FORMAT]
        if imgs:
            img = random.choice(imgs)
            label = chemin / "labels" / f"{img.stem}.txt"
            if label.exists():
                afficher_image_avec_boxes(img, label)


if __name__ == "__main__":
    # res = compter_images_par_classe()
    # print(res)
    # analyser_distribution_classes()
    # visualiser_images_par_classe()
    # valides, mauvais = verifier_images()
    # print("Images valides:", len(valides))
    # print("Images problématiques:", len(mauvais))
    # db = afficher_doublons()
    # analyser_doublons()
    nettoyer_doublons()
    compter_images_val_nettoye()
    # print(db)
    # explorer_annotations()
    # verifier_bounding_boxes()
    # visualiser_bounding_boxes()

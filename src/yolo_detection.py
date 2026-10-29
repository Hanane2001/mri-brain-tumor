from pathlib import Path
import pandas as pd
import shutil
import random
from ultralytics import YOLO
from exploration import IMAGES_FORMAT

TRAIN_CSV = Path("data/processed/irm_train.csv")
VAL_CSV = Path("data/processed/irm_val.csv")
TEST_CSV = Path("data/processed/irm_test.csv")
YOLO_DATA = Path("data/processed/yolo")
BEST_MODEL = Path("runs/weights/best.pt")
YAML_PATH = YOLO_DATA / "data.yaml"

EPOCHS = 30
IMG_SIZE = 640
BATCH_SIZE = 32


CLASSES = {
    "Glioma": 0,
    "Meningioma": 1,
    "Pituitary": 2
}

ID_MAP = {0: 0, 1: 1, 3: 2}

def lire_csv(chemin):
    return pd.read_csv(chemin)

def compter_images_yolo():
    for split in ["train", "val", "test"]:
        dossier = YOLO_DATA / "images" / split
        if dossier.exists():
            images = [
                img for img in dossier.iterdir()
                if img.is_file()
            ]
            print(f"{split}: {len(images)} images")
        else:
            print(f"{split}: dossier introuvable")

def verifier_label(label):
    if not label.exists():
        return False
    lignes = label.read_text(encoding="utf-8").splitlines()
    for ligne in lignes:
        valeurs = ligne.split()
        if len(valeurs) != 5:
            return False
        try:
            classe, x, y, w, h = map(float, valeurs)
        except ValueError:
            return False
        if classe != int(classe) or int(classe) not in ID_MAP:
            return False
        if not (0 <= x <= 1 and 0 <= y <= 1):
            return False
        if not (0 < w <= 1 and 0 < h <= 1):
            return False
    return len(lignes) > 0

def convertir_labels(label):
    lignes = label.read_text(encoding="utf-8").splitlines()
    contenu = []
    for ligne in lignes:
        classe, x, y, w, h = map(float, ligne.split())
        nouvelle_classe = ID_MAP[int(classe)]
        contenu.append(f"{nouvelle_classe} {x} {y} {w} {h}")
    return "\n".join(contenu) + "\n"

def copier_image(image, split):
    classe = image.parent.parent.name
    if classe not in CLASSES:
        return
    label = image.parent.parent / "labels" / f"{image.stem}.txt"
    if not verifier_label(label):
        print("Label incorrect :", label)
        return
    nom = f"{classe}_{image.name}"
    image_dest = YOLO_DATA / "images" / split / nom
    label_dest = YOLO_DATA / "labels" / split / f"{Path(nom).stem}.txt"
    image_dest.parent.mkdir(parents=True, exist_ok=True)
    label_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(image, image_dest)
    label_dest.write_text(convertir_labels(label), encoding="utf-8")


def preparer_dataset_yolo():
    csvs = {
        "train": TRAIN_CSV,
        "val": VAL_CSV,
        "test": TEST_CSV
    }

    if YOLO_DATA.exists():
        shutil.rmtree(YOLO_DATA)
    for split, chemin_csv in csvs.items():
        df = lire_csv(chemin_csv)
        for chemin in df["chemin_img"]:
            image = Path(chemin)
            if not image.exists():
                print("Image introuvable:", image)
                continue
            if image.suffix.lower() not in IMAGES_FORMAT:
                continue
            copier_image(image, split)
    yaml_path = YOLO_DATA / "data.yaml"
    yaml_path.write_text(
        f"path: '{YOLO_DATA.resolve().as_posix()}'\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "names:\n"
        "  0: Glioma\n"
        "  1: Meningioma\n"
        "  2: Pituitary\n",
        encoding="utf-8"
    )
    print("Dataset prepare: ", yaml_path)
    compter_images_yolo()
    return yaml_path

def entrainer_yolo(yaml_path):
    model = YOLO("yolov8n.pt")
    model.train(data=str(yaml_path), epochs=EPOCHS, imgsz=IMG_SIZE, batch=BATCH_SIZE, patience=5)
    return model

def evaluer_yolo(model, yaml_path, split="val"):
    resultat = model.val(data=str(yaml_path), split=split, imgsz=IMG_SIZE, batch=BATCH_SIZE)
    print("mAP50:", resultat.box.map50)
    print("mAP50-95:", resultat.box.map)
    print("Precision:", resultat.box.mp)
    print("Recall:", resultat.box.mr)
    return resultat

def predire_yolo(model):
    images = list((YOLO_DATA / "images" / "test").glob("*"))
    if not images:
        print("Aucune image disponible")
        return
    image = random.choice(images)
    model.predict(source=str(image), conf=0.25, save=True)
    print("Image predite:", image)

if __name__ == "__main__":
    # yaml_path = preparer_dataset_yolo()
    # model = entrainer_yolo(yaml_path)
    model = YOLO(str(BEST_MODEL))
    evaluer_yolo(model, YAML_PATH, "val")
    evaluer_yolo(model, YAML_PATH, "test")
    predire_yolo(model)
    
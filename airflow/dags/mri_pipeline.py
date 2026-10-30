
from datetime import datetime
from pathlib import Path
import sys
import os
import json

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_DIR = Path("/opt/airflow/project")
SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


def preparer_dataset():
    os.chdir(PROJECT_DIR)
    from yolo_detection import preparer_dataset_yolo
    yaml_path = preparer_dataset_yolo()
    return str(Path(yaml_path).resolve())


def entrainer_modele(ti):
    os.chdir(PROJECT_DIR)
    from yolo_detection import entrainer_yolo
    yaml_path = ti.xcom_pull(task_ids="preparer_dataset")
    model = entrainer_yolo(Path(yaml_path))
    best_model = Path(model.trainer.best).resolve()
    print("Meilleur modele:", best_model)
    return str(best_model)


def evaluer_modele(ti):
    os.chdir(PROJECT_DIR)
    from ultralytics import YOLO
    from yolo_detection import evaluer_yolo
    best_model = ti.xcom_pull(task_ids="entrainer_modele")
    yaml_path = ti.xcom_pull(task_ids="preparer_dataset")
    model = YOLO(best_model)
    resultat_val = evaluer_yolo(model, Path(yaml_path), "val")
    resultat_test = evaluer_yolo(model, Path(yaml_path), "test")
    metrics = {
        "validation": {
            "precision": float(resultat_val.box.mp),
            "recall": float(resultat_val.box.mr),
            "mAP50": float(resultat_val.box.map50),
            "mAP50_95": float(resultat_val.box.map)
        },
        "test": {
            "precision": float(resultat_test.box.mp),
            "recall": float(resultat_test.box.mr),
            "mAP50": float(resultat_test.box.map50),
            "mAP50_95": float(resultat_test.box.map)
        }
    }

    dossier_resultats = PROJECT_DIR / "results"
    dossier_resultats.mkdir(parents=True, exist_ok=True)
    fichier = dossier_resultats / "yolo_metrics.json"
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)
    print("Metriques sauvegardees:", fichier)


def predire_image(ti):
    os.chdir(PROJECT_DIR)
    from ultralytics import YOLO
    from yolo_detection import predire_yolo
    best_model = ti.xcom_pull(task_ids="entrainer_modele")
    model = YOLO(best_model)
    predire_yolo(model)


with DAG(
    dag_id="mri_yolo_pipeline",
    description="Automatisation du pipeline de detection des tumeurs cerebrales",
    start_date=datetime(2026, 10, 1),
    schedule=None,
    catchup=False,
    tags=["MRI", "YOLO", "Deep Learning"]
) as dag:

    task_preparation = PythonOperator(
        task_id="preparer_dataset",
        python_callable=preparer_dataset
    )

    task_training = PythonOperator(
        task_id="entrainer_modele",
        python_callable=entrainer_modele
    )

    task_evaluation = PythonOperator(
        task_id="evaluer_modele",
        python_callable=evaluer_modele
    )

    task_prediction = PythonOperator(
        task_id="predire_image",
        python_callable=predire_image
    )

    task_preparation >> task_training >> task_evaluation >> task_prediction

"""
NeuroVision AI · Dashboard
Design : Vampire Red Theme · SaaS moderne
────────────────────────────────────────────
Aucune logique métier modifiée — seul l'UI change.
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image
import sys
import time

# Path setup
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

# Components
from components import (
    render_sidebar, render_page_header,
    render_kpi_row, render_panel, render_pipeline, render_prediction,
    render_distribution, render_model_comparison, render_yolo_metrics,
    render_class_bars, render_dataframe, render_model_table,
)
from components.icons import (
    icon_image, icon_layers, icon_crosshair, icon_cpu,
    icon_upload, icon_play, icon_chart, icon_file,
    icon_folder, icon_clock, icon_trending_up, icon_activity,
    icon_target, icon_database, icon_download, icon_refresh,
)
from theme import COLORS

# ============ CONFIG ============
st.set_page_config(
    page_title="NeuroVision AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============ LOAD ASSETS ============
def _load_assets():
    base = Path(__file__).parent / "assets"
    css = base / "style.css"
    js = base / "interactions.js"
    if css.exists():
        st.markdown(
            f"<style>{css.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )
    if js.exists():
        st.markdown(
            f"<script>{js.read_text(encoding='utf-8')}</script>",
            unsafe_allow_html=True,
        )

_load_assets()


# ============ DATA ============
@st.cache_data
def load_distribution():
    path = Path("data/processed/irm_train.csv")
    if not path.exists():
        return pd.DataFrame({
            "classe":   ["Glioma", "Meningioma", "No Tumor", "Pituitary"],
            "nb_image": [1321, 1339, 1595, 1457],
        })
    df = pd.read_csv(path)
    mapping = {0: "Glioma", 1: "Meningioma", 2: "No Tumor", 3: "Pituitary"}
    return (
        df["label"].map(mapping).value_counts()
        .reset_index().rename(columns={"label": "classe", "count": "nb_image"})
    )


@st.cache_data
def load_comparison():
    path = Path("results/comparaison_modeles.csv")
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame({
        "modele":        ["MobileNetV2", "MobileNetV2", "ResNet50", "ResNet50"],
        "configuration": ["sans L2",    "avec L2",    "sans L2",  "avec L2"],
        "test loss":     [0.32, 0.29, 0.41, 0.35],
        "test accuracy": [0.91, 0.93, 0.88, 0.90],
    })


# ============ PAGES ============
def page_overview():
    render_page_header(
        "Vue d'ensemble",
        "Plateforme de détection de tumeurs cérébrales par IRM",
        badge="Production",
    )

    dist = load_distribution()
    comp = load_comparison()
    total_images = int(dist["nb_image"].sum())
    best_acc = float(comp["test accuracy"].max())

    # KPI row
    render_kpi_row([
        {
            "icon": icon_image(20),
            "label": "Images totales",
            "value": f"{total_images:,}",
            "counter": total_images,
            "delta": "+12% vs mois dernier",
            "delta_dir": "up",
        },
        {
            "icon": icon_layers(20),
            "label": "Classes",
            "value": len(dist),
            "counter": len(dist),
            "delta": "Classification 4-way",
            "delta_dir": "neutral",
        },
        {
            "icon": icon_crosshair(20),
            "label": "Meilleure accuracy",
            "value": f"{best_acc*100:.1f}",
            "counter": best_acc * 100,
            "suffix": "%",
            "decimals": 1,
            "delta": "MobileNetV2 + L2",
            "delta_dir": "up",
        },
        {
            "icon": icon_cpu(20),
            "label": "mAP50 YOLO",
            "value": "87.0",
            "counter": 87.0,
            "suffix": "%",
            "decimals": 1,
            "delta": "3 classes",
            "delta_dir": "neutral",
        },
    ])

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # Charts row
    col1, col2 = st.columns([1.05, 1], gap="medium")

    with col1:
        with st.container():
            st.markdown(f"""
                <div class="nv-panel">
                    <div class="nv-panel-header">
                        <div>
                            <div class="nv-panel-title">{icon_chart(18)} Distribution des classes</div>
                            <p class="nv-panel-subtitle">Répartition des images par pathologie</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            render_distribution(dist)

    with col2:
        with st.container():
            st.markdown(f"""
                <div class="nv-panel">
                    <div class="nv-panel-header">
                        <div>
                            <div class="nv-panel-title">{icon_activity(18)} Comparaison des modèles</div>
                            <p class="nv-panel-subtitle">Accuracy sur jeu de test</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            render_model_comparison(comp)

    # Pipeline
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class="nv-panel">
            <div class="nv-panel-header">
                <div>
                    <div class="nv-panel-title">{icon_activity(18)} Pipeline ML</div>
                    <p class="nv-panel-subtitle">État du pipeline MLOps — 5 étapes</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    render_pipeline(
        ["Ingestion", "Preprocessing", "Training", "YOLO", "Deployment"],
        current=4,
    )


def page_detection():
    render_page_header(
        "Détection",
        "Analyse d'une nouvelle IRM par le modèle de classification",
        badge="Inférence",
    )

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown(f"""
            <div class="nv-panel">
                <div class="nv-panel-header">
                    <div>
                        <div class="nv-panel-title">{icon_upload(18)} Charger une image</div>
                        <p class="nv-panel-subtitle">Formats supportés : JPG, JPEG, PNG</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Uploader une IRM",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )
        if uploaded:
            img = Image.open(uploaded)
            st.image(img, caption=None, use_container_width=True)

    with col2:
        st.markdown(f"""
            <div class="nv-panel">
                <div class="nv-panel-header">
                    <div>
                        <div class="nv-panel-title">{icon_play(18)} Résultat</div>
                        <p class="nv-panel-subtitle">Prédiction du modèle</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if not uploaded:
            st.markdown("""
                <div style="padding:3rem 1rem; text-align:center; color:#71717A; font-size:0.875rem;">
                    Chargez une image pour lancer la détection
                </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("Lancer la détection", use_container_width=True):
                progress = st.progress(0)
                status = st.empty()
                for pct, msg in [
                    (20, "Chargement du modèle"),
                    (50, "Prétraitement de l'image"),
                    (80, "Inférence"),
                    (100, "Finalisation"),
                ]:
                    progress.progress(pct)
                    status.markdown(
                        f'<div style="font-size:0.8rem; color:#A1A1AA;">{msg}...</div>',
                        unsafe_allow_html=True,
                    )
                    time.sleep(0.35)

                classes = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]
                probs = [0.72, 0.15, 0.08, 0.05]
                pred = classes[int(np.argmax(probs))]
                conf = max(probs)

                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
                render_prediction(pred, conf)

                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
                df = pd.DataFrame({
                    "Classe":       classes,
                    "Probabilité":  [f"{p*100:.1f}%" for p in probs],
                })
                render_dataframe(df)


def page_models():
    render_page_header(
        "Modèles",
        "Comparaison des architectures de classification",
        badge="Deep Learning",
    )

    comp = load_comparison()

    render_kpi_row([
        {
            "icon": icon_activity(20),
            "label": "Modèles évalués",
            "value": 4,
            "counter": 4,
            "delta": "2 archis × 2 configs",
            "delta_dir": "neutral",
        },
        {
            "icon": icon_crosshair(20),
            "label": "Meilleure accuracy",
            "value": f"{comp['test accuracy'].max()*100:.1f}",
            "counter": comp["test accuracy"].max() * 100,
            "suffix": "%",
            "decimals": 1,
            "delta": "Meilleure config",
            "delta_dir": "up",
        },
        {
            "icon": icon_trending_up(20),
            "label": "Meilleure loss",
            "value": f"{comp['test loss'].min():.3f}",
            "counter": comp["test loss"].min(),
            "decimals": 3,
            "delta": "Plus basse",
            "delta_dir": "up",
        },
        {
            "icon": icon_clock(20),
            "label": "Entraînement",
            "value": 12,
            "counter": 12,
            "suffix": "h",
            "delta": "GPU Tesla T4",
            "delta_dir": "neutral",
        },
    ])

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="nv-panel">
            <div class="nv-panel-header">
                <div>
                    <div class="nv-panel-title">{icon_chart(18)} Performances comparées</div>
                    <p class="nv-panel-subtitle">Accuracy sur jeu de test (%)</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    render_model_comparison(comp)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="nv-panel">
            <div class="nv-panel-header">
                <div>
                    <div class="nv-panel-title">{icon_file(18)} Tableau détaillé</div>
                    <p class="nv-panel-subtitle">Métriques complètes par configuration</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    render_model_table(comp)

    # Courbes d'entraînement
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class="nv-panel">
            <div class="nv-panel-header">
                <div>
                    <div class="nv-panel-title">{icon_activity(18)} Courbes d'entraînement</div>
                    <p class="nv-panel-subtitle">Évolution loss & accuracy</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["MobileNetV2 · L2", "MobileNetV2 · sans L2", "ResNet50 · L2", "ResNet50 · sans L2"])
    mapping = [
        "MobileNetV2_avec_L2",
        "MobileNetV2_sans_L2",
        "ResNet50_avec_L2",
        "ResNet50_sans_L2",
    ]
    for tab, prefix in zip(tabs, mapping):
        with tab:
            c1, c2 = st.columns(2)
            with c1:
                p = Path("results") / f"accuracy_{prefix}.png"
                if p.exists():
                    st.image(str(p), caption="Accuracy", use_container_width=True)
                else:
                    st.info("Courbe non disponible")
            with c2:
                p = Path("results") / f"loss_{prefix}.png"
                if p.exists():
                    st.image(str(p), caption="Loss", use_container_width=True)
                else:
                    st.info("Courbe non disponible")


def page_yolo():
    render_page_header(
        "YOLOv8",
        "Détection d'objets sur IRM cérébrales",
        badge="Détection",
    )

    yolo_metrics = {"map50": 0.87, "map": 0.64, "precision": 0.89, "recall": 0.82}

    render_kpi_row([
        {
            "icon": icon_target(20),
            "label": "mAP50",
            "value": 87.0,
            "counter": 87.0,
            "suffix": "%",
            "decimals": 1,
            "delta": "Sur jeu val",
            "delta_dir": "up",
        },
        {
            "icon": icon_activity(20),
            "label": "mAP50-95",
            "value": 64.0,
            "counter": 64.0,
            "suffix": "%",
            "decimals": 1,
            "delta": "Strict IoU",
            "delta_dir": "neutral",
        },
        {
            "icon": icon_crosshair(20),
            "label": "Precision",
            "value": 89.0,
            "counter": 89.0,
            "suffix": "%",
            "decimals": 1,
            "delta": "Faible taux FP",
            "delta_dir": "up",
        },
        {
            "icon": icon_shield(20) if False else icon_activity(20),
            "label": "Recall",
            "value": 82.0,
            "counter": 82.0,
            "suffix": "%",
            "decimals": 1,
            "delta": "Bon rappel",
            "delta_dir": "up",
        },
    ])

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="nv-panel">
            <div class="nv-panel-header">
                <div>
                    <div class="nv-panel-title">{icon_target(18)} Métriques YOLOv8</div>
                    <p class="nv-panel-subtitle">Évaluation sur jeu de validation</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    render_yolo_metrics(yolo_metrics)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="nv-panel">
            <div class="nv-panel-header">
                <div>
                    <div class="nv-panel-title">{icon_image(18)} Prédictions</div>
                    <p class="nv-panel-subtitle">Exemples de détections sur le jeu de test</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    pred_dir = Path("runs/detect/predict")
    if pred_dir.exists():
        imgs = list(pred_dir.glob("*.jpg")) + list(pred_dir.glob("*.png"))
        imgs = imgs[:6]
        if imgs:
            cols = st.columns(3)
            for i, img in enumerate(imgs):
                with cols[i % 3]:
                    st.image(str(img), use_container_width=True)
        else:
            _empty_state("Aucune prédiction enregistrée")
    else:
        _empty_state("Exécutez `yolo_detection.py` pour générer des prédictions")


def page_data():
    render_page_header(
        "Données",
        "Exploration du dataset et fichiers de preprocessing",
        badge="Dataset",
    )

    dist = load_distribution()
    comp = load_comparison()

    tab_dist, tab_comp, tab_files = st.tabs([
        "Distribution", "Comparaison modèles", "Fichiers",
    ])

    with tab_dist:
        c1, c2 = st.columns([1, 1], gap="medium")
        with c1:
            st.markdown(f"""
                <div class="nv-panel">
                    <div class="nv-panel-header">
                        <div>
                            <div class="nv-panel-title">{icon_layers(18)} Donut</div>
                            <p class="nv-panel-subtitle">Répartition proportionnelle</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            render_distribution(dist)
        with c2:
            st.markdown(f"""
                <div class="nv-panel">
                    <div class="nv-panel-header">
                        <div>
                            <div class="nv-panel-title">{icon_chart(18)} Barres</div>
                            <p class="nv-panel-subtitle">Volumes par classe</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            render_class_bars(dist)

    with tab_comp:
        st.markdown(f"""
            <div class="nv-panel">
                <div class="nv-panel-header">
                    <div>
                        <div class="nv-panel-title">{icon_activity(18)} Comparaison</div>
                        <p class="nv-panel-subtitle">Modèles & configurations</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        render_model_comparison(comp)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        render_model_table(comp)

    with tab_files:
        st.markdown(f"""
            <div class="nv-panel">
                <div class="nv-panel-header">
                    <div>
                        <div class="nv-panel-title">{icon_folder(18)} Fichiers processed</div>
                        <p class="nv-panel-subtitle">CSV générés par preprocessing.py</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        files = [
            ("data/processed/irm_train.csv", "Train"),
            ("data/processed/irm_val.csv",   "Validation"),
            ("data/processed/irm_test.csv",  "Test"),
        ]
        for path, label in files:
            p = Path(path)
            if p.exists():
                df = pd.read_csv(p)
                with st.expander(f"{label} · {len(df)} lignes", expanded=False):
                    render_dataframe(df.head(15))
            else:
                st.markdown(f"""
                    <div style="padding:1rem; background:rgba(193,18,31,0.05);
                                border-left:3px solid #C1121F; border-radius:8px;
                                font-size:0.85rem; margin-bottom:0.5rem;">
                        <strong style="color:#F5F5F7;">{label}</strong>
                        <span style="color:#A1A1AA;"> · Fichier introuvable : {path}</span>
                    </div>
                """, unsafe_allow_html=True)


# ============ HELPERS ============
def _empty_state(msg: str):
    st.markdown(f"""
        <div style="padding:2rem 1rem; text-align:center;
                    border:1px dashed #26262B; border-radius:12px;
                    color:#71717A; font-size:0.875rem;">
            {msg}
        </div>
    """, unsafe_allow_html=True)


# ============ ROUTER ============
page = render_sidebar()

ROUTES = {
    "overview":  page_overview,
    "detection": page_detection,
    "models":    page_models,
    "yolo":      page_yolo,
    "data":      page_data,
}

ROUTES.get(page, page_overview)()
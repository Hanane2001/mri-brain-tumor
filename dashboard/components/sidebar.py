import streamlit as st
from components.icons import (
    icon_home, icon_search, icon_activity,
    icon_target, icon_database, icon_brain,
)


NAV_ITEMS = [
    ("overview",   "Vue d'ensemble", icon_home,     "🏠"),
    ("detection",  "Détection",      icon_search,   "🔍"),
    ("models",     "Modèles",        icon_activity, "📈"),
    ("yolo",       "YOLO",           icon_target,   "🎯"),
    ("data",       "Données",        icon_database, "📁"),
]


def render_sidebar() -> str:
    """Retourne la clé de la page sélectionnée."""
    with st.sidebar:
        # Logo
        st.markdown(f"""
            <div class="nv-logo">
                <div class="nv-logo-mark">{icon_brain(20)}</div>
                <div class="nv-logo-text">
                    <h3>NeuroVision</h3>
                    <span>Brain AI Platform</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown('<div class="nv-section-label">Navigation</div>', unsafe_allow_html=True)

        # On utilise des boutons invisibles pour garder l'état via session_state
        if "current_page" not in st.session_state:
            st.session_state.current_page = "overview"

        options = {key: f"{label}" for key, label, _, _ in NAV_ITEMS}
        keys = list(options.keys())

        # Streamlit radio stylisé en menu pill via CSS (déjà géré)
        labels = [options[k] for k in keys]
        current_idx = keys.index(st.session_state.current_page)
        choice = st.radio(
            "nav",
            labels,
            index=current_idx,
            label_visibility="collapsed",
            key="nav_radio",
        )
        page = keys[labels.index(choice)]
        st.session_state.current_page = page

        # Statut système
        st.markdown('<div class="nv-section-label">Système</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="nv-status">
                <div class="nv-status-row">
                    <span><span class="nv-dot"></span>Pipeline</span>
                    <strong>Actif</strong>
                </div>
                <div class="nv-status-row">
                    <span>Modèles chargés</span>
                    <strong>4</strong>
                </div>
                <div class="nv-status-row">
                    <span>Dernière MAJ</span>
                    <strong>Aujourd'hui</strong>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Footer
        st.markdown(
            '<div style="margin-top:2rem; padding-top:1rem; border-top:1px solid #26262B; '
            'font-size:0.7rem; color:#71717A; text-align:center;">'
            'v2.0.0 · © 2025 NeuroVision AI</div>',
            unsafe_allow_html=True,
        )

    return page
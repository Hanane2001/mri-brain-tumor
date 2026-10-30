import streamlit as st


def render_kpi_row(kpis: list):
    """
    kpis: list of dict {
        'icon': str (SVG), 'label': str, 'value': str | float,
        'suffix': str, 'delta': str, 'delta_dir': 'up'|'down'|'neutral'
    }
    """
    cols = st.columns(len(kpis))
    for col, kpi in zip(cols, kpis):
        with col:
            delta_html = ""
            if kpi.get("delta"):
                arrow = "↑" if kpi.get("delta_dir") == "up" else "↓" if kpi.get("delta_dir") == "down" else "•"
                cls = f"nv-kpi-delta {kpi.get('delta_dir', '')}"
                delta_html = f'<div class="{cls}">{arrow} {kpi["delta"]}</div>'

            st.markdown(f"""
                <div class="nv-kpi">
                    <div class="nv-kpi-icon">{kpi.get('icon', '')}</div>
                    <div class="nv-kpi-label">{kpi['label']}</div>
                    <div class="nv-kpi-value"
                         data-counter="{kpi.get('counter', kpi['value'])}"
                         data-suffix="{kpi.get('suffix', '')}"
                         data-decimals="{kpi.get('decimals', 0)}">
                        {kpi['value']}{kpi.get('suffix', '')}
                    </div>
                    {delta_html}
                </div>
            """, unsafe_allow_html=True)


def render_panel(title: str, subtitle: str = "", icon_svg: str = "", content_fn=None):
    """Wrapper pour panels (cartes sections)."""
    subtitle_html = f'<p class="nv-panel-subtitle">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
        <div class="nv-panel-header">
            <div>
                <div class="nv-panel-title">{icon_svg} {title}</div>
                {subtitle_html}
            </div>
        </div>
    """, unsafe_allow_html=True)
    if content_fn:
        content_fn()


def render_pipeline(steps: list, current: int = 4):
    """steps: list of labels. current = index du step actif."""
    html = '<div class="nv-pipeline">'
    for i, label in enumerate(steps):
        if i < current:
            cls = "done"
        elif i == current:
            cls = "active"
        else:
            cls = ""
        html += (
            f'<div class="nv-pipeline-step {cls}">'
            f'<div class="nv-pipeline-dot">{i + 1}</div>'
            f'<div class="nv-pipeline-label">{label}</div>'
            f'</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_prediction(label: str, confidence: float):
    st.markdown(f"""
        <div class="nv-prediction">
            <div class="nv-prediction-label">Classe détectée</div>
            <div class="nv-prediction-value">{label}</div>
            <div class="nv-prediction-conf">Confiance · {confidence * 100:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)
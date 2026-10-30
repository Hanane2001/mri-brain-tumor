import streamlit as st
from components.icons import icon_shield


def render_page_header(title: str, subtitle: str, badge: str = "Production"):
    st.markdown(f"""
        <div class="nv-page-header">
            <div>
                <h1 class="nv-page-title">{title}</h1>
                <p class="nv-page-subtitle">{subtitle}</p>
            </div>
            <div class="nv-badge">
                {icon_shield(14)}
                <span>{badge}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
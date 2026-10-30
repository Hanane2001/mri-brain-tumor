import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from theme import COLORS, CHART_SEQUENCE


# ─── Layout de base SANS legend/xaxis/yaxis ───
def _base_layout(**extra):
    """Layout commun sans clés en conflit."""
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text_muted"], size=12),
        margin=dict(l=24, r=24, t=48, b=24),
        hoverlabel=dict(
            bgcolor=COLORS["bg_card"],
            bordercolor=COLORS["primary"],
            font=dict(color=COLORS["text"]),
        ),
    )
    base.update(extra)
    return base


# ─── Distribution des classes (donut) ───
def render_distribution(distribution: pd.DataFrame):
    fig = px.pie(
        distribution,
        names="classe",
        values="nb_image",
        color_discrete_sequence=CHART_SEQUENCE,
        hole=0.68,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        textfont=dict(size=12, color=COLORS["text"]),
        marker=dict(line=dict(color=COLORS["bg_card"], width=3)),
        hovertemplate="<b>%{label}</b><br>%{value} images<br>%{percent}<extra></extra>",
    )
    fig.update_layout(
        **_base_layout(
            height=360,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02,
                bgcolor="rgba(0,0,0,0)",
                font=dict(color=COLORS["text_muted"]),
            ),
            annotations=[dict(
                text=(
                    f"<b>{distribution['nb_image'].sum():,}</b><br>"
                    f"<span style='font-size:10px;color:#71717A'>TOTAL</span>"
                ),
                x=0.5, y=0.5,
                font=dict(size=20, color=COLORS["text"]),
                showarrow=False,
            )],
        )
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─── Comparaison modèles (barres groupées) ───
def render_model_comparison(df: pd.DataFrame):
    fig = go.Figure()
    models = df["modele"].unique()
    for i, model in enumerate(models):
        sub = df[df["modele"] == model]
        fig.add_trace(go.Bar(
            name=model,
            x=sub["configuration"],
            y=sub["test accuracy"] * 100,
            marker=dict(
                color=CHART_SEQUENCE[i % len(CHART_SEQUENCE)],
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            text=[f"{v:.1f}%" for v in sub["test accuracy"] * 100],
            textposition="outside",
            textfont=dict(color=COLORS["text"], size=11, family="Inter"),
            hovertemplate="<b>%{x}</b><br>Accuracy: %{y:.1f}%<extra></extra>",
        ))
    fig.update_layout(
        **_base_layout(
            height=380,
            barmode="group",
            bargap=0.25,
            bargroupgap=0.08,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                bgcolor="rgba(0,0,0,0)",
                font=dict(color=COLORS["text_muted"]),
            ),
            xaxis=dict(
                title="",
                gridcolor="rgba(255,255,255,0.04)",
                linecolor=COLORS["border"],
                zeroline=False,
            ),
            yaxis=dict(
                title="Accuracy (%)",
                range=[0, 105],
                gridcolor="rgba(255,255,255,0.04)",
                linecolor=COLORS["border"],
                zeroline=False,
            ),
        )
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─── Métriques YOLO (jauge) ───
def render_yolo_metrics(metrics: dict):
    items = [
        ("mAP50",     metrics.get("map50", 0)),
        ("mAP50-95",  metrics.get("map", 0)),
        ("Precision", metrics.get("precision", 0)),
        ("Recall",    metrics.get("recall", 0)),
    ]
    cols = st.columns(4)
    for col, (label, val) in zip(cols, items):
        with col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val * 100,
                number={
                    "suffix": "%",
                    "font": {"color": COLORS["text"], "size": 22, "family": "Inter"},
                },
                title={
                    "text": label,
                    "font": {"color": COLORS["text_muted"], "size": 12},
                },
                gauge={
                    "axis": {
                        "range": [0, 100],
                        "tickcolor": COLORS["text_dim"],
                        "tickfont": {"size": 9, "color": COLORS["text_dim"]},
                    },
                    "bar": {"color": COLORS["primary"], "thickness": 0.7},
                    "bgcolor": "rgba(255,255,255,0.03)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 50],   "color": "rgba(193,18,31,0.06)"},
                        {"range": [50, 80],  "color": "rgba(193,18,31,0.10)"},
                        {"range": [80, 100], "color": "rgba(193,18,31,0.16)"},
                    ],
                    "threshold": {
                        "line": {"color": COLORS["primary_soft"], "width": 2},
                        "thickness": 0.85,
                        "value": val * 100,
                    },
                },
            ))
            fig.update_layout(
                **_base_layout(
                    height=200,
                    margin=dict(l=16, r=16, t=40, b=16),
                )
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─── Progression par classe (barres horizontales) ───
def render_class_bars(distribution: pd.DataFrame):
    df = distribution.sort_values("nb_image", ascending=True)
    fig = go.Figure(go.Bar(
        y=df["classe"],
        x=df["nb_image"],
        orientation="h",
        marker=dict(
            color=df["nb_image"],
            colorscale=[[0, COLORS["primary_dark"]], [1, COLORS["primary_soft"]]],
            line=dict(width=0),
        ),
        text=df["nb_image"],
        textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
        hovertemplate="<b>%{y}</b><br>%{x} images<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(
            height=300,
            margin=dict(l=100, r=30, t=20, b=40),
            xaxis=dict(
                title="Images",
                gridcolor="rgba(255,255,255,0.04)",
                linecolor=COLORS["border"],
                zeroline=False,
            ),
            yaxis=dict(
                title="",
                gridcolor="rgba(255,255,255,0.04)",
                linecolor=COLORS["border"],
                zeroline=False,
            ),
        )
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
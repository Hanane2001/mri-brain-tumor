import streamlit as st
import pandas as pd


def render_dataframe(df: pd.DataFrame, height=None, key=None):
    """Dataframe avec style uniforme."""
    kwargs = {
        "use_container_width": True,
        "hide_index": True,
    }
    if height is not None:
        kwargs["height"] = height
    if key is not None:
        kwargs["key"] = key
    st.dataframe(df, **kwargs)


def render_model_table(df: pd.DataFrame):
    """Tableau comparatif avec statut."""
    display = df.copy()
    display["test accuracy"] = display["test accuracy"].apply(lambda x: f"{x*100:.1f}%")
    display["test loss"] = display["test loss"].apply(lambda x: f"{x:.3f}")

    best_acc = df["test accuracy"].max()
    display["statut"] = df["test accuracy"].apply(
        lambda x: "Meilleur" if x == best_acc else "Standard"
    )

    render_dataframe(display)
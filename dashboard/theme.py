COLORS = {
    "primary":       "#C1121F",
    "primary_soft":  "#E63946",
    "primary_dark":  "#8B0F1A",
    "primary_glow":  "rgba(193, 18, 31, 0.35)",
    "bg":            "#0A0A0B",
    "bg_elevated":   "#121214",
    "bg_card":       "#17171A",
    "bg_hover":      "#1F1F23",
    "border":        "#26262B",
    "border_accent": "rgba(193, 18, 31, 0.35)",
    "text":          "#F5F5F7",
    "text_muted":    "#A1A1AA",
    "text_dim":      "#71717A",
    "success":       "#10B981",
    "warning":       "#F59E0B",
    "danger":        "#EF4444",
    "info":          "#3B82F6",
}

CHART_SEQUENCE = [
    "#C1121F",
    "#E63946",
    "#F5F5F7",
    "#A1A1AA",
    "#8B0F1A",
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["text_muted"], size=12),
    title_font=dict(color=COLORS["text"], size=15),
    margin=dict(l=24, r=24, t=48, b=24),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor=COLORS["border"], zeroline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor=COLORS["border"], zeroline=False),
    hoverlabel=dict(bgcolor=COLORS["bg_card"], bordercolor=COLORS["primary"],
                    font=dict(color=COLORS["text"])),
)
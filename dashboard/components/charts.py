"""
Plotly chart templates for the dashboard.
"""
import plotly.express as px
import plotly.graph_objects as go


AUTORONTO_COLORS = {
    "primary": "#1B3A5C",
    "secondary": "#2E86AB",
    "accent": "#F6AE2D",
    "success": "#2ECC71",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "bg": "#0E1117",
    "card_bg": "#1E2A3A",
    "text": "#FAFAFA",
    "muted": "#8899AA",
}


def task_status_pie(completed, in_progress, not_started):
    fig = go.Figure(data=[go.Pie(
        labels=["Complete", "In Progress", "Not Started"],
        values=[completed, in_progress, not_started],
        marker=dict(colors=[AUTORONTO_COLORS["success"], AUTORONTO_COLORS["warning"], AUTORONTO_COLORS["muted"]]),
        hole=0.45,
        textinfo="label+percent",
        textfont=dict(size=13, color="white"),
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=280,
    )
    return fig


def team_progress_bar_chart(teams):
    names = [t["name"] for t in teams]
    progress = [t["progress"] for t in teams]
    colors = [
        AUTORONTO_COLORS["success"] if p >= 75
        else AUTORONTO_COLORS["warning"] if p >= 50
        else AUTORONTO_COLORS["danger"]
        for p in progress
    ]

    fig = go.Figure(data=[go.Bar(
        x=names,
        y=progress,
        marker_color=colors,
        text=[f"{p:.0f}%" for p in progress],
        textposition="outside",
        textfont=dict(color="white", size=11),
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(title="Progress %", range=[0, 110]),
        margin=dict(t=20, b=100, l=40, r=10),
        height=350,
    )
    return fig


def hours_comparison_chart(teams):
    names = [t["name"] for t in teams]
    actual = [t["actual_hours"] for t in teams]

    fig = go.Figure(data=[go.Bar(
        x=names, y=actual,
        marker_color=AUTORONTO_COLORS["accent"],
        text=[f"{h:.0f}h" for h in actual],
        textposition="outside",
        textfont=dict(color="white", size=11),
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(title="Actual Hours"),
        margin=dict(t=20, b=100, l=40, r=10),
        height=350,
    )
    return fig


def resource_hours_chart(resources, top_n=15):
    sorted_res = sorted(resources, key=lambda r: r.get("total_hours", 0), reverse=True)[:top_n]
    names = [r["name"] for r in sorted_res]
    hours = [round(r["total_hours"], 1) for r in sorted_res]
    colors = [
        AUTORONTO_COLORS["danger"] if r.get("role") == "ADMIN"
        else AUTORONTO_COLORS["accent"] if r.get("role") == "LEAD"
        else AUTORONTO_COLORS["secondary"]
        for r in sorted_res
    ]

    fig = go.Figure(data=[go.Bar(
        x=hours, y=names,
        orientation="h",
        marker_color=colors,
        text=[f"{h}h" for h in hours],
        textposition="outside",
        textfont=dict(color="white", size=10),
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=10),
        xaxis=dict(title="Hours Logged"),
        yaxis=dict(autorange="reversed"),
        margin=dict(t=10, b=40, l=200, r=40),
        height=max(300, len(sorted_res) * 28),
    )
    return fig


def progress_gauge(value, title="Progress"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix="%", font=dict(size=36, color="white")),
        gauge=dict(
            axis=dict(range=[0, 100], tickfont=dict(color="white")),
            bar=dict(color=AUTORONTO_COLORS["accent"]),
            bgcolor=AUTORONTO_COLORS["card_bg"],
            steps=[
                dict(range=[0, 50], color=AUTORONTO_COLORS["danger"]),
                dict(range=[50, 75], color=AUTORONTO_COLORS["warning"]),
                dict(range=[75, 100], color=AUTORONTO_COLORS["success"]),
            ],
        ),
        title=dict(text=title, font=dict(color="white", size=14)),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(t=40, b=10, l=20, r=20),
        height=200,
    )
    return fig


def team_health_heatmap(teams):
    """Create a grid heatmap of team health."""
    import math
    n = len(teams)
    cols = 6
    rows = math.ceil(n / cols)

    z = []
    text = []
    for r in range(rows):
        row_z = []
        row_text = []
        for c in range(cols):
            idx = r * cols + c
            if idx < n:
                t = teams[idx]
                row_z.append(t["progress"])
                emoji = "🟢" if t["progress"] >= 75 else ("🟡" if t["progress"] >= 50 else "🔴")
                row_text.append(f"{emoji} {t['name']}<br>{t['progress']:.0f}%")
            else:
                row_z.append(None)
                row_text.append("")
        z.append(row_z)
        text.append(row_text)

    fig = go.Figure(data=go.Heatmap(
        z=z,
        text=text,
        texttemplate="%{text}",
        textfont=dict(size=11, color="white"),
        colorscale=[
            [0, AUTORONTO_COLORS["danger"]],
            [0.5, AUTORONTO_COLORS["warning"]],
            [1, AUTORONTO_COLORS["success"]],
        ],
        zmin=0, zmax=100,
        showscale=False,
        hoverinfo="text",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, autorange="reversed"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=rows * 80 + 20,
    )
    return fig

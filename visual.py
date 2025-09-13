import numpy as np
import pandas as pd
import plotly.graph_objects as go
import shap
from scipy.stats import gaussian_kde

# ---------- Visual Charts ----------

def indicator_chart(value: float, spec_min: float, title="Predicted 28-Day Strength (MPa)"):
    is_pass = value >= spec_min
    bar_color = "green" if is_pass else "red"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title, "font": {"size": 16}},
        number={"font": {"size": 32}},
        delta={
            "reference": spec_min,
            "increasing": {"color": "green"},
            "decreasing": {"color": "red"},
            "font": {"size": 14}
        },
        gauge={
            "axis": {
                "range": [0, max(80, spec_min * 1.5)],
                "tickfont": {"size": 12}
            },
            "threshold": {
                "line": {"width": 4, "color": "red"},
                "value": spec_min,
                "thickness": 0.75
            },
            "bar": {"color": bar_color}
        }
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=40, b=0)
    )

    return fig


def bar_compare(pred: float, baseline: float, actual: float | None = None):
    labels = ["Prediction", "Dataset Avg"]
    values = [pred, baseline]
    colors = ["#1f77b4", "#ff7f0e"]

    if actual is not None:
        labels.append("Actual")
        values.append(actual)
        colors.append("#2ca02c")

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors),
        textinfo="label+value+percent",
        textposition="outside",
        pull=[0.05] * len(values),
        insidetextorientation="radial"
    ))

    fig.update_traces(
        textfont_size=14,
        showlegend=True,
        hoverinfo="label+percent+value"
    )

    fig.update_layout(
        title="Strength Comparison",
        height=400,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="right",
            x=1
        )
    )

    return fig


def strength_histogram(strengths: pd.Series):
    x = strengths.dropna()

    # Histogram
    hist = go.Histogram(
        x=x,
        nbinsx=40,
        name="Histogram",
        marker_color="#636efa",
        opacity=0.6
    )

    # KDE line
    kde = gaussian_kde(x)
    x_range = np.linspace(x.min(), x.max(), 200)
    kde_vals = kde(x_range)
    kde_scaled = kde_vals * len(x) * (x.max() - x.min()) / 40

    kde_line = go.Scatter(
        x=x_range,
        y=kde_scaled,
        mode='lines',
        name='KDE',
        line=dict(color="#ef553b", width=3)
    )

    fig = go.Figure(data=[hist, kde_line])

    fig.update_layout(
        title="Training Strength Distribution + KDE",
        xaxis_title="MPa",
        yaxis_title="Count",
        height=320,
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def roi_stacked_bar(material: float, scrap: float, lab: float):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Material",
        x=["Savings"],
        y=[material],
        marker_color="#1f77b4"
    ))
    fig.add_trace(go.Bar(
        name="Scrap",
        x=["Savings"],
        y=[scrap],
        marker_color="#ff7f0e"
    ))
    fig.add_trace(go.Bar(
        name="Lab",
        x=["Savings"],
        y=[lab],
        marker_color="#2ca02c"
    ))

    fig.update_layout(
        title="Monthly ROI Breakdown",
        barmode="group",
        height=300,
        yaxis_title="USD",
        margin=dict(l=40, r=20, t=40, b=40)
    )
    return fig

# ---------- Explainability ----------

def shap_local_bar(model, x_row: pd.DataFrame):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x_row)[0]
    order = np.argsort(np.abs(shap_values))[::-1]
    features = x_row.columns[order]
    values = shap_values[order]

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation="h",
        marker_color=["#636efa" if v >= 0 else "#ef553b" for v in values]
    ))

    fig.update_layout(
        title="SHAP Values (Local Explanation)",
        height=420,
        margin=dict(l=120, r=20, t=40, b=40),
        xaxis_title="Impact on Prediction",
        yaxis_title="Feature"
    )
    return fig

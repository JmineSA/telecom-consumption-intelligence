import plotly.graph_objects as go

from . import palette
from .config import AMBER, NAVY, PRED, TARGET, TEAL, KNOWN


def _c():
    return palette.CHART


def _tone(color):
    """Map the series colours used by pages to colours that read on both light and dark backgrounds."""
    c = palette.CHART
    return {NAVY: c["actual"], TEAL: c["teal"], AMBER: c["amber"]}.get(color, color)


def _base(fig, height=320):
    """Layout without colours: text, grid and axis colours come from Streamlit's chart theme, which follows the theme live."""
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", size=13),
        legend=dict(orientation="h", y=-0.18, x=0), hovermode="x unified")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(zeroline=False)
    return fig


def trend(df):
    """Average next-day usage per customer: actual vs forecast, by the day it is for."""
    g = df.groupby("forecast_date").agg(actual=(TARGET, "mean"), forecast=(PRED, "mean")).reset_index()
    fig = go.Figure()
    fig.add_scatter(x=g["forecast_date"], y=g["actual"], name="Actual", mode="lines",
                    line=dict(color=_c()["actual"], width=2.5), hovertemplate="%{y:.2f} GB")
    fig.add_scatter(x=g["forecast_date"], y=g["forecast"], name="Forecast", mode="lines",
                    line=dict(color=_c()["teal"], width=2.5, dash="dash"), hovertemplate="%{y:.2f} GB")
    fig.update_yaxes(title="GB per customer per day")
    return _base(fig)


def plan_mix(cust):
    order = [p for p in KNOWN["plan_type"] if p in set(cust["plan_type"])] + \
            sorted(set(cust["plan_type"]) - set(KNOWN["plan_type"]))
    counts = cust["plan_type"].value_counts().reindex(order)
    k = _c()
    colors = [k["actual"], k["teal"], k["teal_soft"], k["amber"], k["grey"]][: len(order)]
    fig = go.Figure(go.Pie(labels=[p.replace("_", " ") for p in order], values=counts.values, hole=0.58,
                           marker=dict(colors=colors, line=dict(color="rgba(128,128,128,0.55)", width=1.5)), sort=False, textinfo="percent",
                           hovertemplate="%{label}: %{value:,} customers<extra></extra>"))
    fig = _base(fig, 320)
    fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.1))
    return fig


def hbar(series, color=TEAL, fmt="{:,.0f}", unit=""):
    """Horizontal bars, largest on top. `series` is indexed by label."""
    labels = [str(i).replace("_", " ") for i in series.index]
    fig = go.Figure(go.Bar(x=series.values, y=labels, orientation="h", marker=dict(color=_tone(color)),
                           text=[fmt.format(v) + unit for v in series.values], textposition="outside",
                           cliponaxis=False, hovertemplate="%{y}: %{text}<extra></extra>"))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(visible=False, range=[0, float(series.max()) * 1.25 if len(series) else 1])
    fig = _base(fig, max(150, 46 * len(series) + 30))
    fig.update_layout(hovermode="closest", showlegend=False)
    return fig


def error_trend(d, ref_mae=None):
    g = d.dropna(subset=[TARGET]).assign(ae=lambda x: x["residual"].abs()).groupby("forecast_date")["ae"].mean().reset_index()
    fig = go.Figure()
    fig.add_scatter(x=g["forecast_date"], y=g["ae"], name="Average error", mode="lines",
                    line=dict(color=_c()["actual"], width=2.5), hovertemplate="%{y:.2f} GB")
    if ref_mae:
        fig.add_hline(y=ref_mae, line=dict(color=_c()["amber"], width=2, dash="dash"),
                      annotation_text="Error when the model was trained", annotation_position="top left")
    fig.update_yaxes(title="Average error (GB)", rangemode="tozero")
    return _base(fig)


def actual_vs_forecast(d, n=3000):
    d = d.dropna(subset=[TARGET])
    d = d.sample(min(n, len(d)), random_state=0)
    hi = float(max(d[TARGET].max(), d[PRED].max()))
    fig = go.Figure()
    fig.add_scattergl(x=d[PRED], y=d[TARGET], mode="markers", marker=dict(color=_c()["teal"], size=5, opacity=0.35),
                      hovertemplate="Forecast %{x:.1f} GB<br>Actual %{y:.1f} GB<extra></extra>")
    fig.add_scatter(x=[0, hi], y=[0, hi], mode="lines", line=dict(color=_c()["grey"], dash="dash"), hoverinfo="skip")
    fig.update_xaxes(title="Forecast (GB)")
    fig.update_yaxes(title="Actual (GB)")
    fig = _base(fig, 340)
    fig.update_layout(hovermode="closest", showlegend=False)
    return fig


def residual_hist(d):
    r = d.dropna(subset=[TARGET])["residual"].clip(-20, 20)
    fig = go.Figure(go.Histogram(x=r, nbinsx=60, marker=dict(color=_c()["teal"]),
                                 hovertemplate="%{x:.1f} GB: %{y:,} rows<extra></extra>"))
    fig.add_vline(x=0, line=dict(color=_c()["actual"], width=1.5))
    fig.update_xaxes(title="Actual minus forecast (GB), capped at 20")
    fig.update_yaxes(title="Rows")
    fig = _base(fig, 340)
    fig.update_layout(hovermode="closest", showlegend=False)
    return fig


def customer_line(d):
    d = d.sort_values("forecast_date")
    fig = go.Figure()
    fig.add_scatter(x=d["forecast_date"], y=d[TARGET], name="Actual", mode="lines+markers",
                    line=dict(color=_c()["actual"], width=2.5), hovertemplate="%{y:.2f} GB")
    fig.add_scatter(x=d["forecast_date"], y=d[PRED], name="Forecast", mode="lines+markers",
                    line=dict(color=_c()["teal"], width=2.5, dash="dash"), hovertemplate="%{y:.2f} GB")
    fig.update_yaxes(title="GB per day")
    return _base(fig, 300)


def contrib(series, unit=" GB"):
    """Signed bars for one forecast: teal pushes the forecast up, amber pulls it down. Largest effect on top."""
    s = series.reindex(series.abs().sort_values(ascending=False).index)
    c = _c()
    labels = [str(i).replace("_", " ") for i in s.index]
    fig = go.Figure(go.Bar(x=s.values, y=labels, orientation="h", marker=dict(color=[c["teal"] if v >= 0 else c["amber"] for v in s.values]),
                           text=[f"{v:+.2f}{unit}" for v in s.values], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{text}<extra></extra>"))
    lim = float(s.abs().max()) * 1.3 if len(s) else 1
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(range=[-lim, lim], zeroline=True, showgrid=False, showticklabels=False)
    fig = _base(fig, max(150, 40 * len(s) + 40))
    fig.update_layout(hovermode="closest", showlegend=False)
    return fig


def compare_bars(t, a_name="A", b_name="B"):
    """A and B side by side for each group. `t` has columns A and B, indexed by group."""
    c = _c()
    fig = go.Figure()
    fig.add_bar(x=[str(i).replace("_", " ") for i in t.index], y=t["A"], name=a_name, marker_color=c["actual"],
                hovertemplate="%{x}: %{y:,.2f}<extra>" + a_name + "</extra>")
    fig.add_bar(x=[str(i).replace("_", " ") for i in t.index], y=t["B"], name=b_name, marker_color=c["teal"],
                hovertemplate="%{x}: %{y:,.2f}<extra>" + b_name + "</extra>")
    fig.update_layout(barmode="group", hovermode="closest")
    fig.update_yaxes(rangemode="tozero")
    return _base(fig)

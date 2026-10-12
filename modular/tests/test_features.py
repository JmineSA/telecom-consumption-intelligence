import pandas as pd

from src.features import build_features


def _toy():
    d = pd.date_range("2026-01-01", periods=10)
    rows = [{"user_id": u, "date": x, "total_gb": float(i + 1 + 10 * u),
             "streaming_gb": 1.0, "social_gb": 1.0, "gaming_gb": 1.0, "messaging_gb": 1.0}
            for u in (0, 1) for i, x in enumerate(d)]
    return pd.DataFrame(rows)


def test_lag_is_yesterday_and_target_is_tomorrow():
    out = build_features(_toy())
    u0 = out[out.user_id == 0].reset_index(drop=True)
    assert u0.loc[3, "lag_1d_total_gb"] == u0.loc[2, "total_gb"]
    assert u0.loc[3, "target_next_day_gb"] == u0.loc[4, "total_gb"]
    assert pd.isna(u0.loc[9, "target_next_day_gb"])  # last day is the forecast row


def test_rolling_average_excludes_today():
    out = build_features(_toy())
    u0 = out[out.user_id == 0].reset_index(drop=True)
    assert u0.loc[3, "rolling_7d_avg_gb"] == (1 + 2 + 3) / 3


def test_customers_do_not_leak_into_each_other():
    out = build_features(_toy())
    u1 = out[out.user_id == 1].reset_index(drop=True)
    assert pd.isna(u1.loc[0, "lag_1d_total_gb"])


def test_persistent_gap_counts_only_the_running_streak():
    from src.kpis import persistent_gap
    d = pd.date_range("2026-01-01", periods=6)
    rows = []
    for u, res in (("a", [3, 3, 3, 3, 0, 3]), ("b", [3, 3, 3, 3, 3, 3]), ("c", [0, 0, 0, 0, 3, 3])):
        for x, r in zip(d, res):
            rows.append({"user_id": u, "date": x, "residual": float(r), "target_next_day_gb": 1.0, "pred_next_day_gb": 1.0})
    out = persistent_gap(pd.DataFrame(rows), 2.0, 3)
    assert list(out["user_id"]) == ["b"]  # a's streak was broken, c has only 2 days


def _actions_frame():
    """Two regions: North has high forecast use and heavy congestion, South does not."""
    rows = []
    for u, region, pred, cong in (("n1", "North", 12.0, 1), ("n2", "North", 12.0, 1),
                                  ("s1", "South", 6.0, 0), ("s2", "South", 6.0, 0)):
        for i, x in enumerate(pd.date_range("2026-01-01", periods=4)):
            rows.append({"user_id": u, "date": x, "region": region, "plan_type": "Prepaid_Daily", "congested": cong, "total_gb": pred,
                         "pred_next_day_gb": pred, "target_next_day_gb": pred, "residual": 0.0,
                         "forecast_date": x + pd.Timedelta(days=1), "monthly_bill_zar": 100.0, "churn_probability": 0.1})
    return pd.DataFrame(rows)


def test_capacity_card_only_for_high_demand_and_congested_region(monkeypatch):
    import streamlit as st
    from src import actions
    monkeypatch.setattr(st, "session_state", {"buffer": 8, "eval_from": None})
    b = {"df": _actions_frame(), "threshold": 0.5, "report": {"has_actuals": True}}
    card = actions.capacity(b)
    assert card is not None and "North" in card["title"]
    quiet = _actions_frame().assign(congested=0)
    assert actions.capacity({**b, "df": quiet}) is None  # no congestion, no recommendation


def test_cards_hidden_without_actuals(monkeypatch):
    import streamlit as st
    from src import actions
    monkeypatch.setattr(st, "session_state", {"topup_gb": 2.0, "topup_days": 3, "retain_gb": 2.0, "retain_days": 5,
                                              "price_gb": 30, "takeup": 20, "buffer": 8, "eval_from": None})
    b = {"df": _actions_frame(), "threshold": 0.5, "report": {"has_actuals": False}}
    assert actions.top_up(b) is None and actions.under_use(b) is None and actions.reliability(b) is None


def test_top_up_card_uses_sidebar_assumptions(monkeypatch):
    import streamlit as st
    from src import actions
    f = _actions_frame()
    f["residual"] = 3.0                      # every customer beat the forecast by 3 GB on every day
    monkeypatch.setattr(st, "session_state", {"topup_gb": 2.0, "topup_days": 3, "retain_gb": 2.0, "retain_days": 5,
                                              "price_gb": 30, "takeup": 20, "buffer": 8, "eval_from": None})
    card = actions.top_up({"df": f, "threshold": 0.5, "report": {"has_actuals": True}})
    assert card["metrics"][0] == ("Subscribers", "4")
    assert card["metrics"][2][1] == "R 2,160"   # 4 customers x 3 GB x 30 days x R30 x 20% take-up

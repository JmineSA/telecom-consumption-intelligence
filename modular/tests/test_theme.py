"""Every colour pair the app draws must stay readable in both themes (WCAG contrast)."""
import pytest

from src import palette


def _lum(hex_):
    r, g, b = (int(hex_.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _ratio(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


@pytest.mark.parametrize("theme", ["LIGHT", "DARK"])
@pytest.mark.parametrize("fg,bg", palette.TEXT_PAIRS)
def test_text_is_readable(theme, fg, bg):
    colours = getattr(palette, theme)
    assert _ratio(colours[fg], colours[bg]) >= 4.5, f"{theme}: {fg} on {bg}"


@pytest.mark.parametrize("name", list(palette.CHART))
def test_chart_colours_show_on_every_background(name):
    backgrounds = [palette.LIGHT["page"], palette.LIGHT["card"], palette.DARK["page"], palette.DARK["card"]]
    for bg in backgrounds:
        assert _ratio(palette.CHART[name], bg) >= 3.0, f"{name} on {bg}"


def test_left_edge_colours_show_on_cards():
    for theme in (palette.LIGHT, palette.DARK):
        for key in ("edge_teal", "edge_amber", "edge_risk", "dot_pass", "dot_warn", "dot_crit"):
            assert _ratio(theme[key], theme["card"]) >= 3.0


def test_kpi_animates_once_per_visit(monkeypatch):
    import streamlit as st
    from src import theme

    class Col:
        def __init__(self): self.out = []
        def markdown(self, h, unsafe_allow_html=False): self.out.append(h)

    monkeypatch.setattr(st, "session_state", {})
    col = Col()
    theme.begin_page("overview"); theme.kpi(col, "A", "1", accent="risk"); theme.kpi(col, "B", "2")
    assert 'class="kpi risk enter"' in col.out[0] and 'class="kpi neutral enter"' in col.out[1]
    assert "--i:0" in col.out[0] and "--i:1" in col.out[1]
    theme.begin_page("overview"); theme.kpi(col, "A", "9", accent="risk")      # rerun, e.g. a filter changed
    assert "enter" not in col.out[2]
    theme.begin_page("revenue"); theme.kpi(col, "A", "9")                      # page re-entered
    theme.begin_page("overview"); theme.kpi(col, "A", "9")
    assert "enter" in col.out[3] and "enter" in col.out[4]

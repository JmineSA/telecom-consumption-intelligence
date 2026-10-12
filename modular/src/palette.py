"""Colours for custom components in light and dark mode.

Streamlit's own widgets follow the theme in .streamlit/config.toml. Everything this app draws itself follows it too:

* HTML cards and tags use the CSS function light-dark(). Streamlit marks the page as light or dark, so these
  colours switch the moment the theme changes, with no rerun.
* Plotly charts cannot use light-dark(), so series colours come from CHART: mid-tone colours that keep at
  least 3:1 contrast on both the light and the dark backgrounds. Axis, grid and text colours are left to
  Streamlit's chart theme, which also switches live.
"""

LIGHT = {
    "page": "#F3F5F7", "card": "#FFFFFF", "line": "#E1E6EC", "row_line": "#E8EDF2",
    "ink": "#0F1B2D", "muted": "#5B6B7F",
    "good": "#0A6670", "bad": "#B23A0A",
    "tag_bg": "#FDE9D9", "tag_fg": "#8F3207",
    "tag_teal_bg": "#DDF1F3", "tag_teal_fg": "#0A5A62",
    "tag_risk_bg": "#FBE0D3", "tag_risk_fg": "#8F3207",
    "tag_grey_bg": "#E8EDF2", "tag_grey_fg": "#3B4A5E",
    "tag_pass_bg": "#DDF1E4", "tag_pass_fg": "#14532D",
    "edge_teal": "#0E7C86", "edge_amber": "#CF6C20", "edge_risk": "#C2410C",
    "tag_warn_bg": "#FEF3C7", "tag_warn_fg": "#6B4200", "tag_crit_bg": "#FDE2E2", "tag_crit_fg": "#8A1C1C",
    "dot_pass": "#1E8E4E", "dot_warn": "#B87A00", "dot_crit": "#C62828",
    "red_edge": "#B83B3B", "red_tint": "#FFF5F4", "red_fg": "#9B2C2C",
    "shadow_sm": "rgba(15,27,45,.08)", "shadow_md": "rgba(15,27,45,.14)",
    "side_bg": "#0F1B2D", "side_ink": "#E6ECF3", "side_muted": "#A9B6C7", "side_accent": "#3FB7C1",
}
DARK = {
    "page": "#0B1220", "card": "#141C2C", "line": "#2A3650", "row_line": "#26324A",
    "ink": "#E6ECF3", "muted": "#9AA8BC",
    "good": "#6FD0D9", "bad": "#FF9A6B",
    "tag_bg": "#4A2E14", "tag_fg": "#FFD3A8",
    "tag_teal_bg": "#0F3A3F", "tag_teal_fg": "#A8E8EE",
    "tag_risk_bg": "#4A2414", "tag_risk_fg": "#FFC7A8",
    "tag_grey_bg": "#26324A", "tag_grey_fg": "#C9D3E0",
    "tag_pass_bg": "#123B22", "tag_pass_fg": "#A7E8BE",
    "edge_teal": "#3FB7C1", "edge_amber": "#F0924F", "edge_risk": "#F0743A",
    "tag_warn_bg": "#4A3A0C", "tag_warn_fg": "#FDE9A8", "tag_crit_bg": "#4F1D1D", "tag_crit_fg": "#FFC2C2",
    "dot_pass": "#4CC38A", "dot_warn": "#E5B53B", "dot_crit": "#FF6B6B",
    "red_edge": "#E5675F", "red_tint": "#1D1A27", "red_fg": "#FFB0A8",
    "shadow_sm": "rgba(0,0,0,.35)", "shadow_md": "rgba(0,0,0,.55)",
    "side_bg": "#070C16", "side_ink": "#E6ECF3", "side_muted": "#A9B6C7", "side_accent": "#3FB7C1",
}

# Chart series colours that work on every background above.
CHART = {"actual": "#5F7FAE", "teal": "#0E7C86", "teal_soft": "#2893A0", "amber": "#CF6C20", "grey": "#7A8799"}

# Pairs of (foreground, background) that must stay readable. Checked by tests/test_theme.py.
TEXT_PAIRS = [("ink", "card"), ("muted", "card"), ("good", "card"), ("bad", "card"), ("ink", "page"), ("muted", "page"),
              ("tag_fg", "tag_bg"), ("tag_teal_fg", "tag_teal_bg"), ("tag_risk_fg", "tag_risk_bg"),
              ("tag_grey_fg", "tag_grey_bg"), ("tag_pass_fg", "tag_pass_bg"), ("tag_warn_fg", "tag_warn_bg"),
              ("tag_crit_fg", "tag_crit_bg"), ("red_fg", "red_tint"), ("red_fg", "card"),
              ("side_ink", "side_bg"), ("side_muted", "side_bg")]


def css(prop: str, key: str) -> str:
    """One CSS declaration that follows the theme. The light value comes first as a fallback for old browsers."""
    return f"{prop}:{LIGHT[key]};{prop}:light-dark({LIGHT[key]},{DARK[key]});"


def ld(key: str) -> str:
    return f"light-dark({LIGHT[key]},{DARK[key]})"

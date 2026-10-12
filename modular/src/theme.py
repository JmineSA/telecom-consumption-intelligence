"""Look and feel: CSS, KPI cards, number formats."""
import streamlit as st

from . import config, palette


def inject():
    c = palette.css
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
.stApp, .stApp p, .stApp label, .stMarkdown {{ font-family: 'DM Sans', sans-serif; }}
/* keep Streamlit's icon font, otherwise icon names print over the text (e.g. the expander arrow) */
[data-testid="stIconMaterial"], span[class*="material-symbols"], .material-icons {{
  font-family: 'Material Symbols Rounded', 'Material Icons' !important; }}
h1 {{ font-size: 1.7rem !important; font-weight: 700 !important; padding: 0 !important; }}
.kpi, .panel, .act {{ border-width:1px; border-style:solid; border-radius:12px; {c('background','card')} {c('border-color','line')} {c('color','ink')} }}
.kpi {{ padding:16px 18px; height:100%; min-height:156px; box-sizing:border-box; border-left-width:4px; {c('border-left-color','edge_teal')} }}
.kpi.ok {{ {c('border-left-color','dot_pass')} }}
.kpi.watch {{ {c('border-left-color','edge_amber')} }}
.kpi.risk {{ {c('border-left-color','red_edge')} {c('background','red_tint')} }}
.kpi.risk .d, .kpi.risk .d.bad {{ {c('color','red_fg')} }}
/* Entrance: only on a card's first render after entering a page (see theme.kpi). Transform and opacity only, so nothing shifts. */
@keyframes kpi-in {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:none; }} }}
.kpi.enter {{ animation:kpi-in 480ms cubic-bezier(.2,.7,.2,1) backwards; animation-delay:calc(var(--i,0) * 70ms); }}
@media (prefers-reduced-motion: reduce) {{ .kpi.enter {{ animation:none; }} }}
.kpi .k {{ font-size:13px; {c('color','muted')} }}
.kpi .v {{ font-size:27px; font-weight:700; margin-top:4px; {c('color','ink')} line-height:1.15; }}
.kpi .d {{ font-size:12px; margin-top:6px; {c('color','good')} }}
.kpi .d.bad {{ {c('color','bad')} }}
.kpi .d.flat {{ {c('color','muted')} }}
.panel {{ padding:16px 18px; }}
.alert {{ display:flex; gap:12px; align-items:flex-start; padding:10px 0; border-bottom-width:1px; border-bottom-style:solid; {c('border-bottom-color','row_line')} font-size:14px; {c('color','ink')} }}
.alert:last-child {{ border-bottom:none; }}
.tag {{ font-size:11px; padding:3px 9px; border-radius:10px; white-space:nowrap; font-weight:500; {c('background','tag_bg')} {c('color','tag_fg')} }}
.tag.teal {{ {c('background','tag_teal_bg')} {c('color','tag_teal_fg')} }}
.tag.risk {{ {c('background','tag_risk_bg')} {c('color','tag_risk_fg')} }}
.tag.grey {{ {c('background','tag_grey_bg')} {c('color','tag_grey_fg')} }}
.tag.pass {{ {c('background','tag_pass_bg')} {c('color','tag_pass_fg')} }}
.act {{ border-left-width:4px; padding:16px 18px; margin-bottom:12px; {c('border-left-color','muted')} }}
.act.opportunity {{ {c('border-left-color','edge_teal')} }} .act.attention {{ {c('border-left-color','edge_amber')} }} .act.risk {{ {c('border-left-color','edge_risk')} }}
.act .at {{ font-weight:700; font-size:15px; margin:8px 0 4px; {c('color','ink')} }}
.act .ax {{ font-size:13px; line-height:1.5; {c('color','muted')} }}
.act .ar {{ display:flex; gap:24px; flex-wrap:wrap; margin-top:12px; }}
.act .av {{ font-size:17px; font-weight:700; {c('color','ink')} }} .act .al {{ font-size:11.5px; {c('color','muted')} }}
.act .an {{ font-size:11px; margin-top:10px; {c('color','muted')} }}
.chk {{ padding:12px 0; border-bottom-width:1px; border-bottom-style:solid; {c('border-bottom-color','row_line')} }}
.chk:last-child {{ border-bottom:none; }}
.chk-h {{ display:flex; gap:10px; align-items:baseline; flex-wrap:wrap; font-size:14px; {c('color','ink')} }}
.chk-s {{ font-size:12.5px; line-height:1.5; margin-top:4px; {c('color','muted')} }}
.chk-s b {{ font-weight:600; {c('color','ink')} }}
.gh {{ font-weight:700; font-size:15px; margin-bottom:2px; {c('color','ink')} }}
.gh span {{ font-weight:400; font-size:12px; margin-left:8px; {c('color','muted')} }}
.dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }}
.dot.pass {{ {c('background','dot_pass')} }} .dot.warn {{ {c('background','dot_warn')} }} .dot.crit {{ {c('background','dot_crit')} }}
.tag.warn {{ {c('background','tag_warn_bg')} {c('color','tag_warn_fg')} }}
.tag.crit {{ {c('background','tag_crit_bg')} {c('color','tag_crit_fg')} }}
.gate {{ border-width:1px; border-left-width:6px; border-style:solid; border-radius:12px; padding:18px 20px; margin-top:8px; }}
.gate .gt {{ font-size:20px; font-weight:700; }} .gate .gx {{ font-size:13px; margin-top:6px; line-height:1.5; }}
.gate.ready {{ {c('background','tag_pass_bg')} {c('color','tag_pass_fg')} {c('border-color','dot_pass')} }}
.gate.blocked {{ {c('background','tag_crit_bg')} {c('color','tag_crit_fg')} {c('border-color','dot_crit')} }}
.side-gate {{ font-size:12px; line-height:1.4; padding:8px 10px; border-radius:8px; margin:2px 0 10px; }}
.side-gate.ready {{ {c('background','tag_pass_bg')} {c('color','tag_pass_fg')} }}
.side-gate.blocked {{ {c('background','tag_crit_bg')} {c('color','tag_crit_fg')} }}
.brand {{ font-weight:700; font-size:17px; line-height:1.25; padding:6px 0 2px; }}
/* ---- Card hover: one language, three intensities. Transform/shadow/border only, so nothing reflows. ---- */
.kpi, .act, .panel {{ position:relative; transition:transform 220ms cubic-bezier(.2,.7,.2,1), box-shadow 220ms ease, border-color 220ms ease, background-color 220ms ease; }}
.kpi .k, .kpi .v {{ transition:color 220ms ease; }}
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {{ border-radius:12px; box-shadow:0 0 0 1px transparent; transition:box-shadow 220ms ease; }}
@media (hover:hover) {{
  .kpi:hover {{ transform:translateY(-4px); z-index:2; box-shadow:0 8px 22px {palette.ld('shadow_md')}; {c('border-top-color','edge_teal')} {c('border-right-color','edge_teal')} {c('border-bottom-color','edge_teal')} }}
  .kpi.ok:hover {{ {c('border-top-color','dot_pass')} {c('border-right-color','dot_pass')} {c('border-bottom-color','dot_pass')} }}
  .kpi.watch:hover {{ {c('border-top-color','edge_amber')} {c('border-right-color','edge_amber')} {c('border-bottom-color','edge_amber')} }}
  .kpi.risk:hover {{ {c('border-top-color','red_edge')} {c('border-right-color','red_edge')} {c('border-bottom-color','red_edge')} }}
  .kpi:hover .k {{ {c('color','ink')} }}
  .act:hover {{ transform:translateY(-2px); z-index:1; box-shadow:0 8px 22px {palette.ld('shadow_md')}; {c('border-top-color','muted')} {c('border-right-color','muted')} {c('border-bottom-color','muted')} }}
  .panel:hover {{ box-shadow:0 2px 8px {palette.ld('shadow_sm')}; {c('border-color','muted')} }}
  [data-testid="stPlotlyChart"]:hover, [data-testid="stDataFrame"]:hover {{ box-shadow:0 0 0 1px {palette.ld('line')}, 0 2px 10px {palette.ld('shadow_sm')}; }}
}}
@media (prefers-reduced-motion: reduce) {{
  .kpi, .act, .panel, .kpi .k, .kpi .v, [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {{ transition:none; }}
  .kpi:hover, .act:hover {{ transform:none; }}
}}

/* ---- Sidebar navigation. Selectors use Streamlit's stable data-testid values and stay inside the nav. ---- */
[data-testid="stSidebarNav"]::before {{ content:"{config.APP_NAME}"; display:block; padding:4px 12px 14px 32px; font-weight:700; font-size:16px; letter-spacing:.2px;
  {c('color','side_ink')} background:radial-gradient(circle at 16px 13px, var(--side-dot) 0 5px, transparent 5.5px); }}
[data-testid="stSidebarNav"] {{ --side-dot:{palette.ld('side_accent')}; padding-top:6px; }}
[data-testid="stSidebarNavItems"] {{ gap:2px; padding:0 4px; max-height:none; }}
[data-testid="stSidebarNavLink"] {{ position:relative; display:flex; align-items:center; gap:10px; min-height:38px; padding:7px 12px; border-radius:10px; {c('color','side_muted')}
  transition:background-color 180ms ease, color 180ms ease, transform 180ms ease; }}
[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] {{ font-size:20px; color:inherit; }}
[data-testid="stSidebarNavLink"] p {{ margin:0; font-size:14px; font-weight:500; color:inherit; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
[data-testid="stSidebarNavLink"]:hover {{ background-color:color-mix(in srgb, {palette.ld('side_accent')} 14%, transparent); {c('color','side_ink')} }}
[data-testid="stSidebarNavLink"][aria-current="page"] {{ background-color:color-mix(in srgb, {palette.ld('side_accent')} 22%, transparent); {c('color','side_ink')} }}
[data-testid="stSidebarNavLink"][aria-current="page"] p {{ font-weight:700; }}
[data-testid="stSidebarNavLink"]::before {{ content:""; position:absolute; left:0; top:9px; bottom:9px; width:3px; border-radius:0 3px 3px 0; background:{palette.ld('side_accent')};
  opacity:0; transform:scaleY(.4); transition:opacity 180ms ease, transform 180ms ease; }}
[data-testid="stSidebarNavLink"][aria-current="page"]::before {{ opacity:1; transform:none; }}
[data-testid="stSidebarNavLink"]:focus-visible {{ outline:2px solid {palette.ld('side_accent')}; outline-offset:1px; }}
[data-testid="stSidebarNavSeparator"] {{ display:none; }}
@media (hover:hover) {{ [data-testid="stSidebarNavLink"]:not([aria-current="page"]):hover {{ transform:translateX(2px); }} }}
@media (prefers-reduced-motion: reduce) {{ [data-testid="stSidebarNavLink"], [data-testid="stSidebarNavLink"]::before {{ transition:none; }}
  [data-testid="stSidebarNavLink"]:hover {{ transform:none !important; }} }}
[data-testid="stNavSectionHeader"] {{ padding:14px 12px 4px; }}
[data-testid="stNavSectionHeader"], [data-testid="stNavSectionHeader"] * {{ font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; {c('color','side_muted')} }}
.side-h {{ font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; margin:6px 0 2px; {c('color','side_muted')} }}
</style>""", unsafe_allow_html=True)


ACCENTS = ("neutral", "ok", "watch", "risk")


def begin_page(page_key):
    """Call once per run, before the page script. Cards animate once per visit to a page, not on every rerun."""
    ss = st.session_state
    if ss.get("_kpi_page") != page_key:
        ss["_kpi_page"], ss["_kpi_seen"] = page_key, set()
    ss["_kpi_n"] = 0


def kpi(col, label, value, sub="", tone="good", accent="neutral"):
    """One KPI card. accent: neutral (teal), ok (green), watch (amber) or risk (red, only for real risk measures)."""
    assert accent in ACCENTS, accent
    ss = st.session_state
    seen, key = ss.setdefault("_kpi_seen", set()), (ss.get("_kpi_page"), label)
    enter = key not in seen          # first render in this visit: animate; later reruns render it without the class
    seen.add(key)
    i = ss.get("_kpi_n", 0); ss["_kpi_n"] = i + 1
    cls = f"kpi {accent}" + (" enter" if enter else "")
    col.markdown(f'<div class="{cls}" style="--i:{min(i, 8)}"><div class="k">{label}</div><div class="v">{value}</div>'
                 f'<div class="d {tone}">{sub}</div></div>', unsafe_allow_html=True)


def int_(x):   return f"{x:,.0f}"
def gb(x):     return f"{x:,.1f} GB"
def rand(x):
    return f"R {x/1e6:,.1f}M" if abs(x) >= 1e6 else f"R {x:,.0f}"
def pct(x, signed=False): return f"{x:+.1%}" if signed else f"{x:.1%}"
def label(s):  return str(s).replace("_", " ")


def gate_summary(q) -> str:
    """One line: the dataset status and how many warnings came with it."""
    w, c = q.count("warn"), q.count("crit")
    if q.ready:
        return "Ready for scoring" + (f", {w} warning{'s' if w != 1 else ''}" if w else "")
    return f"Not ready for scoring, {c} critical issue{'s' if c != 1 else ''}"


def data_label(b, checks=True):
    """Which data is loaded, and whether it passed the data checks."""
    r, q = b["report"], st.session_state.get("quality")
    line = (f"Showing {b['source']}: {r['rows']:,} rows from {r['customers']:,} customers, "
            f"{r['date_min']:%d %b %Y} to {r['date_max']:%d %b %Y}."
            + (" Scored with the retrained model." if st.session_state.get("model_name") == "Retrained model" else ""))
    if checks and q is not None and not st.session_state.get("quality_blocked"):
        line += f" Data checks: {gate_summary(q).lower()}. Details are on the Data Checks page."
    st.caption(line)


def gate_badge(q, blocked):
    """Compact status under the uploader."""
    from html import escape as e
    if blocked:
        txt, cls = f"{e(q.source)} was not loaded. {e(gate_summary(q))}. See Data Checks.", "blocked"
    else:
        txt, cls = e(gate_summary(q)) + ".", "ready"
    st.markdown(f'<div class="side-gate {cls}">{txt}</div>', unsafe_allow_html=True)


_PILL = {"pass": ("Passed", "pass"), "warn": ("Warning", "warn"), "crit": ("Critical", "crit")}


def check_group(name, checks):
    """One panel of checks: status, what was found, why it matters, and what to do."""
    from html import escape as e
    w, c = sum(x.status == "warn" for x in checks), sum(x.status == "crit" for x in checks)
    meta = f"{len(checks)} check{'s' if len(checks) != 1 else ''}" + (f", {w} warning{'s' if w != 1 else ''}" if w else "") \
        + (f", {c} critical" if c else "")
    rows = []
    for x in checks:
        label_, cls = _PILL[x.status]
        row = (f'<div class="chk"><div class="chk-h"><span class="tag {cls}"><span class="dot {cls}"></span>{label_}</span>'
               f'<b>{e(x.name)}</b><span>{e(x.finding)}</span></div>')
        if x.impact:
            row += f'<div class="chk-s">{"<b>Why it matters.</b> " if x.status != "pass" else ""}{e(x.impact)}</div>'
        if x.action and x.status != "pass":
            row += f'<div class="chk-s"><b>What to do.</b> {e(x.action)}</div>'
        rows.append(row + "</div>")
    st.markdown(f'<div class="panel" style="margin-bottom:12px"><div class="gh">{e(name)}<span>{meta}</span></div>{"".join(rows)}</div>',
                unsafe_allow_html=True)


def gate_banner(q, loaded_source):
    from html import escape as e
    w, c = q.count("warn"), q.count("crit")
    if q.ready:
        note = (f"{w} warning{'s' if w != 1 else ''} to review. Scoring continued, and the dashboard now shows this dataset."
                if w else "Every check passed. Scoring continued, and the dashboard now shows this dataset.")
        html = f'<div class="gate ready"><div class="gt">Dataset Status: READY FOR SCORING</div><div class="gx">{e(note)}</div></div>'
    else:
        note = (f"{c} critical issue{'s' if c != 1 else ''} must be fixed before this dataset can be scored. "
                f"Nothing was scored, and the dashboard is still showing {loaded_source}.")
        html = f'<div class="gate blocked"><div class="gt">Dataset Status: NOT READY FOR SCORING</div><div class="gx">{e(note)}</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def show(fig):
    """Draw a Plotly chart at full width. Works on older and newer Streamlit versions."""
    try:
        st.plotly_chart(fig, width="stretch")
    except Exception:
        st.plotly_chart(fig, use_container_width=True)


_STATE = {"opportunity": ("Opportunity", "teal"), "attention": ("Attention", ""),
          "risk": ("Risk", "risk"), "monitor": ("Monitoring", "grey")}


def action_cards(cards):
    """Recommendation cards in two columns. Each card: state, title, text, metrics, note."""
    from html import escape as e
    for i in range(0, len(cards), 2):
        for col, c in zip(st.columns(2), cards[i:i + 2]):
            tag, cls = _STATE[c["state"]]
            mets = "".join(f'<div><div class="av">{e(v)}</div><div class="al">{e(l)}</div></div>' for l, v in c["metrics"])
            note = f'<div class="an">{e(c["note"])}</div>' if c.get("note") else ""
            col.markdown(f'<div class="act {c["state"]}"><span class="tag {cls}">{tag}</span>'
                         f'<div class="at">{e(c["title"])}</div><div class="ax">{e(c["text"])}</div>'
                         f'<div class="ar">{mets}</div>{note}</div>', unsafe_allow_html=True)

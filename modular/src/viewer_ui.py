"""The Data viewer on the Data Checks page: look at the data, tidy it, calculate on it, take it away or use it."""
import pandas as pd
import streamlit as st

from . import charts, state, theme, viewer
from .config import TEAL
from .theme import label


def _reset(ss, source, mode, n, seed):
    base = ss["data"]
    work = base if source == "Full dataset" and len(base) > viewer.EDITABLE_ROWS else \
        (base.copy() if source == "Full dataset" else viewer.draw_sample(base, mode, n, seed))
    ss["vw"].update(df=work, added=[], ver=ss["vw"].get("ver", 0) + 1, xlsx=None)


def render():
    ss = st.session_state
    vw = ss.setdefault("vw", {"open": False, "seed": 0})
    st.subheader("Data viewer")
    st.caption("Look at the rows behind the numbers, sort and tidy them, add your own calculations, and take the result away. "
               "Nothing here changes the dashboard until you choose to use it.")
    if not vw["open"]:
        if st.button("View data", icon=":material/table_view:"):
            vw["open"] = True
            st.rerun()
        return
    if st.button("Close data viewer", icon=":material/close:"):
        vw["open"] = False
        st.rerun()

    base = ss["data"]
    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1, 1])
    source = c1.radio("Show", ["Sample", "Full dataset"], horizontal=True, key="vw_source")
    mode = c2.selectbox("Sample type", viewer.SAMPLE_MODES, key="vw_mode", disabled=source != "Sample")
    n = c3.number_input("Sample rows", 10, 500, 50, 10, key="vw_n", disabled=source != "Sample")
    if c4.button("New random sample", disabled=source != "Sample" or mode != "Random"):
        vw["seed"] += 1
    sig = (ss["version"], source, mode, int(n), vw["seed"])
    if vw.get("sig") != sig or "df" not in vw:
        vw["sig"] = sig
        _reset(ss, source, mode, int(n), vw["seed"])
    work = vw["df"]
    editable = len(work) <= viewer.EDITABLE_ROWS

    with st.expander("Choose columns to show"):
        shown = st.multiselect("Columns to show", list(work.columns), default=list(work.columns), format_func=label,
                               key=f"vw_cols_{vw['ver']}", label_visibility="collapsed")
    if editable:
        st.caption(f"{len(work):,} rows of {len(base):,}. Click a column heading to sort. Change a cell by double-clicking it. "
                   "Tick the box at the left of a row and press the bin icon to delete it. Add a row at the bottom.")
        edited = st.data_editor(work, key=f"vw_ed_{vw['ver']}", num_rows="dynamic", column_order=shown or None, height=420)
    else:
        st.caption(f"{len(work):,} rows. Tables this large are read-only so the page stays fast. You can still sort, filter, "
                   "calculate and summarise below.")
        edited = work
        st.dataframe(work[shown] if shown else work, height=420)
    changed = editable and not edited.equals(work)
    if changed:
        st.caption(f"You have edited this table: {len(edited):,} rows now.")

    t_calc, t_filter, t_sum, t_out = st.tabs(["Calculate", "Keep rows", "Summarise", "Take away or use"])

    with t_calc:
        st.caption("Add a column of your own, for example total GB divided by monthly bill.")
        nums = viewer.numeric_columns(edited)
        a, o, b, nm = st.columns([1.4, .6, 1.4, 1.4])
        ca = a.selectbox("First column", nums, format_func=label, key="vw_ca")
        op = o.selectbox("Operation", list(viewer.OPS), key="vw_op")
        kind = b.radio("Second value", ["Column", "Number"], horizontal=True, key="vw_kind")
        cb = b.selectbox("Column", nums, format_func=label, key="vw_cb", label_visibility="collapsed") if kind == "Column" \
            else b.number_input("Number", value=1.0, key="vw_num", label_visibility="collapsed")
        name = nm.text_input("New column name", key="vw_name", placeholder="gb_per_rand")
        if st.button("Add column", key="vw_add"):
            try:
                vw["df"] = viewer.add_column(edited, name, ca, op, cb)
                vw["added"].append(name.strip())
                vw["ver"] += 1
                st.rerun()
            except ValueError as e:
                st.error(str(e))
        if vw["added"]:
            st.caption("Your columns: " + ", ".join(vw["added"]) + ". They are left out if you use this data in the dashboard.")

    with t_filter:
        st.caption("Remove every row that does not match. Use Start again to get them back.")
        f1, f2, f3 = st.columns([1.4, 1.2, 1.4])
        fc = f1.selectbox("Column", list(edited.columns), format_func=label, key="vw_fc")
        fh = f2.selectbox("Condition", viewer.FILTERS, key="vw_fh")
        fv = f3.text_input("Value", key="vw_fv")
        if st.button("Keep matching rows", key="vw_keep"):
            try:
                out = viewer.keep_rows(edited, fc, fh, fv)
                if out.empty:
                    st.warning("No rows match, so nothing was removed.")
                else:
                    vw["df"] = out
                    vw["ver"] += 1
                    st.rerun()
            except (ValueError, TypeError):
                st.error("That value does not fit the column. Use a number for number columns and a date such as 2026-03-01 for dates.")

    with t_sum:
        st.caption("Totals and averages by group, from the rows above (including your edits).")
        s1, s2, s3 = st.columns(3)
        by = s1.selectbox("Group by", [None] + [c for c in edited.columns if edited[c].nunique() <= 200],
                          format_func=lambda c: "Everything together" if c is None else label(c), key="vw_by")
        val = s2.selectbox("Measure", viewer.numeric_columns(edited), format_func=label, key="vw_val")
        agg = s3.selectbox("Calculation", list(viewer.AGGS), key="vw_agg")
        if val:
            res = viewer.summarise(edited, by, val, agg)
            st.dataframe(res, hide_index=True)
            if by and 1 < len(res) <= 30:
                theme.show(charts.hbar(res.set_index(by).iloc[:, 0].head(15), TEAL, "{:,.2f}"))
            st.download_button("Download this summary (CSV)", viewer.to_csv(res), "summary.csv", "text/csv", key="vw_dl_sum")

    with t_out:
        st.caption("Your edits and calculated columns are included in what you download.")
        d1, d2 = st.columns(2)
        d1.download_button("Download as CSV", viewer.to_csv(edited), "data_view.csv", "text/csv", key="vw_dl_csv")
        if len(edited) <= 200_000:
            if d2.button("Prepare Excel file", key="vw_xl"):
                vw["xlsx"] = viewer.to_excel(edited)
            if vw.get("xlsx"):
                d2.download_button("Download as Excel", vw["xlsx"], "data_view.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="vw_dl_xl")
        else:
            d2.caption("Excel is limited to 200,000 rows. Use CSV.")
        st.divider()
        st.markdown("**Use this data in the dashboard**")
        if source != "Full dataset":
            st.caption("Switch to Full dataset to use your changes. A sample is only part of the data.")
        else:
            st.caption("Your edited data goes through the same Data Checks as an upload. If it is not ready for scoring, "
                       "the dashboard keeps the current data. Columns you added are left out.")
            if st.button("Check and use this data", type="primary", key="vw_apply"):
                buf = viewer.to_parquet_buffer(viewer.for_upload(edited, vw["added"]))
                buf.name, buf.size = "edited_data.parquet", buf.getbuffer().nbytes
                with st.spinner("Checking and scoring your data"):
                    ok = state.load_upload(buf)
                ss["last_upload"] = ("edited_data.parquet", buf.size)
                if not ok:
                    st.session_state["vw_blocked"] = True
                st.rerun()
    if ss.pop("vw_blocked", False):
        st.error("The edited data is not ready for scoring, so the dashboard kept the previous data. See the checks above.")
    if st.button("Start again", key="vw_restart", icon=":material/restart_alt:"):
        _reset(ss, source, mode, int(n), vw["seed"])
        st.rerun()

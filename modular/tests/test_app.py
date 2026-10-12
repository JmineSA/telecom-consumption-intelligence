from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.mark.parametrize("page", ["views/overview.py", "views/forecast.py", "views/revenue.py",
                                  "views/geography.py", "views/insights.py", "views/compare.py", "views/monitoring.py", "views/data_checks.py", "views/about.py"])
def test_page_runs_without_errors(page):
    at = AppTest.from_file(APP, default_timeout=120).run()
    if page != "views/overview.py":
        at = at.switch_page(page).run()
    assert not at.exception, at.exception


def test_full_report_builds_pdf_and_excel():
    at = AppTest.from_file(APP, default_timeout=300).run()
    [b for b in at.button if b.key == "prep_full"][0].click()
    at.run()
    assert not at.exception, at.exception
    _, pdf, xls, _ = at.session_state["report_store"]["full"]
    assert pdf[:4] == b"%PDF" and xls[:2] == b"PK"

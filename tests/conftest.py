import os
import shutil
from pathlib import Path

import pytest

GIT_GIA = Path(__file__).resolve().parent / "chan_host" / "bin" / "git"
HUONG_DAN = ("TỪ CHỐI CHẠY: pytest phải đi qua bộ chặn host (AGENT_RULES.md §13, D61) — chạy trần thì test cũ có thể "
             "push thật vào kho tạm. Lệnh đúng: tests/chan_host/chay.sh -q [đường test]")


def pytest_configure(config):
    """D61: thiếu một dấu của `tests/chan_host/chay.sh` (biến runner, plugin `chan_host`, `git` giả đầu PATH) → thoát 4
    trước khi thu thập test nào."""
    git = shutil.which("git")
    if (os.environ.get("TRAM_CHAN_CHAY_SH") != "1" or not config.pluginmanager.has_plugin("chan_host")
            or git is None or os.path.realpath(git) != str(GIT_GIA)):
        pytest.exit(HUONG_DAN, returncode=4)
    config.addinivalue_line("markers", "g3: kịch bản đo G3, chạy kèm bằng TRAM_TEST_G3=1")
    config._tram_g3_bo_qua = 0


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    if os.environ.get("TRAM_TEST_G3") != "1":
        bo = [item for item in items if item.get_closest_marker("g3") is not None]
        config._tram_g3_bo_qua = len(bo)
        items[:] = [item for item in items if item.get_closest_marker("g3") is None]
        config.hook.pytest_deselected(items=bo)


def pytest_sessionfinish(session):
    if hasattr(session.config, "workeroutput"):
        session.config.workeroutput["tram_g3_bo_qua"] = session.config._tram_g3_bo_qua


@pytest.hookimpl(optionalhook=True)
def pytest_testnodedown(node, error):
    # Mọi worker thu thập cùng bộ test: lấy max, không cộng trùng sáu lần.
    node.config._tram_g3_bo_qua = max(node.config._tram_g3_bo_qua,
                                    getattr(node, "workeroutput", {}).get("tram_g3_bo_qua", 0))


def pytest_terminal_summary(terminalreporter, config):
    terminalreporter.write_line(f"=== bỏ qua {config._tram_g3_bo_qua} test G3 (TRAM_TEST_G3=1 để chạy kèm) ===")


@pytest.fixture(autouse=True)
def tram_home_tam(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_HOME", str(tmp_path / "tram-home"))
    return tmp_path / "tram-home"

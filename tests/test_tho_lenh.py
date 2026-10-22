import io
import json
import subprocess
import threading
import urllib.error
from pathlib import Path

import pytest

from tram.cli import main
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.khach import KhachTram, LoiKhachTram
from tram.tho.kiem_may import DauDo, in_ket_qua, kiem_may

GB = 1024 ** 3


def _ch(tmp_path) -> CauHinhTho:
    (tmp_path / "khe1").mkdir(exist_ok=True)
    return CauHinhTho("B", "http://127.0.0.1:7700", (
        KheCauHinh("claude-1", "claude", None, tmp_path / "khe1", "Claude 1", ("coder",)),
        KheCauHinh("claude-2", "claude", None, tmp_path / "khe-khong-co", "Claude 2", ("qc",))))


def _dd(tmp_path, **kw) -> DauDo:
    kho = tmp_path / "kho"
    (kho / "hr-codex").mkdir(parents=True)
    goc = {"ping": lambda: {"may_id": "B", "khe": [{"khe_id": "B/claude-1", "cau_dao": {"ngat": False}},
                                                    {"khe_id": "B/claude-2", "cau_dao": {"ngat": True,
                                                                                         "toi_luc": "x"}}]},
           "du_an": lambda: ["hr-codex"], "which": lambda c: f"/usr/bin/{c}",
           "chay": lambda a, **k: subprocess.CompletedProcess(a, 0, "2.1.0 (Claude Code)\n" if "--version" in a
                                                              else "sleep 0\n", ""),
           "con_trong": lambda p: 50 * GB, "thu_muc_kho": kho}
    return DauDo(**{**goc, **kw})


def _muc(ds):
    return {m.muc: m.muc_do for m in ds}


def test_kiem_may_xanh_va_cac_muc_cho_cong_luon_do(tmp_path):
    ds = kiem_may(_ch(tmp_path), _dd(tmp_path))
    m = _muc(ds)
    assert m["tram-api"] == m["B/claude-1 CLI"] == m["B/claude-1 cấu hình"] == m["kho hr-codex"] == "xanh"
    assert m["B/claude-2 cấu hình"] == "do" and m["B/claude-2 cầu dao"] == "vang"
    assert m["B/claude-1 đăng nhập"] == m["cách ly"] == m["quyền ghi worktree"] == "do"     # chờ S2, S6
    van_ban, ma = in_ket_qua(ds)
    assert ma == 1 and "[ĐỎ] cách ly: chờ spike S6" in van_ban and "[XANH] tram-api: máy B" in van_ban


def test_kiem_may_bao_do_dung_cho(tmp_path):
    def loi():
        raise LoiKhachTram("tram-api trả 401")
    dd = _dd(tmp_path, ping=loi, which=lambda c: None if c == "claude" else f"/usr/bin/{c}",
             con_trong=lambda p: 3 * GB,
             chay=lambda a, **k: subprocess.CompletedProcess(a, 0, "sleep 10\n", ""))
    (tmp_path / "kho/hr-codex/erp").mkdir()
    (tmp_path / "kho/hr-codex/erp/.env").write_text("DB_PASSWORD=that")
    m = _muc(kiem_may(_ch(tmp_path), dd))
    assert m["tram-api"] == m["B/claude-1 CLI"] == m["B/claude-1 cầu dao"] == m["kho hr-codex"] == "do"
    assert m["máy ngủ"] == m["dung lượng"] == "vang"
    m = _muc(kiem_may(_ch(tmp_path), _dd(tmp_path / "x", du_an=lambda: ["chua-clone"])))
    assert m["kho chua-clone"] == "do"


class _PhanHoi(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_khach_gui_bearer_doc_loi_va_khong_lo_token():
    goi = []

    def mo(yc, timeout):
        goi.append(yc)
        if yc.full_url.endswith("/api/tho/bao"):
            raise urllib.error.HTTPError(yc.full_url, 409, "x", {}, io.BytesIO(b'{"ly_do": "luot-cu"}'))
        return _PhanHoi(json.dumps({"may_id": "B", "khe": [], "du_an": [{"ten": "hr-codex"}]}).encode())

    k = KhachTram("http://127.0.0.1:7700", "bi-mat-123", mo=mo)
    assert k.ping()["may_id"] == "B" and goi[0].get_header("Authorization") == "Bearer bi-mat-123"
    assert k.du_an() == ["hr-codex"] and goi[1].get_header("Authorization") is None
    assert k.goi("POST", "/api/tho/bao", {"x": 1}) == (409, {"ly_do": "luot-cu"})
    assert "bi-mat" not in repr(k)
    with pytest.raises(LoiKhachTram):
        KhachTram("http://127.0.0.1:1", "t", mo=lambda yc, timeout: (_ for _ in ()).throw(OSError("x"))).ping()


def test_cli_tat_bat_khe_va_go_may(tram_home_tam, capsys, monkeypatch):
    from datetime import datetime, timezone
    from tram.phieu.kho import mo_kho_phieu
    from tram.phieu.khe import dang_ky_khe, khe_dang_bat
    from tram.phieu.may import cap_token_may, xac_thuc_may
    kho = mo_kho_phieu()
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "1", "vai_uu_tien": ["qc"]}],
                    luc=datetime.now(timezone.utc))
    tok = cap_token_may(kho, "B", luc=datetime.now(timezone.utc))
    assert main(["tho", "tat-khe", "B/claude-1", "--vi-sao", "để dành"]) == 0 and not khe_dang_bat(kho, "B/claude-1")
    assert main(["tho", "bat-khe", "B/claude-1"]) == 0 and khe_dang_bat(kho, "B/claude-1")
    assert main(["tho", "tat-khe", "B/claude-9"]) == 2
    monkeypatch.setattr("builtins.input", lambda *_: "không")
    assert main(["chu", "go-may", "B"]) == 1 and xac_thuc_may(kho, tok) == "B"
    assert main(["chu", "go-may", "B", "--dong-y"]) == 0 and xac_thuc_may(kho, tok) is None
    assert main(["chu", "go-may", "B", "--dong-y"]) == 2
    assert "thu hồi 0 phiếu" in capsys.readouterr().out


def test_cli_kiem_thieu_tho_yaml_la_do(tram_home_tam, capsys):
    assert main(["tho", "kiem"]) == 1 and "[ĐỎ] tho.yaml" in capsys.readouterr().out


def test_tram_api_bat_va_dung_bo_canh(monkeypatch, tram_home_tam):
    import uvicorn
    monkeypatch.setattr(uvicorn, "run", lambda app, **kw: None)
    assert main(["api"]) == 0
    assert not any(t.name == "tram-canh" and t.is_alive() for t in threading.enumerate())
    assert (Path(tram_home_tam) / "su-kien.db").exists()

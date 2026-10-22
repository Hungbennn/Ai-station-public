"""Ép cửa sổ chay.bat_dau → CLI nhận stdin, không cần tải CPU hay tiến trình OS.

Vòng khe, số lần, sổ phiếu, TheoDoi và API thật; chỉ CLI là bản giả trong luồng.
Không chạy lệnh kiểm ngoài (việc này chỉ kiểm dừng/khởi động lại).
"""
import json
import io
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

import test_kich_ban_3a2 as kb
from tram.chay_cli.giao_dien import KetQuaChay
from tram.tho.bao import doc_khoi


def test_khoi_dong_cli_cham_khong_sinh_lan_thu_ba(tmp_path, monkeypatch):
    dung_that, toi_that = kb.dung_may, kb.chay_toi
    vao_cli, cho_khoi_dong = threading.Event(), threading.Event()
    cac_lan = []

    def dung_may(goc, mp, kich_ban):
        m = dung_that(goc, mp, kich_ban)
        chon = m.t.pt.chon_phieu

        def chon_khong_lenh(*a):
            p = chon(*a)
            return p.model_copy(update={"can_lenh_kiem": False, "lenh_kiem": []}) if p else None

        m.t.pt.chon_phieu = chon_khong_lenh

        def chay(argv, *, cwd, stdin, dung, env, **kw):
            cac_lan.append(stdin.name)
            if len(cac_lan) == 1:
                vao_cli.set()
                # CLI chưa được CPU: nhường quyền cho test quyết định dừng hay cho chạy.
                while not cho_khoi_dong.wait(0.01):
                    if dung.is_set():
                        return KetQuaChay(-15, False, False, False, True)
            # Cùng cách đếm của cli_gia.py: lần bị dừng trước đọc stdin KHÔNG được đếm.
            d = cwd / ".tram"
            n = len(list(d.glob("stdin-*.md"))) + 1
            (d / f"stdin-{n}.md").write_text(stdin.read_text())
            for buoc in json.loads(m.kb.read_text())[str(n)]:
                if "ghi" in buoc:
                    p = cwd / buoc["ghi"][0]
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(buoc["ghi"][1])
                elif "cho_dung" in buoc:
                    assert dung.wait(40), "test chưa gửi lệnh dừng CLI"
                elif "chay" in buoc:
                    dong = {"loai": "xong", "noi_dung": "xong", "commit": None,
                            "ban_giao": doc_khoi(cwd, kb.FILE_BG)}
                    Path(env["TRAM_HANG_DOI"]).write_text(json.dumps(dong) + "\n")
                # `ngu: 30` cũ: cho hết giấc ngủ ngay để tái hiện nhanh, không chờ 30 giây.
            return KetQuaChay(0, True, False, False, dung.is_set())

        m.nc.tao_cli = lambda *a, **kw: SimpleNamespace(chay=chay)
        return m

    def chay_toi(m, dieu_kien, **kw):
        def kiem():
            if len(cac_lan) <= 1:
                if not kb.su_kien(m, "chay.bat_dau"):
                    return False
                assert vao_cli.wait(40), "chưa tới cửa khởi chạy CLI"
                dat = dieu_kien()
                if not dat:
                    cho_khoi_dong.set()
                return dat
            return dieu_kien()
        return toi_that(m, kiem, **kw)

    monkeypatch.setattr(kb, "dung_may", dung_may)
    monkeypatch.setattr(kb, "chay_toi", chay_toi)
    kb.test_tat_tram_tho_chay_roi_khoi_dong_lai_chay_tiep(tmp_path, monkeypatch)
    assert cac_lan == ["goi.md", "goi-2.md"]


def test_cli_gia_cho_lenh_dung_sau_khi_nhan_stdin(tmp_path, monkeypatch):
    import cli_gia

    class DaChoDung(Exception):
        pass

    def cho():
        assert (tmp_path / ".tram/stdin-1.md").read_text() == "gói lần 1"
        assert (tmp_path / "san-sang").is_file()
        raise DaChoDung

    p = tmp_path / "kb.json"
    p.write_text(json.dumps([{"ghi": ["san-sang", "1"]}, {"cho_dung": True},
                             {"ghi": ["khong-duoc-chay-tiep", "1"]}]))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLI_GIA_KICH_BAN", str(p))
    monkeypatch.setattr(cli_gia, "sys", SimpleNamespace(stdin=io.StringIO("gói lần 1"), argv=["cli-gia"]))
    monkeypatch.setattr(cli_gia, "threading", SimpleNamespace(Event=lambda: SimpleNamespace(wait=cho)))
    with pytest.raises(DaChoDung):
        cli_gia.main()
    assert not (tmp_path / "khong-duoc-chay-tiep").exists()


@pytest.mark.parametrize("loi_dieu_kien", [False, True], ids=["het-han", "loi-dieu-kien"])
def test_chay_toi_luon_dung_va_doi_vong_khe(tmp_path, monkeypatch, loi_dieu_kien):
    da_dung = threading.Event()

    def chay(tat):
        tat.wait()
        da_dung.set()

    def dieu_kien():
        if loi_dieu_kien:
            raise ValueError("điều kiện lỗi")
        return False

    monkeypatch.setattr(kb, "VongKhe", lambda *a: SimpleNamespace(chay=chay))
    m = SimpleNamespace(nc=SimpleNamespace(ch=SimpleNamespace(khe=[None])))
    with pytest.raises(ValueError if loi_dieu_kien else AssertionError,
                       match="điều kiện lỗi" if loi_dieu_kien else "chưa đạt điều kiện"):
        kb.chay_toi(m, dieu_kien, giay=0)
    assert da_dung.is_set()

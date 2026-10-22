"""Dựng tram-api với phụ thuộc giả cho test (bd giả, SQLite tạm)."""
import os
from pathlib import Path

from bd_gia import BdGia
from tram.api.app import tao_app
from tram.api.bo_dem import BoDemBeads
from tram.api.phu_thuoc import PhuThuocApi
from tram.cau_hinh.tram import CauHinhTram
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.kho import KhoThaoTac

MAY_B = "may-b.tail.ts.net"
LOGIN = "dai-ca@example.com"
DAI_CA = {"Tailscale-User-Login": LOGIN, "X-Tram": "1", "Origin": f"https://{MAY_B}"}


def tao_pt(tmp_path: Path, bds: dict[str, BdGia], *, thu_muc_tinh: Path | None = None) -> PhuThuocApi:
    db = tmp_path / "sk.db"
    return PhuThuocApi(
        cau_hinh=CauHinhTram(dai_ca_logins=(LOGIN,), ten_may_b=MAY_B),
        cac_du_an=lambda: sorted(bds),
        tao_bd=lambda ten: bds[ten],
        bo_dem=BoDemBeads(lambda ten: bds[ten]),
        mo_kho=lambda: KhoSuKien(db),
        mo_kho_tt=lambda: KhoThaoTac(db),
        thu_muc_tinh=thu_muc_tinh,
    )


def tao_app_gia(tmp_path: Path, bds: dict[str, BdGia], *, co_passkey=True, **kw):
    pt = tao_pt(tmp_path, bds, **kw)
    app = tao_app(pt)
    if co_passkey:
        from passkey_phien_gia import dang_nhap_app
        # Sổ passkey riêng mỗi tiến trình: hai tiến trình tram-api thật dùng chung tmp_path (test hai tiến trình) mà chung
        # sổ thì mã ghép máy của tiến trình này bị tiến trình kia thu hồi → "Mã không hợp lệ hoặc hết hạn" (bs-2bd.1.29).
        dang_nhap_app(app, tmp_path / f"pk-test-{os.getpid()}.db")
    return app, pt

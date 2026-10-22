"""tram-api với kho phiếu tạm, đồng hồ tiêm được và token máy B, C (CHỈ DÙNG TRONG TEST)."""
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone

from api_gia import tao_pt
from asgi_gia import goi
from tram.api.app import tao_app
from tram.phieu.kho import KhoPhieu
from tram.phieu.may import cap_token_may

BAT_DAU = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)
KHE = [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude tài khoản 1", "vai_uu_tien": ["coder"]},
       {"ten": "claude-2", "cli": "claude", "ten_goi_nho": "Claude tài khoản 2", "vai_uu_tien": ["spec", "qc"]}]


@dataclass
class TramGia:
    app: object
    pt: object
    token: dict[str, str]
    gio: list[datetime]

    def toi(self, **kw) -> None:
        self.gio[0] += timedelta(**kw)

    def goi(self, method: str, path: str, may: str | None = "B", json_body=None, headers: dict | None = None):
        h = {"Authorization": f"Bearer {self.token[may]}"} if may else {}
        return goi(self.app, method, path, json_body=json_body, headers={**h, **(headers or {})})

    def kho(self) -> KhoPhieu:
        return self.pt.mo_kho_phieu()


def tao_tram(tmp_path, *, chon=None, token_noi_bo: str | None = None, dang_ky: bool = True) -> TramGia:
    db, gio = tmp_path / "sk.db", [BAT_DAU]
    pt = replace(tao_pt(tmp_path, {}), mo_kho_phieu=lambda: KhoPhieu(db), chon_phieu=chon,
                 doc_token_noi_bo=lambda: token_noi_bo, dong_ho=lambda: gio[0])
    kho = KhoPhieu(db)
    token = {m: cap_token_may(kho, m, luc=BAT_DAU) for m in ("B", "C")}
    kho.close()
    t = TramGia(tao_app(pt), pt, token, gio)
    if dang_ky:
        assert t.goi("POST", "/api/tho/dang-ky", json_body={"may_id": "B", "khe": KHE}).status == 200
        from tram.phieu.khe import bat_tat_khe
        from contextlib import closing
        with closing(t.kho()) as kho:
            with kho.giao_dich():
                for k in KHE:
                    bat_tat_khe(kho, 'B/'+k['ten'], bat=True, vi_sao='fixture đã được chủ duyệt',
                                tac_nhan='dai-ca', luc=BAT_DAU)
    return t

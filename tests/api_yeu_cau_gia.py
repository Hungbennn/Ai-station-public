"""CHỈ DÙNG TRONG TEST (plan 4d 4D-2): tram-api thật trong bộ nhớ + sổ tiếp nhận thật (SQLite tạm) + `bd` giả có đếm
lần đọc/tạo + gián điệp mở sổ. `goi_tho` gửi được header trùng tên. Không mạng, không `bd` thật."""
import asyncio
import json
from pathlib import Path

from api_gia import DAI_CA, MAY_B, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from yeu_cau_gia import MA, BdTep, yc

from tram.yeu_cau.mau import dau_xem
from tram.yeu_cau.so_nhan import SoNhan

TAO, XEM = "/api/feature/yeu-cau", "/api/feature/yeu-cau/xem"


class BdDem(BdTep):
    def tat_ca(self):
        with open(self.thu_muc / "doc.log", "a") as f:
            f.write("1\n")
        return super().tat_ca()

    def so_lan_doc(self) -> int:
        p = self.thu_muc / "doc.log"
        return len(p.read_text().splitlines()) if p.exists() else 0


def mo_app(tmp_path, *, bat_ghi=True, ngu=0.0, su_co=None):
    Path(tmp_path).mkdir(parents=True, exist_ok=True)
    app, pt = tao_app_gia(Path(tmp_path), {"hr-codex": BdGia()})
    bd, mo = BdDem(tmp_path, ngu=ngu, su_co=su_co), []
    pt.bat_ghi = bat_ghi if callable(bat_ghi) else (lambda ten: bat_ghi)
    pt.tao_bd_yeu_cau = lambda ten: bd

    def mo_so():
        mo.append(1)
        return SoNhan(Path(tmp_path) / "so.db")
    pt.mo_so_nhan = mo_so
    return app, pt, bd, mo


def than(**sua):
    y = yc()
    return {"ma_yeu_cau": MA, "du_an": "hr-codex", "tieu_de": y.tieu_de, "uu_tien": 2, "phieu": y.phieu.model_dump(),
            **sua}


def dau(**sua) -> str:
    d = than(**sua)
    return dau_xem(yc(d["ma_yeu_cau"], du_an=d["du_an"], tieu_de=d["tieu_de"], uu_tien=d["uu_tien"],
                      phieu=d["phieu"]))


def tao(app, headers=None, **sua):
    return goi(app, "POST", TAO, json_body={**than(**sua), "dau_xem": dau(**sua)}, headers=DAI_CA if headers is None
               else headers)


def goi_tho(app, duong, than_yc, headers: list[tuple[str, str]], host="127.0.0.1:7700"):
    """Như `asgi_gia.goi` nhưng header là danh sách — gửi được hai `Tailscale-User-Login`."""
    body = json.dumps(than_yc, ensure_ascii=False).encode()
    hdr = [("host", host), ("content-type", "application/json"), *[(k.lower(), v) for k, v in headers]]
    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "POST", "scheme": "http",
             "path": duong, "raw_path": duong.encode(), "query_string": b"", "root_path": "",
             "headers": [(k.encode("latin-1"), v.encode("latin-1")) for k, v in hdr],
             "client": ("127.0.0.1", 50000), "server": ("127.0.0.1", 7700)}
    nhan, gui = [{"type": "http.request", "body": body, "more_body": False}], []

    async def receive():
        return nhan.pop(0) if nhan else {"type": "http.disconnect"}

    async def send(m):
        gui.append(m)
    asyncio.run(app(scope, receive, send))
    return next(m for m in gui if m["type"] == "http.response.start")["status"]


def chay_api(tmp, cho, hang):
    """Một tiến trình tram-api dùng chung sổ và bd giả, chờ hiệu lệnh có hạn."""
    app, _, _, _ = mo_app(Path(tmp), ngu=0.2)
    cho.wait(timeout=10)
    hang.put(tao(app).status)

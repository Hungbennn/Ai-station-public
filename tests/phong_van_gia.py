"""CHỈ DÙNG TRONG TEST (plan 4d 4D-3b): nạp script máy A; `MoTram` thay hàm mở URL của urllib bằng tram-api THẬT trong
bộ nhớ (sổ SQLite tạm, `bd` giả), gắn danh tính như `tailscale serve` — bỏ header danh tính do client tự gửi."""
import io
import json
import re
import sys
import urllib.error

from api_gia import LOGIN, MAY_B
from api_yeu_cau_gia import mo_app
from asgi_gia import goi
from test_phieu_yeu_cau import MAU

from tram.duong_dan import goc_repo

THU_MUC = goc_repo() / "ky-nang" / "phong-van-yeu-cau"
GOC = "https://" + MAY_B
sys.path.insert(0, str(THU_MUC))
import khach  # noqa: E402
import nhap  # noqa: E402
import yeu_cau  # noqa: E402


class PhanHoi(io.BytesIO):
    def __init__(self, status, body):
        super().__init__(body)
        self.status = status


class MoTram:
    def __init__(self, tmp_path, login=LOGIN, **kw):
        self.app, self.pt, self.bd, self.mo = mo_app(tmp_path / "b", **kw)
        self.login, self.goi = login, []

    def __call__(self, req, timeout):
        self.goi.append((req, timeout))
        hdr = {k: v for k, v in req.header_items() if k.lower() != "tailscale-user-login"}
        hdr["Host"] = MAY_B
        if self.login:
            hdr["Tailscale-User-Login"] = self.login
        r = goi(self.app, req.get_method(), req.full_url[len(GOC):], json_body=json.loads(req.data), headers=hdr)
        if r.status >= 400:
            raise urllib.error.HTTPError(req.full_url, r.status, "loi", {}, io.BytesIO(r.body))
        return PhanHoi(r.status, r.body)


def nhap_day_du(tmp_path, **sua):
    """Nháp do `moi` sinh rồi được phiên Claude điền tại chỗ (giữ mã)."""
    p = nhap.moi(tmp_path / "nhap", du_an="hr-codex")
    d = json.loads(p.read_text(encoding="utf-8"))
    d.update({"tieu_de": "Hoa hồng tạm tính", "phieu": dict(MAU)}, **sua)
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return p


def chay(capsys, mo, *argv):
    ma = yeu_cau.main([*argv, "--tram", GOC] if argv[0] != "moi" else list(argv), mo)
    return ma, capsys.readouterr().out


def ma_xem(out):
    return re.search(r"mã xem ([0-9a-f]{16})", out).group(1)

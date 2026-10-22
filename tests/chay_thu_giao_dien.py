"""Chạy tram-api với dữ liệu GIẢ (`tests/du_lieu_giao_dien.py`) để kiểm tay giao diện lát 2f — CHỈ DÙNG KHI KIỂM.

`uv run python tests/chay_thu_giao_dien.py [cong] [--dai-ca]` (mặc định 7798) sau `npm run build`. Mọi thứ trong thư mục
tạm (TRAM_HOME, su-kien.db, TRAM_REPO/du-an, HOME giả có plist); bd, launchctl, security, memory service đều giả — không
mạng, không ~/.tram, Keychain, launchctl, beads thật. `--dai-ca`: lớp ASGI CHỈ ĐỂ KIỂM TAY, gắn `Tailscale-User-Login`
của Đại ca giả + đổi Origin cục bộ thành máy B giả (xem Cài đặt, Ký ức, nút ghi). Không phải test pytest.
TM-4 `--kenh-that`: CHỈ ĐỂ XEM trang Tự động như khi cửa ghi là `unix-socket` (nút mở); ghi qua cổng TCP này bị 403.
TM-4 `--gia-deploy`: CHỈ ĐỂ XEM — khoá/hàng giả TM-2/TM-3 THAY khoá/hàng thật của dự án giả (dùng khi TM-3 đã ghép);
không có cờ thì khoá/hàng thật thắng, giả chỉ lấp chỗ trạm chưa có."""
import os
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path
from types import SimpleNamespace

TAM = Path(tempfile.mkdtemp(prefix="tram-giao-dien-"))
os.environ["TRAM_HOME"] = str(TAM / "tram-home")
os.environ["TRAM_REPO"] = str(TAM / "repo")                   # nap_du_an đọc TRAM_REPO/du-an/<ten>.yaml

import uvicorn  # noqa: E402
import yaml  # noqa: E402

from api_gia import LOGIN, MAY_B, tao_pt  # noqa: E402
from bd_gia import BdGia  # noqa: E402
from bead_gia import bead  # noqa: E402
from du_lieu_giao_dien import (GIA, LUC, cac_bead, gieo, gieo_tu_dong, iso, ky_uc,  # noqa: E402
                               them_gia, them_phe_duyet_gia)
from tram.api import tuyen_doc, tuyen_tu_dong  # noqa: E402
from tram.api.app import tao_app  # noqa: E402
from tram.cau_hinh.du_an import nap_du_an  # noqa: E402
from tram.phieu.kho import KhoPhieu  # noqa: E402
from tram.suy import he_thong, san_sang  # noqa: E402

# tên → (đường dẫn dưới ~, gitnexus, lệnh cho phép, hàng rào {loại: từ khoá}) — mockup CAU_HINH_DU_AN
DU_AN = {"hr-codex": ("Developer/hr-codex", "hr-codex", ["uv run pytest -q", "uv run ruff check ."],
                      {"tien": ["hoàn tiền", "thuế", "hoá đơn"], "quyen": ["phân quyền", "vai trò"]}),
         "tram": ("Developer/Ben Station", "ben-station", ["uv run pytest -q", "npm --prefix frontend test"],
                  {"quyen": ["CSP", "danh tính", "token"]}),
         "ke-toan": ("Developer/ke-toan", None, ["uv run pytest -q"], {"tien": ["sổ cái", "bút toán"]})}
SAN_SANG = [("bs-g28.9", "Tailscale máy B đã đăng nhập", "closed", ()),          # mockup SAN_SANG (bead repo trạm)
            ("bs-8eh.17", "Tailscale máy A (Đại ca cài, D6)", "open", ()),
            ("bs-urj.4", "Kickstart vn.tram.nho sau ghép 1b-4 T4 (D11)", "open", ("bs-8eh.1",)),
            ("bs-8eh.1", "1b-2 T10 — /nho, mã Đại ca, tram-noi-bo-token", "open", ()),
            ("bs-hpc.5", "1b-1 memory: dịch vụ, Keychain, M1/M2, recall", "closed", ())]
DANG_CHAY = ("vn.tram.api", "vn.tram.quet", "vn.tram.nho", "vn.tram.bao-tin")      # vn.tram.sao-luu: chưa cài


def chay_gia(argv: list[str]) -> tuple[int, str]:
    """Bộ chạy giả cho `DocHeThong`: launchctl (4 dịch vụ chạy), security (thiếu `tram-noi-bo-token`)."""
    if argv[0] == "launchctl":
        return (0, "state = running\n") if argv[-1].rsplit("/", 1)[-1] in DANG_CHAY else (113, "")
    return (44, "") if argv[-1] == "tram-noi-bo-token" else (0, "")


@dataclass
class NhoGia:
    """Memory service giả (như `KhachGia` của tests/test_api_nho.py) — `/danh-sach`, `/ghi`, `/xoa` trong bộ nhớ."""
    ds: list[dict]

    def goi(self, duong: str, than: dict, *, thoi_gian_cho: float) -> dict:
        bay = iso(LUC)
        if duong == "/ghi":
            k = {"id": f"m-tay{len(self.ds):020x}", "noi_dung": than["noi_dung"], "pham_vi": than["pham_vi"],
                 "nhan": than.get("nhan") or [], "quan_trong": 0.8, "nguon": [{"loai": "dai_ca_ghi"}],
                 "nguon_dai_ca": True, "tao_luc": bay, "hieu_luc_tu": bay, "dung_luc": None, "so_lan_dung": 0}
            self.ds.insert(0, k)
            return {"id": k["id"], "pham_vi": k["pham_vi"], "xoa": [], "lap_lai": False}
        if duong == "/xoa":
            self.ds = [k for k in self.ds if k["id"] != than["id"]]
            return {"da_xoa": True}
        so = Counter(k["pham_vi"] for k in self.ds)
        cho = Counter(k["pham_vi"] for k in self.ds if k["hieu_luc_tu"] > bay)
        ds = [k for k in self.ds if (not than.get("pham_vi") or k["pham_vi"] == than["pham_vi"])
              and (not than.get("cho_hieu_luc") or k["hieu_luc_tu"] > bay)]
        return {"ky_uc": ds, "tong": len(ds),
                "pham_vi": [{"pham_vi": p, "so": n, "so_cho": cho[p]} for p, n in sorted(so.items())]}


class DaiCaGia:
    """CHỈ ĐỂ KIỂM TAY: mọi yêu cầu mang danh tính Đại ca giả; Origin cục bộ → `https://<máy B giả>`."""

    def __init__(self, app, cong: int):
        self.app, self.cuc_bo = app, {f"http://127.0.0.1:{cong}".encode(), f"http://localhost:{cong}".encode()}

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            h = [(k, f"https://{MAY_B}".encode() if k == b"origin" and v in self.cuc_bo else v)
                 for k, v in scope["headers"] if k != b"tailscale-user-login"]
            scope = {**scope, "headers": [*h, (b"tailscale-user-login", LOGIN.encode())]}
        await self.app(scope, receive, send)


def moi_truong() -> None:
    """`du-an/*.yaml` trong TRAM_REPO tạm; plist giả trong HOME giả; thay bộ đọc launchd/Keychain và bảng sẵn sàng."""
    (TAM / "repo" / "du-an").mkdir(parents=True)
    for ten, (dd, gn, lenh, rao) in DU_AN.items():
        raw = {"ten": ten, "duong_dan": str(Path.home() / dd), "gitnexus_repo": gn, "lenh_cho_phep": lenh,
               "hang_rao": {k: {"tu_khoa": v} for k, v in rao.items()},
               "moi_truong_kiem": {"file": str(TAM / "env"), "dich": ".env.testing"} if ten == "hr-codex" else None}
        (TAM / "repo" / "du-an" / f"{ten}.yaml").write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    (la := TAM / "home" / "Library" / "LaunchAgents").mkdir(parents=True)
    for nhan in DANG_CHAY:
        (la / f"{nhan}.plist").write_text("<plist/>\n", encoding="utf-8")
    he_thong._CHUNG = he_thong.DocHeThong(chay=chay_gia, home=TAM / "home", uid=501)
    ds = [bead(i, title=t, status=st, labels=["san-sang"], chan_boi=cb) for i, t, st, cb in SAN_SANG]
    san_sang.CHUNG = san_sang.BangSanSang(doc_bead=lambda: ds, which=lambda lenh: f"/gia/bin/{lenh}")
    tu_dong_gia("--gia-deploy" in sys.argv)


def tu_dong_gia(ep: bool) -> None:
    """TM-4: ghép khoá giả TM-2/TM-3 vào GET tự động và dòng "sẵn sàng deploy" ở Phê duyệt (khoá/hàng thật thắng,
    `ep` thì giả thay thật — `them_gia`, `them_phe_duyet_gia`)."""
    ct, tt, gom = tuyen_tu_dong.chi_tiet_du_an, tuyen_tu_dong.tom_tat_du_an, tuyen_doc.gom_phe_duyet
    tuyen_tu_dong.chi_tiet_du_an = lambda kho, ten, **kw: them_gia(ten, ct(kho, ten, **kw), ep=ep)
    tuyen_tu_dong.tom_tat_du_an = lambda kho, ten, **kw: them_gia(ten, tt(kho, ten, **kw), tom_tat=True, ep=ep)
    tuyen_doc.gom_phe_duyet = lambda *a, **kw: them_phe_duyet_gia(gom(*a, **kw), ep=ep)


def main() -> None:
    cong = int(next((a for a in sys.argv[1:] if not a.startswith("--")), 7798))
    dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
    moi_truong()
    kho = KhoPhieu(TAM / "sk.db")
    g3 = gieo(kho)
    gieo_tu_dong(kho)
    kho.close()
    pt = tao_pt(TAM, {t: BdGia(ds) for t, ds in cac_bead(g3).items()}, thu_muc_tinh=dist)
    ch = replace(pt.cau_hinh, telegram=replace(pt.cau_hinh.telegram, chat_id="1", gio_yen_lang="23:00–07:00"))
    pt = replace(pt, mo_kho_phieu=lambda: KhoPhieu(TAM / "sk.db"), dong_ho=lambda: LUC, nho=NhoGia(ky_uc()),
                 usage=replace(pt.usage, gia=GIA), cau_hinh=ch,
                 bo_giao=SimpleNamespace(cac_du_an=lambda: [nap_du_an(t) for t in DU_AN], kho_git=lambda da: None),
                 bat_ghi=lambda ten: ten != "ke-toan")                  # TM-4: ke-toan "chỉ quét thử"
    app = tao_app(pt, cong=cong)
    if "--kenh-that" in sys.argv:
        app.state.kenh_ghi = "unix-socket"
    print(f"Dữ liệu giả ở {TAM} — mở http://127.0.0.1:{cong}/ (Ctrl+C để dừng)", flush=True)
    uvicorn.run(DaiCaGia(app, cong) if "--dai-ca" in sys.argv else app, host="127.0.0.1", port=cong,
                server_header=False, log_level="warning")


if __name__ == "__main__":
    main()

"""Chạy tram-api với dữ liệu GIẢ để kiểm tay trang Văn phòng trên trình duyệt (plan 2c Task 8) — CHỈ DÙNG KHI KIỂM.

`uv run python tests/chay_thu_van_phong.py [cong]` (mặc định 7799) sau `cd frontend && npm run build`. Mọi dữ liệu nằm
trong thư mục tạm (TRAM_HOME, su-kien.db); `bd` là `BdGia`; không gọi mạng, không đụng ~/.tram hay beads thật.
Không phải test pytest (tên file không bắt đầu bằng `test_`)."""
import os
import sys
import tempfile
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

TAM = Path(tempfile.mkdtemp(prefix="tram-van-phong-"))
os.environ["TRAM_HOME"] = str(TAM / "tram-home")

import uvicorn  # noqa: E402

from api_gia import tao_pt  # noqa: E402
from bd_gia import BdGia  # noqa: E402
from bead_gia import bead  # noqa: E402
from kho_phieu_gia import dat_phieu  # noqa: E402
from tram.api.app import tao_app  # noqa: E402
from tram.phieu.cau_dao import ngat_cau_dao  # noqa: E402
from tram.phieu.khe import bat_tat_khe, dang_ky_khe  # noqa: E402
from tram.phieu.kho import KhoPhieu  # noqa: E402
from tram.phieu.nhip_tim import ghi_nhip  # noqa: E402

LUC = datetime.now(timezone.utc).replace(microsecond=0)
KHE = [("claude-1", "claude"), ("claude-2", "claude"), ("codex-1", "codex"), ("claude-3", "claude"),
       ("codex-2", "codex"), ("claude-4", "claude")]


def gieo(db: Path) -> None:
    kho = KhoPhieu(db)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": t, "cli": c, "ten_goi_nho": t, "vai_uu_tien": ["coder"]} for t, c in KHE], luc=LUC)
        for t, _ in KHE:
            if t != "codex-2":                                            # codex-2: mất kết nối
                ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
        bat_tat_khe(kho, "B/claude-3", bat=False, vi_sao="để dành", tac_nhan="dai-ca", luc=LUC)
        ngat_cau_dao(kho, "B/claude-4", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=2), luc=LUC)
    dat_phieu(kho, "B/claude-1", luc=LUC, bead_id="hr-1", tieu_de="Sửa cắt UTF-8 tóm tắt hoàn tiền")
    p = dat_phieu(kho, "B/codex-1", luc=LUC, bead_id="hr-3", tieu_de="Chọn cách tính thuế", buoc="qc")
    with kho.giao_dich():
        kho.ghi_su_kien("hr-codex", "bao.can_hoi", {"giao_id": p.giao_id}, luc=LUC, bead_id="hr-3")
    kho.close()


def main() -> None:
    cong = int(sys.argv[1]) if len(sys.argv) > 1 else 7799
    dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
    bds = {"hr-codex": BdGia([bead("hr-1", title="Sửa cắt UTF-8", labels=["cot:ai-lam"]),
                              bead("hr-2", title="Xem lại hoá đơn", labels=["cot:cho-review"]),
                              bead("hr-3", title="Chọn cách tính thuế", labels=["cot:can-chot"])]),
           "tram": BdGia([])}
    gieo(TAM / "sk.db")
    pt = replace(tao_pt(TAM, bds, thu_muc_tinh=dist), mo_kho_phieu=lambda: KhoPhieu(TAM / "sk.db"),
                 dong_ho=lambda: LUC)
    print(f"Dữ liệu giả ở {TAM} — mở http://127.0.0.1:{cong}/#/van-phong (Ctrl+C để dừng)")
    uvicorn.run(tao_app(pt, cong=cong), host="127.0.0.1", port=cong, server_header=False, log_level="warning")


if __name__ == "__main__":
    main()

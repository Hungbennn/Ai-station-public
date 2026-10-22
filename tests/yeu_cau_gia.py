"""CHỈ DÙNG TRONG TEST (plan 4d 4D-1): `bd` giả lưu trong file JSONL — nhiều tiến trình dùng chung được, đếm MỌI lần
gọi create (kể cả lần chết giữa chừng), gây sự cố đúng một lần ở điểm chọn. Không chạy `bd` thật."""
import fcntl
import json
import os
import time
from pathlib import Path

from test_phieu_yeu_cau import MAU
from tram.beads.bd import LoiBd
from tram.beads.mo_hinh import Bead
from tram.giao_viec.phieu_yeu_cau import PhieuYeuCau
from tram.yeu_cau.dich_vu import tiep_nhan
from tram.yeu_cau.mau import YeuCau, digest, dong_dau
from tram.yeu_cau.so_nhan import SoNhan

MA = "yc-" + "0123456789abcdef" * 2
LOGIN = "dai-ca@example.com"
BI_MAT = "BI-MAT-KHONG-DUOC-LO"


def yc(ma=MA, **sua) -> YeuCau:
    d = {"du_an": "hr-codex", "tieu_de": "Hoa hồng tạm tính", "uu_tien": 2, "phieu": dict(MAU), **sua}
    return YeuCau(ma, d["du_an"], d["tieu_de"], d["uu_tien"], PhieuYeuCau.model_validate(d["phieu"]))


class BdTep:
    """`su_co = (điểm, cách)`: điểm ∈ doc | truoc_ghi | sau_ghi; cách ∈ chet (os._exit) | loi (LoiBd) | la (lỗi lạ)."""

    def __init__(self, thu_muc, *, ngu=0.0, su_co=None, repo="/kho/b/hr-codex"):
        self.thu_muc, self.ngu, self.su_co, self.repo = Path(thu_muc), ngu, su_co, Path(repo)
        self.tep, self.dem = self.thu_muc / "beads.jsonl", self.thu_muc / "tao.log"

    def _su_co(self, diem):
        co = self.thu_muc / "su-co.da"
        if self.su_co is None or self.su_co[0] != diem or co.exists():
            return
        co.write_text(diem)
        if self.su_co[1] == "chet":
            os._exit(9)
        raise (LoiBd if self.su_co[1] == "loi" else RuntimeError)(f"bd giả lỗi -d {BI_MAT}")

    def tat_ca(self):
        time.sleep(self.ngu)
        self._su_co("doc")
        dong = self.tep.read_text(encoding="utf-8").splitlines() if self.tep.exists() else []
        return [Bead.tu_json(json.loads(x)) for x in dong]

    def tat_ca_yeu_cau(self):
        return self.tat_ca()

    def them(self, mo_ta, loai="feature", nhan=(), tieu_de="x", uu_tien=None):
        with open(self.tep, "a+", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0)
            moi = f"hr-f{len(f.read().splitlines()) + 1}"
            f.write(json.dumps({"id": moi, "title": tieu_de, "description": mo_ta, "issue_type": loai,
                                "labels": list(nhan), "priority": uu_tien, "status": "open",
                                "updated_at": "2026-10-16T00:00:00Z"}, ensure_ascii=False) + "\n")
        return moi

    def tao(self, tieu_de, *, loai, mo_ta, nhan=(), uu_tien=None, nghiem_thu=None, cha=None):
        with open(self.dem, "a", encoding="utf-8") as f:
            f.write(f"{os.getpid()}\n")
        time.sleep(self.ngu)
        self._su_co("truoc_ghi")
        moi = self.them(mo_ta, loai, nhan, tieu_de, uu_tien)
        self._su_co("sau_ghi")
        return moi

    def so_lan_tao(self) -> int:
        return len(self.dem.read_text().splitlines()) if self.dem.exists() else 0

    def them_dau(self, ma=MA, loai="feature"):
        return self.them(dong_dau(ma) + "\nphiếu", loai)


class DongHo:
    """Đồng hồ giả (giây epoch) cho hạn giữ chỗ."""

    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def giu_cho(so, han, chu="chet"):
    """Như một lần gửi trước đã giữ chỗ cho MA rồi chết (chưa đọc bd, chưa create)."""
    so.nhan(MA, du_an="hr-codex", digest=digest(yc()), nguoi_gui=LOGIN, chu=chu, han=han)


def chay_mot(db, thu_muc, cho, hang, su_co=None, ngu=0.2):
    """Một tiến trình tram-api giả: chờ hiệu lệnh có hạn rồi tiếp nhận yêu cầu."""
    so, bd = SoNhan(Path(db)), BdTep(thu_muc, ngu=ngu, su_co=su_co)
    try:
        if cho is not None:
            cho.wait(timeout=10)
        hang.put(tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN).trang_thai)
    finally:
        so.close()

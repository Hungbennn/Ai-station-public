"""Cài lại hồ sơ Seatbelt + manifest kiểm bản hiện hành (v2) từ chính manifest đã cài; in kế hoạch, chờ dong-y.
Chỉ thay hai tệp root đã có trong sổ R2 — không đụng user, sudoers hay launchd như `cai-dat-tho`."""
import json
from pathlib import Path

from tram.chu import dinh_danh
from tram.chu.cai_dat_kiem import tep_root
from tram.chu.so_cai_tho import SoCai, doi_soat
from tram.chu.tai_nguyen import kiem_truoc, tao
from tram.duong_dan import tram_home
from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, manifest_ho_so


def lap(cu: dict, soan: Path) -> list:
    if set(cu) < {"cong", "goc", "nha_quan_ly", "tram_home"}:
        raise ValueError("Manifest đã cài thiếu khoá — cài bằng `tram chu cai-dat-tho`")
    hs, mf = manifest_ho_so(tram_home_tram=Path(cu["tram_home"]), nha_quan_ly=Path(cu["nha_quan_ly"]),
                            goc=Path(cu["goc"]), cong=[int(c) for c in cu["cong"]])
    soan.mkdir(parents=True, exist_ok=True)
    (soan / HO_SO_KIEM.name).write_bytes(hs)
    (soan / MANIFEST_KIEM.name).write_bytes(mf)
    # V2-5: hồ sơ trước, manifest sau — dừng giữa chừng thì manifest cũ không khớp hồ sơ mới → cổng đóng.
    return [tep_root(soan / HO_SO_KIEM.name, HO_SO_KIEM, hs, "0644"),
            tep_root(soan / MANIFEST_KIEM.name, MANIFEST_KIEM, mf, "0644")]


def main() -> int:
    so, obs = SoCai(), dinh_danh.quan_sat_that
    try:
        with so.giu():
            ds = lap(json.loads(MANIFEST_KIEM.read_bytes()), tram_home() / "cai-dat-tho" / "ho-so-soan")
            for tn, v in zip(ds, kiem_truoc(so, ds, quan_sat=obs)):
                print(f"[{v}] {tn.kieu} {tn.ten}: {tn.mo_ta()}")
            if input("Gõ dong-y để cài hồ sơ kiểm bản hiện hành: ").strip() != "dong-y":
                return 1
            doi_soat(so, obs, dinh_danh.khop)
            for tn in ds:
                print(tao(so, tn, quan_sat=obs), tn.ten)
    except (OSError, ValueError, RuntimeError) as e:
        print(f"Không cài hồ sơ: {type(e).__name__}: {e}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

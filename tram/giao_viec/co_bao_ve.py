"""Bộ bảo vệ ben-station §2; cấu hình chỉ được cộng thêm."""
from tram.kiem.duong_dan_cam import DUONG_DAN_CAM_TRAM, khop_mau

BEN = (
    "tram/api/bao_mat.py", "tram/api/kenh_ghi.py", "tram/llm/claude.py", "tram/bao_tin/telegram.py",
    "tram/tho/token_may.py", "tram/chu/cap_ma.py", "tram/nho/ma_dai_ca.py", "tram/nho/bi_mat.py",
    "tram/kiem/**", "tram/tho/sandbox.py", "tram/tho/principal*.py", "tram/giao_viec/kiem_lai.py",
    "tram/giao_viec/kiem_principal.py", "tram/su_kien/ket_noi.py", "tram/phieu/luoc_do.py", "tram/nho/bang.py",
    "tram/cong_bo/**", "tram/giao_viec/pr.py", "tram/giao_viec/pr_merge.py", "tram/chu/launchd.py",
    "tram/chu/cai_dat*.py", "tram/tho/launchd_tho.py", "tram/chu/go_cai_dat_tho.py",
    "tram/cau_hinh/giao_viec.py", "tram/cau_hinh/bat_ghi.py", "du-an/**", "tram/han_muc/luat.py",
    "tram/cau_hinh/tram.py", "tram-kiem", "docs/AGENT_RULES.md",
)
NHAN = {"co-do", "rui-ro:bao-mat", "rui-ro:he-thong", "rui-ro:kien-truc", "rui-ro:du-lieu"}


def nguy_hiem(files, labels, them=(), *, ben=False):
    mau = (*DUONG_DAN_CAM_TRAM, *them, *(BEN if ben else ()))
    return bool(NHAN.intersection(labels)) or any(khop_mau(p, m) for p in files for m in mau)

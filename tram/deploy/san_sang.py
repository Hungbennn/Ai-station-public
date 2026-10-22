"""Probe chỉ đọc khi bật; các quyền thật do Đại ca chuẩn bị ngoài trạm."""
from tram.deploy.duong import DuongDeploy
from tram.thao_tac.loi import KhongHopLe


def can_duong(ten, cd):
    try:
        r = DuongDeploy(ten, cd).goi("chuan_bi", "kiem-cai-dat", "", "")
    except (OSError, ValueError, KeyError):
        r = None
    if not r or not all(r[k] for k in ("dat", "da_dung", "san_sang")):
        raise KhongHopLe("Cần đường deploy riêng và bản quay lại đã kiểm")

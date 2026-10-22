"""Chốt bền cho kết quả chưa rõ; Tiếp tục thông thường không xoá chốt."""
from tram.deploy.trang_thai import bat_dau_cua, ma


def chua_doi_soat(ds):
    da = {ma(s) for s in ds if s.loai == "deploy.doi_soat"}
    return [s for s in ds if s.loai == "deploy.xong" and s.du_lieu.get("ket_qua") in ("khong_ro", "lui_hong")
            and ma(s) not in da]


def ban_can_doi_soat(ds):
    x = chua_doi_soat(ds)
    bd = bat_dau_cua(ds, x[-1]) if x else None
    return None if bd is None else {"ma": ma(bd), "commit": bd.du_lieu["commit"],
                                    "truoc": bd.du_lieu["commit_truoc"]}

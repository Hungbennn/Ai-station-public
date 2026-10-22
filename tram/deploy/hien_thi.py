"""Phần hiển thị của tự deploy cho trang Tự động và trang Phê duyệt (design D-5, D101; dạng khoá theo hợp đồng của
plan TM-4) — tính lúc đọc từ sự kiện: hàng "sẵn sàng deploy", "đang deploy", lịch sử (mới → cũ). `chi_tiet` do máy
chủ dựng, CHỈ mã thoát, số giây, quá hạn, số PR, commit ngắn — KHÔNG lệnh, đầu ra lệnh (spec "Không lọt bí mật")."""
from tram.deploy.trang_thai import (SK, bat_dau_cua, chuoi_dang_do, commit_truoc, la_tu_merge, ma, merge_chua_deploy,
                                    moc_ban, yeu_cau_cho)

LOAI_LICH_SU = ("tu_merge", "san_sang", "deploy_dat", "deploy_lui", "lui_hong", "khong_ro", "tu_tat", "tam_dung", "huy")
AI = ("dai_ca", "dai_ca_bam", "tu_deploy", "tram")
LOAI_XONG = {"dat": "deploy_dat", "da_lui": "deploy_lui", "lui_hong": "lui_hong", "khong_ro": "khong_ro"}
TEN_BUOC = {"deploy": "deploy", "kiem_song": "kiểm còn sống", "lui": "lùi",
            "kiem_song_sau_lui": "kiểm còn sống sau lùi"}
CAU_TRAM = {("tu_tat", "hong-3-lan"): "hỏng 3 lần liên tiếp — chờ Đại ca bật lại",
            ("tu_tat", "lui-hong"): "lùi hỏng — trạm tắt tự deploy",
            ("tam_dung", "lui-hong"): "trạm tạm dừng dự án sau khi lùi hỏng",
            ("tam_dung", "khong-ro"): "trạm tạm dừng dự án: deploy không rõ kết quả — cần Đại ca kiểm"}


def dang_deploy(ds: list[SK]) -> dict | None:
    if dd := chuoi_dang_do(ds):
        d = dd[-1].du_lieu
        return {"trang_thai": "chay", "commit": d.get("commit"), "nguon": d.get("nguon"), "luc": dd[-1].luc}
    if yc := yeu_cau_cho(ds):
        return {"trang_thai": "cho", "commit": yc.du_lieu.get("commit"), "nguon": "dai_ca", "luc": yc.luc}
    return None


def san_sang(ds: list[SK]) -> dict | None:
    """Hàng "sẵn sàng deploy" (D96, D97 luật 5): MỘT hàng cho commit mới nhất trạm đã ghi nhận sau lần `dat`, gồm mọi
    merge chưa lên trước nó. None khi không có gì chờ hay đang deploy. Người gọi xét thêm "đủ 3 lệnh"."""
    moc = moc_ban(ds)
    gom = [s for s in merge_chua_deploy(ds) if moc and s.id in moc[-1].du_lieu.get("bao_gom", [])]
    if not gom or dang_deploy(ds) is not None:
        return None
    return {"commit": moc[-1].du_lieu["commit"], "so_merge": len(gom), "bead_ids": [s.bead_id for s in gom],
            "luc": moc[-1].luc, "commit_dang_chay": commit_truoc(ds) or None}


def _buoc(x: SK) -> str:
    d = x.du_lieu
    ket = "quá hạn" if d.get("het_gio") else f"mã thoát {d.get('ma_thoat')}"
    return f"{TEN_BUOC.get(d.get('buoc'), d.get('buoc'))}: {ket} · {d.get('giay')} giây"


def _dong(ds: list[SK], s: SK) -> dict | None:
    d, tram = s.du_lieu, s.tac_nhan.startswith("tram/")
    if s.loai == "pr.da_merge" and la_tu_merge(ds, s):           # gộp tay: đã nằm trong "gồm N việc"
        return {"loai": "tu_merge", "bead_id": s.bead_id, "commit": d.get("merge_commit"),
                "chi_tiet": f"PR #{d['pr']}" if "pr" in d else "", "ai": "tram"}
    if s.loai == "deploy.huy":
        from tram.tu_dong.khoa import NHAN_LY_DO
        nhan = {**NHAN_LY_DO, "ban_moi_hon": "Có bản mới hơn — bấm Deploy lại trên bản mới"}
        return {"loai": "huy", "bead_id": None, "commit": d.get("commit"), "ai": "dai_ca_bam",
                "chi_tiet": nhan.get(d.get("ly_do"), "Không thể deploy — tải lại")}
    if s.loai == "deploy.san_sang":
        return {"loai": "san_sang", "bead_id": None, "commit": d.get("commit"),
                "chi_tiet": f"gồm {d.get('so_merge')} việc đã merge", "ai": "tram"}
    if s.loai == "deploy.xong" and d.get("ket_qua") in LOAI_XONG:
        bd = bat_dau_cua(ds, s)
        bd = bd.du_lieu if bd else {}
        buoc = " → ".join(_buoc(x) for x in ds if x.loai == "deploy.lenh"
                           and ma(x) == ma(s) and not x.du_lieu.get("bat_dau"))
        if d["ket_qua"] in ("da_lui", "lui_hong") and bd.get("commit_truoc"):
            buoc += f" (bản trước {bd['commit_truoc'][:7]})"
        return {"loai": LOAI_XONG[d["ket_qua"]], "bead_id": None, "commit": bd.get("commit"), "chi_tiet": buoc,
                "ai": "dai_ca_bam" if bd.get("nguon") == "dai_ca" else "tu_deploy"}
    loai = {"tu_dong.cai_dat": "tu_tat", "tu_dong.tam_dung": "tam_dung"}.get(s.loai)
    if loai and tram and (loai, d.get("ly_do")) in CAU_TRAM:
        return {"loai": loai, "bead_id": None, "commit": None, "chi_tiet": CAU_TRAM[(loai, d["ly_do"])], "ai": "tram"}
    return None


def lich_su(ds: list[SK], gioi_han: int = 20) -> list[dict]:
    """`loai` ∈ `LOAI_LICH_SU`, `ai` ∈ `AI`. D127: nút Deploy bị huỷ có loại `huy`."""
    ra = ({"luc": s.luc, **x} for s in reversed(ds) if (x := _dong(ds, s)) is not None)
    return [x for _, x in zip(range(gioi_han), ra)]

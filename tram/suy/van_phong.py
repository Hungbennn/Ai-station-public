"""Phòng của Văn phòng 3D (spec 2 §5.5) và sức khoẻ trạm cho tủ máy ở Phòng máy chủ — suy lúc đọc (Q12).

Sức khoẻ (plan 2c G5): `do` khi estop bật, không đọc được beads của một dự án, hoặc có mục "Hệ cần xem" khác cầu dao
khe; `vang` khi cầu dao khe ngắt hoặc khe `loi` / `mat_ket_noi`; còn lại `xanh`. Chỉ trả câu cố định + tên dự án /
mã khe — không trả nội dung lỗi (có thể chứa đường dẫn, argv)."""
PHONG_CO_DINH = (("dieu-phoi", "dieu_phoi", "Điều phối"), ("giam-doc", "giam_doc", "Phòng giám đốc"),
                 ("may-chu", "may_chu", "Phòng máy chủ"), ("ca-phe", "ca_phe", "Góc cà phê"))
TEN_HE = {"quet.loi": "lỗi quét beads", "cham_cot.bo_qua": "bộ chấm bỏ qua bead lỗi liên tiếp",
          "nho.loi_llm": "memory lỗi LLM", "nho.loi_embedder": "memory lỗi embedder"}
TEN_KHE = {"loi": "lỗi lần chạy cuối", "mat_ket_noi": "mất kết nối"}
GIU_TOI_DA = 10


def suc_khoe(*, estop_bat: bool, muc: list[dict], loi_doc: dict[str, str], nhan_vat: list[dict]) -> dict:
    do, vang = [], []
    if estop_bat:
        do.append("Estop đang bật")
    do += [f"Không đọc được beads của dự án {t}" for t in sorted(loi_doc)]
    for m in muc:
        if m["loai"] != "he":
            continue
        sk = m["chi_tiet"].get("su_kien")
        if sk == "khe.cau_dao_ngat":
            vang.append(f"Cầu dao khe {m['chi_tiet'].get('khe_id')} đang ngắt")
        else:
            do.append(f"{m['du_an']}: {TEN_HE.get(sk, sk)}" + (f" ({m['bead_id']})" if m.get("bead_id") else ""))
    vang += [f"Khe {x['khe_id']}: {TEN_KHE[x['trang_thai']]}" for x in nhan_vat if x["trang_thai"] in TEN_KHE]
    mau = "do" if do else "vang" if vang else "xanh"
    tu = ([{"mau": "do", "ly_do": x} for x in do] + [{"mau": "vang", "ly_do": x} for x in vang])[:GIU_TOI_DA]
    return {"mau": mau, "ly_do": (do + vang)[:GIU_TOI_DA], "muc": tu}       # 2f T6: tủ thứ i lấy màu muc[i]


def cac_phong(cac_du_an: list[str], *, so_cho: int, suc_khoe: dict, dieu_phoi: dict | None = None) -> list[dict]:
    """Bốn phòng cố định rồi mỗi dự án đã `them` một phòng. Điều phối: `dieu_phoi` = `{sang, nhip_cuoi}` suy từ
    nhịp hook máy A (`tram/suy/dieu_phoi.py`, plan 2e); không truyền → `sang: None` ("chưa có tín hiệu", 2c G4)."""
    them = {"dieu-phoi": dieu_phoi or {"sang": None}, "giam-doc": {"so_cho": so_cho}, "may-chu": {"suc_khoe": suc_khoe}}
    ra = [{"ma": ma, "loai": loai, "ten": ten, **them.get(ma, {})} for ma, loai, ten in PHONG_CO_DINH]
    return ra + [{"ma": f"du-an:{t}", "loai": "du_an", "ten": t, "du_an": t} for t in cac_du_an]

"""Dữ liệu GIẢ cho máy chủ kiểm giao diện lát 2f (`tests/chay_thu_giao_dien.py`) — CHỈ DÙNG KHI KIỂM TAY, không phải
test pytest. Bám mockup `docs/mockup/2026-10-15-giao-dien/du-lieu.js`, `du-lieu-ky-uc-usage.js`; giờ lùi từ `LUC`.
TM-4: trang Tự động theo mockup `docs/mockup/2026-10-18-tu-merge-tu-deploy/du-lieu.js` (`gieo_tu_dong`, `them_gia`)."""
import random
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from bead_gia import bead, notes_ban_giao
from kho_phieu_gia import dat_phieu
from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.khe import bat_tat_khe, dang_ky_khe
from tram.phieu.kho import chuoi_gio as iso
from tram.phieu.nhip_tim import ghi_nhip
from tram.suy import phe_duyet
from tram.tu_dong.luu import doi_cai_dat

LUC = datetime.now(timezone.utc).replace(microsecond=0)
P, NGAY = timedelta(minutes=1), timedelta(days=1)
C2, C4, URL = "2" * 40, "4" * 40, "https://github.com/dai-ca/hr-codex/pull/"     # commit_ban_giao hr-2, hr-4
# khe, cli, tên gợi nhớ, vai, hạn mức ĐÃ dùng (5h %, phút tới reset 5h, tuần %) — mockup ghi phần "còn"
KHE = [("claude-1", "claude", "claude-chinh", ["coder"], (38, 83, 19)),
       ("claude-2", "claude", "claude-phu", ["coder", "qc"], (6, 178, 30)),
       ("codex-1", "codex", "codex-chinh", ["qc"], (52, 38, 43)),
       ("claude-3", "claude", "claude-de-danh", ["coder"], (0, None, 8)),
       ("codex-2", "codex", "codex-phu", ["coder"], None),                     # không nhịp tim → mất kết nối
       ("claude-4", "claude", "claude-thu", ["spec"], (100, 115, 66))]
SONNET, CODEX, HAIKU = "claude-sonnet-4-5", "gpt-5-codex", "claude-haiku-4-5"   # "o3-cu": mô hình thiếu giá
GIA = {SONNET: {"vao": 3, "ra": 15, "cache_doc": 0.3, "cache_ghi": 3.75},
       CODEX: {"vao": 1.25, "ra": 10, "cache_doc": 0.125, "cache_ghi": 0},
       HAIKU: {"vao": 1, "ra": 5, "cache_doc": 0.1, "cache_ghi": 1.25}}
CAU_HOI = "Tính thuế trên giá trước hay sau chiết khấu? Làm tròn theo từng dòng hay theo tổng hoá đơn?"
KY_UC = [  # (phạm vi, nhãn, nội dung, quan trọng, loại nguồn, bead nguồn, số ngày trước — âm: chờ hiệu lực, lần dùng)
    ("/du-an/hr-codex/nghiep-vu", "mau-in", "Đổi template hoá đơn thì chạy test mẫu in.", .55, "agent", "hr-2", 0, 0),
    ("/du-an/hr-codex/cach-lam", "ruff", "Chạy `ruff check .` trước `uv run pytest`.", .5, "agent", "hr-2", 0, 0),
    ("/vai/coder", "lenh", "Trước khi báo xong, chạy đủ lệnh được phép theo thứ tự.", .55, "thang_cap", None, -7, 0),
    ("/du-an/hr-codex/nghiep-vu", "hoa-don", "Hoá đơn làm tròn đến đồng ở tổng cuối.", .8, "da_chot", "hr-2", 1, 1),
    ("/du-an/tram/cach-lam", "csp", "Route mới trong tram/api đi qua GiuaAnToan.", .5, "agent", "bs-1", 1, 1),
    ("/du-an/hr-codex/nghiep-vu", "ngay", "Phiếu lương hiện ngày dạng dd/mm/yyyy.", .8, "da_chot", "hr-5", 2, 3),
    ("/chung", "chu", "Chữ hiện cho người dùng viết tiếng Việt có dấu.", .8, "dai_ca_ghi", None, 4, 14),
    ("/vai/qc", "nghiem-thu", "QC đối chiếu từng tiêu chí nghiệm thu với diff.", .65, "thang_cap", None, 12, 6)]


def ky_uc() -> list[dict]:
    return [{"id": f"m-{i:024x}", "noi_dung": nd, "pham_vi": pv, "nhan": [nh], "quan_trong": qt,
             "nguon": [{"loai": lo, "du_an": "tram" if "tram" in pv else "hr-codex", **({"bead_id": b} if b else {})}],
             "nguon_dai_ca": lo in ("da_chot", "dai_ca_ghi"), "tao_luc": iso(LUC - max(n, 0) * NGAY - i * 60 * P),
             "hieu_luc_tu": iso(LUC - n * NGAY - i * 60 * P), "dung_luc": iso(LUC - i * 30 * P) if d else None,
             "so_lan_dung": d} for i, (pv, nh, nd, qt, lo, b, n, d) in enumerate(KY_UC)]


def cac_bead(g3: str) -> dict[str, list]:
    esc = f"ly_do: agent-can-hoi\nbead_goc: hr-3\ngiao_id: {g3}\n\n{CAU_HOI}"          # mẫu 4a-1
    return {"hr-codex": [
        bead("hr-1", title="Sửa cắt UTF-8 tóm tắt hoàn tiền", issue_type="bug", priority=1, labels=["cot:ai-lam"],
             status="in_progress", assignee="tram/giao-viec", acceptance_criteria="- Cắt theo ký tự, không theo byte"),
        bead("hr-3", title="Chọn cách tính thuế", priority=2, labels=["cot:can-chot"]),
        bead("hr-2", title="Xem lại hoá đơn", priority=2, labels=["cot:cho-review"],
             notes=notes_ban_giao(nhanh="tram/hr-2", commit=C2, pr=URL + "12")),
        bead("hr-4", title="Kiểm định dạng mã số thuế", issue_type="feature", priority=3, labels=["cot:cho-review"],
             notes=notes_ban_giao(nhanh="tram/hr-4", commit=C4, pr=URL + "11")),
        bead("hr-5", title="Sửa định dạng ngày trên phiếu lương", status="closed", closed_at=iso(LUC - 95 * P)),
        bead("hr-6", title="Hỏi: cách tính thuế cho hr-3", priority=1, issue_type="decision",
             labels=["tram:escalation"], description=esc),
        bead("hr-7", title="Thêm bộ lọc phòng ban cho báo cáo lương", priority=3)],             # chưa chấm
        "tram": [bead("bs-1", title="Đèn điều phối theo nhịp hook", labels=["cot:ai-lam"], priority=2)],
        "ke-toan": [bead("kt-1", title="Đối chiếu sổ cái tháng 9", priority=2)]}


def _usage_cu(kho, r: random.Random) -> None:
    """20 ngày `chay.xong` (khe) + `cham_cot.ket_qua` (cham-cot) có token cho trang Usage (tram/usage/su_kien.py)."""
    for n in range(20, 0, -1):
        for khe, mh in (("claude-1", SONNET), ("claude-2", SONNET), ("codex-1", CODEX), ("claude-3", SONNET),
                        ("claude-4", "o3-cu" if n > 15 else SONNET), *[(None, HAIKU)] * 3):
            for _ in range(r.randint(0, 2) if khe else 1):
                v = r.randint(110_000, 230_000) if khe else r.randint(30_000, 90_000)
                dl = {"khe_id": f"B/{khe}", "luot": 1, "ket_thuc": "xong", "token_cache_doc": v * 3} if khe else {}
                kho.ghi_su_kien(r.choice(["hr-codex", "tram", "ke-toan"]), "chay.xong" if khe else "cham_cot.ket_qua",
                                dl, luc=LUC - n * NGAY, token_vao=v, token_ra=v // 9, mo_hinh=mh)


def gieo(kho) -> str:
    """Khe + nhịp tim + phiếu + sự kiện (cũ → mới, đúng thứ tự id). Trả `giao_id` phiếu QC của codex-1 (hr-3)."""
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": t, "cli": c, "ten_goi_nho": g, "vai_uu_tien": v} for t, c, g, v, _ in KHE],
                    luc=LUC - 30 * NGAY)
        _usage_cu(kho, random.Random(20261015))
    g1 = dat_phieu(kho, "B/claude-1", luc=LUC, bead_id="hr-1", tieu_de="Sửa cắt UTF-8 tóm tắt hoàn tiền").giao_id
    g3 = dat_phieu(kho, "B/codex-1", luc=LUC, bead_id="hr-3", tieu_de="Chọn cách tính thuế", buoc="qc").giao_id
    hr, he, k1, tok = "hr-codex", "_tram", {"khe_id": "B/claude-1"}, {"token_vao": 520_000, "token_ra": 61_000}
    su_kien = [  # (phút trước LUC, dự án, loại, bead, dữ liệu[, cột riêng]) — cũ → mới
        (100, "tram", "quet.loi", None, {"loi": "bd timeout"}), (95, hr, "bead.dong", "hr-5", {}),
        (90, hr, "bead.vao_cot_3", "hr-4", {"commit_ban_giao": C4}),
        (85, hr, "pr.mo", "hr-4", {"loai": "bead", "pr": 11, "url": URL + "11", "commit": C4}),
        (80, hr, "pr.da_merge", "hr-4", {"pr": 11, "commit": C4}), (70, hr, "qc.ket_qua", "hr-2", {"ket_luan": "dat"}),
        (69, hr, "bead.vao_cot_3", "hr-2", {"commit_ban_giao": C2}),
        (68, hr, "pr.mo", "hr-2", {"loai": "bead", "pr": 12, "url": URL + "12", "commit": C2}),
        *[(60, hr, "nho.ghi", "hr-2", {"id": f"m-{i:024x}", "pham_vi": KY_UC[i][0]}) for i in (0, 1)],
        (55, hr, "pr.khong_xac_minh", "hr-2", {"pr": 12, "commit": C2, "ly_do": "khong-phai-merge-commit"}),
        (50, he, "khe.tat", None, {}), (48, hr, "nho.loi_embedder", "hr-1", {"su_kien_id": 4051}),
        (45, hr, "giao.nhan", "hr-3", {"giao_id": g3, "khe_id": "B/codex-1", "buoc": "qc"}),
        (44, hr, "nho.phuc_hoi", "hr-1", {"loai": "embedder"}),
        (40, hr, "cham_cot.ket_qua", "hr-1", {"cot": "ai-lam", "ly_do": "Lỗi rõ, có test tái hiện."}),
        (39, hr, "cham_cot.ket_qua", "hr-3", {"cot": "can-chot", "ly_do": "Hai cách tính hợp lệ.",
                                              "cau_hoi": CAU_HOI.split("? ")}, {"token_vao": 41_000, "mo_hinh": HAIKU}),
        (38, hr, "giao.nhan", "hr-1", {"giao_id": g1, **k1, "buoc": "code"}), (30, he, "khe.cau_dao_ngat", None, {}),
        (28, hr, "escalation.tao", "hr-6", {"escalation_id": "hr-6", "bead_goc": "hr-3", "giao_id": g3,
                                            "ly_do": "agent-can-hoi"}),
        (28, hr, "bao.can_hoi", "hr-3", {"giao_id": g3, "loai_hoi": "can_quyet_dinh"}, {"tac_nhan": "tho/B/codex-1"}),
        (25, hr, "chay.bat_dau", "hr-1", {**k1, "luot": 1}),
        *[(20, hr, "chay.xong", b, {"khe_id": f"B/{k}", "luot": 1, "ket_thuc": kt}, {**tok, "mo_hinh": m})
          for k, b, m, kt in (("claude-1", "hr-1", SONNET, "loi"), ("codex-1", "hr-3", CODEX, "xong"),
                              ("claude-2", "hr-2", SONNET, "xong"), ("claude-4", None, SONNET, "xong"))],
        (10, hr, "chay.bat_dau", "hr-1", {**k1, "luot": 2}),
        *[(3, d, "quet.xong", None, {"da_cham": n}) for d, n in ((hr, 4), ("tram", 1), ("ke-toan", 1))],
        (1, he, "dieu_phoi.nhip", None, {"su_kien": "Stop", "phien": "0" * 16}, {"tac_nhan": "dai-ca/may-a"})]
    with kho.giao_dich():
        for phut, du_an, loai, b, dl, *kw in su_kien:
            luc = LUC - phut * P
            if loai == "khe.tat":
                bat_tat_khe(kho, "B/claude-3", bat=False, vi_sao="để dành", tac_nhan="dai-ca", luc=luc)
            elif loai == "khe.cau_dao_ngat":
                ngat_cau_dao(kho, "B/claude-4", ly_do="het-han-muc", toi_luc=LUC + 115 * P, luc=luc)
            else:
                kho.ghi_su_kien(du_an, loai, dl, luc=luc, bead_id=b, **(kw[0] if kw else {}))
        for t, *_, hm in (k for k in KHE if k[4]):                              # nhịp tim kèm hạn mức 5h / tuần
            cs = [CuaSo(loai=ten, trang_thai="biet", phan_tram=x, doc_luc=iso(LUC), reset_luc=r and iso(LUC + r * P))
                  for ten, x, r in (("5h", hm[0], hm[1]), ("tuan", hm[2], 4 * 24 * 60))]
            ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh",
                     han_muc=HanMuc(khe_id=f"B/{t}", cua_so=cs, nguon="stream"))
    return g3


# ---- TM-4: trang Tự động (mockup 2026-10-18). "tram" đóng vai repo-nhap; "ke-toan" chỉ quét thử ----
LENH_TRAM = {"lenh_deploy": "/Users/Shared/tram-deploy/tram/deploy.sh",
             "lenh_kiem_song": "/Users/Shared/tram-deploy/tram/kiem-song.sh",
             "lenh_lui": "/Users/Shared/tram-deploy/tram/lui.sh"}


def gieo_tu_dong(kho) -> None:
    """Cài đặt THẬT qua hàm TM-1: Đại ca khai lệnh deploy + lùi, rồi lệnh kiểm còn sống, rồi bật tự merge."""
    for doi in ({"lenh_deploy": LENH_TRAM["lenh_deploy"], "lenh_lui": LENH_TRAM["lenh_lui"]},
                {"lenh_kiem_song": LENH_TRAM["lenh_kiem_song"]}, {"tu_merge": True}):
        doi_cai_dat(kho.db, "tram", lambda c, d=doi: replace(c, **d), tac_nhan="dai-ca/dashboard")


C_MOI, C_9B, C_77, C_5D = "a41c07e" + "1" * 33, "9be2d40" + "2" * 33, "77f0a19" + "3" * 33, "5d3e8b2" + "4" * 33
RONG = {"cho_dai_ca": [], "san_sang": None, "dang_deploy": None, "lich_su": [], "dem_hong": 0}
# Khoá TM-2/TM-3 hứa thêm vào GET /api/du-an/<ten>/tu-dong — GIẢ tới khi hai lát đó ghép (khoá thật thắng, `them_gia`).
TU_DONG_GIA = {"tram": {
    "cho_dai_ca": [  # dạng TM-2 (`tram/suy/tu_merge.cho_dai_ca`; mã/nhãn/mức như `tu_merge_xet.NHAN`, `MUC`)
        {"bead_id": "bs-17", "tieu_de": "Đổi chữ nút Lưu", "luc": iso(LUC - 3 * P),
         "ly_do": [{"ma": "ci_dang_chay", "nhan": "CI đang chạy — xét lại vòng sau", "muc": "tat"}]},
        {"bead_id": "bs-14", "tieu_de": "Sửa định dạng ngày ở trang danh sách", "luc": iso(LUC - 9 * P),
         "ly_do": [{"ma": "ci_do", "nhan": "CI chưa xanh", "muc": "can_nguoi"}]},
        {"bead_id": "bs-16", "tieu_de": "Thêm cột ghi chú cho bảng khách", "luc": iso(LUC - 14 * P),
         "ly_do": [{"ma": "schema_duong_dan", "nhan": "Cấu trúc DB — luôn chờ Đại ca", "muc": "loi"}]},
        {"bead_id": "bs-15", "tieu_de": "Làm tròn tổng tiền hoá đơn", "luc": iso(LUC - 31 * P),
         "ly_do": [{"ma": "hang_rao_tien", "nhan": "Chạm hàng rào: tiền/giá", "muc": "can_nguoi"},
                   {"ma": "hang_rao_co_do", "nhan": "Cờ đỏ", "muc": "can_nguoi"}]}],
    "san_sang": {"commit": C_MOI, "so_merge": 2, "bead_ids": ["bs-11", "bs-12"], "luc": iso(LUC - 22 * P),
                 "commit_dang_chay": C_5D},
    "dang_deploy": None, "dem_hong": 1,
    "lich_su": [  # dạng TM-3 (`tram/deploy/hien_thi.lich_su`): chi_tiet chỉ mã thoát, giây, số PR, commit ngắn
        {"luc": iso(LUC - 22 * P), "loai": "san_sang", "bead_id": None, "commit": C_MOI,
         "chi_tiet": "gồm 2 việc đã merge", "ai": "tram"},
        {"luc": iso(LUC - 22 * P), "loai": "tu_merge", "bead_id": "bs-12", "commit": C_MOI,
         "chi_tiet": "PR #31", "ai": "tram"},
        {"luc": iso(LUC - 127 * P), "loai": "tu_merge", "bead_id": "bs-11", "commit": C_9B,
         "chi_tiet": "PR #30", "ai": "tram"},
        {"luc": iso(LUC - 200 * P), "loai": "huy", "bead_id": None, "commit": C_9B,
         "chi_tiet": "Estop đang bật", "ai": "dai_ca_bam"},
        {"luc": iso(LUC - 344 * P), "loai": "deploy_lui", "bead_id": None, "commit": C_77,
         "chi_tiet": "deploy: mã thoát 0 · 51 giây → kiểm còn sống: mã thoát 22 · 34 giây → lùi: mã thoát 0 · 40 giây"
                     " → kiểm còn sống sau lùi: mã thoát 0 · 2 giây (bản trước 5d3e8b2)", "ai": "dai_ca_bam"},
        {"luc": iso(LUC - 654 * P), "loai": "deploy_dat", "bead_id": None, "commit": C_5D,
         "chi_tiet": "deploy: mã thoát 0 · 48 giây → kiểm còn sống: mã thoát 0 · 3 giây", "ai": "dai_ca_bam"}]}}


def them_gia(ten: str, that: dict, *, tom_tat: bool = False, ep: bool = False) -> dict:
    """Ghép khoá giả TM-2/TM-3 vào phản hồi thật. Mặc định khoá thật (khi đã có) thắng; `ep` (cờ `--gia-deploy`, CHỈ ĐỂ
    XEM): khoá giả thay khoá thật của dự án có trong `TU_DONG_GIA`. `tom_tat`: phần tử GET /api/tu-dong."""
    gia = TU_DONG_GIA.get(ten, RONG)
    if tom_tat:
        gia = {"san_sang": gia["san_sang"] is not None, "dem_hong": gia["dem_hong"]}
    return {**that, **gia} if ep and ten in TU_DONG_GIA else {**gia, **that}


def them_phe_duyet_gia(that: list[dict], *, ep: bool = False) -> list[dict]:
    """Dòng "sẵn sàng deploy" GIẢ ở GET /api/phe-duyet (D101; dạng TM-3: chi_tiet = san_sang). Không nối hàng giả khi đã
    có hàng thật (Codex vòng 1, mục Nhỏ): mặc định chỉ thêm khi trạm chưa có TM-3 (`THU_TU` chưa có loại này) và dự án
    chưa có hàng thật; `ep` (CHỈ ĐỂ XEM): bỏ hàng thật của dự án giả rồi thêm hàng giả — không bao giờ trùng."""
    gia = [{"loai": "san-sang-deploy", "du_an": ten, "bead_id": None, "tieu_de": "", "uu_tien": None,
            "updated_at": v["san_sang"]["luc"], "chi_tiet": dict(v["san_sang"])}
           for ten, v in TU_DONG_GIA.items() if v["san_sang"]]
    if ep:
        return [m for m in that if m["loai"] != "san-sang-deploy" or m["du_an"] not in TU_DONG_GIA] + gia
    if "san-sang-deploy" in phe_duyet.THU_TU:          # TM-3 đã ghép: trạng thái thật quyết, không thêm hàng giả
        return that
    co_that = {m["du_an"] for m in that if m["loai"] == "san-sang-deploy"}
    return that + [m for m in gia if m["du_an"] not in co_that]

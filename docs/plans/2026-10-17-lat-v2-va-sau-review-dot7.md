# Lát V2 — sau review đợt 7 — Implementation Plan

> **For agentic workers:** Khi được giao triển khai, dùng `ai-skills:executing-plans` để thực hiện từng task với checkpoint. Đây là plan docs-only; không phải quyền chạy OS hay lịch. Không tự dispatch worker trong phiên review này.

**Goal:** Đóng các lỗ quan sát/lifecycle/đối soát xác định trong REVIEW-CODEX đợt 7 trước các cổng liên quan.
**Architecture:** Giữ D45–D53; tách inventory bảo mật khỏi danh sách giao việc, strict adapter khỏi parser Beads tương thích cũ, probe evidence khỏi suy luận vắng marker. Cleanup phải có owner và hạn; không thay proof OS bằng polling hay mock.
**Tech Stack:** Python hiện có, pytest, SQLite; macOS OS proof ở G3/G4/G5 riêng. Không dependency mới.
**Spec:** `docs/specs/2026-10-13-phan-3-may-tho-han-muc.md` §7.2/7.3/7.6/8.1; `docs/specs/2026-10-13-phan-4-giao-viec.md` §6.2/7.1; quyết định D45–D53; `docs/handovers/2026-10-16-thiet-ke-3c-boundary.md`.

## Global Constraints

- Chỉ tài liệu được áp trong ZIP review. Mọi code/diff dưới đây là **đề xuất**, chưa chạy RED/GREEN, chưa ghép source.
- Không root runtime; chỉ cơ chế user cho S6; không mạng/IPC dùng chung cho kiểm lại; cổng đóng chờ Đại ca mở.
- HR bat_ghi=false, giao_viec.bat=false. Không nới auth/allowlist, không xóa sổ yêu cầu để tạo lại, không sửa quyết định/mockup.
- Khi triển khai phải dùng checkout cô lập, kiểm AGENTS/CLAUDE/HEAD và test safety trước. Fake runner không được lọt sudo/cron/at/launchctl/Keychain/API; process tests chỉ process tự sinh của user test.
- Lệnh `uv run pytest ...` ở đây chỉ là lệnh cho coding agent sau khi có môi trường test được phép; reviewer **không chạy**. Không commit/push/merge/đóng bead từ gói này.
- Các diff độc lập lấy neo snapshot đợt 7. Tích hợp theo thứ tự task; khi một file được sửa trước, áp hunk theo nội dung, không áp mù line number. Phải kiểm diff và tests tích hợp.

## Trạng thái task và phụ thuộc

| Task | Finding | Đầu ra | Gate |
|---|---|---|---|
| V2-0 | C01, .15 | RED tái dùng PGID + thiết kế ownership còn cần review; chưa có patch an toàn hoàn chỉnh | G5/G7 và primitive trong G4 |
| V2-1 | C02, .19 | Cleanup khi KeyboardInterrupt/exception, test giả; SIGTERM riêng | G4 |
| V2-2 | Q01 | Strict JSON adapter trước create, regression qua Bd thật + runner giả | G6 |
| V2-3 | Q02 | Inventory env đầy đủ, lỗi cấu hình đóng quan sát | G4 |
| V2-4 | Q03 | Probe protocol rõ từng nguồn; đủ proof IPC/Mach/XPC | G4 |
| V2-5 | Q04 | Attestation profile đầy đủ từ cấu hình/bản cài tin cậy | G4 |
| V2-6 | .14/.16/.17/.18 | Các task lifecycle/caller còn mở, bắt buộc hoàn thiện thiết kế được chỉ định trước code | G4/G5/G7 tùy caller |
| V2-7 | Q06 + phủ lỗi HTTP | Cleanup test process + sentinel body | G2/G6 |
| V2-8 | Q05/N01 | Runbook/ledger đã sửa trong gói, reviewer sau đối chiếu | G3–G7 |

V2-2/3 có thể làm độc lập về file nhưng không mặc định giao subagent. V2-0 → V2-6 trước nghiệm thu lifecycle; V2-1 không đóng C02 một mình. Mỗi task giữ cổng đóng nếu acceptance chưa đủ. Task cần thiết kế còn mở được ghi rõ, **không giao code từ mô tả thiếu**, không lấy một helper mẫu làm bản vá trọn hệ thống.

## V2-0 — Identity tiến trình và phạm vi thu hồi (thiết kế còn chặn)

**Files:** `tram/kiem/cay_tien_trinh.py`, `tram/kiem/vong_doi.py`, `tram/tho/mo_coi.py`; test mới `tests/test_vong_doi_tai_su_dung.py`. Interface hiện tại `TienTrinh(pid, ppid, pgid, uid, ruid)` thiếu incarnation. `kill(pgid,sig)` không mang proof ownership.

- [ ] RED: thêm test sau. Fake snapshots/kill, không process hay signal thật. Chạy `uv run pytest tests/test_vong_doi_tai_su_dung.py -q`; hiện thất bại vì gửi nhóm 5000.

```python
from test_vong_doi import PopenGia, SUDO
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.vong_doi import Nhom


def test_nhom_tai_su_dung_khong_duoc_kill():
    gui = []
    cu = [SUDO, TienTrinh(5000, 4242, 5000, 502, 502)]
    moi = [SUDO, TienTrinh(5000, 1, 5000, 502, 502)]
    anh = iter([cu, moi])
    n = Nhom(PopenGia(), kill=lambda g, s: gui.append(g),
             chup=lambda: next(anh, moi))
    n.cay()
    assert n.thu_hoi(cho_term=0, cho_cuoi=0, han_gui=1) is False
    assert 5000 not in gui
```

- [ ] Viết thiết kế **trước GREEN**: phân biệt nhóm cũ thật còn thành viên mồ côi và nhóm cùng số mới; fake trên cũng có thể biểu diễn reparent hợp lệ, nên thiếu thông tin hiện tại phải trả “không chứng minh được”, không đoán. Không chỉ chặn ppid=1 vì bỏ cháu hợp lệ. Thêm định danh sinh tiến trình ở adapter OS và proof tồn tại của thành viên đã quan sát, plus revalidate trước signal. Phải phân tích check→signal/PID reuse còn lại, không tuyên bố timestamp làm thao tác nguyên tử.
- [ ] Bổ sung mô hình event/ownership khả thi trên macOS đang dùng để không bỏ fast fork+setsid; nếu chỉ polling thì ghi chính xác giới hạn, giữ trả chưa xác nhận và gate. Riêng UID tram-kiem có thể thu hồi toàn UID vì dành riêng, nhưng không áp bừa kill -1 lên worker đang có việc khác.
- [ ] Test snapshot có cùng UID nhưng birth khác; PGID đổi; ps lỗi; root đã gặt; root chưa gặt; nhóm của manager; nhóm 0/1; mồ côi hợp lệ; fork/reparent trước ảnh đầu; legacy pid receipt không birth. Assert **zero wrong signal**, không chỉ assert function returns False. Legacy receipt phải giữ để đối soát, không xóa rồi báo sạch.
- [ ] GREEN chỉ sau review thiết kế và đầy đủ code/tests mới. Run `uv run pytest tests/test_cay_tien_trinh.py tests/test_vong_doi.py tests/test_vong_doi_ps.py tests/test_vong_doi_tai_su_dung.py -q`, rồi focused callers quota/CLI/harness. G3 phải có evidence kernel/version về identity provider; không thực thi provider OS trong review.

**Vì sao chưa có implementation patch:** snapshot không có nguồn birth identity hoặc cơ chế ownership nguyên tử đã đo. Một bản vá số PGID/timestamp giả sẽ hạ yêu cầu “không gửi ra ngoài cây”. Việc giữ cổng và task thiết kế là có chủ đích, không đánh dấu finding đã sửa.

## V2-1 — Cleanup khi ngắt harness (bs-863.19)

**Files:** sửa `tram/kiem/han_tong.py`; thêm `tests/test_han_tong_ngat.py`. Interface giữ nguyên; KeyboardInterrupt được ném lại **sau** thu hồi và don; còn dấu khi bất kỳ cleanup nào không xác nhận. `don` phải được gọi cả khi thu_hoi ném.

- [ ] Thêm test RED dưới đây; `uv run pytest tests/test_han_tong_ngat.py -q`. Hiện goi rỗng sau Ctrl-C, nên fail.

```python
import pytest
from tram.kiem.han_tong import chay_han_tong


@pytest.mark.parametrize("sach", [True, False])
@pytest.mark.parametrize("loi", [KeyboardInterrupt, RuntimeError])
def test_ngat_van_thu_hoi_roi_don(tmp_path, sach, loi):
    goi = []
    dau = tmp_path / "dau"
    class N:
        def cho(self, han):
            raise loi("khong-in-noi-dung")
        def thu_hoi(self):
            goi.append("thu")
            return sach
    def don():
        goi.append("don")
        return True
    with pytest.raises(loi):
        chay_han_tong(["gia"], han=1, kill=lambda *a: None, dau=dau,
                      don=don, khoi=lambda *a, **kw: N())
    assert goi == ["thu", "don"]
    assert dau.exists() is (not sach)


def test_thu_hoi_nem_van_don_va_giu_dau(tmp_path):
    goi = []
    class N:
        def cho(self, han):
            return 0
        def thu_hoi(self):
            raise RuntimeError("loi-thu-hoi")
    with pytest.raises(RuntimeError):
        chay_han_tong(["gia"], han=1, kill=lambda *a: None,
                      dau=tmp_path / "dau", don=lambda: goi.append(1) or True,
                      khoi=lambda *a, **kw: N())
    assert goi == [1] and (tmp_path / "dau").exists()
```

- [ ] Áp hunk sau, không thay semantics mã thoát bình thường/timeout. Đây không giải quyết child vô hình của V2-0.

```diff
--- a/tram/kiem/han_tong.py
+++ b/tram/kiem/han_tong.py
@@ -53,11 +53,16 @@
         n = khoi(argv, kill=kill, stdin=subprocess.DEVNULL, **kw)
     except OSError:
         n = None
-    ma = n.cho(han) if n else None
-    sach = n.thu_hoi() if n else True
-    xong = _don(don) and sach
-    if xong:
-        dau.unlink()
+    ma, sach, xong = None, False, False
+    try:
+        ma = n.cho(han) if n else None
+    finally:
+        try:
+            sach = n.thu_hoi() if n else True
+        finally:
+            xong = _don(don) and sach
+            if xong:
+                dau.unlink()
     if n is None:
         raise LoiThuHoi("không khởi chạy được harness")
     if ma is None:
```


- [ ] GREEN: `uv run pytest tests/test_han_tong.py tests/test_han_tong_ngat.py tests/test_lenh_nghiem_thu.py -q`; tests cũ timeout/kill denied phải giữ nguyên semantics.
- [ ] Acceptance bổ sung trước G4: CLI parent chuyển SIGTERM sang đường interruption có kiểm soát, restore handler trong finally; test child giả xác nhận cleanup trước return. Ngắt lần hai trong cleanup phải giữ dấu và không mở cổng; không hứa SIGKILL cleanup được. Chưa có handler SIGTERM trong patch này; task chưa trọn nếu bỏ acceptance này.
- [ ] Review cuối: không xóa dấu khi cleanup lỗi; không in exception payload; cập nhật bs-863.19 bằng evidence thực ở repo đích, không đóng từ plan.

## V2-2 — Adapter đối soát nghiêm (dot6-Q03/dot7-Q01)

**Files:** `tram/beads/bd.py`, `tram/yeu_cau/dich_vu.py`, `tests/yeu_cau_gia.py`; thêm `tests/test_yeu_cau_schema_bd.py`.
**Interface:** `Bd.tat_ca_yeu_cau() -> list[Bead]`, lỗi `LoiBd` cố định. Không thay `tat_ca()` của dashboard. Dịch vụ chỉ dùng adapter mới. Fake kế thừa dùng phương thức ủy quyền động để giữ fault injection/đếm của BdDem.

**Hợp đồng kỹ thuật đề xuất:** đối soát cần id, issue_type, description có type rõ; không dùng default của dataclass thay bằng chứng. Trong lát này thiếu/null field trên bất kỳ record → không kết luận, zero create. Nếu bd thật hợp lệ lược description rỗng, phải đo fixture và review rule riêng ở G6.7; không tự nới vì muốn test xanh.

- [ ] RED: thêm toàn bộ test. Hiện null id/thiếu issue_type/description đi tới create. `uv run pytest tests/test_yeu_cau_schema_bd.py -q`.

```python
import json
import pytest
from yeu_cau_gia import LOGIN, MA, yc
from tram.beads.bd import Bd
from tram.yeu_cau.mau import dong_dau
from tram.yeu_cau.dich_vu import tiep_nhan
from tram.yeu_cau.so_nhan import SoNhan


@pytest.mark.parametrize("sua, bo", [({"id": None}, None), ({"id": ""}, None),
    ({"id": 7}, None), ({}, "issue_type"), ({}, "description"),
    ({"description": None}, None), ({"issue_type": []}, None)])
def test_schema_la_khong_duoc_coi_la_khong_thay(tmp_path, sua, bo):
    row = {"id": "hr-f1", "updated_at": "x", "issue_type": "feature",
           "description": dong_dau(MA)}
    row.update(sua)
    if bo:
        row.pop(bo)
    goi = []
    def runner(a):
        goi.append(a[2])
        return json.dumps([row]) if a[2] == "list" else "hr-f2"
    so = SoNhan(tmp_path / "so.db")
    try:
        kq = tiep_nhan(so, Bd(tmp_path, runner=runner), yc(), nguoi_gui=LOGIN)
        assert (kq.trang_thai, kq.ly_do) == ("chua_tao", "doc_bd_loi")
        assert goi == ["list"]
        assert so.lay(MA).trang_thai == "nhan"
    finally:
        so.close()


def test_schema_tot_marker_cu_khong_create(tmp_path):
    row = {"id": "hr-f1", "updated_at": "x", "issue_type": "feature",
           "description": dong_dau(MA)}
    goi = []
    def runner(a):
        goi.append(a[2])
        return json.dumps([row])
    so = SoNhan(tmp_path / "so.db")
    try:
        kq = tiep_nhan(so, Bd(tmp_path, runner=runner), yc(), nguoi_gui=LOGIN)
        assert (kq.trang_thai, kq.bead_id) == ("da_co", "hr-f1")
        assert goi == ["list"]
    finally:
        so.close()
```

- [ ] Implementation tối thiểu (3 hunks). Không in raw JSON trong lỗi adapter mới.

```diff
--- a/tram/beads/bd.py
+++ b/tram/beads/bd.py
@@ -37,6 +37,10 @@
 
     def tat_ca(self) -> list[Bead]:
         return _doc_ds(self._chay("list", "--json", "--all", "--limit", "0"))
+
+    def tat_ca_yeu_cau(self) -> list[Bead]:
+        """Đối soát trước create: schema lạ không đồng nghĩa danh sách rỗng."""
+        return _doc_ds_yeu_cau(self._chay("list", "--json", "--all", "--limit", "0"))
 
     def phien_ban(self, bead_id: str) -> str:
         """`updated_at` hiện tại của một bead — version để kiểm lại trước khi ghi (spec §5.6).
@@ -117,3 +121,20 @@
         return [Bead.tu_json(d) for d in ds]
     except (ValueError, KeyError, TypeError, AttributeError) as e:
         raise LoiBd(f"bd list: JSON không đọc được ({type(e).__name__}: {e})") from e
+
+
+def _doc_ds_yeu_cau(ra: str) -> list[Bead]:
+    try:
+        ds = json.loads(ra)
+        if not isinstance(ds, list):
+            raise ValueError
+        for d in ds:
+            if not isinstance(d, dict):
+                raise ValueError
+            if any(not isinstance(d.get(k), str) for k in ("id", "issue_type", "description")):
+                raise ValueError
+            if not d["id"] or d["id"] != d["id"].strip() or not d["issue_type"]:
+                raise ValueError
+        return [Bead.tu_json(d) for d in ds]
+    except (ValueError, KeyError, TypeError, AttributeError):
+        raise LoiBd("bd list: schema đối soát không hợp lệ") from None
```

```diff
--- a/tram/yeu_cau/dich_vu.py
+++ b/tram/yeu_cau/dich_vu.py
@@ -26,7 +26,7 @@
 def _doi_soat(bd, ma: str) -> tuple[str | None, str | None]:
     """(id, None): thấy đúng một feature mang dấu · (None, None): chưa thấy · (None, lý do): không kết luận được."""
     try:
-        ds = tim_theo_dau(bd.tat_ca(), ma)
+        ds = tim_theo_dau(bd.tat_ca_yeu_cau(), ma)
     except Exception:                           # LoiBd, JSON/giải mã lạ: không kết luận, không lộ chi tiết
         return None, "doc_bd_loi"
     if len(ds) > 1:
```

```diff
--- a/tests/yeu_cau_gia.py
+++ b/tests/yeu_cau_gia.py
@@ -46,6 +46,9 @@
         dong = self.tep.read_text(encoding="utf-8").splitlines() if self.tep.exists() else []
         return [Bead.tu_json(json.loads(x)) for x in dong]
 
+    def tat_ca_yeu_cau(self):
+        return self.tat_ca()
+
     def them(self, mo_ta, loai="feature", nhan=(), tieu_de="x", uu_tien=None):
         with open(self.tep, "a+", encoding="utf-8") as f:
             fcntl.flock(f, fcntl.LOCK_EX)
```


- [ ] GREEN: `uv run pytest tests/test_yeu_cau_schema_bd.py tests/test_yeu_cau_dich_vu.py tests/test_yeu_cau_su_co.py tests/test_api_yeu_cau.py tests/test_api_yeu_cau_tu_choi.py -q`. Sau V2-7 mới chạy lại các tests đa tiến trình.
- [ ] Thêm ca container {}, duplicate marker, unknown + schema hỏng và unknown → commit trễ, zero create; dùng cùng runner JSON thật. Existing service tests phải giữ hành vi cùng key khác payload=409.
- [ ] Review adapter boundary, body/log sentinel và G6.7 fixture Beads thật; không suy ra hỗ trợ schema chưa đo.

## V2-3 — Inventory môi trường không phụ thuộc bat_ghi

**Files:** thêm `tram/giao_viec/du_an_quan_sat.py`, `tests/test_du_an_quan_sat.py`; sửa `noi_that.py`, `lenh_nghiem_thu.py`, `kiem_principal.py`. Giữ `cac_du_an_that` cho chọn việc; observer nhận `cac_du_an_quan_sat(thu_muc=None)` gồm cả khóa ghi. Một YAML hỏng → LoiBanChep, không bỏ qua.

- [ ] RED: thêm file test sau, chạy `uv run pytest tests/test_du_an_quan_sat.py -q` (thiếu module là RED đầu; sau khi có helper phải có regression wiring để tránh sửa chỉ helper).

```python
import pytest
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import env_kin
from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat


def test_du_an_khoa_ghi_van_phai_kin_env(tmp_path):
    env = tmp_path / "env.testing"
    env.write_text("GIA=1")
    env.chmod(0o644)
    cfg = tmp_path / "du-an"
    cfg.mkdir()
    (cfg / "b.yaml").write_text(
        f"ten: b\nduong_dan: /r/b\nhang_rao: {{}}\nbat_ghi: false\n"
        f"moi_truong_kiem:\n  file: {env}\n  dich: .env.testing\n")
    ds = lambda: cac_du_an_quan_sat(cfg)
    assert [x.ten for x in ds()] == ["b"]
    with pytest.raises(LoiBanChep):
        env_kin(ds)
    env.chmod(0o600)
    env_kin(ds)


def test_mot_yaml_hong_khong_duoc_bien_mat_khoi_inventory(tmp_path):
    (tmp_path / "x.yaml").write_text("ten: [")
    with pytest.raises(LoiBanChep):
        cac_du_an_quan_sat(tmp_path)
```

- [ ] Tạo helper nguyên văn:

```python
from pathlib import Path
from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
from tram.giao_viec.ban_chep import LoiBanChep


def cac_du_an_quan_sat(thu_muc: Path | None = None) -> list:
    try:
        return [nap_du_an(ten, thu_muc=thu_muc)
                for ten in liet_ke_du_an(thu_muc) if not ten.startswith("_")]
    except Exception as e:
        raise LoiBanChep(f"không đọc đủ inventory môi trường kiểm ({type(e).__name__})") from None
```

- [ ] Nối helper vào ba đường sau. Phải bổ sung test gọi `dung_bo_that`/CLI con/probe mặc định với spies cho các observer OS khác; gọi observer env lấy từ CongLuot, khẳng định env 0644 của dự án false làm nó ném. Không import module thành công rồi coi wiring đạt.

```diff
--- a/tram/giao_viec/noi_that.py
+++ b/tram/giao_viec/noi_that.py
@@ -21,6 +21,7 @@
 from tram.giao_viec.doc_beads import DocBeads
 from tram.giao_viec.luong import bat_dau_luong_giao
 from tram.giao_viec.cong_that import dung_cong, thu_hoi_theo_uid
+from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat
 from tram.kiem.chay_lenh import _kill_nhom
 
 
@@ -55,7 +56,8 @@
                       tao_bd=lambda da: Bd(da.duong_dan, actor=ASSIGNEE), mo_kho=mo_kho_phieu, ch=ch,
                       dong_ho=lambda: datetime.now(timezone.utc), boc=pk.boc_lenh if pk else None,
                       don_sach=partial(thu_hoi_theo_uid, pk) if pk else None, boc_luot=pk.boc_luot if pk else None,
-                      cong=dung_cong(pk, cg.thu_muc_kiem, cac_du_an=cac) if pk else None,
+                      cong=dung_cong(pk, cg.thu_muc_kiem,
+                                      cac_du_an=lambda: cac_du_an_quan_sat(thu_muc_du_an)) if pk else None,
                       kill=pk.kill_nhom if pk else _kill_nhom,
                       doc_beads=DocBeads(bo_dem) if bo_dem is not None else None, thu_muc_kiem=cg.thu_muc_kiem,
                       p4c=nap_phu_thuoc_4c() if cg.bat else PhuThuoc4c())
```

```diff
--- a/tram/giao_viec/lenh_nghiem_thu.py
+++ b/tram/giao_viec/lenh_nghiem_thu.py
@@ -30,8 +30,8 @@
 def _don(pk, goc) -> bool:
     from tram.giao_viec import cong_that
     from tram.giao_viec.ban_chep import giu_khoa
-    from tram.giao_viec.noi_that import cac_du_an_that
-    c = cong_that.dung_cong(pk, goc, cac_du_an=cac_du_an_that)
+    from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat
+    c = cong_that.dung_cong(pk, goc, cac_du_an=cac_du_an_quan_sat)
     with giu_khoa():
         try:
             c.thu_hoi()
@@ -49,13 +49,13 @@
 def _trong(args, pk, goc) -> int:
     from tram.giao_viec.cong_that import dung_cong, thu_hoi_theo_uid
     from tram.giao_viec.nghiem_thu_kiem import nghiem_thu
-    from tram.giao_viec.noi_that import cac_du_an_that
+    from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat
     from tram.tho.kiem_may import in_ket_qua
     dau = tram_home() / "kiem-lai.dong"
     if os.getppid() != args.cha or args.dau_ino is None or not dau.exists() or dau.stat().st_ino != args.dau_ino:
         print("Không chạy: --trong chỉ dành cho tiến trình con của CLI cha đang giữ dấu kiem-lai.dong", file=sys.stderr)
         return 2
-    cong = dung_cong(pk, goc, cac_du_an=cac_du_an_that)
+    cong = dung_cong(pk, goc, cac_du_an=cac_du_an_quan_sat)
     van_ban, ma = in_ket_qua(nghiem_thu(pk, goc, cong=cong, boc_luot=pk.boc_luot,
                                         thu_hoi=partial(thu_hoi_theo_uid, pk), tai_sinh=args.tai_sinh, cho=args.cho))
     print(van_ban)
```

```diff
--- a/tram/giao_viec/kiem_principal.py
+++ b/tram/giao_viec/kiem_principal.py
@@ -17,6 +17,7 @@
 from tram.duong_dan import tram_home
 from tram.giao_viec.ban_chep import KiemLaiDangBan, giu_khoa, ten_ban_chep
 from tram.giao_viec.cong_that import dung_cong, thu_hoi_theo_uid
+from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat
 from tram.giao_viec.kiem_goc import kiem_sudoers_khong_root, kiem_thu_muc_goc, uid_that
 from tram.kiem.chay_gioi_han import chay_gioi_han
 from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem
@@ -93,7 +94,7 @@
                    uid_cua: Callable[[str], int] = uid_that) -> list[MucKiem]:
     if pk is None:
         return [_muc("principal kiểm lại", False, "chưa đặt cach_ly.tram_kiem — chờ S6")]
-    sud_chay, cong = chay or partial(chay_gioi_han, kill=kill_cuc_bo), cong or dung_cong(pk, thu_muc, cac_du_an=list)
+    sud_chay, cong = chay or partial(chay_gioi_han, kill=kill_cuc_bo), cong or dung_cong(pk, thu_muc, cac_du_an=cac_du_an_quan_sat)
     chay = chay or partial(chay_gioi_han, kill=gop_kill(pk.kill_nhom, kill_cuc_bo))
     try:
         sud = kiem_sudoers_khong_root(chay=sud_chay)
```


- [ ] Sửa test `tests/test_lenh_nghiem_thu.py` dùng identity callback mới; không bỏ assertion inventory. Chạy `uv run pytest tests/test_du_an_quan_sat.py tests/test_cong_that.py tests/test_lenh_nghiem_thu.py tests/test_bat_ghi.py -q`, rồi tests kiem_principal/noi_that liên quan.
- [ ] Chấp nhận: dự án false vẫn không giao/ghi; observer thấy env của nó; YAML hỏng đóng cổng; thông báo không lộ YAML/raw value. Thiếu env ở dự án chưa dùng cũng phải được xử lý minh bạch, không tự bỏ dự án khỏi observer.

## V2-4 — Chứng cứ từng probe và OS matrix

**Files:** `tram/giao_viec/kich_ban_nghiem_thu.py`, `nghiem_thu_kiem.py`; thêm `tram/giao_viec/chung_cu_probe.py`, `tests/test_chung_cu_probe.py`; sửa tests harness. Đây là task hai bước: code parser/producer offline, sau đó proof OS riêng; parser đạt không đóng C01.

**Interface mới:** mỗi nguồn in đúng một `probe:<nguon>:bat-dau` và một `probe:<nguon>:ket:<ma>` sau khi lệnh trả. Thiếu/duplicate/timeout/không integer/nguồn lạ = chưa chứng minh. Mã khác 0 chỉ là **thất bại**, không tự là “Seatbelt chặn”. Bằng chứng enforcement cần positive control trong môi trường thử được duyệt và lý do OS tương ứng.

- [ ] RED: thêm tests parser sau; `uv run pytest tests/test_chung_cu_probe.py -q`.

```python
import pytest
from tram.giao_viec.chung_cu_probe import doc_probe


@pytest.mark.parametrize("s", ["kich-ban-bat-dau\n", "probe:cron:bat-dau\n",
    "probe:cron:ket:126\n", "probe:cron:bat-dau\nprobe:cron:ket:x\n",
    "probe:cron:bat-dau\nprobe:cron:ket:1\nprobe:cron:ket:1\n"])
def test_thieu_hong_trung_khong_phai_bi_chan(s):
    assert doc_probe(s, "cron") is None


def test_co_ma_nhung_khong_tu_ket_luan_seatbelt():
    assert doc_probe("probe:cron:bat-dau\nprobe:cron:ket:126\n", "cron") == 126
    assert doc_probe("probe:cron:bat-dau\nprobe:cron:ket:0\n", "cron") == 0
```

- [ ] Implement helper đầy đủ:

```python
import re


def doc_probe(log: str, nguon: str) -> int | None:
    dong = [s for s in log.splitlines() if s.startswith(f"probe:{nguon}:")]
    if len(dong) != 2 or dong[0] != f"probe:{nguon}:bat-dau":
        return None
    m = re.fullmatch(rf"probe:{re.escape(nguon)}:ket:([0-9]+)", dong[1])
    if m is None:
        return None
    ma = int(m.group(1))
    return ma if 0 <= ma <= 255 else None
```

- [ ] Producer: giữ nguyên các command trong `cai`, thay cấu trúc trả shell bằng vòng zip NGUON/cai. Bỏ `&& echo ...-da-cai` ở từng lệnh; lấy mã của command nguyên tử. Chạy fake commands trong test, tuyệt đối không thực thi cron/at thật. Template cụ thể:

```python
def boc_probe(nguon: str, lenh: str) -> str:
    return (f'( echo probe:{nguon}:bat-dau; ( {lenh} ); ma=$?; '
            f'echo probe:{nguon}:ket:$ma ) &')
```

- [ ] Consumer: dùng `doc_probe` cho từng NGUON. `None` → ĐỎ “probe chưa hoàn tất”; 0 → ĐỎ “cài được” (setsid: riêng theo cleanup); >0 → VÀNG “lệnh thất bại, chờ proof OS”, **không xanh**. G4 runbook phải đòi biên bản reason/positive control mới công nhận deny. Thêm integration regression `kich-ban-bat-dau` đơn lẻ và fake code 127/timeout không cho toàn harness đạt. CLI `in_ket_qua` coi vàng có thể mã 0: vì vậy thêm mục tổng `đủ bằng chứng S6` ĐỎ khi bất kỳ probe chưa được nghiệm thu, hoặc trả mã riêng chưa đạt; không chỉ đổi màu rồi vẫn exit 0.
- [ ] GREEN focused tests harness + parser + UID guard; monkeypatch probe runner assert zero host commands. Với một fake nguồn hoàn thành thành công thì phải đỏ, với nguồn chưa chạy phải đỏ tổng.
- [ ] OS subtask (chờ G3/permission): fixture riêng cho direct XPC job-creation trong user/gui/login, POSIX named semaphore/shared memory, SysV IPC, loopback/remote socket, Mach lookup trái allowlist, nguồn chạy sau cleanup; mỗi case có đối chứng dương, deadline và receipt cleanup. Chưa có executable probes này trong snapshot; **không giao thực thi từ shell mẫu trên**. Coding agent phải soạn harness OS cụ thể và review trước G4, không đóng C01 từ exit 126 của launchctl.

## V2-5 — Attestation profile, không tìm substring (task thiết kế/cài đặt còn chặn)

**Files:** `tram/tho/quyen_kiem.py`, `tram/chu/cai_dat_kiem.py`, `tram/giao_viec/cong_that.py`, tests profile/install. Giữ hồ sơ root:wheel, runtime không sudo.

- [ ] RED: thêm vào `tests/test_cong_that.py`:

```python
@pytest.mark.parametrize("them", ["(allow file-write*)", "(allow network*)",
                                 "(allow job-creation)"])
def test_profile_mo_rong_du_hai_chuoi_van_bi_tu_choi(tmp_path, tram_home_tam, them):
    p = tmp_path / "hs.sb"
    p.write_text(f'(version 1)\n(deny default)\n'
                 f'(deny file-read* (subpath "{tram_home_tam}"))\n{them}\n')
    p.chmod(0o644)
    with pytest.raises(LoiBanChep):
        ho_so_cai(p, chu=os.getuid())
```

- [ ] Contract trước code: expected profile sinh bằng đúng `ho_so_tram_kiem(tram_home_tram, nha_quan_ly, goc, cong)` và cùng phiên bản mã đã review. Runtime hiện không có `nha_quan_ly` chính tắc, nên không tự dùng Path.home(): tài khoản trạm và quản lý thợ khác nhau. Chọn manifest của installer ghi rõ inputs + hash phiên bản; expected không được đọc từ file profile đang cần kiểm rồi tự hash so với chính nó.
- [ ] Installer ghi manifest root-owned qua cùng receipt/journal với profile, mode 0644; runtime kiểm owner, mode, loại regular/no symlink và tất cả parent không writable bởi principal. Byte profile phải bằng generator với input manifest đã đối chiếu config hiện hành; đổi TRAM_HOME/goc/version → đóng, yêu cầu cài lại qua gate. Không bỏ compat nguồn cũ bằng nhận ngầm profile chỉ có hai chuỗi.
- [ ] RED bổ sung: profile đúng; sửa một allow; đường gốc cũ; comment giả deny; manifest thiếu/hỏng/khác config; symlink; parent writable; installer crash giữa hai file; root mode sai. Chỉ fake stat/install runner, không chmod/chown host.
- [ ] GREEN: tests profile/cai_dat_kiem/cong_that/lenh_nghiem_thu sau khi implementation đầy đủ được review. Runbook G3.0 lưu digest/profile version, không chứa credentials. **Chưa có patch hoàn chỉnh trong gói** vì cần khóa contract manifest/runtime inputs; không triển khai riêng một hash helper và coi task xong.

## V2-6 — Backlog lifecycle phải chốt trước code

Đây là các task TDD có acceptance bắt buộc, **chưa có implementation đầy đủ**. Giữ trạng thái “thiết kế cần hoàn thiện”; không dùng quy tắc “mọi dòng có trong plan” để giao code từ các mô tả này. Cần coding agent bổ sung diff đầy đủ sau V2-0, gửi review lại. Đây là lý do chưa đánh dấu C02/P1 đã sửa.

### V2-6a — H1 stdin/archive (bs-863.18, trước G4)

Files: `tram/kiem/chay_gioi_han.py`, `tram/giao_viec/ban_chep.py`, `cay_kiem.py`; test mới `tests/test_ban_chep_pipeline_han.py`.

- [ ] RED contract: thêm `stdin=` (file object/FD) loại trừ `input`; truyền trực tiếp cho Popen, không đọc cả archive vào RAM. Dùng fake `khoi` ghi kw, assert stdin đúng object và input+stdin lỗi trước spawn. Test consumer timeout/kill denied; producer lỗi/consumer exit sớm; producer còn treo khi tar xong. Assert mọi owned process được attempted cleanup, cổng chưa rõ còn đóng; byte env không vào exception.
- [ ] Thiết kế ownership cả producer git archive và consumer tar; start_new_session cho producer, đóng bản sao stdout parent sau khi truyền, thu hồi producer trong finally kể cả tar spawn thất bại. Không chỉ đổi `_chay=partial(chay_gioi_han,kill=...)` vì API hiện chưa có stdin và producer vẫn ngoài primitive.
- [ ] GREEN sau implementation: tests ban_chep/tree/R7, new pipeline, chay_gioi_han, harness. Mọi timeout có cận toàn pipeline + cleanup, không cộng wait thứ hai vô hạn. Không đổi metadata tar/tree.

### V2-6b — Probe âm/login đúng principal (bs-863.14/.17, trước G5)

Files: `tram/tho/kiem_am.py`, `kiem_cong.py`, `do_may.py`, `kiem_3b.py`, `tram/chu/kiem_cach_ly.py`.

- [ ] RED: fake spawn timeout và kill PermissionError phải kết thúc trong deadline, kết quả không xanh. `codex login status` argv phải qua pr.boc, kill=pr.kill_nhom, env mới chỉ PATH/LANG/CODEX_HOME; không manager HOME/token. Hai khe khác nhau không lẫn CODEX_HOME. Không principal/sai UID → zero login/app-server spawn.
- [ ] Tách probe version không credential khỏi login-status; nối kill/runner rõ vào consumer, kiểm UID thật trước. Không đổi sang P1 mà quên môi trường hoặc biến một lỗi hạ tầng thành negative success.
- [ ] GREEN: tests kiem_am/kiem_cong/kiem_3b + quota propagation/heartbeat, sentinel capsys/body/sổ; `LoiThuHoi` dừng khe đúng chủ đích. G5 đo nhịp thực riêng, không suy deadline chỉ từ mock.

### V2-6c — TheoDoi dừng hữu hạn (bs-863.16, trước G7)

Files: `tram/tho/theo_doi.py`, callers mot_lan/phieu_chay, HTTP/Git I/O của `_moc`.

- [ ] RED: fake `mot_luot` kẹt I/O với Event handshake. `ket_thuc` trả/né mốc trong hạn nhưng không gọi final read đồng thời, không xóa pid/phiếu hoặc chạy lượt tiếp khi thread chưa dừng.
- [ ] Đưa cancellation/deadline vào cả I/O; join hữu hạn chỉ là phần chờ. Nếu chưa dừng thì báo LoiThuHoi/stop khe và giữ receipt. Không trả success trong lúc luồng nền vẫn có thể push/ghi.
- [ ] GREEN: callback release đúng hạn, timeout, exception, tín hiệu dừng, last-row delivery exactly once; fake server/runner, không push/API thật. Worker integration sau V2-0 và .15.

## V2-7 — Test safety và envelope errors

**Bead:** `bs-2bd.1.16`. Review tĩnh vòng 1 trên HEAD `684158e`; chưa chạy RED/GREEN.
**Sửa:** `tests/test_yeu_cau_da_tien_trinh.py`, `tests/test_api_yeu_cau_hai_tien_trinh.py`,
`tests/yeu_cau_gia.py`, `tests/api_yeu_cau_gia.py`, `tram/api/tuyen_yeu_cau.py`.
**Thêm:** `tests/tien_trinh_thu.py`, `tests/test_tien_trinh_thu.py`,
`tests/test_tien_trinh_callsite.py`, `tests/test_tien_trinh_barrier.py`,
`tests/test_api_yeu_cau_loi_kin.py`, `tram/api/loi_envelope.py`.

Hợp đồng: chỉ thu hồi object `multiprocessing.Process` do chính test tạo, không đọc PID từ file,
không `killpg`/quét process. Danh sách sở hữu ghi trước `start`; toàn bộ tạo/start/join/get/assert nằm
trong context cleanup. Mỗi join cleanup tối đa 2 giây, tối đa hai join/con; không retry vô hạn.
Lỗi cleanup phải làm test thất bại và vẫn thử dọn con tiếp, vẫn đóng queue. Không báo PID/exception gốc.
Không đóng object Process trong helper để test còn kiểm `exitcode`/`is_alive`; queue không dùng lại sau cleanup.
Chỉ hỗ trợ con trực tiếp của các target này (không sinh cháu), không thay primitive lifecycle sản phẩm V2-0.
Không sửa file kill list, auth, DB schema, công tắc hay D45–D53. HTTP chỉ bắt
`RequestValidationError` tại router 4d, trả body cố định; các tuyến khác giữ handler mặc định.

### V2-7a — RED helper, rồi GREEN helper

- [ ] Tạo nguyên file `tests/test_tien_trinh_thu.py` bên dưới trước. Chạy focused sau khi được phép
  triển khai: ban đầu lỗi import vì helper chưa tồn tại, **chưa tính là RED hành vi**. Tạo helper
  `tests/tien_trinh_thu.py` ở dạng RED sau rồi chạy lại; test thứ tự và còn-sống phải đỏ do không dọn.

```python
"""Bản RED tạm của helper sở hữu tiến trình test."""
from contextlib import contextmanager


def don_cac_con(ds):
    return None


@contextmanager
def quan_ly_con(ds, hang):
    yield
```

Nguyên file `tests/test_tien_trinh_thu.py`:

```python
"""Cleanup có hạn, không bỏ con sau khi con trước lỗi; tất cả process ở đây là giả."""
import pytest
from tien_trinh_thu import don_cac_con, quan_ly_con


class ConGia:
    def __init__(self, *, pid=1, song=True, li=False, hong=False):
        self.pid, self.song, self.li, self.hong = pid, song, li, hong
        self.nhat_ky = []

    def is_alive(self):
        self.nhat_ky.append("song")
        return self.song

    def terminate(self):
        self.nhat_ky.append("terminate")
        if self.hong:
            raise OSError("chi-tiet-khong-duoc-lo")

    def join(self, han):
        self.nhat_ky.append(("join", han))

    def kill(self):
        self.nhat_ky.append("kill")
        self.song = self.li


class HangGia:
    def __init__(self, hong=False):
        self.nhat_ky, self.hong = [], hong

    def cancel_join_thread(self):
        self.nhat_ky.append("cancel")
        if self.hong:
            raise OSError("chi-tiet-khong-duoc-lo")

    def close(self):
        self.nhat_ky.append("close")


def test_terminate_join_kill_join_dung_thu_tu():
    p = ConGia()
    don_cac_con([p])
    assert p.nhat_ky == ["song", "terminate", ("join", 2), "song", "kill", ("join", 2), "song"]
    assert not p.song


def test_con_chua_start_va_con_da_thoat_khong_nhan_signal():
    chua, xong = ConGia(pid=None), ConGia(song=False)
    don_cac_con([chua, xong])
    assert chua.nhat_ky == []
    assert xong.nhat_ky == ["song", ("join", 2), "song", "song"]


def test_terminate_du_thi_khong_kill():
    class ConDungMem(ConGia):
        def terminate(self):
            super().terminate()
            self.song = False

    p = ConDungMem()
    don_cac_con([p])
    assert p.nhat_ky == ["song", "terminate", ("join", 2), "song", "song"]
    assert not p.song


@pytest.mark.parametrize("kw", [{"li": True}, {"hong": True}])
def test_loi_con_dau_van_don_con_sau_va_queue(kw):
    a, b, hang = ConGia(**kw), ConGia(), HangGia()
    with pytest.raises(RuntimeError, match="Không dọn được tiến trình test") as loi:
        with quan_ly_con([a, b], hang):
            pass
    assert "chi-tiet" not in str(loi.value)
    assert not b.song and "kill" in b.nhat_ky
    assert hang.nhat_ky == ["cancel", "close"]


@pytest.mark.parametrize("loai", [AssertionError, RuntimeError, KeyboardInterrupt])
def test_loi_than_khong_bo_cleanup_va_duoc_truyen_lai(loai):
    p, hang = ConGia(), HangGia()
    with pytest.raises(loai, match="loi-than"):
        with quan_ly_con([p], hang):
            raise loai("loi-than")
    assert not p.song and hang.nhat_ky == ["cancel", "close"]


def test_cancel_queue_loi_van_close_va_bao_that_bai():
    hang = HangGia(hong=True)
    with pytest.raises(RuntimeError, match="Không đóng được queue test"):
        with quan_ly_con([], hang):
            pass
    assert hang.nhat_ky == ["cancel", "close"]
```

- [ ] GREEN: thay toàn bộ bản RED `tests/tien_trinh_thu.py` bằng:

```python
"""Sở hữu và thu hồi con trực tiếp do test tạo; không dùng cho lifecycle sản phẩm."""
from contextlib import contextmanager


def don_cac_con(ds):
    loi = False
    for p in ds:
        try:
            if p.pid is None:
                continue
            if p.is_alive():
                p.terminate()
            p.join(2)
            if p.is_alive():
                p.kill()
                p.join(2)
            if p.is_alive():
                loi = True
        except Exception:
            loi = True
    if loi:
        raise RuntimeError("Không dọn được tiến trình test do fixture sở hữu") from None


def dong_hang(hang):
    loi = False
    for dong in (hang.cancel_join_thread, hang.close):
        try:
            dong()
        except Exception:
            loi = True
    if loi:
        raise RuntimeError("Không đóng được queue test") from None


@contextmanager
def quan_ly_con(ds, hang):
    try:
        yield
    finally:
        try:
            don_cac_con(ds)
        finally:
            dong_hang(hang)
```

Lỗi OS khi terminate/join/kill là thất bại cleanup, không tuyên bố đã thu hồi được con đó.
Helper vẫn xử lý các con khác và queue. Nếu cả cleanup con lẫn queue lỗi, exception queue giữ
exception cleanup trong context; cả hai chỉ có thông báo cố định. Không cam kết chống nhiều lần
ngắt bất đồng bộ trong chính cleanup; không dùng helper này làm bằng chứng G4/G5.

### V2-7b — RED callsite, rồi bọc đầy đủ hai callsite

Tạo nguyên file `tests/test_tien_trinh_callsite.py` trước khi thay callsite. Dùng chính hai hàm
hiện tại, thay CTX bằng giả; không mock `quan_ly_con`. Mỗi lỗi phải dẫn tới cleanup. Trên mã cũ
assert queue/con đỏ vì không có finally. Ca constructor thứ hai kiểm cả cửa sổ cấp phát sau start.

```python
"""Lỗi constructor/start/join/get/assert tại callsite thật đều phải đi qua cleanup."""
from types import SimpleNamespace

import pytest
import test_api_yeu_cau_hai_tien_trinh as api
import test_yeu_cau_da_tien_trinh as dich_vu
from test_tien_trinh_thu import ConGia, HangGia


@pytest.mark.parametrize("mod", [api, dich_vu])
@pytest.mark.parametrize("diem", ["tao", "start", "join", "get", "assert"])
def test_callsite_don_khi_loi(tmp_path, monkeypatch, mod, diem):
    ds, hang = [], HangGia()

    class Con(ConGia):
        exitcode = (9 if mod is api else None) if diem == "assert" else 0

        def start(self):
            if diem == "start" and self is ds[-1] and len(ds) == 2:
                raise RuntimeError("loi-thu")
            self.pid, self.song = 1, True

        def join(self, han):
            if han == 60 and diem == "join":
                raise RuntimeError("loi-thu")
            super().join(han)

    def tao_con(**kw):
        if diem == "tao" and len(ds) == 1:
            raise RuntimeError("loi-thu")
        p = Con(pid=None, song=False)
        ds.append(p)
        return p

    def lay(*, timeout):
        assert timeout == 5
        raise RuntimeError("loi-thu")

    hang.get = lay
    ctx = SimpleNamespace(Barrier=lambda n: object(), Queue=lambda: hang, Process=tao_con)
    monkeypatch.setattr(mod, "CTX", ctx)
    with pytest.raises(AssertionError if diem == "assert" else RuntimeError):
        if mod is api:
            api.test_hai_tien_trinh_tram_api_cung_yeu_cau_chi_mot_feature(tmp_path)
        else:
            dich_vu.chay(2, tmp_path / "sk.db", tmp_path)
    assert hang.nhat_ky == ["cancel", "close"]
    assert all(not p.song for p in ds)
    assert all("kill" in p.nhat_ky for p in ds if p.pid is not None)
```

- [ ] Trong `tests/test_yeu_cau_da_tien_trinh.py`, thêm import:

```python
from tien_trinh_thu import quan_ly_con
```

Thay **toàn bộ** hàm `chay` (các test nghiệp vụ bên dưới giữ nguyên):

```python
def chay(n, db, thu_muc, su_co=None):
    cho, hang = (CTX.Barrier(n) if n > 1 else None), CTX.Queue()
    ds = []
    with quan_ly_con(ds, hang):
        for _ in range(n):
            p = CTX.Process(target=chay_mot, args=(str(db), str(thu_muc), cho, hang, su_co))
            ds.append(p)
            p.start()
        for p in ds:
            p.join(60)
        ma_thoat = [p.exitcode for p in ds]
        assert all(c is not None for c in ma_thoat), "Tiến trình test quá hạn"
        kq = [hang.get(timeout=5) for c in ma_thoat if c == 0]
        return sorted(kq), ma_thoat
```

- [ ] Trong `tests/test_api_yeu_cau_hai_tien_trinh.py`, thêm cùng import:

```python
from tien_trinh_thu import quan_ly_con
```

Thay **toàn bộ** hàm test, không bỏ assert nghiệp vụ:

```python
def test_hai_tien_trinh_tram_api_cung_yeu_cau_chi_mot_feature(tmp_path):
    cho, hang = CTX.Barrier(2), CTX.Queue()
    ds = []
    with quan_ly_con(ds, hang):
        for _ in range(2):
            p = CTX.Process(target=chay_api, args=(str(tmp_path), cho, hang))
            ds.append(p)
            p.start()
        for p in ds:
            p.join(60)
        assert [p.exitcode for p in ds] == [0, 0]
        ma = sorted(hang.get(timeout=5) for _ in ds)
        assert ma.count(201) == 1 and set(ma) <= {200, 201, 202}
        assert BdTep(tmp_path).so_lan_tao() == 1
        app, _, _, _ = mo_app(tmp_path)
        r = tao(app)
        assert (r.status, r.json()["trang_thai"], r.json()["bead_id"]) == (200, "da_co", "hr-f1")
```

### V2-7c — RED barrier có hạn, rồi sửa đúng hai target

Tạo nguyên file `tests/test_tien_trinh_barrier.py`. Trên target cũ, `p.join(15)` hết hạn mà
`exitcode is None`, assert đỏ; context vẫn thu hồi cả hai con. Target mới tự thoát lỗi barrier
sau 10 giây, chưa đọc/tạo bead; con cố tình bỏ barrier vẫn bị helper thu hồi.

```python
"""Con bỏ barrier không làm teardown treo; chỉ spawn con Python của chính test."""
import multiprocessing as mp

import pytest
from api_yeu_cau_gia import chay_api
from tien_trinh_thu import quan_ly_con
from yeu_cau_gia import BdTep, chay_mot

CTX = mp.get_context("spawn")


def bo_barrier(san_sang, dung):
    san_sang.set()
    dung.wait(timeout=30)


@pytest.mark.parametrize("target", [chay_mot, chay_api])
def test_con_khong_toi_barrier_duoc_thu_hoi(tmp_path, target):
    san_sang, dung, cho = CTX.Event(), CTX.Event(), CTX.Barrier(2)
    hang, ds = CTX.Queue(), []
    with quan_ly_con(ds, hang):
        bo = CTX.Process(target=bo_barrier, args=(san_sang, dung))
        ds.append(bo)
        bo.start()
        assert san_sang.wait(timeout=10)
        args = (str(tmp_path), cho, hang) if target is chay_api else (
            str(tmp_path / "sk.db"), str(tmp_path), cho, hang)
        p = CTX.Process(target=target, args=args)
        ds.append(p)
        p.start()
        p.join(15)
        assert p.exitcode is not None and p.exitcode != 0
        assert bo.is_alive()
        assert BdTep(tmp_path).so_lan_tao() == 0
        assert not (tmp_path / "beads.jsonl").exists()
    assert all(not p.is_alive() and p.exitcode is not None for p in ds)
```

- [ ] Trong `tests/yeu_cau_gia.py`, chỉ thay toàn bộ hàm `chay_mot` ở cuối file như sau.
  **Giữ nguyên** `BdTep.tat_ca_yeu_cau()` đã thêm ở V2-2; không chép đè helper từ snapshot cũ.

```python
def chay_mot(db, thu_muc, cho, hang, su_co=None, ngu=0.2):
    """Một tiến trình tram-api giả: chờ hiệu lệnh có hạn rồi tiếp nhận yêu cầu."""
    so, bd = SoNhan(Path(db)), BdTep(thu_muc, ngu=ngu, su_co=su_co)
    try:
        if cho is not None:
            cho.wait(timeout=10)
        hang.put(tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN).trang_thai)
    finally:
        so.close()
```

`os._exit(9)` trong fake cố ý mô phỏng crash nên bỏ qua finally; OS đóng handle của tiến trình,
cha vẫn join và đóng queue. Không thay cửa sổ crash hay số lần create của test cũ.

- [ ] Trong `tests/api_yeu_cau_gia.py`, chỉ thay toàn bộ hàm `chay_api` cuối file:

```python
def chay_api(tmp, cho, hang):
    """Một tiến trình tram-api dùng chung sổ và bd giả, chờ hiệu lệnh có hạn."""
    app, _, _, _ = mo_app(Path(tmp), ngu=0.2)
    cho.wait(timeout=10)
    hang.put(tao(app).status)
```

### V2-7d — RED envelope qua ASGI thật, rồi GREEN chỉ router 4d

Tạo nguyên file `tests/test_api_yeu_cau_loi_kin.py`. Tách type sai/extra/mã sai để mỗi ca có đúng
một lỗi, TAO luôn có `dau_xem` hợp lệ. `caplog` bắt logging, `capsys` bắt stdout/stderr.
Spy đếm cả mở adapter (không chỉ đọc bd), mở sổ và file sổ; không mock validation/route/response.
Ca thiếu/giả danh tính và route ngoài 4d là regression dự kiến đã xanh, không gọi chúng là RED.

```python
"""Envelope lỗi không phản chiếu input; chỉ áp cho hai tuyến 4d."""
import pytest
from api_gia import DAI_CA
from api_yeu_cau_gia import TAO, XEM, dau, mo_app, than
from asgi_gia import goi

BI_MAT = "BI_MAT_DOT7"


@pytest.mark.parametrize("duong", [XEM, TAO])
@pytest.mark.parametrize("sua", [
    {"phieu": BI_MAT}, {"extra": BI_MAT}, {"ma_yeu_cau": BI_MAT},
])
def test_loi_envelope_khong_echo_input(tmp_path, capsys, caplog, duong, sua):
    app, pt, bd, mo = mo_app(tmp_path)
    mo_bd, tao_bd = [], pt.tao_bd_yeu_cau

    def dem(ten):
        mo_bd.append(ten)
        return tao_bd(ten)

    pt.tao_bd_yeu_cau = dem
    body = {**than(), **({"dau_xem": dau()} if duong == TAO else {}), **sua}
    r = goi(app, "POST", duong, json_body=body, headers=DAI_CA)
    assert r.status == 422
    assert BI_MAT not in r.body.decode()
    assert r.json() == {"trang_thai": "khong_hop_le", "loi": ["Thân yêu cầu không hợp lệ"]}
    out = capsys.readouterr()
    assert BI_MAT not in out.out + out.err + caplog.text
    assert mo == mo_bd == []
    assert bd.so_lan_doc() == bd.so_lan_tao() == 0
    assert not (tmp_path / "so.db").exists()


@pytest.mark.parametrize("duong", [XEM, TAO])
@pytest.mark.parametrize("headers", [{}, {**DAI_CA, "Tailscale-User-Login": "ke-la@example.com"}])
def test_envelope_sai_khong_bo_qua_danh_tinh(tmp_path, duong, headers):
    app, _, bd, mo = mo_app(tmp_path)
    body = {**than(), **({"dau_xem": dau()} if duong == TAO else {}), "phieu": BI_MAT}
    r = goi(app, "POST", duong, json_body=body, headers=headers)
    assert r.status == 403 and BI_MAT not in r.body.decode()
    assert mo == [] and bd.so_lan_doc() == bd.so_lan_tao() == 0


def test_handler_mac_dinh_ngoai_4d_khong_doi(tmp_path):
    app, _, _, _ = mo_app(tmp_path)

    @app.get("/kiem-envelope-test")
    def doc(so: int):
        return {"so": so}

    r = goi(app, "GET", "/kiem-envelope-test?so=sai")
    assert r.status == 422
    assert "detail" in r.json() and "trang_thai" not in r.json()
```

Suy luận RED: `ThanXem.phieu: dict`, `extra="forbid"`, pattern mã gây
`RequestValidationError`; `tram/api/app.py` chưa đăng ký handler cho loại này. Handler mặc định
FastAPI trả `jsonable_encoder(exc.errors())` có input lỗi. Phải ghi kết quả chạy thực lúc triển
khai; review này chỉ đọc mã, không coi suy luận là kết quả test.

- [ ] Tạo nguyên file `tram/api/loi_envelope.py`:

```python
"""Che input trong lỗi envelope của riêng API yêu cầu feature (4d)."""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute


class TuyenEnvelopeKin(APIRoute):
    def get_route_handler(self):
        xu_ly = super().get_route_handler()

        async def goi(request: Request):
            try:
                return await xu_ly(request)
            except RequestValidationError:
                return JSONResponse(
                    {"trang_thai": "khong_hop_le", "loi": ["Thân yêu cầu không hợp lệ"]},
                    status_code=422,
                )

        return goi
```

- [ ] Trong `tram/api/tuyen_yeu_cau.py`, thêm import cạnh import `phu_thuoc`:

```python
from tram.api.loi_envelope import TuyenEnvelopeKin
```

Thay duy nhất dòng dựng router hiện có bằng:

```python
router = APIRouter(dependencies=[Depends(yeu_cau_ghi)], route_class=TuyenEnvelopeKin)
```

Không bắt `HTTPException`, không đổi dependency `yeu_cau_ghi`, không dùng `exc.errors()`/body/log
trong handler, không sửa `tram/api/app.py` hay handler toàn API. Test hợp lệ và lỗi phiếu nghiệp vụ
trong `tests/test_api_yeu_cau.py` tiếp tục kiểm 200/201/202/409/422/503 với body hiện có.

### V2-7e — Kiểm chứng khi triển khai (review không chạy)

- [ ] Chạy RED/GREEN theo thứ tự a → b → c → d; không tăng timeout hay bỏ assertion để qua test.
  Sau mỗi GREEN chạy file test mới tương ứng; sau d chạy focused dưới đây trong môi trường offline
  và PATH chặn host theo `AGENT_RULES.md` §13:

```bash
UV_OFFLINE=1 uv run pytest -q tests/test_tien_trinh_thu.py tests/test_tien_trinh_callsite.py tests/test_tien_trinh_barrier.py tests/test_yeu_cau_da_tien_trinh.py tests/test_api_yeu_cau_hai_tien_trinh.py tests/test_api_yeu_cau_loi_kin.py tests/test_api_yeu_cau.py tests/test_api_yeu_cau_tu_choi.py tests/test_yeu_cau_schema_bd.py
```

- [ ] Trước full `UV_OFFLINE=1 uv run pytest -q`, audit fixture/runner theo §13. PATH không chặn
  đường dẫn tuyệt đối: mọi lời gọi executable tuyệt đối nguy hiểm phải đã bị thay bằng runner giả
  hoặc bị từ chối ở môi trường kiểm. Chưa có bằng chứng đó thì không chạy full, báo thiếu điều kiện;
  không tự thiết kế/cài guard hệ thống trong V2-7. Lưu log guard rỗng và số đo thật, không ghi số dự kiến
  thành số đã đạt. Không chạy frontend vì không đổi frontend.
- [ ] Đối chiếu diff chỉ các file đã liệt kê; giữ strict adapter V2-2 và mọi assert chống tạo trùng.
  Unit fake chứng minh thứ tự/escalation/nhánh lỗi; spawn tests chứng minh thu hồi các con test;
  không thay thế chứng cứ principal, PID reuse, cháu, IPC/launchd hoặc G4/G5/G6 trên OS thật.

## V2-8 — Tài liệu, gate và bàn giao

- [x] Review source/test/plan/spec, ledger finding cũ, severity/file:dòng và readiness từng phần ở root REVIEW-CODEX.
- [x] Runbook dùng function TK, bỏ cleanup glob và không coi G4.0–G4.5 tự đủ đóng C01; phụ lục gate đợt 7 có ưu tiên rõ.
- [x] Tasks/plan và todo trỏ V2, không đóng bead từ tài liệu.
- [ ] Coding agent sau này ghi từng task RED/GREEN trên HEAD thực, diff trọn source/test/docs và review độc lập. V2-0/4(OS)/5/6 còn thiết kế phải có plan bổ sung hoàn chỉnh trước code tương ứng.
- [ ] Tới gate mới trình Đại ca kịch bản cụ thể sau khi chuẩn bị đủ; không xin lại D45–D53, không suy diễn quyền OS từ việc đã duyệt thiết kế.

**Độ sẵn sàng của chính plan này:** V2-1 patch cleanup cơ bản, V2-2 strict adapter và V2-3 inventory có code/test đề xuất cụ thể; vẫn cần RED/GREEN và các integration acceptance ghi rõ. V2-0/4 phần OS/5/6 chưa đủ implementation để giao coding trọn lát. Đây là giới hạn minh bạch của review tĩnh, không báo “đã sửa hết” hay “V2 sẵn sàng code toàn bộ”.

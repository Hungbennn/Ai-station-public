# Lát V5 — vá trước chạy thật — Implementation Plan

> **For agentic workers:** dùng `ai-skills:executing-plans` để thực hiện từng task; checkbox là bước thực thi tương lai. Lời Đại ca ngày 18/10 cho phép viết plan và áp tạm để kiểm chứng; **không commit**, kể cả bước cuối task. Không tự chạy cổng OS.

**Goal:** bịt đường lý do agent mang bí mật vào escalation, chốt các sửa vòng đời đã có, bổ sung hồi quy SQLite và Ctrl-C, sửa tác nhân cấp mã CLI.

**Architecture:** đặt quét tại cửa ghi chung `tao_escalation`, trước chuẩn hoá/cắt chuỗi và cả create/notes. Tái sử dụng primitive sở hữu cây hiện hành; không tạo bộ chạy thay thế. Tách tác nhân nguồn CLI bằng tham số truyền vào nghiệp vụ cấp mã, giữ mặc định API.

**Tech Stack:** Python ≥3.12, stdlib, SQLite, pytest qua runner của repo; không gói mới.

**Spec:** yêu cầu Đại ca 18/10/2026; D102/D111/D133 trong `docs/quyet-dinh/2026-10-18-agent-tu-cap-nhat-viec.md`; D54 trong `docs/quyet-dinh/2026-10-18-chot-sau-dot8.md`; D155 trong `docs/quyet-dinh/2026-10-18-passkey.md`; INV-001 trong `docs/PRODUCT_ARCHITECTURE.md`; `docs/AGENT_RULES.md` §2/11/13; V4-1 `docs/plans/2026-10-18-lat-v4-kiem-khe-chan-pytest.md`; V2 và phụ lục cổng sau review đợt 7.

**Mốc tác giả ghi:** `be1423d`, nhánh `plan/v5-va-truoc-chay-that`, cây ban đầu sạch. Bản này có 10 task. Review vòng 1 chỉ đọc mã, không chạy code/test/mạng. Các số đo bên dưới là báo cáo lịch sử của tác giả, chưa được reviewer xác minh và không chứng minh bản plan đã sửa xanh. Phần **Ghi chú triển khai — review vòng 1** cuối file thắng các khối cũ ở Task 3/9.

## Global Constraints

- Kill list §2 mục 2: **chỉ GỌI** `tram.nho.bi_mat.quet`, không sửa `bi_mat.py`, regex hay ngưỡng. `tram/chu/cap_ma.py` cũng thuộc mục 2: chỉ thêm tác nhân, không đổi mã/mật khẩu/TTL/token.
- Tiến trình, sudo và cách ly thuộc vùng nhạy §2 mục 3: giữ UID thực, `start_new_session`, đăng ký vào `chu` trong `hoan`, thu hồi đúng principal, không xác nhận được thì đóng cổng. Không sửa sudoers, không bỏ `-n`, không cho phép kế thừa credential quản lý.
- Không chạy sudo, Keychain, launchctl ghi, lịch, mạng, `~/.tram` thật; không kill PID không do mình tạo. Fake PID trong test chỉ đi qua kill giả. Không sửa cơ chế an toàn để sandbox xanh.
- Mỗi file `tram/` ≤120 dòng, dòng ≤120 ký tự; lỗi không chép argv, đường dẫn, stdout/stderr hay byte bí mật. Không đổi schema DB, không đổi công tắc giao việc.
- **CHỈ ĐỌC Beads:** đã thử `bd show bs-2bd.1.27 bs-2bd.1.25 bs-863.14 bs-863.16 bs-863.17 bs-863.18 bs-863.19 bs-2bd.1.24 bs-2bd.1.29 bs-78r.11`; thất bại `openat LOCK: operation not permitted`. Không đọc `.beads/`; nội dung từng bead lấy từ yêu cầu Đại ca và đối chiếu mã.
- Các task đã được HEAD sửa không tạo lỗi giả để gọi là lỗi còn tồn tại. RED của chúng dưới đây là **kiểm đột biến**: tạm lấy bỏ đúng bảo vệ, chạy test thấy đỏ, khôi phục thấy xanh. Không áp mutation vào sản phẩm. Phân biệt rõ với RED nguyên trạng Task 1/10.
- Không coi số trong CURRENT_STATE là baseline hiện tại. Baseline tập chọn lọc 54 passed; toàn bộ chưa đo xanh trong sandbox. Các phép đo tiến trình/ps/sysctl/bind/sudo cần người điều phối chạy ngoài sandbox theo cổng; không tự cấp quyền chạy thật.
- Test bắt buộc `tests/chan_host/chay.sh`; mọi lượt đã báo đều **0 dòng chặn mới**. Không pytest trần, không tải gói.
- Worktree không có `.venv`: dùng môi trường đã cài ở checkout chính, chỉ đọc, `UV_NO_SYNC=1`. Bắt buộc đặt `PYTHONPATH="$PWD"` vì editable install ở môi trường đó trỏ checkout chính. Cache riêng `/tmp/v5-uv-cache`. Lần đầu thiếu cache/PYTHONPATH đã được nhận diện, không dùng làm chứng cứ xanh cho bản vá.
- Kết thúc hoàn nguyên toàn bộ nguồn/test tạm; chỉ để lại plan này và báo cáo bắt buộc `KET-QUA-CODEX.md`. Không commit dù PLAN-CHUNG/skill có bước commit.

## Bảng G — giả định và bằng chứng

| G | Điều kiện / giả định | Bằng chứng và giới hạn |
|---|---|---|
| G1 | Câu hỏi bí mật vẫn tạo decision và quan hệ chặn | 12 ca mới: 3 loại lý do × create/gộp × ngắn/sau mốc cắt; scanner thật |
| G2 | D54 đã ghép, không áp V4-1 lần nữa | `kiem_cong._api_db`, `ds + them`, client/route đích, `[CHUYỂN]`; mutation đỏ rồi xanh |
| G3 | Chỉ `sudo -n`, không nhận mật khẩu | Primitive hiện có; bổ sung lỗi cố định hướng dẫn người vận hành chạy `sudo -v` trong Terminal rồi thử lại, cả khi lỗi xảy ra ở bước UID; mã/test đầy đủ ở ghi chú vòng 1 |
| G4 | Join hữu hạn, hết hạn không đọc song song | test hợp đồng + `test_theo_doi_dung.py` |
| G5 | Codex dùng principal/env kín | test argv/kill/env; `kiem_3b` kiểm UID trước |
| G6 | H1 truyền FD nguyên, nguồn có chủ | test hợp đồng stdin + bộ pipeline hiện hành; phần OS còn chờ |
| G7 | Ngắt vẫn thu hồi trước dọn | 4 tổ hợp `KeyboardInterrupt`/lỗi thường × sạch/không sạch |
| G8 | Sidecar bị unlink không phải hardlink | SQLite thật, đóng kết nối khác ngay sau open và fstat=0; hardlink >1 vẫn từ chối |
| G9 | Test ranh giới sở hữu không phụ thuộc thời gian OS | fake Popen + handler đồng bộ; mutation đăng ký sau hoan đỏ; chưa chứng minh nguyên nhân duy nhất của flake cũ |
| G10 | CLI là tram/chu; API vẫn tram/api | test đọc sự kiện DB thật tạm; D155 sẽ đóng CLI ở lát passkey |

## File Structure và thứ tự

Thực hiện 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10. Task 1/10 sửa nguồn; 4/5/6/8 thêm test; Task 3 bổ sung thông báo lỗi và sửa cleanup của test; Task 9 sửa test và đóng ống nguồn ở nhánh ngắt sớm. Task 2/7 kiểm chứng mã đã có. Không cần refactor liên package mới.

Task 1 giao với plan TC ở `escalation.py`: quét luôn độc lập nút tự cập nhật. Task 2 giao V4-1: chỉ kiểm lại, không áp patch cũ. Task 3 giữ sudo không tương tác theo quyết định điều phối, không thêm helper mật khẩu. Task 4–7 giao V2b/V2c: không thay hợp đồng đã ghép. Task 10 giao passkey D155: khi CLI bị đóng, giữ test mặc định API, thay test CLI bằng từ chối của lát passkey; không mở lại CLI để giữ test cũ.

## Chuẩn bị môi trường kiểm chứng

```bash
export PYTHONPATH="$PWD"
export UV_CACHE_DIR=/tmp/v5-uv-cache
export UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv'
export UV_NO_SYNC=1
```

Đường môi trường trên là máy đang viết plan; ở máy khác dùng `.venv` đã cài sẵn của worktree. Không đồng bộ/tải gói. Mỗi lệnh test bên dưới chạy sau khối này.

## Task 1: bs-2bd.1.27 — quét lý do trước cửa ghi escalation

**Files:** Modify `tram/giao_viec/escalation.py`, `tests/test_escalation.py`; Read `tram/giao_viec/xu_ly_viec.py`, `tram/nho/bi_mat.py`.

**Interfaces:** Consumes `quet(cac_chuoi: Iterable[str]) -> dict[str, int]`; giữ nguyên signature `tao_escalation(...) -> str | None`, idempotency và quan hệ blocks.

`_xet` chuyển nguyên `noi_dung` của `bao.bi`; `escalation_cau_hoi` chuyển nguyên `bao.can_hoi`. Cả hai hội tụ ở đây. Quét bản gốc trước `split`/`[:2000]`; không ghi nhóm khớp hay byte lý do vào log. Câu thay thế là hằng văn bản cố định. Không đụng sự kiện nguồn đã ghi và không tuyên bố đã làm sạch lịch sử.
- [ ] **Step 1 — thêm test nguyên văn.**
```diff
--- a/tests/test_escalation.py
+++ b/tests/test_escalation.py
@@ -74,3 +74,20 @@
     g, kho = moi(tmp_path)
     with pytest.raises(ValueError):
         tao(g, kho, ly_do="tu-che")
+
+
+@pytest.mark.parametrize("ly_do", ["agent-bi", "agent-can-hoi", "can-thao-tac-nguy-hiem"])
+@pytest.mark.parametrize("gop", [False, True])
+@pytest.mark.parametrize("noi_dung", ["password=gia-lap-chi-de-test", "x " * 2100 + "password=gia-lap-chi-de-test"],
+                         ids=["ngan", "sau-moc-cat"])
+def test_ly_do_co_bi_mat_van_tao_escalation_nhung_khong_chep(tmp_path, ly_do, gop, noi_dung):
+    g, kho = moi(tmp_path)
+    if gop:
+        tao(g, kho, ly_do=ly_do, nguon="truoc")
+    e = tao(g, kho, ly_do=ly_do, nguon="sau", cau_hoi=noi_dung)
+    esc = g.beads[e]
+    van_ban = esc.notes if gop else esc.description
+    assert "Nội dung có dấu hiệu bí mật đã được ẩn; Đại ca xem lại yêu cầu." in van_ban
+    assert "gia-lap-chi-de-test" not in repr(g.goi)
+    assert g.so_lan("tao") == 1
+    assert e in [p.depends_on_id for p in g.beads["hr-1"].phu_thuoc]
```
- [ ] **Step 2 — RED trên HEAD.**
```bash
tests/chan_host/chay.sh -q tests/test_escalation.py
```
Đã thấy 12 failed, 7 passed: assertion thiếu câu “Nội dung có dấu hiệu bí mật đã được ẩn; Đại ca xem lại yêu cầu.”. 12 ca chạy với scanner thật; test cũ giữ đường nội dung sạch/idempotency.
- [ ] **Step 3 — mã tối thiểu.**
```diff
--- a/tram/giao_viec/escalation.py
+++ b/tram/giao_viec/escalation.py
@@ -10,6 +10,7 @@
 from tram.cham_cot.luat_cung import LOAI_CHAN
 from tram.giao_viec.su_kien import da_co, ghi_mot_lan
 from tram.phieu.kho import KhoPhieu
+from tram.nho.bi_mat import quet
 
 NHAN = "tram:escalation"
 LY_DO = ("agent-bi", "can-thao-tac-nguy-hiem", "agent-can-hoi", "het-ngan-sach", "nhanh-bi-day",
@@ -49,7 +50,10 @@
     ma = ma_escalation(du_an, bead.id, ly_do, nguon)
     if da_co(kho, du_an, "escalation.tao", {"ma_thao_tac": ma}):
         return None
-    cau_hoi = " ".join((cau_hoi or CAU_HOI.get(ly_do, "")).split())[:2000]
+    cau_hoi = cau_hoi or CAU_HOI.get(ly_do, "")
+    if quet([cau_hoi]):
+        cau_hoi = "Nội dung có dấu hiệu bí mật đã được ẩn; Đại ca xem lại yêu cầu."
+    cau_hoi = " ".join(cau_hoi.split())[:2000]
     beads = bd.tat_ca()
     esc = next((b for b in beads if b.issue_type == "decision" and NHAN in b.labels
                 and f"bead_goc: {bead.id}" in b.description.splitlines()
```
- [ ] **Step 4 — GREEN và hồi quy.**
```bash
tests/chan_host/chay.sh -q tests/test_escalation.py tests/test_xu_ly_viec.py
```
Đã xanh trong lượt 109 passed cuối. Không có điều kiện nút TC trước lời gọi quét; D102/D111/D133 giữ nguyên.
- [ ] **Step 5 — bàn giao, không commit.** Kiểm diff, giữ đúng phạm vi task. Người điều phối QC rồi mới cân nhắc đóng bead; phiên này không ghi Beads, không commit/merge/push.

## Task 2: bs-2bd.1.25 — xác nhận V4-1 đã đủ ở mức mã

**Files:** Read `tram/tho/kiem_cong.py`, `tram/tho/kiem_am.py`, `tram/chu/kiem_cach_ly.py`, `tram/tho/khach.py`, `tram/api/tho_them.py`; Test `tests/test_kiem_khe_d54.py`, `tests/test_tham_do_principal.py`.

**Interfaces:** Consumes `KhachTram.kiem_am() -> DichKiemAm`; `cach_ly(..., dich, chay_td, xac_minh, chup) -> list[MucKiem]`. Không thêm route/hợp đồng.

- [ ] **Step 1 — giữ test hiện có nguyên văn; không thêm trùng.**
```python
"""D54 (bs-2bd.1.25): hai thăm dò "API Duyệt giả danh Đại ca" và "kết nối DB nghiệp vụ" của khe chạy trong
`tram tho kiem` dưới tài khoản QUẢN LÝ THỢ (sudoers `tram-tho → khe` có sẵn), đích lấy từ trạm qua `/api/tho/kiem-am`
(token máy). Phía trạm (`tram chu kiem-cach-ly` in [CHUYỂN]) ở `test_tham_do_principal.py`, `test_chu_tho.py`.
Không sudo, không mạng, không Keychain: tram-api trong bộ nhớ, `chay`/`xac_minh`/`chup` GIẢ."""
import json
import subprocess
from dataclasses import replace
from types import SimpleNamespace

import pytest

from api_gia import DAI_CA, LOGIN, MAY_B
from khach_gia import _TraLoi, khach_asgi
from test_kiem_cong import cau_hinh
from tho_api_gia import tao_tram
from tram.tho import kiem_cong
from tram.tho.cham_tham_do import mo_cong
from tram.tho.khach import DichKiemAm, KhachTram, LoiKhachTram
from tram.tho.kiem_am import KetQuaThamDo, chay_tham_do
from tram.tho.kiem_cong import cach_ly, dau_do_that

DICH = DichKiemAm(LOGIN, MAY_B, ("127.0.0.1:3306",))
API = "API Duyệt với header danh tính giả"


def test_tram_cap_dich_tu_cau_hinh_cua_chinh_no_qua_token_may(tmp_path, tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {db_nghiep_vu: ['127.0.0.1:3306']}\n")
    t = tao_tram(tmp_path)
    assert khach_asgi(t.app, t.token["B"]).kiem_am() == DICH                     # login + Origin đúng như trạm kiểm
    assert t.goi("GET", "/api/tho/kiem-am", may=None).status == 401
    for h in ({"Authorization": "Bearer sai"}, DAI_CA):                         # token sai; danh tính Đại ca không thay
        r = t.goi("GET", "/api/tho/kiem-am", may=None, headers=h)
        assert r.status == 401 and not {"dai_ca_login", "may_b", "db_nghiep_vu"} & set(r.json())
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {db_nghiep_vu: ['khong hop le']}\n")
    r = t.goi("GET", "/api/tho/kiem-am")
    assert r.status == 503 and r.json() == {"ly_do": "cach-ly-sai"}


@pytest.mark.parametrize("than", [{"dai_ca_login": "a@x\r\nX-Tram: 1", "may_b": "b", "db_nghiep_vu": []},
                                  {"dai_ca_login": "a@x", "may_b": "b/../c", "db_nghiep_vu": []},
                                  {"dai_ca_login": "a@x", "may_b": "b", "db_nghiep_vu": ["127.0.0.1"]},
                                  {"dai_ca_login": "a@x", "may_b": "b", "db_nghiep_vu": "127.0.0.1:1"}, []])
def test_khach_tu_choi_dich_sai_dang_truoc_khi_vao_argv(than):
    k = KhachTram("http://127.0.0.1:7700", "t", mo=lambda yc, timeout: _TraLoi(200, json.dumps(than).encode()))
    with pytest.raises(LoiKhachTram, match="sai dạng"):
        k.kiem_am()
    k = KhachTram("http://127.0.0.1:7700", "t", mo=lambda yc, timeout: _TraLoi(200, b'{"dai_ca_login": null, '
                                                                                 b'"may_b": null, "db_nghiep_vu": []}'))
    with pytest.raises(LoiKhachTram, match="sai dạng"):
        k.kiem_am()
    k = KhachTram("http://127.0.0.1:7700", "t", mo=lambda yc, timeout: _TraLoi(200, b'{"db_nghiep_vu": []}'))
    with pytest.raises(LoiKhachTram, match="sai dạng"):
        k.kiem_am()


def ghi(da):
    def chay_td(ds, *, boc, env, kill):
        da.append({"ds": ds, "argv": boc(["/bin/cat", "x"]), "env": env, "kill": kill})
        return [KetQuaThamDo(t.ten, True, "mã 1") for t in ds]
    return chay_td


def test_tho_kiem_chay_api_va_db_duoi_principal_khe_sau_uid(tmp_path):
    ch, da, xm = cau_hinh(tmp_path, ("user:tram-k-1",)), [], []
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", dich=lambda: DICH, chay_td=ghi(da),
                 xac_minh=lambda ten, boc, kill: xm.append((ten, len(da))) or 600, chup=lambda: [])
    assert [m.muc_do for m in ra] == ["xanh"] and xm == [("tram-k-1", 0)]                  # UID TRƯỚC thăm dò
    ds = {t.ten: t for t in da[0]["ds"]}
    assert da[0]["argv"][:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"] and set(da[0]["env"]) == {"PATH",
                                                                                                      "LANG"}
    assert da[0]["kill"].__self__.user == "tram-k-1"
    a = ds[API].argv
    assert a[:2] == ["/usr/bin/curl", "-q"]  # bỏ .curlrc của khe; env thăm dò chỉ PATH/LANG
    assert f"Tailscale-User-Login: {LOGIN}" in a and f"Origin: https://{MAY_B}" in a
    assert a[-1] == "http://127.0.0.1:7700/api/phe-duyet/kiem-am/kiem-am/duyet" and ds[API].kieu == "http"
    db = ds["kết nối DB nghiệp vụ 127.0.0.1:3306"]
    assert db.argv == ["/usr/bin/nc", "-z", "-G", "3", "127.0.0.1", "3306"] and db.doi_chung.func is mo_cong


def test_khong_lay_duoc_dich_thi_do_va_van_chay_phan_rut_gon(tmp_path):
    ch, da = cau_hinh(tmp_path, ("user:tram-k-1",)), []

    def hong():
        raise LoiKhachTram("tram-api trả 401 bi-mat")
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=hong, chay_td=ghi(da), xac_minh=lambda *a: 600,
                 chup=lambda: [])
    assert [m.muc_do for m in ra] == ["do"] and "không lấy được đích từ tram-api (LoiKhachTram)" in ra[0].chi_tiet
    assert "bi-mat" not in ra[0].chi_tiet and API not in [t.ten for t in da[0]["ds"]] and da[0]["ds"]


@pytest.mark.parametrize("ma, out, muc, ly", [(0, "403", "xanh", "thăm dò đạt"), (0, "200", "do", "API nhận yêu cầu"),
                                             (7, "000", "do", "không kết luận: không gọi được API"),
                                             (0, "404", "do", "không chứng minh từ chối quyền")])
def test_cham_api_giu_chuan_a_t6(tmp_path, ma, out, muc, ly):
    """Chuẩn V2b A-T6 qua `chay_tham_do` THẬT (chạy GIẢ; chỉ giữ thăm dò dương + API — đối chứng Keychain/file của
    phần rút gọn không chạy trong test): chỉ 401/403 là bị chặn; lỗi hạ tầng không thành "đạt"; không chép đầu ra."""
    def chay(argv, **kw):
        kq = (ma, out, "curl: bi-mat") if "/usr/bin/curl" in argv else (0, "", "")
        return subprocess.CompletedProcess(argv, *kq)

    def chay_td(ds, **kw):
        return chay_tham_do([t for t in ds if t.kieu in ("ok", "http")], chay=chay, **kw)
    ch = cau_hinh(tmp_path, ("user:tram-k-1",))
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=lambda: DichKiemAm(LOGIN, MAY_B, ()), chay_td=chay_td,
                 xac_minh=lambda *a: 600, chup=lambda: [])
    assert ra[0].muc_do == muc and ly in ra[0].chi_tiet and "bi-mat" not in ra[0].chi_tiet


def test_dau_do_that_lay_dich_tu_khach(monkeypatch):
    da = {}
    monkeypatch.setattr(kiem_cong, "cach_ly", lambda ch, du_an, **kw: da.update(kw) or [])
    khach = SimpleNamespace(ping=lambda: {}, du_an=lambda: [], kiem_am=lambda: DICH)
    dau_do_that(SimpleNamespace(), khach).cach_ly()
    assert da["dich"] is khach.kiem_am


@pytest.mark.parametrize("api, tren_b", [("http://127.0.0.1:7700", True), ("http://localhost:7700", True),
                                         ("https://may-b.tail.ts.net", False), ("https://127.0.0.1:7700", False)])
def test_chi_kiem_api_db_khi_tho_o_may_b(tmp_path, api, tren_b):
    """Review vòng 1 #5: đích (loopback, DB `127.0.0.1:…` của trạm) là theo máy B. Thợ ở máy khác (`tram_api` HTTPS)
    chưa có ánh xạ đích đã chứng minh, và 403 qua `tailscale serve` không chứng minh kênh ghi trên B đã tách → ĐỎ
    không kết luận, KHÔNG lấy đích, KHÔNG chạy curl/nc; phần rút gọn vẫn chạy."""
    ch, da, goi = replace(cau_hinh(tmp_path, ("user:tram-k-1",)), tram_api=api), [], []
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=lambda: goi.append(1) or DICH, chay_td=ghi(da),
                 xac_minh=lambda *a: 600, chup=lambda: [])
    kieu = {t.kieu for t in da[0]["ds"]}
    assert (goi == [1]) is tren_b and ({"http", "nc"} <= kieu) is tren_b and "ok" in kieu
    assert [m.muc_do for m in ra] == ["xanh" if tren_b else "do"]
    assert ("không kết luận: thợ không ở máy B" in ra[0].chi_tiet) is not tren_b and ch.tren_may_b is tren_b
```
- [ ] **Step 2 — kiểm độ nhạy, không phải lỗi HEAD.** Tạm đổi đúng dòng:
```python
kq = chay_td(ds, boc=p.boc, env={"PATH": ch.chay.path_cli, "LANG": "C.UTF-8"}, kill=p.kill_nhom)
```
Chạy `tests/chan_host/chay.sh -q tests/test_kiem_khe_d54.py::test_tho_kiem_chay_api_va_db_duoi_principal_khe_sau_uid`: 1 failed, `KeyError: 'API Duyệt với header danh tính giả'`.
- [ ] **Step 3 — giữ/khôi phục mã HEAD, không áp V4-1 lại.**
```python
def _api_db(ch: CauHinhTho, dich: Callable[[], DichKiemAm]) -> tuple[list[ThamDo], list[KetQuaThamDo]]:
    """(thăm dò API Duyệt + DB nghiệp vụ, lỗi) — đích lấy MỘT lần từ trạm cho mọi khe. Đích (loopback, DB của trạm)
    theo máy B: thợ máy khác chưa có ánh xạ đích đã chứng minh, 403 qua proxy không chứng minh kênh ghi tách → bỏ."""
    if not ch.tren_may_b:
        ly = "không kết luận: thợ không ở máy B (tram_api không phải loopback) — D54 lát này chỉ kiểm trên máy B"
        return [], [KetQuaThamDo("API Duyệt + DB nghiệp vụ", False, ly)]
    try:
        d = dich()
    except LoiKhachTram as e:
        return [], [KetQuaThamDo("API Duyệt + DB nghiệp vụ", False,
                                 f"không kết luận: không lấy được đích từ tram-api ({type(e).__name__})")]
    return tham_do_api_db(api=ch.tram_api, dai_ca_login=d.dai_ca_login, may_b=d.may_b, db=list(d.db_nghiep_vu)), []


def cach_ly(ch: CauHinhTho, du_an: list[str], *, goc: Path, goc_wt: Path, dich: Callable[[], DichKiemAm],
            chay_td=chay_tham_do, xac_minh=danh_tinh.xac_minh_uid, chup=chup_nhan) -> list[MucKiem]:
    ra, (them, loi_dich) = [], _api_db(ch, dich)
    for k in ch.khe:
        kid = ch.khe_id(k)
        try:
            p = principal_cua(ch, k, goc=goc, goc_wt=goc_wt, wt=None, ten="kiem")
        except ChuaCoPrincipal as e:
            ra.append(MucKiem(f"{kid} cách ly", "do", str(e)))
            continue
        uid, ly_do = _uid(p, xac_minh)
        if ly_do is not None:
            ra.append(MucKiem(f"{kid} cách ly", "do", ly_do))
            continue
        khac = [x for x in ch.khe if x.ten != k.ten]
        kho = [goc_wt.parent / "kho" / d / ".git" for d in du_an]
        ds = tham_do_khe(keychain=list(KEYCHAIN_CAM),
                         doc_cam=[goc / "tho" / ch.may_id / k.ten / "phieu.json", Path.home() / "Library/Keychains",
                                  *([ch.chay.thu_muc_tram / "su-kien.db"] if ch.chay.thu_muc_tram else [])],
                         ghi_cam=[*(goc / "hang-doi" / ch.may_id / x.ten for x in khac),
                                  *(x.thu_muc_cau_hinh for x in khac), *(g / "hooks" for g in kho)],
                         ghi_duoc=goc / "hang-doi" / ch.may_id / k.ten, ghi_tep_cam=[g / "config" for g in kho])
        kq = chay_td(ds + them, boc=p.boc, env={"PATH": ch.chay.path_cli, "LANG": "C.UTF-8"}, kill=p.kill_nhom)
        hong = [x for x in kq if not x.dat] + loi_dich + _tan_du(uid, chup)
        ra.append(MucKiem(f"{kid} cách ly", "do" if hong else "xanh",
                          "; ".join(f"{x.ten}: {x.chi_tiet}" for x in hong) or f"{len(kq)} thăm dò đạt"))
    return ra
```
- [ ] **Step 4 — GREEN và hồi quy.**
```bash
tests/chan_host/chay.sh -q tests/test_kiem_khe_d54.py
```
1 passed khi hoàn nguyên mutation; cả file có trong lượt 109 passed. Đủ phần mã D54: đích từ trạm, token máy, loopback, UID trước, kill principal, curl -q; phía trạm [CHUYỂN] không tính lỗi. Người điều phối có thể đóng phần triển khai bead sau QC; G5 vẫn cần bằng chứng chạy dưới tài khoản quản lý thợ thật, không suy ra từ fixture.
- [ ] **Step 5 — bàn giao, không commit.** Kiểm diff, giữ đúng phạm vi task. Người điều phối QC rồi mới cân nhắc đóng bead; phiên này không ghi Beads, không commit/merge/push.

## Task 3: bs-863.14 — primitive đã có, sudo không tương tác

**Files:** Read `tram/tho/kiem_am.py`, `tram/tho/kiem_cong.py`, `tram/chu/kiem_cach_ly.py`, `tram/kiem/vong_doi.py`, `tram/kiem/so_huu.py`, `docs/handovers/g3-bo-sung.sh`; Test `tests/test_kiem_am_p1.py`.

**Interfaces:** `chay_tham_do(..., kill, timeout=30, chay=chay_gioi_han)` giữ nguyên; `khoi_chay(..., chu)` sở hữu trước ngắt; không thêm giao diện truyền mật khẩu khi mẫu G3 chưa được xác định.

- [ ] **Step 1 — test primitive hiện có nguyên văn.**
```python
"""bs-863.14: thăm dò cách ly qua primitive P1 — hạn tuyệt đối, thu hồi cả cây bằng `kill` của principal; lỗi hạ tầng
(quá hạn, không khởi chạy, chưa thu hồi) KHÔNG BAO GIỜ thành "bị chặn"; dương hỏng → âm không kết luận. Chạy/kill GIẢ,
trừ một ca dùng `python -c` của chính user đang test (tự thu hồi đúng PID mình tạo)."""
import os
import signal
import subprocess
import sys
import time

from tram.kiem.vong_doi import LoiThuHoi, kill_cuc_bo
from tram.tho.kiem_am import ThamDo, chay_tham_do

DS = [ThamDo("keychain", ["/usr/bin/security"], "keychain"), ThamDo("đọc", ["/bin/cat"], "doc"),
      ThamDo("hợp lệ", ["/usr/bin/true"], "ok")]
LOI = {44: "The specified item could not be found in the keychain.", 1: "cat: x: Permission denied"}


def chay_gia(ket: dict, goi: list):
    def chay(argv, **kw):
        goi.append((argv, kw))
        r = ket[argv[-1]]
        if isinstance(r, BaseException):
            raise r
        return subprocess.CompletedProcess(argv, r, "", LOI.get(r, ""))
    return chay


def test_qua_p1_voi_kill_cua_principal_duong_chay_truoc():
    goi, kill = [], lambda g, s: None
    kq = chay_tham_do(DS, boc=lambda a: ["/usr/bin/sudo", "-n", *a], env={"PATH": "/x"}, kill=kill,
                      chay=chay_gia({"/usr/bin/security": 44, "/bin/cat": 1, "/usr/bin/true": 0}, goi))
    assert [k.dat for k in kq] == [True, True, True] and [k.ten for k in kq] == ["keychain", "đọc", "hợp lệ"]
    assert [a[-1] for a, _ in goi] == ["/usr/bin/true", "/usr/bin/security", "/bin/cat"]
    assert all(a[:2] == ["/usr/bin/sudo", "-n"] and kw["kill"] is kill and kw["timeout"] == 30
               and kw["env"] == {"PATH": "/x"} for a, kw in goi)


def test_loi_ha_tang_khong_bao_gio_la_bi_chan():
    kq = chay_tham_do(DS, boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay_gia(
        {"/usr/bin/security": subprocess.TimeoutExpired("x", 30), "/bin/cat": OSError("spawn"),
         "/usr/bin/true": 0}, []))
    assert [k.dat for k in kq] == [False, False, True] and all("không kết luận" in k.chi_tiet for k in kq[:2])


def test_duong_hong_thi_am_khong_chay_khong_xanh():
    goi = []
    kq = chay_tham_do(DS, boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay_gia({"/usr/bin/true": 1}, goi))
    assert [k.dat for k in kq] == [False, False, False] and len(goi) == 1 and "dương" in kq[0].chi_tiet


def test_chua_thu_hoi_duoc_thi_dung_khong_chay_tiep():
    goi = []
    kq = chay_tham_do(DS, boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay_gia(
        {"/usr/bin/true": 0, "/usr/bin/security": LoiThuHoi("x"), "/bin/cat": 1}, goi))
    assert [k.dat for k in kq] == [False, False, True] and [a[-1] for a, _ in goi] == ["/usr/bin/true",
                                                                                          "/usr/bin/security"]


def test_that_qua_han_va_kill_bi_tu_choi_van_tra_trong_han(tmp_path):
    pid = tmp_path / "pid"
    treo = ("import os, signal, sys, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            f"open({str(pid)!r}, 'w').write(str(os.getpid())); time.sleep(30)")

    def tu_choi(g, s):
        raise PermissionError
    t0 = time.monotonic()
    try:
        kq = chay_tham_do([ThamDo("treo", ["x"], "doc")], boc=lambda a: [sys.executable, "-c", treo],
                          env=dict(os.environ), kill=tu_choi, timeout=0.5)
        assert time.monotonic() - t0 < 10 and kq[0].dat is False and "không kết luận" in kq[0].chi_tiet
    finally:
        if pid.exists():
            try:
                os.kill(int(pid.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass
```
- [ ] **Step 2 — kiểm độ nhạy.** Tạm bỏ `kill=kill` ở lời gọi `chay` trong `chay_tham_do`; test `test_qua_p1_voi_kill_cua_principal_duong_chay_truoc` đỏ `KeyError: 'kill'`, 1 failed. Đây là mutation, HEAD đã sửa primitive.
- [ ] **Step 3 — giữ mã hiện hành dưới đây.**
```python
def chay_tham_do(ds: list[ThamDo], *, boc: Callable[[list[str]], list[str]], env: dict[str, str], kill: Kill,
                 timeout: float = 30, chay: Callable = chay_gioi_han) -> list[KetQuaThamDo]:
    ra: dict[int, KetQuaThamDo] = {}
    dung = None
    for i in sorted(range(len(ds)), key=lambda i: ds[i].kieu != "ok"):          # dương trước, giữ thứ tự trong nhóm
        t = ds[i]
        if dung is None and t.kieu != "ok" and not all(ra[j].dat for j in ra if ds[j].kieu == "ok"):
            dung = "không kết luận: thăm dò dương hỏng — principal/sandbox không chạy được lệnh hợp lệ"
        if dung is not None or not _doi_chung(t):
            ra[i] = KetQuaThamDo(t.ten, False, dung or "không kết luận: đối chứng hỏng — đích không có/không kiểm được")
            continue
        try:
            kq = chay(boc(t.argv), kill=kill, capture_output=True, text=True, timeout=timeout, env=env)
            kl, ly = cham(t.kieu, kq.returncode, (kq.stdout or "").strip(), kq.stderr or "")
        except LoiThuHoi:
            kl, ly = "khong-ket-luan", "không xác nhận thu hồi tiến trình thăm dò"
            dung = "không chạy: thăm dò trước chưa thu hồi được — kiểm principal"
        except (OSError, subprocess.SubprocessError, ValueError) as e:
            kl, ly = "khong-ket-luan", f"lỗi hạ tầng ({type(e).__name__})"
        ra[i] = KetQuaThamDo(t.ten, kl == "dat", ly if kl != "khong-ket-luan" else f"không kết luận: {ly}")
    return [ra[i] for i in range(len(ds))]
```
`kiem_cong.dang_nhap` cũng dùng `chay_gioi_han`, `kiem_cach_ly` chuyển `kill` từ principal kiểm lại cho `chay_td`. Giữ các primitive này. Quyết định điều phối vòng 1: tuyệt đối không nhận/ghi mật khẩu; giữ `sudo -n`, session riêng và stdin đóng. Áp thêm mã thông báo và test nguyên văn ở ghi chú vòng 1; không cần mẫu `mat_khau` của G3.
- [ ] **Step 4 — GREEN và hồi quy.**
```bash
tests/chan_host/chay.sh -q tests/test_kiem_am_p1.py
```
Tác giả báo mutation khôi phục: 1 passed; cả file xanh trong lượt 109 cũ. Bản sửa vòng 1 chưa chạy: ngoài sandbox cần đo NOPASSWD có/không, lỗi thoát nhanh và hướng dẫn `sudo -v`, quá hạn, Ctrl-C, thu hồi. Không có luồng nhập hay huỷ nhập mật khẩu trong ứng dụng.
- [ ] **Step 5 — bàn giao, không commit.** Kiểm diff, giữ đúng phạm vi task. Người điều phối QC rồi mới cân nhắc đóng bead; phiên này không ghi Beads, không commit/merge/push.

## Task 4: bs-863.16 — join hữu hạn

**Files:** Create `tests/test_v5_contract_4.py`; Read `tram/tho/theo_doi.py`; Test `tests/test_theo_doi_dung.py`.

**Interfaces:** TheoDoi.dung_lai(han=None), ket_thuc(han=None); chưa dừng ném LoiThuHoi, giữ phiếu.

- [ ] **Step 1 — test mới nguyên văn.**
```python
from types import SimpleNamespace

from tram.tho.theo_doi import TheoDoi


def test_join_nhan_han_huu_han():
    goi = []
    luong = SimpleNamespace(join=lambda timeout=None: goi.append(timeout), is_alive=lambda: False)
    td = TheoDoi(None, None, None)
    td._luong = luong
    td.dung_lai(han=2)
    assert len(goi) == 1 and goi[0] is not None and 0 <= goi[0] <= 2
```
- [ ] **Step 2 — RED bằng mutation vì HEAD đã sửa.** Tạm thay:
```python
self._luong.join(max(0.0, het - time.monotonic()))
# bằng
self._luong.join()
```
Chạy `tests/chan_host/chay.sh -q tests/test_v5_contract_4.py`: 1 failed, assertion `goi[0] is not None`. Tên file lúc đo mutation là `tests/test_v5_contracts.py`; đã tách theo task, nội dung hàm giữ nguyên và chạy lại tập cuối.
- [ ] **Step 3 — mã bảo vệ đã có, giữ nguyên.**
```python
    def _dung_den(self, het: float) -> None:
        with self._khoa_hen:
            self._het_hen = True
            if self._hen is not None:
                self._hen.cancel()
        self._ngung.set()
        if self._luong is not None:
            self._luong.join(max(0.0, het - time.monotonic()))
            if self._luong.is_alive():
                raise LoiThuHoi("luồng đọc hàng đợi chưa dừng trong hạn — dừng khe, giữ phiếu")

    def dung_lai(self, han: float | None = None) -> None:     # KHÔNG đọc lần cuối; chưa dừng → `LoiThuHoi`
        self._dung_den(time.monotonic() + (self.han_dung if han is None else han))

    def ket_thuc(self, han: float | None = None) -> None:
        """Dừng luồng nền rồi đọc lần cuối (dòng ghi ngay trước khi CLI thoát) — cả hai trong MỘT hạn."""
        het = time.monotonic() + (self.han_dung if han is None else han)
        self._dung_den(het)
        chay_trong_han(lambda: self.mot_luot(self._ngung_cuoi), het, ngung=self._ngung_cuoi,
                       ten=f"đọc hàng đợi lần cuối {self.pc.p.giao_id}", luong=self._luong_cuoi)
```
- [ ] **Step 4 — GREEN và hồi quy.**
```bash
tests/chan_host/chay.sh -q tests/test_v5_contract_4.py tests/test_theo_doi_dung.py
```
1 passed sau khôi phục mutation; test mới có trong lượt 109 passed. Phần mã của bead đã có; chỉ bổ sung chứng cứ hồi quy. Các ca tiến trình thật bị sandbox chặn không được tính là xanh.
- [ ] **Step 5 — bàn giao, không commit.** Kiểm diff, giữ đúng phạm vi task. Người điều phối QC rồi mới cân nhắc đóng bead; phiên này không ghi Beads, không commit/merge/push.

## Task 5: bs-863.17 — Codex login dưới principal khe

**Files:** Create `tests/test_v5_contract_5.py`; Read `tram/tho/do_may.py`; Test `tests/test_kiem_3b.py`.

**Interfaces:** dang_nhap_codex(pr, codex, thu_muc, *, path, chay=chay_gioi_han) -> tuple[bool | None, str]; pr đã qua UID ở kiem_3b.

- [ ] **Step 1 — test mới nguyên văn.**
```python
import subprocess
from pathlib import Path
from types import SimpleNamespace

from tram.tho.do_may import dang_nhap_codex


def test_codex_login_dung_principal_va_env_kin():
    goi = []
    kill = lambda *a: None
    pr = SimpleNamespace(boc=lambda a: ["principal-gia", *a], kill_nhom=kill)
    def chay(a, **kw):
        goi.append((a, kw))
        return subprocess.CompletedProcess(a, 0, "", "")
    assert dang_nhap_codex(pr, "/bin/codex-gia", Path("/cau-hinh-khe"), path="/bin", chay=chay)[0] is True
    a, kw = goi[0]
    assert a == ["principal-gia", "/bin/codex-gia", "login", "status"]
    assert kw["kill"] is kill and kw["timeout"] == 20
    assert kw["env"] == {"PATH": "/bin", "LANG": "C.UTF-8", "CODEX_HOME": "/cau-hinh-khe"}
```
- [ ] **Step 2 — RED bằng mutation vì HEAD đã sửa.** Tạm thay:
```python
chay(pr.boc([codex, "login", "status"]),
# bằng
chay([codex, "login", "status"],
```
Chạy `tests/chan_host/chay.sh -q tests/test_v5_contract_5.py`: 1 failed, assertion `argv bắt đầu bằng principal-gia`. Tên file lúc đo mutation là `tests/test_v5_contracts.py`; đã tách theo task, nội dung hàm giữ nguyên và chạy lại tập cuối.
- [ ] **Step 3 — mã bảo vệ đã có, giữ nguyên.**
```python
def dang_nhap_codex(pr, codex: str, thu_muc: Path, *, path: str, chay: Callable = chay_gioi_han
                    ) -> tuple[bool | None, str]:
    """(True | False | None = không kết luận, chi tiết) — `pr` là principal ĐÃ xác minh UID (người gọi). `LoiThuHoi`
    NỔI LÊN (review vòng 1 A05): người gọi phải thôi mọi thăm dò khác dưới principal này."""
    env = {"PATH": path, "LANG": "C.UTF-8", "CODEX_HOME": str(thu_muc)}
    try:
        s = chay(pr.boc([codex, "login", "status"]), kill=pr.kill_nhom, capture_output=True, text=True, timeout=20,
                 env=env)
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, f"không kết luận: không chạy được `codex login status` dưới principal ({type(e).__name__})"
    if s.returncode == 0:
        return True, "đã đăng nhập (`codex login status` mã 0, dưới principal của khe)"
    return False, (f"chưa đăng nhập (`codex login status` mã {s.returncode}) — Đại ca đăng nhập tay dưới principal "
                   f"của khe với CODEX_HOME={thu_muc}")
```
- [ ] **Step 4 — GREEN và hồi quy.**
```bash
tests/chan_host/chay.sh -q tests/test_v5_contract_5.py tests/test_kiem_3b.py
```
1 passed sau khôi phục mutation; test mới có trong lượt 109 passed. Phần mã của bead đã có; chỉ bổ sung chứng cứ hồi quy. Các ca tiến trình thật bị sandbox chặn không được tính là xanh.
- [ ] **Step 5 — bàn giao, không commit.** Kiểm diff, giữ đúng phạm vi task. Người điều phối QC rồi mới cân nhắc đóng bead; phiên này không ghi Beads, không commit/merge/push.

## Task 6: bs-863.18 — H1 stdin nguyên trạng

**Files:** Create `tests/test_v5_contract_6.py`; Read `tram/kiem/chay_gioi_han.py`; Test `tests/test_chay_gioi_han.py`.

**Interfaces:** chay_gioi_han(..., input=None, stdin=None, ...); input và stdin loại trừ trước spawn; người gọi sở hữu FD.

- [ ] **Step 1 — test mới nguyên văn.**
```python
from types import SimpleNamespace

import tram.kiem.chay_gioi_han as gh


def test_stdin_truyen_nguyen_va_khong_dong_cua_nguoi_goi(tmp_path, monkeypatch):
    goi = []
    p = SimpleNamespace(stdin=None, stdout=None, stderr=None, returncode=0)
    n = SimpleNamespace(p=p, ket_thu_hoi=True)
    def khoi(a, **kw):
        goi.append(kw["stdin"])
        kw["chu"].append(n)
        return n
    monkeypatch.setattr(gh, "_ong", lambda *a: (b"", b"", True))
    f = tmp_path / "vao"
    f.write_bytes(b"du-lieu-gia")
    with f.open("rb") as vao:
        assert gh.chay_gioi_han(["gia"], kill=lambda *a: None, timeout=1, stdin=vao, khoi=khoi).returncode == 0
        assert goi == [vao] and not vao.closed
```
- [ ] **Step 2 — RED bằng mutation vì HEAD đã sửa.** Tạm thay:
```python
vao = stdin if stdin is not None else
# bằng
vao = subprocess.DEVNULL if stdin is not None else
```
Chạy `tests/chan_host/chay.sh -q tests/test_v5_contract_6.py`: 1 failed, assertion `goi == [vao]`. Tên file lúc đo mutation là `tests/test_v5_contracts.py`; đã tách theo task, nội dung hàm giữ nguyên và chạy lại tập cuối.
- [ ] **Step 3 — mã bảo vệ đã có, giữ nguyên.**
```python
def chay_gioi_han(argv: list[str], *, kill: Kill, timeout: float, capture_output: bool = False, text: bool = False,
                  input=None, stdin=None, env=None, cwd=None, check: bool = False,
                  khoi: Callable = khoi_chay) -> subprocess.CompletedProcess:
    if not math.isfinite(timeout):
        raise ValueError("timeout phải hữu hạn")
    if input is not None and stdin is not None:
        raise ValueError("input và stdin loại trừ nhau")
    ten = [Path(str(argv[0])).name] if argv else []
    ong = subprocess.PIPE if capture_output else subprocess.DEVNULL
    if text and isinstance(input, str):
        input = input.encode()
    vao = stdin if stdin is not None else subprocess.PIPE if input is not None else subprocess.DEVNULL
    het, chu = time.monotonic() + timeout, []                            # hạn tuyệt đối tính TRƯỚC spawn
    try:
        try:
            n = khoi(list(argv), kill=kill, stdin=vao, stdout=ong, stderr=ong, env=env, cwd=cwd, chu=chu)
        except OSError as e:                    # `khoi_chay`: OSError chỉ khi Popen chưa tạo được tiến trình
            raise OSError(f"{ten}: không khởi chạy được ({type(e).__name__})") from None
        chu[:] = chu or [n]                     # `khoi` giả không tự ghi `chu`: nhận Nhom nó trả
        ra, loi, xong = _ong(n, input, het)
    except BaseException as e:
        _don(chu, ten, e)
        raise
    _don(chu, ten, None if xong else subprocess.TimeoutExpired(ten, timeout))
    if not xong:
        raise subprocess.TimeoutExpired(ten, timeout)
    if check and n.p.returncode:
        raise subprocess.CalledProcessError(n.p.returncode, ten)
    if text:
        ra, loi = (None if x is None else x.decode("utf-8", "replace") for x in (ra, loi))
    return subprocess.CompletedProcess(list(argv), n.p.returncode, ra, loi)
```
Đường gọi bản chép đã qua primitive, không viết lại:
```python
def _chay(argv: list[str], *, kill: Kill, timeout: float | None = None, **kw) -> subprocess.CompletedProcess:
    try:
        return chay_gioi_han(argv, kill=kill, capture_output=True, timeout=timeout or THOI_GIAN, **kw)
    except LoiThuHoi:                       # tick chỉ bắt OSError: chưa xác nhận thu hồi = bản chép không công nhận
        raise LoiBanChep("lệnh dưới tram-kiem: không xác nhận thu hồi cây tiến trình — không công nhận") from None
```
`ong_chep.chay_ong` đã giữ nguồn trong `chu` và finally thu hồi; nhận stdin là stdout của nguồn. Không gặt bằng communicate. Test OS `test_stdin_la_file_object_truyen_thang_khong_doc_vao_ram`, `test_stdin_ong_nguon_qua_han_thi_thu_hoi_khong_kem_du_lieu` và pipeline phải chạy ngoài sandbox; test giả ở đây không chứng nhận thu hồi OS.
- [ ] **Step 4 — GREEN và hồi quy.**
```bash
tests/chan_host/chay.sh -q tests/test_v5_contract_6.py tests/test_chay_gioi_han.py
```
1 passed sau khôi phục mutation; test mới có trong lượt 109 passed. Phần mã của bead đã có; chỉ bổ sung chứng cứ hồi quy. Các ca tiến trình thật bị sandbox chặn không được tính là xanh.
- [ ] **Step 5 — bàn giao, không commit.** Kiểm diff, giữ đúng phạm vi task. Người điều phối QC rồi mới cân nhắc đóng bead; phiên này không ghi Beads, không commit/merge/push.

## Task 7: bs-863.19 — Ctrl-C không bỏ lại con

**Files:** Read `tram/kiem/han_tong.py`, `tram/kiem/ngat.py`; Test `tests/test_han_tong_ngat.py`, `tests/test_so_huu_han_tong.py`.

**Interfaces:** chay_han_tong(argv, *, han, kill, dau, don, khoi, **kw) -> int; ngắt phát lại sau finally, don luôn sau thu hồi.

- [ ] **Step 1 — test có sẵn nguyên văn.**
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
```
- [ ] **Step 2 — mutation đỏ.** Tạm thay `sach = thu_hoi_con_lai(chu)` bằng `sach = True`. Chạy test trên: 4 failed, `assert ['don'] == ['thu', 'don']`. Không sửa HEAD theo mutation.
- [ ] **Step 3 — giữ mã đã sửa, không thêm except nuốt KeyboardInterrupt.**
```python
def chay_han_tong(argv: list[str], *, han: float, kill: Kill, dau: Path, don: Callable[[], bool],
                  khoi: Callable = khoi_chay, **kw) -> int:
    """Mã thoát của harness khi xong trong hạn VÀ dọn xác nhận; ngược lại ném (HetHanTong | LoiThuHoi). `don()` LUÔN
    chạy sau khi đã thử thu hồi — kể cả khi thu hồi không xác nhận — để gỡ lịch harness đã cài."""
    if not (math.isfinite(han) and han > 0):
        raise ValueError("hạn tổng phải hữu hạn, dương")
    dau.parent.mkdir(parents=True, exist_ok=True)
    chu, co_dau, ma, sach, xong = [], False, None, False, False
    try:
        with hoan():                            # tạo dấu + spawn: ngắt chỉ ném khi Nhom đã ở `chu` (finally thu hồi)
            try:
                os.close(os.open(dau, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
            except FileExistsError:
                raise LoiThuHoi(f"cổng đang đóng ({dau.name}): lượt trước chưa xác nhận dọn — không chạy") from None
            co_dau = True
            try:
                n = khoi(argv, kill=kill, stdin=subprocess.DEVNULL, chu=chu, **kw)
                chu[:] = chu or [n]             # `khoi` giả không tự ghi `chu`: nhận Nhom nó trả
            except OSError:
                if chu:
                    raise
                sach = True                     # Popen chưa tạo được tiến trình: không có gì để thu hồi
        ma = chu[0].cho(han) if chu else None
    finally:
        if co_dau:
            try:
                with hoan():                    # ngắt lần hai ném SAU khi thu hồi xong VÀ đã ghi kết quả
                    if chu:
                        sach = thu_hoi_con_lai(chu)
            finally:
                xong = _don(don) and sach
                if xong:
                    dau.unlink()
    if not chu:
        raise LoiThuHoi("không khởi chạy được harness")
    if ma is None:
        raise HetHanTong(f"harness quá hạn tổng {han:g} s — " + ("đã thu hồi và dọn" if xong else "CỔNG GIỮ ĐÓNG"))
    if not xong:
        raise LoiThuHoi("harness xong nhưng chưa xác nhận thu hồi/dọn — cổng giữ đóng")
    return ma
```
- [ ] **Step 4 — GREEN và hồi quy.**
```bash
tests/chan_host/chay.sh -q tests/test_han_tong_ngat.py
```
4 passed sau khôi phục; cả file xanh trong lượt 109. SIGTERM của CLI cha phải qua term_thanh_ngat hiện hành; không tuyên bố bảo đảm SIGKILL. Thu hồi chưa xác nhận hoặc don lỗi giữ dấu; ngắt không biến thành kết quả thành công.
- [ ] **Step 5 — bàn giao, không commit.** Kiểm diff, giữ đúng phạm vi task. Người điều phối QC rồi mới cân nhắc đóng bead; phiên này không ghi Beads, không commit/merge/push.

## Task 8: bs-2bd.1.24 — sidecar vừa bị SQLite unlink

**Files:** Create `tests/test_v5_sqlite_unlink.py`; Read `tram/su_kien/mo_an_toan.py`; Test `tests/test_siet_quyen.py`.

**Interfaces:** mo_da_kiem(Path, **kw) -> sqlite3.Connection; không đổi cấu trúc DB hay hợp đồng quyền.

- [ ] **Step 1 — test nguyên văn.**
```python
import os
import sqlite3

import pytest

from tram.su_kien import mo_an_toan as m


@pytest.mark.parametrize("duoi", ["-wal", "-shm"])
def test_ket_noi_khac_dong_xoa_sidecar_sau_open(tmp_path, monkeypatch, duoi):
    p = tmp_path / "kho.db"
    db = sqlite3.connect(p)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("CREATE TABLE mau (id INTEGER)")
    db.commit()
    that, thay = m._mo, []

    def mo(ten, dfd, tao):
        fd = that(ten, dfd, tao)
        if ten == p.name + duoi:
            assert fd is not None
            db.close()
            thay.append(os.fstat(fd).st_nlink)
        return fd

    monkeypatch.setattr(m, "_mo", mo)
    try:
        moi = m.mo_da_kiem(p)
        try:
            assert moi.execute("SELECT count(*) FROM mau").fetchone() == (0,)
        finally:
            moi.close()
        assert thay == [0]
    finally:
        db.close()
```
- [ ] **Step 2 — RED bằng dựng lại điều kiện cũ.** Tạm đổi `if st.st_nlink > 1:` thành `if st.st_nlink != 1:`. Chạy `tests/chan_host/chay.sh -q tests/test_v5_sqlite_unlink.py`: 2 failed, `LoiQuyenKho: kho SQLite có liên kết cứng — không đổi quyền, không mở`. SQLite thật xoá sidecar, không fake st_nlink.
- [ ] **Step 3 — giữ điều kiện HEAD nguyên văn.**
```python
if st.st_nlink > 1:                  # 0: -wal/-shm vừa bị kết nối khác đóng xoá — không phải liên kết
    raise LoiQuyenKho("kho SQLite có liên kết cứng — không đổi quyền, không mở")
```
- [ ] **Step 4 — GREEN và hồi quy.**
```bash
tests/chan_host/chay.sh -q tests/test_v5_sqlite_unlink.py tests/test_siet_quyen.py
```
2 passed sau khôi phục; cả file siet_quyen xanh trong lượt 109, gồm hardlink kho/WAL/SHM không chmod/không mở. Chỉ thêm test; không nới điều kiện symlink, UID, file thường hay đối chiếu inode kho chính.
- [ ] **Step 5 — bàn giao, không commit.** Kiểm diff, giữ đúng phạm vi task. Người điều phối QC rồi mới cân nhắc đóng bead; phiên này không ghi Beads, không commit/merge/push.

## Task 9: bs-2bd.1.29 — test Ctrl-C tại ranh giới sở hữu

**Files:** Modify `tests/test_ban_chep_pipeline_han.py`; Read `tram/giao_viec/ong_chep.py`, `tram/kiem/ngat.py`, `tram/kiem/vong_doi.py`, `tram/kiem/giu_xac.py`.

**Interfaces:** Giữ khoi_chay và chay_ong sản phẩm nguyên trạng; test giả Popen, bảng tiến trình và kill nhưng chạy hoan/Nhom/so_huu thật.

Test cũ đi qua chuẩn bị cây git và ba mkdir trước khi tới điểm tiêm SIGINT, còn fixture đặt THOI_GIAN=1.0; khi OS bận, phép thử có thể hỏng trước ranh giới đang muốn kiểm. Nó còn phụ thuộc giao tín hiệu thật qua raise_signal/handler môi trường. Đây là các cửa sổ phụ thuộc tải quan sát được từ mã, **chưa đủ bằng chứng kết luận nguyên nhân duy nhất** của “DID NOT RAISE”. Lần chạy nguyên trạng trong sandbox thực tế đỏ `LoiBanChep: ... không xác nhận thu hồi cây tiến trình`, chưa đến spawn nguồn. Không gọi kết quả đó là tái hiện đúng flake gốc.
- [ ] **Step 1 — test thay thế nguyên văn, chỉ thay hàm đích.**
```diff
--- a/tests/test_ban_chep_pipeline_han.py
+++ b/tests/test_ban_chep_pipeline_han.py
@@ -107,17 +107,53 @@
     assert chay(m, {"kiem.sh": "exit 0\n"}, kill=kill).loi == "cay-khac-nguon" and goi == [kill, kill]
 
 
-def test_ctrl_c_ngay_sau_khi_nguon_spawn_nguon_da_co_chu_va_bi_thu_hoi(ong, monkeypatch):
-    """R2-02: Ctrl-C THẬT ngay sau Popen của nguồn — hoãn, phát lại khi nguồn đã ở `chu`: thu hồi rồi mới ngắt."""
-    k, sha, wt, _ = ong
-    goi, that = [], cay_kiem.nguon_archive
+def test_ctrl_c_ngay_sau_khi_nguon_spawn_nguon_da_co_chu_va_bi_thu_hoi(tmp_path, monkeypatch):
+    """Tiêm ngắt tại ranh giới Popen bằng handler đồng bộ; không phụ thuộc git hay lịch chạy OS."""
+    import io
+    from tram.kiem.ngat import term_thanh_ngat
 
-    def popen(a, **kw):
-        goi.append(subprocess.Popen(a, **kw))
-        signal.raise_signal(signal.SIGINT)
-        return goi[-1]
-    monkeypatch.setattr(ong_chep, "nguon_archive", lambda *a, **kw: that(
-        *a, khoi=lambda x, **k: khoi_chay(x, popen=popen, **k), **kw))
-    with pytest.raises(KeyboardInterrupt):
-        chep_ban(k.kho, sha, wt, boc=lambda a: a)
-    assert goi[0].returncode is not None and not _song(goi[0].pid)
+    goi, chu_nguon = [], []
+
+    class P:
+        pid, returncode = 4242, None
+        stdin = stderr = None
+
+        def __init__(self):
+            self.stdout = io.BytesIO(b"archive-gia")
+
+        def wait(self, timeout=None):
+            if self.returncode is None:
+                raise subprocess.TimeoutExpired("nguon-gia", timeout)
+            return self.returncode
+
+        def poll(self):
+            return self.returncode
+
+    p = P()
+
+    def kill(pgid, sig):
+        assert pgid == p.pid
+        goi.append("thu-hoi")
+        p.returncode = -sig
+
+    def nguon(kho, commit, *, chu):
+        chu_nguon.append(chu)
+        def popen(a, **kw):
+            assert kw["start_new_session"] is True and chu == []
+            goi.append("spawn")
+            signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
+            return p
+        return khoi_chay(["nguon-gia"], kill=kill, chu=chu, popen=popen, chup=lambda: [])
+
+    def dich(*a, **kw):
+        pytest.fail("đích không được chạy sau ngắt ở nguồn")
+
+    monkeypatch.setattr(ong_chep, "nguon_archive", nguon)
+    try:
+        with term_thanh_ngat(), pytest.raises(KeyboardInterrupt):
+            ong_chep.chay_ong(tmp_path, "sha-gia", ["dich-gia"], chay=dich, han=1)
+        assert goi == ["spawn", "thu-hoi"]
+        assert len(chu_nguon[0]) == 1 and chu_nguon[0][0].p is p
+        assert chu_nguon[0][0].ket_thu_hoi is True and p.returncode == -signal.SIGTERM
+    finally:
+        p.stdout.close()
```
- [ ] **Step 2 — chứng minh test bắt đúng lỗi sở hữu.** Tạm đưa `chu.append(n)` ra ngoài `with hoan()` trong `khoi_chay`. Chạy test đích: 1 failed, `assert ['spawn'] == ['spawn', 'thu-hoi']`. Đây là mutation kiểm độ nhạy, không phải tái hiện triệu chứng chập chờn gốc.
- [ ] **Step 3 — hoàn nguyên primitive; mã sản phẩm giữ nguyên.**
```python
def khoi_chay(argv: list[str], *, kill: Kill, chu: list, popen: Callable = subprocess.Popen,
              chup: Callable[[], list[TienTrinh]] = chup_nhan, **kw) -> Nhom:
    """Hợp đồng `so_huu` mục 1: `Nhom` vào `chu` TRONG `hoan()`, trước mọi lối ra sau Popen; gốc không theo dõi được
    (`Goc.hong`) → `LoiThuHoi`, `Nhom` vẫn ở `chu` — người gọi thu hồi (không bao giờ xác nhận), cổng đóng."""
    if not isinstance(chu, list):
        raise TypeError("chu phải là list sở hữu của người gọi")
    kw["start_new_session"] = True
    with hoan():
        n = Nhom(popen(argv, **kw), kill=kill, chup=chup)
        chu.append(n)
    if n.goc.hong:
        raise LoiThuHoi("không theo dõi được gốc — tiến trình ở danh sách sở hữu của người gọi, chưa xác nhận thu hồi")
    return n
```
- [ ] **Step 4 — GREEN và hồi quy.**
```bash
tests/chan_host/chay.sh -q tests/test_ban_chep_pipeline_han.py::test_ctrl_c_ngay_sau_khi_nguon_spawn_nguon_da_co_chu_va_bi_thu_hoi
```
1 passed, không child thật, không sleep, không mở rộng timeout. Tiêm vào handler đang cài để ngắt chỉ phát lại sau chu.append. Các test pipeline khác vẫn giữ tích hợp archive/tar thật. Chưa đóng bead vì chưa tái hiện đúng flake gốc ngoài sandbox: điều phối phải chạy file pipeline đầy đủ và nhóm test tín hiệu với môi trường thật; nếu flake còn, thu handler SIGINT và ngat._muc tại lúc vào test, không tăng timeout.
- [ ] **Step 5 — bàn giao, không commit.** Kiểm diff, giữ đúng phạm vi task. Người điều phối QC rồi mới cân nhắc đóng bead; phiên này không ghi Beads, không commit/merge/push.

## Task 10: bs-78r.11 — tác nhân CLI cấp mã

**Files:** Create `tests/test_v5_cap_ma.py`; Modify `tram/chu/cap_ma.py`, `tram/phieu/ma_ghep.py`; Test `tests/test_ma_ghep.py`.

**Interfaces:** cap_ma_ghep(kho, may_id, *, luc, tac_nhan: str = "tram/api") -> MaGhep; CLI truyền tram/chu. Không đổi default KhoPhieu hay API khác.

- [ ] **Step 1 — test nguyên văn.**
```python
from contextlib import closing
from types import SimpleNamespace

from tram.chu.cap_ma import _cap_ma
from tram.phieu.kho import mo_kho_phieu
from tram.phieu.ma_ghep import cap_ma_ghep
from kho_phieu_gia import LUC


def test_cli_cap_ma_ghi_tac_nhan_chu(tram_home_tam, capsys):
    assert _cap_ma(SimpleNamespace(may_id="may-v5")) == 0
    capsys.readouterr()
    with closing(mo_kho_phieu()) as kho:
        assert kho.db.execute("SELECT tac_nhan FROM su_kien WHERE loai='may.cap_ma'").fetchall() == [("tram/chu",)]


def test_cap_ma_mac_dinh_van_la_api(tram_home_tam):
    with closing(mo_kho_phieu()) as kho:
        cap_ma_ghep(kho, "may-api", luc=LUC)
        assert kho.db.execute("SELECT tac_nhan FROM su_kien WHERE loai='may.cap_ma'").fetchall() == [("tram/api",)]
```
- [ ] **Step 2 — RED trên HEAD.** Chạy `tests/chan_host/chay.sh -q tests/test_v5_cap_ma.py`: 1 failed, 1 passed; `AssertionError: assert [('tram/api',)] == [('tram/chu',)]`. Test đọc sự kiện, không chỉ mock tham số.
- [ ] **Step 3 — bản vá nguyên văn.**
```diff
--- a/tram/phieu/ma_ghep.py
+++ b/tram/phieu/ma_ghep.py
@@ -46,7 +46,7 @@
     return db.execute("SELECT 1 FROM may_tho WHERE may_id = ? AND go_luc IS NULL", (may_id,)).fetchone() is not None
 
 
-def cap_ma_ghep(kho: KhoPhieu, may_id: str, *, luc: datetime) -> MaGhep:
+def cap_ma_ghep(kho: KhoPhieu, may_id: str, *, luc: datetime, tac_nhan: str = "tram/api") -> MaGhep:
     """Mã mới cho `may_id` (huỷ mã cũ chưa dùng của máy đó). Máy đang có token → ValueError (gỡ trước)."""
     if not MAY_RE.fullmatch(may_id):
         raise ValueError(f"may_id không hợp lệ: {may_id!r}")
@@ -60,7 +60,8 @@
                    (chuoi_gio(luc), may_id))
         db.execute("INSERT INTO ma_ghep (bam_ma, may_id, tao_luc, het_luc) VALUES (?,?,?,?)",
                    (_bam(ma), may_id, chuoi_gio(luc), het))
-        kho.ghi_su_kien(DU_AN_TRAM, "may.cap_ma", {"may_id": may_id, "het_luc": het}, luc=luc)
+        kho.ghi_su_kien(DU_AN_TRAM, "may.cap_ma", {"may_id": may_id, "het_luc": het},
+                        luc=luc, tac_nhan=tac_nhan)
     return MaGhep(f"{ma[:4]}-{ma[4:8]}-{ma[8:]}", may_id, het)
 
 
```
```diff
--- a/tram/chu/cap_ma.py
+++ b/tram/chu/cap_ma.py
@@ -12,7 +12,7 @@
     from tram.tho.do_may import TAG_THO
     try:
         with closing(mo_kho_phieu()) as kho:
-            mg = cap_ma_ghep(kho, args.may_id, luc=datetime.now(timezone.utc))
+            mg = cap_ma_ghep(kho, args.may_id, luc=datetime.now(timezone.utc), tac_nhan="tram/chu")
     except ValueError as e:
         print(e, file=sys.stderr)
         return 2
```
- [ ] **Step 4 — GREEN và hồi quy.**
```bash
tests/chan_host/chay.sh -q tests/test_v5_cap_ma.py tests/test_ma_ghep.py
```
Xanh trong lượt 109 passed. D155: đây chỉ sửa nhãn tác nhân cho CLI hiện hành; không thay kế hoạch đóng CLI cũ ở lát passkey, không thêm đường vượt passkey.
- [ ] **Step 5 — bàn giao, không commit.** Kiểm diff, giữ đúng phạm vi task. Người điều phối QC rồi mới cân nhắc đóng bead; phiên này không ghi Beads, không commit/merge/push.

## Kiểm chứng tổng và cổng còn đóng

Đã tạm áp bản vá/test, chạy qua runner; tập chọn lọc cuối **109 passed in 12.57s**, 0 dòng chặn mới, 0 điểm mù, 22 push giả lập (không push thật). Tập gồm escalation/xử lý việc, D54, primitive thăm dò, theo dõi, Codex, ngắt hạn tổng, ba test hợp đồng mới, SQLite, cấp mã, kiểm độ dài và test Ctrl-C mới.

Lệnh tập chọn lọc:

```bash
tests/chan_host/chay.sh -q tests/test_escalation.py tests/test_xu_ly_viec.py tests/test_kiem_khe_d54.py tests/test_kiem_am_p1.py tests/test_theo_doi_dung.py tests/test_kiem_3b.py tests/test_han_tong_ngat.py tests/test_v5_contract_4.py tests/test_v5_contract_5.py tests/test_v5_contract_6.py tests/test_v5_sqlite_unlink.py tests/test_v5_cap_ma.py tests/test_ma_ghep.py tests/test_siet_quyen.py tests/test_do_dai_ma.py tests/test_ban_chep_pipeline_han.py::test_ctrl_c_ngay_sau_khi_nguon_spawn_nguon_da_co_chu_va_bi_thu_hoi
```
Toàn bộ phải chạy lại ngoài sandbox sau khi áp plan:

```bash
tests/chan_host/chay.sh -q
```

Lượt toàn bộ ban đầu bị dừng sau 10 failed, 140 passed (87.60s); lỗi bản chép không xác nhận thu hồi, 0 dòng chặn. Lượt này dùng import checkout chính (HEAD cùng mốc), không dùng làm chứng cứ bản vá. Lượt cuối có PYTHONPATH đúng worktree: `tests/chan_host/chay.sh -q --maxfail=1` → **1 failed, 139 passed in 18.46s**, lỗi `tests/test_ban_chep.py::test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau` ném `LoiBanChep: lệnh dưới tram-kiem: không xác nhận thu hồi cây tiến trình — không công nhận`, 0 dòng chặn mới; không có baseline toàn bộ xanh trong phiên. Không bỏ/xfail các ca bị OS chặn. Frontend không đổi nên không chạy frontend.

Người điều phối phải bổ sung: H1 FD thật/ống thật; thu hồi dưới đúng UID, ps/sysctl và kill bị từ chối; SIGINT/SIGTERM ở CLI cha; join kẹt I/O vẫn giữ phiếu; D54 API giả danh và DB dưới quản lý thợ trên máy B; sudo thiếu quyền không hỏi mật khẩu, báo hướng dẫn rồi thoát. Không suy rộng unit test thành cổng G3/G4/G5/G7 đạt.

## Kiểm tra tính áp dụng của plan

Đã hoàn nguyên 10 file tạm về HEAD rồi lấy đúng khối `diff` và mã file mới trong tài liệu này để áp lại. `git apply --check` đạt; 10 file dựng lại khớp từng byte với bản đã kiểm. Lượt chạy sau áp lại: **109 passed in 11.65s**, 0 dòng chặn mới, 0 điểm mù, 22 push giả lập. `git diff --check` đạt. RED nguyên trạng chạy lại với PYTHONPATH đúng: Task 1 **12 failed, 7 passed → 19 passed**; Task 10 **1 failed, 1 passed → 2 passed**.

Đây là báo cáo của tác giả cho bản cũ, không chứng minh bản sửa vòng 1 hay triệu chứng gốc Task 9. Người điều phối cần áp plan đã sửa trước khi chạy các test mới. Báo cáo vòng review này là `REVIEW-CODEX-v5-vong1.md`; reviewer chỉ sửa plan và báo cáo đó, không áp nguồn/test.

## Quyết định điều phối đã nhận — không hỏi lại

1. Giữ `sudo -n` qua primitive có sở hữu/hạn. Nếu cần mật khẩu, báo lỗi rõ hướng dẫn chạy `sudo -v` trong Terminal rồi chạy lại; tuyệt đối không đọc/ghi mật khẩu. Không sửa sudoers, không đảm bảo cache từ Terminal dùng được trong session con; nếu vẫn lỗi thì giữ đỏ, người vận hành kiểm quyền đã cấp.
2. Điều phối tự chạy Ctrl-C ngoài sandbox. Đây là cổng OS, không phải thiếu sót thiết kế của plan. Không tăng timeout để che lỗi.

## Ghi chú triển khai — review vòng 1 (thắng phần thân)

Reviewer chỉ suy luận RED/GREEN từ mã, không chạy. Giữ các test/patch Task 1, 2, 4–8, 10;
Task 3 và 9 áp các bổ sung dưới đây. Các con số 54/109 và kết quả apply trong phần thân là lịch sử
của tác giả, không phải kết quả của bản này. Không ghi đè nguồn/test khi đang review tài liệu.

### R1-01 — Task 3: thông báo sudo ở cả bước UID và bước chạy

**Files bổ sung:** Modify `tram/tho/kiem_am.py`, `tram/tho/kiem_cong.py`,
`tram/chu/kiem_cach_ly.py`, `tests/test_kiem_am_p1.py`; Create `tests/test_v5_sudo_khong_tuong_tac.py`.

Không suy ra “sai mật khẩu” chỉ từ mã 1: lệnh con cũng có thể trả mã 1. Hiện bước dò UID bỏ đầu ra,
nên thông báo phải có điều kiện “Nếu sudo cần mật khẩu”, giữ lý do gốc cố định. Không đọc stderr để
phân loại, không thêm preflight `sudo`, không đưa mật khẩu vào stdin/argv/env. Nối hướng dẫn ở nhánh
không đạt của thăm dò, UID thất bại và lệnh trạng thái thất bại. Nhánh xanh giữ nguyên.

**RED:** tạo nguyên file test sau. Trên HEAD các nhánh lỗi thiếu `sudo -v`; ca thành công đã xanh.
Chạy file này qua runner trước khi sửa nguồn, sau đó chạy lại cùng các file hồi quy cuối mục.

```python
import subprocess

import pytest

from test_kiem_cong import cau_hinh
from tram.chu.kiem_cach_ly import kiem_cach_ly
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.khach import DichKiemAm
from tram.tho.kiem_am import ThamDo, chay_tham_do
from tram.tho.kiem_cong import cach_ly, dang_nhap
from tram.tho.principal import doc_principal


def kiem_loi(chuoi):
    assert "sudo -v" in chuoi and "Terminal" in chuoi
    assert "Nếu sudo cần mật khẩu" in chuoi and "GIA_LAP_KHONG_DUOC_IN" not in chuoi


def cam(*a, **kw):
    pytest.fail("không được chạy tiếp sau lỗi UID")


@pytest.mark.parametrize("loi", [LoiDanhTinh, LoiThuHoi])
def test_uid_loi_huong_dan_va_khong_chay_tiep(tmp_path, tram_home_tam, loi):
    def xm(*a):
        raise loi("GIA_LAP_KHONG_DUOC_IN")
    ch = cau_hinh(tmp_path, ("user:tram-k-1",))
    muc, ly = dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, xac_minh=xm, chay=cam)
    assert muc == "do"
    kiem_loi(ly)
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, xac_minh=xm, chay_td=cam, chup=cam,
                 dich=lambda: DichKiemAm("dai-ca@x", "b.ts.net", ()))
    assert len(ra) == 1 and ra[0].muc_do == "do"
    kiem_loi(ra[0].chi_tiet)
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {tram_kiem: user:tram-kiem}\n")
    van_ban, ma = kiem_cach_ly([], xac_minh=xm, chay_td=cam)
    assert ma == 1
    kiem_loi(van_ban)


@pytest.mark.parametrize("ket", [0, 1, OSError, LoiThuHoi])
def test_lenh_trang_thai_khong_nhan_mat_khau(tmp_path, ket):
    goi = []
    ch = cau_hinh(tmp_path, ("user:tram-k-1",))
    def chay(argv, **kw):
        goi.append((argv, kw))
        if isinstance(ket, type):
            raise ket("GIA_LAP_KHONG_DUOC_IN")
        return subprocess.CompletedProcess(argv, ket, "GIA_LAP_KHONG_DUOC_IN", "GIA_LAP_KHONG_DUOC_IN")
    muc, ly = dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay, xac_minh=lambda *a: 600)
    assert muc == ("xanh" if ket == 0 else "do")
    argv, kw = goi[0]
    assert len(goi) == 1 and argv[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"]
    assert kw["timeout"] == 30 and kw["kill"].__self__.user == "tram-k-1"
    assert set(kw["env"]) == {"PATH", "LANG", "CLAUDE_CONFIG_DIR"}
    assert "input" not in kw and "stdin" not in kw and "-S" not in argv
    if ket == 0:
        assert "sudo -v" not in ly and "GIA_LAP_KHONG_DUOC_IN" not in ly
    else:
        kiem_loi(ly)


def test_sudo_tu_choi_tham_do_duong_khong_thanh_bi_chan():
    goi = []
    p = doc_principal("user:tram-k-1")
    def chay(argv, **kw):
        goi.append((argv, kw))
        return subprocess.CompletedProcess(argv, 1, "GIA_LAP_KHONG_DUOC_IN", "sudo: a password is required")
    ds = [ThamDo("âm", ["/bin/cat", "gia"], "doc"), ThamDo("dương", ["/usr/bin/true"], "ok")]
    ra = chay_tham_do(ds, boc=p.boc, env={"PATH": "/bin", "LANG": "C.UTF-8"}, kill=p.kill_nhom, chay=chay)
    assert len(goi) == 1 and goi[0][0][-1] == "/usr/bin/true"
    assert goi[0][0][:2] == ["/usr/bin/sudo", "-n"] and goi[0][1]["timeout"] == 30
    assert goi[0][1]["kill"].__self__ is p and all(not r.dat for r in ra)
    kiem_loi(ra[1].chi_tiet)
    assert "không kết luận" in ra[0].chi_tiet and "GIA_LAP_KHONG_DUOC_IN" not in repr(ra)
```

**GREEN — thay chính xác các đoạn, không thay toàn file bằng đoạn trích.**

Trong `tram/tho/kiem_am.py`, đặt hằng sau khối import, trước `HOOK`:

```python
HUONG_DAN_SUDO = (" Nếu sudo cần mật khẩu, người vận hành chạy `sudo -v` trong Terminal rồi chạy lại. "
                  "Nếu vẫn lỗi, kiểm quyền sudo đã cấp; trạm không nhận hay lưu mật khẩu.")
```

Trong `chay_tham_do`, ngay trước dòng gán `ra[i] = KetQuaThamDo(t.ten, kl == "dat", ...)`, thêm:

```python
        ly += HUONG_DAN_SUDO if kl != "dat" else ""
```

Trong `tram/tho/kiem_cong.py`, thêm import (giữ import từ `kiem_am` hiện có):

```python
from tram.tho.kiem_am import HUONG_DAN_SUDO
```

Thay toàn hàm `_uid` bằng:

```python
def _uid(p, xac_minh) -> tuple[int | None, str | None]:
    """Lỗi UID/thu hồi: không chạy thêm; chỉ hướng dẫn có điều kiện, không chép ngoại lệ."""
    try:
        return xac_minh(p.user, p.boc, p.kill_nhom), None
    except (danh_tinh.LoiDanhTinh, LoiThuHoi) as e:
        ly = ("UID: không xác nhận thu hồi tiến trình dò — kiểm principal" if isinstance(e, LoiThuHoi)
              else "UID thực của principal chưa chứng minh — không chạy thăm dò")
        return None, ly + HUONG_DAN_SUDO
```

Trong `dang_nhap`, thay từ `except LoiThuHoi:` đến hết hàm bằng:

```python
    except LoiThuHoi:
        return "do", "không xác nhận thu hồi tiến trình lệnh trạng thái — kiểm principal" + HUONG_DAN_SUDO
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return "do", f"không chạy được lệnh trạng thái: {type(e).__name__}" + HUONG_DAN_SUDO
    return ("xanh", "đã đăng nhập (lệnh chờ S2 xác nhận)") if kq.returncode == 0 else (
        "do", "chưa đăng nhập / lỗi" + HUONG_DAN_SUDO)
```

`kiem_cong.py` từ 118 thành 119 dòng theo phép đếm thay đoạn; không cần tách module.
Trong `tram/chu/kiem_cach_ly.py`, thêm import:

```python
from tram.tho.kiem_am import HUONG_DAN_SUDO
```

Thay duy nhất dòng dựng `pr = ValueError(...)` trong nhánh lỗi xác minh UID bằng:

```python
                pr = ValueError(f"UID thực chưa chứng minh ({type(e).__name__}) — không chạy thăm dò"
                                + HUONG_DAN_SUDO)
```

Hồi quy sau áp: `tests/chan_host/chay.sh -q tests/test_v5_sudo_khong_tuong_tac.py tests/test_kiem_am_p1.py tests/test_kiem_cong.py tests/test_tham_do_principal.py tests/test_kiem_khe_d54.py tests/test_chu_tho.py tests/test_do_dai_ma.py`.
Chỉ khi runner thật báo xanh mới ghi số test. UID vẫn phải chứng minh trước probe, không cấp quyền mới.

### R1-02 — Task 3: test quá hạn phải giữ handle con, cleanup không dựa file PID

Test thật cũ chỉ kill khi con kịp ghi file và không wait/gặt; nếu child chưa ghi file thì bị bỏ lại.
Trong `tests/test_kiem_am_p1.py`, thay toàn hàm
`test_that_qua_han_va_kill_bi_tu_choi_van_tra_trong_han` bằng mã sau (các import trong hàm là đầy đủ):

```python
def test_that_qua_han_va_kill_bi_tu_choi_van_tra_trong_han():
    from functools import partial
    from tram.kiem.chay_gioi_han import chay_gioi_han
    from tram.kiem.vong_doi import khoi_chay

    cac_chu = []
    treo = "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)"

    def khoi(argv, **kw):
        cac_chu.append(kw["chu"])
        return khoi_chay(argv, **kw)

    def tu_choi(g, s):
        raise PermissionError

    t0 = time.monotonic()
    try:
        kq = chay_tham_do([ThamDo("treo", ["x"], "doc")], boc=lambda a: [sys.executable, "-c", treo],
                          env=dict(os.environ), kill=tu_choi, timeout=0.5,
                          chay=partial(chay_gioi_han, khoi=khoi))
        assert cac_chu and len(cac_chu[0]) == 1
        assert time.monotonic() - t0 < 10 and not kq[0].dat and "không kết luận" in kq[0].chi_tiet
    finally:
        for chu in cac_chu:
            for n in chu:
                if n.p.returncode is None:
                    n.p.kill()
                n.p.wait(timeout=5)
                n.goc.gat()
```

Con này chỉ ngủ, không sinh hậu duệ. Handle `Popen` do chính test tạo được giữ cả khi `khoi_chay`
ném sau đăng ký; cleanup chỉ dừng con đó, chờ hữu hạn, không tra hay kill theo tên/file PID.
Đây là sửa vệ sinh test, không dựng mutation sản phẩm. Reviewer không chạy ca OS này.

### R1-03 — Task 9: phát lại giả đồng bộ và kiểm ống đóng trước cleanup của test

Giữ diff Task 9 làm bước đầu; sau đó trong hàm test mới, ngay sau import `term_thanh_ngat`, thêm:

```python
    from tram.kiem import ngat
```

Ngay sau `monkeypatch.setattr(ong_chep, "nguon_archive", nguon)`, trước `try:`, thêm:

```python
    monkeypatch.setattr(ngat.signal, "raise_signal", lambda so: signal.getsignal(so)(so, None))
```

`hoan._khoi_phuc` vẫn chạy thật và khôi phục handler trước phát lại; chỉ thay giao tín hiệu của OS.
Không có SIGINT thật, fake PID chỉ vào `kill` giả. Các ca tín hiệu thật vẫn nằm ở cổng điều phối.
Ngay sau assertion `ket_thu_hoi is True and p.returncode == -signal.SIGTERM`, thêm:

```python
        assert p.stdout.closed
```

Giữ `finally: p.stdout.close()` để dọn tài nguyên test nếu assertion đỏ. Assertion phải nằm TRƯỚC
finally đó. Trên HEAD đây là RED thực: `nguon_archive` ném ngắt trước phép gán `nguon`, bỏ qua
finally trong cùng; finally ngoài chỉ thu hồi, chưa đóng ống trong `chu`.

**GREEN:** thêm vào import của `tram/giao_viec/ong_chep.py`:

```python
from contextlib import suppress
from tram.kiem.ngat import hoan
```

Thay khối finally ngoài cùng của `chay_ong` (ngay trước `return ma, r.returncode`) bằng:

```python
    finally:
        with hoan():
            try:
                for n in chu:
                    with suppress(OSError):
                        n.p.stdout.close()
            finally:
                if chu and not thu_hoi_con_lai(chu) and not ngat:
                    raise loi("git archive: nguồn của ống CHƯA xác nhận thu hồi "
                              "(thu hồi CHƯA) — không công nhận") from None
```

Giữ finally đóng ống bên trong hiện hành: khi nguồn đã trả, lỗi đóng ống vẫn đi đường lỗi cũ.
Đóng lần nữa là idempotent với ống của Popen; lỗi OSError ở dọn dự phòng không chặn thu hồi.
Ngắt trong lúc đóng được hoãn tới sau thu hồi. Không wait/communicate mới, không thêm timeout,
không gặt sớm, không gửi tín hiệu ngoài danh sách sở hữu. Bản vá chỉ quản lý FD của nguồn do ta tạo.

**Kiểm độ nhạy sau GREEN:** (1) bỏ khối đóng dự phòng → assertion `p.stdout.closed` đỏ;
(2) đưa `chu.append(n)` ra ngoài `hoan()` → thiếu `thu-hoi` và danh sách sở hữu rỗng.
Hoàn nguyên từng mutation trước ca tiếp theo. Không cần tái hiện flake cũ để chấp nhận thiết kế test này.

**Hồi quy tương lai:** chạy test đích Task 9, rồi
`tests/chan_host/chay.sh -q tests/test_ban_chep_pipeline_han.py tests/test_ong_chep_uu_tien.py tests/test_so_huu_han_tong.py tests/test_han_tong_ngat.py tests/test_do_dai_ma.py`.
Các ca pipeline thật do điều phối chạy ngoài sandbox; giữ kiểm ưu tiên lỗi nguồn, cổng đóng và không lộ byte môi trường.

### Phạm vi và cổng kết thúc sau review

Các khối giữ nguyên ở Task 2/4–8 là mô tả mã hiện hành, không phải file thay thế hoàn chỉnh.
Các khối thay đoạn R1-01/R1-03 là mã bổ sung hoàn chỉnh; không áp lại hàm cũ Task 3/9 sau chúng.
Task 9 nay Modify cả `tram/giao_viec/ong_chep.py`, không còn là task chỉ sửa test.
Tập chọn lọc lịch sử phải thêm `tests/test_v5_sudo_khong_tuong_tac.py`; toàn bộ vẫn chạy qua runner.
Không ghi nhận cổng đạt, không đóng bead dựa vào review tĩnh. Số test toàn bộ chưa xác minh.
Không còn câu hỏi mật khẩu hay quyền chạy Ctrl-C cần hỏi Đại ca ở vòng này.


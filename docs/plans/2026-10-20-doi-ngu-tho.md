# Hai thợ Claude trên máy B — Implementation Plan

> **Cho agent thực hiện:** dùng kỹ năng `executing-plans`, làm tuần tự Task 1–9.
> **Trạng thái:** ĐẠT để code sau review vòng 3; C1/C2 đã giải, tắt giao giữ kênh nhận máy A. Chưa được chạy thật.
> QĐ1–QĐ4 = A, QĐ5 = B đã chốt; không phải chờ chốt lại các quyết định này. Chưa được chạy thật.
> Phiên review chỉ sửa tài liệu; rehearsal trong bản sao tạm, không sửa `tram/` của worktree, không commit/bd/push.

**Goal:** hai khe `B/claude-1`, `B/claude-2` hiện đúng trên Đội ngũ và nhận mọi việc đủ điều kiện
của ben-station qua code → kiểm lại Uq → QC khác khe. Không giới hạn một bead; HR và tự merge/deploy tắt.

**Architecture:** dùng user/Keychain/ACL/launchd của macOS, một quản lý thợ hiện có. Đăng ký B
không đi qua đăng ký từ xa. Khe gửi bản sửa qua hàng đợi sẵn có; quản lý chốt commit sau thu hồi,
giữ metadata Git và cấu hình phiếu ngoài quyền ghi của khe. Trạm giữ quyền GitHub, thợ đọc kho cục bộ.
Không thêm dịch vụ nền hoặc sổ chứng nhận phải đánh dấu tay.

**Tech Stack:** Python 3.12 + stdlib, PyYAML/pytest hiện có, Git, Claude CLI, macOS Keychain/ACL/launchd.
Không thêm dependency. Runtime thợ dùng bản sao mã đã ghép và bundle root đã cài cho Uq ở `/Users/Shared/tram-tho-code`.

**Spec:** [proposal](../../openspec/changes/doi-ngu-tho/proposal.md),
[hành vi](../../openspec/changes/doi-ngu-tho/specs/doi-ngu-tho/spec.md),
[design](../../openspec/changes/doi-ngu-tho/design.md),
[năm quyết định](../../openspec/changes/doi-ngu-tho/QUYET-DINH.md).

**Nền:** ban đầu `19a86c0`; vòng 3 áp lại trên HEAD `c73248d` (đã ghép main `d149183`),
nhánh `spec/doi-ngu-tho`. Nguồn trạng thái: lời Đại ca và log phiên 20/10,
bao gồm cập nhật tối về reboot và disable thợ. Không dùng số test hay tình trạng máy của nhánh bối cảnh
làm kết quả mới. Bead chưa gắn theo lệnh cấm `bd` của phiên này.

## Global Constraints

- Hai khe đầu là `B/claude-1`, `B/claude-2`, chạy bằng `tram-khe1`, `tram-khe2`, khác UID.
- QĐ1–QĐ4 = A, QĐ5 = B đã được Đại ca chốt. QĐ2 thu hẹp “không credential”; QĐ3 giao quản lý chốt commit.
  Cần cập nhật ADR/tài liệu sở hữu ở phiên triển khai; quyết định thiết kế không cấp phép chạy thật.
- Rehearsal dùng bản sao tạm của HEAD, test qua runner và dependency có sẵn (bundle root + `TRAM_KIEM_DA_CHUAN_BI=1`, offline).
  Kết quả đo thật ở cuối plan; lỗi sandbox được tách khỏi lỗi mã. Không chép kết quả dự kiến thành bằng chứng.
- Trước code: chạy baseline, ghi số thật; sau từng task: test task + hồi quy; cuối: cả suite và QC nguyên văn.
  Chỉ `tests/chan_host/chay.sh`; Git/CLI/HTTP/Keychain/sudo/launchd đều giả trong test, 0 dòng chặn mới.
- `tram/`: file ≤120 dòng, dòng ≤120 ký tự Unicode. Không thêm ngoại lệ hoặc nén nhiều lệnh lên một dòng.
- Mã dưới đây nguyên văn: Create chép trọn; Modify là unified diff theo thứ tự task. Có file xuất hiện nhiều
  task vì các bước nối tiếp, không áp một bản vá sau lên HEAD mà bỏ bước trước.
- Không sửa `docs/CURRENT_STATE.md`, không tạo bàn giao trong `docs/handovers/`, không code trong phiên soạn.
- Không thêm quyền root cho quản lý thợ. Lệnh sudo ở phần chạy thật do Đại ca gọi từ Terminal.app theo từng cổng.
- Không cài lại Uq, không đổi hồ sơ kiểm, không sửa passkey, không thêm Codex/HR hoặc bật tự merge/deploy.
- Không mật khẩu/token/OAuth trong argv, YAML, file thường, log, prompt hay env của CLI; Keychain mã hoá là kho giữ
  bí mật đã được phép. Native CLI có thể lưu khác theo bản: kiểm ở R2; fallback credential file là S2 đỏ.
- Thời hạn và lỗi theo design §7. Thất bại/không rõ thì dừng, giữ phần đã làm; không coi thoát 0 là đủ bằng chứng OS.
- Khe chỉ ghi cây mã và append hàng đợi. Quản lý giữ Git, settings/MCP; không cấp ghi objects/refs chung.
- Không giết theo tên, không tự gỡ estop/mở cổng, không viết lịch. Dùng bộ thu hồi/loại tiến trình Apple hiện có.
- Không chạy script bên dưới ngay từ nhánh spec. Sau code/QC/ghép mới có các file công cụ và lệnh mới.

## Bảng G

G trong bảng này thuộc plan, không thay số G0–G7 của sổ tay cũ.

| G | Điều bảo đảm | Task / bằng chứng offline | Bằng chứng thật |
|---|---|---|---|
| G1 | Khe 2 riêng, cài giữ tắt, Uq giữ nguyên | 1, sổ cài/giả lập hệ thống | R1, UID/sudoers/plist |
| G2 | B đăng ký hai khe tắt, retry không trùng, không xoay token | 2, API giả + lỗi ghi file | R2/R3, GET Đội ngũ |
| G3 | Claude và token máy dùng được trong daemon; không credential file | 4, runner giả/không vào vòng khi auth lỗi | R2/R5, S2/S3 |
| G4 | Kiểm ben-station không đòi HR | 3, bộ đo giả có hai dự án | R4 |
| G5 | Khe không chạm Git/settings; quản lý chốt SHA sau thu hồi | 5–7, báo cáo giả SHA/hàng đợi | R4 S6, R7 |
| G6 | Repo đúng nguồn, B không giữ quyền GitHub | 9, wrapper không log output | R3 S7 |
| G7 | Mọi bead đủ điều kiện của ben-station, HR bị chặn trước claim/cấp | 8, bộ giao thật trên dữ liệu giả | R6/R7 |
| G8 | Native auth không ghi log; mỗi bước sudo một lệnh | 9, test logger + điều kiện dịch vụ | R1–R7 |
| G9 | Hạn mức chưa biết không bị bịa; thu hồi/estop/QC còn hiệu lực | hồi quy hạn mức, phiếu, chọn khe | R4/R7 S1/S4/S8 |
| G11 | Cổng riêng mỗi lượt, dọn cả phiếu cũ; dependency đúng lock offline | 6, Git thật + bundle tmp/root | R4 S6, R7 |
| G10 | Không hồi quy, giữ trần dòng, đủ bằng chứng mới archive | toàn suite + QC cuối plan | Chỉ archive sau R7 |

## Files và ranh giới

`tram/chu` sở hữu cài phần thợ; `tram/tho` sở hữu cấu hình, báo cáo, quyền và vòng chạy;
`tram/cau_hinh` giữ giới hạn; `tram/giao_viec` kiểm giới hạn trước tác dụng phụ.
Không đổi schema hoặc route. CLI thêm `dang-ky-b`, cờ `kiem --du-an`, hai cờ cài;
`do_nen` là entrypoint một lần của chính daemon để đo S2.
Prompt vai chỉ đổi cách báo/commit khi ở B. Trang Đội ngũ hiện có, không cần mockup mới.

Các script công cụ là sổ tay chạy thật, không là dịch vụ hoặc cổng chứng nhận mới. Chúng in đường log,
chỉ ghi tên bước/mã lỗi; không gộp cả quy trình thành một lệnh bật tất cả.

| File | Loại |
|---|---|
| `cong-cu/doi_ngu_b.py` | Create |
| `cong-cu/doi_ngu_chuan_bi.py` | Create |
| `cong-cu/doi_ngu_io.py` | Create |
| `cong-cu/doi_ngu_s6.py` | Create |
| `tests/test_cai_dat_tho_kiem.py` | Modify |
| `tests/test_dang_nhap_principal.py` | Modify |
| `tests/test_doi_ngu_bao.py` | Create |
| `tests/test_doi_ngu_cai.py` | Create |
| `tests/test_doi_ngu_chot.py` | Create |
| `tests/test_doi_ngu_cong_cu.py` | Create |
| `tests/test_doi_ngu_dang_ky.py` | Create |
| `tests/test_doi_ngu_giao.py` | Create |
| `tests/test_doi_ngu_nen.py` | Create |
| `tests/test_doi_ngu_pham_vi_kiem.py` | Create |
| `tests/test_doi_ngu_quyen.py` | Create |
| `tests/test_kiem_cong.py` | Modify |
| `tests/test_tho_chuan_bi.py` | Modify |
| `tests/test_tho_theo_doi_ket_thuc.py` | Modify |
| `tram/cau_hinh/giao_viec.py` | Modify |
| `tram/cau_hinh/pham_vi_giao.py` | Create |
| `tram/chu/cai_dat_tho.py` | Modify |
| `tram/chu/lenh_tho.py` | Modify |
| `tram/giao_viec/noi_that.py` | Modify |
| `tram/tho/bao.py` | Modify |
| `tram/tho/chot_bao_b.py` | Create |
| `tram/tho/chuan_bi.py` | Modify |
| `tram/tho/dang_ky_b.py` | Create |
| `tram/tho/do_nen.py` | Create |
| `tram/tho/ket_thuc.py` | Modify |
| `tram/tho/kiem_cong.py` | Modify |
| `tram/tho/lenh.py` | Modify |
| `tram/tho/lenh_chay.py` | Modify |
| `tram/tho/mot_lan.py` | Modify |
| `tram/tho/principal.py` | Modify |
| `tram/tho/quyen_cay_b.py` | Create |
| `tram/tho/san_sang_b.py` | Create |
| `tram/tho/theo_doi.py` | Modify |
| `vai/coder.md` | Modify |
| `vai/qc.md` | Modify |
| `vai/spec.md` | Modify |
| `tests/doi_deps_gia.py` | Create |
| `tests/test_doi_ngu_vong_doi.py` | Create |
| `tests/test_doi_ngu_deps.py` | Create |
| `tram/tho/luot_b.py` | Create |
| `tram/tho/chuan_bi_b.py` | Create |
| `tram/tho/deps_b.py` | Create |
| `tram/tho/phieu_chay.py` | Modify |
| `tram/tho/mo_coi_khe.py` | Modify |
| `tram/tho/vong_khe.py` | Modify |
| `tram/tho/don_dep.py` | Modify |
| `tests/test_tho_lenh_chay.py` | Modify |

## Tasks

### Task 1: Cài riêng phần thợ và giữ tắt

**Scenario:** Thêm khe thứ hai khi phần kiểm đã chạy.
**Files:** test `tests/test_doi_ngu_cai.py`; các file Create/Modify được ghi ngay dưới mã.
- [ ] Step 1 — tạo test nguyên văn:

```python
from pathlib import Path
import pytest
from he_gia import HeGia
from tram.chu.cai_dat_tho import lap_ke_hoach_tho
from tram.giao_viec.principal_kiem import tu_cach_ly


def lap(tmp_path, khe):
    he = HeGia()
    return lap_ke_hoach_tho(uv="uv", repo=tmp_path, tram="hung", quan_ly="tram-tho", khe=khe,
        co_che="user", kiem=tu_cach_ly("user:tram-kiem"), thu_muc_kiem=tmp_path / "kiem",
        quan_sat=he.quan_sat, chay=he.chay, chi_tho=True, giu_tat=True)


def test_khong_dung_uq_khong_nap(tram_home_tam, tmp_path):
    kh = lap(tmp_path, {"claude-1": "tram-khe1", "claude-2": "tram-khe2"})
    assert kh.lenh == [] and kh.han_lenh == 30
    assert {p.name for p in kh.tep} == {"tram-tho.sudoers", "vn.tram.tho.plist"}
    assert not any("tram-kiem" in mo or "quan-kiem" in mo for mo, _ in kh.buoc)
    assert "tram-khe1,tram-khe2" in next(v.decode() for p, v in kh.tep.items() if p.suffix == ".sudoers")


@pytest.mark.parametrize("users", [("tram-khe1", "tram-khe1"), ("hung", "tram-khe2"),
    ("tram-tho", "tram-khe2"), ("tram-kiem", "tram-khe2"), ("tram-quan-kiem", "tram-khe2")])
def test_tu_choi_dung_chung_uid_chuc_nang(tram_home_tam, tmp_path, users):
    with pytest.raises(ValueError, match="user riêng"):
        lap(tmp_path, dict(zip(("claude-1", "claude-2"), users)))


def test_han_ap_ca_buoc_tao_tai_nguyen(tram_home_tam, tmp_path):
    he, da = HeGia(), []
    def chay(argv, **kw):
        da.append(kw.get("timeout"))
        return he.chay(argv, **kw)
    kh = lap_ke_hoach_tho(uv="uv", repo=tmp_path, tram="hung", quan_ly="tram-tho",
                         khe={"claude-1": "tram-khe1", "claude-2": "tram-khe2"},
                         co_che="user", chi_tho=True, giu_tat=True, quan_sat=he.quan_sat, chay=chay)
    kh.buoc[1][1]()
    assert da and all(x == 30 for x in da)
```

- [ ] Step 2 — RED: `tests/chan_host/chay.sh -q tests/test_doi_ngu_cai.py`.
  RED đã đo với chữ ký nhận hai cờ nhưng chưa áp hành vi: **5 failed, 1 passed**, gồm `assert kh.lenh == []` và `DID NOT RAISE ValueError`. Test bổ sung chứng minh callback tạo tài nguyên nhận `timeout=None`; sau sửa nhận 30 giây.
- [ ] Step 3 — áp mã dưới đây (file mới chép trọn; bản vá áp theo thứ tự task):

**Modify: `tram/chu/cai_dat_tho.py`**

```diff
--- a/tram/chu/cai_dat_tho.py
+++ b/tram/chu/cai_dat_tho.py
@@ -8,6 +8,7 @@
 lệnh, da_tao kèm định danh sau quan sát), thứ đã có mà sổ không ghi thì từ chối cài."""
 import plistlib
 import subprocess
+from functools import partial
 from pathlib import Path

 from tram.chu.cai_dat import KeHoach
@@ -47,13 +48,19 @@
 def lap_ke_hoach_tho(*, uv: str, repo: Path, tram: str, quan_ly: str, khe: dict[str, str], co_che: str,
                      kiem: PrincipalKiem | None = None, thu_muc_kiem: Path | None = None,
                      db_nghiep_vu: tuple[str, ...] = (), so: SoCai | None = None, quan_sat=None,
-                     chay=subprocess.run) -> KeHoach:
+                     chay=subprocess.run, chi_tho: bool = False, giu_tat: bool = False) -> KeHoach:
     """`khe`: tên khe → user principal (cơ chế `sandbox`: mọi khe cùng một user). `tram`: user macOS của tài khoản
     trạm (chủ tram-api). `kiem`, `thu_muc_kiem`: từ `doc_principal_kiem()` và `giao_viec.thu_muc_kiem`."""
     if co_che not in ("user", "sandbox"):
         raise ValueError("--co-che user | sandbox (Đại ca chốt sau S6)")
     if la := [u for u in (*khe.values(), quan_ly) if not USER_RE.fullmatch(u)]:
         raise ValueError(f"tên user không hợp lệ (cần [a-z_][a-z0-9_-]*, gỡ được về sau): {', '.join(la)}")
+    if co_che == "user" and (len(set(khe.values())) != len(khe) or
+                             set(khe.values()) & {tram, quan_ly, "tram-kiem", "tram-quan-kiem"}):
+        raise ValueError("Mỗi khe cần user riêng, khác trạm và phần kiểm")
+    if chi_tho:
+        kiem, thu_muc_kiem, db_nghiep_vu = None, None, ()
+    chay = partial(chay, timeout=30)
     soan, so, quan_sat = tram_home() / "cai-dat-tho", so or SoCai(), quan_sat or dinh_danh.quan_sat_that
     pk = phan_kiem(kiem=kiem, thu_muc_kiem=thu_muc_kiem, co_che=co_che, tram=tram, quan_ly=quan_ly, soan=soan,
                    khe=tuple(khe.values()), db_nghiep_vu=db_nghiep_vu, quan_sat=quan_sat)
@@ -95,4 +102,5 @@
         "dưới launchd không là việc của spike S2 — không được thì dừng, không đổi sang lưu token ra file.",
         f"Sổ {so.p}: chỉ ghi thêm. S6 hỏng → `tram chu go-cai-dat-tho` chỉ gỡ thứ sổ ghi da_tao VÀ còn đúng định "
         "danh (user: UID + GeneratedUID; file: sha256) — in kế hoạch, chờ dong-y."]
-    return KeHoach(tep=tep, lenh=lenh, canh_bao=canh_bao + pk.canh_bao, buoc=buoc)
+    return KeHoach(tep=tep, lenh=[] if giu_tat else lenh, canh_bao=canh_bao + pk.canh_bao,
+                  buoc=buoc, han_lenh=30)
```
**Modify: `tram/chu/lenh_tho.py`**

```diff
--- a/tram/chu/lenh_tho.py
+++ b/tram/chu/lenh_tho.py
@@ -28,9 +28,11 @@
     try:
         khoa.enter_context(so.giu())          # R4: cả lần cài (kế hoạch → dong-y → chạy) giữ khoá sổ, không chờ
         kh = lap_ke_hoach_tho(uv=shutil.which("uv") or "uv", repo=goc_repo(), tram=getpass.getuser(),
-                              quan_ly=args.quan_ly, khe=khe, co_che=args.co_che, kiem=doc_principal_kiem(),
-                              thu_muc_kiem=nap_cau_hinh_giao_viec().thu_muc_kiem,
-                              db_nghiep_vu=nap_cau_hinh_cach_ly().db_nghiep_vu, so=so)
+                              quan_ly=args.quan_ly, khe=khe, co_che=args.co_che,
+                              kiem=None if args.chi_tho else doc_principal_kiem(),
+                              thu_muc_kiem=None if args.chi_tho else nap_cau_hinh_giao_viec().thu_muc_kiem,
+                              db_nghiep_vu=() if args.chi_tho else nap_cau_hinh_cach_ly().db_nghiep_vu, so=so,
+                              chi_tho=args.chi_tho, giu_tat=args.giu_tat)
     except (ValueError, OSError) as e:         # cấu hình/sổ lỗi, tài nguyên lạ, SoCaiDangBan, dscl lỗi
         khoa.close()
         print(f"Không cài: {e}", file=sys.stderr)
@@ -42,7 +44,7 @@
             return 1
         try:
             thuc_hien(kh)
-        except (LoiCaiDat, OSError, ValueError, subprocess.CalledProcessError) as e:
+        except (LoiCaiDat, OSError, ValueError, subprocess.SubprocessError) as e:
             print(f"Dừng giữa chừng: {e}\nSổ cài đặt đã ghi đúng phần đã tạo — `tram chu go-cai-dat-tho` gỡ được.",
                   file=sys.stderr)
             return 1
@@ -84,6 +86,8 @@
     c.add_argument("--quan-ly", default="tram-tho", help="User macOS của tiến trình quản lý thợ")
     c.add_argument("--khe", action="append", required=True, help="<tên khe>=<user principal>, lặp lại mỗi khe")
     c.add_argument("--co-che", required=True, choices=("user", "sandbox"), help="Cơ chế cách ly (chốt sau S6)")
+    c.add_argument("--chi-tho", action="store_true", help="Không cài lại phần kiểm")
+    c.add_argument("--giu-tat", action="store_true", help="Chỉ cài file, không nạp dịch vụ")
     c.add_argument("--dong-y", action="store_true")
     c.set_defaults(ham=_cai_dat_tho)
     t = chu.add_parser("cap-token-may", help="Cấp token máy thợ, chỉ in vào ống tới `tram tho nhan-token`")
```

**Modify: `tests/test_cai_dat_tho_kiem.py`**

```diff
--- a/tests/test_cai_dat_tho_kiem.py
+++ b/tests/test_cai_dat_tho_kiem.py
@@ -113,7 +113,8 @@
                                                  f"giao_viec:\n  thu_muc_kiem: {tmp_path}/kiem\n")
     monkeypatch.setattr("tram.chu.dinh_danh.quan_sat_that", HeGia().quan_sat)
     monkeypatch.setattr("builtins.input", lambda _: "khong")
-    args = SimpleNamespace(khe=["claude-1=tram-k-1"], quan_ly="tram-tho", co_che="user", dong_y=False)
+    args = SimpleNamespace(khe=["claude-1=tram-k-1"], quan_ly="tram-tho", co_che="user", dong_y=False,
+                           chi_tho=False, giu_tat=False)
     assert lenh_tho._cai_dat_tho(args) == 1 and f"{tmp_path}/kiem" in capsys.readouterr().out
     assert lenh_tho._cai_dat_tho(SimpleNamespace(**{**vars(args), "co_che": "sandbox"})) == 2
     assert "khác --co-che" in capsys.readouterr().err
```

- [ ] Step 4 — GREEN: `tests/chan_host/chay.sh -q tests/test_doi_ngu_cai.py`; chạy hồi quy nêu dưới.
  Hồi quy: `tests/test_cai_dat_tho_kiem.py tests/test_so_cai_tho.py tests/test_go_cai_dat_tho.py`.
  Cờ không thay việc đối soát sổ. User hiện có không khớp biên nhận vẫn dừng; không tự nhận làm của trạm.

### Task 2: Đăng ký B bằng token đang có, ghi cấu hình sau xác nhận

**Scenario:** Đăng ký lần đầu và gửi lại; HTTP lỗi hoặc mất phản hồi.
**Files:** test `tests/test_doi_ngu_dang_ky.py`; các file Create/Modify được ghi ngay dưới mã.
- [ ] Step 1 — tạo test nguyên văn:

```python
import yaml
import pytest
from tram.tho.dang_ky_b import dang_ky_b
from tram.tho.khach import LoiKhachTram


def ung_vien(p):
    p.write_text(yaml.safe_dump({"may_id": "B", "tram_api": "http://127.0.0.1:7700",
        "chay": {"day": "kho-tho"}, "khe": [{"ten": f"claude-{n}", "cli": "claude",
        "principal": f"user:tram-khe{n}", "thu_muc_cau_hinh": f"/Users/tram-khe{n}/claude",
        "ten_goi_nho": f"Tho {n}", "vai_uu_tien": ["coder"]} for n in (1, 2)]}))
    return p


class Khach:
    def __init__(self, ma=200):
        self.ma, self.gui = ma, []
    def ping(self):
        return {"may_id": "B"}
    def goi(self, method, url, than):
        self.gui.append((method, url, than))
        return self.ma, {"loi": "khong-duoc-in"}


def test_http_hong_khong_thay_file(tmp_path):
    p, dich = ung_vien(tmp_path / "moi"), tmp_path / "tho.yaml"
    dich.write_text("cu")
    with pytest.raises(LoiKhachTram, match="HTTP 503"):
        dang_ky_b(p, dich, Khach(503))
    assert dich.read_text() == "cu" and not list(tmp_path.glob("tho-truoc-*"))


def test_thanh_cong_retry_giu_ban_sao(tmp_path):
    p, dich, khach = ung_vien(tmp_path / "moi"), tmp_path / "tho.yaml", Khach()
    dich.write_text("cu")
    for _ in range(2):
        assert dang_ky_b(p, dich, khach) == ["B/claude-1", "B/claude-2"]
    assert dich.read_bytes() == p.read_bytes() and dich.stat().st_mode & 0o777 == 0o600
    assert len(list(tmp_path.glob("tho-truoc-*"))) == 1
    assert khach.gui[0] == khach.gui[1]
    assert "principal" not in khach.gui[0][2]["khe"][0]


def test_token_sai_may_khong_post(tmp_path):
    khach = Khach()
    khach.ping = lambda: {"may_id": "C"}
    with pytest.raises(ValueError, match="Token"):
        dang_ky_b(ung_vien(tmp_path / "moi"), tmp_path / "tho.yaml", khach)
    assert khach.gui == []



def test_api_retry_khong_tu_bat_khe(tmp_path):
    from contextlib import closing
    from tho_api_gia import tao_tram, KHE
    from tram.phieu.khe import khe_dang_bat
    t = tao_tram(tmp_path, dang_ky=False)
    than = {"may_id": "B", "khe": KHE}
    for _ in range(2):
        assert t.goi("POST", "/api/tho/dang-ky", json_body=than).status == 200
    assert t.goi("POST", "/api/tho/dang-ky", may="C", json_body=than).status == 403
    with closing(t.kho()) as kho:
        assert kho.db.execute("SELECT COUNT(*) FROM su_kien WHERE loai='khe.dang_ky'").fetchone()[0] == 2
        assert not khe_dang_bat(kho, "B/claude-1") and not khe_dang_bat(kho, "B/claude-2")


def test_ghi_file_hong_sau_post_giu_cu_retry_duoc(tmp_path, monkeypatch):
    from tram.tho import dang_ky_b as module
    p, dich, khach = ung_vien(tmp_path / "moi"), tmp_path / "tho.yaml", Khach()
    dich.write_text("cu")
    replace = module.os.replace
    monkeypatch.setattr(module.os, "replace", lambda *a: (_ for _ in ()).throw(OSError("disk")))
    with pytest.raises(OSError):
        dang_ky_b(p, dich, khach)
    assert dich.read_text() == "cu" and len(khach.gui) == 1
    assert not list(tmp_path.glob(".tho-*"))
    monkeypatch.setattr(module.os, "replace", replace)
    assert dang_ky_b(p, dich, khach) == ["B/claude-1", "B/claude-2"]
```

- [ ] Step 2 — RED: `tests/chan_host/chay.sh -q tests/test_doi_ngu_dang_ky.py`.
  RED đã đo với `dang_ky_b` stub trả `None`: **3 failed, 1 passed**, gồm `DID NOT RAISE LoiKhachTram`. API retry là hồi quy đã xanh sẵn. Test bổ sung mô phỏng `os.replace` lỗi sau POST, giữ file cũ và retry thành công.
- [ ] Step 3 — áp mã dưới đây (file mới chép trọn; bản vá áp theo thứ tự task):

**Create: `tram/tho/dang_ky_b.py`**

```python
"""Đăng ký cấu hình B; không cài dịch vụ hoặc cấp lại token."""
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.khach import LoiKhachTram


def kiem_b(ch):
    if ch.may_id != "B" or ch.tram_api != "http://127.0.0.1:7700" or ch.chay.day != "kho-tho":
        raise ValueError("Cần máy B, API loopback và đường kho-tho")
    expected = {"claude-1": "user:tram-khe1", "claude-2": "user:tram-khe2"}
    if {k.ten: k.principal for k in ch.khe} != expected or any(k.cli != "claude" for k in ch.khe):
        raise ValueError("Cần đúng hai khe Claude riêng trên B")
    for k in ch.khe:
        if k.thu_muc_cau_hinh != Path(f"/Users/{k.principal[5:]}/claude"):
            raise ValueError("Thư mục Claude phải thuộc đúng khe")


def dang_ky_b(nguon: Path, dich: Path, khach) -> list[str]:
    ch = nap_cau_hinh_tho(nguon)
    kiem_b(ch)
    noi_dung = nguon.read_bytes()
    if khach.ping().get("may_id") != "B":
        raise ValueError("Token không thuộc máy B")
    than = {"may_id": "B", "khe": [{n: asdict(k)[n] for n in
        ("ten", "cli", "ten_goi_nho", "vai_uu_tien")} for k in ch.khe]}
    ma, _ = khach.goi("POST", "/api/tho/dang-ky", than)
    if ma != 200:
        raise LoiKhachTram(f"Đăng ký B chưa xác nhận (HTTP {ma})")
    dich.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if dich.is_symlink():
        raise ValueError("Không thay cấu hình là symlink")
    if dich.exists() and dich.read_bytes() == noi_dung:
        return [f"B/{k.ten}" for k in ch.khe]
    if dich.exists():
        fd, _ = tempfile.mkstemp(prefix="tho-truoc-", suffix=".yaml", dir=dich.parent)
        with os.fdopen(fd, "wb") as f:
            f.write(dich.read_bytes())
            f.flush()
            os.fsync(f.fileno())
    fd, ten = tempfile.mkstemp(prefix=".tho-", dir=dich.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(noi_dung)
            f.flush()
            os.fsync(f.fileno())
        os.replace(ten, dich)
    finally:
        Path(ten).unlink(missing_ok=True)
    return [f"B/{k.ten}" for k in ch.khe]


def lenh(args):
    import fcntl
    import pwd
    from tram.duong_dan import tram_home
    from tram.tho.khach import KhachTram, doc_token_may
    if pwd.getpwuid(os.getuid()).pw_name != "tram-tho":
        print("Chạy đăng ký dưới tài khoản tram-tho.")
        return 2
    if not args.dong_y:
        print("Sẽ đăng ký hai khe B và thay tho.yaml; không bật dịch vụ.")
        if input("Gõ dong-y: ").strip() != "dong-y":
            return 1
    try:
        token = doc_token_may()
        if not token:
            raise ValueError("Thiếu token máy")
        goc = tram_home()
        goc.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd = os.open(goc / ".dang-ky-b.lock", os.O_CREAT | os.O_RDWR, 0o600)
        with os.fdopen(fd, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            dang_ky_b(Path(args.tep), goc / "tho.yaml", KhachTram("http://127.0.0.1:7700", token))
    except (OSError, ValueError, LoiKhachTram):
        print("Chưa hoàn tất đăng ký B; giữ dịch vụ tắt, đối soát rồi thử lại cùng cấu hình/token.")
        return 2
    print("Đã đăng ký hai khe B; chưa bật khe hoặc giao việc.")
    return 0


def them_lenh(tho):
    p = tho.add_parser("dang-ky-b", help="Đăng ký hai khe trên máy B, không bật thợ")
    p.add_argument("--tep", required=True)
    p.add_argument("--dong-y", action="store_true")
    p.set_defaults(ham=lenh)
```
**Modify: `tram/tho/lenh.py`**

```diff
--- a/tram/tho/lenh.py
+++ b/tram/tho/lenh.py
@@ -58,6 +58,8 @@
     tho.add_parser("kiem", help="Kiểm máy thợ: xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ").set_defaults(ham=_kiem)
     from tram.tho.lenh_dang_ky import them_lenh_dang_ky
     them_lenh_dang_ky(tho)
+    from tram.tho.dang_ky_b import them_lenh
+    them_lenh(tho)
     for ten, mo_ta in (("tat-khe", "Tắt khe (phiếu đang chạy dừng mềm)"), ("bat-khe", "Bật lại khe")):
         x = tho.add_parser(ten, help=mo_ta)
         x.add_argument("khe", help="khe_id, vd B/claude-1")
```

- [ ] Step 4 — GREEN: `tests/chan_host/chay.sh -q tests/test_doi_ngu_dang_ky.py`; chạy hồi quy nêu dưới.
  Hồi quy: `tests/test_trang_thai_khe.py tests/test_giao_viec_api.py`.
  Kiểm thêm bằng API giả: token máy khác B bị 403; gửi cùng hai khe hai lần chỉ có hai sự kiện `khe.dang_ky`.

### Task 3: Kiểm repo đúng phạm vi

**Scenario:** HR chưa clone.
**Files:** test `tests/test_doi_ngu_pham_vi_kiem.py`; các file Create/Modify được ghi ngay dưới mã.
- [ ] Step 1 — tạo test nguyên văn:

```python
from types import SimpleNamespace
import pytest
from tram.tho.kiem_cong import dau_do_that


def test_chi_thu_hep_repo_khong_bo_kiem_khe(monkeypatch, tmp_path):
    from tram.tho import kiem_cong
    da = []
    monkeypatch.setattr(kiem_cong, "cach_ly", lambda ch, ds, **kw: da.extend(ds) or [])
    k = SimpleNamespace(du_an=lambda: ["ben-station", "hr-codex"], ping=lambda: {}, kiem_am=lambda: None)
    dd = dau_do_that(object(), k, du_an=("ben-station",))
    assert dd.du_an() == ["ben-station"] and dd.dang_nhap is not None
    dd.cach_ly()
    assert da == ["ben-station"]
    with pytest.raises(ValueError, match="không có"):
        dau_do_that(object(), k, du_an=("khong-co",))
```

- [ ] Step 2 — RED: `tests/chan_host/chay.sh -q tests/test_doi_ngu_pham_vi_kiem.py`.
  RED đã đo sau thêm chữ ký `du_an` nhưng chưa lọc: **1 failed**, danh sách trả về còn `hr-codex`. Không dùng lỗi `unexpected keyword argument` làm bằng chứng hành vi.
- [ ] Step 3 — áp mã dưới đây (file mới chép trọn; bản vá áp theo thứ tự task):

**Modify: `tram/tho/kiem_cong.py`**

```diff
--- a/tram/tho/kiem_cong.py
+++ b/tram/tho/kiem_cong.py
@@ -1,12 +1,4 @@
-"""Các mục chờ cổng của `tram tho kiem` (spec 3 §9.3, H7) — chạy THẬT dưới principal của khe, không đánh dấu xanh bằng
-fixture: đăng nhập CLI qua lệnh trạng thái (không đọc file đăng nhập — lệnh chính xác CHỜ S2), và kiểm chứng âm rút
-gọn §7.3 mục 7 (Keychain/token máy, thư mục tiến trình quản lý, hàng đợi + cấu hình khe khác, `.git/config` và
-`.git/hooks` của kho) + hai thăm dò dương. Principal chưa khai/sai → đỏ. bs-863.14: UID thực của principal chứng minh
-TRƯỚC (`xac_minh_uid`); thăm dò qua P1 với `kill` của principal, env dựng mới chỉ PATH/LANG (không HOME của quản lý).
-Review vòng 1 A02: thăm dò xong mà bảng tiến trình của nhân còn tiến trình của UID principal → ĐỎ (CHỈ QUAN SÁT, không
-giết: có thể `tram tho chay` đang chạy phiếu — sổ tay: dừng nó trước khi kiểm). D54 (18/10): thêm hai thăm dò "API
-Duyệt giả danh Đại ca" và "kết nối DB nghiệp vụ" dưới CHÍNH principal khe (trạm không chạy thay khe); đích do trạm cấp
-(`KhachTram.kiem_am`); thợ không ở máy B hay không lấy được đích → ĐỎ "không kết luận", phần rút gọn vẫn chạy."""
+"""Kiểm đăng nhập và cách ly khe bằng thăm dò đúng principal; lỗi đối chứng không tính đạt."""
 import subprocess
 from collections.abc import Callable
 from pathlib import Path
@@ -111,10 +103,14 @@
     return ra


-def dau_do_that(ch: CauHinhTho, khach) -> DauDo:
+def dau_do_that(ch: CauHinhTho, khach, *, du_an: tuple[str, ...] = ()) -> DauDo:
     """Đầu đo của `tram tho kiem` có mục chờ cổng chạy THẬT (3a-2)."""
     from tram.duong_dan import tram_home
     goc, goc_wt = tram_home(), Path.home() / "tram" / "worktrees"
-    return DauDo(ping=khach.ping, du_an=khach.du_an,
+    ds = khach.du_an() if du_an else None
+    if du_an and not set(du_an) <= set(ds):
+        raise ValueError("Dự án kiểm không có ở trạm")
+    lay = (lambda: list(du_an)) if du_an else khach.du_an
+    return DauDo(ping=khach.ping, du_an=lay,
                  dang_nhap=lambda k: dang_nhap(ch, k, goc=goc, goc_wt=goc_wt),
-                 cach_ly=lambda: cach_ly(ch, khach.du_an(), goc=goc, goc_wt=goc_wt, dich=khach.kiem_am))
+                 cach_ly=lambda: cach_ly(ch, lay(), goc=goc, goc_wt=goc_wt, dich=khach.kiem_am))
```
**Modify: `tram/tho/lenh.py`**

```diff
--- a/tram/tho/lenh.py
+++ b/tram/tho/lenh.py
@@ -16,7 +16,12 @@
         print(f"[ĐỎ] tho.yaml: {e}")
         return 1
     khach = KhachTram(ch.tram_api, doc_token_may() or "")
-    van_ban, ma = in_ket_qua(kiem_may(ch, dau_do_that(ch, khach)))      # mục chờ cổng chạy thật (3a-2)
+    try:
+        dd = dau_do_that(ch, khach, du_an=tuple(args.du_an))
+        van_ban, ma = in_ket_qua(kiem_may(ch, dd))
+    except (ValueError, OSError):
+        print("Không xác nhận được phạm vi kiểm máy thợ.")
+        return 2
     print(van_ban)
     return ma

@@ -55,7 +60,9 @@

 def them_lenh_tho(sub, chu) -> None:
     tho = sub.add_parser("tho", help="Máy thợ (phần 3)").add_subparsers(dest="lenh_tho", required=True)
-    tho.add_parser("kiem", help="Kiểm máy thợ: xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ").set_defaults(ham=_kiem)
+    k = tho.add_parser("kiem", help="Kiểm máy thợ: xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ")
+    k.add_argument("--du-an", action="append", default=[])
+    k.set_defaults(ham=_kiem)
     from tram.tho.lenh_dang_ky import them_lenh_dang_ky
     them_lenh_dang_ky(tho)
     from tram.tho.dang_ky_b import them_lenh
```

- [ ] Step 4 — GREEN: `tests/chan_host/chay.sh -q tests/test_doi_ngu_pham_vi_kiem.py`; chạy hồi quy nêu dưới.
  Hồi quy: `tests/test_tho_lenh.py tests/test_kiem_cong.py tests/test_kiem_3b.py`; API/DB vẫn chạy dưới từng principal.

### Task 4: Dừng sạch khi đăng nhập chưa sẵn sàng; phép thử nền hữu hạn

**Scenario:** Keychain khoá hoặc CLI lưu credential ra file; Có đăng nhập tương tác nhưng chưa chứng minh chạy nền.
**Files:** test `tests/test_doi_ngu_nen.py`; các file Create/Modify được ghi ngay dưới mã.
- [ ] Step 1 — tạo test nguyên văn:

```python
from dataclasses import replace
from types import SimpleNamespace
from pathlib import Path
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.cau_hinh_chay import CauHinhChay
from tram.tho.san_sang_b import san_sang_b
from tram.tho.do_nen import thu_claude


def ch():
    return CauHinhTho("B", "http://127.0.0.1:7700", tuple(KheCauHinh(f"claude-{n}", "claude",
        f"user:tram-khe{n}", Path(f"/Users/tram-khe{n}/claude"), f"Tho {n}", ("coder",))
        for n in (1, 2)), CauHinhChay(day="kho-tho"))


def test_thieu_auth_khong_san_sang():
    assert not san_sang_b(ch(), do=lambda *a, **kw: ("do", "khoa"))
    assert san_sang_b(ch(), do=lambda *a, **kw: ("xanh", "ok"))


def test_hai_luot_nen_khong_token_khong_tools(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    (tmp_path / "tram").mkdir()
    da = []
    def run(argv, **kw):
        da.append((argv, kw))
        return SimpleNamespace(returncode=0, stdout='{"type":"result","is_error":false,"result":"SAN-SANG"}')
    assert thu_claude(ch(), chay=run)
    assert len(da) == 2 and all(x[1]["timeout"] == 120 for x in da)
    assert [x[1]["env"]["CLAUDE_CONFIG_DIR"] for x in da] == ["/Users/tram-khe1/claude", "/Users/tram-khe2/claude"]
    assert all("--tools" in x[0] and "CLAUDE_CODE_OAUTH_TOKEN" not in x[1]["env"] for x in da)


def test_loi_auth_khong_lap_daemon(monkeypatch):
    from tram.tho import cau_hinh, lenh_chay, san_sang_b as module
    monkeypatch.setattr(cau_hinh, "nap_cau_hinh_tho", ch)
    monkeypatch.setattr(module, "san_sang_b", lambda c: False)
    monkeypatch.setattr(lenh_chay, "chay_may", lambda *a: (_ for _ in ()).throw(AssertionError("nhan viec")))
    assert lenh_chay._chay(SimpleNamespace()) == 0



def test_exit_0_nhung_chua_dang_nhap_khong_xanh(tmp_path):
    from test_kiem_cong import cau_hinh
    from tram.tho.kiem_cong import dang_nhap
    c = cau_hinh(tmp_path)
    for out in ('{"loggedIn":false}', '{}', '[]', 'khong-phai-json'):
        def run(*a, **kw):
            return SimpleNamespace(returncode=0, stdout=out)
        assert dang_nhap(c, c.khe[0], goc=tmp_path, goc_wt=tmp_path,
                        chay=run, xac_minh=lambda *a: 600)[0] == "do"


def test_yaml_hong_thoat_sach_khong_goi_keychain(monkeypatch):
    import yaml
    from tram.tho import cau_hinh, lenh_chay
    def hong():
        raise yaml.YAMLError("noi-dung-khong-duoc-in")
    monkeypatch.setattr(cau_hinh, "nap_cau_hinh_tho", hong)
    monkeypatch.setattr(lenh_chay, "doc_token_may", lambda: (_ for _ in ()).throw(AssertionError()))
    assert lenh_chay._chay(SimpleNamespace()) == 0


def test_het_han_ghi_token_khong_in_dau_ra(monkeypatch, capsys):
    import io
    import subprocess
    from tram.tho import lenh_chay
    monkeypatch.setattr(lenh_chay.sys, "stdin", io.StringIO("t" * 43))
    def hong(token):
        raise subprocess.TimeoutExpired(["security", "-i"], 10, output="bi-mat", stderr="bi-mat")
    monkeypatch.setattr(lenh_chay, "luu_token_may", hong)
    assert lenh_chay._nhan_token(SimpleNamespace()) == 2
    assert "bi-mat" not in capsys.readouterr().err
```

- [ ] Step 2 — RED: `tests/chan_host/chay.sh -q tests/test_doi_ngu_nen.py`.
  RED hành vi: `san_sang_b` stub trả `None` không đạt assertion sẵn sàng; JSON `loggedIn:false` bị mã cũ coi xanh. Bổ sung tái hiện `yaml.YAMLError` và `subprocess.TimeoutExpired` thoát khỏi CLI; mã sửa trả kết quả cố định, không in dữ liệu con.
- [ ] Step 3 — áp mã dưới đây (file mới chép trọn; bản vá áp theo thứ tự task):

**Create: `tram/tho/san_sang_b.py`**

```python
"""Dò đăng nhập trước khi B bắt đầu vòng nhận việc; không coi đây là chứng cứ S2."""
from pathlib import Path

from tram.tho.dang_ky_b import kiem_b
from tram.tho.kiem_cong import dang_nhap


def san_sang_b(ch, *, do=dang_nhap) -> bool:
    from tram.duong_dan import tram_home
    if not ch.tren_may_b:
        return True
    kiem_b(ch)
    return all(do(ch, k, goc=tram_home(), goc_wt=Path.home() / "tram/worktrees")[0] == "xanh"
               for k in ch.khe)
```
**Modify: `tram/tho/lenh_chay.py`**

```diff
--- a/tram/tho/lenh_chay.py
+++ b/tram/tho/lenh_chay.py
@@ -6,6 +6,8 @@
 import subprocess
 import sys
 import threading
+
+import yaml

 from tram.tho.khach import KEYCHAIN_THO, doc_token_may
 from tram.tho.ngu_canh import NguCanhTho
@@ -31,7 +33,7 @@
         {"ten": k.ten, "cli": k.cli, "ten_goi_nho": k.ten_goi_nho, "vai_uu_tien": list(k.vai_uu_tien)}
         for k in ch.khe]})
     if ma != 200:
-        print(f"Đăng ký khe thất bại: {ma} {kq}", file=sys.stderr)
+        print(f"Đăng ký khe thất bại: HTTP {ma}", file=sys.stderr)
         return 2
     luong = [threading.Thread(target=VongKhe(nc, k).chay, args=(tat,), name=f"khe-{k.ten}") for k in ch.khe]
     for t in luong:
@@ -46,11 +48,19 @@
 def _chay(args) -> int:
     from tram.tho.cau_hinh import nap_cau_hinh_tho
     from tram.tho.khach import KhachTram
-    ch = nap_cau_hinh_tho()
+    from tram.tho.san_sang_b import san_sang_b
+    try:
+        ch = nap_cau_hinh_tho()
+        if not san_sang_b(ch):
+            print("Chưa xác nhận đăng nhập nền của hai khe; đăng nhập rồi khởi động lại thợ.")
+            return 0
+    except (ValueError, OSError, yaml.YAMLError):
+        print("Cấu hình thợ chưa sẵn sàng; giữ tắt, đối soát rồi khởi động lại.")
+        return 0
     token = doc_token_may()
     if not token:
-        print("Chưa có token máy trong Keychain (tram tho nhan-token).", file=sys.stderr)
-        return 2
+        print("Chưa có token máy trong Keychain; mở đúng Keychain rồi khởi động lại thợ.", file=sys.stderr)
+        return 0
     tat = threading.Event()
     for s in (signal.SIGTERM, signal.SIGINT):
         signal.signal(s, lambda *_: tat.set())
@@ -62,7 +72,7 @@
     if not TOKEN_RE.fullmatch(token):
         raise ValueError("Token máy sai dạng")
     chay(["security", "-i"], input=f"add-generic-password -U -s {KEYCHAIN_THO} -a tram -w {token}\n", text=True,
-         check=True, capture_output=True)
+         check=True, capture_output=True, timeout=10)
     if doc() != token:
         raise RuntimeError("Không lưu được token vào Keychain (Keychain của user này có mở không? — S2)")

@@ -72,8 +82,8 @@
     token = (sys.stdin.readline() if not sys.stdin.isatty() else getpass.getpass("Dán token máy (ẩn): ")).strip()
     try:
         luu_token_may(token)
-    except (ValueError, RuntimeError, subprocess.CalledProcessError) as e:
-        print(f"Lỗi: {e}", file=sys.stderr)
+    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError):
+        print("Chưa xác nhận lưu token máy; giữ thợ tắt và đối soát Keychain.", file=sys.stderr)
         return 2
     print(f"Đã lưu token máy vào Keychain ({KEYCHAIN_THO}).")
     return 0
```
**Create: `tram/tho/do_nen.py`**

```python
"""Phép thử hữu hạn từ chính daemon thợ; không xin phiếu, không ghi danh tính/token ra log."""
import json
import tempfile
from pathlib import Path

from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.khach import KhachTram, doc_token_may
from tram.tho.principal import doc_principal
from tram.tho.san_sang_b import san_sang_b


def thu_claude(ch, *, chay=chay_gioi_han):
    with tempfile.TemporaryDirectory(prefix="do-nen-", dir=Path.home() / "tram") as ten:
        goc = Path(ten)
        goc.chmod(0o755)
        for k in ch.khe:
            pr = doc_principal(k.principal)
            env = {"PATH": ch.chay.path_cli, "LANG": "C.UTF-8", "CLAUDE_CONFIG_DIR": str(k.thu_muc_cau_hinh)}
            argv = ["claude", "-p", "--output-format", "stream-json", "--verbose", "--tools", "",
                    "--setting-sources", "user", "--strict-mcp-config", "--max-turns", "1"]
            kq = chay(pr.boc(argv), env=env, cwd=goc, kill=pr.kill_nhom, timeout=120,
                      input="Chỉ trả lời SAN-SANG. Không dùng công cụ.", text=True, capture_output=True)
            dong = [json.loads(x) for x in kq.stdout.splitlines() if x.strip()]
            dat = any(x.get("type") == "result" and x.get("is_error") is False
                      and "SAN-SANG" in x.get("result", "") for x in dong)
            if kq.returncode != 0 or not dat:
                return False
    return True


def main():
    try:
        ch = nap_cau_hinh_tho()
        token = doc_token_may()
        if not token or not san_sang_b(ch):
            print("DO-NEN: CHUA-DANG-NHAP", flush=True)
            return 2
        if KhachTram(ch.tram_api, token).ping().get("may_id") != "B":
            print("DO-NEN: TOKEN-KHONG-KHOP", flush=True)
            return 2
        if not thu_claude(ch):
            print("DO-NEN: CLAUDE-CHUA-DAT", flush=True)
            return 2
    except Exception:
        print("DO-NEN: KHONG-KET-LUAN", flush=True)
        return 2
    print("DO-NEN: DAT-HAI-KHE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Modify: `tram/tho/kiem_cong.py`**

```diff
--- a/tram/tho/kiem_cong.py
+++ b/tram/tho/kiem_cong.py
@@ -1,4 +1,5 @@
 """Kiểm đăng nhập và cách ly khe bằng thăm dò đúng principal; lỗi đối chứng không tính đạt."""
+import json
 import subprocess
 from collections.abc import Callable
 from pathlib import Path
@@ -19,7 +20,6 @@

 LENH_DANG_NHAP = ("auth", "status")                    # CHỜ S2: lệnh trạng thái không đọc file đăng nhập
 KEYCHAIN_CAM = ("tram-tho-token", "tram-noi-bo-token", "tram-anthropic-api-key")
-

 def _uid(p, xac_minh) -> tuple[int | None, str | None]:
     """Lỗi UID/thu hồi: không chạy thêm; chỉ hướng dẫn có điều kiện, không chép ngoại lệ."""
@@ -47,8 +47,12 @@
         return "do", "không xác nhận thu hồi tiến trình lệnh trạng thái — kiểm principal" + HUONG_DAN_SUDO
     except (OSError, subprocess.SubprocessError, ValueError) as e:
         return "do", f"không chạy được lệnh trạng thái: {type(e).__name__}" + HUONG_DAN_SUDO
-    return ("xanh", "đã đăng nhập (lệnh chờ S2 xác nhận)") if kq.returncode == 0 else (
-        "do", "chưa đăng nhập / lỗi" + HUONG_DAN_SUDO)
+    try:
+        co = json.loads(kq.stdout).get("loggedIn") is True
+    except (ValueError, AttributeError):
+        co = False
+    return ("xanh", "đã đăng nhập") if kq.returncode == 0 and co else (
+        "do", "chưa xác nhận đăng nhập / dạng phản hồi không khớp S2" + HUONG_DAN_SUDO)


 def _tan_du(uid: int, chup) -> list[KetQuaThamDo]:
```
**Modify: `tests/test_kiem_cong.py`**

```diff
--- a/tests/test_kiem_cong.py
+++ b/tests/test_kiem_cong.py
@@ -43,7 +43,7 @@

     def chay(argv, **kw):
         goi.append((argv, kw["env"]))
-        return SimpleNamespace(returncode=0)
+        return SimpleNamespace(returncode=0, stdout='{"loggedIn":true}')
     ch = cau_hinh(tmp_path)
     assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay, xac_minh=lambda *a: 600)[0] == "xanh"
     argv, env = goi[0]
```
**Modify: `tests/test_dang_nhap_principal.py`**

```diff
--- a/tests/test_dang_nhap_principal.py
+++ b/tests/test_dang_nhap_principal.py
@@ -24,7 +24,7 @@
         goi.append((argv, kw))
         if isinstance(ket, BaseException):
             raise ket
-        return subprocess.CompletedProcess(argv, ket, "Logged in as ai@x\n", "")
+        return subprocess.CompletedProcess(argv, ket, '{"loggedIn":true}\n' if "auth" in argv else "Logged in as ai@x\n", "")
     return chay


```

- [ ] Step 4 — GREEN: `tests/chan_host/chay.sh -q tests/test_doi_ngu_nen.py`; chạy hồi quy nêu dưới.
  Hồi quy: `tests/test_tho_lenh_chay.py`; chạy thật mới xác nhận cờ CLI và Keychain.
  Lệnh `do_nen` là chế độ một lần của chính `vn.tram.tho`, không thêm dịch vụ.

### Task 5: Báo cáo qua hàng đợi, không cần quyền commit của khe

**Scenario:** Mốc tạm hoặc báo cáo giả SHA.
**Files:** test `tests/test_doi_ngu_bao.py`; các file Create/Modify được ghi ngay dưới mã.
- [ ] Step 1 — tạo test nguyên văn:

```python
import json
from tram.tho.bao import bao
from test_tram_bao import khoi, FILE


def test_bao_b_khong_goi_git(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_GIT_QUA_QUAN_LY", "1")
    monkeypatch.setenv("TRAM_NHANH", "tram/bs-thu")
    p = tmp_path / FILE
    p.parent.mkdir(parents=True)
    p.write_text("<!-- ban-giao -->" + json.dumps(khoi()) + "<!-- ban-giao -->")
    def cam(*a, **kw):
        raise AssertionError("Khe không được chạy Git để báo")
    dong = bao("xong", "xong", wt=tmp_path, hang_doi=tmp_path / "hd", ban_giao=FILE, chay=cam)
    assert dong["commit"] is None and dong["ban_giao"]["commit"] is None
    assert dong["ban_giao"]["nhanh"] == "tram/bs-thu"
    assert json.loads((tmp_path / "hd").read_text()) == dong
```

- [ ] Step 2 — RED: `tests/chan_host/chay.sh -q tests/test_doi_ngu_bao.py`.
  RED trên mã cũ: **1 failed**, `AssertionError: Khe không được chạy Git để báo`. GREEN kiểm báo cáo/hàng đợi đều có `commit=None`.
- [ ] Step 3 — áp mã dưới đây (file mới chép trọn; bản vá áp theo thứ tự task):

**Modify: `tram/tho/bao.py`**

```diff
--- a/tram/tho/bao.py
+++ b/tram/tho/bao.py
@@ -78,17 +78,19 @@
             raise LoiBao(f"--{loai.replace('_', '-')} không kèm bàn giao hay loại câu hỏi")
         return _ghi(hang_doi, dong_de_nghi(loai, noi_dung, viec_moi))
     _kiem_tham_so(loai, noi_dung, ban_giao, loai_hoi)
+    qua_quan_ly = os.environ.get("TRAM_GIT_QUA_QUAN_LY") == "1"
     khoi = None
     if ban_giao:
-        khoi = {**doc_khoi(wt, ban_giao), "nhanh": _git(wt, "rev-parse", "--abbrev-ref", "HEAD", chay=chay),
+        khoi = {**doc_khoi(wt, ban_giao), "nhanh": (os.environ["TRAM_NHANH"] if qua_quan_ly else
+                _git(wt, "rev-parse", "--abbrev-ref", "HEAD", chay=chay)),
                 "commit": None, "luot": 0}
         kiem_cau_truc(khoi, can_chinh_thuc=loai == "xong")
-    if _git(wt, "status", "--porcelain", chay=chay):
+    if not qua_quan_ly and _git(wt, "status", "--porcelain", chay=chay):
         co_ten = _git(wt, "config", "user.email", chay=chay, kiem=False)
         _git(wt, "add", "-A", chay=chay)
         _git(wt, *(() if co_ten else DANH_TINH), "commit", "-q", "-m",
              f"{loai}: {(noi_dung.strip().splitlines() or [loai])[0][:72]}", chay=chay)
-    commit = _git(wt, "rev-parse", "HEAD", chay=chay)
+    commit = None if qua_quan_ly else _git(wt, "rev-parse", "HEAD", chay=chay)
     if khoi is not None:
         khoi["commit"] = commit
     dong = {"loai": loai, "noi_dung": noi_dung, "commit": commit,
```
**Modify: `tram/tho/mot_lan.py`**

```diff
--- a/tram/tho/mot_lan.py
+++ b/tram/tho/mot_lan.py
@@ -55,6 +55,8 @@
     so.ghi_lan_chay(nc.dong_ho())
     env = env_cli(thu_muc_cau_hinh=pc.k.thu_muc_cau_hinh, giao_id=p.giao_id, hang_doi=pc.hang_doi, wt=pc.wt,
                   path=ch.path_cli, ma_giao=p.ma_giao if ch.nho_url else None, nho_url=ch.nho_url)
+    if nc.ch.tren_may_b:
+        env |= {"TRAM_GIT_QUA_QUAN_LY": "1", "TRAM_NHANH": p.repo.nhanh}
     bo = BO_CLI[pc.k.cli]
     env[bo.bien_thu_muc] = env.pop("CLAUDE_CONFIG_DIR")
     cli = (nc.tao_cli or bo.tao_chay)(pc.principal.boc, khe_id=p.khe_id, kill=pc.principal.kill_nhom,
```
**Modify: `tram/tho/principal.py`**

```diff
--- a/tram/tho/principal.py
+++ b/tram/tho/principal.py
@@ -16,7 +16,7 @@
 SANDBOX_EXEC = "/usr/bin/sandbox-exec"
 BIEN_GIU = ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "TRAM_GIAO_ID", "TRAM_HANG_DOI", "TRAM_MA_GIAO", "TRAM_NHO_URL",
             "PATH", "LANG", "APP_ENV", "TMPDIR", "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0",
-            "GIT_CONFIG_KEY_1", "GIT_CONFIG_VALUE_1")
+            "GIT_CONFIG_KEY_1", "GIT_CONFIG_VALUE_1", "TRAM_GIT_QUA_QUAN_LY", "TRAM_NHANH")
 USER_RE = re.compile(r"[a-z_][a-z0-9_-]{0,30}")


```
**Modify: `vai/coder.md`**

```diff
--- a/vai/coder.md
+++ b/vai/coder.md
@@ -15,3 +15,6 @@
 - Thiếu thông tin nghiệp vụ, phải chọn phương án thay Đại ca → `tram bao --can-hoi --loai can_quyet_dinh "<câu hỏi cụ thể>"` rồi dừng.
 - Cần thao tác nguy hiểm (migrate dữ liệu thật, xoá dữ liệu, deploy, gửi khách) → `tram bao --can-hoi --loai thao_tac_nguy_hiem "<việc cần làm>"` rồi dừng. Không tự làm.
 - Bí sau khi đã thử → `tram bao --bi "<vướng ở đâu, đã thử gì>"`.
+
+Khi `TRAM_GIT_QUA_QUAN_LY=1`: không tự git add/commit; viết bàn giao rồi gọi `tram bao`.
+Quản lý thợ chốt commit sau khi lượt dừng sạch. Mốc tạm mới lưu tiến độ, chưa phải bản đã công bố.
```
**Modify: `vai/qc.md`**

```diff
--- a/vai/qc.md
+++ b/vai/qc.md
@@ -20,3 +20,6 @@
 ```

 `ket_luan` là `dat` hoặc `tra_ve`. `commit_code` chép đúng SHA trạm đưa trong lớp 4. Mỗi phát hiện: `{"muc": "chan" | "quan-trong" | "nho", "noi_dung": "…", "vi_tri": "file:dòng"}`. Có phát hiện mức `chan` thì kết luận `tra_ve`. Trong bàn giao, tiêu chí chưa đạt ghi `"dat": false` kèm bằng chứng — chỉ được khi kết luận `tra_ve`.
+
+Khi `TRAM_GIT_QUA_QUAN_LY=1`: không tự git add/commit; viết bàn giao rồi gọi `tram bao`.
+Quản lý thợ chốt commit sau khi lượt dừng sạch. Mốc tạm mới lưu tiến độ, chưa phải bản đã công bố.
```
**Modify: `vai/spec.md`**

```diff
--- a/vai/spec.md
+++ b/vai/spec.md
@@ -27,3 +27,6 @@

 - Thiếu thông tin nghiệp vụ hoặc phải chọn phương án thay Đại ca → `tram bao --can-hoi --loai can_quyet_dinh "<câu hỏi>"` rồi dừng.
 - Bí sau khi đã thử → `tram bao --bi "<vướng ở đâu, đã thử gì>"`.
+
+Khi `TRAM_GIT_QUA_QUAN_LY=1`: không tự git add/commit; viết bàn giao rồi gọi `tram bao`.
+Quản lý thợ chốt commit sau khi lượt dừng sạch. Mốc tạm mới lưu tiến độ, chưa phải bản đã công bố.
```

- [ ] Step 4 — GREEN: `tests/chan_host/chay.sh -q tests/test_doi_ngu_bao.py`; chạy hồi quy nêu dưới.
  Hồi quy: `tests/test_tram_bao.py tests/test_hang_doi.py`. Biến môi trường chỉ chọn cách báo;
  không là hàng rào quyền. Khe tự xoá cờ vẫn không ghi được Git nhờ ACL.

### Task 6: Cây riêng mỗi lượt, đóng quyền ở cổng cha và cấp thư viện root offline

**Scenario:** Đổi code→QC/khe; restart/dừng mềm; file thuộc UID khe; worktree kiểm offline.
**Files:** test `tests/test_doi_ngu_quyen.py`; các Create/Modify bên dưới.
**Interfaces:** B gọi `chuan_bi_b(nc, k, so, hop, tt, p)`; từ xa giữ luồng cũ.
`don_luot_b(pc, nc)` đóng cổng, xác nhận sạch UID rồi xoá cây; lỗi → `LoiThuHoi`, giữ sổ.
`cap_deps_b(wt, chay=...)` dùng reader/extractor Uq hiện có, không sửa module Uq.

- [ ] Step 1 — viết các test/fixture nguyên văn (không gọi sudo, không đổi UID thật):

```python
from pathlib import Path
import subprocess
import pytest
from tram.tho.quyen_cay_b import lenh_quyen_b, trao_quyen_b


def test_chi_cay_ma_va_hang_doi(tmp_path):
    wt = tmp_path / "wt"
    wt.mkdir()
    (wt / ".git").write_text("gitdir: /private/git/worktrees/wt")
    hd = tmp_path / "hang-doi.jsonl"
    ds = lenh_quyen_b(wt, hd, user="tram-khe1")
    assert any("deny write" in " ".join(a) and a[-1] == str(wt / ".git") for a in ds)
    find = next(a for a in ds if a[0] == "/usr/bin/find")
    assert "-prune" in find and str(wt / ".tram") in find
    assert all("delete_child" not in " ".join(a) for a in ds if "user:tram-khe1" in " ".join(a))
    assert not any("/private/git" in " ".join(a) for a in ds)
    assert any(a[-1] == str(hd) and "allow read,append" in a[-2] for a in ds)


def test_acl_hong_dung_ngay(tmp_path):
    (tmp_path / ".git").write_text("gitdir: /g")
    da = []
    def hong(argv, **kw):
        da.append(argv)
        raise subprocess.CalledProcessError(1, argv)
    with pytest.raises(subprocess.CalledProcessError):
        trao_quyen_b(tmp_path, tmp_path / "hd", user="tram-khe1", chay=hong)
    assert len(da) == 1


def test_khe_khac_khong_doc_cay_va_settings_duoc_doc_khong_duoc_ghi(tmp_path):
    (tmp_path / ".git").write_text("gitdir: /g")
    hd = tmp_path / "phieu/hang-doi.jsonl"
    hd.parent.mkdir()
    (hd.parent / "settings.json").touch()
    ds = lenh_quyen_b(tmp_path, hd, user="tram-khe1")
    assert ["/bin/chmod", "700", str(tmp_path)] in ds
    assert ["/bin/chmod", "700", str(hd.parent)] in ds
    assert any(a[-1] == str(hd.parent) and "allow list,search" in a[-2] for a in ds)
    assert any(a[-1] == str(hd.parent / "settings.json") and "allow read," in a[-2] for a in ds)


def test_quan_ly_co_quyen_ke_thua_doc_va_don_file_uid_khe(tmp_path):
    (tmp_path / '.git').write_text('gitdir: /g')
    ds = lenh_quyen_b(tmp_path, tmp_path / 'phieu/hang-doi.jsonl', user='tram-khe1')
    import pwd
    manager = f'user:{pwd.getpwuid(tmp_path.stat().st_uid).pw_name} allow '
    assert any(manager in ' '.join(a) and 'delete_child' in ' '.join(a)
               and 'file_inherit,directory_inherit' in ' '.join(a) for a in ds)
    assert any(a[-1] == str(tmp_path) and 'only_inherit' in a[-2] and manager in a[-2] for a in ds)
    assert not any('chown' == x for a in ds for x in a)
    assert any(a[-1] == str(tmp_path / '.tram') and 'file_inherit' in a[-2] and 'write' not in a[-2] for a in ds)


def test_cu_phap_acl_that_chi_trong_tmp(tmp_path):
    # Chỉ kiểm cú pháp macOS, không đổi UID/không sudo; nobody không phải hai tài khoản khe thật.
    wt, hd = tmp_path / 'cay', tmp_path / 'phieu/hang-doi.jsonl'
    (wt / '.tram').mkdir(parents=True)
    (wt / '.git').write_text('gitdir: /khong-dung')
    (wt / '.tram/goi.md').write_text('goi-gia')
    (wt / 'src').mkdir()
    (wt / 'src/a.py').write_text('x=1')
    hd.parent.mkdir()
    hd.touch()
    (hd.parent / 'settings.json').write_text('{}')
    trao_quyen_b(wt, hd, user='nobody', chay=subprocess.run)
    # File sinh sau còn đọc/dọn được; chủ quản lý không bị ACL của nobody chặn.
    (wt / 'src/moi').write_text('x')
    (wt / 'src/moi').unlink()
```

**Create: `tests/doi_deps_gia.py`**

```python
"""Bundle nhỏ trong tmp; không đọc/ghi kho root thật trong unit test."""
import json
from pathlib import Path
from test_phu_thuoc_kiem import archive, mau
from tram.kiem.deps_manifest import bam, ma_bundle
from tram.kiem.deps_root import doc_bundle


def bundle(tmp_path, monkeypatch, nguon):
    import tram.tho.deps_b as d
    import tram.quan_kiem.cap_deps as c
    m = mau()
    m['nguon'] = nguon
    blobs = {'python-site.tar': archive([('thu_vien.py', 'file', b'x=1\n')]),
             'node-modules.tar': archive([('vue/package.json', 'file', b'{}')])}
    for name, b in blobs.items():
        m['artifacts'][name] = {'sha256': bam(b), 'size': len(b),
                                'bytes': 4 if name == 'python-site.tar' else 2, 'entries': 1}
    root = tmp_path / 'bundle' / ma_bundle(m)
    root.mkdir(parents=True)
    (root / 'manifest.json').write_text(json.dumps(m))
    for name, b in blobs.items():
        (root / name).write_bytes(b)
    monkeypatch.setattr(d, 'GOC_DEPS', root.parent)
    monkeypatch.setattr(d, 'doc_root', lambda p, n: Path(p).read_bytes())
    monkeypatch.setattr(c, 'duong_manifest', lambda m: root / 'manifest.json')
    monkeypatch.setattr(c, 'doc_bundle', lambda p, nhan: doc_bundle(p, doc=lambda p, n: p.read_bytes(), nhan=nhan))
    return root, m
```

**Create: `tests/test_doi_ngu_vong_doi.py`**

```python
from dataclasses import replace
from types import SimpleNamespace
import subprocess
import pytest
from git_gia import git
from tho_chay_gia import dung_may, lay_phieu
from tram.tho.chuan_bi import chuan_bi
from tram.tho.phieu_chay import don_phieu


def dung(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    m.nc.chay_lenh = lambda *a, **kw: subprocess.CompletedProcess(a[0], 0)
    return m, k, so, hop, tt


def test_restart_giu_ban_sua_va_khong_cap_lai_acl(tmp_path, monkeypatch):
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    (pc.wt / 'a.txt').write_text('dang-do')
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    again = chuan_bi(m.nc, k, so, hop, tt)
    assert (again.wt / 'a.txt').read_text() == 'dang-do'
    assert git(again.wt, 'status', '--porcelain')  # Không tự commit/reset khi restart.
    assert not any('/usr/bin/find' in a for a in calls)


def test_code_qc_khac_luot_khac_khe_khong_dung_lai_cay(tmp_path, monkeypatch):
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    (pc.wt / 'chi-code.txt').write_text('khong-sang-qc')
    tt2 = replace(tt, phieu={**tt.phieu, 'luot': tt.phieu['luot'] + 1,
                            'khe_id': 'B/claude-2', 'buoc': 'qc', 'vai': 'qc'})
    qc = chuan_bi(m.nc, replace(k, ten='claude-2'), so, hop, tt2)
    assert qc.wt != pc.wt and not (qc.wt / 'chi-code.txt').exists()
    assert qc.thu_muc != pc.thu_muc


def test_don_xoa_cay_khong_go_acl_file_uid_khe(tmp_path, monkeypatch):
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    (pc.wt / 'file-khe').write_text('x')
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    don_phieu(pc, m.nc)
    assert not pc.wt.exists() and not pc.thu_muc.exists()
    assert not any('-a' in a or '/usr/bin/find' in a for a in calls)


def test_dung_mem_giu_commit_roi_don(tmp_path, monkeypatch):
    from tram.tho import ket_thuc
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    (pc.wt / 'a.txt').write_text('WIP cua khe')
    monkeypatch.setattr(ket_thuc, '_day', lambda *a: 'chua-cong-bo')
    ket_thuc.ket_thuc_mem(pc, m.nc, 'khe-tat')
    sha = git(pc.wt, 'rev-parse', 'HEAD')
    don_phieu(pc, m.nc)
    assert not pc.wt.exists()
    assert git(m.b.tho, 'show', f'{sha}:a.txt') == 'WIP cua khe'
    assert 'rac/' in git(m.b.tho, 'branch', '--contains', sha)


def test_don_hong_dong_cong_giu_so_khong_chmod_file_khe(tmp_path, monkeypatch):
    from tram.tho import luot_b
    from tram.kiem.vong_doi import LoiThuHoi
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    so.luu_phieu(tt)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    monkeypatch.setattr(luot_b.shutil, 'rmtree', lambda p: (_ for _ in ()).throw(PermissionError('UID khe')))
    with pytest.raises(LoiThuHoi):
        don_phieu(pc, m.nc)
    assert so.doc_phieu() is not None
    assert calls == [['/bin/chmod', '-N', str(pc.wt.parent)]]
    assert not (pc.wt.parent / 'san-sang').exists()


def test_tat_tho_giu_cay_nhung_dong_cong(tmp_path, monkeypatch):
    from tram.tho import phieu_chay
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    vk = SimpleNamespace(k=k, so=so, hop=hop, pc=None, buoc='', lenh='tat-tho')
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    assert phieu_chay.chay_phieu(m.nc, vk, tt) == 'tat-tho'
    gates = list(m.nc.goc_wt.iterdir())
    assert len(gates) == 1 and (gates[0] / 'san-sang').is_file()
    assert calls[-1] == ['/bin/chmod', '-N', str(gates[0])]


def test_khong_don_duoc_uid_khong_xoa_cay(tmp_path, monkeypatch):
    from tram.kiem.vong_doi import LoiThuHoi
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    m.nc.don_uid = lambda p: (_ for _ in ()).throw(LoiThuHoi('con-tien-trinh'))
    calls = []
    m.nc.chay_lenh = lambda a, **kw: calls.append(a)
    with pytest.raises(LoiThuHoi):
        don_phieu(pc, m.nc)
    assert pc.wt.exists() and calls[-1] == ['/bin/chmod', '-N', str(pc.wt.parent)]


def test_chuan_bi_loi_retry_dung_phieu_khong_reuse_nua_cay(tmp_path, monkeypatch):
    from tram.tho import chuan_bi_b
    from tram.kiem.vong_doi import LoiThuHoi
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    that = chuan_bi_b.tao_noi_dung
    monkeypatch.setattr(chuan_bi_b, 'tao_noi_dung', lambda *a: (_ for _ in ()).throw(ValueError('loi-deps')))
    with pytest.raises(LoiThuHoi):
        chuan_bi(m.nc, k, so, hop, tt)
    cong = next(m.nc.goc_wt.iterdir())
    (cong / 'cay/rac').touch()
    monkeypatch.setattr(chuan_bi_b, 'tao_noi_dung', that)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    assert not (pc.wt / 'rac').exists() and (cong / 'san-sang').is_file()


def test_phieu_cu_sau_restart_don_ma_khong_chuan_bi_lai(tmp_path, monkeypatch):
    import threading
    from tram.tho.vong_khe import VongKhe
    m, k, so, hop, tt = dung(tmp_path, monkeypatch)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    so.luu_phieu(tt)
    vk = VongKhe(m.nc, k)
    vk.phieu_moi, vk.lenh = tt, 'luot-cu'
    tat = threading.Event()
    monkeypatch.setattr(vk, 'khoi_dong', lambda: None)
    monkeypatch.setattr(vk, '_vong_nhip', lambda t: None)
    that = vk.so.xoa_phieu
    def xoa():
        assert not pc.wt.exists()
        that()
        tat.set()
    monkeypatch.setattr(vk.so, 'xoa_phieu', xoa)
    vk.chay(tat)
    assert so.doc_phieu() is None and not pc.wt.parent.exists()
```

**Create: `tests/test_doi_ngu_deps.py`**

```python
import io
import json
from pathlib import Path
import subprocess
import pytest
from tram.kiem.deps_manifest import KHOA_NGUON, bam
from tram.kiem.deps_root import GOC_DEPS, doc_bundle
from tram.kiem.deps_tar import giai_nen
from tram.kiem.toolchain import PYTHON


def test_worktree_ben_duoc_cap_python_node(tmp_path, monkeypatch):
    from tho_chay_gia import dung_may, lay_phieu
    from git_gia import git
    from tram.tho.chuan_bi import chuan_bi
    m = dung_may(tmp_path, monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    repo = Path(__file__).resolve().parents[1]
    for rel in KHOA_NGUON:
        p = m.b.tho / rel
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_bytes((repo / rel).read_bytes())
    git(m.b.tho, 'add', '-A')
    git(m.b.tho, '-c', 'user.name=Test', '-c', 'user.email=test@localhost', 'commit', '-qm', 'lock')
    tt.phieu['repo']['cha'] = git(m.b.tho, 'rev-parse', 'HEAD')
    tt.phieu['du_an'] = 'ben-station'
    tt.phieu['can_moi_truong_kiem'] = False
    m.b.tho.rename(m.b.tho.with_name('ben-station'))
    from doi_deps_gia import bundle
    bundle(tmp_path, monkeypatch, {rel: bam((repo / rel).read_bytes()) for rel in KHOA_NGUON})
    pc = chuan_bi(m.nc, k, so, hop, tt)
    assert (pc.wt / '.venv/bin/python').is_file()
    assert (pc.wt / 'frontend/node_modules/vue/package.json').is_file()


def test_env_duoc_dat_sau_boc_principal():
    from tram.tho.deps_b import boc_kiem_b
    pc = type('PC', (), {'p': type('P', (), {'du_an': 'ben-station'})(),
                         'principal': type('PR', (), {'boc': lambda self, a: ['sudo-gia', *a]})()})()
    assert boc_kiem_b(pc)(['tests/chan_host/chay.sh', '-q']) == [
        'sudo-gia', '/usr/bin/env', 'TRAM_KIEM_DA_CHUAN_BI=1', 'tests/chan_host/chay.sh', '-q']


@pytest.mark.parametrize('loi', ['doi-lock', 'thieu-bundle', 'sai-hash', 'symlink', 'dich-da-co'])
def test_deps_loi_khong_ghi_vao_dich_la(tmp_path, monkeypatch, loi):
    from doi_deps_gia import bundle
    from tram.tho.deps_b import cap_deps_b
    wt = tmp_path / 'cay'
    wt.mkdir()
    for rel in KHOA_NGUON:
        p = wt / rel
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(rel)
    root, m = bundle(tmp_path, monkeypatch, {rel: bam(rel.encode()) for rel in KHOA_NGUON})
    if loi == 'doi-lock':
        (wt / 'uv.lock').write_text('doi')
    elif loi == 'thieu-bundle':
        (root / 'manifest.json').unlink()
    elif loi == 'sai-hash':
        (root / 'python-site.tar').write_bytes(b'hong')
    elif loi == 'symlink':
        (wt / 'uv.lock').unlink()
        (wt / 'uv.lock').symlink_to(root / 'manifest.json')
    else:
        (wt / '.venv').mkdir()
    with pytest.raises((ValueError, subprocess.SubprocessError)):
        cap_deps_b(wt)
    assert not (wt / 'frontend/node_modules').exists()


def test_khong_chay_ma_repo_duoi_quan_ly(tmp_path, monkeypatch):
    from doi_deps_gia import bundle
    from tram.tho.deps_b import cap_deps_b
    wt = tmp_path / 'cay'
    wt.mkdir()
    for rel in KHOA_NGUON:
        p = wt / rel
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(rel)
    bundle(tmp_path, monkeypatch, {rel: bam(rel.encode()) for rel in KHOA_NGUON})
    (wt / 'sitecustomize.py').write_text('raise RuntimeError("MA-REPO-CHAY")')
    da = []
    def chay(a, **kw):
        da.append((a, kw))
        return subprocess.run(a, **kw)
    cap_deps_b(wt, chay=chay)
    assert (wt / '.venv/lib/python3.12/site-packages/thu_vien.py').is_file()
    assert all(a[:2] == [f'{PYTHON}/bin/python3.12', '-I'] and kw['timeout'] == 300 for a, kw in da)
```

- [ ] Step 2 — RED: `tests/chan_host/chay.sh -q tests/test_doi_ngu_quyen.py tests/test_doi_ngu_vong_doi.py tests/test_doi_ngu_deps.py`.
  Review vòng 2 đã đo trước bản vá: **6 failed** đúng lỗi — restart reset mất bản sửa, code/QC dùng lại
  cây, kết thúc không xoá cây, dừng mềm còn cây, thiếu Python/Node và thiếu wrapper cờ kiểm đã chuẩn bị.
  Ca QC đã sửa fixture `vai=qc` trước ghi RED; không tính ValidationError của fixture làm bằng chứng.
  Ca dependency đầu dùng bundle root thật để tái hiện; test thường dùng bundle nhỏ trong tmp ở trên.
- [ ] Step 3 — áp mã nguyên văn theo thứ tự:

**Create: `tram/tho/quyen_cay_b.py`**

```python
"""ACL chỉ cấp một lần trên cây mới; thu quyền ở cổng cha, không chmod file UID khe."""
import pwd
from pathlib import Path
from tram.tho.principal import USER_RE

QUYEN_CAY = 'read,write,append,execute,delete,readattr,readextattr,readsecurity'
QUYEN_THU_MUC = 'list,search,add_file,add_subdirectory,readattr,readextattr,readsecurity'
QUAN_LY = 'read,write,append,execute,delete,delete_child,readattr,writeattr,readextattr,writeextattr,readsecurity'


def lenh_quyen_b(wt: Path, hang_doi: Path, *, user: str) -> list[list[str]]:
    if not USER_RE.fullmatch(user):
        raise ValueError('Tên principal không hợp lệ')
    if not (wt / '.git').is_file() or (wt / '.git').is_symlink():
        raise ValueError('Cần worktree do quản lý tạo')
    def acl(p, quyen, who=user):
        return ['/bin/chmod', '+a', f'user:{who} allow {quyen}', str(p)]
    ds = [['/bin/chmod', '700', str(wt)], ['/bin/chmod', '700', str(hang_doi.parent)],
          acl(hang_doi.parent, 'list,search,readattr,readsecurity'),
          acl(wt, QUYEN_THU_MUC),
          ['/bin/chmod', '+a', f'user:{user} deny write,append,delete,writeattr,writeextattr,writesecurity,chown',
           str(wt / '.git')]]
    # Kế thừa cho file mới kể cả umask 077. Quản lý đọc/ghi/dọn được file UID khe;
    # chủ file cố ý gỡ ACL thì thất bại đóng, không mở sudo root để cưỡng ép.
    for who, quyen in ((pwd.getpwuid(wt.stat().st_uid).pw_name, QUAN_LY), (user, QUYEN_CAY)):
        ds.append(['/usr/bin/find', str(wt), '-mindepth', '1', '(', '-path', str(wt / '.git'), '-o', '-path',
                   str(wt / '.tram'), ')', '-prune', '-o', '(', '-type', 'd', '-o', '-type', 'f', ')',
                   '-exec', '/bin/chmod', '+a', f'user:{who} allow {quyen},file_inherit,directory_inherit', '{}', '+'])
        ds.append(acl(wt, f'{quyen},only_inherit,file_inherit,directory_inherit', who))
    # .tram và .git không thể bị thay tên: root không cấp delete_child, .tram không cấp delete.
    ds += [acl(wt / '.tram', 'read,execute,readattr,readsecurity,file_inherit,directory_inherit'),
           acl(hang_doi, 'read,append,readattr,readsecurity')]
    for p in [*(wt / '.tram').glob('goi*.md'), *(hang_doi.parent / n for n in ('settings.json', 'mcp.json'))]:
        if p.is_file():
            ds.append(acl(p, 'read,readattr,readsecurity'))
    return ds


def trao_quyen_b(wt, hang_doi, *, user, chay):
    for argv in lenh_quyen_b(wt, hang_doi, user=user):
        chay(argv, check=True, capture_output=True, timeout=30)
```

**Create: `tram/tho/luot_b.py`**

```python
"""Mỗi phiếu/lượt B có cổng 0700 do quản lý giữ; không dùng lại cây giữa hai khe."""
import os
import shutil
import subprocess
from pathlib import Path

from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.ngu_canh import rid
from tram.tho.worktree import GIT, duong_dan_worktree


def git(kho, *args):
    return subprocess.run([*GIT, '-C', str(kho), *args], check=True, capture_output=True, text=True, timeout=600)


def dong_cong(cong, nc):
    if cong.is_symlink() or cong.stat().st_uid != os.getuid():
        raise ValueError('Cổng lượt không thuộc quản lý')
    nc.chay_lenh(['/bin/chmod', '-N', str(cong)], check=True, capture_output=True, timeout=30)
    cong.chmod(0o700)


def xoa_cay(cong, kho):
    # Cổng đã đóng, UID đã dọn. Không chmod/chown file của khe; rmtree không theo symlink.
    (cong / 'san-sang').unlink(missing_ok=True)
    wt = cong / 'cay'
    if wt.exists():
        shutil.rmtree(wt)
    # --force nhận cả worktree thiếu thư mục; chỉ gỡ registration của đúng lượt.
    ds = git(kho, 'worktree', 'list', '--porcelain').stdout.splitlines()
    if f'worktree {wt}' in ds:
        git(kho, 'worktree', 'remove', '--force', str(wt))
    shutil.rmtree(cong)


def chuan_bi_b(nc, k, so, hop, tt, p):
    from tram.tho.chuan_bi import PhieuDangChay
    from tram.tho.chuan_bi_b import tao_noi_dung
    duong_dan_worktree(nc.goc_wt, p.du_an, p.repo.nhanh)  # Giữ kiểm tên dự án/nhánh cũ.
    cong = nc.goc_wt / rid(p.giao_id, p.luot, p.khe_id)
    kho, wt, hd = nc.goc_kho / p.du_an, cong / 'cay', cong / 'phieu'
    pr = nc.principal(k, wt, f'{p.giao_id}-{p.luot}')
    try:
        if cong.exists():
            dong_cong(cong, nc)
            if not (cong / 'san-sang').is_file():
                xoa_cay(cong, kho)
        if not cong.exists():
            cong.mkdir(parents=True, mode=0o700)
            dong_cong(cong, nc)
            git(kho, 'fetch', '-q', 'origin')
            git(kho, 'worktree', 'add', '--detach', str(wt), p.repo.cha)
            tao_noi_dung(nc, p, wt, hd, pr)
            (cong / 'san-sang').touch(mode=0o600)
        if getattr(pr, 'user', None):
            nc.chay_lenh(['/bin/chmod', '+a', f'user:{pr.user} allow search', str(cong)],
                         check=True, capture_output=True, timeout=30)
        return PhieuDangChay(p, tt, k, so, hop, wt, hd, pr, hd / 'settings.json',
                            hd / 'mcp.json' if (hd / 'mcp.json').is_file() else None)
    except (OSError, ValueError, subprocess.SubprocessError):
        if cong.exists():
            dong_cong(cong, nc)
        raise LoiThuHoi('Chuẩn bị lượt B lỗi; giữ phiếu và cổng đóng để đối soát') from None


def don_luot_b(pc, nc):
    cong = pc.wt.parent
    try:
        dong_cong(cong, nc)
        nc.don_khe(pc.k)
        xoa_cay(cong, nc.goc_kho / pc.p.du_an)
    except (OSError, ValueError, subprocess.SubprocessError):
        raise LoiThuHoi('Dọn lượt B lỗi; giữ phiếu, không nhận lượt mới') from None


def don_phieu_cu_b(nc, k, tt):
    from types import SimpleNamespace
    from tram.phieu.mo_hinh import Phieu
    p = Phieu.model_validate(tt.phieu)
    cong = nc.goc_wt / rid(p.giao_id, p.luot, p.khe_id)
    if cong.exists():
        don_luot_b(SimpleNamespace(wt=cong / 'cay', p=p, k=k), nc)
```

**Create: `tram/tho/chuan_bi_b.py`**

```python
"""Chuẩn bị cây mới sau cổng đóng; retry cùng phiếu không reset bản sửa hay cấp lại ACL."""
import os
from tram.cau_hinh.du_an import nap_du_an
from tram.chay_cli.lenh_claude import ghi_file_phieu
from tram.kiem.moi_truong import LoiMoiTruongKiem, chep_moi_truong_kiem
from tram.tho.quyen_cay_b import trao_quyen_b
from tram.tho.worktree import _them_exclude


def tao_noi_dung(nc, p, wt, hd, pr):
    import subprocess
    from tram.tho.chuan_bi import loai_khoi_git
    _them_exclude(wt, lambda a, **kw: subprocess.run(a, timeout=60, **kw))
    if os.path.lexists(wt / '.tram'):
        raise ValueError('Cây nguồn chứa .tram')
    (wt / '.tram').mkdir(mode=0o700)
    (wt / '.tram/goi.md').write_text(p.goi_ngu_canh, encoding='utf-8')
    if p.can_moi_truong_kiem:
        mt = nap_du_an(p.du_an).moi_truong_kiem
        if mt is None:
            raise LoiMoiTruongKiem('Thiếu môi trường kiểm')
        if p.du_an == "ben-station":
            from tram.quan_kiem.cap_deps import kiem_dich_env
            kiem_dich_env(mt.dich)
        loai_khoi_git(wt, mt.dich)
        chep_moi_truong_kiem(mt.file, wt, mt.dich)
    if p.du_an == 'ben-station':
        from tram.tho.deps_b import cap_deps_b
        cap_deps_b(wt, chay=nc.chay_lenh)
    hd.mkdir(mode=0o700)
    (hd / 'hang-doi.jsonl').touch(mode=0o600)
    ghi_file_phieu(hd, p, nho=bool(nc.ch.chay.nho_url))
    if getattr(pr, 'user', None):
        trao_quyen_b(wt, hd / 'hang-doi.jsonl', user=pr.user, chay=nc.chay_lenh)
```

**Create: `tram/tho/deps_b.py`**

```python
"""B dùng bundle root đã cài cho Uq; không đổi Uq, không chạy mã repo bằng UID quản lý."""
import subprocess
from tram.kiem.deps_manifest import KHOA_NGUON, bam, doc_manifest
from tram.kiem.deps_root import GOC_DEPS, doc_root
from tram.quan_kiem.cap_deps import cap_deps


def cap_deps_b(wt, *, chay=subprocess.run):
    if (wt / 'frontend').is_symlink() or any((wt / rel).is_symlink() for rel in KHOA_NGUON):
        raise ValueError('Nguồn dependency không được là symlink')
    nguon = {rel: bam((wt / rel).read_bytes()) for rel in KHOA_NGUON}
    ds = [doc_manifest(doc_root(p, 65536)) for p in sorted(GOC_DEPS.glob('*/manifest.json'))]
    ds = [m for m in ds if m['nguon'] == nguon]
    if len(ds) != 1:
        raise ValueError('Cần đúng một bundle root khớp lock ben-station')
    def chay_helper(argv, *, kill, **kw):
        # Helper -I/stdlb của runtime tin cậy, timeout do cap_deps áp; không chạy mã cây lượt.
        return chay(argv, **kw)
    cap_deps(wt, ds[0], boc=lambda a: a, kill=None, chay=chay_helper)


def boc_kiem_b(pc):
    def boc(argv):
        return pc.principal.boc(['/usr/bin/env', 'TRAM_KIEM_DA_CHUAN_BI=1', *argv])
    return boc if pc.p.du_an == 'ben-station' else pc.principal.boc
```

**Modify: `tram/tho/chuan_bi.py`**

```diff
--- a/tram/tho/chuan_bi.py
+++ b/tram/tho/chuan_bi.py
@@ -65,6 +65,9 @@
 def chuan_bi(nc: NguCanhTho, k: KheCauHinh, so: SoKhe, hop: HopThu, tt: TrangThaiPhieu) -> PhieuDangChay | str:
     """Trả `PhieuDangChay`, hoặc `ly_do` của `bao.bi` khi không chạy được (`thieu-moi-truong-kiem`, `loi-may-tho`)."""
     p = Phieu.model_validate(tt.phieu)
+    if nc.ch.tren_may_b:
+        from tram.tho.luot_b import chuan_bi_b
+        return chuan_bi_b(nc, k, so, hop, tt, p)
     try:
         wt = duong_dan_worktree(nc.goc_wt, p.du_an, p.repo.nhanh)
         kq = chuan_bi_worktree(nc.goc_kho / p.du_an, wt, nhanh=p.repo.nhanh, cha=p.repo.cha, bead_id=p.bead_id,
```

**Modify: `tram/tho/phieu_chay.py`**

```diff
--- a/tram/tho/phieu_chay.py
+++ b/tram/tho/phieu_chay.py
@@ -32,7 +32,10 @@
 def don_phieu(pc: PhieuDangChay, nc: NguCanhTho) -> None:
     go_khoa(pc.wt)
     xoa_ref_tam(pc.wt, pc.p)
-    if getattr(pc.principal, "user", None):
+    if nc.ch.tren_may_b:
+        from tram.tho.luot_b import don_luot_b
+        don_luot_b(pc, nc)
+    elif getattr(pc.principal, "user", None):
         git_wt = Path(subprocess.run(["git", "-C", str(pc.wt), "rev-parse", "--absolute-git-dir"],
                                      capture_output=True, text=True, check=True).stdout.strip())
         for lenh in lenh_trao_quyen(pc.wt, git_wt, pc.thu_muc, user=pc.principal.user, thu=True):
@@ -100,6 +103,9 @@
         vk.pc, vk.buoc = None, "ranh"
         if kt == "tat-tho":
             go_khoa(pc.wt)                      # giữ phieu.json + hộp thư: khởi động lại chạy tiếp
+            if nc.ch.tren_may_b:
+                from tram.tho.luot_b import dong_cong
+                dong_cong(pc.wt.parent, nc)
         else:
             don_phieu(pc, nc)
     return kt
```

**Modify: `tram/tho/mo_coi_khe.py`**

```diff
--- a/tram/tho/mo_coi_khe.py
+++ b/tram/tho/mo_coi_khe.py
@@ -27,3 +27,16 @@
                       and t.get("giao_id") == p.giao_id):
             gui_su_kien(nc, hop, p, "chay.xong", {"lan": x["lan"], "ket_thuc": "mo-coi"}, x["lan"])
     return tt, False
+
+
+def don_phieu_cu(vk):
+    """Nhịp từ chối phiếu giữ qua restart: dọn lượt B trước khi bỏ sổ."""
+    try:
+        if vk.nc.ch.tren_may_b:
+            from tram.tho.luot_b import don_phieu_cu_b
+            don_phieu_cu_b(vk.nc, vk.k, vk.phieu_moi)
+        vk.so.xoa_phieu()
+        vk.phieu_moi, vk.han_giu = None, None
+        return True
+    except LoiThuHoi:
+        return False
```

**Modify: `tram/tho/vong_khe.py`**

```diff
--- a/tram/tho/vong_khe.py
+++ b/tram/tho/vong_khe.py
@@ -13,7 +13,7 @@
 from tram.tho.han_muc_ranh import DocHanMucRanh
 from tram.tho.hop_thu import HopThu
 from tram.tho.khach import LoiKhachTram
-from tram.tho.mo_coi_khe import don_mo_coi_khe
+from tram.tho.mo_coi_khe import don_mo_coi_khe, don_phieu_cu
 from tram.tho.ngu_canh import NguCanhTho
 from tram.tho.phieu_chay import chay_phieu
 from tram.tho.so_khe import SoKhe, TrangThaiPhieu, gio_utc
@@ -98,9 +98,9 @@
         nhip.start()
         while not tat.is_set() and not self.hong:
             if self.lenh in DUNG_CUNG and self.phieu_moi is not None:
-                self.so.xoa_phieu()
-                self.phieu_moi = None
-                self.han_giu = None
+                self.hong = not don_phieu_cu(self)
+                if self.hong:
+                    break
             if self.phieu_moi is None or not self.da_xac_nhan:
                 tat.wait(0.2)
                 continue
```

**Modify: `tram/tho/don_dep.py`**

```diff
--- a/tram/tho/don_dep.py
+++ b/tram/tho/don_dep.py
@@ -10,7 +10,7 @@


 def don_da_dong(nc: NguCanhTho) -> list[str]:
-    if not nc.goc_wt.is_dir():
+    if nc.ch.tren_may_b or not nc.goc_wt.is_dir():
         return []
     wt = {(d.name, w.name): w for d in nc.goc_wt.iterdir() if d.is_dir() for w in d.iterdir() if w.is_dir()}
     if not wt:
```

**Modify: `tram/tho/mot_lan.py`**

```diff
--- a/tram/tho/mot_lan.py
+++ b/tram/tho/mot_lan.py
@@ -59,7 +59,9 @@
         env |= {"TRAM_GIT_QUA_QUAN_LY": "1", "TRAM_NHANH": p.repo.nhanh}
     bo = BO_CLI[pc.k.cli]
     env[bo.bien_thu_muc] = env.pop("CLAUDE_CONFIG_DIR")
-    cli = (nc.tao_cli or bo.tao_chay)(pc.principal.boc, khe_id=p.khe_id, kill=pc.principal.kill_nhom,
+    from tram.tho.deps_b import boc_kiem_b
+    boc = boc_kiem_b(pc) if nc.ch.tren_may_b else pc.principal.boc
+    cli = (nc.tao_cli or bo.tao_chay)(boc, khe_id=p.khe_id, kill=pc.principal.kill_nhom,
                      khi_bat_dau=lambda pid: ghi_pid(so.pid, pid=pid, giao_id=p.giao_id, luot=p.luot, lan=lan),
                      khi_han_muc=so.luu_han_muc, tran_token_ra=p.ngan_sach.token_ra - tt.token_ra)
     hen = threading.Timer(max(0.0, giay_con_lai(pc, nc.dong_ho())), dung.set)
```

**Modify: `tests/test_tho_chuan_bi.py`**

```diff
--- a/tests/test_tho_chuan_bi.py
+++ b/tests/test_tho_chuan_bi.py
@@ -18,12 +18,12 @@
     m = dung_may(tmp_path, monkeypatch, [])
     k, so, hop, tt = lay_phieu(m)
     pc = chuan_bi(m.nc, k, so, hop, tt)
-    assert git(pc.wt, "rev-parse", "HEAD") == m.b.cha and pc.wt == m.nc.goc_wt / "hr-codex" / "hr-1"
+    assert git(pc.wt, "rev-parse", "HEAD") == m.b.cha and pc.wt.parent.parent == m.nc.goc_wt
     assert (pc.wt / ".tram" / "goi.md").read_text() == pc.p.goi_ngu_canh
     assert (pc.wt / ".env.testing").read_text() == "APP_ENV=testing\n" and pc.hang_doi.exists()
     assert git(pc.wt, "status", "--porcelain") == ""                          # .env.testing bị loại khỏi git
     allow = json.loads(pc.settings.read_text())["permissions"]["allow"]
-    assert "Bash(python3 kiem_ok.py)" in allow and pc.mcp is None and pc.thu_muc == so.hang_doi / pc.p.giao_id
+    assert "Bash(python3 kiem_ok.py)" in allow and pc.mcp is None and pc.thu_muc == pc.wt.parent / "phieu"
     import pytest
     from tram.tho.chuan_bi import loai_khoi_git
     from tram.kiem.moi_truong import LoiMoiTruongKiem
@@ -39,13 +39,15 @@
     m.nc.chay_lenh = lambda argv, **kw: da.append(argv)
     k, so, hop, tt = lay_phieu(m)
     pc = chuan_bi(m.nc, k, so, hop, tt)
-    assert [a[1] for a in da] == [str(pc.wt), git(pc.wt, "rev-parse", "--absolute-git-dir"), str(pc.thu_muc)]
-    assert all(a[0] == "/usr/bin/find" and a[10:12] == ["/bin/chmod", "+a"] and "user:tram-k-b-claude-1 allow" in a[12]
-               for a in da)
+    assert pc.hang_doi.is_file()
+    assert any(a[-1] == str(pc.hang_doi) and "append" in a[-2] for a in da)
+    assert any(a[-1] == str(pc.settings) and "allow read," in a[-2] for a in da)
+    assert not any(a[-1] == git(pc.wt, "rev-parse", "--absolute-git-dir") for a in da)


 def test_khong_chuan_bi_duoc_tra_ly_do(tmp_path, monkeypatch):
     m = dung_may(tmp_path, monkeypatch, [])
+    m.nc.ch = replace(m.nc.ch, tram_api="https://may-b.example.test")
     k, so, hop, tt = lay_phieu(m)
     assert chuan_bi(replace(m.nc, goc_kho=tmp_path / "khong-co"), k, so, hop, tt) == "loi-may-tho"
     (tmp_path / "env.testing").unlink()
```

**Modify: `tests/test_tho_lenh_chay.py`**

```diff
--- a/tests/test_tho_lenh_chay.py
+++ b/tests/test_tho_lenh_chay.py
@@ -35,7 +35,8 @@
     tat = threading.Event()
     th = threading.Thread(target=chay_may, args=(m.nc, tat), kwargs={"chu_ky_don": 0.2}, daemon=True)
     th.start()
-    wt = m.nc.goc_wt / "hr-codex" / "hr-1"
+    def con_cay():
+        return any(m.nc.goc_wt.glob("*/cay"))
     het = time.monotonic() + 40
     da_dong = False
     while time.monotonic() < het:
@@ -45,12 +46,12 @@
                     kho.ghi_su_kien("hr-codex", "bead.dong", {"du_an": "hr-codex", "bead_id": "hr-1"},
                                     luc=m.t.gio[0], bead_id="hr-1", tac_nhan="tram/giao-viec")
                 da_dong = True
-        if da_dong and not wt.exists():
+        if da_dong and not con_cay():
             break
         time.sleep(0.1)
     tat.set()
     th.join(timeout=30)
-    assert da_dong and not wt.exists()
+    assert da_dong and not con_cay()


 def test_luu_token_qua_stdin_khong_qua_argv():
```

- [ ] Step 4 — GREEN: chạy lại ba file test Step 2; hồi quy `test_tho_chuan_bi.py`,
  `test_tho_lenh_chay.py`, `test_phu_thuoc_kiem.py`, `test_phu_thuoc_luot.py`, `test_do_dai_ma.py`,
  `test_vong_import.py`. Số đo review cuối plan; không coi test giả UID là phép đo macOS.

**Vòng đời:** một thư mục cha 0700 do quản lý sở hữu cho `(giao_id, luot, khe_id)`, worktree detached +
phiếu nằm bên trong. Chỉ mở `search` sau khi chuẩn bị xong; `san-sang` nằm ngoài vùng khe ghi.
Retry cùng phiếu giữ thay đổi chưa commit, không cấp ACL hay giải nén lại. Chuẩn bị dở không có dấu thì
đóng cổng, dọn đúng cây rồi tạo lại. Kết thúc mềm giữ WIP theo cơ chế hiện có trước dọn; tắt daemon giữ
cây/phiếu nhưng đóng cổng; lỗi dọn/UID dừng khe. Phiếu cũ sau restart cũng dọn trước xoá sổ.
Không thu ACL từng file, không chmod/chown file UID khe. ACL kế thừa cho quản lý cho phép đọc/dọn file mới
kể cả umask 077; khe cố ý gỡ quyền khiến dọn lỗi thì đóng cổng, giữ phiếu để đối soát, không lờ lỗi.

**Thư viện:** tìm đúng một manifest root có hash bốn file nguồn khớp; helper có `-I` và hạn 300 giây,
kiểm runtime/lock/đích trống, hash archive rồi giải nén Python/Node bằng helper G4 đã có. Thiếu/sai thì
không mở cổng, không chạy CLI. `.venv` và `node_modules` riêng từng lượt; không dùng symlink cache chung,
không tải mạng. Wrapper đặt `TRAM_KIEM_DA_CHUAN_BI=1` sau sudo cho cả CLI và lệnh kiểm sau xong (Task 7).
Cờ này không là chứng cứ an toàn; Uq vẫn tự cấp/kiểm thư viện trong lượt kiểm riêng.

### Task 7: Quản lý chốt SHA sau thu hồi và giữ kiểm lại/QC

**Scenario:** Hoàn tất một việc; Mốc tạm hoặc báo cáo giả SHA.
**Files:** test `tests/test_doi_ngu_chot.py`; các file Create/Modify được ghi ngay dưới mã.
- [ ] Step 1 — tạo test nguyên văn:

```python
from types import SimpleNamespace
from tram.tho.chot_bao_b import chot_bao_b


def test_bo_sha_agent_gan_sha_quan_ly():
    pc = SimpleNamespace(wt="/work", p=SimpleNamespace(luot=4, repo=SimpleNamespace(nhanh="tram/bs-thu")))
    dong = {"commit": "a" * 40, "ban_giao": {"commit": "a" * 40, "luot": 999, "nhanh": "main"}}
    ra = chot_bao_b(pc, dong, chot=lambda wt, msg: "b" * 40)
    assert ra["commit"] == ra["ban_giao"]["commit"] == "b" * 40
    assert ra["ban_giao"]["luot"] == 4 and ra["ban_giao"]["nhanh"] == "tram/bs-thu"
    assert dong["ban_giao"]["commit"] == "a" * 40


def test_moc_b_khong_cong_bo(monkeypatch):
    from tram.tho import theo_doi
    pc = SimpleNamespace(tt=SimpleNamespace(ban_giao_tam=None), wt="/work", p=object(),
                         hop=SimpleNamespace(gui_mot=lambda *a: None))
    nc = SimpleNamespace(ch=SimpleNamespace(tren_may_b=True, chay=SimpleNamespace(day="kho-tho")),
                         khach=object(), cho_thu_lai=0)
    monkeypatch.setattr(theo_doi, "day_va_cong_bo", lambda *a, **kw: (_ for _ in ()).throw(AssertionError()))
    obj = SimpleNamespace(pc=pc, nc=nc)
    theo_doi.TheoDoi._moc(obj, {"commit": "a" * 40, "ban_giao": {"buoc_tiep": ["x"]}}, None)
    assert pc.tt.ban_giao_tam == {"buoc_tiep": ["x"]}


def test_chot_git_that_bo_sha_gia_trong_hang_doi(tmp_path, monkeypatch):
    from git_gia import git
    from tho_chay_gia import FILE_BG, dung_may, khoi_bg, lay_phieu
    from tram.tho.chuan_bi import chuan_bi
    from tram.tho.bao import bao
    from tram.tho.hang_doi import xu_ly_hang_doi
    m = dung_may(tmp_path, monkeypatch, [])
    pc = chuan_bi(m.nc, *lay_phieu(m))
    (pc.wt / FILE_BG).parent.mkdir(parents=True)
    (pc.wt / FILE_BG).write_text(khoi_bg("Tên kết thúc 'ỷ' không mất byte"))
    monkeypatch.setenv("TRAM_GIT_QUA_QUAN_LY", "1")
    monkeypatch.setenv("TRAM_NHANH", pc.p.repo.nhanh)
    dong = bao("xong", "xong", wt=pc.wt, hang_doi=pc.hang_doi, ban_giao=FILE_BG)
    assert dong["commit"] is None and git(pc.wt, "status", "--porcelain")
    ds, _ = xu_ly_hang_doi(pc.hang_doi, khe_id=pc.p.khe_id, giao_id=pc.p.giao_id, luot=pc.p.luot)
    than = ds[0].than
    than["commit"] = "a" * 40
    ra = chot_bao_b(pc, than)
    assert ra["commit"] == ra["ban_giao"]["commit"] == git(pc.wt, "rev-parse", "HEAD")
    assert ra["commit"] != "a" * 40 and not git(pc.wt, "status", "--porcelain")
    assert ra["ban_giao"]["luot"] == pc.p.luot
```

- [ ] Step 2 — RED: `tests/chan_host/chay.sh -q tests/test_doi_ngu_chot.py`.
  RED đã đo với helper trả nguyên báo cáo và `_moc` cũ, fixture đầy đủ: **3 failed** — SHA giả còn nguyên, mốc gọi công bố và cây Git thật chưa được quản lý commit. Không dùng AttributeError do fixture thiếu trường làm bằng chứng.
- [ ] Step 3 — áp mã dưới đây (file mới chép trọn; bản vá áp theo thứ tự task):

**Create: `tram/tho/chot_bao_b.py`**

```python
"""Chốt sau thu hồi; SHA do quản lý đọc, không tin SHA trong hàng đợi."""
from tram.tho.day import luu_wip


def chot_bao_b(pc, dong, *, chot=luu_wip):
    commit = chot(pc.wt, "xong: quản lý thợ chốt bản sửa")
    ra = {**dong, "commit": commit}
    if "ban_giao" in dong:
        ra["ban_giao"] = {**dong["ban_giao"], "commit": commit, "nhanh": pc.p.repo.nhanh,
                          "luot": pc.p.luot}
    return ra
```
**Modify: `tram/tho/ket_thuc.py`**

```diff
--- a/tram/tho/ket_thuc.py
+++ b/tram/tho/ket_thuc.py
@@ -44,6 +44,8 @@
         noi_dung = (noi_dung + f"\nChưa công bố được trước hạn chót: WIP giữ cục bộ ở nhánh {rac}; snapshot là commit "
                     "trạm đã công bố gần nhất (không phải toàn bộ việc đã làm).").strip()
     bg = pc.tt.ban_giao_tam or dung_ban_giao_tam(pc.wt, pc.p, commit, ghi_chu=noi_dung[:500])
+    if nc.ch.tren_may_b:
+        bg = {**bg, "commit": commit, "nhanh": pc.p.repo.nhanh, "luot": pc.p.luot}
     loai = "het_han_muc" if ly_do == "het_han_muc" else "bi"
     bao(pc, nc, {"loai": loai, "noi_dung": noi_dung[:4000], "ban_giao": bg, "commit": commit,
                  **({"ly_do": ly_do} if loai == "bi" else {})}, request_id)
@@ -53,7 +55,11 @@
 def ket_thuc_xong(pc: PhieuDangChay, nc: NguCanhTho, dong: dict) -> str:
     """CLI đã thoát. Worktree sạch (`wip: sau xong`) → lệnh kiểm của thợ → công bố → `bao.xong` nguyên kết quả."""
     p, ch = pc.p, nc.ch.chay
-    luu_wip(pc.wt, "wip: sau xong")
+    if nc.ch.tren_may_b:
+        from tram.tho.chot_bao_b import chot_bao_b
+        dong = chot_bao_b(pc, dong)
+    else:
+        luu_wip(pc.wt, "wip: sau xong")
     bg = BanGiao.model_validate(dong["ban_giao"])
     ket_luan = None
     if p.buoc == "qc" and (pc.wt / bg.file_ban_giao).is_file():
@@ -65,7 +71,9 @@
         cam = cam_tu_lenh_tho(nc.khach, p.du_an, pc.wt, p.repo.nhanh_chinh)
     except OSError:
         loi_cam = LOI_CAM
-    kq = kiem_sau_xong(pc.wt, p, bg, thu_muc_log=nc.goc / "log" / "kiem", boc=pc.principal.boc,
+    from tram.tho.deps_b import boc_kiem_b
+    boc = boc_kiem_b(pc) if nc.ch.tren_may_b else pc.principal.boc
+    kq = kiem_sau_xong(pc.wt, p, bg, thu_muc_log=nc.goc / "log" / "kiem", boc=boc,
                        env=moi_truong_kiem({"PATH": ch.path_cli, "LANG": "C.UTF-8"}),
                        them_cam=giao.duong_dan_cam,
                        bat_buoc=cam, loi_cam=loi_cam,
```
**Modify: `tram/tho/theo_doi.py`**

```diff
--- a/tram/tho/theo_doi.py
+++ b/tram/tho/theo_doi.py
@@ -37,6 +37,8 @@
         pc, nc = self.pc, self.nc
         if than.get("ban_giao"):
             pc.tt.ban_giao_tam = than["ban_giao"]
+        if nc.ch.tren_may_b:
+            return  # Mốc B lưu trong sổ phiếu; chỉ chốt/công bố sau khi thu hồi CLI.
         if than.get("commit") and len(than["commit"]) == 40:
             day_va_cong_bo(pc.wt, pc.p, than["commit"], khach=nc.khach, phuong_an=nc.ch.chay.day,
                            han=time.monotonic() + 60, cho=nc.cho_thu_lai, dung=ngung)
```

**Modify: `tests/test_tho_theo_doi_ket_thuc.py`**

```diff
--- a/tests/test_tho_theo_doi_ket_thuc.py
+++ b/tests/test_tho_theo_doi_ket_thuc.py
@@ -4,6 +4,7 @@
 import sys
 import threading
 from contextlib import closing
+from dataclasses import replace
 from types import SimpleNamespace

 from git_gia import git
@@ -19,6 +20,8 @@
 def bao(pc, *args):
     env = {"PATH": "/usr/bin:/bin", "TRAM_GIAO_ID": pc.p.giao_id, "TRAM_HANG_DOI": str(pc.hang_doi),
            "PYTHONPATH": str(GOC), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
+    if git(pc.wt, "rev-parse", "--abbrev-ref", "HEAD") == "HEAD":
+        env.update(TRAM_GIT_QUA_QUAN_LY="1", TRAM_NHANH=pc.p.repo.nhanh)
     subprocess.run([sys.executable, "-c", "import sys; from tram.cli import main; sys.exit(main(sys.argv[1:]))",
                     "bao", *args], cwd=pc.wt, env=env, check=True, capture_output=True)

@@ -29,13 +32,15 @@
                                                           (loai,))]


-def chuan_bi_phieu(tmp_path, monkeypatch, **kw):
+def chuan_bi_phieu(tmp_path, monkeypatch, *, tu_xa=False, **kw):
     m = dung_may(tmp_path, monkeypatch, [], **kw)
+    if tu_xa:
+        m.nc.ch = replace(m.nc.ch, tram_api="https://may-b.example.test")
     return m, chuan_bi(m.nc, *lay_phieu(m))


 def test_moc_cong_bo_va_giu_ban_giao_tam_can_hoi_dung_ngay(tmp_path, monkeypatch):
-    m, pc = chuan_bi_phieu(tmp_path, monkeypatch)
+    m, pc = chuan_bi_phieu(tmp_path, monkeypatch, tu_xa=True)
     (pc.wt / "a.txt").write_text("1")
     bao(pc, "--moc", "mốc 1")
     with open(pc.hang_doi, "a") as f:
@@ -62,7 +67,7 @@
     assert ket_thuc_xong(pc, m.nc, td.xong) == "cong_bo"
     x = su_kien(m, "bao.xong")[0]
     assert x["loi_ban_giao"] == [] and x["commit"] == git(pc.wt, "rev-parse", "HEAD")
-    assert git(pc.wt, "log", "-1", "--format=%s") == "wip: sau xong" and x["ban_giao"]["luot"] == pc.p.luot
+    assert git(pc.wt, "log", "-1", "--format=%s") == "xong: quản lý thợ chốt bản sửa" and x["ban_giao"]["luot"] == pc.p.luot


 def test_qc_doc_khoi_qc_tieu_chi_false_ma_tra_ve_khong_loi(tmp_path, monkeypatch):
```

- [ ] Step 4 — GREEN: `tests/chan_host/chay.sh -q tests/test_doi_ngu_chot.py`; chạy hồi quy nêu dưới.
  Hồi quy và bài tích hợp bắt buộc: `tests/test_tho_lenh_chay.py`, `tests/test_tho_theo_doi_ket_thuc.py`.
  Ca từng hỏng ở bản bối cảnh: `test_chay_may_tron_vong_roi_don_worktree_bead_da_dong`;
  phải đo lại và sửa trong đúng luồng nếu còn đỏ, không bỏ test hay tăng thời gian chờ để che lỗi.

### Task 8: Mở mọi việc đủ điều kiện, giữ phạm vi ben-station và hạn mức

**Scenario:** Mở mọi việc đủ điều kiện của ben-station; mở rộng việc vẫn giữ hạn mức.
**Files:** test `tests/test_doi_ngu_giao.py`; cấu hình và nguồn dự án của bộ giao bên dưới.
**Interfaces:** dùng `cac_du_an` sẵn có cho tick/chọn/cấp, không thêm callback lọc bead.

- [ ] Step 1 — tạo test nguyên văn:

```python
from dataclasses import replace
from types import SimpleNamespace
import pytest
from tram.cau_hinh.giao_viec import CauHinhGiaoViec, nap_cau_hinh_giao_viec
from tram.cau_hinh.pham_vi_giao import danh_sach
from tram.giao_viec.noi_that import dung_bo_that


@pytest.mark.parametrize("ds", [[], "ben-station", [True], ["../hr"]])
def test_sai_pham_vi_khong_mo_rong(ds):
    with pytest.raises(ValueError):
        danh_sach({"du_an": ds}, "du_an")


def test_nap_cau_hinh_khong_tu_bat(tmp_path):
    p = tmp_path / "cau-hinh.yaml"
    p.write_text("giao_viec:\n  du_an: [ben-station]\n")
    ch = nap_cau_hinh_giao_viec(p)
    assert not ch.bat and ch.du_an == ("ben-station",)
    assert not hasattr(ch, "bead")
    p.write_text("giao_viec:\n  bead: [bs-thu]\n")
    with pytest.raises(ValueError):
        nap_cau_hinh_giao_viec(p)


@pytest.mark.parametrize("bead_id", ["bs-mot", "bs-hai"])
def test_moi_bead_ben_duoc_xet_hr_khong_doc_claim_cap(tmp_path, monkeypatch, bead_id):
    from giao_viec_gia import dung, bug
    from tram.giao_viec import noi_that
    t = dung(tmp_path, bug(bead_id))
    try:
        ben = replace(t.da, ten="ben-station")
        monkeypatch.setattr(noi_that, "cac_du_an_that", lambda _: [t.da, ben])
        bo = dung_bo_that(CauHinhGiaoViec(du_an=("ben-station",)), t.bo.ch)
        doc = []
        def tao_bd(da):
            doc.append(da.ten)
            assert da.ten == "ben-station"
            return t.g
        bo = replace(bo, tao_bd=tao_bd, mo_kho=t.bo.mo_kho, kho_git=t.bo.kho_git, dong_ho=t.bo.dong_ho)
        assert [d.ten for d in bo.cac_du_an()] == ["ben-station"]
        dx = bo.chon("B/claude-1", None)
        assert dx is not None and dx.bead_id == bead_id and dx.du_an == "ben-station"
        assert t.g.beads[bead_id].status == "in_progress" and doc == ["ben-station"]
        assert not bo.con_hop_le(SimpleNamespace(du_an="hr-codex", bead_id="hr-1"))
        assert bo.con_hop_le(dx)
        monkeypatch.setattr(noi_that, "cac_du_an_that", lambda _: [])
        assert not bo.con_hop_le(dx)  # bat_ghi vừa tắt: nguồn đọc lại không còn dự án.
    finally:
        t.kho.close()
```

- [ ] Step 2 — RED: `tests/chan_host/chay.sh -q tests/test_doi_ngu_giao.py`.
  RED đã đo với trường `du_an`, parser stub và nguồn dự án chưa lọc: **7 failed**; dữ liệu sai không bị từ chối
  và nguồn vẫn chứa HR. Không coi lỗi import là RED hành vi. GREEN: hai bead ben khác nhau đều được claim.
- [ ] Step 3 — áp mã theo thứ tự:

**Create: `tram/cau_hinh/pham_vi_giao.py`**

```python
"""Danh sách cho phép; thiếu khoá giữ tương thích, danh sách rỗng tường minh bị từ chối."""
import re


def danh_sach(raw, ten):
    if ten not in raw:
        return ()
    ds = raw[ten]
    if not isinstance(ds, list) or not ds or any(
            not isinstance(x, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", x) for x in ds):
        raise ValueError(f"giao_viec.{ten} cần danh sách tên không rỗng")
    return tuple(dict.fromkeys(ds))
```
**Modify: `tram/cau_hinh/giao_viec.py`**

```diff
--- a/tram/cau_hinh/giao_viec.py
+++ b/tram/cau_hinh/giao_viec.py
@@ -20,7 +20,7 @@
 from tram.giao_viec.principal_kiem import PrincipalKiem
 from tram.tho.quyen_kiem import goc_hop_le

-KHOA = {"bat", "chu_ky_giay", "thu_muc_kiem", "principal_kiem"}      # principal_kiem: khoá cũ, chỉ để đối chiếu
+KHOA = {"bat", "chu_ky_giay", "thu_muc_kiem", "principal_kiem", "du_an"}
 CHU_KY = (30, 150)


@@ -30,6 +30,7 @@
     chu_ky_giay: int = 120
     thu_muc_kiem: Path | None = None
     principal_kiem: PrincipalKiem | None = None
+    du_an: tuple[str, ...] = ()


 def _thu_muc(raw, pk: PrincipalKiem | None) -> Path | None:
@@ -59,4 +60,6 @@
     pk = doc_principal_kiem(p)
     if bat and pk is None:
         raise ValueError("giao_viec.bat cần cach_ly.tram_kiem — kiểm lại không bao giờ chạy dưới quyền tram-api (G4)")
-    return CauHinhGiaoViec(bat, chu_ky, _thu_muc(gv.get("thu_muc_kiem"), pk), pk)
+    from tram.cau_hinh.pham_vi_giao import danh_sach
+    return CauHinhGiaoViec(bat, chu_ky, _thu_muc(gv.get("thu_muc_kiem"), pk), pk,
+                          danh_sach(gv, "du_an"))
```
**Modify: `tram/giao_viec/noi_that.py`**

```diff
--- a/tram/giao_viec/noi_that.py
+++ b/tram/giao_viec/noi_that.py
@@ -52,7 +52,7 @@
     from tram.de_nghi.vong import NguonDeNghi
     from tram.phieu.kho import mo_kho_phieu
     from tram.quan_kiem.client import CongTuXa, kiem_tu_xa
-    cac = lambda: cac_du_an_that(thu_muc_du_an)
+    cac = lambda: [d for d in cac_du_an_that(thu_muc_du_an) if not cg.du_an or d.ten in cg.du_an]
     return BoGiaoViec(cac_du_an=cac,
                       tao_bd=lambda da: Bd(da.duong_dan, actor=ASSIGNEE), mo_kho=mo_kho_phieu, ch=ch,
                       dong_ho=lambda: datetime.now(timezone.utc), kiem_tu_xa=kiem_tu_xa, cong=CongTuXa(),
```

- [ ] Step 4 — GREEN: `tests/chan_host/chay.sh -q tests/test_doi_ngu_giao.py`.
  Hồi quy: `tests/test_noi_giao_viec.py tests/test_bo_giao_viec.py tests/test_giao_viec_api.py`
  và `tests/test_ngan_sach_giao.py tests/test_khe_cau_dao.py tests/test_nhip_han_muc.py`.
  Không sửa ngưỡng, ngân sách, quota hay số lượt; nhật ký chặn phải có 0 dòng mới.
- [ ] Step 5 — ghi số thật và QC; không commit trong phiên review.

### Task 9: Sổ tay một lệnh và log đã lọc

**Scenario:** Bật lại daemon bị disable; Remote github đã có, origin thiếu; tắt giao giữ kênh nhận máy A.
`bat_ghi: true` của ben-station trên main (71ff846) độc lập với giao việc. `giao(c, False)` không ghi file dự án;
nhánh bật vẫn đảm bảo True. `con_phieu_b()` đọc kho qua `tram_home()`, chỉ đọc và không tạo DB khi thiếu.
**Files:** test `tests/test_doi_ngu_cong_cu.py`; các file Create/Modify được ghi ngay dưới mã.
- [ ] Step 1 — tạo test nguyên văn:

```python
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cong-cu"))
from doi_ngu_io import Chay, Dung
import doi_ngu_io
from doi_ngu_chuan_bi import can_tat


def test_log_khong_ghi_dau_ra_con(tmp_path, monkeypatch):
    monkeypatch.setattr(doi_ngu_io.tempfile, "mkdtemp", lambda **kw: str(tmp_path))
    monkeypatch.setattr(doi_ngu_io.subprocess, "run", lambda *a, **kw:
                        SimpleNamespace(returncode=1, stdout="bi-mat", stderr="bi-mat"))
    c = Chay()
    with pytest.raises(Dung):
        c.goi("thu", ["gia"])
    assert c.log.read_text() == "thu: 1\n"
    assert c.log.stat().st_mode & 0o777 == 0o600


def test_khong_co_service_chua_du_phai_disable():
    class Gia:
        def goi(self, ten, argv, **kw):
            return (SimpleNamespace(returncode=113, stderr="Could not find service", stdout="")
                    if ten == "dich-vu-tho" else SimpleNamespace(stdout='"vn.tram.tho" => false'))
    with pytest.raises(Dung, match="disable"):
        can_tat(Gia())


def test_kho_tho_nhan_commit_moi_tu_remote_tracking_cua_nguon(tmp_path):
    from git_gia import git
    from kho_kiem_gia import dung_kho
    from doi_ngu_chuan_bi import dong_bo_nguon
    k = dung_kho(tmp_path)
    tho = tmp_path / "tho"
    git(tmp_path, "clone", "-q", str(k.kho), str(tho))
    moi = k.day("main", {"moi.txt": "moi"})
    git(k.kho, "fetch", "-q", "origin")
    assert git(k.kho, "rev-parse", "main") != moi
    class Gia:
        def goi(self, ten, argv, **kw):
            assert argv[:5] == ["sudo", "-H", "-u", "tram-tho", "git"]
            assert argv[5:7] == ["-C", str(tho)]
            return git(tho, *argv[7:])
    dong_bo_nguon(Gia(), tho)
    assert git(tho, "rev-parse", "origin/main") == moi
    assert git(tho, "cat-file", "-t", moi) == "commit"


def test_bat_giao_khong_gioi_han_bead_giu_ngan_sach(tmp_path, monkeypatch):
    import yaml
    import doi_ngu_b as m
    from tram.phieu.kho import KhoPhieu
    repo = tmp_path / "repo"
    (repo / "du-an").mkdir(parents=True)
    for ten in ("ben-station", "hr-codex"):
        (repo / f"du-an/{ten}.yaml").write_text("bat_ghi: false\n")
    ch = tmp_path / "cau-hinh.yaml"
    ch.write_text("giao_viec: {bat: false, bead: [bs-cu]}\nhan_muc: {ngung: 90}\n")
    kho = KhoPhieu(tmp_path / "su-kien.db")
    kho.close()
    monkeypatch.setattr(m, "REPO", repo)
    monkeypatch.setattr(m, "CAU_HINH", ch)
    monkeypatch.setattr("builtins.input", lambda *a: (_ for _ in ()).throw(AssertionError("hoi bead")))
    c = SimpleNamespace(goi=lambda *a, **kw: None)
    m.giao(c, True)
    raw = yaml.safe_load(ch.read_text())
    assert raw["giao_viec"] == {"bat": True, "du_an": ["ben-station"]}
    assert raw["han_muc"] == {"ngung": 90}
    assert yaml.safe_load((repo / "du-an/ben-station.yaml").read_text())["bat_ghi"] is True
    assert yaml.safe_load((repo / "du-an/hr-codex.yaml").read_text())["bat_ghi"] is False


@pytest.mark.parametrize("truong", ["tu_merge", "tu_deploy"])
def test_bat_giao_tu_choi_khi_tu_dong_dang_bat(tmp_path, monkeypatch, truong):
    from dataclasses import replace
    from contextlib import closing
    from tram.phieu.kho import KhoPhieu
    from tram.tu_dong.luu import doi_cai_dat
    import doi_ngu_b as m
    with closing(KhoPhieu(tmp_path / "su-kien.db")) as kho:
        doi_cai_dat(kho.db, "ben-station", lambda cd: replace(cd, **{truong: True}), tac_nhan="fixture")
    ch = tmp_path / "cau-hinh.yaml"
    ch.write_text("giao_viec: {bat: false}\n")
    monkeypatch.setattr(m, "CAU_HINH", ch)
    repo = tmp_path / "repo"
    (repo / "du-an").mkdir(parents=True)
    (repo / "du-an/ben-station.yaml").write_text("bat_ghi: false\n")
    monkeypatch.setattr(m, "REPO", repo)
    with pytest.raises(Dung, match="tu-dong"):
        m.giao(SimpleNamespace(goi=lambda *a, **kw: None), True)
    assert ch.read_text() == "giao_viec: {bat: false}\n"


@pytest.mark.parametrize("bat_ghi", ["true", "false"])
def test_tat_giao_giu_nguyen_kenh_nhan_yeu_cau(tmp_path, monkeypatch, bat_ghi):
    import yaml
    import doi_ngu_b as m
    repo = tmp_path / "repo"
    (repo / "du-an").mkdir(parents=True)
    p = repo / "du-an/ben-station.yaml"
    truoc = f"# Kênh nhận yêu cầu độc lập với giao việc\nbat_ghi: {bat_ghi}\n"
    p.write_text(truoc)
    ch = tmp_path / "cau-hinh.yaml"
    ch.write_text("giao_viec: {bat: true}\nhan_muc: {ngung: 90}\n")
    monkeypatch.setattr(m, "REPO", repo)
    monkeypatch.setattr(m, "CAU_HINH", ch)
    m.giao(SimpleNamespace(goi=lambda *a, **kw: None), False)
    assert p.read_text() == truoc
    raw = yaml.safe_load(ch.read_text())
    assert raw["giao_viec"]["bat"] is False
    assert raw["han_muc"] == {"ngung": 90}


def test_con_phieu_b_doc_tram_home_chi_doc(tmp_path, monkeypatch):
    import sqlite3
    import doi_ngu_b as m
    home = tmp_path / "tram home # rieng"
    home.mkdir()
    p = home / "su-kien.db"
    connect = sqlite3.connect
    db = connect(p)
    db.execute("CREATE TABLE phieu (may_id TEXT, trang_thai TEXT)")
    db.executemany("INSERT INTO phieu VALUES (?, ?)",
                   [("B", "hieu_luc"), ("B", "xong"), ("A", "hieu_luc")])
    db.commit()
    db.close()
    monkeypatch.setenv("TRAM_HOME", str(home))
    def doc(dia_chi, **kw):
        assert dia_chi == p.as_uri() + "?mode=ro"
        assert kw == {"uri": True, "timeout": 5}
        return connect(dia_chi, **kw)
    monkeypatch.setattr(m.sqlite3, "connect", doc)
    assert m.con_phieu_b() == 1
    p.unlink()
    with pytest.raises(sqlite3.OperationalError):
        m.con_phieu_b()
    assert not p.exists()


def test_runtime_dung_bundle_root_va_chi_mo_doc_sau_chuan_bi(tmp_path, monkeypatch):
    import shutil
    import subprocess
    import doi_ngu_chuan_bi as c
    repo, runtime, log = tmp_path / 'repo', tmp_path / 'runtime', tmp_path / 'log'
    (repo / 'du-an').mkdir(parents=True)
    log.mkdir()
    (repo / 'du-an/ben-station.yaml').write_text('ten: ben-station\nmoi_truong_kiem: {file: /x, dich: .env.testing}\n')
    cfg = tmp_path / 'cau-hinh.yaml'
    cfg.write_text('{}')
    for name, value in {'REPO': repo, 'RUNTIME': runtime, 'TRAM': runtime / '.venv/bin/tram',
                        'CAU_HINH': cfg}.items():
        monkeypatch.setattr(c, name, value)
    monkeypatch.setattr(c, 'can_tat', lambda c: None)
    da = []
    def goi(ten, argv, **kw):
        da.append((ten, argv))
        if ten == 'clone-runtime':
            assert runtime.stat().st_mode & 0o777 == 0o700
            shutil.copytree(repo / 'du-an', runtime / 'du-an')
        if ten == 'deps-root':
            assert 'cap_deps_b' in argv[3] and '-I' in argv
            (runtime / '.venv/bin').mkdir(parents=True)
        if ten == 'runtime-chi-doc':
            subprocess.run(argv, check=True)
    obj = type('C', (), {'goc': log, 'goi': staticmethod(goi), 'ghi': staticmethod(lambda *a: None)})()
    c.chuan_bi(obj)
    assert runtime.stat().st_mode & 0o777 == 0o755
    assert not any('uv' in a or 'sync' in a for _, a in da)
    assert c.TRAM.stat().st_mode & 0o777 == 0o755
    assert str(runtime) in c.TRAM.read_text()
```

- [ ] Step 2 — RED: `tests/chan_host/chay.sh -q tests/test_doi_ngu_cong_cu.py`.
  RED với `Chay.goi`/`can_tat` stub: **2 failed**, `DID NOT RAISE Dung`. Bổ sung: fetch nguồn trả SHA cũ (**1 failed**) và tự merge/deploy đang bật vẫn ghi cấu hình (**2 failed**); đã sửa refspec và kiểm công tắc chỉ đọc trước ghi.
  Vòng 3 trên mã vòng 2: **3 failed, 7 deselected** — hai ca tắt làm đổi nguyên văn YAML dự án
  (`AssertionError`), một ca URI kho không theo `TRAM_HOME` (`AssertionError`); mọi dữ liệu ở tmp.
- [ ] Step 3 — áp mã dưới đây (file mới chép trọn; bản vá áp theo thứ tự task):

**Create: `cong-cu/doi_ngu_io.py`**

```python
"""I/O cho sổ tay B: log chỉ tên bước và mã, không ghi đầu ra con."""
import os
import subprocess
import tempfile
from pathlib import Path


class Dung(RuntimeError):
    pass


class Chay:
    def __init__(self):
        self.goc = Path(tempfile.mkdtemp(prefix="doi-ngu-b-", dir="/private/tmp"))
        self.log = self.goc / "ket-qua.txt"
        self.log.touch(mode=0o600)
        print(f"Log: {self.log}", flush=True)

    def ghi(self, ten, ma):
        with self.log.open("a") as f:
            f.write(f"{ten}: {ma}\n")

    def goi(self, ten, argv, *, han=600, input=None, check=True, env=None):
        try:
            r = subprocess.run(argv, input=input, capture_output=True, text=True, timeout=han, env=env)
        except (OSError, subprocess.TimeoutExpired):
            self.ghi(ten, "KHONG-KET-LUAN")
            raise Dung(ten) from None
        self.ghi(ten, r.returncode)
        if check and r.returncode:
            raise Dung(ten)
        return r

    def tuong_tac(self, ten, argv):
        # Terminal hiện màn đăng nhập; không thu/copy/log stdout hoặc stdin.
        ma = subprocess.call(argv)
        self.ghi(ten, ma)
        if ma:
            raise Dung(ten)


def ghi_yaml(p, raw):
    import yaml
    p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, ten = tempfile.mkstemp(prefix=".doi-ngu-", dir=p.parent)
    try:
        with os.fdopen(fd, "w") as f:
            yaml.safe_dump(raw, f, allow_unicode=True, sort_keys=False)
            f.flush()
            os.fsync(f.fileno())
        if p.exists():
            fd, _ = tempfile.mkstemp(prefix="truoc-doi-ngu-", dir=p.parent)
            with os.fdopen(fd, "wb") as f:
                f.write(p.read_bytes())
        os.replace(ten, p)
    finally:
        Path(ten).unlink(missing_ok=True)
```
**Create: `cong-cu/doi_ngu_chuan_bi.py`**

```python
"""Chuẩn bị runtime/kho/cấu hình B; chỉ người vận hành gọi sau duyệt."""
import os
import re
from pathlib import Path

from doi_ngu_io import Dung, ghi_yaml

REPO = Path("/Users/dai-ca/Developer/Ben Station")
RUNTIME = Path("/Users/Shared/tram-tho-code")
TRAM = RUNTIME / ".venv/bin/tram"
PYTHON = "/usr/local/tram/toolchains/python/3.12.15-20261009/bin/python3.12"
THO = Path("/Users/tram-tho")
CAU_HINH = Path("/Users/dai-ca/.tram/cau-hinh.yaml")
PLIST = Path("/Library/LaunchDaemons/vn.tram.tho.plist")


def lenh_tho(*args):
    return ["sudo", "-H", "-u", "tram-tho", str(TRAM), "tho", *args]


def can_tat(c):
    r = c.goi("dich-vu-tho", ["launchctl", "print", "system/vn.tram.tho"], check=False, han=30)
    if r.returncode == 0 or "Could not find service" not in r.stderr:
        raise Dung("tho-chua-xac-nhan-da-dung")
    r = c.goi("disable", ["launchctl", "print-disabled", "system"], han=30)
    if not re.search(r'"vn\.tram\.tho"\s*=>\s*true', r.stdout):
        raise Dung("tho-chua-disable")


def chuan_bi(c):
    import yaml
    can_tat(c)
    raw_gv = yaml.safe_load(CAU_HINH.read_text()) or {}
    if raw_gv.get("giao_viec", {}).get("bat", False):
        raise Dung("giao-viec-dang-bat")
    c.goi("sao-luu-su-kien", [str(REPO / ".venv/bin/tram"), "chu", "sao-luu"])
    if RUNTIME.exists():
        raise Dung("runtime-da-co-doi-soat-truoc-khi-cai-lai")
    RUNTIME.mkdir(mode=0o700)
    c.goi("clone-runtime", ["git", "clone", "--no-local", "--no-hardlinks", str(REPO), str(RUNTIME)])
    script = "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
    script += "from tram.tho.deps_b import cap_deps_b; cap_deps_b(Path(sys.argv[1]))"
    c.goi("deps-root", [PYTHON, "-I", "-c", script, str(RUNTIME)])
    TRAM.write_text(f"#!{RUNTIME}/.venv/bin/python\nimport sys\nsys.path.insert(0, {str(RUNTIME)!r})\n"
                    "from tram.cli import main\nsys.exit(main())\n")
    TRAM.chmod(0o755)
    env = {**os.environ, "TRAM_REPO": str(RUNTIME), "UV_PYTHON_DOWNLOADS": "never"}
    c.goi("cai-chi-tho", [str(REPO / ".venv/bin/tram"), "chu", "cai-dat-tho", "--co-che", "user",
        "--khe", "claude-1=tram-khe1", "--khe", "claude-2=tram-khe2", "--chi-tho", "--giu-tat", "--dong-y"], env=env)
    for user in ("tram-tho", "tram-khe1", "tram-khe2"):
        c.goi("chan-nha-dai-ca", ["chmod", "+a", f"user:{user} deny list,search", "/Users/dai-ca"], han=30)
    for n in (1, 2):
        user = f"tram-khe{n}"
        c.goi("thu-muc-claude", ["sudo", "-u", user, "mkdir", "-p", f"/Users/{user}/claude"], han=30)
        c.goi("quyen-nha-khe", ["sudo", "chmod", "700", f"/Users/{user}"], han=30)
        c.goi("quyen-claude", ["sudo", "chmod", "700", f"/Users/{user}/claude"], han=30)
        c.goi("quan-ly-di-qua", ["sudo", "chmod", "+a", "user:tram-tho allow search", f"/Users/{user}"], han=30)
        c.goi("quan-ly-xem-thu-muc", ["sudo", "chmod", "+a", "user:tram-tho allow search,list",
                                   f"/Users/{user}/claude"], han=30)
    for rel in (".tram", ".tram/log", "tram", "tram/kho", "tram/worktrees", ".tram/hang-doi/B"):
        c.goi("thu-muc-tho", ["sudo", "-u", "tram-tho", "mkdir", "-p", str(THO / rel)], han=30)
    for rel in ("", ".tram"):
        c.goi("kin-nha-quan-ly", ["sudo", "chmod", "700", str(THO / rel)], han=30)
    for n in (1, 2):
        user = f"tram-khe{n}"
        for rel in ("", ".tram", ".tram/hang-doi", ".tram/hang-doi/B", "tram", "tram/worktrees"):
            c.goi("di-qua", ["sudo", "chmod", "+a", f"user:{user} allow search", str(THO / rel)], han=30)
        q = THO / f".tram/hang-doi/B/claude-{n}"
        c.goi("hang-doi-khe", ["sudo", "-u", "tram-tho", "mkdir", "-p", str(q)], han=30)
        c.goi("kin-hang-doi", ["sudo", "chmod", "700", str(q)], han=30)
        c.goi("quyen-hang-doi", ["sudo", "chmod", "+a", f"user:{user} allow list,search", str(q)], han=30)
    raw = {"may_id": "B", "tram_api": "http://127.0.0.1:7700", "chay": {"day": "kho-tho",
        "path": f"{RUNTIME}/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin", "thu_muc_tram": "/Users/dai-ca/.tram"},
        "khe": [{"ten": f"claude-{n}", "cli": "claude", "principal": f"user:tram-khe{n}",
        "thu_muc_cau_hinh": f"/Users/tram-khe{n}/claude", "ten_goi_nho": f"Tho Claude {n}",
        "vai_uu_tien": ["spec", "coder"] if n == 1 else ["qc"]} for n in (1, 2)]}
    p = c.goc / "tho-ung-vien.yaml"
    ghi_yaml(p, raw)
    c.goi("ung-vien", ["sudo", "install", "-o", "tram-tho", "-m", "600", str(p), str(THO / ".tram/tho-ung-vien.yaml")])
    da = RUNTIME / "du-an/ben-station.yaml"
    raw = yaml.safe_load(da.read_text())
    raw["duong_dan"] = str(THO / "tram/kho/ben-station")
    raw["moi_truong_kiem"]["file"] = str(RUNTIME / "du-an/ben-station.env.testing")
    ghi_yaml(da, raw)
    da.chmod(0o644)
    c.goi("runtime-chi-doc", ["find", str(RUNTIME), "(", "-type", "d", "-o", "-type", "f", ")",
                             "-exec", "chmod", "go-w", "{}", "+"])
    RUNTIME.chmod(0o755)
    c.ghi("chuan-bi", "XONG-GIU-TAT")


def kho(c):
    import yaml
    can_tat(c)
    def remote(ten):
        r = c.goi("doc-remote", ["git", "-C", str(REPO), "remote", "get-url", ten], check=False, han=30)
        return r.stdout.strip() if r.returncode == 0 else None
    github, origin = remote("github"), remote("origin")
    if github not in ("git@github.com:Hungbennn/ben-station.git", "https://github.com/Hungbennn/ben-station.git"):
        raise Dung("github-chua-khop")
    if origin not in (None, github):
        raise Dung("origin-khac-github")
    if origin is None:
        c.goi("them-origin", ["git", "-C", str(REPO), "remote", "add", "origin", github], han=30)
    nguon = Path("/Users/Shared/tram-nguon/ben-station")
    link = Path("/Users/dai-ca/.tram/kho-kiem/ben-station")
    dich = THO / "tram/kho/ben-station"
    if nguon.exists() or link.exists() or link.is_symlink() or dich.exists():
        raise Dung("kho-da-co-can-doi-soat-khong-ghi-de")
    nguon.parent.mkdir(mode=0o700, exist_ok=True)
    c.goi("clone-nguon", ["git", "clone", "--no-checkout", "--config", "core.hooksPath=/dev/null", github, str(nguon)])
    link.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    link.symlink_to(nguon)
    c.goi("nguon-di-qua", ["chmod", "+a", "user:tram-tho allow search", str(nguon.parent)], han=30)
    c.goi("nguon-doc", ["find", str(nguon), "(", "-type", "d", "-o", "-type", "f", ")", "-exec", "chmod", "+a",
        "user:tram-tho allow read,execute,readattr,readsecurity,file_inherit,directory_inherit", "{}", "+"])
    for safe in (nguon, nguon / ".git"):
        c.goi("git-doc-nguon", ["sudo", "-H", "-u", "tram-tho", "git", "config", "--global", "--add",
                               "safe.directory", str(safe)], han=30)
    c.goi("clone-tho", ["sudo", "-u", "tram-tho", "git", "-c", f"safe.directory={nguon}/.git", "clone",
        "--no-local", "--no-hardlinks", "--config", "core.hooksPath=/dev/null", str(nguon), str(dich)])
    dong_bo_nguon(c, dich)
    for p in (THO, THO / "tram", THO / "tram/kho"):
        c.goi("tram-di-qua", ["sudo", "chmod", "+a", "user:hungle allow search", str(p)], han=30)
    c.goi("tram-doc-kho", ["sudo", "find", str(dich), "(", "-type", "d", "-o", "-type", "f", ")", "-exec", "chmod", "+a",
        "user:hungle allow read,execute,readattr,readsecurity,file_inherit,directory_inherit", "{}", "+"])
    raw = yaml.safe_load(CAU_HINH.read_text()) or {}
    if raw.get("giao_viec", {}).get("bat", False):
        raise Dung("giao-viec-dang-bat")
    cb = raw.setdefault("cong_bo", {})
    cb["phuong_an"] = "lai"
    cb.setdefault("kho_tho", {})["B"] = str(THO / "tram/kho")
    ghi_yaml(CAU_HINH, raw)


def dong_bo_nguon(c, dich):
    # Nguồn --no-checkout chỉ fetch origin/*; refs/heads/main của nó không tự tiến.
    c.goi("refspec-nguon", ["sudo", "-H", "-u", "tram-tho", "git", "-C", str(dich), "config", "--replace-all",
                           "remote.origin.fetch", "+refs/remotes/origin/*:refs/remotes/origin/*"], han=30)
    c.goi("fetch-nguon", ["sudo", "-H", "-u", "tram-tho", "git", "-C", str(dich), "fetch", "origin"])
```
**Create: `cong-cu/doi_ngu_b.py`**

```python
"""Sổ tay một lệnh từng bước; chỉ chạy ở B sau khi được duyệt kịch bản."""
import os
import plistlib
import subprocess
import sqlite3
import sys
import time
from pathlib import Path

from doi_ngu_io import Chay, Dung, ghi_yaml
from doi_ngu_chuan_bi import CAU_HINH, PLIST, REPO, RUNTIME, THO, TRAM, can_tat, chuan_bi, kho, lenh_tho


def keychain(c):
    can_tat(c)
    for u in ("tram-tho", "tram-khe1", "tram-khe2"):
        p = Path(f"/Users/{u}/Library/Keychains/login.keychain-db")
        r = c.goi("co-keychain", ["sudo", "test", "-f", str(p)], check=False, han=30)
        if r.returncode == 1:
            c.goi("thu-muc-keychain", ["sudo", "-u", u, "mkdir", "-p", str(p.parent)], han=30)
            c.tuong_tac("tao-keychain", ["sudo", "-H", "-u", u, "security", "create-keychain", str(p)])
        elif r.returncode != 0:
            raise Dung("khong-doc-duoc-keychain")
        c.tuong_tac("chon-keychain", ["sudo", "-H", "-u", u, "security", "default-keychain", "-s", str(p)])
        c.tuong_tac("mo-keychain", ["sudo", "-H", "-u", u, "security", "unlock-keychain", str(p)])


def dang_nhap(c, n):
    can_tat(c)
    u = f"tram-khe{n}"
    # Không chụp đầu ra: trình duyệt/mã đăng nhập chỉ Đại ca nhìn ở Terminal.app.
    c.tuong_tac("dang-nhap-claude", ["sudo", "-H", "-u", u, "env",
        f"CLAUDE_CONFIG_DIR=/Users/{u}/claude", "/opt/homebrew/bin/claude", "auth", "login"])
    c.tuong_tac("xem-danh-tinh", ["sudo", "-H", "-u", u, "env",
        f"CLAUDE_CONFIG_DIR=/Users/{u}/claude", "/opt/homebrew/bin/claude", "auth", "status"])
    for p in (f"/Users/{u}/claude/.credentials.json", f"/Users/{u}/.claude/.credentials.json"):
        r = c.goi("khong-credential-file", ["sudo", "test", "-e", p], check=False, han=30)
        if r.returncode != 1:
            raise Dung("S2-can-doi-soat-cach-luu-khong-mo-file")


def token(c):
    can_tat(c)
    if con_phieu_b():
        raise Dung("B-con-phieu-khong-cap-token-moi")
    if input("Cấp token B mới sẽ vô hiệu token cũ. Gõ cap-moi sau đối soát phiếu: ").strip() != "cap-moi":
        raise Dung("chua-xac-nhan-cap-token")
    a = subprocess.Popen([str(REPO / ".venv/bin/tram"), "chu", "cap-token-may", "B", "--dong-y"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    b = None
    try:
        b = subprocess.Popen(lenh_tho("nhan-token"), stdin=a.stdout,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        a.stdout.close()
        mb, ma = b.wait(timeout=30), a.wait(timeout=30)
        c.ghi("token-keychain", f"nguon={ma},dich={mb}")
        if ma or mb:
            raise Dung("token-chua-xac-nhan-khong-tu-cap-lai")
    finally:
        if a.stdout and not a.stdout.closed:
            a.stdout.close()
        for p in (a, b):
            if p is not None and p.poll() is None:
                p.kill()
                p.wait(timeout=10)


def do_nen(c):
    can_tat(c)
    cu = c.goi("doc-plist", ["sudo", "cat", str(PLIST)], han=30).stdout.encode()
    pl = plistlib.loads(cu)
    if pl.get("UserName") != "tram-tho" or pl.get("Label") != "vn.tram.tho":
        raise Dung("plist-khong-dung-tho")
    backup = c.goc / "tho-cu.plist"
    backup.write_bytes(cu)
    log = THO / f".tram/log/do-nen-{time.time_ns()}.log"
    pl.update(ProgramArguments=[str(RUNTIME / ".venv/bin/python"), "-m", "tram.tho.do_nen"],
              KeepAlive=False, StandardOutPath=str(log), StandardErrorPath=str(log))
    moi = c.goc / "tho-do.plist"
    moi.write_bytes(plistlib.dumps(pl))
    try:
        c.goi("cai-do-nen", ["sudo", "install", "-o", "root", "-g", "wheel", "-m", "644", str(moi), str(PLIST)])
        c.goi("enable-do", ["sudo", "launchctl", "enable", "system/vn.tram.tho"], han=30)
        c.goi("bootstrap-do", ["sudo", "launchctl", "bootstrap", "system", str(PLIST)], han=30)
        het = time.monotonic() + 300
        while time.monotonic() < het:
            r = c.goi("doi-do-nen", ["sudo", "cat", str(log)], check=False, han=30)
            ket = [x for x in r.stdout.splitlines() if x in ("DO-NEN: DAT-HAI-KHE", "DO-NEN: CHUA-DANG-NHAP",
                "DO-NEN: TOKEN-KHONG-KHOP", "DO-NEN: CLAUDE-CHUA-DAT", "DO-NEN: KHONG-KET-LUAN")]
            if ket:
                c.ghi("do-nen", ket[-1])
                if ket[-1] != "DO-NEN: DAT-HAI-KHE":
                    raise Dung("S2-do-nen-chua-dat")
                return
            time.sleep(3)
        raise Dung("do-nen-qua-han")
    finally:
        c.goi("bootout-do", ["sudo", "launchctl", "bootout", "system/vn.tram.tho"], check=False, han=30)
        c.goi("disable-do", ["sudo", "launchctl", "disable", "system/vn.tram.tho"], han=30)
        c.goi("tra-plist", ["sudo", "install", "-o", "root", "-g", "wheel", "-m", "644", str(backup), str(PLIST)])
        can_tat(c)


def can_tu_dong_tat():
    from contextlib import closing
    from tram.tu_dong.luu import doc_cai_dat
    uri = (CAU_HINH.parent / "su-kien.db").as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=5)) as db:
        cd, _ = doc_cai_dat(db, "ben-station")
    if cd.tu_merge or cd.tu_deploy:
        raise Dung("tu-dong-dang-bat-can-dai-ca-tat-qua-cua-da-duyet")


def giao(c, bat):
    import yaml
    raw = yaml.safe_load(CAU_HINH.read_text()) or {}
    gv = raw.setdefault("giao_viec", {})
    gv["bat"], gv["du_an"] = bat, ["ben-station"]
    gv.pop("bead", None)  # Bỏ cấu hình thử cũ nếu còn; không đổi các hạn mức.
    if bat:
        can_tu_dong_tat()
        for p in (REPO / "du-an").glob("*.yaml"):
            d = yaml.safe_load(p.read_text()) or {}
            if p.stem != "ben-station" and d.get("bat_ghi") is True:
                raise Dung("du-an-khac-dang-bat")
        p = REPO / "du-an/ben-station.yaml"
        da = yaml.safe_load(p.read_text())
        da["bat_ghi"] = True
        ghi_yaml(p, da)
    ghi_yaml(CAU_HINH, raw)
    c.goi("nap-lai-api", ["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/vn.tram.api"], han=30)


def con_phieu_b():
    import sqlite3
    from contextlib import closing
    from tram.duong_dan import tram_home
    uri = (tram_home() / "su-kien.db").resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=5)) as db:
        return db.execute("SELECT COUNT(*) FROM phieu WHERE may_id = ? AND trang_thai = ?",
                          ("B", "hieu_luc")).fetchone()[0]


def doi_het_phieu(c):
    het = time.monotonic() + 210
    while time.monotonic() < het:
        if con_phieu_b() == 0:
            c.ghi("phieu", "B-KHONG-CON-PHIEU-HIEU-LUC")
            return
        time.sleep(3)
    raise Dung("con-phieu-chua-bootout")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("chuan-bi", "keychain", "login-1", "login-2", "token",
            "dang-ky", "kho", "do-nen", "kiem", "s6", "bat-khe", "bat-tho", "bat-giao", "tat-giao", "dung"):
        print("Chọn đúng bước của sổ tay; không có bước chạy tất cả.")
        return 2
    if os.getuid() == 0 or Path.home() != Path("/Users/dai-ca"):
        print("Mở Terminal.app dưới hungle; không sudo toàn bộ script.")
        return 2
    c, buoc = Chay(), sys.argv[1]
    try:
        c.tuong_tac("xac-thuc-sudo", ["sudo", "-v"])
        if buoc == "chuan-bi":
            chuan_bi(c)
        elif buoc == "keychain":
            keychain(c)
        elif buoc.startswith("login-"):
            dang_nhap(c, int(buoc[-1]))
        elif buoc == "token":
            token(c)
        elif buoc == "dang-ky":
            can_tat(c)
            c.goi("dang-ky-b", lenh_tho("dang-ky-b", "--tep", str(THO / ".tram/tho-ung-vien.yaml"), "--dong-y"))
        elif buoc == "kho":
            kho(c)
        elif buoc == "do-nen":
            do_nen(c)
        elif buoc == "s6":
            from doi_ngu_s6 import s6
            s6(c)
        elif buoc == "bat-khe":
            for n in (1, 2):
                c.goi("bat-khe", [str(REPO / ".venv/bin/tram"), "tho", "bat-khe", f"B/claude-{n}",
                                  "--vi-sao", "Thử hai khe B sau cổng R4"])
        elif buoc == "kiem":
            can_tat(c)
            r = c.goi("kiem-ben-station", lenh_tho("kiem", "--du-an", "ben-station"), check=False)
            for mau in ("B/claude-1", "B/claude-2", "kho ben-station", "tram-api", "cách ly"):
                dong = [x for x in r.stdout.splitlines() if mau in x]
                c.ghi(mau, "DO" if any("[ĐỎ]" in x for x in dong) else "XEM-CONG-R4")
            if r.returncode:
                raise Dung("kiem-ben-station")
        elif buoc == "bat-tho":
            can_tat(c)
            c.goi("enable-tho", ["sudo", "launchctl", "enable", "system/vn.tram.tho"], han=30)
            c.goi("bootstrap-tho", ["sudo", "launchctl", "bootstrap", "system", str(PLIST)], han=30)
        elif buoc in ("bat-giao", "tat-giao"):
            giao(c, buoc == "bat-giao")
        elif buoc == "dung":
            giao(c, False)
            for n in (1, 2):
                c.goi("tat-khe", [str(REPO / ".venv/bin/tram"), "tho", "tat-khe", f"B/claude-{n}",
                                  "--vi-sao", "Dừng đợt thử B"])
            doi_het_phieu(c)
            c.goi("bootout-tho", ["sudo", "launchctl", "bootout", "system/vn.tram.tho"], han=30)
            c.goi("disable-tho", ["sudo", "launchctl", "disable", "system/vn.tram.tho"], han=30)
        c.ghi(buoc, "XONG-BUOC-KHONG-PHAI-XONG-CONG")
        return 0
    except (Dung, OSError, ValueError, subprocess.SubprocessError, sqlite3.Error):
        c.ghi(buoc, "DUNG-DOI-SOAT")
        print("Dừng tại bước ghi trong log; không chạy tiếp hoặc tự chạy lại tất cả.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

**Create: `cong-cu/doi_ngu_s6.py`**

```python
"""Phép đo quyền có đối chứng; chạy từ hungle, lệnh thử nằm dưới đúng khe, không lưu bí mật."""
import json
import pwd
from pathlib import Path

from doi_ngu_io import Dung
from doi_ngu_chuan_bi import THO, TRAM, RUNTIME, can_tat


def s6(c):
    from tram.tho.cham_tham_do import cham
    can_tat(c)
    def q(ten, *argv, check=True):
        return c.goi(ten, ["sudo", "-H", "-u", "tram-tho", *map(str, argv)], check=check, han=60)
    tmp = Path(q("thu-muc-do", "mktemp", "-d", str(THO / "tram/s6.XXXXXX")).stdout.strip())
    if tmp.parent != THO / "tram" or not tmp.name.startswith("s6."):
        raise Dung("duong-do-sai")
    q("di-qua-do", "chmod", "755", tmp)
    repo = tmp / "repo"
    q("repo-do", "git", "init", "-q", repo)
    q("commit-do", "git", "-C", repo, "-c", "user.name=probe", "-c", "user.email=probe@localhost",
      "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", "probe")
    for n in (1, 2):
        gate = tmp / f"g{n}"
        q("cong-do", "mkdir", "-m", "700", gate)
        w, hd = gate / "cay", gate / "phieu/hang-doi.jsonl"
        q("worktree-do", "git", "-C", repo, "worktree", "add", "-q", "-b", f"tram/probe-{n}", w)
        q("goi-do", "mkdir", w / ".tram")
        q("hang-doi-do", "mkdir", "-m", "700", hd.parent)
        q("file-do", "touch", hd, hd.parent / "settings.json")
        q("di-qua-hang-doi", "chmod", "+a", f"user:tram-khe{n} allow list,search", hd.parent)
        script = "import sys, subprocess; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
        script += "from tram.tho.quyen_cay_b import trao_quyen_b; "
        script += "trao_quyen_b(Path(sys.argv[2]), Path(sys.argv[3]), user=sys.argv[4], chay=subprocess.run)"
        q("acl-do", RUNTIME / ".venv/bin/python", "-I", "-c", script, RUNTIME, w, hd, f"tram-khe{n}")
        q("cong-kin", "chmod", "700", gate)
        q("mo-cong", "chmod", "+a", f"user:tram-khe{n} allow search", gate)
    for n in (1, 2):
        gate = tmp / f"g{n}"
        user, w, hd = f"tram-khe{n}", gate / "cay", gate / "phieu/hang-doi.jsonl"
        def thu(ten, argv, dat):
            r = c.goi(f"{user}-{ten}", ["sudo", "-H", "-u", user, *map(str, argv)], check=False, han=30)
            loai = "ok" if dat else "ghi"
            if cham(loai, r.returncode, r.stdout.strip(), r.stderr)[0] != "dat":
                raise Dung(f"{user}-{ten}")
            return r
        r = thu("uid", ["id", "-u"], True)
        if int(r.stdout.strip()) != pwd.getpwnam(user).pw_uid:
            raise Dung("uid-khong-khop")
        thu("ghi-ma", ["touch", w / "duong.txt"], True)
        thu("append-bao", ["/bin/sh", "-c", 'printf x >> "$1"', "probe", hd], True)
        thu("git-config", ["touch", repo / ".git/config"], False)
        thu("git-objects", ["touch", repo / ".git/objects/khong-duoc"], False)
        thu("git-refs", ["touch", repo / ".git/refs/heads/khong-duoc"], False)
        thu("git-hooks", ["touch", repo / ".git/hooks/khong-duoc"], False)
        thu("doi-git-pointer", ["mv", w / ".git", w / "git-khac"], False)
        thu("settings", ["touch", hd.parent / "settings.json"], False)
        thu("hang-doi-khe-khac", ["cat", tmp / f"g{3-n}/phieu/hang-doi.jsonl"], False)
        thu("nha-dai-ca", ["ls", "/Users/dai-ca"], False)
        thu("cau-hinh-khe-khac", ["ls", f"/Users/tram-khe{3-n}/claude"], False)
    for n in (1, 2):
        gate, user = tmp / f"g{n}", f"tram-khe{n}"
        w = gate / "cay"
        def thu(ten, argv, dat):
            r = c.goi(ten, ["sudo", "-H", "-u", user, *map(str, argv)], check=False, han=30)
            if cham("ok" if dat else "ghi", r.returncode, r.stdout.strip(), r.stderr)[0] != "dat":
                raise Dung(ten)
        thu("file-uid-khe", ["/bin/sh", "-c", 'umask 077; mkdir "$1/d"; printf x > "$1/d/f"', "probe", w], True)
        uid = q("chu-file", "stat", "-f", "%u", w / "d/f").stdout.strip()
        if uid != str(pwd.getpwnam(user).pw_uid):
            raise Dung("file-khong-thuoc-khe")
        q("quan-ly-doc-file", "cat", w / "d/f")
        q("dong-cong", "chmod", "-N", gate)
        thu("quyen-cu-da-dong", ["cat", w / "d/f"], False)
        script = "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
        script += "from tram.tho.luot_b import xoa_cay; xoa_cay(Path(sys.argv[2]), Path(sys.argv[3]))"
        q("xoa-luot", RUNTIME / ".venv/bin/python", "-I", "-c", script, RUNTIME, gate, repo)
    # Đối chứng token từ đúng chủ; giá trị chỉ dùng trong bộ nhớ gọi API, không ghi log.
    r = q("token-doi-chung", "security", "find-generic-password", "-s", "tram-tho-token", "-w")
    from tram.tho.khach import KhachTram
    from tram.tho.kiem_am import chay_tham_do, tham_do_api_db
    from tram.tho.principal import doc_principal
    khach = KhachTram("http://127.0.0.1:7700", r.stdout.strip())
    d = khach.kiem_am()
    for n in (1, 2):
        user = f"tram-khe{n}"
        pr = doc_principal(f"user:{user}")
        r = c.goi("token-khe-bi-chan", ["sudo", "-H", "-u", user, "security", "find-generic-password",
            "-s", "tram-tho-token", "-w", str(THO / "Library/Keychains/login.keychain-db")], check=False, han=30)
        if cham("keychain", r.returncode, r.stdout.strip(), r.stderr)[0] != "dat":
            raise Dung("keychain-chua-chung-minh-bi-chan")
        ds = tham_do_api_db(api=khach.url, dai_ca_login=d.dai_ca_login, may_b=d.may_b, db=list(d.db_nghiep_vu))
        kq = chay_tham_do(ds, boc=pr.boc, kill=pr.kill_nhom,
                         env={"PATH": "/opt/homebrew/bin:/usr/bin:/bin", "LANG": "C.UTF-8"})
        if not all(x.dat for x in kq):
            raise Dung("API-DB-chua-dat")
    c.ghi("S6", "DAT-PHEP-DO-QUYEN-CON-CAN-THU-HOI-R4")
    # Giữ thư mục đo để đối soát; chỉ rmdir/xoá sau khi Đại ca duyệt đúng đường, không quét theo tên.
```

- [ ] Step 4 — GREEN: `tests/chan_host/chay.sh -q tests/test_doi_ngu_cong_cu.py`; chạy hồi quy nêu dưới.
  Các bước là công cụ cho Đại ca, chưa chạy trong phiên soạn. Mọi subprocess trong test phải giả.
  Không dùng `sudo` thật để thử wrapper. Chạy `python -m py_compile` trên file công cụ chỉ ở thư mục tạm.
  Script cố ý dừng khi runtime/kho đã tồn tại: giữ phần đã làm, đối soát, không xoá để chạy lại.

## Kiểm tích hợp và QC sau Task 9

- [ ] Đo lại toàn bộ qua bộ chặn, không dùng pytest trần:

```bash
tests/chan_host/chay.sh -q tests/test_doi_ngu_cai.py tests/test_doi_ngu_dang_ky.py tests/test_doi_ngu_pham_vi_kiem.py tests/test_doi_ngu_nen.py tests/test_doi_ngu_bao.py tests/test_doi_ngu_quyen.py tests/test_doi_ngu_chot.py tests/test_doi_ngu_giao.py tests/test_doi_ngu_cong_cu.py
tests/chan_host/chay.sh -q tests/test_tho_lenh_chay.py tests/test_tho_theo_doi_ket_thuc.py tests/test_tho_chuan_bi.py tests/test_tram_bao.py tests/test_hang_doi.py tests/test_bo_giao_viec.py tests/test_noi_giao_viec.py tests/test_giao_viec_api.py tests/test_han_muc_claude.py tests/test_chon_khe.py tests/test_kiem_khe_d54.py tests/test_dang_nhap_principal.py
tests/chan_host/chay.sh -q
```

- [ ] Chạy thêm `tests/test_doi_ngu_vong_doi.py`, `tests/test_doi_ngu_deps.py` và các test `test_phu_thuoc_*.py`.
- [ ] Test cũ báo cáo trong bối cảnh từng hỏng tại thu hồi/kết thúc vòng thợ: không bỏ qua. Nếu còn hỏng,
  xác định lỗi trước; việc sửa vượt mã của plan phải bổ sung bản vá/test nguyên văn và review lại.
- [ ] Kiểm bảng Files: không import vòng; `test_do_dai_ma.py`, `test_vong_import.py` đạt. Bản mã trong plan
  đã được áp bằng `git apply --check`/`git apply` tuần tự trên bản sao HEAD và chạy test; số đo ở cuối plan.
- [ ] Mở Đội ngũ dưới CSP thật với dữ liệu giả; hai khe tắt sau đăng ký, sau nhịp thì đúng trạng thái;
  không đọc `bat` của API thành `giao_viec.bat`. Không đổi frontend, nên không tự thêm yêu cầu xây UI.
- [ ] QC từng dòng thêm so với plan; người điều phối kiểm lại, không tự commit/merge trong phiên này.

## Chạy thật — sổ tay cho Đại ca (chỉ sau code, review, QC và ghép)

**Đại ca mở Terminal.app trên máy B, tài khoản hungle.** Mỗi khối dưới là một lệnh.
Không `sudo` cả script. Script sẽ tự hỏi mật khẩu Mac nếu cần; không ghi mật khẩu hay màn đăng nhập vào log.
Mỗi lần có thư mục `/private/tmp/doi-ngu-b-…` riêng (700), `ket-qua.txt` (600).
Khi hỏng, gửi đúng file `ket-qua.txt`; không gửi file auth, log Claude thô, toàn bộ cấu hình hoặc ảnh mã đăng nhập.
`XONG-BUOC` chỉ nói bước lệnh xong, chưa nói cổng đã đạt.

Các giá trị đường dẫn dưới đây là cấu hình cụ thể của máy B đã nêu trong bàn giao, không là đường tương đối
trong worktree spec. Python ghim lấy từ `tram/kiem/toolchain.py`; nếu máy đã đổi bản thì dừng đối chiếu,
không tải bản khác hoặc tìm Python trong nhà Đại ca để lách quyền.

### R0 — kiểm trước khi làm

Người điều phối đọc bằng chứng G4 gần nhất và xác nhận đúng code/checkout API đang chạy; công cụ một lệnh
phải đã nằm ở checkout chính sau QC. Sao lưu kho sự kiện bằng lệnh đã có; script `chuan-bi` cũng gọi sao lưu.
Đối soát không còn phiếu B; hai khe đang tắt, `giao_viec.bat:false`, mọi dự án ngoài ben-station `bat_ghi:false`,
TM/TC/tự deploy tắt; estop/cổng kiểm giữ đúng trạng thái đã duyệt. Không tắt chúng để chữa một phép thử.

Đọc sổ cài xác nhận `tram-tho`, `tram-khe1` còn đúng UID/GUID. Có user/file lạ hoặc bản cài dở thì đối soát
trước, không xoá sổ/nhận tài nguyên lạ. `vn.tram.tho` phải đang vắng **và** disable; Uq vẫn running.
Kho thợ dùng cho lần đầu phải mới, không mang ACL cũ. Thư mục runtime/kho đã có thì script dừng có chủ đích;
người điều phối chuẩn bị kế hoạch tiếp nối đúng phần đã làm, không dặn Đại ca xoá rồi thử lại.

### R1 — thêm khe 2, chuẩn bị bản chạy riêng, giữ thợ tắt

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" chuan-bi
```

Lệnh clone mã đã ghép sang `/Users/Shared/tram-tho-code`, cấp thư viện từ bundle root đã cài cho Uq,
chạy `cai-dat-tho --chi-tho --giu-tat` cho hai khe. Không tải gói thiếu; thiếu cache thì dừng và báo rõ,
không đổi lockfile. Trình cài vẫn đối soát sổ trước mỗi tài nguyên, không đụng Uq.

Bản runtime dùng Python ghim và helper G4 ngoài nhà hungle, không dùng cache hay uv sync.
Thiếu/sai bundle thì dừng; không tự tải hay sửa Uq. Runtime giữ 700 tới khi chuẩn bị xong, sau đó chỉ mở đọc. Chặn **đúng ba tài khoản thợ** đi vào nhà hungle, không áp luật lên
Apple hay quét mọi dịch vụ. Chỉ cấp các đường đi qua/hàng đợi cần thiết. Đặt cấu hình ứng viên không có bí mật.
Cần kiểm `/opt/homebrew/bin/claude` và mọi đích symlink đọc/chạy được từ hai user; nếu CLI hiện cài trong nhà
hungle thì cài bản CLI chính thức ở chỗ dùng chung theo kịch bản riêng đã duyệt, không mở lại cả nhà hungle.

**Mật khẩu:** Mac. **Kỳ vọng:** hai UID khác nhau; script kết thúc `XONG-GIU-TAT`; daemon vẫn disable, Uq nguyên.
**Hỏng:** giữ phần đã tạo và sổ cài. Log chỉ bước lỗi; người điều phối đối chiếu sổ để chuẩn bị lần tiếp,
không tự gỡ user, không chạy trình cài cũ thiếu hai cờ.

### R2 — Keychain và hai đăng nhập Claude

Lần đầu tạo/chọn/mở Keychain của ba tài khoản bằng giao diện hỏi mật khẩu của `security`:

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" keychain
```

Đại ca tự nhập mật khẩu Keychain khi macOS hỏi; không dùng mật khẩu rỗng, không thêm `-p`, `-w` cùng giá trị
vào argv, không dùng `set -x`, `script` hoặc `tee`. Nếu công cụ macOS cần phiên GUI của đúng user, dừng bước
và mở phiên đó bằng macOS; `sudo -H` không giả làm phiên GUI. Bước này không bảo đảm Keychain tự mở sau reboot.

Hai lần đăng nhập, mỗi lần chọn đúng một tài khoản Claude:

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" login-1
```

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" login-2
```

Script chạy dưới `tram-khe1`/`tram-khe2`, dùng đúng `/Users/tram-kheN/claude`. Màn đăng nhập chỉ hiện trực tiếp
ở Terminal.app/trình duyệt, không được thu vào log. Đại ca xem danh tính ở `auth status`, xác nhận hai account
khác nhau; báo “hai tài khoản khác nhau”, không gửi email hay token. Hai thư mục khác nhau chưa đủ S3.

Phép dò `.credentials.json` chỉ phát hiện hai vị trí phổ biến, **không chứng minh mọi cách lưu của CLI**.
Người điều phối phải đối chiếu bản CLI đang cài với tài liệu chính thức hoặc nguồn cài đặt và mục Keychain
native của đúng user (chỉ metadata, không xem giá trị). Nếu có lưu plaintext/fallback chưa rõ: S2 đỏ, dừng;
không chuyển sang setup-token/env bằng suy đoán. Đây là phụ thuộc máy thật có chủ đích, không chỗ điền mã sau.

Cấp token máy **một lần**, sau sao lưu và đối soát không có phiếu B:

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" token
```

**Mật khẩu:** Mac/Keychain, có xác nhận `cap-moi`. Token chạy trong pipe thẳng vào Keychain tram-tho.
Nếu đầu nguồn đã thành công mà đầu nhận lỗi, token cũ đã hết hiệu lực: giữ tắt, đối soát rồi mới cấp lại;
không chạy bước này khi chỉ gặp lỗi đăng ký HTTP. Không dùng `tram chu cap-ma B` (đã đóng theo D155).

### R3 — đăng ký để hiện thẻ; nối kho đọc cục bộ

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" dang-ky
```

Kỳ vọng GET `/api/doi-ngu` có `B/claude-1`, `B/claude-2`, đều **tắt**. Chưa có nhịp tim là bình thường.
Có plist hệ thống không chặn đăng ký B. Gửi lại cùng cấu hình không thêm thẻ hay sự kiện đăng ký trùng.
HTTP lỗi giữ tho.yaml cũ; POST thành công rồi ghi file lỗi có thể đã hiện thẻ, retry cùng token/cấu hình.

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" kho
```

Lệnh đối chiếu đúng GitHub `Hungbennn/ben-station`; giữ `github`, thêm `origin` nếu thiếu. Gặp khác URL thì dừng,
không in URL thô. Tạo kho kiểm không checkout ở `/Users/Shared/tram-nguon/ben-station`, symlink từ kho kiểm của trạm,
cấp tram-tho đọc; clone kho thợ bằng đường cục bộ, không credential. Cấu hình fetch của kho thợ là
`+refs/remotes/origin/*:refs/remotes/origin/*`: kho nguồn không checkout chỉ cập nhật remote-tracking refs,
không tự cập nhật nhánh `main` cục bộ. Test Git thật với remote tạm chứng minh thợ nhận được SHA mới. Cấu hình công bố `lai` và ánh xạ B,
`giao_viec.bat` vẫn false. Các repo/đường đã có đều dừng để đối soát; không xoá/ghi đè.

**S7 phải kiểm:** sau trạm fetch một commit mới, quản lý thợ fetch qua origin cục bộ thấy đúng SHA đó;
trạm nhận ref thử từ kho thợ đúng SHA/lượt; hai khe không push, không đọc credential GitHub. Chọn một ref thử
đã được duyệt, không push để “xem có chạy không”. Trong đợt thử thật, quyền công bố/PR phải được duyệt riêng;
phiên soạn này tuyệt đối không thực hiện push. Kho kiểm là cùng nguồn đang được tick cập nhật, không phải mirror
cần ai nhớ đồng bộ. Bật công bố không đồng nghĩa cho phép tự merge/deploy.

### R4 — đo nền và quyền trước khi nhận việc

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" do-nen
```

Lệnh tạm dùng **chính** `vn.tram.tho`, cùng UserName, HOME, PATH, WorkingDirectory; đổi entrypoint thành phép đo
một lần, `KeepAlive:false`. Mỗi khe trả lời một câu cố định, tối đa một lượt/120 giây, không có công cụ.
Token máy chỉ dùng ping; không gọi nhịp xin phiếu. Sau đo bootout/disable rồi trả nguyên plist.
Log chỉ nhận các dòng `DO-NEN: …` đã định nghĩa; không chép stream Claude. Có thể tốn hai lượt Claude.

**Kỳ vọng:** `DO-NEN: DAT-HAI-KHE`, thợ lại vắng và disable. Đây mới là bằng chứng headless ban đầu của S2;
không thay S4 đầy đủ. Nếu CLI không hiểu cờ, Keychain khoá hoặc chưa có consent native thì dừng ở S2,
không bỏ các cờ quyền. Không chạy lại liên tục để thử vận may.

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" s6
```

Phép này chạy từ tài khoản trạm để làm đối chứng, mỗi lệnh thử vẫn dưới đúng user khe. Nó tạo repo/hàng đợi
thử không có bí mật trong vùng riêng của tram-tho, dùng chính mã cấp quyền của Task 6, thử dương trước âm.
Token máy được đối chứng dưới đúng chủ; API/DB dùng danh sách đích do trạm trả, không gán fixture là đạt.
Thư mục đo được giữ để đối soát, không tự quét xoá theo tên.

**Vì sao có phép đo này:** `tram tho kiem` cũ quan sát mục Keychain/đường trạm từ tài khoản quản lý thợ.
Khi quản lý bị chặn đọc nhà hungle đúng thiết kế, đối chứng ấy có thể “không kết luận”. Không bỏ mục đỏ để
lấy xanh; bằng chứng S6 cuối phải do người vận hành có quyền đối chứng đo dưới chính hai khe.
Cờ `kiem --du-an` vẫn hữu ích để chẩn đoán repo, không phải chứng nhận toàn bộ S6.

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" kiem
```

Lệnh cuối chỉ chẩn đoán; nếu đỏ vì đối chứng không đọc được, ghi rõ kết quả “không kết luận”, dùng phép S6 có
đối chứng để quyết cổng tương ứng. Không biến mục lỗi thật thành cảnh báo và không gọi toàn bộ máy là xanh.

Những phép còn phải đo trong kịch bản S của sổ tay cũ, giữ đúng phạm vi hai Claude:

| Cổng | Thao tác/đối chứng và điều kiện đạt |
|---|---|
| S1 | Lượt thử Claude thật; không có event/quota thì giữ chưa biết. Chỉ đặt `thang_utilization` sau xác minh đơn vị. Fixture rejected/429 chứng minh luật, không chứng minh nhà cung cấp đã phát event thật. |
| S3 | Hai danh tính account khác nhau do Đại ca xem trực tiếp, đúng user/thư mục. Không lưu email vào log. |
| S4 | Một lượt theo settings vai thật: tác vụ hợp lệ chạy; Bash/MCP ngoài danh sách bị từ chối; settings project/local và `.mcp.json` của repo không mở thêm quyền. Không dùng skip-permissions. |
| S6 | Bổ sung đổi `.git` bằng symlink, xoá/rename metadata, sửa index, thay settings bằng rename, symlink từ cây mã ra ngoài; tất cả bị chặn. CLI con tách phiên/nhóm vẫn được thu hồi theo UID, Apple đi qua theo mã lọc đang có. Không dùng reboot Uq thay phép này. |
| S8 | Bàn giao `tram bao --xong` từ Claude thật được nhận; hook PreCompact gọi đúng entrypoint, mốc chỉ lưu tiến độ trên B; SIGTERM/estop giữ WIP và không công bố SHA do agent bịa. |
| G5 liên quan | Nhịp tim, thu hồi khi mất liên lạc, API ghi giả danh bị chặn và DB không vào được. Không bắt chạy Codex app-server hoặc thêm khe Codex. |

Các phép adversarial dùng canary/repo thử đã tạo, có đối chứng đích tồn tại; không dùng dữ liệu sản xuất làm
vật thử. Thao tác và ngân sách của từng phép cần Đại ca cho phép riêng theo sổ tay. Nếu lộ lỗ hoặc CLI khác hợp
đồng thì dừng, sửa spec/plan rồi review; không thêm ngoại lệ để đi tiếp. Bằng chứng giữ lệnh, giờ, UID, phiên bản,
SHA mã/quyền và kết luận, không giữ nội dung stream/token. Không tạo bảng marker tự ghi “đã qua cổng”.

**Bổ sung S6/C1/C2:** file/thư mục khe tạo với umask 077 phải thuộc UID khe, quản lý đọc/dọn được;
đóng cổng thì khe cũ không còn đọc cây dù ACL con còn. Hai lượt có đường khác; đổi code→QC, restart
cùng phiếu, dừng mềm, phiếu cũ bị từ chối đều phải đối soát sổ và quyền. Chạy đủ 6 lệnh kiểm mặc định
dưới từng UID với bundle root, không cài gói; lỗi lock/hash phải dừng trước CLI. Nếu một ca không đạt, giữ giao tắt.

### R5 — thử lại sau reboot theo QĐ1-A

Đại ca reboot lúc ngồi ở B, đăng nhập hungle; Uq/API/nho/bao-tin phải lên như bằng chứng tối 20/10.
Thợ vẫn disable. Chạy lại `keychain` nếu cần mở khoá bằng mật khẩu, rồi **cùng lệnh `do-nen` ở R4**.
Chỉ khi hai khe đạt mới nhận S2 trong điều kiện “đã đăng nhập/mở khoá”. Không suy thành “tự chạy trước login”.
Không cài daemon giữ mật khẩu hay tự nhấn đồng ý Keychain. Đăng nhập khác user/khác CLI version thì đo lại S2/S3.

### R6 — bật thợ, mở mọi việc đủ điều kiện của ben-station

Sau R1–R5 đạt và Đại ca cho phép bước bật, khi giao việc vẫn tắt:

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" bat-tho
```

Lệnh dùng `launchctl enable system/vn.tram.tho` rồi bootstrap plist đúng nhãn, không dùng kickstart để thay enable.
Kỳ vọng không lặp exit 1/2; đúng UserName, có nhịp tim cả hai khe. Nếu lỗi giữa enable/bootstrap: giữ giao việc tắt,
đối soát trạng thái nạp, disable lại theo bước dừng; không coi nhãn có trong launchctl là đã nhận việc được.

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" bat-khe
```

Bật khe là cấp quyền riêng, không nằm trong đăng ký. Chờ hai nhịp tim mới và UI hiện rảnh. Bộ giao xét mọi bead
ben-station theo tiêu chí/lệnh kiểm/nhãn/ngân sách hiện có trong `tram/giao_viec/dieu_kien.py`. Không tạo bead
trong script, không nới hạn mức hoặc bật tự deploy trạm.

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" bat-giao
```

Lệnh đặt `giao_viec.du_an:[ben-station]`, không hỏi/ghi danh sách bead, bật ghi đúng YAML của checkout API
và bật `giao_viec.bat`, nạp lại API. Giữ mọi điều kiện, ngân sách mỗi bead/phiếu, trần giờ/ngày, quota và cầu dao
hiện có. Script đọc cài đặt sự kiện, từ chối nếu tự merge/deploy ben-station đang bật; không tự sửa quyền
hoặc tắt công tắc thay Đại ca. Script cũng từ chối nếu dự án khác đang bật ghi. Nạp API hỏng thì chạy `tat-giao`,
không tiếp tục thử nhận. Runtime thợ chỉ dùng bản YAML sao từ checkout chính cho lệnh kiểm; không chỉnh HR.

### R7 — nghiệm thu và đường lui

Đạt khi có **cùng một chuỗi bằng chứng**: hai khe thật/hai tài khoản → nhịp → phiếu ben-station đúng bead/lượt →
CLI đúng UID sửa mã → báo xong → thu hồi sạch → SHA do quản lý chốt → trạm nhận đúng SHA → Uq kiểm lại →
QC bằng khe khác → kết quả công bố/PR theo quyền đã duyệt. Dashboard hết trống chỉ là mốc giữa.
Test mất nhịp/estop theo cổng đã cho phép; giữ nguyên hạn mức/thu hồi, không mở cổng kiểm tự động.

Dừng phát việc mới; giữ nguyên `bat_ghi` ben-station để máy A vẫn gửi được yêu cầu:

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" tat-giao
```

Dừng hai khe: tắt khe để dừng mềm, chờ **kho phiếu** hết phiếu B (không dựa vào thẻ UI đang tắt), rồi bootout/disable:

```bash
"/Users/dai-ca/Developer/Ben Station/.venv/bin/python" "/Users/dai-ca/Developer/Ben Station/cong-cu/doi_ngu_b.py" dung
```

Chờ quá hạn thì dừng và giữ log/phiếu, không giả vờ thu hồi được. Bootout không thay bằng chứng sạch UID;
người điều phối đối soát theo cơ chế thu hồi đang có. Uq giữ chạy. Không xoá user, Keychain, kho/WIP;
không restore DB sau khi có phiếu mới, không tự xoay token, không tự gỡ estop. Bản sao YAML dùng đối chiếu để
hoàn lại đúng khoá đã sửa; không đè toàn bộ cấu hình mới bằng bản cũ.

QĐ5-B có hiệu lực ngay khi mở giao: mọi bead đủ điều kiện của ben-station được xét, không cần bước mở rộng.
Một chuỗi hoàn tất là mẫu bằng chứng nghiệm thu, không phải danh sách cho phép. Archive sau mọi Scenario có bằng chứng;
người điều phối cập nhật trạng thái/bàn giao và Beads ở phiên được phép.

## Kiểm chứng review vòng 2 — 20/10/2026

C1/C2 đã được giải trong mã nguyên văn: Task 6 có cổng cha/worktree riêng theo phiếu-lượt-khe,
retry không reset, đóng/dọn khi kết thúc và xử lý phiếu cũ sau restart; Task 6–7 cấp bundle root và
đặt cờ runner sau sudo. Task 9 dùng cùng bundle cho runtime và đo file UID khe/đóng cổng ở S6.
Không cần quyết định mới, không thêm quyền sudo root/Git hay sửa Uq.

- Rehearsal tại `/private/tmp/doi-v2-hz3elsn_/`; áp lại toàn bộ Create/Modify từ plan trên bản sao HEAD.
  Mã ở bản sao được so từng byte với mã đã chạy; AST, trần dòng và vòng import được kiểm bằng test.
- RED hành vi C1/C2: **6 failed** trước vá. RED bổ sung bằng lùi riêng mã cũ: quyền kế thừa quản lý,
  dọn phiếu cũ sau restart và runtime dùng bundle root. Log `red.txt`, `additional-red.txt`.
- Hồi quy từ bản áp sạch: **236 passed, 4 deselected**; chi tiết trong [REVIEW-CODEX.md](../../REVIEW-CODEX.md).
- Bản sao sạch được cấp bundle root thật (digest `4ed173d9a6ed5409fe58fc00fd6ed76e7e83786801f1624d2c58874a909bad0b`):
  cả **6 lệnh kiểm mặc định** đạt; ba nhóm Python **52 + 29 + 7 passed**, frontend kiểm/build/kiểm-dist đạt.
  Đây là chạy dưới UID reviewer trong tmp; không phải bằng chứng hai UID khe/macOS S6 đã đạt.
- Toàn suite thử với `--maxfail=40`: **175 passed, 40 failed**, dừng trong nhóm thu hồi tiến trình.
  Đối chứng HEAD chưa vá: 6 ca (bản chép + bốn ca thu hồi + vòng thợ đầy đủ) cũng thất bại.
  Không dùng lỗi `sysctl`/`ps`/bind do sandbox để đánh trượt plan; không tuyên bố toàn suite xanh.
- Mọi lượt test qua bộ chặn, **0 dòng chặn mới**. Helper `python -I` tin cậy không nạp audithook được
  runner báo là điểm mù; vẫn giữ ghi nhận, không nới bộ chặn hoặc coi nó là sandbox hoàn chỉnh.
- `openspec validate doi-ngu-tho --strict` dùng binary có sẵn, tắt telemetry; không tải bản pin mới.

Giữ các cổng S2/Keychain, ACL/UID/S6, S7 và R7 sau code/QC/ghép. Không archive hoặc mở giao bằng test giả.
Kết luận một dòng và mọi phát hiện mới đã sửa: [REVIEW-CODEX.md](../../REVIEW-CODEX.md).


## Kiểm chứng sửa gọn vòng 3 — 20/10/2026

Trên HEAD `c73248d`: cả 45 khối Create/Modify (29 diff, 51 tệp kể cả test Step 1) áp sạch theo thứ tự;
29 diff đều qua `git apply --check`. Ba ca hồi quy mới đỏ trên mã vòng 2, xanh sau sửa;
nhóm liên quan **145 passed, 0 failed**, **0 dòng chặn mới**. OpenSpec strict và `git diff --check` đạt.
Chi tiết, lệnh và log: [REVIEW-PLAN-3.md](../../openspec/changes/doi-ngu-tho/REVIEW-PLAN-3.md).

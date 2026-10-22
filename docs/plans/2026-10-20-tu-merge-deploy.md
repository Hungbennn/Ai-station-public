# Tự merge/deploy — tiếp nối TM 18/10: Implementation Plan

> **Cho agent thực hiện:** làm tuần tự Task 1–7; Task 8 là kiểm tích hợp, không phải lượt vá muộn.
> **Trạng thái:** ĐÃ REVIEW/SỬA — CHƯA ĐẠT để code: còn cổng baseline/rehearsal toàn bộ.
> Review tại `f098d4a`; chỉ plan và `REVIEW-CODEX.md` được sửa trong worktree.
> Phiên soạn 20/10 chỉ sửa tài liệu theo yêu cầu Đại ca; không code `tram/`, commit, `bd` hoặc push.
> Mã được trích sang bản sao tạm để đối chiếu và kiểm thử; không áp vào `tram/` của worktree.

**Goal:** PR đủ bằng chứng được GitHub gộp; chỉ bản merge cố định đã kiểm qua Uq được đưa lên bằng quyền riêng
của dự án, có bản quay lại đã thử, không lặp deploy khi kết quả chưa rõ.

**Architecture:** sửa luồng TM đã có, giữ GitHub/`gh`, Uq + Seatbelt đã cài, launchd của dự án,
SQLite sự kiện, passkey, Telegram và hai màn Tự động/Phê duyệt. Không cài nền triển khai mới.
GitHub giữ required checks; trạm giữ bằng chứng/ngữ cảnh/quyền. Đường deploy do Đại ca chuẩn bị một lần;
trạm chỉ gọi ba entrypoint tin cậy, không chạy script lấy từ commit lỗi bằng tài khoản trạm.

**Tech Stack:** Python 3.12, stdlib, FastAPI/Pydantic/pytest và Vue hiện có; không thêm dependency.

**Spec:** [change tu-merge-deploy](../../openspec/changes/tu-merge-deploy/proposal.md),
[merge](../../openspec/changes/tu-merge-deploy/specs/tu-merge/spec.md),
[deploy](../../openspec/changes/tu-merge-deploy/specs/tu-deploy/spec.md),
[QĐ1–QĐ4 đã chốt A](../../openspec/changes/tu-merge-deploy/QUYET-DINH.md);
[điều khiển giữ lại](../../openspec/changes/tu-merge-tu-deploy/specs/dieu-khien-tu-dong/spec.md).
D69–D151 giữ trừ đúng phần thay trong bảng dưới. Passkey D135–D155 thắng cửa header/unix-socket cũ.

**Nền:** nhánh `spec/tu-merge-deploy`, HEAD `f098d4a`; mã TM và Uq đã có, không áp lại TM-1…TM-4.
Khuôn tham khảo: plan TM-2, TM-3 ngày 18/10 và plan D157. Bàn giao G4 20/10 thắng các dòng trạng thái cũ
“chưa có tram-kiem/chưa đạt G4”; phiên này không xác nhận lại OS hoặc điều kiện reboot.

## Global Constraints

- `tram/`: mỗi file **≤120 dòng**, mỗi dòng **≤120 ký tự Unicode**; không thêm ngoại lệ, không nén nhiều lệnh.
- N₀ toàn bộ chưa đạt. Không dùng số test thu thập làm số test xanh; xem bằng chứng và giới hạn trong REVIEW-CODEX.
- Chỉ `tests/chan_host/chay.sh`; Git/GitHub/đích/Uq giả, `TRAM_HOME` tạm; không pytest trần.
- Mỗi file chỉ có một bản cuối dưới đây: Create chép trọn; Modify là unified diff từ HEAD nêu trên.
  Đã đối chiếu patch/import/chữ ký trên bản sao tạm; đây không phải quyền áp mã hay chạy thật.
- TDD: nạp test trước mã của từng task. Lỗi thiếu module chỉ là lỗi thu thập, **không đủ bằng chứng RED hành vi**.
  Nếu cần, thêm khai báo tối thiểu để thu thập rồi chạy thấy assertion hỏng đúng yêu cầu; sau đó mới áp thân mã.
  Hồi quy giữ lại có thể xanh ngay. Không làm test hỏng giả bằng đổi kỳ vọng hay bỏ mock bảo vệ host.
- Trước khi thực thi, đo baseline đúng HEAD và chạy trọn thứ tự task tại môi trường đủ quyền quan sát tiến trình.
  Không xoá/bỏ qua test OS để có số xanh. Task còn đỏ thì chưa chuyển tiếp; ghi log thật, không dùng RED dự đoán.
- Phiên review không commit. Việc ghép chỉ xét sau QC và cả bộ xanh; chạy thật cần cổng riêng.
- Không `git push`, `bd dolt push`, `bd`; không gọi API GitHub ghi, launchctl ghi, sudo, Keychain, `~/.tram` thật.
- Kill list 1/3/5/7/8: đây chỉ là plan. Không mở cổng, không sửa daemon Uq, Seatbelt hay quyền OS trong code.
- Thời hạn: `gh` 60 giây/lời gọi; deploy/lùi 900 giây; health/probe/đối soát 120 giây.
  Uq dùng hạn/lượt/thu hồi của client hiện có. Timeout phía gọi không chứng minh tác vụ đích đã dừng.
- Không migration, restore DB, force-push, đóng feature cha hoặc tự deploy ben-station.
- Ba lệnh và các script/config chúng nạp phải ngoài vùng agent ghi được. Không chỉ kiểm file đầu rồi tin closure.
- Mọi lỗi hiển thị là câu hằng/mã; không ghi stdout/stderr, argv, nội dung bead, token vào sự kiện/Telegram.
- Không dùng một lần G4 đạt thay bằng chứng của từng PR/M. Marker `nguon_kiem=uq` chỉ do trạm ghi sau client
  kiểm fingerprint/đúng lượt/thu hồi; sự kiện cũ thiếu marker đóng cổng tự merge, phải kiểm lại.

## Hợp nhất trước khi triển khai

Đã thực hiện ở lớp tài liệu trong phiên soạn này. Không archive change nào và không sửa luật vận hành đã có hiệu lực.

| Phần 18/10 | Giữ/bỏ trong 20/10 | Nguồn duy nhất sau hợp nhất |
|---|---|---|
| `tu-merge` + `tu-deploy` ADDED ở change cũ | Chuyển thành `lich-su-tu-merge.md`, `lich-su-tu-deploy.md` ngoài `specs/`; bỏ heading ADDED ở bản lịch sử | Hai spec trong change mới |
| `dieu-khien-tu-dong` | Giữ, sửa CI thành khoá cứng và dẫn passkey hiện có | Change cũ; archive chỉ capability này |
| TM-1…TM-4, UI, cấu hình sự kiện/idempotency | Giữ mã, không tái dựng và không áp lại plan cũ | Các điểm nối trong plan này |
| D70–D71/D93, D94: nút bỏ CI, mọi job xanh, không bắt cập nhật | Bỏ; GitHub bắt required checks có app nguồn + strict + không bypass | QĐ1; Task 1 |
| D95: PR spec đã duyệt | Giữ ngoại lệ QC/code, nhưng đúng commit/tài liệu và cổng GitHub vẫn bắt buộc | Task 1–2, test spec hiện có |
| D97/D125: luôn lấy HEAD mới nhất, gồm code đẩy thẳng | Bỏ; chọn M từ merge đã xác minh; M kiểm riêng, phần ngoài luồng phải xác nhận | QĐ2; Task 4–6 |
| D-6: ba lệnh chạy trong worktree dưới tài khoản trạm | Bỏ đường gọi production đó; giữ primitive/test runner cũ cho các nơi còn dùng | QĐ3; Task 3/5 |
| D73/D75: lần đầu chưa có bản lùi | Bổ sung biết L, giữ artifact/config, tương thích dữ liệu và đã thử rollback | QĐ4; Task 3/5 + cổng tay |
| D76/D89/D90–D92/D112/D120 | Giữ schema/xoá dữ liệu/đường cấm; hai nút cột/hàng rào thường vẫn có | Luật cũ + Task 2 |
| D96/D100/D115–D116/D123–D124/D126–D130 | Giữ merge tay chờ bấm, hạn, ba lần hỏng, chống lặp, nút chung, báo tin | Task 5–8 + hồi quy cũ |

Bản design và mốc nghiệm thu 18/10 được giữ riêng ở `lich-su-design.md` và `lich-su-nghiem-thu.md`;
không mất dấu quyết định hoặc bằng chứng cũ.

Không nhập hai bộ ADDED trùng capability. Archive sau tất cả cổng: change cũ chỉ điều khiển;
change mới chỉ merge/deploy. Bản lịch sử là dữ liệu đối chiếu, không đem lại luật cũ khi đọc.

## Bảng G — cổng và bằng chứng

Tên G dưới đây là cổng **của plan**, không ghi đè số G0–G7 trong sổ tay chạy thật.
Mọi hàng chưa đạt bằng chứng mới đều **chưa đạt**, kể cả test nền 54 xanh.

| G | Điều bảo đảm | Task / bằng chứng offline | Cổng thật |
|---|---|---|---|
| G1 | Một bộ delta; QĐ1–4 đã chốt | Bảng hợp nhất; validate đúng OpenSpec 1.14.0 | Không |
| G2 | GitHub kiểm bắt buộc, strict, app nguồn, không bypass/queue | 1–2; `test_tm20_github`, `test_gh`, `test_gh_tu_merge` | R1 |
| G3 | Đúng Uq/lượt/ref/digest và QC khác khe; cổng đóng chặn merge | 2; `test_tm20_bang_chung`, `test_tu_merge*`, `test_quan_kiem*` hiện có | R2 |
| G4 | Spec chỉ tài liệu đã duyệt; schema/cấm cứng không bị hai nút miễn | 1–2; `test_tu_merge_spec`, `test_tu_merge_tuoi`, `test_tu_merge_rao` | R1–R2 |
| G5 | Chỉ M đã merge; không đổi thành N/HEAD; kiểm M riêng | 4–5; `test_tm20_ban`, `test_deploy_race` | R2 |
| G6 | Quyền/đích riêng, entrypoint ngoài repo; không chạy mã dưới trạm | 3; `test_tm20_duong`; không suy OS từ fake | R3 |
| G7 | L sẵn, đúng bản/chức năng/artifact; rollback một lần đúng L | 3/5/8; `test_tm20_chuoi`, `test_deploy_vong` | R3–R4 |
| G8 | Một chuỗi/dự án, đúng cài đặt, D123/124, Estop, không nuốt lượt mới | 5–8; `test_deploy_cong_tac_v2`, `test_deploy_race` | R4–R5 |
| G9 | Không rõ khoá bền, đọc trước, không chạy lại; xác nhận có passkey | 5–6/8; `test_tm20_cua`, `test_tm20_tich_hop`, `test_passkey_tm_tc` | R5 |
| G10 | Hai màn/nút chung; 409, thông báo, không lộ bí mật | 6–8; API/passkey, frontend kiem/build/kiem-dist, `test_bao_tin_tu_dong` | R5 |
| G11 | File/dòng 120; không vòng import mới; không thêm dependency | `test_do_dai_ma`, `test_vong_import`, diff manifest | Không |
| G12 | Toàn bộ và QC nguyên văn, rồi mới ghép/archive | Task 8 cuối + kiểm G1–G11; số đo thật | R1–R5 đủ |

## Hợp đồng đường deploy — phần cần Đại ca chuẩn bị

Chọn đúng một loại đích ở lát này: **Mac, dịch vụ launchd đã có**. Không dựng adapter workflow GitHub hay hệ plugin.
Dự án chỉ có workflow khác thì giữ deploy tay tới khi có đường tương thích; không tự biến push thành deploy.
Quy ước đường tuyệt đối là hợp đồng mới của adapter, không phải khẳng định máy hiện có các file này.
Tên dự án `ten` lấy từ cấu hình đã kiểm; ba lệnh lưu bằng sự kiện trên dashboard là các argv sau:

| Thao tác | argv cố định theo tên dự án |
|---|---|
| Deploy | `/usr/bin/sudo -n -u tram-dp-{ten} -- /Library/TramDeploy/{ten}/deploy` |
| Kiểm | `/usr/bin/sudo -n -u tram-dp-{ten} -- /Library/TramDeploy/{ten}/kiem-song` |
| Lùi | `/usr/bin/sudo -n -u tram-dp-{ten} -- /Library/TramDeploy/{ten}/lui` |

`{ten}` trong bảng là quy tắc nội suy của `tach_lenh`, **không phải đoạn mã để điền sau**.
Ba file executable và cha do root giữ, không symlink/ghi nhóm-người khác; ACL và mọi tệp nạp gián tiếp được
kiểm trong cổng R3. Tài khoản riêng chỉ đủ ghi bản triển khai và điều khiển đúng nhãn/miền launchd của dự án;
không đọc Keychain trạm, không quản dịch vụ trạm hoặc dự án khác. Không cấp sudo tổng quát/root.
Mã plan không cài user, sudoers, plist hoặc wrapper. HR Codex chưa cung cấp đường deploy: **chưa được bật**.

Entry point nhận **một JSON qua stdin**, không nhận bí mật/lenh tùy ý từ argv:
`v=1, du_an, ma, buoc, commit, truoc`. `ma` ổn định; đích phải đối soát cùng mã nếu đã nhận,
không phát động tác dụng phụ mới. Không dùng file sự kiện trạm làm hàng lệnh cho agent.
Đích phải giữ khoá theo dự án suốt thao tác, so bản đang chạy với `truoc` ngay trước đổi bản; sai thì từ chối,
không tự chọn L khác. Chốt này thuộc wrapper tin cậy, cần đo R3/R4; phép đọc của trạm không thay khoá tại đích.

Phản hồi JSON duy nhất ≤4096 byte, exit 0, đúng các khoá của yêu cầu cộng:
`dat: bool`, `da_dung: bool`, `san_sang: bool`, `ban_truoc: SHA`, `ban_thuc: SHA`, `artifact: SHA`.
`ban_thuc` và `artifact` là kết quả đo tại đích, không sao chép từ đầu vào. Exit khác 0, JSON thiếu/lạ,
mất kênh, timeout, không chứng minh đã dừng đều là **không rõ**, không lấy exit code làm kết luận deploy hỏng đã rõ.
Lỗi nghiệp vụ đã rõ trả exit 0 và `dat=false, da_dung=true`; trạm mới được thử lùi.
Không phát stdout/stderr của build ra kênh JSON. Log vận hành của wrapper phải dùng bộ lọc bí mật hiện có;
trạm chỉ giữ dữ liệu kết luận, không ghi lại output thô.

| `buoc` | Entry point / điều phải chứng minh |
|---|---|
| `chuan_bi` | Kiểm chỉ đọc: L đang phục vụ, đủ artifact/config, đã thử lùi, dữ liệu tương thích M; commit rỗng chỉ dò khả năng bật |
| `deploy` | Dùng artifact truy về M, build trong cách ly nếu cần; không lấy HEAD; chuyển đúng đích, đợi tác vụ kết thúc |
| `kiem_song` | M thực sự phục vụ + phép thử chức năng cốt lõi đạt, không chỉ HTTP 200/PID |
| `lui` | Dùng script tin cậy và artifact L; không chạy script của M, không restore DB |
| `kiem_song_sau_lui` | L thực sự phục vụ + phép thử chức năng cốt lõi đạt |
| `doi_soat` | Chỉ đọc lượt `ma`/bản thực tế, chứng minh hết writer; không deploy/lùi trong lúc đối soát |

Đường deploy tự giữ thông tin bản ổn định tại đích như cơ chế đang có; trạm không dựng thêm kho biên nhận. Không áp mẫu user/đường dẫn này nếu phải thay hệ deploy sẵn có;
đích đầu tiên cần được xác nhận ở R3, thiếu thì giữ tắt. Plan không cài wrapper hay nền deploy mới.
`san_sang` chỉ true sau lần thử đường lui có bằng chứng. `chuan_bi` lần đầu đọc L thực tế, không lấy chuỗi rỗng
của `commit_truoc` làm quyền deploy. Lịch sử trạm chỉ đổi bản ổn định sau kiểm thành công.

## Bản đồ tác động và trình tự

Giữ kho sự kiện, ledger thao tác/passkey, Uq, GitHub và launchd đang có. Không schema, dịch vụ hay dependency mới.
`deploy.lenh` ghi ý định trước tác dụng phụ và kết quả sau đó; UI chỉ dựng dòng kết quả, restart vẫn biết đang lùi.
Đối soát đi qua `chay_thao_tac` trước mọi ghi; không có sổ idempotency thứ hai.
Merge tự động chờ khi còn chuỗi deploy chưa kết thúc, kể cả crash chưa kịp ghi `deploy.xong`;
merge tay từ ngoài trạm vẫn được ghi nhận để xử lý sau. Không tạo cơ chế dò PID mới cho chốt này.
Chặn schema/đường cấm trên diff **L..M**, cả Deploy tay: diff với origin/main không đủ khi M đã merge.
Các fixture chuyển biên shell dưới trạm sang biên đích giả; test thu hồi/log/P1 nguyên vẹn.

Một file chỉ sửa ở task sở hữu dưới đây. Không còn “Create lần hai” hay Task 8 sửa lỗi để cứu GREEN của task trước.
Mỗi task: **test/fixture → RED hành vi → mã → GREEN + hồi quy**. Lệnh dưới chạy sau từng nửa RED/GREEN;
không chạy code block shell chứa lệnh sản phẩm thật. Mã mới ngoài phạm vi test đều là đề xuất trong tài liệu.

### Task 1: GitHub giữ CI bắt buộc; bỏ nút miễn CI

**RED cần chứng minh:** CI cũ không được miễn; required checks/nguồn/strict/queue đều đóng khi thiếu.

```bash
tests/chan_host/chay.sh -q tests/test_tm20_github.py tests/test_gh.py tests/test_gh_tu_merge.py tests/test_tu_dong_cai_dat.py
```

#### Test/fixture — áp trước, chạy RED

#### Create `tests/test_tm20_github.py` — toàn bộ file

```python
"""QĐ1: dữ liệu gh giả, không mạng, không chạy CLI thật."""
import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from tram.giao_viec.gh_bao_ve import cong_merge

H = "a" * 40
P = SimpleNamespace(so=1, head=H, base="main")
BV = {"required_status_checks": {"strict": True, "checks": [{"context": "test", "app_id": 1}]},
      "enforce_admins": {"enabled": True}, "required_pull_request_reviews":
      {"bypass_pull_request_allowances": {"users": [], "teams": [], "apps": []}}}
PR = {"headRefOid": H, "isDraft": False, "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN"}


def gia(bv=None, pr=None, checks=None, rules=None, fail=False):
    calls = []
    def run(argv, dau_vao):
        calls.append(argv)
        if fail:
            return 1, "secret", "secret"
        if "checks" in argv:
            d = [{"bucket": "pass"}] if checks is None else checks
        elif "view" in argv:
            d = PR if pr is None else pr
        elif argv[-1].endswith("/protection"):
            d = BV if bv is None else bv
        else:
            d = [[] if rules is None else rules]
        return 0, json.dumps(d), ""
    return run, calls


def test_optional_fail_does_not_block():
    run, calls = gia(pr={**PR, "mergeStateStatus": "UNSTABLE"})
    assert cong_merge(run, "owner/repo", P) == "xanh"
    assert any("--required" in a for a in calls)
    assert all("statusCheckRollup" not in " ".join(a) for a in calls)


@pytest.mark.parametrize("change", ["strict", "empty", "source", "admin", "bypass"])
def test_missing_protection_blocks(change):
    b = deepcopy(BV)
    if change == "strict":
        b["required_status_checks"]["strict"] = False
    if change == "empty":
        b["required_status_checks"]["checks"] = []
    if change == "source":
        b["required_status_checks"]["checks"][0]["app_id"] = -1
    if change == "admin":
        b["enforce_admins"]["enabled"] = False
    if change == "bypass":
        b["required_pull_request_reviews"]["bypass_pull_request_allowances"]["users"] = [{"id": 1}]
    assert cong_merge(gia(bv=b)[0], "owner/repo", P) == "do"


@pytest.mark.parametrize("kw", [
    {"fail": True}, {"checks": []}, {"checks": [{"bucket": "pending"}]},
    {"rules": [{"type": "merge_queue"}]}, {"pr": {**PR, "isDraft": True}},
    {"pr": {**PR, "headRefOid": "b" * 40}}, {"pr": {**PR, "mergeable": "CONFLICTING"}},
    {"pr": {**PR, "mergeStateStatus": "BEHIND"}}, {"pr": {**PR, "mergeStateStatus": "UNKNOWN"}},
])
def test_closed_when_uncertain(kw):
    assert cong_merge(gia(**kw)[0], "owner/repo", P) != "xanh"


def test_merge_queue_on_next_page_blocks():
    base, _ = gia()
    def run(argv, dau_vao):
        if "/rules/branches/" in argv[-1]:
            pages = [[], [{"type": "merge_queue"}]]
            data = pages if "--paginate" in argv and "--slurp" in argv else pages[0]
            return 0, json.dumps(data), ""
        return base(argv, dau_vao)
    assert cong_merge(run, "owner/repo", P) != "xanh"
```

#### Modify `tests/test_gh_tu_merge.py` — bản vá

```diff
--- a/tests/test_gh_tu_merge.py
+++ b/tests/test_gh_tu_merge.py
@@ -1,34 +1,6 @@
-"""TM-2 (spec `tu-merge` "Điều kiện CI GitHub xanh", D93; design D-2, D-3): đọc CI từ `statusCheckRollup`, dạng duy
-nhất của lệnh merge. Hàm thuần — không `gh`, không mạng."""
-import pytest
-
-from tram.giao_viec.gh_tu_merge import dang_merge, la_dang_merge, trang_thai_ci
-
+"""QĐ1: dạng lệnh merge chặt; required checks ở test_tm20_github."""
+from tram.giao_viec.gh_tu_merge import dang_merge, la_dang_merge
 R, H = "dai-ca/repo-nhap", "c" * 40
-
-
-def run(status="COMPLETED", conclusion="SUCCESS"):
-    return {"__typename": "CheckRun", "name": "test", "status": status, "conclusion": conclusion}
-
-
-def ctx(state):
-    return {"__typename": "StatusContext", "context": "ci/x", "state": state}
-
-
-@pytest.mark.parametrize("ds, ky_vong", [
-    ([], "rong"),                                                            # D93: không có CI = chưa xanh
-    ([run(), run(conclusion="NEUTRAL"), run(conclusion="SKIPPED"), ctx("SUCCESS")], "xanh"),
-    ([run(), run(status="IN_PROGRESS", conclusion="")], "dang_chay"),         # Scenario "CI đang chạy"
-    ([run(status="QUEUED", conclusion=None), ctx("PENDING")], "dang_chay"),
-    ([ctx("EXPECTED")], "dang_chay"),
-    ([run(), run(conclusion="FAILURE")], "do"),                               # Scenario "CI đỏ"
-    ([run(status="IN_PROGRESS"), run(conclusion="CANCELLED")], "do"),         # một cái hỏng là đỏ, dù cái khác chạy
-    ([run(conclusion="TIMED_OUT")], "do"), ([run(conclusion="ACTION_REQUIRED")], "do"), ([ctx("ERROR")], "do"),
-    ([ctx("FAILURE")], "do"), ([{"__typename": "Lạ"}], "do"), (["x"], "do"), (None, "do"), ({"a": 1}, "do"),
-])
-def test_trang_thai_ci(ds, ky_vong):
-    assert trang_thai_ci(ds) == ky_vong
-
 
 def test_dang_merge_duy_nhat():
     a = dang_merge(R, 12, H)
```

#### Modify `tests/test_gh.py` — bản vá

```diff
--- a/tests/test_gh.py
+++ b/tests/test_gh.py
@@ -89,11 +89,11 @@
 def test_xem_pr_doc_ci_tren_dau_pr():
     xanh = [{"__typename": "CheckRun", "status": "COMPLETED", "conclusion": "SUCCESS"}]
     c = Chay((0, json.dumps(pr(statusCheckRollup=xanh)), ""), (0, json.dumps([pr()]), ""))
-    assert GhCli(c).xem_pr(R, 7).ci == "xanh"
+    assert GhCli(c).xem_pr(R, 7).ci is None
     argv = c.goi[0][0]
-    assert argv[:4] == ["gh", "pr", "view", "7"] and argv[argv.index("--json") + 1].endswith(",statusCheckRollup")
+    assert argv[:4] == ["gh", "pr", "view", "7"] and "statusCheckRollup" not in argv[argv.index("--json") + 1]
     assert GhCli(c).ds_pr(R, "tram/hr-1")[0].ci is None                     # `list` không đọc CI
-    assert GhCli(Chay((0, json.dumps(pr(statusCheckRollup="lạ")), ""))).xem_pr(R, 7).ci == "do"
+    assert GhCli(Chay((0, json.dumps(pr(statusCheckRollup="lạ")), ""))).xem_pr(R, 7).ci is None
 
 
 @pytest.mark.parametrize("url,ky_vong", [
```

#### Modify `tests/test_tu_dong_cai_dat.py` — bản vá

```diff
--- a/tests/test_tu_dong_cai_dat.py
+++ b/tests/test_tu_dong_cai_dat.py
@@ -10,7 +10,7 @@
 LENH = {"deploy": "/Users/Shared/tram-deploy/repo-nhap/deploy.sh",
         "kiem_song": "curl -fsS --max-time 20 https://repo-nhap.example.vn/suc-khoe",
         "lui": "sh scripts/lui.sh --ve 'ban truoc'"}
-DU = tu_api({"tu_merge": True, "tu_deploy": True, "dieu_kien": {"ci": False, "cot": True, "hang_rao": True},
+DU = tu_api({"tu_merge": True, "tu_deploy": True, "dieu_kien": {"ci": True, "cot": True, "hang_rao": True},
              "lenh": LENH})
 
 
@@ -31,7 +31,7 @@
 
 def test_dang_api_va_dang_su_kien_qua_lai():
     assert sang_api(DU) == {"tu_merge": True, "tu_deploy": True,
-                            "dieu_kien": {"ci": False, "cot": True, "hang_rao": True}, "lenh": LENH}
+                            "dieu_kien": {"ci": True, "cot": True, "hang_rao": True}, "lenh": LENH}
     assert tu_api(sang_api(DU)) == DU and DU.du_lenh
     assert tu_phang(DU.phang()) == DU
     assert tu_phang({"tu_merge": True, "khoa_tuong_lai": 1}) == replace(MAC_DINH, tu_merge=True)   # mã cũ/mới đọc nhau
@@ -40,7 +40,7 @@
 
 def test_truong_doi_theo_thu_tu_mo_hinh():
     assert truong_doi(MAC_DINH, MAC_DINH) == []
-    assert truong_doi(MAC_DINH, DU) == ["tu_merge", "tu_deploy", "dk_ci", "lenh_deploy", "lenh_kiem_song", "lenh_lui"]
+    assert truong_doi(MAC_DINH, DU) == ["tu_merge", "tu_deploy", "lenh_deploy", "lenh_kiem_song", "lenh_lui"]
 
 
 @pytest.mark.parametrize("lenh", ["", *LENH.values(), "make deploy", "./scripts/kiem-song.sh"])
```

#### Mã — chỉ áp sau RED, rồi chạy lại lệnh trên

#### Create `tram/giao_viec/gh_bao_ve.py` — toàn bộ file

```python
"""QĐ1: classic branch protection + required checks do gh chọn, không phân loại CI tuỳ chọn."""
import json
from urllib.parse import quote

from tram.giao_viec.gh_tu_merge import REPO_RE


def bao_ve_dat(d):
    try:
        checks = d["required_status_checks"]
        nguon = checks["checks"]
        bypass = (d.get("required_pull_request_reviews") or {}).get("bypass_pull_request_allowances", {})
        return (checks["strict"] is True and d["enforce_admins"]["enabled"] is True
                and isinstance(nguon, list) and bool(nguon)
                and all(isinstance(x.get("context"), str) and bool(x["context"])
                        and type(x.get("app_id")) is int and x["app_id"] > 0 for x in nguon)
                and not any(bypass.get(k) for k in ("users", "teams", "apps")))
    except (KeyError, TypeError, AttributeError):
        return False


def cong_merge(chay, repo, pr):
    if not REPO_RE.fullmatch(repo):
        return "do"
    def doc(argv):
        ma, ra, _ = chay(["gh", *argv], None)
        if ma and not (argv[:2] == ["pr", "checks"] and ma in (1, 8)):
            raise ValueError("github-chua-cho-phep")
        return json.loads(ra)
    try:
        base = quote(pr.base, safe="")
        bv = doc(["api", "--method", "GET", f"repos/{repo}/branches/{base}/protection"])
        pages = doc(["api", "--method", "GET", "--paginate", "--slurp",
                     f"repos/{repo}/rules/branches/{base}"])
        if not isinstance(pages, list) or not pages or not all(isinstance(p, list) for p in pages):
            return "do"
        rules = [r for page in pages for r in page]
        if not bao_ve_dat(bv) or not isinstance(rules, list) or any(
                r.get("type") == "merge_queue" for r in rules):
            return "do"
        p = doc(["pr", "view", str(pr.so), "--repo", repo, "--json",
                 "headRefOid,isDraft,mergeable,mergeStateStatus"])
        if (p.get("headRefOid") != pr.head or p.get("isDraft") is not False
                or p.get("mergeable") != "MERGEABLE" or p.get("mergeStateStatus") not in ("CLEAN", "UNSTABLE")):
            return "do"
        checks = doc(["pr", "checks", str(pr.so), "--repo", repo, "--required", "--json", "bucket"])
        return "xanh" if isinstance(checks, list) and checks and all(
            c.get("bucket") in ("pass", "skipping") for c in checks) else "do"
    except (ValueError, KeyError, TypeError, AttributeError):
        return "loi"
```

#### Modify `tram/giao_viec/gh.py` — bản vá

```diff
--- a/tram/giao_viec/gh.py
+++ b/tram/giao_viec/gh.py
@@ -10,11 +10,11 @@
 from dataclasses import dataclass
 from pathlib import Path
 
-from tram.giao_viec.gh_tu_merge import REPO_RE, SHA_RE, dang_merge, la_dang_merge, trang_thai_ci
+from tram.giao_viec.gh_tu_merge import REPO_RE, SHA_RE, dang_merge, la_dang_merge
 from tram.giao_viec.git_kiem import GIT
 
 TRUONG = "number,url,state,headRefName,headRefOid,baseRefName,isCrossRepository,mergedAt,mergeCommit"
-TRUONG_XEM = TRUONG + ",statusCheckRollup"                    # CI trên đầu PR (D-2) — chỉ `view`
+TRUONG_XEM = TRUONG                    # CI trên đầu PR (D-2) — chỉ `view`
 LENH_DUOC_PHEP = frozenset({"list", "view", "create", "merge"})   # `merge`: chỉ dạng `la_dang_merge` (test khoá)
 REMOTE_RE = re.compile(r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)"
                        r"([A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}?)(?:\.git)?/?")
@@ -35,7 +35,7 @@
     base: str
     ngoai_repo: bool
     merge_commit: str | None
-    ci: str | None = None    # xanh | do | dang_chay | rong (`gh_tu_merge.trang_thai_ci`); None: lệnh không đọc CI
+    ci: str | None = None    # xanh | do | dang_chay | rong (kết luận cổng GitHub); None: lệnh không đọc CI
 
 
 def chay_gh(argv: list[str], dau_vao: str | None) -> tuple[int, str, str]:
@@ -60,7 +60,7 @@
         so, mc = d["number"], d["mergeCommit"]
         pr = PrInfo(so, d["url"], d["state"], d["headRefName"], d["headRefOid"], d["baseRefName"],
                     d["isCrossRepository"], mc["oid"] if mc else None,
-                    trang_thai_ci(d["statusCheckRollup"]) if "statusCheckRollup" in d else None)
+                    None)
     except (TypeError, KeyError) as e:
         raise LoiGh(f"gh trả PR sai dạng: {type(e).__name__}") from None
     if (type(so) is not int or so <= 0 or pr.url != f"https://github.com/{repo}/pull/{so}"
@@ -107,6 +107,10 @@
         self._gh("create", "--repo", repo, "--head", nhanh, "--base", base, f"--title={tieu_de}",
                  "--body-file", "-", dau_vao=than)
 
+    def cong_merge(self, repo: str, pr: PrInfo) -> str:
+        from tram.giao_viec.gh_bao_ve import cong_merge
+        return cong_merge(self._chay, repo, pr)
+
     def merge_pr(self, repo: str, so: int, commit: str) -> None:
         """Lỗi hay không rõ → `LoiGh`; người gọi ĐỌC LẠI PR trước khi gửi lại (spec `tu-merge`, design D-7)."""
         if (args := dang_merge(repo, so, commit)) is None:
```

#### Modify `tram/api/than.py` — bản vá

```diff
--- a/tram/api/than.py
+++ b/tram/api/than.py
@@ -52,7 +52,7 @@
 
 
 class ThanDieuKien(_Kin):                                   # TM-1 (D70, D71): chỉ ba nút có nút; QC/kiểm lại → 422
-    ci: bool
+    ci: Literal[True]
     cot: bool
     hang_rao: bool
 
```

#### Modify `tram/tu_dong/cai_dat.py` — bản vá

```diff
--- a/tram/tu_dong/cai_dat.py
+++ b/tram/tu_dong/cai_dat.py
@@ -38,19 +38,19 @@
 
 def tu_phang(d: dict) -> CaiDatTuDong:
     """Đọc từ sự kiện: khoá lạ bỏ qua, khoá thiếu lấy mặc định — mã cũ đọc được sự kiện mới và ngược lại."""
-    return CaiDatTuDong(**{k: v for k, v in d.items() if k in _TEN})
+    return CaiDatTuDong(**{**{k: v for k, v in d.items() if k in _TEN}, "dk_ci": True})
 
 
 def sang_api(cd: CaiDatTuDong) -> dict:
     return {"tu_merge": cd.tu_merge, "tu_deploy": cd.tu_deploy,
-            "dieu_kien": {"ci": cd.dk_ci, "cot": cd.dk_cot, "hang_rao": cd.dk_hang_rao},
+            "dieu_kien": {"ci": True, "cot": cd.dk_cot, "hang_rao": cd.dk_hang_rao},
             "lenh": {"deploy": cd.lenh_deploy, "kiem_song": cd.lenh_kiem_song, "lui": cd.lenh_lui}}
 
 
 def tu_api(d: dict) -> CaiDatTuDong:
     """`d` đã qua kiểm thân yêu cầu (đủ khoá, đúng kiểu, không khoá lạ). Lệnh bỏ khoảng trắng hai đầu."""
     dk, ln = d["dieu_kien"], d["lenh"]
-    return CaiDatTuDong(d["tu_merge"], d["tu_deploy"], dk["ci"], dk["cot"], dk["hang_rao"],
+    return CaiDatTuDong(d["tu_merge"], d["tu_deploy"], True, dk["cot"], dk["hang_rao"],
                         ln["deploy"].strip(), ln["kiem_song"].strip(), ln["lui"].strip())
 
 
```

#### Modify `tram/giao_viec/gh_tu_merge.py` — bản vá

```diff
--- a/tram/giao_viec/gh_tu_merge.py
+++ b/tram/giao_viec/gh_tu_merge.py
@@ -8,8 +8,6 @@
 
 SHA_RE = re.compile(r"[0-9a-f]{40}")
 REPO_RE = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}")
-KET_LUAN_XANH = frozenset({"SUCCESS", "NEUTRAL", "SKIPPED"})
-CI = ("xanh", "do", "dang_chay", "rong")
 
 
 def dang_merge(repo: str, so: int, commit: str) -> list[str] | None:
@@ -23,26 +21,3 @@
     """Chặn ở cửa `GhCli._gh`: đối số của `merge` phải đúng y dạng `dang_merge` sinh ra."""
     return (len(args) == 6 and args[0].isdigit() and args[0] == str(int(args[0]))
             and dang_merge(args[2], int(args[0]), args[5]) == list(args))
-
-
-def _mot(c: object) -> str:
-    if not isinstance(c, dict):
-        return "do"
-    if c.get("__typename") == "CheckRun":
-        if c.get("status") != "COMPLETED":
-            return "dang_chay"
-        return "xanh" if c.get("conclusion") in KET_LUAN_XANH else "do"
-    if c.get("__typename") == "StatusContext":
-        s = c.get("state")
-        return "xanh" if s == "SUCCESS" else "dang_chay" if s in ("PENDING", "EXPECTED") else "do"
-    return "do"                                 # dạng lạ → coi là chưa xanh (đóng khi không biết)
-
-
-def trang_thai_ci(ds: object) -> str:
-    """`xanh` khi MỌI kiểm tra đã xong và đạt; một cái hỏng → `do`; còn chạy → `dang_chay`; không có → `rong` (D93)."""
-    if not isinstance(ds, list):
-        return "do"
-    if not ds:
-        return "rong"
-    kq = {_mot(c) for c in ds}
-    return "do" if "do" in kq else "dang_chay" if "dang_chay" in kq else "xanh"
```

**GREEN:** tất cả test của task và hồi quy liên quan đạt, 0 dòng chặn mới; lỗi host không được tính là GREEN.

### Task 2: Bằng chứng Uq, decision và chốt merge hiện hành

**RED cần chứng minh:** Marker legacy/sai lượt hoặc decision mở/thiếu phải chặn. Lỗi đọc ba lần phải dừng và ghi một lỗi.

```bash
tests/chan_host/chay.sh -q tests/test_tm20_bang_chung.py tests/test_tm20_doc_github.py tests/test_tm20_decision.py tests/test_tu_merge*.py
```

#### Test/fixture — áp trước, chạy RED

#### Modify `tests/gh_gia.py` — bản vá

```diff
--- a/tests/gh_gia.py
+++ b/tests/gh_gia.py
@@ -34,6 +34,9 @@
             self.khi_xem(so)
         return self.prs[so]
 
+    def cong_merge(self, repo, pr):
+        return pr.ci or "xanh"
+
     def merge_pr(self, repo, so, commit):
         self._kiem("merge_pr", repo, so, commit)
         p = self.prs[so]
```

#### Modify `tests/test_tu_merge.py` — bản vá

```diff
--- a/tests/test_tu_merge.py
+++ b/tests/test_tu_merge.py
@@ -48,6 +48,7 @@
     (goc := tmp_path / "repo-tram" / "du-an").mkdir(parents=True)
     (goc / "hr-codex.yaml").write_text(f"ten: hr-codex\nbat_ghi: {'true' if bat_ghi else 'false'}\n")
     monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo-tram"))
+    monkeypatch.setattr("tram.giao_viec.tu_merge_gui.cong_mo", lambda: True)
     t = dung(tmp_path, bug(**{**GIU, **b_kw}), *them)
     da = replace(t.da, hang_rao=TIEN if hang_rao is None else hang_rao,
                  giao=replace(t.da.giao, duong_dan_cam_cho_phep=cho_phep))
@@ -288,7 +289,7 @@
     ("Đại ca đã tự gán cột", {"labels": ["cot:ai-lam", "cot-khoa"]}, {}, ["cot"]),
     ("Tắt nút cột", {"labels": ["cot:ai-lam", "cot-khoa"]}, {"dk_cot": False}, []),
     ("Repo chưa có CI, nút CI bật", {}, {"ci": "rong"}, ["ci_rong"]),
-    ("Dự án tắt nút CI", {}, {"ci": "rong", "dk_ci": False}, []),
+    ("Cờ CI cũ không miễn khoá", {}, {"ci": "rong", "dk_ci": False}, ["ci_rong"]),
 ])
 def test_dieu_kien_tren_du_lieu_that(tmp_path, monkeypatch, canh, kw, nut, ly_do):
     """Mốc 2.6: hàng rào chỉ theo đường dẫn diff (D91); `schema` theo đường dẫn + từ khoá, không theo nút (D76, D92,
```

#### Modify `tests/test_tu_merge_xet.py` — bản vá

```diff
--- a/tests/test_tu_merge_xet.py
+++ b/tests/test_tu_merge_xet.py
@@ -54,7 +54,7 @@
                "PR không do trạm mở": ["pr_khac"], "QC trả về": ["qc"],
                "Kiểm lại không đạt / bằng chứng hết hiệu lực": ["kiem_lai"], "CI đang chạy": ["ci_dang_chay"],
                "CI đỏ": ["ci_do"], "Repo chưa có CI, nút CI bật (D93)": ["ci_rong"], "Đại ca đã tự gán cột": ["cot"],
-               "Diff chạm đường dẫn tiền": ["hang_rao_tien"],
+               "Dự án tắt nút CI": ["ci_rong"], "Diff chạm đường dẫn tiền": ["hang_rao_tien"],
                "Tắt nút hàng rào vẫn chặn migration": ["schema_duong_dan"],
                "Việc nói tới xoá dữ liệu": ["schema_tu_khoa"],
                "Agent sửa file lệnh deploy dùng, tắt nút hàng rào (D89)": ["file_lenh"],
@@ -85,8 +85,8 @@
         "dau_pr_khac", "schema_duong_dan", "schema_tu_khoa", "file_lenh", "ci_do", "cot", "hang_rao_tien",
         "hang_rao_co_do"]
     tat_nut = replace(tt, cai_dat=replace(MAC_DINH, dk_ci=False, dk_cot=False, dk_hang_rao=False))
-    assert ly_do_chua_merge(tat_nut, het, bat_ghi=True, estop_bat=False)[-3:] == ["schema_duong_dan",
-                                                                                 "schema_tu_khoa", "file_lenh"]
+    assert ly_do_chua_merge(tat_nut, het, bat_ghi=True, estop_bat=False)[-4:] == [
+        "schema_duong_dan", "schema_tu_khoa", "file_lenh", "ci_do"]
     assert all(m in NHAN for m in ly_do_chua_merge(tt, het, bat_ghi=False, estop_bat=True))
 
 
@@ -109,10 +109,11 @@
     goc = [("giao.nhan", {"giao_id": "g-1", "luot": 1, "buoc": "code", "khe_id": "B/claude-1"}),
            ("giao.ket_thuc", {"giao_id": "g-1", "ket_thuc": "xong", "ly_do": None, "commit": C}),
            ("kiem.lai", {"giao_id": "g-1", "bead_id": "hr-1", "luot": 1, "commit": C, "digest_tieu_chi": "d",
-                         "dat": dat}),
+                         "dat": dat, "nguon_kiem": "uq"}),
            ("giao.nhan", {"giao_id": "g-2", "luot": 2, "buoc": "qc", "khe_id": khe_qc}),
            ("qc.ket_qua", {"giao_id": "g-2", "commit_code": C, "commit_qc": Q, "ket_luan": ket_luan}),
-           ("bead.vao_cot_3", {"commit_code": C, "commit_ban_giao": Q, "giao_id_code": "g-1", "luot_code": 1}),
+           ("bead.vao_cot_3", {"commit_code": C, "commit_ban_giao": Q, "giao_id_code": "g-1", "luot_code": 1,
+                              "digest_tieu_chi": "d"}),
            *them]
     return [SK(i, l, d, "2026-10-18T03:00:00Z") for i, (l, d) in enumerate(goc, 1)]
 
```

#### Create `tests/test_tm20_bang_chung.py` — toàn bộ file

```python
"""Không nâng kết quả legacy/agent thành Uq; khớp đủ bộ bằng chứng."""
from dataclasses import replace
import pytest
from test_tu_merge_xet import _ds
from tram.giao_viec.tu_merge_xet import kiem_lai_qc
from tram.tu_dong import cong_kiem


@pytest.mark.parametrize("k,v", [
    ("nguon_kiem", "agent"), ("nguon_kiem", None), ("luot", 2),
    ("giao_id", "g-khac"), ("commit", "c" * 40), ("digest_tieu_chi", "khac"), ("dat", False),
])
def test_sai_mot_phan_la_dong(k, v):
    ds = _ds()
    ds[2] = replace(ds[2], du_lieu={**ds[2].du_lieu, k: v})
    assert kiem_lai_qc(ds, ds[5]) == (False, False)


def test_cong_loi_thi_dong(monkeypatch):
    class Cong:
        def trang_thai(self):
            raise OSError("khong-doc-duoc")
    monkeypatch.setattr(cong_kiem, "CongTuXa", Cong)
    assert cong_kiem.cong_mo() is False


def test_cong_mo_chua_du_neu_con_dau(monkeypatch, tmp_path):
    class Cong:
        def trang_thai(self):
            return {"trang_thai": "mo"}
    monkeypatch.setattr(cong_kiem, "CongTuXa", Cong)
    monkeypatch.setenv("TRAM_HOME", str(tmp_path))
    assert cong_kiem.cong_mo()
    (tmp_path / "kiem-lai.dong").touch()
    assert not cong_kiem.cong_mo()
```

#### Modify `tests/su_kien_gia.py` — bản vá

```diff
--- a/tests/su_kien_gia.py
+++ b/tests/su_kien_gia.py
@@ -29,7 +29,7 @@
 def kiem(kho, giao_id, commit, dat=True, digest="sha256:d", luot=1, bead_id="hr-1"):
     return sk(kho, "kiem.lai", {"giao_id": giao_id, "bead_id": bead_id, "luot": luot, "commit": commit,
                                 "digest_tieu_chi": digest, "dat": dat, "ket_qua": [], "digest_log": [],
-                                "cham_cam": []}, bead_id)
+                                "cham_cam": [], "nguon_kiem": "uq"}, bead_id)
 
 
 def qc(kho, giao_id, commit_code, commit_qc, ket_luan="dat", bead_id="hr-1", phat_hien=()):
```

#### Modify `tests/test_tu_merge_spec.py` — bản vá

```diff
--- a/tests/test_tu_merge_spec.py
+++ b/tests/test_tu_merge_spec.py
@@ -29,6 +29,7 @@
     (goc := tmp_path / "repo-tram" / "du-an").mkdir(parents=True)
     (goc / "hr-codex.yaml").write_text("ten: hr-codex\nbat_ghi: true\n")
     monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo-tram"))
+    monkeypatch.setattr("tram.giao_viec.tu_merge_gui.cong_mo", lambda: True)
     k, kho = dung_kho(tmp_path), kho_tam(tmp_path)
     s = k.day("tram/spec-hr-f", {"docs/specs/x.md": "spec\n"}, tu=k.main)
     fetch(k.kho)
```

#### Create `tests/test_tm20_doc_github.py` — toàn bộ file

```python
"""Lỗi đọc bền qua tick; không lặp merge, thành công xoá chuỗi lỗi đọc."""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from gh_gia import REPO
from su_kien_gia import ds
from test_tu_merge import cot_3_co_pr, dung_tu_merge
from tram.giao_viec.gh import LoiGh
from tram.giao_viec.tu_merge_gui import gui_merge


@pytest.mark.parametrize("hong", ["xem_pr", "cong_merge"])
def test_ba_vong_doc_hong_dung_thu(tmp_path, monkeypatch, hong):
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    calls = []
    def loi(*args):
        calls.append(1)
        raise LoiGh("github-doc-loi")
    monkeypatch.setattr(gh, hong, loi)
    for _ in range(4):
        gui_merge(gh, REPO, t.kho, "hr-codex", "hr-1", ds(t.kho), so_pr=1, commit=q,
                  loai="code", ly_do=lambda pr: [], luc=datetime.now(timezone.utc))
    assert len(calls) == 3
    assert sum(s.loai == "tu_merge.loi" for s in ds(t.kho)) == 1
    assert not any(s.loai == "tu_merge.bat_dau" for s in ds(t.kho))


def test_doc_tot_xoa_chuoi_loi(tmp_path, monkeypatch):
    from tram.giao_viec.doc_merge import ghi_doc
    t, _, _ = dung_tu_merge(tmp_path, monkeypatch)
    luc = datetime.now(timezone.utc)
    def ghi(loi):
        return ghi_doc(t.kho, "hr-codex", "hr-1", ds(t.kho), "tm-doc", loi, luc)
    assert [ghi(True), ghi(True), ghi(False), ghi(True)] == [1, 2, 0, 1]


def test_crash_before_deploy_result_blocks_merge(tmp_path, monkeypatch):
    from tram.deploy.ghi import ghi
    from test_tu_merge import merge_goi
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    ghi(t.kho.db, 'hr-codex', 'deploy.bat_dau', {'ma_thao_tac': 'dp-pending'})
    gui_merge(gh, REPO, t.kho, 'hr-codex', 'hr-1', ds(t.kho), so_pr=1, commit=q,
              loai='code', ly_do=lambda pr: [], luc=datetime.now(timezone.utc))
    assert not merge_goi(gh)
```

#### Create `tests/test_tm20_decision.py` — toàn bộ file

```python
"""Cửa đọc tươi phải dùng cùng luật blocks của luồng giao việc."""
from dataclasses import replace
from types import SimpleNamespace as NS
import pytest
from bd_gia import BdGia
from tram.beads.mo_hinh import Bead, PhuThuoc
from tram.giao_viec.tu_merge_tuoi import doc_hien_hanh
from tram.phieu.kho import KhoPhieu


@pytest.mark.parametrize('state', ['open', 'missing', 'closed'])
def test_dependency_is_rechecked_at_merge(tmp_path, state):
    b = Bead.tu_json(dict(id='b', updated_at='2026-10-20', status='in_progress', issue_type='task'))
    b = replace(b, phu_thuoc=(PhuThuoc('decision-1', 'blocks'),))
    d = replace(b, id='decision-1', issue_type='decision', phu_thuoc=(), status=state)
    bd = BdGia([b] if state == 'missing' else [b, d])
    k = KhoPhieu(tmp_path / 'sk.db')
    try:
        assert (doc_hien_hanh(bd, k, NS(ten='a'), 'b') is not None) == (state == 'closed')
    finally:
        k.close()
```

#### Mã — chỉ áp sau RED, rồi chạy lại lệnh trên

#### Modify `tram/giao_viec/tu_merge_gui.py` — bản vá

```diff
--- a/tram/giao_viec/tu_merge_gui.py
+++ b/tram/giao_viec/tu_merge_gui.py
@@ -7,9 +7,13 @@
 from collections.abc import Callable
 from datetime import datetime
 
-from tram.giao_viec.gh import GhCli, PrInfo
+from tram.giao_viec.gh import GhCli, PrInfo, LoiGh
+from tram.giao_viec.doc_merge import doc, ghi_doc
 from tram.giao_viec.su_kien import SK, cua_so, da_co, moi_nhat
 from tram.phieu.kho import KhoPhieu
+from tram.tu_dong.cong_kiem import cong_mo
+from tram.deploy.doi_soat import chua_doi_soat
+from tram.deploy.trang_thai import chuoi_dang_do, doc_su_kien
 
 TAC_NHAN = "tram/tu-merge"
 SO_LAN = 3
@@ -60,7 +64,12 @@
     if any(s.loai in ("tu_merge.xong", "tu_merge.loi") and s.du_lieu.get("ma_thao_tac") == ma for s in ds):
         return None
     da_gui = sum(1 for s in ds if s.loai == "tu_merge.bat_dau" and s.du_lieu.get("ma_thao_tac") == ma)
-    pr = gh.xem_pr(repo, so_pr)
+    try:
+        pr = doc(gh, repo, so_pr)
+    except LoiGh:
+        n = ghi_doc(kho, du_an, bead_id, ds, ma, True, luc)
+        return _loi(kho, du_an, bead_id, ma, "gh-doc-loi-3-lan", luc) if n >= SO_LAN else None
+    ghi_doc(kho, du_an, bead_id, ds, ma, False, luc)
     if pr.trang_thai == "MERGED":
         if not da_gui:
             return None                                     # Đại ca merge tay — xác minh như luồng cũ
@@ -68,7 +77,14 @@
             kho, du_an, bead_id, ma, "merge-khac-commit", luc)
     if pr.trang_thai != "OPEN":
         return _loi(kho, du_an, bead_id, ma, "pr-da-dong", luc) if da_gui else None
-    if ly := ly_do(pr):
+    cong = cong_mo()
+    ly = ly_do(pr)
+    if not cong:
+        ly.append("cong_kiem")
+    deploy = doc_su_kien(kho.db, du_an)
+    if chua_doi_soat(deploy) or chuoi_dang_do(deploy):
+        ly.append("deploy_chua_ro")
+    if ly:
         ghi_cho(kho, du_an, bead_id, ds, ly, commit, luc)
         return None
     if da_gui >= SO_LAN:
```

#### Modify `tram/giao_viec/tu_merge_xet.py` — bản vá

```diff
--- a/tram/giao_viec/tu_merge_xet.py
+++ b/tram/giao_viec/tu_merge_xet.py
@@ -11,7 +11,10 @@
 from tram.tu_dong.khoa import NHAN_LY_DO, ly_do_chan
 from tram.tu_dong.luu import TrangThaiTuDong
 
-NHAN = {**NHAN_LY_DO, "du_lieu_loi": "Không đọc được dữ kiện hiện hành — chờ xét lại",
+NHAN = {**NHAN_LY_DO,
+        "cong_kiem": "Cổng kiểm đóng hoặc chưa đọc được",
+        "deploy_chua_ro": "Deploy chưa đối soát — cần Đại ca xác nhận bản thực tế",
+         "du_lieu_loi": "Dữ kiện chưa đủ hoặc việc còn bị chặn — chờ xét lại",
         "du_lieu_doi": "Dữ kiện duyệt spec đã đổi — chờ xét lại", "qc": "QC chưa đạt cho đúng commit này",
         "kiem_lai": "Kiểm lại chưa đạt hoặc bằng chứng hết hiệu lực", "pr_khac": "PR không phải PR trạm đã mở",
         "dau_pr_khac": "Đầu PR khác commit đã kiểm", "schema_duong_dan": "Cấu trúc DB — luôn chờ Đại ca",
@@ -48,7 +51,7 @@
     ra += [m for m, chan in (("qc", not dk.qc_dat), ("kiem_lai", not dk.kiem_lai_dat), ("pr_khac", not dk.dung_pr),
                              ("dau_pr_khac", not dk.dau_pr_dung)) if chan]
     ra += [*dk.schema, *dk.file_lenh]
-    ra += [f"ci_{dk.ci}"] if cd.dk_ci and dk.ci != "xanh" else []
+    ra += [f"ci_{dk.ci}"] if dk.ci != "xanh" else []
     ra += ["cot"] if cd.dk_cot and not dk.cot_ai else []
     return ra + (list(dk.hang_rao) if cd.dk_hang_rao else [])
 
@@ -67,6 +70,12 @@
     nhãn. Kiểm lại: lượt code mới nhất đạt tại `commit_code` của `v`. QC: kết luận đạt sau lần kiểm lại đó, cho đúng
     commit, do khe KHÁC khe đã code (INV-006); thiếu sự kiện nhận việc của khe QC → không đạt (đóng khi không biết)."""
     d, w = v.du_lieu, cua_so(ds)
+    ket = moi_nhat(w, "kiem.lai")
+    if ket is None or ket.du_lieu.get("nguon_kiem") != "uq" or any(
+            ket.du_lieu.get(a) != d.get(b) for a, b in (
+                ("luot", "luot_code"), ("giao_id", "giao_id_code"),
+                ("commit", "commit_code"), ("digest_tieu_chi", "digest_tieu_chi"))):
+        return False, False
     kl = bo_bang_chung("", ds, la_spike=True)
     kl_dat = kl is not None and (kl["commit_code"], kl["giao_id_code"]) == (d["commit_code"], d["giao_id_code"])
     bc = bo_bang_chung("", ds, la_spike=False)
```

#### Modify `tram/giao_viec/tu_merge.py` — bản vá

```diff
--- a/tram/giao_viec/tu_merge.py
+++ b/tram/giao_viec/tu_merge.py
@@ -97,6 +97,7 @@
         moi, bg, es = _khoa(kho, da)
         cam = cam if moi.cai_dat == tt.cai_dat else ("file_lenh_loi",)
         return ly_do_chua_merge_spec(moi, dung_pr=_dung_pr(pr, mo.du_lieu, f"tram/spec-{b.id}", da),
-                                     dau_pr_dung=pr.head == c, bat_ghi=bg, estop_bat=es, file_lenh=cam)
+                                     dau_pr_dung=pr.head == c, bat_ghi=bg, estop_bat=es,
+                                     file_lenh=cam + (() if pr.ci == "xanh" else ("ci_do",)))
     return gui_merge(gh, repo, kho, da.ten, b.id, ds, so_pr=mo.du_lieu["pr"], commit=c, loai="spec", ly_do=ly_do,
                      luc=luc)
```

#### Create `tram/tu_dong/cong_kiem.py` — toàn bộ file

```python
"""Đọc cổng hiện có; không mở lại và không fallback sang principal trạm."""
from tram.duong_dan import tram_home
from tram.quan_kiem.client import CongTuXa


def cong_mo():
    try:
        return (not (tram_home() / "kiem-lai.dong").exists()
                and CongTuXa().trang_thai().get("trang_thai") == "mo")
    except (OSError, ValueError):
        return False
```

#### Modify `tram/giao_viec/tick_pipeline.py` — bản vá

```diff
--- a/tram/giao_viec/tick_pipeline.py
+++ b/tram/giao_viec/tick_pipeline.py
@@ -55,6 +55,7 @@
     return ghi_ket_qua(kho, da, p, sha, {
         "giao_id": p.giao_id, "bead_id": b.id, "luot": p.luot, "commit": sha,
         "digest_tieu_chi": digest_tieu_chi(list(p.tieu_chi)), "dat": kq.dat,
+        "nguon_kiem": "uq" if bo.kiem_tu_xa is not None and p.can_lenh_kiem else "legacy",
         "ket_qua": list(kq.ket_qua), "digest_log": kq.digest_log, "cham_cam": list(kq.cham_cam)}, luc)
 
 
```

#### Create `tram/deploy/doi_soat.py` — toàn bộ file

```python
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
```

#### Create `tram/giao_viec/doc_merge.py` — toàn bộ file

```python
"""Đọc trước merge, đếm lỗi liên lạc liên tiếp trong kho sự kiện đang có."""
from dataclasses import replace

from tram.giao_viec.gh import LoiGh


def doc(gh, repo, so):
    pr = gh.xem_pr(repo, so)
    if pr.trang_thai == "OPEN":
        pr = replace(pr, ci=gh.cong_merge(repo, pr))
        if pr.ci == "loi":
            raise LoiGh("github-doc-loi")
    return pr


def ghi_doc(kho, du_an, bead_id, ds, ma, loi, luc):
    cu = next((s.du_lieu for s in reversed(ds) if s.loai == "tu_merge.doc"
               and s.du_lieu.get("ma_thao_tac") == ma), {})
    n = int(cu.get("loi_lien_tiep", 0)) + 1 if loi else 0
    if loi or cu.get("loi_lien_tiep", 0):
        with kho.giao_dich():
            kho.ghi_su_kien(du_an, "tu_merge.doc", {"ma_thao_tac": ma, "loi_lien_tiep": n},
                            luc=luc, bead_id=bead_id, tac_nhan="tram/tu-merge")
    return n
```

#### Modify `tram/giao_viec/tu_merge_tuoi.py` — bản vá

```diff
--- a/tram/giao_viec/tu_merge_tuoi.py
+++ b/tram/giao_viec/tu_merge_tuoi.py
@@ -2,6 +2,7 @@
 import sqlite3
 
 from tram.beads.bd import LoiBd
+from tram.cham_cot.luat_cung import bi_chan_boi
 from tram.giao_viec.doc_lai import dau_bead
 from tram.giao_viec.su_kien import cua_so, moi_nhat, su_kien_bead
 
@@ -9,8 +10,11 @@
 def doc_hien_hanh(bd, kho, da, bead_id):
     """Không dùng bộ đệm. Đọc Beads trước SQLite vì bd list có thể chậm; không giữ giao dịch khi đọc bd."""
     try:
-        b = next((b for b in bd.tat_ca() if b.id == bead_id), None)
-        return (b, su_kien_bead(kho, da.ten, bead_id)) if b is not None else None
+        theo_id = {b.id: b for b in bd.tat_ca()}
+        b = theo_id.get(bead_id)
+        if b is None or bi_chan_boi(b, theo_id):
+            return None
+        return b, su_kien_bead(kho, da.ten, bead_id)
     except (LoiBd, OSError, ValueError, sqlite3.Error):
         return None
 
```

**GREEN:** tất cả test của task và hồi quy liên quan đạt, 0 dòng chặn mới; lỗi host không được tính là GREEN.

### Task 3: Ba thao tác qua quyền riêng; xác minh bản thực tế

**RED cần chứng minh:** Exit 0 nhưng thiếu trường/sai bản/artifact không được đạt; timeout hoặc chưa dừng phải không rõ.

```bash
tests/chan_host/chay.sh -q tests/test_tm20_duong.py
```

#### Test/fixture — áp trước, chạy RED

#### Create `tests/test_tm20_duong.py` — toàn bộ file

```python
"""Biên deploy giả; không sudo, launchd hay quyền máy thật."""
import json
from types import SimpleNamespace
import pytest
from tram.deploy import duong
from tram.tu_dong.cai_dat import CaiDatTuDong


def cd(ten="a"):
    def lenh(b):
        return f"/usr/bin/sudo -n -u tram-dp-{ten} -- /Library/TramDeploy/{ten}/{b}"
    return CaiDatTuDong(lenh_deploy=lenh("deploy"), lenh_kiem_song=lenh("kiem-song"), lenh_lui=lenh("lui"))


def test_shape_rejects_repo_shell_and_other_target():
    assert duong.tach_lenh("a", cd())
    assert duong.tach_lenh("b", cd()) is None
    assert duong.tach_lenh("a", CaiDatTuDong(lenh_deploy="sh deploy.sh")) is None


def test_response_bound_to_target_version_and_run(monkeypatch):
    monkeypatch.setattr(duong, "kiem_tep", lambda p: None)
    monkeypatch.setattr(duong.pwd, "getpwnam", lambda n: SimpleNamespace(pw_uid=900, pw_dir="/tmp/nha-dp"))
    monkeypatch.setattr(duong.os, "getuid", lambda: 501)
    calls = []
    def run(argv, **kw):
        calls.append((argv, kw))
        r = json.loads(kw["input"])
        d = {**r, "dat": True, "da_dung": True, "san_sang": True, "ban_truoc": "b" * 40, "ban_thuc": r["commit"], "artifact": r["commit"]}
        return SimpleNamespace(returncode=0, stdout=json.dumps(d).encode(), stderr=b"")
    monkeypatch.setattr(duong, "chay_gioi_han", run)
    d = duong.DuongDeploy("a", cd())
    r = d.goi("kiem_song", "dp-1", "a" * 40, "b" * 40)
    assert r["dat"] and calls[0][1]["timeout"] == 120
    assert calls[0][1]["cwd"] == "/"
    assert "GH_TOKEN" not in calls[0][1]["env"]
    assert calls[0][0][-1] == "/Library/TramDeploy/a/kiem-song"
    def sai(*a, **kw):
        return SimpleNamespace(returncode=0, stdout=b'{"dat":true}', stderr=b"secret")
    monkeypatch.setattr(duong, "chay_gioi_han", sai)
    assert d.goi("deploy", "dp-1", "a" * 40, "b" * 40) is None


def test_writable_or_symlink_entrypoint_is_rejected(tmp_path):
    p = tmp_path / "x"
    p.write_text("echo x")
    with pytest.raises(ValueError):
        duong.kiem_tep(p)
    q = tmp_path / "q"
    q.symlink_to(p)
    with pytest.raises(ValueError):
        duong.kiem_tep(q)
```

#### Mã — chỉ áp sau RED, rồi chạy lại lệnh trên

#### Create `tram/deploy/duong.py` — toàn bộ file

```python
"""Ba entrypoint do Đại ca cấp, root giữ; mã dự án chỉ chạy dưới principal riêng."""
import json
import os
import pwd
import re
import shlex
import stat
import subprocess
from pathlib import Path

from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import LoiThuHoi, kill_cuc_bo

HAN = {"chuan_bi": 120, "deploy": 900, "kiem_song": 120, "lui": 900,
       "kiem_song_sau_lui": 120, "doi_soat": 120}
TRUONG = {"v", "du_an", "ma", "buoc", "commit", "truoc", "dat", "da_dung",
          "san_sang", "ban_truoc", "ban_thuc", "artifact"}


def tach_lenh(ten, cd):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,60}", ten):
        return None
    ra = {}
    for khoa, tep in (("deploy", "deploy"), ("kiem_song", "kiem-song"), ("lui", "lui")):
        try:
            a = shlex.split(getattr(cd, f"lenh_{khoa}"))
        except ValueError:
            return None
        if a != ["/usr/bin/sudo", "-n", "-u", f"tram-dp-{ten}", "--", f"/Library/TramDeploy/{ten}/{tep}"]:
            return None
        ra[khoa] = a
    return ra


def kiem_tep(p):
    p = Path(p)
    for q in (p, *p.parents):
        s = q.lstat()
        if stat.S_ISLNK(s.st_mode) or s.st_uid != 0 or s.st_mode & 0o022:
            raise ValueError("duong-deploy-chua-duoc-bao-ve")
    if not p.is_file() or not os.access(p, os.X_OK):
        raise ValueError("entrypoint-chua-hop-le")


class DuongDeploy:
    def __init__(self, ten, cd):
        self.ten, self.lenh = ten, tach_lenh(ten, cd)
        if self.lenh is None:
            raise ValueError("can-duong-deploy-rieng")
        p = pwd.getpwnam(f"tram-dp-{ten}")
        if p.pw_uid in (0, os.getuid()) or p.pw_uid < 500:
            raise ValueError("principal-deploy-khong-hop-le")
        self.env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "HOME": p.pw_dir, "LANG": "C.UTF-8"}
        for a in self.lenh.values():
            kiem_tep(a[-1])

    def goi(self, buoc, ma, commit, truoc):
        a = self.lenh[buoc if buoc in ("deploy", "lui") else "kiem_song"]
        d = dict(v=1, du_an=self.ten, ma=ma, buoc=buoc, commit=commit, truoc=truoc)
        try:
            kiem_tep(a[-1])
            r = chay_gioi_han(a, kill=kill_cuc_bo, timeout=HAN[buoc], input=json.dumps(d).encode(),
                              capture_output=True, cwd="/", env=self.env)
            if r.returncode != 0 or len(r.stdout) > 4096:
                return None
            k = json.loads(r.stdout)
            if (set(k) != TRUONG or any(k.get(x) != v for x, v in d.items())
                    or any(type(k.get(x)) is not bool for x in ("dat", "da_dung", "san_sang"))
                    or not re.fullmatch(r"[0-9a-f]{40}", str(k.get("ban_truoc")))):
                return None
            if k["dat"]:
                dich = k["ban_truoc"] if buoc == "chuan_bi" else commit
                if k["ban_thuc"] != dich or k["artifact"] != dich:
                    k["dat"] = False
            return k
        except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError, LoiThuHoi):
            return None
```

**GREEN:** tất cả test của task và hồi quy liên quan đạt, 0 dòng chặn mới; lỗi host không được tính là GREEN.

### Task 4: Chọn M, kiểm Uq và hàng rào L..M

**RED cần chứng minh:** Uq nhận M, không phải H; mã lượt phải khác dự án; schema/đường cấm L..M không được miễn.

```bash
tests/chan_host/chay.sh -q tests/test_tm20_ban.py
```

#### Test/fixture — áp trước, chạy RED

#### Create `tests/test_tm20_ban.py` — toàn bộ file

```python
"""Chọn M từ pr.da_merge, kiểm M riêng với H; dữ liệu/Git/Uq giả."""
from types import SimpleNamespace as NS
from tram.deploy import ban
from tram.phieu.kho import KhoPhieu


def test_chon_merge_moi_nhat_khong_chon_head(monkeypatch):
    ds = [NS(id=1, loai="pr.da_merge", du_lieu={"merge_commit": "m1"}),
          NS(id=2, loai="pr.da_merge", du_lieu={"merge_commit": "m2"})]
    monkeypatch.setattr(ban, "merge_chua_deploy", lambda s: s)
    monkeypatch.setattr(ban, "la_to_tien", lambda kg, a, b: a == b or (a, b) in {
        ("m1", "origin/main"), ("m2", "origin/main"), ("m1", "m2")})
    assert ban.chon_ban(None, ds, "main") == "m2"
    assert ban.chon_ban(None, list(reversed(ds)), "main") == "m2"


def test_uq_receives_merge_sha_not_pr_head(tmp_path, monkeypatch):
    kho = KhoPhieu(tmp_path / "sk.db")
    da = NS(ten="a", nhanh_chinh="main", lenh_cho_phep=("test",),
            giao=NS(lenh_kiem_mac_dinh=("test",)))
    calls = []
    monkeypatch.setattr(ban, "cong_mo", lambda: True)
    def kiem(kg, da, **kw):
        calls.append(kw)
        return NS(dat=False)
    monkeypatch.setattr(ban, "kiem_tu_xa", kiem)
    try:
        assert not ban.kiem_ban(kho.db, None, da, "b" * 40, "7")
        assert calls[0]["commit"] == "b" * 40
        assert calls[0]["chay_lenh"] is True
        assert calls[0]["lenh_kiem"] == ["test"]
    finally:
        kho.close()


def test_direct_commit_requires_manual_scope(monkeypatch):
    monkeypatch.setattr(ban, "la_to_tien", lambda *a: True)
    monkeypatch.setattr(ban, "_git", lambda *a: NS(stdout=b"m1\ndirect\nm2\n"))
    ds = [NS(loai="pr.da_merge", du_lieu={"merge_commit": "m1"}),
          NS(loai="pr.da_merge", du_lieu={"merge_commit": "m2"})]
    assert not ban.pham_vi_du(None, ds, "old", "m2")


def test_manual_scope_never_waives_schema_or_protected_paths(monkeypatch):
    da = NS(giao=NS(duong_dan_cam=('deploy/**',)), hang_rao={'schema': NS(duong_dan=('db/**',))})
    for path in ('db/migrate.sql', 'deploy/entry.sh', 'src/safe.py'):
        monkeypatch.setattr(ban, 'tep_doi', lambda *a, p=path: [p], raising=False)
        assert ban.ban_an_toan(None, da, 'L', 'M') is (path == 'src/safe.py')
```

#### Mã — chỉ áp sau RED, rồi chạy lại lệnh trên

#### Create `tram/deploy/ban.py` — toàn bộ file

```python
"""Chỉ chọn merge đã xác minh; kiểm M qua cùng Uq, không suy từ QC của H."""
import fnmatch
import hashlib
import json

from tram.deploy.git import _git, la_to_tien
from tram.deploy.ghi import ghi
from tram.deploy.trang_thai import merge_chua_deploy
from tram.quan_kiem.client import kiem_tu_xa
from tram.tu_dong.cong_kiem import cong_mo
from tram.kiem.diff import tep_doi
from tram.kiem.duong_dan_cam import duong_dan_cham_cam


def chon_ban(kg, ds, nhanh):
    chon = None
    for s in merge_chua_deploy(ds):
        c = s.du_lieu.get("merge_commit")
        if not c or not la_to_tien(kg, c, f"origin/{nhanh}"):
            continue
        if chon is None or la_to_tien(kg, chon, c):
            chon = c
        elif not la_to_tien(kg, c, chon):
            return None
    return chon


def pham_vi_du(kg, ds, truoc, commit):
    if not la_to_tien(kg, truoc, commit):
        return False
    ds_sha = _git(kg, "rev-list", "--first-parent", f"{truoc}..{commit}").stdout.decode().splitlines()
    da = {s.du_lieu.get("merge_commit") for s in ds if s.loai == "pr.da_merge"}
    return bool(ds_sha) and set(ds_sha) <= da


def kiem_ban(db, kg, da, commit, pb):
    if not cong_mo():
        return False
    lenh = list(da.giao.lenh_kiem_mac_dinh)
    if not lenh:
        return False
    policy = json.dumps([da.ten, commit, pb, lenh, list(da.lenh_cho_phep)], sort_keys=True)
    ma = "dpkiem-" + hashlib.sha256(policy.encode()).hexdigest()[:24]
    try:
        r = kiem_tu_xa(kg, da, giao_id=ma, luot=1, commit=commit, lenh_kiem=lenh,
                       lenh_cho_phep=list(da.lenh_cho_phep), chay_lenh=True)
        dat = r.dat is True
    except (OSError, ValueError):
        dat = False
    ghi(db, da.ten, "deploy.kiem", {"ma_thao_tac": ma, "commit": commit, "phien_ban": pb,
                                    "dat": dat, "nguon_kiem": "uq"})
    return dat


def ban_an_toan(kg, da, truoc, commit):
    # M đã vào main: diff origin/main..M thường rỗng; phải kiểm từ bản thực đang chạy L.
    tep = tep_doi(kg, truoc, commit)
    schema = da.hang_rao.get("schema")
    return not duong_dan_cham_cam(tep, them=da.giao.duong_dan_cam) and not (
        schema and any(fnmatch.fnmatch(p, m) for p in tep for m in schema.duong_dan))
```

**GREEN:** tất cả test của task và hồi quy liên quan đạt, 0 dòng chặn mới; lỗi host không được tính là GREEN.

### Task 5: Chuỗi deploy, mốc bật, rollback và phục hồi crash

**RED cần chứng minh:** Bật sau merge dù chưa có tick phải chờ; trigger cũ không kéo merge tay; rollback phải ghi ý định trước gọi.

```bash
tests/chan_host/chay.sh -q tests/test_tm20_chuoi.py tests/test_tm20_review.py tests/test_deploy_vong.py tests/test_deploy_race.py tests/test_deploy_cong_tac_v2.py tests/test_deploy_chuoi.py tests/test_deploy_trang_thai.py
```

#### Test/fixture — áp trước, chạy RED

#### Create `tests/test_tm20_chuoi.py` — toàn bộ file

```python
"""Điều phối dùng kho SQLite tạm và biên Uq/deploy giả; không tác động host."""
from dataclasses import replace
from types import SimpleNamespace as NS
import pytest
from tram.deploy import chay
from tram.deploy.ghi import ghi, ket_thuc
from tram.deploy.trang_thai import doc_su_kien
from tram.deploy.doi_soat import chua_doi_soat
from tram.phieu.kho import KhoPhieu
from tram.tu_dong.luu import doi_cai_dat, doc_trang_thai
from tram.tu_dong.cai_dat import CaiDatTuDong

M, L = "a" * 40, "b" * 40


@pytest.fixture
def bo(tmp_path, monkeypatch):
    k = KhoPhieu(tmp_path / "sk.db")
    da = NS(ten="a", nhanh_chinh="main")
    doi_cai_dat(k.db, "a", lambda c: CaiDatTuDong(tu_deploy=True, lenh_deploy="d", lenh_kiem_song="k",
                                                lenh_lui="l"), tac_nhan="dai-ca/dashboard")
    ghi(k.db, "a", "tu_merge.bat_dau", {"commit": "h", "loai": "code"})
    ghi(k.db, "a", "pr.da_merge", {"commit": "h", "merge_commit": M})
    calls, ans = [], {}
    class Duong:
        def __init__(self, *a):
            pass
        def goi(self, buoc, ma, c, truoc):
            calls.append((buoc, c, truoc))
            if buoc in ans:
                r = ans[buoc]
                return r() if callable(r) else r
            return dict(dat=True, da_dung=True, san_sang=True, ban_truoc=L)
    monkeypatch.setattr(chay, "DuongDeploy", Duong)
    monkeypatch.setattr(chay, "cong_mo", lambda: True)
    monkeypatch.setattr(chay, "kiem_ban", lambda *a: True)
    monkeypatch.setattr(chay, "pham_vi_du", lambda *a: True)
    monkeypatch.setattr(chay, "ban_an_toan", lambda *a: True)
    monkeypatch.setattr(chay, "phu", lambda *a: [2])
    monkeypatch.setattr(chay, "chon_ban", lambda *a: M)
    monkeypatch.setattr(chay, "tu_merge_cho_deploy", lambda *a, **kw: NS(du_lieu={"merge_commit": M}))
    run = lambda: chay.chuoi(k.db, None, da, M, "tu_dong", "sk-2", lambda ten: True)
    yield NS(k=k, da=da, calls=calls, ans=ans, run=run)
    k.close()


def test_success_pins_versions_and_idempotent(bo):
    assert bo.run() == "deploy_dat"
    assert [x[0] for x in bo.calls] == ["chuan_bi", "deploy", "kiem_song"]
    assert bo.calls[-1][1] == M
    assert bo.run() == "deploy_da_co"
    assert len(bo.calls) == 3


def test_known_failure_rolls_back_once_and_checks_old_version(bo):
    bo.ans["deploy"] = dict(dat=False, da_dung=True)
    assert bo.run() == "deploy_da_lui"
    assert [x[0] for x in bo.calls] == ["chuan_bi", "deploy", "lui", "kiem_song_sau_lui"]
    assert bo.calls[-1][1] == L


@pytest.mark.parametrize("step", ["deploy", "kiem_song", "lui", "kiem_song_sau_lui"])
def test_unknown_never_runs_next_step(bo, step):
    if step in ("lui", "kiem_song_sau_lui"):
        bo.ans["deploy"] = dict(dat=False, da_dung=True)
    bo.ans[step] = None
    assert bo.run() == "deploy_khong_ro"
    assert bo.calls[-1][0] == step
    assert chua_doi_soat(doc_su_kien(bo.k.db, "a"))
    assert doc_trang_thai(bo.k.db, "a").tam_dung_du_an is not None


def test_no_baseline_or_failed_uq_never_deploys(bo, monkeypatch):
    bo.ans["chuan_bi"] = dict(dat=True, da_dung=True, san_sang=False, ban_truoc=L)
    assert bo.run() == "deploy_cho_ban_nen"
    bo.ans.clear()
    monkeypatch.setattr(chay, "kiem_ban", lambda *a: False)
    assert bo.run() == "deploy_cho_kiem"
    assert all(x[0] == "chuan_bi" for x in bo.calls)


def test_changed_settings_after_uq_do_not_start(bo, monkeypatch):
    def kiem(*args):
        doi_cai_dat(bo.k.db, "a", lambda c: replace(c, tu_deploy=False), tac_nhan="dai-ca/dashboard")
        return True
    monkeypatch.setattr(chay, "kiem_ban", kiem)
    assert bo.run() == "deploy_hoan"
    assert all(x[0] == "chuan_bi" for x in bo.calls)


def test_finish_is_idempotent(bo):
    assert bo.run() == "deploy_dat"
    ds = doc_su_kien(bo.k.db, "a")
    m = next(s.du_lieu["ma_thao_tac"] for s in ds if s.loai == "deploy.bat_dau")
    ket_thuc(bo.k.db, "a", m, "dat")
    assert len([s for s in doc_su_kien(bo.k.db, "a") if s.loai == "deploy.xong"]) == 1
```

#### Modify `tests/test_deploy_vong.py` — bản vá

```diff
--- a/tests/test_deploy_vong.py
+++ b/tests/test_deploy_vong.py
@@ -1,401 +1,154 @@
-"""TM-3 (tu-deploy, dieu-khien-tu-dong; design D-6, D-7, D-9; D74, D75, D96, D97, D100, D115, D116, D123, D124;
-Codex Q4–Q8): pha deploy của một dự án trên kho kiểm giả (repo bare cục bộ) + kho sự kiện tạm. Ba lệnh là script `sh`
-GIẢ trong thư mục tạm, ghi "bản khách đang dùng" vào một file tạm — không lệnh deploy thật nào, không mạng."""
-import json
-import os
-import shlex
-import shutil
-import stat
-import sys
-import time
-from pathlib import Path
-from types import SimpleNamespace
-
+"""TM20 thay giả lập shell dưới trạm bằng đường dự án; giữ Git/SQLite cục bộ."""
+from dataclasses import replace
+from types import SimpleNamespace as NS
+import subprocess
 import pytest
-
 from kho_kiem_gia import dung_kho
-from tram.chu import estop
-from tram.deploy.lenh import HAN
+from tram.deploy import chay, git as git_deploy
 from tram.deploy.vong import buoc_deploy
-from tram.duong_dan import tram_home
+from tram.deploy.ghi import ghi
+from tram.deploy.trang_thai import doc_su_kien
 from tram.giao_viec.git_kiem import fetch
 from tram.phieu.kho import KhoPhieu
-from tram.su_kien.ghi_trong import ghi_trong_giao_dich
 from tram.tu_dong.cai_dat import CaiDatTuDong
-from tram.tu_dong.luu import DU_AN_TRAM, doc_trang_thai, doi_cai_dat, ghi_tam_dung, giao_dich
+from tram.tu_dong.luu import doi_cai_dat, doc_trang_thai, ghi_tam_dung
+from tram.chu import estop
 
-LOI_CHUOI = {"deploy": 'echo "$TRAM_DEPLOY_COMMIT" > "{g}/ban"; pwd -P > "{g}/pwd"',
-             "kiem_song": "exit 0", "lui": 'echo "$TRAM_DEPLOY_COMMIT_TRUOC" > "{g}/ban"'}
-CO_HONG = {"deploy": "deploy-hong", "kiem_song": "song-hong", "lui": "lui-hong"}
 DAI_CA = "dai-ca/dashboard"
 
 
 class Tram:
-    def __init__(self, tmp_path: Path, *, tu_deploy: bool = False, du_lenh: bool = True):
-        self.g, self.k, self.bg = tmp_path, dung_kho(tmp_path), True
+    def __init__(self, tmp_path, monkeypatch, *, tu_deploy=False):
+        self.k, self.n = dung_kho(tmp_path), 0
         self.kho = KhoPhieu(tmp_path / "su-kien.db")
-        self.da = SimpleNamespace(ten="repo-nhap", nhanh_chinh="main")
-        self.bo = SimpleNamespace(kho_git=lambda d: self.k.kho)
-        lenh = {}
-        for ten, than in LOI_CHUOI.items():
-            f = tmp_path / "tram-deploy" / f"{ten}.sh"
-            f.parent.mkdir(exist_ok=True)
-            f.write_text(f'#!/bin/sh\n[ -f "{tmp_path}/{CO_HONG[ten]}" ] && exit 3\n{than.format(g=tmp_path)}\n')
-            lenh[ten] = f"/bin/sh {shlex.quote(str(f))}"
-        cd = CaiDatTuDong(tu_merge=True, tu_deploy=tu_deploy, lenh_deploy=lenh["deploy"],
-                          lenh_kiem_song=lenh["kiem_song"], lenh_lui=lenh["lui"] if du_lenh else "")
-        doi_cai_dat(self.kho.db, "repo-nhap", lambda c: cd, tac_nhan=DAI_CA)
-        self.n = 0
+        self.da = NS(ten="repo-nhap", nhanh_chinh="main")
+        self.bo = NS(kho_git=lambda da: self.k.kho)
+        self.ban, self.calls, self.hong = self.k.main, [], set()
+        self.khi_kiem, self.khi_goi = lambda: None, lambda b: None
+        self.bg, self.uq = True, True
+        self.cd(tu_deploy=tu_deploy, lenh_deploy="d", lenh_kiem_song="k", lenh_lui="l")
+        monkeypatch.setattr(chay, "DuongDeploy", lambda *a: self)
+        monkeypatch.setattr(chay, "cong_mo", lambda: True)
+        monkeypatch.setattr(chay, "kiem_ban", lambda *a: (self.khi_kiem(), self.uq)[1])
+        monkeypatch.setattr(chay, "pham_vi_du", lambda *a: True)
+        monkeypatch.setattr(chay, "ban_an_toan", lambda *a: True)
+        monkeypatch.setattr(git_deploy, "chay_gioi_han",
+                            lambda a, *, kill, timeout, **kw: subprocess.run(a, timeout=timeout, **kw))
 
-    def ghi(self, loai: str, du_lieu: dict, *, bead: str | None = None, tac_nhan: str = "tram/giao-viec") -> None:
-        with giao_dich(self.kho.db):
-            ghi_trong_giao_dich(self.kho.db, "repo-nhap", loai, du_lieu, bead_id=bead, tac_nhan=tac_nhan,
-                                luc="2026-10-18T10:00:00Z")
+    def cd(self, **kw):
+        doi_cai_dat(self.kho.db, self.da.ten, lambda c: replace(c, **kw), tac_nhan=DAI_CA)
 
-    def merge(self, *, tu: bool = True, fetch_kho: bool = True) -> str:
-        """Một PR của trạm đã merge vào main và đã xác minh (`pr.da_merge`); `tu` = do trạm tự merge (TM-2)."""
+    def ghi(self, loai, d):
+        return ghi(self.kho.db, self.da.ten, loai, d)
+
+    def merge(self, *, tu=True):
         self.n += 1
-        b = f"rn-{self.n}"
-        sha = self.k.day("main", {f"src/f{self.n}.py": f"x = {self.n}\n"})
-        if fetch_kho:
-            fetch(self.k.kho)
+        c = self.k.day("main", {f"src/{self.n}.py": str(self.n)})
+        fetch(self.k.kho)
         if tu:
-            self.ghi("tu_merge.bat_dau", {"ma_thao_tac": f"tm-{b}", "commit": f"c-{b}", "pr": self.n, "loai": "code"},
-                     bead=b, tac_nhan="tram/tu-merge")
-        self.ghi("pr.da_merge", {"bead_id": b, "commit": f"c-{b}", "merge_commit": sha, "ma_thao_tac": f"pr-{b}"},
-                 bead=b)
-        return sha
+            self.ghi("tu_merge.bat_dau", {"commit": c, "loai": "code"})
+        self.ghi("pr.da_merge", {"commit": c, "merge_commit": c})
+        return c
 
-    def bam(self, commit: str, ma: str = "ma-dp-0001") -> None:
-        self.ghi("deploy.yeu_cau", {"ma_thao_tac": ma, "commit": commit, "nguon": "dai_ca"}, tac_nhan=DAI_CA)
+    def bam(self, c):
+        self.ghi("deploy.yeu_cau", {"ma_thao_tac": f"tay-{self.n}", "commit": c,
+                                    "phien_ban": doc_trang_thai(self.kho.db, self.da.ten).phien_ban})
 
-    def buoc(self, bat_ghi: bool | None = None) -> dict:
-        if bat_ghi is not None:
-            self.bg = bat_ghi
+    def goi(self, buoc, ma, c, truoc):
+        self.calls.append((buoc, c, truoc))
+        self.khi_goi(buoc)
+        if "khong_ro" in self.hong and buoc == "deploy":
+            return None
+        dat = buoc not in self.hong
+        if dat and buoc in ("deploy", "lui"):
+            self.ban = c
+        if buoc in ("kiem_song", "kiem_song_sau_lui"):
+            dat = dat and self.ban == c
+        return dict(dat=dat, da_dung=True, san_sang=True, ban_truoc=self.ban)
+
+    def buoc(self):
         return buoc_deploy(self.bo, self.kho, self.da, bat_ghi=lambda ten: self.bg)
 
-    def sk(self, loai: str) -> list[dict]:
-        return [json.loads(d) for (d,) in self.kho.db.execute(
-            "SELECT du_lieu FROM su_kien WHERE loai = ? ORDER BY id", (loai,))]
-
-    def ss(self) -> list[tuple]:
-        return [(x["commit"], x["so_merge"], len(x["bao_gom"])) for x in self.sk("deploy.san_sang")]
-
-    def ban(self) -> str | None:
-        f = self.g / "ban"
-        return f.read_text().strip() if f.exists() else None
-
-    def hong(self, buoc: str, co: bool = True) -> None:
-        f = self.g / CO_HONG[buoc]
-        f.touch() if co else f.unlink(missing_ok=True)
-
-
-def va(monkeypatch, ten: str, boc) -> None:
-    """Bọc hàm `ten` ở mọi module `tram.deploy.*` đang giữ tên đó — chèn việc đúng bước dù hàm nằm ở module nào."""
-    for m in [m for k, m in list(sys.modules.items()) if k.startswith("tram.deploy.") and hasattr(m, ten)]:
-        monkeypatch.setattr(m, ten, boc(getattr(m, ten)))
-
-
-def mot_lan(lam):
-    """Bọc: lần gọi ĐẦU TIÊN chạy `lam()` trước rồi mới gọi hàm thật."""
-    da = []
-
-    def boc(goc):
-        def ham(*a, **kw):
-            if not da:
-                da.append(lam())
-            return goc(*a, **kw)
-        return ham
-    return boc, da
-
-
-def song(pid: int) -> bool:
-    try:
-        os.kill(pid, 0)
-    except ProcessLookupError:
-        return False
-    return True
+    def sk(self, loai):
+        return [s.du_lieu for s in doc_su_kien(self.kho.db, self.da.ten) if s.loai == loai]
 
 
 @pytest.fixture
-def t(tmp_path):
-    tr = Tram(tmp_path)
+def t(tmp_path, monkeypatch):
+    tr = Tram(tmp_path, monkeypatch)
     yield tr
     tr.kho.close()
 
 
-def test_tu_merge_tu_deploy_tat_thi_san_sang_mot_lan(t):
-    """Scenario "Tự merge xong, tự deploy tắt": sẵn sàng deploy, không chạy lệnh nào; không báo lặp mỗi vòng."""
-    m = t.merge()
+def test_disabled_then_enabled_does_not_retroactively_deploy(t):
+    c = t.merge()
     assert t.buoc() == {"san_sang_deploy": 1}
-    (s,) = t.sk("deploy.san_sang")
-    assert (s["commit"], s["so_merge"], len(s["bao_gom"]), s["cho"]) == (m, 1, 1, ["tu_deploy_tat"]) and not t.ban()
-    assert t.buoc() == {} and len(t.sk("deploy.san_sang")) == 1
-    m2 = t.merge(tu=False)                                          # Scenario "Đại ca gộp tay" (D96)
-    assert t.buoc() == {"san_sang_deploy": 1} and t.ss()[-1] == (m2, 2, 2)
+    t.cd(tu_deploy=True)
+    assert t.buoc() == {} and not t.calls
+    t.bam(c)
+    assert t.buoc() == {"deploy_dat": 1} and t.ban == c
+    assert t.buoc() == {}
 
 
-def test_thieu_lenh_hoac_chi_quet_thu_khong_bao(tmp_path):
-    tr = Tram(tmp_path, du_lenh=False)
-    tr.merge()
-    assert tr.buoc() == {} and tr.buoc(bat_ghi=False) == {} and tr.sk("deploy.san_sang") == []
-    tr.kho.close()
+def test_manual_merge_never_triggers_auto(t):
+    t.cd(tu_deploy=True)
+    c = t.merge(tu=False)
+    assert t.buoc() == {"san_sang_deploy": 1} and not t.calls
+    t.bam(c)
+    assert t.buoc() == {"deploy_dat": 1}
 
 
-def test_tu_deploy_sau_tu_merge_dat(tmp_path):
-    """Scenario "Tự deploy sau tự merge": deploy rồi kiểm còn sống trong bản sạch; xong thì xoá bản sạch."""
-    tr = Tram(tmp_path, tu_deploy=True)
-    m = tr.merge()
-    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m
-    (bd,) = tr.sk("deploy.bat_dau")
-    assert (bd["commit"], bd["commit_truoc"], bd["nguon"]) == (m, "", "tu_dong") and bd["ma_thao_tac"].startswith("dp-")
-    assert len(bd["bao_gom"]) == 1 and "yeu_cau" not in bd
-    assert [x["buoc"] for x in tr.sk("deploy.lenh")] == ["deploy", "kiem_song"]
-    assert tr.sk("deploy.xong") == [{"ma_thao_tac": bd["ma_thao_tac"], "ket_qua": "dat", "dem_hong": 0}]
-    assert not (tram_home() / "kho-deploy" / "repo-nhap").exists() and tr.sk("deploy.san_sang") == []
-    log = tram_home() / "deploy-log" / "repo-nhap" / f"{bd['ma_thao_tac']}.log"
-    assert (tmp_path / "pwd").read_text().strip() == str((tram_home() / "kho-deploy" / "repo-nhap").resolve())
-    assert stat.S_IMODE(log.stat().st_mode) == 0o600 and log.read_text().startswith("=== deploy\n")
-    assert tr.buoc() == {}
-    tr.kho.close()
+def test_three_pending_coalesce(t):
+    t.cd(tu_deploy=True)
+    t.merge()
+    t.merge()
+    m = t.merge()
+    assert t.buoc() == {"deploy_dat": 1} and t.ban == m
+    assert len(t.sk("deploy.bat_dau")) == 1
+    assert len(t.sk("deploy.bat_dau")[0]["bao_gom"]) == 3
 
 
-def test_hong_thi_tu_lui_ve_ban_truoc_ba_lan_thi_tu_tat(tmp_path):
-    """Scenario "Lùi thành công", "Lần hỏng thứ ba": tự lùi về bản trước; hỏng 3 lần liên tiếp → tự tắt; D124: bản
-    hỏng không tự chạy lại; merge sau quay về "sẵn sàng deploy" gồm mọi bản chưa lên."""
-    tr = Tram(tmp_path, tu_deploy=True)
-    m1 = tr.merge()
-    assert tr.buoc() == {"deploy_dat": 1}
-    tr.hong("deploy")
-    for lan in (1, 2, 3):
-        tr.merge()
-        assert tr.buoc() == {"deploy_da_lui": 1} and tr.ban() == m1
-        assert tr.sk("deploy.xong")[-1]["dem_hong"] == lan and tr.sk("deploy.bat_dau")[-1]["commit_truoc"] == m1
-    assert doc_trang_thai(tr.kho.db, "repo-nhap").cai_dat.tu_deploy is False
-    assert tr.buoc() == {}                                          # bản hỏng không tự chạy lại
-    m5 = tr.merge()
-    assert tr.buoc() == {"san_sang_deploy": 1} and tr.ss()[-1] == (m5, 4, 4)
-    tr.kho.close()
+def test_pause_only_manual_can_start(t):
+    t.cd(tu_deploy=True)
+    c = t.merge()
+    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=True, tac_nhan=DAI_CA)
+    assert t.buoc() == {"san_sang_deploy": 1}
+    t.bam(c)
+    assert t.buoc() == {"deploy_dat": 1}
 
 
-def test_lui_hong_thi_tam_dung_du_an(tmp_path):
-    """Scenario "Trang chết sau lùi": tắt tự deploy, tạm dừng dự án; merge sau chỉ "sẵn sàng"."""
-    tr = Tram(tmp_path, tu_deploy=True)
-    tr.hong("kiem_song")
-    tr.merge()
-    assert tr.buoc() == {"deploy_lui_hong": 1}
-    assert [x["buoc"] for x in tr.sk("deploy.lenh")] == ["deploy", "kiem_song", "lui", "kiem_song_sau_lui"]
-    tt = doc_trang_thai(tr.kho.db, "repo-nhap")
-    assert tt.cai_dat.tu_deploy is False and tt.tam_dung_du_an.ly_do == "lui-hong"
-    tr.merge()
-    assert tr.buoc() == {"san_sang_deploy": 1} and len(tr.sk("deploy.bat_dau")) == 1
-    tr.kho.close()
+def test_three_known_failures_disable_only_deploy(t):
+    t.cd(tu_deploy=True)
+    old = t.ban
+    t.hong.add("deploy")
+    for n in range(1, 4):
+        t.merge()
+        assert t.buoc() == {"deploy_da_lui": 1}
+        assert t.sk("deploy.xong")[-1]["dem_hong"] == n and t.ban == old
+    assert not doc_trang_thai(t.kho.db, t.da.ten).cai_dat.tu_deploy
 
 
-def test_tam_dung_chan_tu_deploy_nhung_deploy_tay_duoc(tmp_path):
-    """Scenario "Deploy tay khi dự án tạm dừng" (D97 luật 3); "Tạm dừng rồi tiếp tục"."""
-    tr = Tram(tmp_path, tu_deploy=True)
-    ghi_tam_dung(tr.kho.db, "repo-nhap", tam_dung=True, tac_nhan=DAI_CA)
-    m = tr.merge()
-    assert tr.buoc() == {"san_sang_deploy": 1} and tr.ban() is None
-    tr.bam(m)
-    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m and tr.sk("deploy.bat_dau")[0]["nguon"] == "dai_ca"
-    assert tr.sk("deploy.bat_dau")[0]["yeu_cau"] == "ma-dp-0001"
-    ghi_tam_dung(tr.kho.db, "repo-nhap", tam_dung=False, tac_nhan=DAI_CA)
-    m2 = tr.merge()
-    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m2       # sau Tiếp tục: tự deploy chạy lại
-    tr.kho.close()
+def test_unknown_blocks_next_tick_even_after_continue(t):
+    t.cd(tu_deploy=True)
+    t.merge()
+    t.hong.add("khong_ro")
+    assert t.buoc() == {"deploy_khong_ro": 1}
+    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=False, tac_nhan=DAI_CA)
+    count = len(t.calls)
+    t.buoc()
+    assert len(t.calls) == count and t.sk("deploy.xong")[-1]["dem_hong"] == 0
 
 
-def test_tam_dung_roi_tiep_tuc_van_tu_deploy_ban_tu_merge(tmp_path):
-    """Codex Q8: tự merge xong lúc dự án đang TẠM DỪNG → hàng "sẵn sàng"; Tiếp tục → tự deploy bản đó (khác D123)."""
-    tr = Tram(tmp_path, tu_deploy=True)
-    ghi_tam_dung(tr.kho.db, "repo-nhap", tam_dung=True, tac_nhan=DAI_CA)
-    m = tr.merge()
-    assert tr.buoc() == {"san_sang_deploy": 1} and tr.sk("deploy.san_sang")[0]["cho"] == ["tam_dung_du_an"]
-    ghi_tam_dung(tr.kho.db, "repo-nhap", tam_dung=False, tac_nhan=DAI_CA)
-    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m and tr.sk("deploy.bat_dau")[0]["nguon"] == "tu_dong"
-    tr.kho.close()
-
-
-def test_san_sang_truoc_khi_bat_tu_deploy_thi_cho_bam(t):
-    """D123: bản đã "sẵn sàng" TRƯỚC khi Đại ca bật tự deploy → không tự deploy, chờ bấm; tự merge SAU đó mới tự
-    deploy (đem đỉnh nhánh chính, gồm cả bản đang chờ)."""
+def test_estop_mid_chain_keeps_safe_finish(t):
+    t.cd(tu_deploy=True)
     t.merge()
-    assert t.buoc() == {"san_sang_deploy": 1}
-    doi_cai_dat(t.kho.db, "repo-nhap", lambda c: CaiDatTuDong(**{**c.__dict__, "tu_deploy": True}), tac_nhan=DAI_CA)
-    assert t.buoc() == {} and t.ban() is None
-    m2 = t.merge()
-    assert t.buoc() == {"deploy_dat": 1} and t.ban() == m2 and len(t.sk("deploy.bat_dau")[0]["bao_gom"]) == 2
-
-
-def test_estop_huy_nut_deploy_dang_cho_khong_chay(t):
-    """INV-004: estop bật → không chạy gì; nút Deploy bấm trước đó không tự chạy sau khi tắt estop."""
-    m = t.merge()
-    t.bam(m, "ma-dp-0002")
-    estop.bat("thử")
-    assert t.buoc() == {"deploy_huy": 1} and t.sk("deploy.huy") == [
-        {"ma_thao_tac": "ma-dp-0002", "commit": m, "ly_do": "estop"}]
-    estop.tat()
-    assert t.buoc() == {"san_sang_deploy": 1} and t.ban() is None
-
-
-@pytest.mark.parametrize("bat_ghi, commit, ly_do", [(False, None, "bat_ghi"), (True, "f" * 40, "commit_khong_co")])
-def test_nut_deploy_bi_huy_khi_vong_xet_lai(t, bat_ghi, commit, ly_do):
-    """D116: `bat_ghi: false` không Deploy tay — vòng deploy xét lại khoá chung ngay trước chuỗi."""
-    m = t.merge()
-    t.bam(commit or m, "ma-dp-0003")
-    assert t.buoc(bat_ghi=bat_ghi) == {"deploy_huy": 1} and t.sk("deploy.huy")[0]["ly_do"] == ly_do
-    assert t.ban() is None and t.sk("deploy.bat_dau") == []
-
-
-def test_nut_deploy_ban_cu_bi_huy_truoc_khoi_chay(t):
-    """Codex Q7: Đại ca bấm Deploy cho m5, rồi m6 merge trước khi vòng deploy nhận → KHÔNG chạy m5 lặng lẽ: huỷ
-    `ban_moi_hon` (lịch sử "Deploy bị huỷ"), vòng sau báo "sẵn sàng" bản m6 gồm cả m5."""
-    m5 = t.merge()
-    assert t.buoc() == {"san_sang_deploy": 1}
-    t.bam(m5, "ma-dp-0004")
-    m6 = t.merge(tu=False)
-    assert t.buoc() == {"deploy_huy": 1} and t.ban() is None and t.sk("deploy.bat_dau") == []
-    assert t.sk("deploy.huy") == [{"ma_thao_tac": "ma-dp-0004", "commit": m5, "ly_do": "ban_moi_hon"}]
-    assert t.buoc() == {"san_sang_deploy": 1} and t.ss()[-1] == (m6, 2, 2)
-
-
-@pytest.mark.parametrize("doi, tay, ly_do", [("tam_dung", False, None), ("tam_dung_tram", False, None),
-                                             ("tu_deploy_tat", False, None), ("estop", True, "estop"),
-                                             ("bat_ghi", True, "bat_ghi")])
-def test_cua_tuoi_doc_lai_khoa_ngay_truoc_lenh_dau(tmp_path, monkeypatch, doi, tay, ly_do):
-    """Codex Q4: Đại ca đổi khoá TRONG LÚC trạm dựng bản sạch → chuỗi KHÔNG bắt đầu, không lệnh nào chạy; nút Deploy
-    bị huỷ kèm lý do; tự deploy hoãn, kích còn nguyên — mở khoá lại thì vòng sau chạy (D97: đã bắt đầu mới làm nốt)."""
-    tr = Tram(tmp_path, tu_deploy=True)
-    db = tr.kho.db
-
-    def tu_deploy(bat: bool):
-        return lambda: doi_cai_dat(db, "repo-nhap", lambda c: CaiDatTuDong(**{**c.__dict__, "tu_deploy": bat}),
-                                   tac_nhan=DAI_CA)
-    doi_khoa = {"tam_dung": (lambda: ghi_tam_dung(db, "repo-nhap", tam_dung=True, tac_nhan=DAI_CA),
-                             lambda: ghi_tam_dung(db, "repo-nhap", tam_dung=False, tac_nhan=DAI_CA)),
-                "tam_dung_tram": (lambda: ghi_tam_dung(db, DU_AN_TRAM, tam_dung=True, tac_nhan=DAI_CA),
-                                  lambda: ghi_tam_dung(db, DU_AN_TRAM, tam_dung=False, tac_nhan=DAI_CA)),
-                "tu_deploy_tat": (tu_deploy(False), tu_deploy(True)),
-                "estop": (lambda: estop.bat("thử"), estop.tat),
-                "bat_ghi": (lambda: setattr(tr, "bg", False), lambda: setattr(tr, "bg", True))}[doi]
-    m = tr.merge()
-    if tay:
-        tr.bam(m)
-    boc, da = mot_lan(doi_khoa[0])
-    va(monkeypatch, "tao_worktree", boc)
-    kq = tr.buoc()
-    assert da and tr.ban() is None and tr.sk("deploy.bat_dau") == [] and tr.sk("deploy.lenh") == []
-    assert kq == ({"deploy_huy": 1} if tay else {"deploy_hoan": 1})
-    assert [x["ly_do"] for x in tr.sk("deploy.huy")] == ([ly_do] if tay else [])
-    doi_khoa[1]()
-    if not tay:
-        assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m
-    tr.kho.close()
-
-
-def test_merge_ghi_trong_luc_tao_worktree_khong_bi_coi_la_da_deploy(tmp_path, monkeypatch):
-    """Codex Q6: trong lúc dựng bản sạch cho m5, m6 được merge và ghi `pr.da_merge` (kho kiểm chưa fetch) → chuỗi
-    m5 bị hoãn vì remote đã đổi; lượt sau deploy m6 gồm cả hai merge, không mất trigger m6."""
-    tr = Tram(tmp_path, tu_deploy=True)
-    m5 = tr.merge()
-    boc, moi = mot_lan(lambda: tr.merge(fetch_kho=False))
-    va(monkeypatch, "tao_worktree", boc)
-    assert tr.buoc() == {"deploy_hoan": 1} and tr.ban() is None
-    assert tr.sk("deploy.bat_dau") == []
-    fetch(tr.k.kho)
-    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == moi[0]
-    assert [len(x["bao_gom"]) for x in tr.sk("deploy.bat_dau")] == [2]
-    tr.kho.close()
-
-
-def test_merge_va_fetch_trong_luc_tao_worktree_thi_hoan_deploy_ban_moi_nhat(tmp_path, monkeypatch):
-    """D97 luật 5 + Codex Q6: đỉnh nhánh chính đổi trong lúc chuẩn bị → không chạy bản đã cũ; lượt sau deploy MỘT lần
-    bản mới nhất, gồm cả m5."""
-    tr = Tram(tmp_path, tu_deploy=True)
-    tr.merge()
-    boc, moi = mot_lan(tr.merge)
-    va(monkeypatch, "tao_worktree", boc)
-    assert tr.buoc() == {"deploy_hoan": 1} and tr.ban() is None and tr.sk("deploy.bat_dau") == []
-    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == moi[0] and len(tr.sk("deploy.bat_dau")[0]["bao_gom"]) == 2
-    tr.kho.close()
-
-
-@pytest.mark.parametrize("treo, sau_chuoi", [("worktree add", False), ("rev-parse", False), ("merge-base", False),
-                                             ("worktree remove", True)])
-def test_git_chuan_bi_hay_don_treo_thi_dung_trong_han(tmp_path, monkeypatch, treo, sau_chuoi):
-    """Codex Q5: một lời gọi git chuẩn bị/dọn treo → vòng deploy kết thúc trong hạn `HAN["git"]`, tiến trình git bị
-    thu hồi, có trạng thái: treo trước `bat_dau` → chưa ghi gì, đếm `deploy_chuan_bi_loi`; treo lúc dọn sau chuỗi →
-    kết quả chuỗi đã ghi giữ nguyên."""
-    monkeypatch.setitem(HAN, "git", 2)
-    tr = Tram(tmp_path, tu_deploy=True)
-    m = tr.merge()
-    bin_, pid, co = tmp_path / "bin-treo", tmp_path / "git-treo.pid", tmp_path / "git-treo.co"
-    bin_.mkdir()
-    (bin_ / "git").write_text(f'#!/bin/sh\ncase "$*" in *"{treo}"*) [ -f "{co}" ] && echo $$ > "{pid}" &&'
-                              f' exec /bin/sleep 20;; esac\nexec {shlex.quote(shutil.which("git"))} "$@"\n')
-    (bin_ / "git").chmod(0o755)
-    monkeypatch.setenv("PATH", f"{bin_}:{os.environ['PATH']}")
-    if sau_chuoi:
-        va(monkeypatch, "chay_buoc", lambda goc: lambda *a, **kw: (co.touch(), goc(*a, **kw))[1])
-    else:
-        co.touch()
-    bat_dau = time.monotonic()
-    kq = tr.buoc()
-    assert time.monotonic() - bat_dau < 15 and pid.exists()
-    het = time.monotonic() + 5
-    while song(int(pid.read_text())) and time.monotonic() < het:
-        time.sleep(0.1)
-    assert not song(int(pid.read_text()))
-    if sau_chuoi:
-        assert kq == {"deploy_dat": 1} and tr.ban() == m and tr.sk("deploy.xong")[0]["ket_qua"] == "dat"
-    else:
-        assert kq == {"deploy_chuan_bi_loi": 1} and tr.sk("deploy.bat_dau") == [] and tr.ban() is None
-    tr.kho.close()
-
-
-def test_mat_dien_giua_deploy_khong_ro_khong_chay_lai(tmp_path):
-    """Scenario "Mất điện giữa deploy" + D115: ghi "không rõ", tạm dừng cả dự án, không lệnh nào chạy lại."""
-    tr = Tram(tmp_path, tu_deploy=True)
-    m = tr.merge()
-    (merge_id,) = tr.kho.db.execute("SELECT id FROM su_kien WHERE loai = 'pr.da_merge'").fetchone()
-    tr.ghi("deploy.bat_dau", {"ma_thao_tac": "dp-cu", "commit": m, "commit_truoc": "", "nguon": "tu_dong",
-                              "bao_gom": [merge_id]}, tac_nhan="tram/tu-deploy")
-    assert tr.buoc() == {"deploy_khong_ro": 1} and tr.ban() is None
-    assert tr.sk("deploy.xong") == [{"ma_thao_tac": "dp-cu", "ket_qua": "khong_ro", "dem_hong": 0}]
-    assert doc_trang_thai(tr.kho.db, "repo-nhap").tam_dung_du_an.ly_do == "khong-ro"
-    assert tr.buoc() == {} and tr.ban() is None and len(tr.sk("deploy.bat_dau")) == 1
-    tr.kho.close()
-
-
-def test_merge_moi_trong_luc_deploy_cho_luot_sau(tmp_path, monkeypatch):
-    """Scenario "Merge mới trong lúc đang deploy": chuỗi đang chạy làm nốt; bản mới deploy ở lượt sau."""
-    tr = Tram(tmp_path, tu_deploy=True)
-    m1 = tr.merge()
-    boc, moi = mot_lan(tr.merge)
-    va(monkeypatch, "chay_buoc", boc)
-    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == m1
-    assert tr.buoc() == {"deploy_dat": 1} and tr.ban() == moi[0]
-    assert [x["commit_truoc"] for x in tr.sk("deploy.bat_dau")] == ["", m1]
-    tr.kho.close()
-
-
-def test_lenh_treo_qua_han_thi_lui(tmp_path, monkeypatch):
-    """Scenario "Lệnh deploy treo" (hạn rút ngắn): dừng lệnh, tính hỏng, chuyển sang lùi."""
-    monkeypatch.setitem(HAN, "deploy", 1)
-    tr = Tram(tmp_path, tu_deploy=True)
-    f = tmp_path / "tram-deploy" / "deploy.sh"
-    f.write_text("#!/bin/sh\n/bin/sleep 30\n")
-    tr.merge()
-    assert tr.buoc() == {"deploy_da_lui": 1}
-    d = tr.sk("deploy.lenh")[0]
-    assert (d["buoc"], d["het_gio"], d["ma_thoat"] != 0, d["giay"] < 15) == ("deploy", True, True, True)
-    assert [x["buoc"] for x in tr.sk("deploy.lenh")] == ["deploy", "lui", "kiem_song_sau_lui"]
-    tr.kho.close()
-
-
-def test_khong_co_kho_kiem_thi_khong_lam_gi(t):
-    t.merge()
-    t.bo.kho_git = lambda d: None
-    assert t.buoc() == {} and t.sk("deploy.san_sang") == []
+    t.hong.add("deploy")
+    t.khi_goi = lambda b: estop.bat("test") if b == "deploy" else None
+    try:
+        assert t.buoc() == {"deploy_da_lui": 1}
+        t.merge()
+        before = len(t.calls)
+        t.buoc()
+        assert len(t.calls) == before
+    finally:
+        estop.tat()
```

#### Modify `tests/test_deploy_race.py` — bản vá

```diff
--- a/tests/test_deploy_race.py
+++ b/tests/test_deploy_race.py
@@ -1,27 +1,143 @@
-"""Q4/Q6/Q8: kiểm điều phối bằng biên git và runner GIẢ; không chứng minh thu hồi OS (G8 riêng)."""
-import shlex
-import subprocess
-from pathlib import Path
-
+"""Cửa tươi chuyển từ worktree sang sau Uq; không còn kiểm HEAD để chọn mã."""
 import pytest
-
-from test_deploy_vong import (
-    test_cua_tuoi_doc_lai_khoa_ngay_truoc_lenh_dau,
-    test_merge_ghi_trong_luc_tao_worktree_khong_bi_coi_la_da_deploy,
-    test_merge_va_fetch_trong_luc_tao_worktree_thi_hoan_deploy_ban_moi_nhat,
-    test_tam_dung_roi_tiep_tuc_van_tu_deploy_ban_tu_merge,
-)
-from tram.deploy.lenh import KetQuaBuoc
+from test_deploy_vong import t
+from tram.deploy import chay
+from tram.chu import estop
 
 
-@pytest.fixture(autouse=True)
-def bien_gia(monkeypatch):
-    def git(argv, *, kill, timeout, **kw):
-        return subprocess.run(argv, timeout=timeout, **kw)
-    def lenh(buoc, lenh, *, cwd, env, log):
-        if buoc == "deploy":
-            goc = Path(shlex.split(lenh)[1]).parent.parent
-            (goc / "ban").write_text(env["TRAM_DEPLOY_COMMIT"])
-        return KetQuaBuoc(buoc, 0, 0, False, "sha256:gia")
-    monkeypatch.setattr("tram.deploy.git.chay_gioi_han", git)
-    monkeypatch.setattr("tram.deploy.chay.chay_buoc", lenh)
+@pytest.mark.parametrize("doi", ["tat", "bat_ghi", "estop", "lenh"])
+def test_change_during_uq_stops_start(t, doi):
+    t.cd(tu_deploy=True)
+    t.merge()
+    def change():
+        if doi == "tat":
+            t.cd(tu_deploy=False)
+        if doi == "bat_ghi":
+            t.bg = False
+        if doi == "estop":
+            estop.bat("test")
+        if doi == "lenh":
+            t.cd(lenh_deploy="d2")
+    t.khi_kiem = change
+    try:
+        assert t.buoc() == {"deploy_hoan": 1}
+        assert not t.sk("deploy.bat_dau")
+    finally:
+        estop.tat()
+
+
+def test_new_verified_merge_during_uq_coalesces_next_tick(t):
+    t.cd(tu_deploy=True)
+    t.merge()
+    more = []
+    def change():
+        if not more:
+            more.append(t.merge())
+    t.khi_kiem = change
+    assert t.buoc() == {"deploy_hoan": 1}
+    assert t.buoc() == {"deploy_dat": 1} and t.ban == more[0]
+
+
+def test_unverified_head_never_replaces_m(t):
+    t.cd(tu_deploy=True)
+    m = t.merge()
+    t.k.day("main", {"direct.py": "unsafe"})
+    assert t.buoc() == {"deploy_dat": 1} and t.ban == m
+
+
+def test_scope_outside_verified_merges_requires_manual(t, monkeypatch):
+    t.cd(tu_deploy=True)
+    m = t.merge()
+    monkeypatch.setattr(chay, "pham_vi_du", lambda *a: False)
+    assert t.buoc() == {"deploy_cho_pham_vi": 1}
+    t.bam(m)
+    assert t.buoc() == {"deploy_dat": 1}
+
+
+def test_manual_merge_after_auto_still_waits(t):
+    t.cd(tu_deploy=True)
+    t.merge()
+    m = t.merge(tu=False)
+    assert t.buoc() == {'san_sang_deploy': 1}
+    assert not t.calls
+    t.bam(m)
+    assert t.buoc() == {'deploy_dat': 1}
+
+
+def test_enabling_without_intervening_tick_waits(t):
+    t.merge()
+    t.cd(tu_deploy=True)
+    assert t.buoc() == {'san_sang_deploy': 1}
+    assert not t.calls
+
+
+def test_estop_cancels_queued_manual_request(t):
+    m = t.merge()
+    t.buoc()
+    t.bam(m)
+    estop.bat('test')
+    try:
+        assert t.buoc() == {'deploy_huy': 1}
+        assert not t.calls
+    finally:
+        estop.tat()
+    t.buoc()
+    assert not t.calls
+
+
+def test_new_merge_during_deploy_survives(t):
+    t.cd(tu_deploy=True)
+    m = t.merge()
+    more = []
+    def add(buoc):
+        if buoc == 'deploy' and not more:
+            more.append(t.merge())
+    t.khi_goi = add
+    assert t.buoc() == {'deploy_dat': 1} and t.ban == m
+    assert t.buoc() == {'deploy_dat': 1} and t.ban == more[0]
+
+
+def test_project_lock_prevents_second_writer(t):
+    from tram.giao_viec.ban_chep import giu_khoa
+    from tram.duong_dan import tram_home
+    t.cd(tu_deploy=True)
+    t.merge()
+    with giu_khoa(tram_home() / 'deploy-khoa' / f'{t.da.ten}.lock'):
+        assert t.buoc() == {'deploy_dang_chay': 1}
+    assert not t.calls
+
+
+@pytest.mark.parametrize('toan_tram', [False, True])
+def test_pause_during_uq_prevents_start(t, toan_tram):
+    from tram.tu_dong.luu import ghi_tam_dung
+    t.cd(tu_deploy=True)
+    t.merge()
+    t.khi_kiem = lambda: ghi_tam_dung(t.kho.db, '_tram' if toan_tram else t.da.ten,
+                                     tam_dung=True, tac_nhan='dai-ca/dashboard')
+    assert t.buoc() == {'deploy_hoan': 1}
+    assert not t.sk('deploy.bat_dau')
+
+
+def test_crash_inside_rollback_disables_next_tick(t):
+    from tram.tu_dong.luu import doc_trang_thai
+    t.cd(tu_deploy=True)
+    t.merge()
+    t.hong.add('deploy')
+    def crash(buoc):
+        if buoc == 'lui':
+            raise OSError('fake-crash')
+    t.khi_goi = crash
+    t.buoc()
+    count = len(t.calls)
+    assert t.buoc() == {'deploy_khong_ro': 1}
+    assert len(t.calls) == count
+    assert doc_trang_thai(t.kho.db, t.da.ten).cai_dat.tu_deploy is False
+
+
+def test_manual_scope_does_not_bypass_forbidden_diff(t, monkeypatch):
+    m = t.merge(tu=False)
+    t.buoc()
+    t.bam(m)
+    monkeypatch.setattr(chay, 'ban_an_toan', lambda *a: False)
+    assert t.buoc() == {'deploy_cho_cam': 1}
+    assert not t.sk('deploy.bat_dau')
```

#### Modify `tests/test_deploy_cong_tac_v2.py` — bản vá

```diff
--- a/tests/test_deploy_cong_tac_v2.py
+++ b/tests/test_deploy_cong_tac_v2.py
@@ -1,74 +1,35 @@
-"""V2-Q2/D123: chuỗi công tắc trên kho sự kiện thật, runner/Git có hạn giả (không chứng minh OS)."""
-from dataclasses import replace
-
-import pytest
-
-from test_deploy_race import bien_gia
-from test_deploy_vong import DAI_CA, Tram, mot_lan, va
-from tram.deploy.trang_thai import doc_su_kien, tu_merge_cho_deploy
-from tram.tu_dong.luu import doi_cai_dat, ghi_tam_dung
+"""D123/D124 giữ nguyên; điểm chèn race chuyển sang Uq thay tạo worktree."""
+from test_deploy_vong import t
+from tram.tu_dong.luu import ghi_tam_dung
 
 
-@pytest.mark.parametrize("tat, nhip_khi_tat", [(True, True), (True, False), (False, False)])
-def test_v2_q2_san_sang_tam_dung_roi_doi_cong_tac(tmp_path, tat, nhip_khi_tat):
-    tr = Tram(tmp_path, tu_deploy=True)
-    try:
-        ghi_tam_dung(tr.kho.db, tr.da.ten, tam_dung=True, tac_nhan=DAI_CA)
-        commit = tr.merge()
-        assert tr.buoc() == {"san_sang_deploy": 1}
-        assert tr.buoc() == {}
-        assert len(tr.sk("deploy.san_sang")) == 1
-        if tat:
-            doi_cai_dat(tr.kho.db, tr.da.ten, lambda c: replace(c, tu_deploy=False), tac_nhan=DAI_CA)
-            if nhip_khi_tat:
-                assert tr.buoc() == {"san_sang_deploy": 1}
-                assert "tu_deploy_tat" in tr.sk("deploy.san_sang")[-1]["cho"]
-                for _ in range(3):
-                    assert tr.buoc() == {}
-                assert len(tr.sk("deploy.san_sang")) == 2
-            doi_cai_dat(tr.kho.db, tr.da.ten, lambda c: replace(c, tu_deploy=True), tac_nhan=DAI_CA)
-        ghi_tam_dung(tr.kho.db, tr.da.ten, tam_dung=False, tac_nhan=DAI_CA)
-        tr.buoc()
-        for _ in range(3):
-            assert tr.buoc() == {}
-        assert len(tr.sk("deploy.bat_dau")) == (0 if tat else 1)
-        assert tr.ban() == (None if tat else commit)
-        assert tu_merge_cho_deploy(doc_su_kien(tr.kho.db, tr.da.ten)) is None
-        if tat:
-            tr.bam(commit)
-            assert tr.buoc() == {"deploy_dat": 1}
-            assert tr.buoc() == {}
-            assert len(tr.sk("deploy.bat_dau")) == 1
-            assert tr.sk("deploy.bat_dau")[0]["nguon"] == "dai_ca"
-    finally:
-        tr.kho.close()
+def test_pause_resume_preserves_trigger(t):
+    t.cd(tu_deploy=True)
+    m = t.merge()
+    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=True, tac_nhan="dai-ca/dashboard")
+    t.buoc()
+    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=False, tac_nhan="dai-ca/dashboard")
+    assert t.buoc() == {"deploy_dat": 1} and t.ban == m
 
 
-@pytest.mark.parametrize("tat", [True, False])
-def test_doi_cong_tac_khi_chuan_bi_phai_xet_lai_trigger(tmp_path, monkeypatch, tat):
-    tr = Tram(tmp_path, tu_deploy=True)
-    try:
-        db, ten = tr.kho.db, tr.da.ten
-        ghi_tam_dung(db, ten, tam_dung=True, tac_nhan=DAI_CA)
-        commit = tr.merge()
-        assert tr.buoc() == {"san_sang_deploy": 1}
-        ghi_tam_dung(db, ten, tam_dung=False, tac_nhan=DAI_CA)
+def test_off_on_between_ticks_consumes_ready_trigger(t):
+    t.cd(tu_deploy=True)
+    m = t.merge()
+    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=True, tac_nhan="dai-ca/dashboard")
+    t.buoc()
+    t.cd(tu_deploy=False)
+    t.cd(tu_deploy=True)
+    ghi_tam_dung(t.kho.db, t.da.ten, tam_dung=False, tac_nhan="dai-ca/dashboard")
+    assert t.buoc() == {} and not t.sk("deploy.bat_dau")
+    t.bam(m)
+    assert t.buoc() == {"deploy_dat": 1}
 
-        def doi():
-            if tat:
-                doi_cai_dat(db, ten, lambda c: replace(c, tu_deploy=False), tac_nhan=DAI_CA)
-                doi_cai_dat(db, ten, lambda c: replace(c, tu_deploy=True), tac_nhan=DAI_CA)
 
-        boc, da = mot_lan(doi)
-        va(monkeypatch, "tao_worktree", boc)
-        assert tr.buoc() == ({"deploy_hoan": 1} if tat else {"deploy_dat": 1})
-        assert da and len(tr.sk("deploy.bat_dau")) == (0 if tat else 1)
-        assert len(tr.sk("deploy.lenh")) == (0 if tat else 2)
-        if tat:
-            assert tr.buoc() == {}                 # không tự thử lại bản đã chờ trước lần bật
-            tr.bam(commit)
-            assert tr.buoc() == {"deploy_dat": 1}   # quyền bấm tay vẫn giữ
-        assert tr.buoc() == {}
-        assert len(tr.sk("deploy.bat_dau")) == 1
-    finally:
-        tr.kho.close()
+def test_failed_version_is_not_automatically_retried(t):
+    t.cd(tu_deploy=True)
+    t.merge()
+    t.hong.add("deploy")
+    assert t.buoc() == {"deploy_da_lui": 1}
+    n = len(t.calls)
+    t.buoc()
+    assert len(t.calls) == n
```

#### Create `tests/test_tm20_review.py` — toàn bộ file

```python
"""Hồi quy review độc lập: kho tạm, không gọi Uq/deploy thật."""
from types import SimpleNamespace as NS
from dataclasses import replace
import pytest
from test_tm20_chuoi import bo, M, L
from tram.deploy.trang_thai import SK, tu_merge_cho_deploy, doc_su_kien
from tram.deploy.ghi import ghi
from tram.deploy.doi_soat import chua_doi_soat
from tram.deploy import chay, ban


def test_enable_without_tick_does_not_consume_old_merge():
    def s(i, loai, **d):
        return SK(i, loai, d, '', 'tram/tu-deploy', 'b')
    ds = [s(1, 'tu_merge.bat_dau', commit=M), s(2, 'pr.da_merge', commit=M, merge_commit=M),
          s(3, 'tu_dong.cai_dat', doi=['tu_deploy'], cai_dat={'tu_deploy': True})]
    assert tu_merge_cho_deploy(ds) is None


def test_wrong_auto_trigger_cannot_deploy_new_manual_merge(bo, monkeypatch):
    monkeypatch.setattr(chay, 'tu_merge_cho_deploy', lambda *a, **kw: NS(du_lieu={'merge_commit': L}))
    assert bo.run() == 'deploy_hoan'
    assert not any(b == 'deploy' for b, *_ in bo.calls)


def test_baseline_is_observed_after_uq(bo, monkeypatch):
    current = [L]
    def kiem(*a):
        current[0] = 'c' * 40
        return True
    monkeypatch.setattr(chay, 'kiem_ban', kiem)
    bo.ans['chuan_bi'] = lambda: dict(dat=True, da_dung=True, san_sang=True, ban_truoc=current[0])
    assert bo.run() == 'deploy_dat'
    assert next(truoc for b, c, truoc in bo.calls if b == 'deploy') == 'c' * 40


def test_uq_run_id_includes_project(tmp_path, monkeypatch):
    from tram.phieu.kho import KhoPhieu
    calls = []
    monkeypatch.setattr(ban, 'cong_mo', lambda: True)
    monkeypatch.setattr(ban, 'kiem_tu_xa', lambda *a, **kw: (calls.append(kw), NS(dat=True))[1])
    k = KhoPhieu(tmp_path / 'sk.db')
    try:
        for ten in ('a', 'b'):
            da = NS(ten=ten, lenh_cho_phep=('test',), giao=NS(lenh_kiem_mac_dinh=('test',)))
            ban.kiem_ban(k.db, None, da, M, '1')
        assert calls[0]['giao_id'] != calls[1]['giao_id']
    finally:
        k.close()


def test_rollback_intent_persisted_before_external_call(bo):
    bo.ans['deploy'] = dict(dat=False, da_dung=True)
    def crash():
        ds = doc_su_kien(bo.k.db, 'a')
        assert any(s.loai == 'deploy.lenh' and s.du_lieu.get('buoc') == 'lui' for s in ds)
        raise OSError('mat-ket-noi')
    bo.ans['lui'] = crash
    with pytest.raises(OSError):
        bo.run()


def test_missing_baseline_does_not_mark_current_as_healthy(bo, monkeypatch):
    bo.ans['chuan_bi'] = dict(dat=True, da_dung=True, san_sang=False, ban_truoc=L)
    assert bo.run() == 'deploy_cho_ban_nen'
    assert not any(s.loai == 'deploy.bat_dau' for s in doc_su_kien(bo.k.db, 'a'))


def test_wrong_artifact_never_becomes_success(monkeypatch):
    import json
    from tram.deploy import duong
    from test_tm20_duong import cd
    monkeypatch.setattr(duong, 'kiem_tep', lambda p: None)
    monkeypatch.setattr(duong.pwd, 'getpwnam', lambda n: NS(pw_uid=900, pw_dir='/tmp/dp'))
    def run(argv, **kw):
        req = json.loads(kw['input'])
        r = {**req, 'dat': True, 'da_dung': True, 'san_sang': True,
             'ban_truoc': L, 'ban_thuc': L, 'artifact': L}
        return NS(returncode=0, stdout=json.dumps(r).encode())
    monkeypatch.setattr(duong, 'chay_gioi_han', run)
    assert duong.DuongDeploy('a', cd()).goi('kiem_song', 'dp-1', M, L)['dat'] is False
```

#### Mã — chỉ áp sau RED, rồi chạy lại lệnh trên

#### Create `tram/deploy/thuc_hien.py` — toàn bộ file

```python
"""Một chuỗi, chỉ lùi khi đường deploy xác nhận không còn writer của lượt."""
import time
from tram.deploy.ghi import ghi


def thuc_hien(db, ten, duong, m, commit, truoc):
    def goi(buoc, c):
        ghi(db, ten, "deploy.lenh", {"ma_thao_tac": m, "buoc": buoc, "bat_dau": True})
        start = time.monotonic()
        r = duong.goi(buoc, m, c, truoc)
        ghi(db, ten, "deploy.lenh", {"ma_thao_tac": m, "buoc": buoc,
                                     "ma_thoat": 0 if r and r["dat"] else 1,
                                     "giay": round(time.monotonic() - start), "het_gio": None,
                                     "da_dung": bool(r and r["da_dung"])})
        return r
    r = goi("deploy", commit)
    if not r or not r["da_dung"]:
        return "khong_ro"
    if r["dat"]:
        r = goi("kiem_song", commit)
        if not r or not r["da_dung"]:
            return "khong_ro"
        if r["dat"]:
            return "dat"
    r = goi("lui", truoc)
    if not r or not r["da_dung"]:
        return "khong_ro"
    if not r["dat"]:
        return "lui_hong"
    r = goi("kiem_song_sau_lui", truoc)
    if not r or not r["da_dung"]:
        return "khong_ro"
    return "da_lui" if r["dat"] else "lui_hong"
```

#### Modify `tram/deploy/chay.py` — bản vá

```diff
--- a/tram/deploy/chay.py
+++ b/tram/deploy/chay.py
@@ -1,15 +1,13 @@
-"""Chuẩn bị bản sạch, kiểm tươi sát lúc bắt đầu, ghi đúng tập commit được bao phủ."""
-import os
-import subprocess
-
+"""Chốt M/L/cài đặt; Uq kiểm M, quyền dự án chạy triển khai. Không checkout mã dưới trạm."""
 from tram.chu import estop
-from tram.deploy.chuoi import chay_chuoi
+from tram.deploy.ban import ban_an_toan, chon_ban, kiem_ban, pham_vi_du
+from tram.deploy.doi_soat import chua_doi_soat
+from tram.deploy.duong import DuongDeploy
 from tram.deploy.ghi import ghi, ket_thuc, ma_chuoi
-from tram.deploy.git import dinh_hien_tai, la_to_tien, sha_cua, tao_worktree, xoa_worktree
-from tram.deploy.lenh import chay_buoc, don_log_cu, moi_truong, thu_muc_log
-from tram.deploy.trang_thai import commit_truoc, doc_su_kien, ma, merge_chua_deploy
-from tram.deploy.trang_thai import tu_merge_cho_deploy
-from tram.duong_dan import tram_home
+from tram.deploy.git import la_to_tien
+from tram.deploy.thuc_hien import thuc_hien
+from tram.deploy.trang_thai import doc_su_kien, ma, merge_chua_deploy, tu_merge_cho_deploy
+from tram.tu_dong.cong_kiem import cong_mo
 from tram.tu_dong.khoa import ly_do_chan
 from tram.tu_dong.luu import doc_trang_thai
 
@@ -28,35 +26,40 @@
     ds = doc_su_kien(db, da.ten)
     if any(s.loai == "deploy.bat_dau" and ma(s) == m for s in ds):
         return "deploy_da_co"
-    wt, truoc = tram_home() / "kho-deploy" / da.ten, commit_truoc(ds)
+    if chua_doi_soat(ds) or not cong_mo():
+        return "deploy_cho_doi_soat"
+    tt = doc_trang_thai(db, da.ten)
+    if yc is not None and yc.du_lieu.get("phien_ban") != tt.phien_ban:
+        return huy(db, da.ten, yc, "cai_dat_doi")
     try:
-        # Chụp tập phủ trước tạo worktree. Merge ghi sau đó không bị tiêu thụ bởi mốc sự kiện.
-        bao = phu(kg, ds, commit)
-        tao_worktree(kg, wt, commit)
-        dinh = dinh_hien_tai(kg, da.nhanh_chinh)
-        if yc is None:
-            tm = tu_merge_cho_deploy(doc_su_kien(db, da.ten), ma_nguon=ma_yc)
-            if tm is None:
-                return "deploy_hoan"             # D123: trigger có thể bị tiêu trong lúc chuẩn bị
-        tt = doc_trang_thai(db, da.ten)
-        ly = ly_do_chan(tt, viec="deploy_tay" if yc else "deploy", bat_ghi=bat_ghi(da.ten),
-                       estop_bat=estop.dang_bat())
-        if ly or dinh != commit:
-            return huy(db, da.ten, yc, ly[0] if ly else "ban_moi_hon") if yc else "deploy_hoan"
-        ghi(db, da.ten, "deploy.bat_dau", {"ma_thao_tac": m, "commit": commit, "commit_truoc": truoc,
-                                          "nguon": nguon, "bao_gom": bao, **({"yeu_cau": ma(yc)} if yc else {})})
-        thu_muc = thu_muc_log(da.ten)
-        don_log_cu(thu_muc)
-        env = moi_truong(os.environ, da.ten, commit, truoc)
-        def chay(buoc, lenh):
-            kq = chay_buoc(buoc, lenh, cwd=wt, env=env, log=thu_muc / f"{m}.log")
-            ghi(db, da.ten, "deploy.lenh", {"ma_thao_tac": m, **kq.su_kien()})
-            return kq
-        ket_qua = chay_chuoi(tt.cai_dat, chay)
-        ket_thuc(db, da.ten, m, ket_qua)
-        return f"deploy_{ket_qua}"
-    finally:
-        try:
-            xoa_worktree(kg, wt)
-        except (OSError, subprocess.SubprocessError):
-            ghi(db, da.ten, "deploy.don_loi", {"ma_thao_tac": m})
+        duong = DuongDeploy(da.ten, tt.cai_dat)
+    except (OSError, ValueError, KeyError):
+        return "deploy_cho_duong"
+    if not kiem_ban(db, kg, da, commit, tt.phien_ban):
+        return "deploy_cho_kiem"
+    nen = duong.goi("chuan_bi", m, commit, "")
+    if not nen or not all(nen[k] for k in ("dat", "da_dung", "san_sang")):
+        return "deploy_cho_ban_nen"
+    truoc = nen["ban_truoc"]
+    if not ban_an_toan(kg, da, truoc, commit):
+        return "deploy_cho_cam"
+    if not pham_vi_du(kg, ds, truoc, commit) and nguon != "dai_ca":
+        return "deploy_cho_pham_vi"
+    moi = doc_trang_thai(db, da.ten)
+    ly = ly_do_chan(moi, viec="deploy_tay" if yc else "deploy", bat_ghi=bat_ghi(da.ten),
+                   estop_bat=estop.dang_bat())
+    ds = doc_su_kien(db, da.ten)
+    if (ly or moi.phien_ban != tt.phien_ban or not cong_mo() or chua_doi_soat(ds)
+            or chon_ban(kg, ds, da.nhanh_chinh) != commit):
+        return huy(db, da.ten, yc, "cai_dat_hoac_ban_doi") if yc else "deploy_hoan"
+    if yc is None:
+        tm = tu_merge_cho_deploy(ds, ma_nguon=ma_yc)
+        if tm is None or tm.du_lieu.get("merge_commit") != commit:
+            return "deploy_hoan"
+    ghi(db, da.ten, "deploy.bat_dau", {"ma_thao_tac": m, "commit": commit, "commit_truoc": truoc,
+                                      "nguon": nguon, "bao_gom": phu(kg, ds, commit),
+                                      "phien_ban": tt.phien_ban, "cai_dat": tt.cai_dat.phang(),
+                                      **({"yeu_cau": ma(yc)} if yc else {})})
+    kq = thuc_hien(db, da.ten, duong, m, commit, truoc)
+    ket_thuc(db, da.ten, m, kq)
+    return f"deploy_{kq}"
```

#### Modify `tram/deploy/vong.py` — bản vá

```diff
--- a/tram/deploy/vong.py
+++ b/tram/deploy/vong.py
@@ -1,16 +1,18 @@
-"""Pha deploy riêng: đối soát, yêu cầu tay, trigger tự động; trước chuỗi đọc lại khoá."""
+"""Một khoá/dự án, đối soát crash trước chọn bản; không chọn HEAD thay merge đã xác minh."""
 import subprocess
 from collections import Counter
-
 import yaml
-
 from tram.cau_hinh.bat_ghi import bat_ghi as doc_bat_ghi
 from tram.chu import estop
+from tram.deploy.ban import chon_ban
 from tram.deploy.chay import chuoi, huy, phu
+from tram.deploy.doi_soat import chua_doi_soat
 from tram.deploy.ghi import ghi, ket_thuc
 from tram.deploy.git import sha_cua
-from tram.deploy.trang_thai import (chuoi_dang_do, da_ghi_nhan, doc_su_kien, ma, merge_chua_deploy,
-                                    tu_merge_cho_deploy, yeu_cau_cho)
+from tram.deploy.trang_thai import (cuoi, chuoi_dang_do, da_ghi_nhan, doc_su_kien, ma,
+                                    merge_chua_deploy, tu_merge_cho_deploy, yeu_cau_cho)
+from tram.duong_dan import tram_home
+from tram.giao_viec.ban_chep import giu_khoa, KiemLaiDangBan
 from tram.tu_dong.khoa import ly_do_chan
 from tram.tu_dong.luu import doc_trang_thai
 
@@ -22,12 +24,21 @@
         return False
 
 
+def _cho(db, ten, c, ly):
+    d = {"commit": c, "ly_do": ly}
+    cu = cuoi(doc_su_kien(db, ten), "deploy.cho")
+    if cu is None or cu.du_lieu != d:
+        ghi(db, ten, "deploy.cho", d)
+
+
 def _buoc(bo, kho, da, bat_ghi, dem):
     db = kho.db
     for bd in chuoi_dang_do(doc_su_kien(db, da.ten)):
         ket_thuc(db, da.ten, ma(bd), "khong_ro")
         dem["deploy_khong_ro"] += 1
     ds = doc_su_kien(db, da.ten)
+    if chua_doi_soat(ds):
+        return
     yc = yeu_cau_cho(ds)
     if estop.dang_bat():
         if yc:
@@ -43,29 +54,35 @@
     tm, gom = tu_merge_cho_deploy(ds), merge_chua_deploy(ds)
     if not yc and not (gom and bat_ghi(da.ten) and tt.cai_dat.du_lenh):
         return
-    dinh = sha_cua(kg, f"origin/{da.nhanh_chinh}")
-    if not dinh:
+    c = chon_ban(kg, ds, da.nhanh_chinh)
+    if not c:
         return
+    bao = phu(kg, ds, c)
+    moi = bool(bao and not da_ghi_nhan(ds, c, bao, cho=ly))
+    if not yc and moi:
+        ghi(db, da.ten, "deploy.san_sang", {"commit": c, "so_merge": len(bao), "bao_gom": bao, "cho": ly})
     if yc:
-        c = yc.du_lieu.get("commit", "")
-        if c != dinh:
-            ly = "ban_moi_hon" if sha_cua(kg, c) else "commit_khong_co"
-            dem[huy(db, da.ten, yc, ly)] += 1
-        else:
-            dem[chuoi(db, kg, da, c, "dai_ca", ma(yc), bat_ghi, yc)] += 1
-    elif tm and not ly:
-        dem[chuoi(db, kg, da, dinh, "tu_dong", f"sk-{tm.id}", bat_ghi)] += 1
+        if yc.du_lieu.get("commit") != c:
+            dem[huy(db, da.ten, yc, "ban_moi_hon")] += 1
+            return
+        kq = chuoi(db, kg, da, c, "dai_ca", ma(yc), bat_ghi, yc)
+    elif tm and tm.du_lieu.get("merge_commit") == c and not ly:
+        kq = chuoi(db, kg, da, c, "tu_dong", f"sk-{tm.id}", bat_ghi)
     else:
-        bao = phu(kg, ds, dinh)
-        if bao and not da_ghi_nhan(ds, dinh, bao, cho=ly):
-            ghi(db, da.ten, "deploy.san_sang", {"commit": dinh, "so_merge": len(bao), "bao_gom": bao, "cho": ly})
+        if moi:
             dem["san_sang_deploy"] += 1
+        return
+    dem[kq] += 1
+    _cho(db, da.ten, c, kq if kq.startswith("deploy_cho_") else "")
 
 
 def buoc_deploy(bo, kho, da, *, bat_ghi=bat_ghi_an_toan):
     dem = Counter()
     try:
-        _buoc(bo, kho, da, bat_ghi, dem)
+        with giu_khoa(tram_home() / "deploy-khoa" / f"{da.ten}.lock"):
+            _buoc(bo, kho, da, bat_ghi, dem)
+    except KiemLaiDangBan:
+        return {"deploy_dang_chay": 1}
     except (OSError, subprocess.SubprocessError):
         dem["deploy_chuan_bi_loi"] += 1
     return dict(dem)
```

#### Modify `tram/deploy/trang_thai.py` — bản vá

```diff
--- a/tram/deploy/trang_thai.py
+++ b/tram/deploy/trang_thai.py
@@ -6,7 +6,8 @@
 
 TAC_NHAN = "tram/tu-deploy"
 LOAI = ("pr.da_merge", "tu_merge.bat_dau", "deploy.yeu_cau", "deploy.huy", "deploy.san_sang", "deploy.bat_dau",
-        "deploy.lenh", "deploy.xong", "tu_dong.cai_dat", "tu_dong.tam_dung")
+        "deploy.lenh", "deploy.xong", "tu_dong.cai_dat", "tu_dong.tam_dung",
+        "deploy.kiem", "deploy.doi_soat", "deploy.cho")
 HONG = ("da_lui", "lui_hong")
 
 
@@ -77,13 +78,12 @@
 
 
 def tu_merge_cho_deploy(ds: list[SK], *, ma_nguon: str | None = None) -> SK | None:
-    # D123: cả khi tắt/bật giữa hai nhịp, bản đã sẵn sàng trước lần tắt vẫn chờ Đại ca.
-    tat = _id(cuoi(ds, "tu_dong.cai_dat", lambda s: "tu_deploy" in s.du_lieu.get("doi", [])
-                  and s.du_lieu.get("cai_dat", {}).get("tu_deploy") is False))
-    da = bao_gom(ds, "deploy.bat_dau") | bao_gom(ds, "deploy.san_sang", lambda s: "tu_deploy_tat" in
-                                               s.du_lieu.get("cho", []))
-    da |= bao_gom(ds, "deploy.san_sang", lambda s: s.id < tat)
-    return cuoi(ds, "pr.da_merge", lambda s: s.id not in da and la_tu_merge(ds, s)
+    # D123: chỉ sự kiện merge sau lần bật gần nhất; không phụ thuộc có tick lúc đang tắt.
+    bat = _id(cuoi(ds, "tu_dong.cai_dat", lambda s: "tu_deploy" in s.du_lieu.get("doi", [])
+                  and s.du_lieu.get("cai_dat", {}).get("tu_deploy") is True))
+    da = bao_gom(ds, "deploy.bat_dau") | bao_gom(ds, "deploy.san_sang",
+        lambda s: "tu_deploy_tat" in s.du_lieu.get("cho", []))
+    return cuoi(ds, "pr.da_merge", lambda s: s.id > bat and s.id not in da and la_tu_merge(ds, s)
                 and (ma_nguon is None or ma_nguon == f"sk-{s.id}"))
 
 
```

#### Modify `tram/deploy/ghi.py` — bản vá

```diff
--- a/tram/deploy/ghi.py
+++ b/tram/deploy/ghi.py
@@ -30,10 +30,18 @@
     TẠM DỪNG dự án, `lui-hong` (D97 luật 1). Không rõ kết quả → TẠM DỪNG dự án, `khong-ro` (Đại ca chốt 18/10, câu 3
     plan TM-1); không tính là một lần hỏng."""
     with giao_dich(db):
+        cu = next((s for s in doc_su_kien(db, du_an) if s.loai == "deploy.xong"
+                   and s.du_lieu.get("ma_thao_tac") == ma), None)
+        if cu is not None:
+            return cu.du_lieu["dem_hong"]
         dem = 0 if ket_qua == "dat" else dem_hong(doc_su_kien(db, du_an)) + (ket_qua in HONG)
         ghi_trong_giao_dich(db, du_an, "deploy.xong", {"ma_thao_tac": ma, "ket_qua": ket_qua, "dem_hong": dem},
                             tac_nhan=TAC_NHAN, luc=bay_gio())
         tat = "lui-hong" if ket_qua == "lui_hong" else ("hong-3-lan" if ket_qua in HONG and dem >= TU_TAT_SAU else "")
+        if ket_qua == "khong_ro" and any(s.loai == "deploy.lenh" and s.du_lieu.get("ma_thao_tac") == ma
+                and s.du_lieu.get("buoc") in ("lui", "kiem_song_sau_lui")
+                for s in doc_su_kien(db, du_an)):
+            tat = "lui-hong"
         if tat:
             doi_cai_dat(db, du_an, lambda c: replace(c, tu_deploy=False), tac_nhan=TAC_NHAN, them={"ly_do": tat})
         if ket_qua in ("lui_hong", "khong_ro"):
```

#### Modify `tram/deploy/hien_thi.py` — bản vá

```diff
--- a/tram/deploy/hien_thi.py
+++ b/tram/deploy/hien_thi.py
@@ -57,7 +57,8 @@
     if s.loai == "deploy.xong" and d.get("ket_qua") in LOAI_XONG:
         bd = bat_dau_cua(ds, s)
         bd = bd.du_lieu if bd else {}
-        buoc = " → ".join(_buoc(x) for x in ds if x.loai == "deploy.lenh" and ma(x) == ma(s))
+        buoc = " → ".join(_buoc(x) for x in ds if x.loai == "deploy.lenh"
+                           and ma(x) == ma(s) and not x.du_lieu.get("bat_dau"))
         if d["ket_qua"] in ("da_lui", "lui_hong") and bd.get("commit_truoc"):
             buoc += f" (bản trước {bd['commit_truoc'][:7]})"
         return {"loai": LOAI_XONG[d["ket_qua"]], "bead_id": None, "commit": bd.get("commit"), "chi_tiet": buoc,
```

**GREEN:** tất cả test của task và hồi quy liên quan đạt, 0 dòng chặn mới; lỗi host không được tính là GREEN.

### Task 6: Passkey, phiên bản và đối soát qua ledger hiện có

**RED cần chứng minh:** Mã thao tác sai hoặc tái dùng cho lượt khác không được mở chốt. Thiếu/giả passkey và phiên bản cũ phải bị từ chối.

```bash
tests/chan_host/chay.sh -q tests/test_tm20_cua.py tests/test_tm20_tich_hop.py tests/test_tm20_doi_soat_review.py tests/test_api_deploy.py tests/test_api_tu_dong.py tests/test_passkey_tm_tc.py tests/test_thao_tac_tu_dong.py
```

#### Test/fixture — áp trước, chạy RED

#### Create `tests/test_tm20_cua.py` — toàn bộ file

```python
"""Chốt bền và thân API; thông báo không chứa output của đường deploy."""
import pytest
from pydantic import ValidationError
from tram.api.than import ThanDieuKien
from tram.api.doi_soat_deploy import ThanTiepTuc
from tram.deploy.doi_soat import chua_doi_soat
from tram.deploy.trang_thai import SK


def test_cannot_disable_ci_by_direct_api():
    with pytest.raises(ValidationError):
        ThanDieuKien(ci=False, cot=True, hang_rao=True)


def test_continue_needs_explicit_run_and_version():
    r = ThanTiepTuc(ma_thao_tac="ma-000001", expected_version="1",
                    doi_soat={"ma": "dp-1", "commit": "a" * 40})
    assert r.doi_soat.commit == "a" * 40
    with pytest.raises(ValidationError):
        ThanTiepTuc(ma_thao_tac="ma-000001", expected_version="1", doi_soat={"ma": "dp-1", "commit": "HEAD"})


def test_continue_event_cannot_clear_uncertainty():
    def s(i, loai, **d):
        return SK(i, loai, d, "2026-10-20", "tram/tu-deploy", None)
    x = s(1, "deploy.xong", ma_thao_tac="dp-1", ket_qua="khong_ro")
    ds = [x, s(2, "tu_dong.tiep_tuc")]
    assert chua_doi_soat(ds) == [x]
    ds.append(s(3, "deploy.doi_soat", ma_thao_tac="dp-khac"))
    assert chua_doi_soat(ds) == [x]
    ds.append(s(4, "deploy.doi_soat", ma_thao_tac="dp-1"))
    assert chua_doi_soat(ds) == []
```

#### Modify `tests/test_api_deploy.py` — bản vá

```diff
--- a/tests/test_api_deploy.py
+++ b/tests/test_api_deploy.py
@@ -25,7 +25,9 @@
 
 @pytest.fixture(autouse=True)
 def dinh_gia(monkeypatch):
-    monkeypatch.setattr("tram.api.tuyen_deploy.doc_dinh", lambda ten: M5)
+    monkeypatch.setattr("tram.api.tuyen_deploy.doc_dinh", lambda ten, db: M5)
+    monkeypatch.setattr("tram.thao_tac.deploy.cong_mo", lambda: True)
+    monkeypatch.setattr("tram.thao_tac.deploy.can_duong", lambda *a: None)
 
 
 def _app(tmp_path, *, unix=True, cd=DU, san_sang=True):
@@ -52,7 +54,7 @@
 
 
 def _than(ma="ma-api-dp-001", commit=M5):
-    return {"ma_thao_tac": ma, "expected_version": "", "expected_commit": commit}
+    return {"ma_thao_tac": ma, "expected_version": "1", "expected_commit": commit}
 
 
 def _yeu_cau(pt) -> list[dict]:
@@ -68,7 +70,7 @@
     ct = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()
     assert ct["san_sang"] is None and ct["dang_deploy"]["trang_thai"] == "cho" and ct["dang_deploy"]["commit"] == M5
     assert goi(app, "POST", DP, json_body=_than(), headers=DAI_CA).json()["lap_lai"] is True
-    assert _yeu_cau(pt) == [{"ma_thao_tac": "ma-api-dp-001", "commit": M5, "nguon": "dai_ca"}]
+    assert _yeu_cau(pt) == [{"ma_thao_tac": "ma-api-dp-001", "commit": M5, "nguon": "dai_ca", "phien_ban": "1"}]
     r = goi(app, "POST", DP, json_body=_than("ma-api-dp-002"), headers=DAI_CA)       # đã có yêu cầu chờ
     assert r.status == 422 and "Đang có một lần deploy" in r.json()["loi"]
 
@@ -146,7 +148,7 @@
 
 def test_dinh_that_doi_chua_co_su_kien_409(tmp_path, monkeypatch):
     app, pt = _app(tmp_path)
-    monkeypatch.setattr("tram.api.tuyen_deploy.doc_dinh", lambda ten: "6" * 40)
+    monkeypatch.setattr("tram.api.tuyen_deploy.doc_dinh", lambda ten, db: "6" * 40)
     r = goi(app, "POST", DP, json_body=_than(), headers=DAI_CA)
     assert r.status == 409 and r.json()["loi"].startswith("Có bản mới hơn — tải lại")
     assert _yeu_cau(pt) == []
```

#### Create `tests/test_tm20_tich_hop.py` — toàn bộ file

```python
"""Đối soát không gửi lại lệnh, khoá tươi và lỗi không rò dữ liệu."""
from types import SimpleNamespace as NS
import pytest
from test_deploy_vong import t
from tram.api import doi_soat_deploy as api
from tram.deploy.doi_soat import chua_doi_soat
from tram.deploy.trang_thai import doc_su_kien
from tram.suy.deploy import chi_tiet_deploy
from tram.thao_tac.loi import KhongHopLe


def test_unknown_requires_explicit_confirmation_and_finished_target(t, monkeypatch):
    t.cd(tu_deploy=True)
    t.merge()
    t.hong.add("khong_ro")
    t.buoc()
    can = chi_tiet_deploy(t.kho.db, t.da.ten)["doi_soat"]
    with pytest.raises(KhongHopLe):
        api._doi_soat(t.kho, t.da.ten, None)
    monkeypatch.setattr(api, "DuongDeploy", lambda *a: t)
    xn = NS(ma=can["ma"], commit=can["truoc"])
    t.hong.discard("khong_ro")
    n = len(t.calls)
    api._doi_soat(t.kho, t.da.ten, xn)
    assert t.calls[n:][0][0] == "doi_soat"
    assert not chua_doi_soat(doc_su_kien(t.kho.db, t.da.ten))
    api._doi_soat(t.kho, t.da.ten, xn)
    assert len(t.calls) == n + 1


def test_wait_reason_is_visible_and_deduplicated(t):
    t.cd(tu_deploy=True)
    t.merge()
    t.uq = False
    t.buoc()
    t.buoc()
    ds = t.sk("deploy.cho")
    assert len(ds) == 1 and ds[0]["ly_do"] == "deploy_cho_kiem"
    assert "kiểm" in chi_tiet_deploy(t.kho.db, t.da.ten)["ly_do_deploy"]


def test_failed_rollback_disables_and_freezes(t):
    t.cd(tu_deploy=True)
    t.merge()
    t.hong.update(("deploy", "lui"))
    assert t.buoc() == {"deploy_lui_hong": 1}
    before = len(t.calls)
    t.buoc()
    assert len(t.calls) == before
```

#### Modify `tests/test_passkey_tm_tc.py` — bản vá

```diff
--- a/tests/test_passkey_tm_tc.py
+++ b/tests/test_passkey_tm_tc.py
@@ -21,7 +21,8 @@
 
 
 @pytest.fixture
-def ctx(tmp_path):
+def ctx(tmp_path, monkeypatch):
+    monkeypatch.setattr("tram.thao_tac.tu_dong.can_duong", lambda *a: None)
     app, pt = tao_app_gia(tmp_path, {'hr': BdGia()}, co_passkey=False)
     pt.bat_ghi = lambda _: True
     dv = DichVu(tmp_path/'pk.db', LOGIN, MAY_B)
```

#### Create `tests/test_tm20_doi_soat_review.py` — toàn bộ file

```python
"""Mã thao tác phải được kiểm trước khi đối soát ghi mở chốt."""
import pytest
from test_tm20_chuoi import bo, M, L
from tram.api import doi_soat_deploy as api
from tram.deploy import chay
from tram.deploy.ghi import ghi
from tram.deploy.trang_thai import doc_su_kien
from tram.deploy.doi_soat import chua_doi_soat
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot


def test_reconcile_invalid_operation_id_cannot_unlock(bo, tmp_path, monkeypatch):
    bo.ans['deploy'] = None
    assert bo.run() == 'deploy_khong_ro'
    can = api.ban_can_doi_soat(doc_su_kien(bo.k.db, 'a'))
    monkeypatch.setattr(api, 'DuongDeploy', chay.DuongDeploy)
    than = api.ThanTiepTuc(ma_thao_tac='not valid id', expected_version='',
                          doi_soat={'ma': can['ma'], 'commit': L})
    kt = KhoThaoTac(tmp_path / 'tt.db')
    try:
        with pytest.raises(KhongHopLe):
            api.tiep_tuc(bo.k, kt, 'a', than)
        assert chua_doi_soat(doc_su_kien(bo.k.db, 'a'))
        assert not any(b == 'doi_soat' for b, *_ in bo.calls)
    finally:
        kt.close()



def test_same_operation_cannot_unlock_another_run(bo, tmp_path, monkeypatch):
    from tram.su_kien.kho import KhoSuKien
    bo.ans['deploy'] = None
    bo.run()
    can = api.ban_can_doi_soat(doc_su_kien(bo.k.db, 'a'))
    monkeypatch.setattr(api, 'DuongDeploy', chay.DuongDeploy)
    kt, kho = KhoThaoTac(tmp_path / 'tt.db'), KhoSuKien(tmp_path / 'sk.db')
    def than(ma):
        return api.ThanTiepTuc(ma_thao_tac='confirm-0001', expected_version='',
                              doi_soat={'ma': ma, 'commit': L})
    try:
        api.tiep_tuc(kho, kt, 'a', than(can['ma']))
        bd = next(s for s in doc_su_kien(kho.db, 'a') if s.loai == 'deploy.bat_dau')
        ghi(kho.db, 'a', 'deploy.bat_dau', {**bd.du_lieu, 'ma_thao_tac': 'dp-another'})
        ghi(kho.db, 'a', 'deploy.xong', {'ma_thao_tac': 'dp-another', 'ket_qua': 'khong_ro'})
        with pytest.raises(XungDot):
            api.tiep_tuc(kho, kt, 'a', than('dp-another'))
        assert chua_doi_soat(doc_su_kien(kho.db, 'a'))
    finally:
        kt.close()
        kho.close()

```

#### Modify `tests/test_bao_tin_tu_dong.py` — bản vá

```diff
--- a/tests/test_bao_tin_tu_dong.py
+++ b/tests/test_bao_tin_tu_dong.py
@@ -79,8 +79,9 @@
     assert soan_tin("cho_review", [Tin("cho_review", "hr", "tam-dung")], None) == "[tram] hr · 1 việc chờ review (tam-dung)"
 
 
-def test_dau_cuoi_dashboard_den_tin_khong_chua_lenh(tmp_path):
+def test_dau_cuoi_dashboard_den_tin_khong_chua_lenh(tmp_path, monkeypatch):
     """Scenario "Bật tự deploy" + "Trạm tự tắt": thao tác dashboard / trạm → sự kiện → tin; không chép lệnh."""
+    monkeypatch.setattr("tram.thao_tac.tu_dong.can_duong", lambda *a: None)
     k, kt = KhoSuKien(tmp_path / "sk.db"), KhoThaoTac(tmp_path / "sk.db")
     du = replace(MAC_DINH, lenh_deploy=LENH, lenh_kiem_song="k.sh", lenh_lui="l.sh")
     luu_cai_dat_thao_tac(k, kt, "repo-nhap", du, bat_ghi=True, ma="ma-tin-00001", expected_version="0")
```

#### Mã — chỉ áp sau RED, rồi chạy lại lệnh trên

#### Create `tram/api/doi_soat_deploy.py` — toàn bộ file

```python
"""Tiếp tục chỉ mở chốt deploy khi Đại ca xác nhận đúng bản và đường đích chứng minh đã dừng."""
from pydantic import BaseModel, ConfigDict, Field

from tram.api.than import ThanGhi
from tram.deploy.doi_soat import ban_can_doi_soat
from tram.deploy.duong import DuongDeploy
from tram.deploy.ghi import ghi
from tram.deploy.trang_thai import doc_su_kien
from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import giu_khoa, KiemLaiDangBan
from tram.thao_tac.loi import KhongHopLe, XungDot
from tram.thao_tac.chay import YeuCau, chay_thao_tac
from tram.tu_dong.luu import ghi_tam_dung
from tram.thao_tac.tu_dong import tam_dung_thao_tac
from tram.tu_dong.cai_dat import tu_phang


class XacNhan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ma: str = Field(min_length=1, max_length=64)
    commit: str = Field(pattern=r"^[0-9a-f]{40}$")


class ThanTiepTuc(ThanGhi):
    doi_soat: XacNhan | None = None


def _doi_soat(kho, ten, xn):
    ds = doc_su_kien(kho.db, ten)
    can = ban_can_doi_soat(ds)
    if can is None:
        if xn and not any(s.loai == "deploy.doi_soat" and s.du_lieu.get("ma_thao_tac") == xn.ma
                          and s.du_lieu.get("commit") == xn.commit for s in ds):
            raise XungDot("Lượt đối soát đã đổi — tải lại")
        return
    if xn is None:
        raise KhongHopLe("Cần xác nhận bản thực tế và lượt cũ đã dừng trước khi Tiếp tục")
    if xn.ma != can["ma"] or xn.commit not in (can["commit"], can["truoc"]):
        raise XungDot("Lượt hoặc bản đối soát đã đổi — tải lại")
    bd = next(s for s in ds if s.loai == "deploy.bat_dau" and s.du_lieu.get("ma_thao_tac") == xn.ma)
    try:
        duong = DuongDeploy(ten, tu_phang(bd.du_lieu["cai_dat"]))
        r = duong.goi("doi_soat", xn.ma, xn.commit, can["truoc"])
    except (OSError, ValueError, KeyError):
        r = None
    if not r or not all(r[k] for k in ("dat", "da_dung", "san_sang")):
        raise KhongHopLe("Chưa xác minh được bản thực tế hoặc lượt cũ còn chạy")
    ghi(kho.db, ten, "deploy.doi_soat", {"ma_thao_tac": xn.ma, "commit": xn.commit,
                                       "xac_nhan": "dai-ca/passkey"})


def tiep_tuc(kho, kho_tt, ten, than):
    try:
        with giu_khoa(tram_home() / "deploy-khoa" / f"{ten}.lock"):
            if than.doi_soat is None:
                _doi_soat(kho, ten, None)
                return tam_dung_thao_tac(kho, kho_tt, ten, tam_dung=False,
                                         ma=than.ma_thao_tac, expected_version=than.expected_version)
            def buoc(_):
                _doi_soat(kho, ten, than.doi_soat)
                ghi_tam_dung(kho.db, ten, tam_dung=False, tac_nhan="dai-ca/dashboard",
                             them={"ma_thao_tac": than.ma_thao_tac})
                return True
            yc = YeuCau(than.ma_thao_tac, "tu_dong.tiep_tuc", ten, None,
                         {"doi_soat": than.doi_soat.model_dump()}, than.expected_version)
            return chay_thao_tac(kho_tt, yc, kiem_moi=lambda: None,
                                 cac_buoc=[("tu_dong.tiep_tuc", buoc)])
    except KiemLaiDangBan:
        raise KhongHopLe("Chuỗi deploy đang chạy — chờ kết thúc") from None
```

#### Modify `tram/api/tuyen_tu_dong.py` — bản vá

```diff
--- a/tram/api/tuyen_tu_dong.py
+++ b/tram/api/tuyen_tu_dong.py
@@ -12,6 +12,7 @@
 from tram.api.loi_envelope import TuyenEnvelopeKin
 from tram.api.phu_thuoc import kiem_du_an_bead
 from tram.api.than import ThanCaiDatTuDong, ThanGhi
+from tram.api.doi_soat_deploy import ThanTiepTuc, tiep_tuc
 from tram.chu import estop
 from tram.suy.tu_dong import chi_tiet_du_an, chung, tom_tat_du_an
 from tram.suy.tu_merge import tieu_de_bead  # TM-2
@@ -87,8 +88,9 @@
 
 
 @ghi.post("/api/du-an/{ten}/tu-dong/tiep-tuc", dependencies=[Depends(can_p)])
-def r_tiep_tuc(ten: str, than: ThanGhi, request: Request) -> dict:
-    return _tam_dung(request, ten, than, False)
+def r_tiep_tuc(ten: str, than: ThanTiepTuc, request: Request) -> dict:
+    kiem_du_an_bead(request.app.state.pt, ten)
+    return _chay(request, lambda k, kt: tiep_tuc(k, kt, ten, than))
 
 
 @ghi.post("/api/tu-dong/tam-dung")
```

#### Modify `tram/api/tuyen_deploy.py` — bản vá

```diff
--- a/tram/api/tuyen_deploy.py
+++ b/tram/api/tuyen_deploy.py
@@ -10,7 +10,8 @@
 from tram.api.tuyen_tu_dong import _bat_ghi, _chay
 from tram.cau_hinh.du_an import nap_du_an
 from tram.chu import estop
-from tram.deploy.git import dinh_hien_tai
+from tram.deploy.ban import chon_ban
+from tram.deploy.trang_thai import doc_su_kien
 from tram.giao_viec.git_kiem import kho_kiem
 from tram.thao_tac.deploy import deploy_thao_tac
 
@@ -21,8 +22,8 @@
     expected_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
 
 
-def doc_dinh(ten):
-    return dinh_hien_tai(kho_kiem(ten), nap_du_an(ten).nhanh_chinh)
+def doc_dinh(ten, db):
+    return chon_ban(kho_kiem(ten), doc_su_kien(db, ten), nap_du_an(ten).nhanh_chinh)
 
 
 @router.post("/api/du-an/{ten}/tu-dong/deploy")
@@ -31,4 +32,5 @@
     kiem_du_an_bead(pt, ten)
     return _chay(request, lambda k, kt: deploy_thao_tac(
         k, kt, ten, commit=than.expected_commit, ma=than.ma_thao_tac, bat_ghi=_bat_ghi(pt, ten),
-        estop_bat=estop.dang_bat(), doc_dinh=lambda: doc_dinh(ten)))
+        estop_bat=estop.dang_bat(), doc_dinh=lambda: doc_dinh(ten, k.db),
+        expected_version=than.expected_version))
```

#### Modify `tram/thao_tac/deploy.py` — bản vá

```diff
--- a/tram/thao_tac/deploy.py
+++ b/tram/thao_tac/deploy.py
@@ -5,6 +5,9 @@
 bản ghi `thao_tac`: khoá chung `deploy_tay` (estop, `bat_ghi`, thiếu lệnh → 422 kèm nhãn), đang deploy hay đã có
 yêu cầu chờ → 422, không có gì chờ → 422, commit Đại ca đang xem khác commit mới nhất → 409 (màn hình cũ)."""
 from tram.deploy.hien_thi import dang_deploy, san_sang
+from tram.deploy.doi_soat import chua_doi_soat
+from tram.tu_dong.cong_kiem import cong_mo
+from tram.deploy.san_sang import can_duong
 from tram.deploy.trang_thai import chua_ghi_nhan, doc_su_kien
 from tram.duong_dan import bay_gio
 from tram.su_kien.ghi_trong import ghi_trong_giao_dich
@@ -18,12 +21,17 @@
 
 
 def deploy_thao_tac(kho, kho_tt, du_an: str, *, commit: str, ma: str, bat_ghi: bool,
-                    estop_bat: bool, doc_dinh) -> KetQuaThaoTac:
+                    estop_bat: bool, doc_dinh, expected_version: str) -> KetQuaThaoTac:
     def kiem() -> None:
         ly = ly_do_chan(doc_trang_thai(kho.db, du_an), viec="deploy_tay", bat_ghi=bat_ghi, estop_bat=estop_bat)
         if ly:
             raise KhongHopLe(NHAN_LY_DO[ly[0]])
+        if doc_trang_thai(kho.db, du_an).phien_ban != expected_version:
+            raise XungDot("Cài đặt đã đổi — tải lại")
         ds = doc_su_kien(kho.db, du_an)
+        if chua_doi_soat(ds) or not cong_mo():
+            raise KhongHopLe("Cổng kiểm đóng hoặc deploy chưa đối soát")
+        can_duong(du_an, doc_trang_thai(kho.db, du_an).cai_dat)
         if dang_deploy(ds) is not None:
             raise KhongHopLe("Đang có một lần deploy của dự án này — chờ xong rồi bấm lại")
         if (ss := san_sang(ds)) is None:
@@ -35,9 +43,10 @@
     def buoc(_) -> dict:
         with giao_dich(kho.db):
             if not any(s.loai == LOAI and s.du_lieu.get("ma_thao_tac") == ma for s in doc_su_kien(kho.db, du_an)):
-                ghi_trong_giao_dich(kho.db, du_an, LOAI, {"ma_thao_tac": ma, "commit": commit, "nguon": "dai_ca"},
+                ghi_trong_giao_dich(kho.db, du_an, LOAI, {"ma_thao_tac": ma, "commit": commit, "nguon": "dai_ca",
+                                    "phien_ban": expected_version},
                                     tac_nhan=TAC_NHAN, luc=bay_gio())
         return {"commit": commit}
 
-    yc = YeuCau(ma, LOAI, du_an, None, {"commit": commit}, commit)
+    yc = YeuCau(ma, LOAI, du_an, None, {"commit": commit, "phien_ban": expected_version}, expected_version)
     return chay_thao_tac(kho_tt, yc, kiem_moi=kiem, cac_buoc=[(LOAI, buoc)])
```

#### Modify `tram/suy/deploy.py` — bản vá

```diff
--- a/tram/suy/deploy.py
+++ b/tram/suy/deploy.py
@@ -1,6 +1,7 @@
 """Khoá hiển thị TM-3 cho trang Tự động và Phê duyệt (D129: cùng tuyến ghi Deploy)."""
 from tram.deploy.hien_thi import dang_deploy, lich_su, san_sang
-from tram.deploy.trang_thai import dem_hong, doc_su_kien
+from tram.deploy.doi_soat import ban_can_doi_soat
+from tram.deploy.trang_thai import cuoi, dem_hong, doc_su_kien
 from tram.tu_dong.luu import doc_trang_thai
 
 
@@ -14,11 +15,18 @@
 
 def chi_tiet_deploy(db, ten):
     ds = doc_su_kien(db, ten)
-    return {"san_sang": san_sang_du_an(db, ten), "dang_deploy": dang_deploy(ds),
-            "lich_su": lich_su(ds), "dem_hong": dem_hong(ds)}
+    cho = cuoi(ds, "deploy.cho")
+    nhan = {"deploy_cho_cam": "Bản chạm đường cấm hoặc schema — cần kịch bản riêng",
+            "deploy_cho_duong": "Cần đường deploy riêng", "deploy_cho_ban_nen": "Cần bản quay lại đã kiểm",
+            "deploy_cho_pham_vi": "Có mã ngoài luồng — Đại ca xem phạm vi rồi Deploy tay",
+            "deploy_cho_kiem": "Bản gộp chưa kiểm đạt", "deploy_cho_doi_soat": "Cần đối soát hoặc mở cổng kiểm"}
+    ly = nhan.get(cho.du_lieu.get("ly_do"), "") if cho else ""
+    return {"san_sang": san_sang_du_an(db, ten), "dang_deploy": dang_deploy(ds), "ly_do_deploy": ly,
+            "lich_su": lich_su(ds), "dem_hong": dem_hong(ds), "doi_soat": ban_can_doi_soat(ds)}
 
 
 def muc_san_sang(du_an, kho):
     from tram.suy.phe_duyet import _muc
     ss = san_sang_du_an(kho.db, du_an)
-    return [] if ss is None else [{**_muc("san-sang-deploy", du_an, None, ss), "updated_at": ss["luc"]}]
+    return [] if ss is None else [{**_muc("san-sang-deploy", du_an, None,
+        {**ss, "phien_ban": doc_trang_thai(kho.db, du_an).phien_ban}), "updated_at": ss["luc"]}]
```

#### Create `tram/deploy/san_sang.py` — toàn bộ file

```python
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
```

#### Modify `tram/thao_tac/tu_dong.py` — bản vá

```diff
--- a/tram/thao_tac/tu_dong.py
+++ b/tram/thao_tac/tu_dong.py
@@ -3,6 +3,7 @@
 `ma_thao_tac`, tác nhân `dai-ca/dashboard`. Lưu cài đặt kiểm `expected_version` = phiên bản cài đặt (409 khi cũ);
 tạm dừng / tiếp tục KHÔNG kiểm (như estop — không hỏng vì màn hình cũ, D78). Kênh ghi (D87) kiểm ở tuyến API."""
 from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
+from tram.deploy.san_sang import can_duong
 from tram.thao_tac.chung import TAC_NHAN, co_su_kien
 from tram.thao_tac.loi import KhongHopLe, XungDot
 from tram.tu_dong.cai_dat import CaiDatTuDong, loi_cai_dat
@@ -16,6 +17,8 @@
     def kiem() -> None:
         if (loi := loi_cai_dat(cd, bat_ghi=bat_ghi)) is not None:
             raise KhongHopLe(loi)
+        if cd.tu_deploy:
+            can_duong(du_an, cd)
         if (hien := doc_cai_dat(kho.db, du_an)[1]) != expected_version:
             raise XungDot(f"Cài đặt tự động của {du_an} đã đổi (hiện {hien}, đang xem {expected_version}) — tải lại")
 
```

**GREEN:** tất cả test của task và hồi quy liên quan đạt, 0 dòng chặn mới; lỗi host không được tính là GREEN.

### Task 7: Giao diện hiện có và xác nhận bản quan sát

**RED cần chứng minh:** CI là khoá cứng; Deploy gửi phiên bản đang xem; đối soát không tự điền SHA thay người xác nhận.

```bash
cd frontend
npm run kiem
npm run build
npm run kiem-dist
```

#### Test/fixture — áp trước, chạy RED

#### Create `frontend/tests/tm20.test.mjs` — toàn bộ file

```javascript
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { DIEU_KIEN, hoiLuuLenh, hoiDeploy } from '../src/luat_trang_tu_dong.js'

test('CI là khoá cứng; câu xác nhận không cấp quyền trạm cho mã dự án', () => {
  assert.equal(DIEU_KIEN.find(x => x.ma === 'ci').khoa, true)
  assert.match(hoiLuuLenh(false), /quyền riêng/)
  assert.match(hoiDeploy('a', 'a'.repeat(40)), /phạm vi/)
})
```

#### Modify `frontend/tests/tu_dong_trang.test.mjs` — bản vá

```diff
--- a/frontend/tests/tu_dong_trang.test.mjs
+++ b/frontend/tests/tu_dong_trang.test.mjs
@@ -23,7 +23,7 @@
 
 test('hằng theo mockup: 5 điều kiện (2 luôn bật), 3 lệnh; mã commit 7 ký tự', () => {
   assert.deepEqual(DIEU_KIEN.map((d) => [d.ma, Boolean(d.khoa)]),
-    [['qc', true], ['kiem_lai', true], ['ci', false], ['cot', false], ['hang_rao', false]])
+    [['qc', true], ['kiem_lai', true], ['ci', true], ['cot', false], ['hang_rao', false]])
   assert.equal(DIEU_KIEN[3].ten, 'Việc ở cột "AI tự làm"')
   assert.deepEqual(LENH.map((l) => l.ma), ['deploy', 'kiem_song', 'lui'])
   assert.equal(ma7('a41c07e9d2b8'), 'a41c07e')
@@ -42,8 +42,8 @@
   assert.equal(hoiTamDung('repo-nhap'),
     'Tạm dừng tự merge và tự deploy của repo-nhap? Cài đặt giữ nguyên; bấm Tiếp tục để chạy lại.')
   assert.equal(hoiDeploy('repo-nhap', 'a41c07e9d2'), 'Deploy bản a41c07e của repo-nhap lên cho khách dùng?\n'
-    + 'Trạm chạy lệnh deploy rồi lệnh kiểm còn sống; hỏng thì tự lùi.')
-  assert.equal(hoiLuuLenh(false), 'Lưu 3 lệnh? Lệnh sẽ chạy trên máy B dưới tài khoản trạm.')
+    + 'Đại ca xác nhận phạm vi toàn bộ bản này, kể cả mã ngoài luồng. Trạm kiểm bản, deploy và lùi khi cần.')
+  assert.equal(hoiLuuLenh(false), 'Lưu 3 lệnh? Dùng đường deploy đã cấp quyền riêng cho dự án.')
   assert.match(hoiLuuLenh(true), /\nThiếu lệnh nên tự deploy sẽ tắt\.$/)
 })
 
```

#### Modify `frontend/tests/phe_duyet.test.mjs` — bản vá

```diff
--- a/frontend/tests/phe_duyet.test.mjs
+++ b/frontend/tests/phe_duyet.test.mjs
@@ -97,7 +97,7 @@
   // Thẻ dùng đúng hàm ghi của trang Tự động (hộp hỏi hoiDeploy, thân {ma_thao_tac, expected_version: "",
   // expected_commit}, 409/422 hiện câu máy chủ — test ở tu_dong_ghi.test.mjs) + link sang trang Tự động.
   const vue = readFileSync(new URL('../src/thanh/phe_duyet/TheSanSang.vue', import.meta.url), 'utf8')
-  assert.match(vue, /dungGhiTuDong\(\(\) => null, /)
+  assert.match(vue, /dungGhiTuDong\(\(\) => props\.muc\.chi_tiet, /)
   assert.match(vue, /@click="g\.deploy\(muc\.chi_tiet\.commit\)"/)
   assert.match(vue, /khoaDeploy\(props\.muc, kho\.tuDong, laDaiCa\.value\)/)
   assert.match(vue, />Mở trang Tự động</)
```

#### Modify `frontend/tests/tu_dong_ghi.test.mjs` — bản vá

```diff
--- a/frontend/tests/tu_dong_ghi.test.mjs
+++ b/frontend/tests/tu_dong_ghi.test.mjs
@@ -69,7 +69,7 @@
   assert.deepEqual(goi.map((x) => x.url), ['/api/du-an/repo%20nhap/tu-dong/tam-dung',
     '/api/du-an/repo%20nhap/tu-dong/tiep-tuc', '/api/du-an/repo%20nhap/tu-dong/deploy'])
   assert.deepEqual(goi.map((x) => boMa(x.than)), [{ expected_version: '' }, { expected_version: '' },
-    { expected_version: '', expected_commit: 'a41c07e9d2b8' }])
+    { expected_version: '41', expected_commit: 'a41c07e9d2b8' }])
   assert.equal(hoi.length, 2)
   assert.match(hoi[0], /^Tạm dừng tự merge và tự deploy của repo nhap\?/)
   assert.match(hoi[1], /^Deploy bản a41c07e của repo nhap/)
```

#### Mã — chỉ áp sau RED, rồi chạy lại lệnh trên

#### Modify `frontend/src/luat_trang_tu_dong.js` — bản vá

```diff
--- a/frontend/src/luat_trang_tu_dong.js
+++ b/frontend/src/luat_trang_tu_dong.js
@@ -8,7 +8,7 @@
   { ma: 'qc', ten: 'QC đạt', mo_ta: 'Một agent khác agent đã code kiểm và kết luận đạt', khoa: true },
   { ma: 'kiem_lai', ten: 'Kiểm lại đạt', mo_ta: 'Trạm tự chạy lại lệnh kiểm trong vùng cách ly', khoa: true },
   { ma: 'ci', ten: 'CI GitHub xanh', ngan: 'CI GitHub xanh',
-    mo_ta: 'Mọi kiểm tra tự động trên GitHub đã chạy xong và đạt' },
+    mo_ta: 'GitHub bắt kiểm đã chọn, nguồn tin cậy và nhánh cập nhật', khoa: true },
   { ma: 'cot', ten: 'Việc ở cột "AI tự làm"', ngan: 'Việc ở cột AI tự làm',
     mo_ta: 'Việc đi từ cột 1, Đại ca không tự gán cột' },
   { ma: 'hang_rao', ten: 'Không chạm hàng rào', ngan: 'Không chạm hàng rào',
@@ -16,7 +16,7 @@
 ]
 export const LENH = [
   { ma: 'deploy', ten: 'Lệnh deploy', ngan: 'lệnh deploy', goi_y: 'đưa bản mới lên' },
-  { ma: 'kiem_song', ten: 'Lệnh kiểm còn sống', ngan: 'lệnh kiểm còn sống', goi_y: 'chạy sau deploy, thoát 0 = sống' },
+  { ma: 'kiem_song', ten: 'Lệnh kiểm còn sống', ngan: 'lệnh kiểm còn sống', goi_y: 'xác nhận đúng bản và chức năng cốt lõi' },
   { ma: 'lui', ten: 'Lệnh lùi về bản trước', ngan: 'lệnh lùi', goi_y: 'chạy khi deploy hỏng' },
 ]
 export const CHUA_CO = 'Chưa có dữ liệu — phần này của trạm chưa chạy.'
@@ -40,8 +40,8 @@
 export const hoiTamDung = (ten) =>
   `Tạm dừng tự merge và tự deploy của ${ten}? Cài đặt giữ nguyên; bấm Tiếp tục để chạy lại.`
 export const hoiDeploy = (ten, commit) => `Deploy bản ${ma7(commit)} của ${ten} lên cho khách dùng?\n`
-  + 'Trạm chạy lệnh deploy rồi lệnh kiểm còn sống; hỏng thì tự lùi.'
-export const hoiLuuLenh = (tatTuDeploy) => 'Lưu 3 lệnh? Lệnh sẽ chạy trên máy B dưới tài khoản trạm.'
+   + 'Đại ca xác nhận phạm vi toàn bộ bản này, kể cả mã ngoài luồng. Trạm kiểm bản, deploy và lùi khi cần.'
+export const hoiLuuLenh = (tatTuDeploy) => 'Lưu 3 lệnh? Dùng đường deploy đã cấp quyền riêng cho dự án.'
   + (tatTuDeploy ? '\nThiếu lệnh nên tự deploy sẽ tắt.' : '')
 
 // Thân POST …/tu-dong/cai-dat luôn mang ĐỦ cài đặt (TM-1 `ThanCaiDat`): bản đang xem + phần đổi.
```

#### Modify `frontend/src/thanh/tu_dong/ghi_tu_dong.js` — bản vá

```diff
--- a/frontend/src/thanh/tu_dong/ghi_tu_dong.js
+++ b/frontend/src/thanh/tu_dong/ghi_tu_dong.js
@@ -64,11 +64,20 @@
   }
   function tamDung(bat) {
     const ten = layTen()
-    return lam(ten, bat ? 'tam-dung' : 'tiep-tuc', thanGhi({}, ''), bat ? hoiTamDung(ten) : '')
+    const ds = !bat && layDl()?.doi_soat
+    let doi_soat
+    if (ds) {
+      const commit = window.prompt(`Lượt ${ds.ma} chưa rõ. Sau khi kiểm bản thực tế và lượt đã dừng, `
+        + `nhập đúng SHA ${ds.commit} hoặc ${ds.truoc}.`)
+      if (![ds.commit, ds.truoc].includes(commit)) return Promise.resolve(false)
+      doi_soat = { ma: ds.ma, commit }
+    }
+    return lam(ten, bat ? 'tam-dung' : 'tiep-tuc', thanGhi(doi_soat ? { doi_soat } : {}, ''),
+      bat ? hoiTamDung(ten) : '')
   }
   function deploy(commit) {
     const ten = layTen()
-    return lam(ten, 'deploy', thanGhi({ expected_commit: commit }, ''), hoiDeploy(ten, commit))
+    return lam(ten, 'deploy', thanGhi({ expected_commit: commit }, layDl()?.phien_ban ?? ''), hoiDeploy(ten, commit))
   }
   return { dangGui, loi, xungDot, luu, tamDung, deploy }
 }
```

#### Modify `frontend/src/trang/TuDong.vue` — bản vá

```diff
--- a/frontend/src/trang/TuDong.vue
+++ b/frontend/src/trang/TuDong.vue
@@ -65,6 +65,7 @@
       </template>
     </DauTrang>
     <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
+    <p v-if="dl?.ly_do_deploy" class="loi" role="status">{{ dl.ly_do_deploy }}</p>
     <p v-if="g.loi.value" class="loi" role="alert">{{ g.loi.value }}</p>
     <template v-if="dl">
       <div v-for="b in bao" :key="b.tieuDe" class="the td-bao" :class="b.lop">
```

#### Modify `frontend/src/thanh/phe_duyet/TheSanSang.vue` — bản vá

```diff
--- a/frontend/src/thanh/phe_duyet/TheSanSang.vue
+++ b/frontend/src/thanh/phe_duyet/TheSanSang.vue
@@ -18,7 +18,7 @@
 const t = computed(() => sanSangDeploy(props.muc))
 const laDaiCa = computed(() => duocGhi(kho.trangThai))
 const lyDo = computed(() => khoaDeploy(props.muc, kho.tuDong, laDaiCa.value))
-const g = dungGhiTuDong(() => null, async () => emit('doi'), () => props.muc.du_an)
+const g = dungGhiTuDong(() => props.muc.chi_tiet, async () => emit('doi'), () => props.muc.du_an)
 </script>
 
 <template>
```

**GREEN:** tất cả test của task và hồi quy liên quan đạt, 0 dòng chặn mới; lỗi host không được tính là GREEN.

### Task 8: Kiểm tích hợp và nghiệm thu toàn bộ

Không thêm mã ở đây, không gọi các test hồi quy vốn xanh là RED. Trước hết chạy toàn bộ test đã thêm/sửa,
bộ báo tin, giới hạn dòng và vòng import; sau đó chạy cả bộ theo mục “Kiểm toàn bộ trước ghép”.
Đối chiếu Scenario ở cuối, mở giao diện dữ liệu giả dưới CSP thật. Cửa passkey phải kiểm thiếu/giả danh tính;
đối soát cùng mã/khác nội dung, restart sau rollback intent, và hai dự án phải được kiểm riêng.
Chỉ ghi kết quả đo. Không lấy fake OS làm bằng chứng R1–R5, không tự bật deploy sau khi test xanh.

## Cổng tay/chạy thật — Đại ca làm, không chạy trong phiên soạn

Các cổng sau không phải test unit, không tick nhờ validate hay Uq từng đạt G4. Mỗi kịch bản cần Đại ca cho phép
riêng theo AGENT_RULES §11. Ghi lệnh, giờ, repo/đích, SHA/lượt, kết quả và đường lui vào sổ tay chạy thật hiện có.
Không yêu cầu Đại ca đưa token, mật khẩu hay log thô vào chat.

| Cổng | Đại ca chuẩn bị/thực hiện | Đạt khi | Nếu chưa đạt |
|---|---|---|---|
| R0 — trước áp/ghép | Duyệt plan/review; trước áp đo baseline đúng HEAD; trước ghép chạy trọn plan và QC | N₀ toàn bộ xanh trước áp; RED → GREEN/QC trước ghép, không dòng chặn mới | Chỉ giữ tài liệu; không bật công tắc |
| R1 — GitHub | Trên repo nháp, Settings → Branches: chọn nhánh chính; required checks từ đúng app, strict/up-to-date, enforce admins; không bypass; không merge queue | Đọc luật bằng tài khoản trạm được; check thiếu/đỏ/pending, base đổi, draft/xung đột/bypass đều chặn; optional job lỗi không cản nếu required đủ | Giữ merge tay; không cấp admin để chữa lỗi đọc |
| R2 — Uq/M | Trên PR thử đã có Uq/QC đúng lượt, cho merge qua luồng trạm; làm M lỗi mặc dù H xanh; đổi tiêu chí hoặc lượt | H không thay kiểm M; M lỗi không deploy; cổng lỗi giữ đóng; spec S1 đổi S2 không gộp/giao con | Giữ M chờ; không lấy HEAD kế tiếp để lách |
| R3 — đích từng dự án | Chuẩn bị ba wrapper đúng hợp đồng, principal/quyền dự án, launchd đã cài; xác minh toàn bộ script/config nạp gián tiếp, owner/mode/ACL | Agent không sửa được đường điều khiển; trạm không chạy mã repo; dự án A không đổi dịch vụ/bản/quyền B; build cách ly và artifact đúng M | Không lưu bật deploy; thiếu đường riêng thì dừng tại “cần đường deploy riêng” |
| R4 — nền và rollback | Dựng bản nền L thủ công; giữ artifact/config; xác nhận tương thích dữ liệu; thử đưa bản lỗi M rồi quay về L trên đích thử | Dịch vụ trả đúng L và chức năng cốt lõi đạt; HTTP 200 của bản cũ không được ghi M đạt; hỏng lùi tắt/tạm dừng, không động DB | Chưa cho `san_sang=true`; không deploy đầu tiên |
| R5 — gián đoạn/quyền | Dừng trạm giữa lượt trước/sau chuyển bản; giả mất phản hồi/tác vụ còn chạy; thử Estop/tạm dừng, hai tab cũ, gửi lại mã; đối soát bằng passkey | Không lặp deploy/lùi; không chồng writer; Tiếp tục thường không xoá chốt; xác nhận đúng M/L và hết writer mới mở; không rò bí mật và tin không lặp | Giữ tạm dừng; Đại ca sửa đích, chỉ đọc để xác minh; không dùng sửa DB/xoá dấu làm đường tắt |

**R1 dùng cơ chế GitHub sẵn có, không dựng bộ CI thứ hai.** Adapter chỉ hỗ trợ classic branch protection đầy đủ
và đọc effective rules để từ chối merge queue. Repo chỉ có ruleset không tương thích hoặc gói không cho đọc/cấu hình
thì chờ merge tay. Đọc đủ trang rules bằng `gh api --paginate --slurp`, không tự viết vòng phân trang.
`gh pr checks --required` chọn đúng tập check; `--match-head-commit` khoá head PR;
nhánh có merge queue có thể bị gh tự đưa vào hàng đợi dù không truyền cờ auto, nên phải chặn trước.
Nguồn: [gh checks](https://cli.github.com/manual/gh_pr_checks),
[gh merge](https://cli.github.com/manual/gh_pr_merge),
[gh api](https://cli.github.com/manual/gh_api),
[REST rules/phân trang](https://docs.github.com/en/rest/repos/rules#get-rules-for-a-branch),
[REST branch protection](https://docs.github.com/en/rest/branches/branch-protection#get-branch-protection).

**R3 không phải tạo nền deploy mới.** Wrapper chỉ là đầu vào kín của đường triển khai đã có của dự án.
Bản executable/config tin cậy phải chạy tiếp đúng đích đã cấp; không được gọi shell/script từ checkout M để điều khiển
quyền cao. Không có script HR Codex trong dữ liệu đầu vào nên plan không bịa lệnh cài/chuyển/lùi dự án đó.
Cài user/quyền/launchd, nếu cần, là kịch bản tay riêng trước khi bật, không do task code tự làm.

**R4 phải làm trước lần bật đầu.** Chụp L từ ứng dụng đang phục vụ, không từ git HEAD. Thử chức năng cốt lõi cả khi
lên M lẫn khi về L. Đích giữ artifact/config L cho tới khi M kiểm đạt. Có migration/phá dữ liệu thì dừng, không
dùng bản sao DB để suy thành quyền restore. Sau hỏng, mã M vẫn ở Git; sửa bằng PR mới, không tự mở lại bead.

**R5 đối soát có hai lớp.** Người xác nhận đúng SHA thực tế; wrapper đọc đúng lượt chứng minh không còn writer và
bản đó hoạt động. Chỉ có một trong hai thì không mở. Khởi động lại launchd không tự chứng minh chuỗi đã thành công.
Nếu bản thực tế không phải M/L hoặc snapshot cũ thiếu ba lệnh, cổng đóng, cần kịch bản khôi phục tay riêng.

## Đối chiếu Scenario → bằng chứng

Các Scenario sau giữ nguyên hồi quy đã có; không chép lại toàn bộ mã của luồng không đổi:

| Nhóm Scenario | Test mới / hồi quy phải chạy |
|---|---|
| PR sai repo/đích/nguồn, head đổi sát merge, phản hồi mất, xác minh rồi đóng bead | `test_tu_merge.py`, `test_pr_merge.py`, `test_gh.py`, `test_tm20_github.py`, `test_tm20_doc_github.py` |
| QC cùng khe, sai lượt/tiêu chí/ref, lần mới lỗi, chỉ agent báo đạt | `test_tm20_bang_chung.py`, `test_tu_merge_xet.py`, `test_tu_merge_tuoi.py`, các test client/fencing Uq |
| Schema/xoá dữ liệu, file điều khiển, hai nút cột/hàng rào | `test_tu_merge_rao.py`, `test_deploy_cam.py`, `test_tu_merge.py`; R3 đo quyền gián tiếp |
| Spec duyệt S1, S2 hoặc lẫn mã; feature cha/con và escalation | `test_tu_merge_spec.py`, `test_tu_merge_con_feature.py`, `test_tu_merge_tuoi.py`; QĐ1 áp cả PR spec |
| Thiếu đường deploy/bản nền, hai đích, script gián tiếp | `test_tm20_duong.py`, `test_tm20_chuoi.py`; R3–R4 bắt buộc |
| M lỗi, N chen, artifact sai, nhiều bản, bật mới và retry mã | `test_tm20_ban.py`, `test_tm20_chuoi.py`, `test_deploy_race.py`, `test_deploy_cong_tac_v2.py` |
| Dừng giữa chuỗi, HTTP 200 sai bản, rollback lỗi/không rõ, hỏng ba lần | `test_tm20_chuoi.py`, `test_deploy_vong.py`, `test_deploy_chuoi.py`, R4–R5 |
| Restart sau chuyển bản, tác vụ từ xa còn chạy, đối soát | `test_tm20_tich_hop.py`, `test_tm20_cua.py`, R5 |
| Thiếu/giả danh tính, stale phiên bản, R mới, hai màn | `test_api_deploy.py`, `test_api_tu_dong.py`, `test_passkey_tm_tc.py`, frontend tests, CSP thật |
| Telegram lỗi, bí mật, giờ yên lặng, không trùng | `test_bao_tin_tu_dong.py`, `test_chong_on_tu_dong.py`, `test_deploy_ong.py`, R5 |

Không xoá bộ test P1/thu hồi/log hiện có. `test_deploy_vong`, `test_deploy_race`,
`test_deploy_cong_tac_v2` thay fixture và expectation của đường production đã bị QĐ2/QĐ3 bỏ:
không còn kỳ vọng worktree dưới tài khoản trạm, dùng HEAD mới nhất hoặc timeout phía gọi là đủ để lùi.
Kiểm P1/giết cây vẫn ở `test_deploy_lenh`, `test_chay_gioi_han` và bộ kiểm hiện hành; không coi mock là chứng cứ OS.

## Kiểm toàn bộ trước ghép

Thực hiện ở worktree task đã được phép code, sau Task 1–7 và kiểm Task 8; phiên soạn tài liệu không chạy đoạn này trên mã đề xuất.

```bash
tests/chan_host/chay.sh -q
cd frontend
npm run kiem
npm run build
npm run kiem-dist
```

Sau đó mở giao diện giả dưới CSP thật bằng runner đã ghi trong AGENT_RULES, kiểm console, hai nơi bấm Deploy,
CI không có nút, 409 vẫn giữ dữ liệu nhập, đối soát chỉ nhận bản đã quan sát. QC đối chiếu mọi dòng thêm với plan.
Không ghép nếu còn sai khác chưa giải thích hoặc test đỏ. Cổng R1–R5 chặn bật chạy thật/archive;
không buộc phải chạy tính năng chưa ghép vào main để được ghép mã có công tắc tắt.

Cập nhật nguồn sở hữu khi thực thi đã qua kiểm: ADR-0007/AGENT_RULES §11/PROJECT/ARCHITECTURE/
PRODUCT_ARCHITECTURE/FEATURE_SPEC chỉ đổi điểm dừng được phép; DEPLOY/sổ tay ghi đường triển khai thật và bằng chứng.
Phiên soạn không tự sửa những nguồn đó để tuyên bố tự merge đã có hiệu lực.

## Rủi ro còn lại

- Đã áp bản nháp và bản sửa lên bản sao tạm, chạy test mục tiêu và ca tái hiện review; chưa có baseline toàn bộ
  xanh hay rehearsal toàn bộ theo thứ tự task. Kết quả chi tiết: `REVIEW-CODEX.md`. Không coi kiểm một phần là ĐẠT.
- GitHub không cho khoá nguyên tử cả luật nhánh, head PR, công tắc cục bộ và đích deploy. Luật có thể bị quản trị viên
  đổi sau phép đọc. Tài khoản trạm không được bypass; R1 phải đo quyền và giữ bảo vệ tại repo thật.
- Branch protection và `gh --required` cần xác minh trên phiên bản gh/tài khoản/gói repo thực tế, kể cả app nguồn,
  branch mới và tình huống merge queue. Không tự sửa luật GitHub khi gặp lỗi đọc.
- Đường deploy thật, ACL/closure script, launchd nhãn/miền, artifact, build cách ly và phép thử chức năng của từng
  dự án chưa được cung cấp/đo. Ba wrapper và JSON chỉ là hợp đồng, không phải bằng chứng quyền OS hay phục hồi.
- Timeout/thu hồi dưới principal khác có thể không xác minh được; phải giữ “không rõ”, không ép thành lỗi đã lùi.
- Rollback chỉ đổi mã/artifact/config thuộc triển khai; dữ liệu sản xuất có thể không tương thích. R4 cần kiểm thật.
- Validate đúng OpenSpec 1.14.0 chưa chạy được: bản pin không có trong cache offline; PATH là 1.11.0, không dùng thay.
- Chưa kiểm lại reboot Uq; không suy từ dòng CURRENT_STATE lạc hậu hoặc từ một lần G4 đạt.

## Ghi chú triển khai

Chưa triển khai vào worktree, không commit. Review và bằng chứng tại [REVIEW-CODEX.md](../../REVIEW-CODEX.md).
Mã nguyên văn đã được gom theo bản cuối; chỉ bổ sung commit/số đo triển khai sau khi có kết quả thật.

# Bộ quản lý kiểm — Implementation Plan (TDD)

> **For agentic workers:** dùng `ai-skills:executing-plans`, áp tuần tự từng task và chạy test qua bộ chặn host.
> **DRAFT — review vòng 1, chưa được coi là sẵn sàng chạy thật.** Đây là plan, không phải xác nhận S6 đạt hoặc giấy phép cài/chạy thật.
> Phiên soạn chỉ áp tạm test/mã để đo rồi hoàn nguyên; không commit, không sửa CURRENT_STATE/handovers.

**Goal:** chuyển đường kiểm lại của sản phẩm khỏi phiên 501 sang LaunchDaemon nonroot `tram-quan-kiem`;
Uq giữ cổng/receipt, chạy mã dự án dưới `tram-kiem` + hồ sơ v2, mọi lỗi hoặc thu hồi chưa rõ đều đóng.

**Architecture:** trạm gửi bytes qua Unix socket, xác thực hai đầu bằng `getpeereid`; Uq nhận một lượt,
worker tin cậy cùng Uq điều phối `boc_luot`, dùng lại `CongLuot`, `cong_that`, `ban_chep`, P1 và bộ quan sát.
Root chỉ cài/gỡ. Không HTTP, hàng đợi bền, token IPC, helper root runtime hoặc dịch vụ đo thứ hai.

**Tech Stack:** Python 3.12/stdlib, macOS launchd/Seatbelt, pytest qua runner chặn host; không thêm gói.

**Nguồn:** D159, D160, D162 trong [quyết định tách phiên](../quyet-dinh/2026-10-18-tach-phien-kiem.md);
`/Users/dai-ca/Developer/Ben Station/.handover/thao-luan-phien-rieng/v3-codex.md` §5–7;
[plan siết đọc](2026-10-18-lat-siet-doc-kiem.md). Lời Đại ca 19/10 **làm thẳng** thắng bước đo riêng
ở v3 §7: toàn bộ bằng chứng Uq/system nằm trong **G4 của chính bản cài sản phẩm** bên dưới.

## Điều kiện ghép trước — D162 ngoài plan này

Ghép `code/siet-doc` trước khi code; đã đọc API trong worktree đó ngày 19/10.
`con_uid(uid, chup=chup_nhan, *, ten=None, ban=None, mot=mot_nhan, duong=duong_nhan)`
trả tàn dư; dùng `ten='tram-quan-kiem'` hoặc `'tram-kiem'`, build 24G90, không tự miễn khe chưa G5.
`NHOM_NEN` là nguồn chung của nhóm OS; không chép bộ lọc Apple hay sửa cơ chế kill trong plan này.
Không áp toàn file từ plan nếu đè thay đổi D162 mới ghép; đối chiếu các khối Modify trước khi áp.

## Global Constraints

- Mốc soạn `2c473ed`, worktree `plan/bo-quan-ly-kiem`, cây ban đầu sạch. Plan siết đọc đã có trong HEAD này;
  khi triển khai trên mốc khác phải ghép nó trước, đối chiếu diff và chạy lại test, không ghi đè thay đổi mới.
- Không sửa UID có sẵn. Uq khác root/501/503, nhóm riêng; trạm là thành viên nhóm socket nhưng 503/khe không phải.
  Dùng `NHOM_NEN` của D162 (12/61/701/100 trên 24G90), giữ nhóm OS; không thêm ACL cho Uq hay 503 vào nhà Đại ca.
- Cây Python kiểm root, hồ sơ/manifest v2 và nhóm riêng dùng lại lát trước. Không cho Uq import repo đang kiểm,
  không dùng Python trong nhà 501; root bundle được chụp từ checkout tin cậy khi cài.
- Cấm commit/push/bd ghi/mạng/sudo/launchctl ghi/Keychain/thay cấu hình thật trong phiên soạn. Toàn bộ lệnh G4
  là kịch bản để **Đại ca duyệt và chạy sau review/code**, không được agent tự chạy trong phiên viết plan.
- Từng file `tram/` ≤120 dòng, từng dòng ≤120 ký tự. Các file nhỏ chia theo ranh giới IPC, vòng đời, cài/gỡ;
  không xây framework cho nhiều loại worker.
- Uq là **một chủ cổng**: khoá daemon suốt đời + khoá một lượt; worker tin cậy của Uq được uỷ nhiệm ghi `ra()`.
  Trạm chỉ phản chiếu cổng qua IPC. Không một bản cổng local thứ hai có quyền quyết định chạy.
- Restart luôn đóng, không chỉ khi thấy receipt dở. Mở lại là thao tác riêng; quan sát/thu hồi chưa rõ thì giữ đóng.
  Worker Uq mồ côi sau crash chặn mở lại; không dùng kill theo UID Uq để chữa, không tự cấp root runtime.
- S6 vẫn đóng tới khi G4 có chứng cứ đủ. Không điền `BANG_CHUNG_LOGIN` bằng số đo cũ hay chỉ một ASID khác.

## Hợp đồng và giới hạn

| Thành phần | Hợp đồng |
|---|---|
| Cài/gỡ | CLI in kế hoạch, chờ đúng `dong-y`; `KeHoach/TaiNguyen/SoCai` R2. Sổ manager riêng trong `~/.tram/cai-quan-kiem/so-cai.jsonl`; migration sudoers cũ khoá/đối soát sổ cài thợ. |
| Runtime | `/usr/local/tram/quan-kiem` root:wheel; Python `-I`; cwd `/var/empty`; HOME/TRAM_HOME Uq `/private/var/db/tram-quan-kiem` 0700. Không token máy. |
| Socket | `/private/var/db/tram-quan-kiem-socket/dieu-khien.sock`; thư mục Uq 0750, socket Uq:nhóm-Uq 0660. Không dùng `/var/run` dễ mất sau reboot. Trạm kiểm từng cha không symlink/group-write/world-write. |
| Peer | Nhân trả euid; server chỉ nhận UID trạm, client chỉ nhận Uq. Không tin UID/đường/FD trong JSON. Không bảo vệ khỏi app khác cùng UID 501 đã được tin. |
| Frame | UInt32 big-endian + JSON ≤64 KiB, cấm khoá lạ/trùng; upload tuyệt đối 30 s, source ≤64 MiB, env tar ≤1 MiB; SHA-256 từng body. Không giải nén ở Uq. |
| Lượt | `id`, `giao_id`, `luot`, dự án, SHA commit/tree, digest policy+toolchain+profile v2, lệnh. ID ổn định theo giao/lượt/SHA; retry cùng fingerprint không chạy lần hai. |
| Policy | Root config đăng ký dự án/lệnh; Uq so digest và allowlist. Chụp `lenh_kiem_mac_dinh` + `lenh_cho_phep` từ `du-an/*.yaml`; G4 dùng tên dự án thật nhưng nguồn fixture giả và cùng policy. Đổi policy phải cài/đo lại. |
| Giới hạn | ≤20 lệnh, ≤1024 ký tự/lệnh; mỗi lệnh 900 s; worker **3300 s gồm quan sát trước, nhận cây, chạy, dọn và xác nhận sau**; cứu dọn 240 s riêng, primitive P1 có grace hữu hạn. Upload không cộng dồn vô hạn. |
| Trạng thái | Receipt fsync trước spawn; `dang-chay`, `xong` + `da_thu_hoi`, hoặc `dong`. Receipt không chứa body/env/stdout payload; kết quả lệnh giữ digest log. Không nhận stdout payload làm chứng nhận dọn. |
| Công bố | Client đối chiếu id/giao/lượt/SHA/fingerprint; trước ghi `kiem.lai`, transaction DB kiểm phiếu, lượt hiện hành và SHA code lần nữa. Kết quả muộn không được công bố. |
| Crash | Dấu bền trước worker, receipt dở/corrupt/restart => đóng. Lỗi kênh/estop/deadline huỷ worker và thu hồi 503; cleanup không rõ không trả pass. Không fallback chạy dưới 501. |

Không nhận tên UID, PID, profile, plist, đường log/đầu ra hay shell command để thực thi dưới Uq từ client.
Trạm xuất Git archive và env giả qua stdin; worker gọi extractor tin cậy dưới 503 + hồ sơ, kiểm tree trước env.
Giữ hạn giải nén 256 MiB/100.000 entries; cấm absolute/`..`/`.git`/hardlink/device/duplicate, symlink thoát cây.
`CongLuot` phía supervisor chỉ giữ trạng thái; quan sát có thể chạy lệnh được đưa vào worker có deadline.

### Bản đồ tác động

| Vùng | Thay đổi / phần giữ lại |
|---|---|
| `tram/kiem/ngoai_le_uid.py`, `tram/chu/nhom_rieng.py` | Dependency D162 ghép trước; chỉ dùng `con_uid(uid, ten=...)` và `NHOM_NEN`, không viết lại. Thu hồi vẫn giết toàn UID. |
| `tram/chu/` | Cài Uq/nhóm/bundle/plist/socket/runas; receipt membership; gỡ có thứ tự, không nhận tài nguyên lạ. Bỏ runas trực tiếp 501→503, không tự phục hồi đường này khi gỡ. |
| `tram/quan_kiem/` | Adapter IPC, receipt/vòng đời, nguồn/receiver, cài bằng chứng và harness G4 của đường sản phẩm. |
| `noi_that`, `tick_pipeline`, `kiem_san_sang`, `lenh` | Production nối client; `mo-cong-kiem` qua IPC; CLI nghiệm thu cũ ngừng chạy local. Injected adapter local còn cho unit test cũ, không được nối ở production. |
| `ban_chep`, `cong_that`, `CongLuot`, P1, `boc_luot` | Tái dùng primitives; không viết lại kill/thu hồi, parser lịch, cấu hình hồ sơ hay trình chạy lệnh. |
| `do_launchd_g4`, `mau_g4` | Thêm miền Uq/login/system và receipt exact labels; giữ parser chặt, không coi lỗi đọc miền là vắng. |

## Bảng G

| G | Kiểm bằng mã/test | Điều kiện đạt |
|---|---|---|
| G0 | Baseline + apply đúng mốc | Không trộn thay đổi khác; báo lỗi môi trường, không tự nới chặn host. |
| G1 | Cài/gỡ R2, quyền, không cài lúc lập kế hoạch | Nhận đúng tài nguyên; crash giữa create/receipt vẫn đối soát rồi gỡ đúng; không sửa/xoá tài nguyên lạ. |
| G2 | IPC/schema/peer/digest/replay | Không chạy request giả/sai/lặp khác nội dung; upload dở không chạy; không nhận đường/FD tuỳ ý. |
| G3 | Một cổng, deadline/cleanup/fencing | Lỗi, mất kênh, thu hồi chưa rõ, worker cũ => đóng; không có local fallback. |
| **G4** | **Bản thật: system + rào + canary + nhiều lượt + crash/reboot** | **Chạy kịch bản dưới đây, có bằng chứng người vận hành xác nhận; unit test không thay OS.** |
| G5 | Bản cài khớp bằng chứng | Build/máy, UID/nhóm, bundle/probe, launcher, sudo/PAM, hồ sơ và toolchain phải khớp fingerprint; đổi phải đo lại. |

## Môi trường và thứ tự TDD

```bash
export PYTHONPATH="$PWD"
export UV_CACHE_DIR=/tmp/quan-kiem-uv
export UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv'
export UV_NO_SYNC=1
```

Không sync/tải gói. Venv dùng chỉ đọc, import từ worktree. Áp task 1→6; trong mỗi task đặt test trước,
chạy RED, rồi đặt mã đúng đường chỉ rõ, chạy GREEN. Khối Python là **toàn bộ nội dung cuối**; khối diff là patch có đủ context trên HEAD, áp bằng `git apply`. Khi mốc đổi phải review diff thay vì chép đè.
Task 1–3 có RED đầu tiên ở collection vì module chưa tồn tại: ghi đúng loại lỗi, không gọi đó là assertion
đã chạy. Task 4–6 có bằng chứng RED hành vi riêng ở bản soạn cũ; phải đo lại sau sửa. Các con số GREEN cuối là phép chạy toàn bộ sau sửa.

## Task 1 — IPC nhỏ: schema, frame, peer hai đầu

**Files:**

- Create `tests/test_quan_kiem_giao_thuc.py`
- Create `tram/quan_kiem/__init__.py`
- Create `tram/quan_kiem/giao_thuc.py`
- Create `tram/quan_kiem/peer.py`

- [ ] **Step 1 — test nguyên văn:**

`tests/test_quan_kiem_giao_thuc.py`

```python
import hashlib
import io
import json
import struct
import pytest
from tram.quan_kiem.giao_thuc import doc, ghi, yeu_cau, fingerprint
from tram.quan_kiem.peer import xac_thuc


def mau():
    return dict(v=1, op='chay', id='a'*32, giao_id='giao-1', luot=1, du_an='repo',
                commit='b'*40, tree='c'*40, policy='d'*64, lenh=['python -m pytest'],
                nguon_n=3, nguon_sha=hashlib.sha256(b'abc').hexdigest(),
                env_n=0, env_sha=hashlib.sha256(b'').hexdigest(), dich='.env.testing')


class Ong:
    def __init__(self, data=b''):
        self.f = io.BytesIO(data)
    def recv(self, n):
        return self.f.read(min(n, 3))
    def sendall(self, data):
        self.f.write(data)
    def settimeout(self, t):
        assert 0 < t <= 30


def test_khung_doc_tung_manh():
    s = Ong()
    ghi(s, mau())
    s.f.seek(0)
    assert yeu_cau(doc(s)) == mau()


@pytest.mark.parametrize('doi', [dict(uid=501), dict(v=True), dict(luot=True), dict(luot=0),
    dict(nguon_n=67108865), dict(lenh=[]), dict(dich='../secret'), dict(id='../a'), dict(op='root')])
def test_tu_choi_du_lieu_sai(doi):
    with pytest.raises(ValueError):
        yeu_cau(mau() | doi)


def test_khoa_json_trung_va_upload_do():
    for raw in [b'{"v":1,"v":1}', b'{']:
        with pytest.raises(ValueError):
            doc(Ong(struct.pack('!I', len(raw)) + raw))
    with pytest.raises(OSError):
        doc(Ong(b'\0\0'))


def test_fingerprint_gan_moi_noi_dung():
    assert fingerprint(mau()) != fingerprint(mau() | {'tree': 'e'*40})


@pytest.mark.parametrize('uid', [0, 503, 504, 502])
def test_peer_gia_khong_tin_uid_client(uid):
    with pytest.raises(PermissionError):
        xac_thuc(object(), 501, lay=lambda s: (uid, 20))


def test_peer_dung():
    xac_thuc(object(), 501, lay=lambda s: (501, 20))


def test_getpeereid_stdlib_socketpair():
    import os
    import socket
    import sys
    from tram.quan_kiem.peer import danh_tinh
    if sys.platform != 'darwin':
        pytest.skip('ABI Darwin')
    a, b = socket.socketpair()
    try:
        assert danh_tinh(a) == (os.geteuid(), os.getegid())
        a.close()
        with pytest.raises(OSError):
            danh_tinh(a)
    finally:
        a.close()
        b.close()
```

- [ ] **Step 2 — chạy RED trước mã:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_giao_thuc.py
```

RED đã quan sát trong phiên soạn:

```text
ModuleNotFoundError: No module named 'tram.quan_kiem.giao_thuc' — lỗi collection, chưa chạy assertion.
```

- [ ] **Step 3 — mã nguyên văn:**

`tram/quan_kiem/__init__.py`

```python
"""Bộ quản lý kiểm riêng của miền system (D159/D160)."""
```

`tram/quan_kiem/giao_thuc.py`

```python
"""Khung JSON 64 KiB, byte nguồn riêng; thời hạn tuyệt đối, không pickle/shell/đường dẫn client."""
import hashlib
import json
import re
import struct
import time

from tram.kiem.moi_truong import loi_dich

KHUNG = 65536
NGUON = 64 * 1024 * 1024
ENV = 1024 * 1024
HAN_DOC = 30
HAN_LUOT = 3600
KHOA = {'v', 'op', 'id', 'giao_id', 'luot', 'du_an', 'commit', 'tree', 'policy', 'lenh',
        'nguon_n', 'nguon_sha', 'env_n', 'env_sha', 'dich'}


def bam(b):
    return hashlib.sha256(b).hexdigest()


def json_bytes(d):
    return json.dumps(d, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def fingerprint(d):
    return bam(json_bytes(d))


def nhan(s, n, het):
    ra = bytearray()
    while len(ra) < n:
        con = het - time.monotonic()
        if con <= 0:
            raise TimeoutError('het-han-doc')
        s.settimeout(min(HAN_DOC, con))
        k = s.recv(min(n - len(ra), 65536))
        if not k:
            raise OSError('upload-do')
        ra.extend(k)
    return bytes(ra)


def _cap(cap):
    if len(dict(cap)) != len(cap):
        raise ValueError('khoa-trung')
    return dict(cap)


def doc(s, *, het=None):
    het = time.monotonic() + HAN_DOC if het is None else het
    n, = struct.unpack('!I', nhan(s, 4, het))
    if not 0 < n <= KHUNG:
        raise ValueError('khung-qua-lon')
    try:
        return json.loads(nhan(s, n, het), object_pairs_hook=_cap)
    except (UnicodeError, ValueError):
        raise ValueError('json-sai') from None


def ghi(s, d):
    b = json_bytes(d)
    if len(b) > KHUNG:
        raise ValueError('khung-qua-lon')
    s.settimeout(HAN_DOC)
    s.sendall(struct.pack('!I', len(b)) + b)


def yeu_cau(d):
    if not isinstance(d, dict) or type(d.get('v')) is not int or d['v'] != 1:
        raise ValueError('phien-ban-sai')
    if d.get('op') in ('trang-thai', 'huy', 'mo'):
        if set(d) != {'v', 'op', 'id'}:
            raise ValueError('khoa-sai')
    elif d.get('op') != 'chay' or set(d) != KHOA:
        raise ValueError('khoa-sai')
    if not isinstance(d.get('id'), str) or not re.fullmatch('[a-f0-9]{32}', d['id']):
        raise ValueError('id-sai')
    if d['op'] != 'chay':
        return d
    for k in ('giao_id', 'du_an'):
        if not isinstance(d[k], str) or not re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}', d[k]):
            raise ValueError('danh-tinh-sai')
    for k in ('commit', 'tree', 'policy', 'nguon_sha', 'env_sha'):
        n = 40 if k in ('commit', 'tree') else 64
        if not isinstance(d[k], str) or not re.fullmatch('[a-f0-9]{%d}' % n, d[k]):
            raise ValueError('digest-sai')
    if type(d['luot']) is not int or not 1 <= d['luot'] <= 2**53:
        raise ValueError('luot-sai')
    for k, tran in (('nguon_n', NGUON), ('env_n', ENV)):
        if type(d[k]) is not int or not 0 <= d[k] <= tran:
            raise ValueError('do-dai-sai')
    if not isinstance(d['lenh'], list) or not 1 <= len(d['lenh']) <= 20 or any(
            not isinstance(x, str) or not 0 < len(x) <= 1024 for x in d['lenh']):
        raise ValueError('lenh-sai')
    if loi_dich(d['dich']):
        raise ValueError('dich-sai')
    return d


def digest_policy(lenh, mac_dinh=()):
    from tram.kiem.toolchain import manifest
    from tram.tho.quyen_kiem import PHIEN_BAN_HO_SO
    return fingerprint({'lenh': lenh, 'mac_dinh': list(mac_dinh), 'toolchain': manifest(), 'ho_so': PHIEN_BAN_HO_SO})
```

macOS: CPython không có `socket.socket.getpeereid`; dùng `ctypes` stdlib gọi libSystem bên dưới.
Không thêm gói; không dùng Linux `SO_PEERCRED`. SDK Darwin có `LOCAL_PEERCRED=1`, nhưng không tự suy
layout `xucred` bằng `struct` khi đã có API `getpeereid`. Test socketpair kiểm UID/GID thật của tiến trình
hiện tại và FD đóng; G4 vẫn phải kiểm peer khác UID. `launchd.plist(5)` cục bộ xác nhận ba khoá
UserName/GroupName/SessionCreate; khoá session không thay quan sát vòng đời.

`tram/quan_kiem/peer.py`

```python
"""macOS getpeereid: nhân cung cấp euid/egid; không nhận danh tính từ JSON."""
import ctypes
import os
import stat
from pathlib import Path


def danh_tinh(s):
    lib = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
    u, g = ctypes.c_uint(), ctypes.c_uint()
    lib.getpeereid.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
    lib.getpeereid.restype = ctypes.c_int
    if lib.getpeereid(s.fileno(), ctypes.byref(u), ctypes.byref(g)):
        raise OSError('khong-doc-duoc-peer')
    return u.value, g.value


def xac_thuc(s, uid, *, lay=danh_tinh):
    if type(uid) is not int or uid <= 0 or lay(s)[0] != uid:
        raise PermissionError('peer-sai')


def duong_socket(p: Path, uid: int, gid: int):
    for cha in p.parents:
        st = cha.lstat()
        if not stat.S_ISDIR(st.st_mode) or st.st_uid not in (0, uid) or st.st_mode & 0o022:
            raise PermissionError('cha-socket-sai')
    st = p.lstat()
    if not stat.S_ISSOCK(st.st_mode) or st.st_uid != uid or st.st_gid != gid or stat.S_IMODE(st.st_mode) != 0o660:
        raise PermissionError('socket-sai')
```

- [ ] **Step 4 — GREEN, rồi kiểm hồi quy cuối plan:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_giao_thuc.py
```

## Task 2 — Một cổng, receipt và thu hồi có hạn

**Files:**

- Create `tests/test_quan_kiem_vong.py`
- Create `tests/test_quan_kiem_thuc_thi.py`
- Create `tram/quan_kiem/vong.py`
- Create `tram/quan_kiem/thuc_thi.py`
- Create `tram/quan_kiem/cong.py`

- [ ] **Step 1 — test nguyên văn:**

`tests/test_quan_kiem_vong.py`

```python
import json
import pytest
from tram.giao_viec.cong_luot import CongLuot, CongDong
from tram.quan_kiem.vong import QuanKiem
from test_quan_kiem_giao_thuc import mau


def tao(tmp_path, chay=None):
    c = CongLuot(tmp_path / 'cong.json', lambda: None, [], ngu=lambda n: None)
    c.mo_lai()
    def worker(d, a, e, huy):
        r = chay(d, a, e, huy) if chay else {'dat': True, 'ket_qua': []}
        c.ra(d['id'])
        return r
    q = QuanKiem(tmp_path, c, worker)
    return q, c


def test_replay_khong_chay_lai(tmp_path):
    calls = []
    q, c = tao(tmp_path, lambda *a: calls.append(a) or {'dat': True, 'ket_qua': []})
    a = q.chay(mau(), b'abc', b'', lambda: False)
    assert q.chay(mau(), b'abc', b'', lambda: False) == a
    assert len(calls) == 1
    with pytest.raises(ValueError, match='id-khac-noi-dung'):
        q.chay(mau() | {'luot': 2}, b'abc', b'', lambda: False)


def test_loi_va_restart_khong_tu_mo(tmp_path):
    def hong(*a):
        raise OSError('khong-duoc-lo-noi-dung')
    q, c = tao(tmp_path, hong)
    with pytest.raises(OSError):
        q.chay(mau(), b'abc', b'', lambda: False)
    assert c.trang_thai()['trang_thai'] == 'dong'
    QuanKiem(tmp_path, c, hong)
    assert c.trang_thai()['trang_thai'] == 'dong'
    assert 'khong-duoc-lo' not in (tmp_path / 'luot' / ('a'*32 + '.json')).read_text()


def test_crash_sau_nhan(tmp_path):
    q, c = tao(tmp_path)
    q.ghi(mau()['id'], {'fingerprint': 'd', 'trang_thai': 'dang-chay'})
    QuanKiem(tmp_path, c, lambda *a: None)
    assert c.trang_thai()['trang_thai'] == 'dong'


def test_digest_sai_khong_chay(tmp_path):
    q, c = tao(tmp_path, lambda *a: pytest.fail('khong duoc spawn'))
    with pytest.raises(ValueError):
        q.chay(mau(), b'sai', b'', lambda: False)


def test_huy_chi_dung_luot(tmp_path):
    q, c = tao(tmp_path)
    assert q.huy('b'*32) is False
    q.dang = 'a'*32
    assert q.huy('b'*32) is False
    assert q.huy('a'*32) is True
    assert q.dung.is_set()
```

`tests/test_quan_kiem_thuc_thi.py`

```python
import pytest
from types import SimpleNamespace
from tram.quan_kiem.thuc_thi import thuc_thi, chay_con


def test_huy_giu_dau_va_don_co_han(tmp_path, monkeypatch):
    import tram.quan_kiem.thuc_thi as m
    calls = []
    def chay(mode, p, han, huy, **kw):
        calls.append((mode, han))
        if mode == 'luot':
            raise TimeoutError()
    monkeypatch.setattr(m, 'chay_con', chay)
    with pytest.raises(TimeoutError):
        thuc_thi({'id': 'a'*32}, b'', b'', lambda: True, cfg={'home': str(tmp_path)}, pk=None)
    assert calls == [('luot', 3300), ('don', 240)]
    assert (tmp_path / 'kiem-lai.dong').exists()


def test_loi_spawn_van_thu_hoi_chu(monkeypatch):
    import tram.quan_kiem.thuc_thi as m
    calls = []
    monkeypatch.setattr(m, 'thu_hoi_con_lai', lambda chu: calls.append(tuple(chu)) or True)
    def loi(*a, chu, **kw):
        chu.append('da-spawn')
        raise OSError()
    with pytest.raises(OSError):
        chay_con('luot', 'x', 1, lambda: False, cfg=dict(python='p', entry='e', home='h'),
                 pk=SimpleNamespace(kill_nhom=lambda *a: None), khoi=loi)
    assert calls == [('da-spawn',)]


def test_worker_cu_sau_crash_chan_mo_cong(monkeypatch):
    import tram.quan_kiem.cong as m
    from tram.kiem.cay_tien_trinh import TienTrinh
    ds = [TienTrinh(10, 1, 10, 504, 504, 1), TienTrinh(11, 10, 11, 504, 504, 2)]
    monkeypatch.setattr(m.os, 'getpid', lambda: 11)
    monkeypatch.setattr(m.os, 'getppid', lambda: 10)
    monkeypatch.setattr(m.os, 'getuid', lambda: 504)
    monkeypatch.setattr(m, 'con_uid', lambda *a, **kw: ds)
    monkeypatch.setattr(m, 'mot_nhan', lambda pid: next(t for t in ds if t.pid == pid))
    m.quan_uq()
    ds.append(TienTrinh(12, 1, 12, 504, 504, 3))
    with pytest.raises(OSError, match='ngoai-luot'):
        m.quan_uq()
```

- [ ] **Step 2 — chạy RED trước mã:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_vong.py tests/test_quan_kiem_thuc_thi.py
```

RED đã quan sát trong phiên soạn:

```text
ModuleNotFoundError: No module named 'tram.quan_kiem.vong' — lỗi collection.
```

- [ ] **Step 3 — mã nguyên văn:**

`tram/quan_kiem/vong.py`

```python
"""Một chủ giữ cổng và receipt; không hàng đợi, không tự mở sau crash."""
import json
import os
import threading
from pathlib import Path

from tram.giao_viec.cong_luot import CongDong
from tram.quan_kiem.giao_thuc import bam, fingerprint, yeu_cau


class QuanKiem:
    def __init__(self, goc, cong, thuc_thi, mo_that=None):
        self.goc, self.cong, self.thuc_thi = Path(goc), cong, thuc_thi
        self.mo_that = mo_that or cong.mo_lai
        self.khoa, self.dung, self.dang = threading.Lock(), threading.Event(), None
        (self.goc / 'luot').mkdir(mode=0o700, exist_ok=True)
        for p in (self.goc / 'luot').glob('*.json'):
            try:
                if json.loads(p.read_bytes())['trang_thai'] == 'dang-chay':
                    self.cong.dong('restart-giua-luot')
            except (ValueError, KeyError, OSError):
                self.cong.dong('receipt-hong')
        if (self.goc / 'kiem-lai.dong').exists():
            self.cong.dong('han-tong-chua-don')

    def ghi(self, id_, d):
        p = self.goc / 'luot' / (id_ + '.json')
        tam = p.with_suffix('.tam')
        with open(tam, 'w', encoding='utf-8') as f:
            json.dump(d, f, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tam, p)
        fd = os.open(p.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def trang_thai(self, id_):
        p = self.goc / 'luot' / (id_ + '.json')
        try:
            return json.loads(p.read_bytes())
        except FileNotFoundError:
            return {'trang_thai': 'khong-co', 'cong': self.cong.trang_thai()['trang_thai']}

    def huy(self, id_):
        if id_ != self.dang:
            return False
        self.dung.set()
        return True

    def dong(self):
        self.dung.set()
        if self.khoa.acquire(blocking=False):
            try:
                self.cong.dong('loi-kenh')
            finally:
                self.khoa.release()

    def mo(self):
        if not self.khoa.acquire(blocking=False):
            raise OSError('dang-ban')
        try:
            self.mo_that()
        except BaseException:
            self.cong.dong('mo-lai-chua-ro')
            raise
        finally:
            self.khoa.release()

    def chay(self, d, nguon, env, mat_kenh):
        yeu_cau(d)
        if not self.khoa.acquire(blocking=False):
            raise OSError('dang-ban')
        fp = fingerprint(d)
        try:
            cu = self.trang_thai(d['id'])
            if cu['trang_thai'] != 'khong-co':
                if cu['fingerprint'] != fp:
                    raise ValueError('id-khac-noi-dung')
                return cu
            if len(nguon) != d['nguon_n'] or bam(nguon) != d['nguon_sha'] or \
                    len(env) != d['env_n'] or bam(env) != d['env_sha']:
                raise ValueError('digest-sai')
            self.cong.vao(d['id'])
            r = {'fingerprint': fp, 'trang_thai': 'dang-chay',
                 'id': d['id'], 'giao_id': d['giao_id'], 'luot': d['luot'], 'commit': d['commit']}
            self.ghi(d['id'], r)
            self.dang = d['id']
            self.dung.clear()
            try:
                kq = self.thuc_thi(d, nguon, env, lambda: self.dung.is_set() or mat_kenh())
                if self.cong.trang_thai()['trang_thai'] != 'mo':
                    raise CongDong('worker-chua-xac-nhan-don')
                r |= {'trang_thai': 'xong', 'ket_qua': kq, 'da_thu_hoi': True}
                self.ghi(d['id'], r)
                return r
            except BaseException:
                self.cong.dong('loi-luot')
                self.ghi(d['id'], r | {'trang_thai': 'dong', 'loi': 'loi-luot'})
                raise
            finally:
                self.dang = None
        finally:
            self.khoa.release()
```

`tram/quan_kiem/thuc_thi.py`

```python
"""Một hạn worker 3300 s, thu hồi 240 s; giữ dấu bền nếu bất kỳ bước nào chưa rõ."""
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

from tram.kiem.gui_tin import gop_kill, kill_cuc_bo
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.kiem.vong_doi import khoi_chay


def chay_con(mode, p, han, huy, *, cfg, pk, khoi=khoi_chay, dong_ho=time.monotonic):
    chu, het = [], dong_ho() + han
    try:
        n = khoi([cfg['python'], '-I', cfg['entry'], mode, str(p)], chu=chu,
                 kill=gop_kill(pk.kill_nhom, kill_cuc_bo), stdin=subprocess.DEVNULL,
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                 env={'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'HOME': cfg['home'],
                      'TRAM_HOME': cfg['home']}, cwd='/var/empty')
        while (ma := n.cho(0.1)) is None:
            if huy() or dong_ho() >= het:
                raise TimeoutError('huy-hoac-het-han')
        if ma != 0 or huy():
            raise OSError('luot-loi')
    finally:
        if not thu_hoi_con_lai(chu):
            raise OSError('thu-hoi-chua-ro')


def thuc_thi(d, nguon, env, huy, *, cfg, pk, thu_hoi=None, khoi=khoi_chay, dong_ho=time.monotonic):
    home, dau = Path(cfg['home']), Path(cfg['home']) / 'kiem-lai.dong'
    os.close(os.open(dau, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600))
    with tempfile.TemporaryDirectory(dir=home, prefix='nhan-') as tam:
        p = Path(tam)
        (p / 'yeu-cau.json').write_text(json.dumps(d))
        (p / 'nguon').write_bytes(nguon)
        (p / 'env').write_bytes(env)
        try:
            chay_con('luot', p, 3300, huy, cfg=cfg, pk=pk, khoi=khoi, dong_ho=dong_ho)
            r = json.loads((p / 'ket-qua.json').read_bytes())
        except BaseException:
            chay_con('don', d['id'], 240, lambda: False, cfg=cfg, pk=pk, khoi=khoi, dong_ho=dong_ho)
            raise
        dau.unlink()
        return r


def mo_that(*, cfg, pk):
    chay_con('mo', '0'*32, 240, lambda: False, cfg=cfg, pk=pk)
    (Path(cfg['home']) / 'kiem-lai.dong').unlink(missing_ok=True)
```

`tram/quan_kiem/cong.py`

```python
"""Dùng lại quan sát/thu hồi hiện hành; không cho Uq vào repo hoặc env của trạm."""
import os
import json
import re
from functools import partial
from pathlib import Path

from tram.giao_viec.ban_chep import don_ban
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.ngu_canh_kiem import ngu_canh_hien_hanh
from tram.giao_viec.cong_luot import CongLuot
from tram.giao_viec.cong_that import doc_tep_root, thu_hoi_theo_uid
from tram.giao_viec.launchd_kiem import doc_launchd
from tram.giao_viec.quan_sat_kiem import tien_trinh, tep_ngoai, goc_rong, cron_at
from tram.kiem.kiem_python import kiem_prefix
from tram.kiem.ngoai_le_uid import con_uid
from tram.kiem.bang_tien_trinh import mot_nhan
from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, ho_so_tu_manifest


def ho_so(c):
    m, hs = ho_so_tu_manifest(doc_tep_root(MANIFEST_KIEM))
    if m['goc'] != c['goc'] or m['tram_home'] != c['home_tram'] or doc_tep_root(HO_SO_KIEM) != hs:
        raise ValueError('ho-so-khac-ban-cai')


def dung(c, pk, nc, *, quan_sat=True):
    g = Path(c['goc'])
    return CongLuot(Path(c['home']) / 'cong.json', partial(thu_hoi_theo_uid, pk), [
        quan_uq, kiem_prefix, partial(ho_so, c), partial(tien_trinh, pk.ten), partial(tep_ngoai, pk.ten, g),
        partial(goc_rong, g), partial(cron_at, pk),
        partial(doc_launchd, pk, ngu_canh=lambda ten: nc, bang_chung=frozenset({nc}))] if quan_sat else [])


def quan_uq():
    """Worker cũ sau crash không được sống cạnh daemon/lượt mới; không tự kill Uq theo UID."""
    toi, cha, uid = os.getpid(), os.getppid(), os.getuid()
    ds = con_uid(uid, ten='tram-quan-kiem')
    theo = {t.pid: t for t in ds}
    if set(theo) != {toi, cha} or theo[toi].ppid != cha or theo[cha].ppid != 1:
        raise OSError('Uq-con-tien-trinh-ngoai-luot')
    if any(t.uid != uid or t.ruid != uid or mot_nhan(t.pid) != t for t in ds):
        raise OSError('Uq-danh-tinh-da-doi')

def phuc_hoi(c, mode, id_):
    pk = tu_cach_ly('user:tram-kiem')
    ids = [id_]
    if mode == 'mo':
        ids = []
        for p in (Path(c['home']) / 'luot').glob('*.json'):
            d = json.loads(p.read_bytes())
            if d['trang_thai'] in ('dang-chay', 'dong'):
                ids.append(p.stem)
    thu_hoi_theo_uid(pk)
    for i in ids:
        if not re.fullmatch('[a-f0-9]{32}', i):
            raise ValueError('receipt-id-sai')
        wt = Path(c['goc']) / ('luot-' + i)
        don_ban(wt, boc=pk.boc_luot(wt), kill=pk.kill_nhom)
    if mode == 'mo':
        dung(c, pk, ngu_canh_hien_hanh(pk.ten)).mo_lai()
```



- [ ] **Step 4 — GREEN, rồi kiểm hồi quy cuối plan:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_vong.py tests/test_quan_kiem_thuc_thi.py
```

Test worker Uq dùng `cong.py`; dependency import `cau_hinh/bang_chung` chỉ nạp ở runtime task 3.

## Task 3 — Nguồn qua bytes, worker 503 và daemon system

**Files:**

- Create `tests/test_quan_kiem_nhan.py`
- Create `tram/quan_kiem/nhan.py`
- Create `tram/quan_kiem/nguon.py`
- Create `tram/quan_kiem/luot.py`
- Create `tram/quan_kiem/dich_vu.py`
- Create `tram/quan_kiem/client.py`
- Create `tram/quan_kiem/cau_hinh.py`
- Create `tram/quan_kiem/bang_chung.py`
- Create `tram/quan_kiem/chay.py`

- [ ] **Step 1 — test nguyên văn:**

`tests/test_quan_kiem_nhan.py`

```python
import io
import tarfile
import pytest
from tram.quan_kiem.nhan import giai_nen


def tar(ten, kind=tarfile.REGTYPE, link=''):
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode='w') as f:
        t = tarfile.TarInfo(ten)
        t.type, t.linkname = kind, link
        t.size = 1 if kind == tarfile.REGTYPE else 0
        f.addfile(t, io.BytesIO(b'x') if t.size else None)
    return b.getvalue()


def test_nhan_file_binh_thuong(tmp_path):
    giai_nen(io.BytesIO(tar('a')), tmp_path)
    assert (tmp_path / 'a').read_bytes() == b'x'


@pytest.mark.parametrize('ten,kind,link', [('../a', tarfile.REGTYPE, ''),
    ('/tmp/a', tarfile.REGTYPE, ''), ('.git/config', tarfile.REGTYPE, ''),
    ('a', tarfile.SYMTYPE, '/tmp'), ('a', tarfile.LNKTYPE, '../x'), ('dev', tarfile.CHRTYPE, '')])
def test_nguon_khong_thoat_cay(tmp_path, ten, kind, link):
    with pytest.raises(ValueError):
        giai_nen(io.BytesIO(tar(ten, kind, link)), tmp_path)
    assert list(tmp_path.iterdir()) == []
```

- [ ] **Step 2 — chạy RED trước mã:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_nhan.py
```

RED đã quan sát trong phiên soạn:

```text
ModuleNotFoundError: No module named 'tram.quan_kiem.nhan' — lỗi collection.
```

- [ ] **Step 3 — mã nguyên văn:**

`tram/quan_kiem/nhan.py`

```python
"""Chỉ gọi dưới tram-kiem + boc_luot; Uq không phân tích archive."""
import sys
import tarfile
from pathlib import Path, PurePosixPath


def giai_nen(nguon, dich):
    with tarfile.open(fileobj=nguon, mode='r|') as t:
        tong, dem, da = 0, 0, set()
        for m in t:
            p = PurePosixPath(m.name)
            tong, dem = tong + m.size, dem + 1
            if p.is_absolute() or '..' in p.parts or '.git' in p.parts or m.name in da or \
                    tong > 256 * 1024 * 1024 or dem > 100000 or not (m.isfile() or m.isdir() or m.issym()):
                raise ValueError('archive-khong-an-toan')
            if m.issym() and (PurePosixPath(m.linkname).is_absolute() or '..' in PurePosixPath(m.linkname).parts):
                raise ValueError('link-khong-an-toan')
            da.add(m.name)
            t.extract(m, dich, filter='data')


if __name__ == '__main__':
    giai_nen(sys.stdin.buffer, Path(sys.argv[1]))
```

`tram/quan_kiem/nguon.py`

```python
"""Phía 501 chỉ xuất bytes có giới hạn; nguồn git có chủ P1, env kín và tar tất định."""
import io
import os
import selectors
import stat
import tarfile
import time

from tram.giao_viec.cay_kiem import nguon_archive, loi_cau_hinh_kho, loi_dich_trong_cay
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.quan_kiem.giao_thuc import NGUON, ENV


def archive(kho, sha):
    if loi_cau_hinh_kho(kho):
        raise ValueError('kho-co-filter')
    chu, ra = [], bytearray()
    try:
        n = nguon_archive(kho, sha, chu=chu)
        het = time.monotonic() + 120
        with selectors.DefaultSelector() as sel:
            sel.register(n.p.stdout, selectors.EVENT_READ)
            while time.monotonic() < het:
                if not sel.select(min(0.2, max(0, het - time.monotonic()))):
                    continue
                b = os.read(n.p.stdout.fileno(), 65536)
                if not b:
                    break
                ra.extend(b)
                if len(ra) > NGUON:
                    raise ValueError('nguon-qua-lon')
            else:
                raise TimeoutError('nguon-qua-han')
        if n.cho(max(0, het - time.monotonic())) != 0:
            raise OSError('archive-loi')
        return bytes(ra)
    finally:
        for n in chu:
            n.p.stdout.close()
        if not thu_hoi_con_lai(chu):
            raise OSError('nguon-chua-thu-hoi')


def moi_truong(kho, sha, mt):
    if mt is None or loi_dich_trong_cay(kho, sha, mt.dich):
        raise ValueError('thieu-moi-truong-kiem')
    fd = os.open(mt.file, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as f:
        st = os.fstat(f.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_mode & 0o077 or st.st_size > ENV - 10240:
            raise ValueError('env-khong-kin')
        data = f.read(ENV)
    if len(data) > ENV - 10240:
        raise ValueError('env-qua-lon')
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode='w') as t:
        m = tarfile.TarInfo(mt.dich)
        m.size, m.mode, m.mtime = len(data), 0o600, 0
        t.addfile(m, io.BytesIO(data))
    return b.getvalue()
```

`tram/quan_kiem/luot.py`

```python
"""Lượt tin cậy Uq; mọi chạm cây dự án đều qua boc_luot dưới tram-kiem."""
import json
from pathlib import Path

from tram.cau_hinh.lenh import khop_bat_ky
from tram.giao_viec.ban_chep import _chay, don_ban, ten_ban_chep, CayKhacNguon
from tram.giao_viec.repo_ban_chep import lenh_repo, lenh_cay
from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem
from tram.kiem.toolchain import PYTHON


NHAN = '/usr/local/tram/quan-kiem/tram/quan_kiem/nhan.py'


def chay_luot(d, nguon, env_tar, *, pk, goc, log, policy, thu_hoi, cfg=None):
    wt = Path(goc) / ('luot-' + d['id'])
    boc, kill = pk.boc_luot(wt), pk.kill_nhom
    thu_hoi()
    try:
        _chay(boc(['/bin/mkdir', str(wt)]), kill=kill, check=True)
        _chay(boc(['/bin/mkdir', '-m', '700', f'{wt}.nha', f'{wt}.nha/tmp']), kill=kill, check=True)
        argv = boc([f'{PYTHON}/bin/python3.12', '-I', '-c', Path(NHAN).read_text(), str(wt)])
        _chay(argv, kill=kill, input=nguon, check=True)
        for a in lenh_repo(wt).values():
            _chay(boc(a), kill=kill, check=True)
        r = _chay(boc(lenh_cay(wt)), kill=kill, check=True)
        if r.stdout.decode('ascii').strip() != d['tree']:
            raise CayKhacNguon('cay-khac-nguon')
        _chay(argv, kill=kill, input=env_tar, check=True)
        if cfg and cfg['g4']:
            from tram.quan_kiem.doi_chung_g4 import doi_chung
            doi_chung(cfg, pk, wt, d['id'])
        env = moi_truong_kiem({}, {'HOME': f'{wt}.nha', 'TMPDIR': f'{wt}.nha/tmp'})
        ket = []
        for i, lenh in enumerate(d['lenh']):
            kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, policy), cwd=wt, env=env, boc=boc, kill=kill,
                              log=Path(log) / f'{d["id"]}-{i}.log', thoi_gian_cho=900)
            if not kq.da_thu_hoi:
                raise OSError('thu-hoi-chua-ro')
            k = kq.sang_lenh_kiem()
            k['tom_tat'] = ''
            ket.append(k)
        return {'dat': bool(ket) and all(k['ket_qua'] == 'pass' for k in ket), 'ket_qua': ket}
    finally:
        don_ban(wt, boc=boc, kill=kill, don_sach=thu_hoi)


def worker(p, cfg):
    from tram.giao_viec.principal_kiem import tu_cach_ly
    from tram.giao_viec.cong_that import thu_hoi_theo_uid
    pk = tu_cach_ly('user:tram-kiem')
    d = json.loads((p / 'yeu-cau.json').read_bytes())
    from tram.quan_kiem.cong import dung
    from tram.giao_viec.ngu_canh_kiem import ngu_canh_hien_hanh
    cong = dung(cfg, pk, ngu_canh_hien_hanh(pk.ten))
    if cong.trang_thai() != {'trang_thai': 'dang-chay', 'luot': d['id']}:
        raise OSError('cong-khong-khop-luot')
    for q in cong.quan_sat:
        q()
    r = chay_luot(d, (p / 'nguon').read_bytes(), (p / 'env').read_bytes(), pk=pk,
                 goc=cfg['goc'], log=cfg['home'] + '/log', policy=cfg['policy'][d['du_an']]['cho_phep'],
                 thu_hoi=lambda: thu_hoi_theo_uid(pk), cfg=cfg)
    cong.ra(d['id'])
    (p / 'ket-qua.json').write_text(json.dumps(r))
```

`tram/quan_kiem/dich_vu.py`

```python
"""Socket cục bộ; hai kết nối tối đa để huỷ/trạng thái không bị lượt đang chạy chặn."""
import os
import select
import socket
import threading
import time
from pathlib import Path

from tram.cau_hinh.lenh import khop_bat_ky
from tram.quan_kiem.giao_thuc import digest_policy, doc, ghi, yeu_cau, nhan, fingerprint, HAN_DOC
from tram.quan_kiem.peer import xac_thuc


def phuc_vu(s, q, c):
    try:
        xac_thuc(s, c['uid_tram'])
        het = time.monotonic() + HAN_DOC
        d = yeu_cau(doc(s, het=het))
        if d['op'] == 'trang-thai':
            ghi(s, q.trang_thai(d['id']))
        elif d['op'] == 'huy':
            ghi(s, {'huy': q.huy(d['id'])})
        elif d['op'] == 'mo':
            q.mo()
            ghi(s, {'cong': q.cong.trang_thai()['trang_thai']})
        else:
            if c['g4'] and not d['giao_id'].startswith('g4-'):
                raise ValueError('g4-chi-du-lieu-gia')
            policy = c['policy'].get(d['du_an'])
            if not policy or d['policy'] != digest_policy(policy['cho_phep'], policy['mac_dinh']) or any(
                    not khop_bat_ky(x, policy['cho_phep']) for x in d['lenh']) or any(
                    x not in d['lenh'] for x in policy['mac_dinh']):
                raise ValueError('policy-sai')
            nguon, env = nhan(s, d['nguon_n'], het), nhan(s, d['env_n'], het)
            def mat_kenh():
                return bool(select.select([s], [], [], 0)[0])
            ghi(s, q.chay(d, nguon, env, mat_kenh))
    except (Exception, KeyboardInterrupt):
        q.dong()
        try:
            ghi(s, {'loi': 'khong-cong-nhan'})
        except OSError:
            pass
    finally:
        s.close()


def nghe(q, c):
    p = Path(c['socket'])
    if os.path.lexists(p):
        st = p.lstat()
        import stat
        if not stat.S_ISSOCK(st.st_mode) or st.st_uid != os.getuid():
            raise PermissionError('socket-cu-khong-thuoc-quan-ly')
        p.unlink()
    cho = threading.BoundedSemaphore(2)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(str(p))
        os.chown(p, -1, c['gid_socket'])
        os.chmod(p, 0o660)
        server.listen(2)
        while True:
            s, _ = server.accept()
            if not cho.acquire(blocking=False):
                s.close()
                continue
            def mot(s=s):
                try:
                    phuc_vu(s, q, c)
                finally:
                    cho.release()
            threading.Thread(target=mot, daemon=False).start()
```

`tram/quan_kiem/client.py`

```python
"""Trạm gọi Uq; mất kênh không rơi về sudo từ 501. ID ổn định qua retry."""
import select
import socket
import time
from pathlib import Path

from tram.giao_viec.kiem_lai import KetQuaKiemLai
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cay_kiem import cay_goc
from tram.kiem.diff import diff_cham_cam
from tram.quan_kiem.cau_hinh import nap
from tram.quan_kiem.giao_thuc import digest_policy, ghi, doc, bam, fingerprint, HAN_LUOT, yeu_cau
from tram.quan_kiem.nguon import archive, moi_truong
from tram.quan_kiem.peer import duong_socket, xac_thuc


def gui(d, nguon=b'', env=b'', *, cau_hinh=nap):
    c = cau_hinh()
    p = Path(c['socket'])
    duong_socket(p, c['uid_quan'], c['gid_socket'])
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(30)
            s.connect(str(p))
            xac_thuc(s, c['uid_quan'])
            ghi(s, d)
            s.sendall(nguon)
            s.sendall(env)
            het = time.monotonic() + HAN_LUOT + 300
            while not select.select([s], [], [], 0.2)[0]:
                from tram.duong_dan import tram_home
                if time.monotonic() >= het or (d['op'] == 'chay' and (tram_home() / 'estop').exists()):
                    raise TimeoutError('estop-hoac-het-han')
            return doc(s, het=het)
    except (OSError, ValueError):
        raise LoiBanChep('bo-quan-ly-khong-tra-ket-qua-hop-le') from None


class CongTuXa:
    def trang_thai(self):
        r = gui({'v': 1, 'op': 'trang-thai', 'id': '0'*32})
        return {'trang_thai': r.get('cong', 'dong')}

    def mo_lai(self):
        if gui({'v': 1, 'op': 'mo', 'id': '0'*32}) != {'cong': 'mo'}:
            raise LoiBanChep('cong-van-dong')


def kiem_tu_xa(kho_git, du_an, *, giao_id, luot, commit, lenh_kiem, lenh_cho_phep, chay_lenh,
                them_cam=(), goi=gui, **kw):
    cham = diff_cham_cam(kho_git, f'origin/{du_an.nhanh_chinh}', commit,
                        them=du_an.giao.duong_dan_cam, bat_buoc=them_cam,
                        cho_phep=du_an.giao.duong_dan_cam_cho_phep)
    if cham:
        return KetQuaKiemLai(False, cham_cam=tuple(cham), loi='dong-file-cau-hinh')
    if not chay_lenh:
        return KetQuaKiemLai(True)
    if du_an.moi_truong_kiem is None:
        return KetQuaKiemLai(False, loi='thieu-moi-truong-kiem')
    nguon, env = archive(kho_git, commit), moi_truong(kho_git, commit, du_an.moi_truong_kiem)
    d = yeu_cau(dict(v=1, op='chay', id=bam(f'{giao_id}/{luot}/{commit}'.encode())[:32],
        giao_id=giao_id, luot=luot, du_an=du_an.ten, commit=commit, tree=cay_goc(kho_git, commit),
        policy=digest_policy(lenh_cho_phep, du_an.giao.lenh_kiem_mac_dinh), lenh=lenh_kiem,
        nguon_n=len(nguon), nguon_sha=bam(nguon),
        env_n=len(env), env_sha=bam(env), dich=du_an.moi_truong_kiem.dich))
    r = goi(d, nguon, env)
    if r.get('trang_thai') != 'xong' or r.get('da_thu_hoi') is not True or any(
            r.get(k) != d[k] for k in ('id', 'giao_id', 'luot', 'commit')) or r.get('fingerprint') != fingerprint(d):
        raise LoiBanChep('ket-qua-khong-khop-luot')
    k = r['ket_qua']
    if type(k.get('dat')) is not bool or not isinstance(k.get('ket_qua'), list):
        raise LoiBanChep('ket-qua-sai-dang')
    return KetQuaKiemLai(k['dat'], tuple(k['ket_qua']))
```

`tram/quan_kiem/cau_hinh.py`

```python
"""Cấu hình/bằng chứng root; không cho env hay client lựa chọn mã, đường ghi hoặc policy."""
import json
import os
import pwd
from pathlib import Path

from tram.giao_viec.cong_that import doc_tep_root
from tram.giao_viec.ngu_canh_kiem import ngu_canh_hien_hanh
from tram.quan_kiem.giao_thuc import fingerprint

CAU_HINH = Path('/usr/local/tram/quan-kiem/config.json')


def nap():
    c = json.loads(doc_tep_root(CAU_HINH))
    keys = {'uid_tram', 'uid_quan', 'gid_socket', 'home', 'goc', 'socket', 'python', 'entry',
            'policy', 'home_tram', 'g4', 'bang_chung'}
    if set(c) != keys or type(c['g4']) is not bool or not isinstance(c['policy'], dict):
        raise ValueError('cau-hinh-sai')
    if c['home'] != '/private/var/db/tram-quan-kiem' or \
            c['socket'] != '/private/var/db/tram-quan-kiem-socket/dieu-khien.sock' or \
            c['entry'] != '/usr/local/tram/quan-kiem/chay.py':
        raise ValueError('duong-cau-hinh-sai')
    u = pwd.getpwnam('tram-quan-kiem')
    if c['uid_quan'] != u.pw_uid or u.pw_uid in (0, c['uid_tram'], pwd.getpwnam('tram-kiem').pw_uid):
        raise ValueError('uid-khong-rieng')
    from tram.quan_kiem.policy import kiem_policy
    kiem_policy(c['policy'])
    return c


def kiem_ngu_canh(c):
    u = pwd.getpwnam('tram-quan-kiem')
    nc = ngu_canh_hien_hanh('tram-kiem')
    if os.getuid() != u.pw_uid or os.geteuid() != u.pw_uid or os.getppid() != 1 or nc.do_hoa:
        raise ValueError('khong-phai-system-quan-kiem')
    import grp
    from tram.chu.nhom_rieng import NHOM_NEN
    he = {grp.getgrnam(n).gr_gid for n in NHOM_NEN}
    if os.getgid() != u.pw_gid or set(os.getgroups()) - {u.pw_gid, c['gid_socket']} - he:
        raise ValueError('nhom-tien-trinh-sai')
    from tram.quan_kiem.bang_chung import dau_van_tay, MUC_G4
    bc = c['bang_chung']
    if not c['g4'] and (not isinstance(bc, dict) or bc.get('dau_van_tay') != dau_van_tay(c) or
                        bc.get('ket_luan') != {k: True for k in MUC_G4}):
        raise ValueError('chua-co-bang-chung-g4')
    return nc
```

`tram/quan_kiem/bang_chung.py`

```python
"""Fingerprint của bản cài G4; kết luận để Đại ca ký sau đo, không tự coi digest là bằng chứng OS."""
import hashlib
import json
import os
import pwd
from pathlib import Path

from tram.giao_viec.ngu_canh_kiem import ban_macos, ma_may
from tram.kiem.toolchain import PREFIX, PHU_THUOC
from tram.quan_kiem.giao_thuc import fingerprint

MUC_G4 = ('nguon-system', 'rao-ho-so', 'doc-canary', 'cong-cu', 'nhieu-luot', 'crash', 'reboot', 'don')


def _tep(p):
    st = p.stat()
    with p.open('rb') as f:
        h = hashlib.file_digest(f, 'sha256').hexdigest()
    return [str(p.resolve()), st.st_uid, st.st_gid, st.st_mode, h]


def dau_van_tay(c):
    roots = [Path('/usr/local/tram/quan-kiem'), *map(Path, (*PREFIX, *PHU_THUOC))]
    tep = {}
    for root in roots:
        for p in sorted(root.rglob('*')):
            if p.is_file() and p.name != 'config.json' and '__pycache__' not in p.parts:
                tep[str(p)] = _tep(p)
    for p in map(Path, ['/usr/local/tram/tram-kiem.sb', '/usr/local/tram/tram-kiem.sb.json',
                        '/Library/LaunchDaemons/vn.tram.quan-kiem.plist', '/etc/sudoers.d/tram-quan-kiem',
                        '/etc/pam.d/sudo', '/etc/sudo.conf']):
        tep[str(p)] = _tep(p) if p.exists() else None
    users = {n: [*pwd.getpwnam(n)[2:4], sorted(os.getgrouplist(n, pwd.getpwnam(n).pw_gid))]
             for n in ('tram-kiem', 'tram-quan-kiem', pwd.getpwuid(c['uid_tram']).pw_name)}
    config = {k: v for k, v in c.items() if k not in ('g4', 'bang_chung')}
    return fingerprint(dict(ban=ban_macos(), may=ma_may(), config=config, users=users, tep=tep))


def in_mau():
    from tram.quan_kiem.cau_hinh import nap
    print(json.dumps({'dau_van_tay': dau_van_tay(nap()), 'ket_luan': {k: False for k in MUC_G4}}, indent=2))


if __name__ == '__main__':
    in_mau()
```

`tram/quan_kiem/chay.py`

```python
"""Điểm vào cố định của LaunchDaemon; worker chỉ chạy mã bundle tin cậy."""
import os
import sys
from functools import partial
from pathlib import Path

from tram.giao_viec.ban_chep import giu_khoa
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.cong_that import thu_hoi_theo_uid
from tram.quan_kiem.cau_hinh import nap, kiem_ngu_canh
from tram.quan_kiem.cong import dung
from tram.quan_kiem.dich_vu import nghe
from tram.quan_kiem.thuc_thi import thuc_thi, mo_that
from tram.quan_kiem.vong import QuanKiem


def main():
    c = nap()
    if os.getuid() != c['uid_quan'] or os.geteuid() != c['uid_quan']:
        raise PermissionError('sai-uid-quan-ly')
    os.environ['TRAM_HOME'] = c['home']
    if sys.argv[1:2] in (['mo'], ['don']):
        from tram.quan_kiem.cong import phuc_hoi
        phuc_hoi(c, sys.argv[1], sys.argv[2])
        return
    if sys.argv[1:2] == ['luot']:
        from tram.quan_kiem.luot import worker
        p = Path(sys.argv[2]).resolve()
        if p.parent != Path(c['home']) or not p.name.startswith('nhan-'):
            raise ValueError('duong-worker-sai')
        worker(p, c)
        return
    nc = kiem_ngu_canh(c)
    pk = tu_cach_ly('user:tram-kiem')
    with giu_khoa(Path(c['home']) / 'daemon.khoa'):
        cong = dung(c, pk, nc, quan_sat=False)
        cong.dong('khoi-dong-can-xac-nhan-lai')
        q = QuanKiem(c['home'], cong, partial(thuc_thi, cfg=c, pk=pk), partial(mo_that, cfg=c, pk=pk))
        nghe(q, c)
```

- [ ] **Step 4 — GREEN, rồi kiểm hồi quy cuối plan:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_nhan.py
```

Không chạy entry daemon ở máy thật tại bước này. G4 helper chỉ được import khi cài chế độ G4; hoàn thành task 6 trước cài.

## Task 4 — Cài/gỡ Uq + LaunchDaemon theo R2

**Files:**

- Modify `cong-cu/g3-tai-khoan.py`
- Create `tests/test_quan_kiem_policy.py`
- Create `tram/quan_kiem/policy.py`
- Create `tests/test_quan_kiem_cai.py`
- Modify `tests/test_cai_dat_tho_kiem.py`
- Modify `tram/chu/so_cai_tho.py`
- Modify `tram/chu/dinh_danh.py`
- Modify `tram/chu/cai_dat_tho.py`
- Create `tram/chu/quan_kiem_membership.py`
- Create `tram/chu/quan_kiem_sudoers.py`
- Create `tram/chu/dung_quan_kiem.py`
- Create `tram/chu/cai_quan_kiem.py`
- Create `tram/chu/go_quan_kiem.py`
- Create `tram/chu/lenh_quan_kiem.py`

**Tài khoản G3 có sẵn — chọn gỡ trước, một lần sudo.** Dùng bộ gỡ receipt hiện có, không viết
đường nhận sở hữu root thứ hai. Giữ UID/GUID/hash/inode kiểm trước mọi xoá; sửa duy nhất kiểm tàn dư
sang API D162, không bỏ thu hồi. Lệnh cụ thể sau khi code/QC, do Đại ca chạy trong Terminal.app:

```bash
sudo /usr/local/tram/toolchains/python/3.12.15-20261009/bin/python3.12 -I -B cong-cu/g3-tai-khoan.py go
```

Một lần sudo cho cả gỡ (bên trong chờ `dong-y`), rồi phiên sudo cài hiện có; không sudo từng record.
Biên nhận `/var/db/tram-g3-quan-kiem/receipt.json` được giữ lại; không ép giữ số 505 sau tạo mới.
Trình cài sản phẩm từ chối user/nhóm G3 còn tồn tại nếu sổ R2 không sở hữu; không nhận tên trùng là của mình.
Nếu G3 đang có job đo/worker thật thì bộ gỡ từ chối; dọn theo receipt trước, không kill theo tên.

- [ ] **Step 1 — test nguyên văn:**

`tests/test_quan_kiem_policy.py`

```python
import pytest
from tram.quan_kiem.policy import chup_policy, kiem_policy


def test_go_g3_dung_api_d162(monkeypatch):
    import runpy
    import tram.kiem.ngoai_le_uid as m
    ns = runpy.run_path('cong-cu/g3-tai-khoan.py')
    calls = []
    c = ns['CaiGo'](chay=lambda *a: calls.append(a) or '')
    c.xac_minh = lambda s: None
    c.luu = lambda s: None
    state = {'uid': 505, 'made': [], 'removed': []}
    monkeypatch.setattr(m, 'con_uid', lambda uid, **kw: calls.append((uid, kw['ten'])) or [])
    c.go(state)
    assert calls[0] == (505, 'tram-quan-kiem')
    monkeypatch.setattr(m, 'con_uid', lambda *a, **kw: [object()])
    with pytest.raises(RuntimeError, match='ngoài D162'):
        c.go(state)


def test_chup_dung_cau_hinh_du_an(tmp_path):
    (tmp_path / 'repo.yaml').write_text(
        'ten: repo\nduong_dan: /fake\nlenh_cho_phep: ["python -m pytest"]\n'
        'lenh_kiem_mac_dinh: ["python -m pytest"]\n')
    assert chup_policy(tmp_path) == {'repo': {'mac_dinh': ['python -m pytest'],
                                           'cho_phep': ['python -m pytest']}}


@pytest.mark.parametrize('p', [{}, {'repo': {'mac_dinh': ['sh x'], 'cho_phep': ['*']}},
    {'repo': {'mac_dinh': ['sh x'], 'cho_phep': ['python -m pytest']}}])
def test_khong_mo_rong_policy(p):
    with pytest.raises(ValueError):
        kiem_policy(p)


@pytest.mark.parametrize('lenh,chap_nhan', [(['python -m pytest'], True), (['python -V'], False)])
def test_server_bat_buoc_lenh_mac_dinh(monkeypatch, lenh, chap_nhan):
    from types import SimpleNamespace
    import tram.quan_kiem.dich_vu as m
    from test_quan_kiem_giao_thuc import mau
    calls, reply = [], []
    d = mau() | {'lenh': lenh, 'policy': 'd' * 64}
    monkeypatch.setattr(m, 'xac_thuc', lambda *a: None)
    monkeypatch.setattr(m, 'doc', lambda *a, **kw: d)
    monkeypatch.setattr(m, 'digest_policy', lambda *a: 'd' * 64)
    monkeypatch.setattr(m, 'nhan', lambda *a: b'')
    monkeypatch.setattr(m, 'ghi', lambda s, r: reply.append(r))
    q = SimpleNamespace(chay=lambda *a: calls.append(a) or {'ok': True}, dong=lambda: None)
    c = {'uid_tram': 501, 'g4': False, 'policy': {'repo': {
        'mac_dinh': ['python -m pytest'], 'cho_phep': ['python -m pytest', 'python -V']}}}
    m.phuc_vu(SimpleNamespace(close=lambda: None), q, c)
    assert bool(calls) is chap_nhan
    assert reply == ([{'ok': True}] if chap_nhan else [{'loi': 'khong-cong-nhan'}])
```

`tests/test_quan_kiem_cai.py`

```python
import plistlib
from pathlib import Path
from tram.chu.cai_quan_kiem import plist, lap, UQ, DAEMON
from tram.chu.so_cai_tho import SoCai


def test_daemon_khong_tro_nha_dai_ca():
    d = plistlib.loads(plist())
    assert d['UserName'] == UQ
    assert d['GroupName'] == UQ
    assert d['SessionCreate'] is True
    assert d['WorkingDirectory'] == '/var/empty'
    assert all('/Users/' not in x for x in d['ProgramArguments'])
    assert '-I' in d['ProgramArguments']


def test_lap_chua_goi_lenh_va_co_so_r2(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_REPO", str(tmp_path))
    so = SoCai(tmp_path / 'so.jsonl')
    (tmp_path / 'du-an').mkdir()
    (tmp_path / 'du-an/repo.yaml').write_text(
        'ten: repo\nduong_dan: /fake\nlenh_cho_phep: ["python -m pytest"]\n'
        'lenh_kiem_mac_dinh: ["python -m pytest"]\n')
    kh = lap(tmp_path, 'hungle', so, quan_sat=lambda *a, **kw: None)
    assert kh.buoc and not so.p.exists()
    assert 'dong-y' in '\n'.join(kh.canh_bao)
    assert any('tram-quan-kiem' in ten for ten, f in kh.buoc)
    assert any(str(DAEMON) in ten for ten, f in kh.buoc)


def test_khong_nhan_user_la(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        lap(tmp_path, 'hungle', SoCai(tmp_path / 'so'), quan_sat=lambda *a, **kw: {'uid': 777})


def test_go_doi_soat_tai_nguyen_crash_truoc_receipt(tmp_path):
    from tram.chu.go_quan_kiem import lap_go
    so = SoCai(tmp_path / 'so')
    name = '/usr/local/tram/quan-kiem/crash.py'
    so.du_dinh('x', 'tep', name, {'sha256': 'a'})
    state = {'hien': {'sha256': 'a', 'uid': 0}}
    calls = []
    def chay(a, **kw):
        calls.append(a)
        state['hien'] = None
    kh = lap_go(so, quan_sat=lambda k, n, **kw: state['hien'] if n == name else None, chay=chay)
    for _, f in kh.buoc:
        f()
    assert calls == [['sudo', '/bin/rm', '-f', name]]
    assert so.muc()['x'].su == 'da_go'
```

`tests/test_cai_dat_tho_kiem.py` — patch chính xác trên HEAD (không chép lại phần không đổi):

```diff
--- a/tests/test_cai_dat_tho_kiem.py
+++ b/tests/test_cai_dat_tho_kiem.py
@@ -26,7 +26,7 @@
 def test_sudoers_chi_runas_tram_kiem_va_tram_kiem_tu_tao_thu_muc(tram_home_tam, tmp_path):
     kh, soan = ke_hoach(tmp_path), tram_home_tam / "cai-dat-tho"
     sud = kh.tep[soan / "tram-tho.sudoers"].decode()
-    assert sud.splitlines()[-1] == "hung ALL=(tram-kiem) NOPASSWD:SETENV: ALL" and "root" not in sud
+    assert "hung ALL=(tram-kiem)" not in sud and "root" not in sud
     buoc = [m for m, _ in kh.buoc]
     assert f"[tạo] thu_muc {tmp_path}/kiem: sudo -u tram-kiem /bin/mkdir -m 0755 {tmp_path}/kiem" in buoc
     assert "D22" in in_ke_hoach(kh) and "go-cai-dat-tho" in in_ke_hoach(kh) and buoc[0].startswith("Đối soát")
@@ -48,7 +48,7 @@
     kh, soan = ke_hoach(tmp_path, chuoi="sandbox:tram-kiem", co_che="sandbox"), tram_home_tam / "cai-dat-tho"
     hs = kh.tep[soan / HO_SO_KIEM.name].decode()
     assert f'(subpath "{tram_home_tam}")' in hs and '(subpath "/Users/tram-tho/.tram")' in hs
-    assert kh.tep[soan / "tram-tho.sudoers"].decode().splitlines()[-1].endswith(f"sandbox-exec -f {HO_SO_KIEM} *")
+    assert "hung ALL=(tram-kiem)" not in kh.tep[soan / "tram-tho.sudoers"].decode()
     buoc = " | ".join(m for m, _ in kh.buoc)
     assert f"install -d -o root -g wheel -m 0755 {THU_MUC_CAI}" in buoc
     assert f"install -m 0644 -o root -g wheel {soan / HO_SO_KIEM.name} {HO_SO_KIEM}" in buoc
```

- [ ] **Step 2 — chạy RED trước mã:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_policy.py tests/test_quan_kiem_cai.py tests/test_cai_dat_tho_kiem.py
```

RED đã quan sát trong phiên soạn:

```text
test_go_doi_soat_tai_nguyen_crash_truoc_receipt: AssertionError, calls == [] thay vì lệnh gỡ; 1 failed, 3 passed.
```

- [ ] **Step 3 — mã nguyên văn:**

`cong-cu/g3-tai-khoan.py` — patch chính xác trên HEAD (không chép lại phần không đổi):

```diff
--- a/cong-cu/g3-tai-khoan.py
+++ b/cong-cu/g3-tai-khoan.py
@@ -11,6 +11,9 @@
 import subprocess
 import sys
 import uuid
+
+# Điểm vào root do người vận hành duyệt; chỉ import checkout chứa script, không cwd/env.
+sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

 TEN = 'tram-quan-kiem'
 RULE = f'{TEN} ALL=(tram-kiem) NOPASSWD: ALL\n'
@@ -160,10 +163,9 @@

     def go(self, s):
         self.xac_minh(s)
-        rows = self.chay('/bin/ps', '-A', '-o', 'uid=,ruid=').splitlines()
-        if not rows or any(len(x.split()) != 2 or not all(v.isdigit() for v in x.split()) for x in rows):
-            raise RuntimeError('không đọc đủ ps; không gỡ')
-        if any(str(s['uid']) in x.split() for x in rows): raise RuntimeError('Uq còn tiến trình; không giết/không gỡ')
+        from tram.kiem.ngoai_le_uid import con_uid
+        if con_uid(s['uid'], ten=TEN):
+            raise RuntimeError('Uq còn tiến trình ngoài D162; không giết/không gỡ')
         for kind in ('sudoers', 'Users', 'Groups'):
             if kind not in s['made'] or kind in s['removed']: continue
             self.xac_minh(s)
```

`tram/quan_kiem/policy.py`

```python
"""Chụp cấu hình dự án đã được trạm đọc; không có mặc định cho phép mọi lệnh."""
import re
from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
from tram.cau_hinh.lenh import khop_bat_ky, kiem_mau


def kiem_policy(policy):
    if not isinstance(policy, dict) or not policy:
        raise ValueError('thieu-policy-du-an')
    for ten, p in policy.items():
        if not isinstance(ten, str) or not re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}', ten):
            raise ValueError('ten-policy-sai')
        if not isinstance(p, dict) or set(p) != {'mac_dinh', 'cho_phep'}:
            raise ValueError('policy-sai')
        for k in p:
            if not isinstance(p[k], list) or not p[k] or any(
                    not isinstance(x, str) or not 0 < len(x) <= 1024 for x in p[k]):
                raise ValueError('lenh-policy-sai')
        if len(p['mac_dinh']) > 20 or any(kiem_mau(x) for x in p['cho_phep']) or any(
                not khop_bat_ky(x, p['cho_phep']) for x in p['mac_dinh']):
            raise ValueError('policy-khong-khop')
    return policy


def chup_policy(thu_muc=None):
    policy = {}
    for ten in liet_ke_du_an(thu_muc):
        da = nap_du_an(ten, thu_muc=thu_muc)
        if da.giao.lenh_kiem_mac_dinh:
            policy[ten] = {'mac_dinh': list(da.giao.lenh_kiem_mac_dinh),
                           'cho_phep': list(da.lenh_cho_phep)}
    return kiem_policy(policy)
```

`tram/chu/so_cai_tho.py` — patch chính xác trên HEAD (không chép lại phần không đổi):

```diff
--- a/tram/chu/so_cai_tho.py
+++ b/tram/chu/so_cai_tho.py
@@ -17,7 +17,7 @@
 from tram.duong_dan import tram_home

 PHIEN_BAN = 2
-KIEU = ("acl_search", "nhom", "user", "nha", "tep", "thu_muc")
+KIEU = ("thanh_vien", "acl_search", "nhom", "user", "nha", "tep", "thu_muc")
 SU = ("du_dinh", "da_tao", "khong_tao", "da_go")
 CHUYEN = {"du_dinh": ("da_tao", "khong_tao"), "da_tao": ("da_go",)}     # chuyển trạng thái hợp lệ

```

`tram/chu/dinh_danh.py` — patch chính xác trên HEAD (không chép lại phần không đổi):

```diff
--- a/tram/chu/dinh_danh.py
+++ b/tram/chu/dinh_danh.py
@@ -84,7 +84,7 @@
 def khop(kieu: str, mong: dict, hien: dict) -> bool:
     if hien.get("loai") == "khac":
         return False
-    if kieu == "acl_search":
+    if kieu in ("acl_search", "thanh_vien"):
         return hien == mong
     if kieu in ("user", "nhom"):
         return hien.get("ten_day_du") == mong.get("ten_day_du")
@@ -96,7 +96,7 @@
 def cung(kieu: str, da: dict | None, hien: dict) -> bool:
     if not da or hien.get("loai") == "khac":
         return False
-    if kieu == "acl_search":
+    if kieu in ("acl_search", "thanh_vien"):
         return hien == da
     if kieu in ("user", "nhom"):
         key = "gid" if kieu == "nhom" else "uid"
```

`tram/chu/cai_dat_tho.py` — patch chính xác trên HEAD (không chép lại phần không đổi):

```diff
--- a/tram/chu/cai_dat_tho.py
+++ b/tram/chu/cai_dat_tho.py
@@ -14,7 +14,7 @@
 from tram.chu.cai_dat_kiem import NHA_KIEM, phan_kiem, tep_root
 from tram.chu import dinh_danh
 from tram.chu.launchd import PATH_HE_THONG
-from tram.chu.nhom_rieng import nhom_tram, user_nhom, siet_user, lenh_bo_nhom, NHOM_THUA, nhom_phu
+from tram.chu.nhom_rieng import nhom_tram, user_nhom, siet_user, lenh_bo_nhom, NHOM_THUA, NHOM_NEN, nhom_phu
 from tram.chu.so_cai_tho import SoCai, doi_soat
 from tram.chu.tai_nguyen import TaiNguyen, kiem_truoc, nha_tram, tao
 from tram.duong_dan import tram_home
@@ -30,8 +30,7 @@
 def noi_dung_sudoers(*, quan_ly: str, principal: list[str], tram: str, kiem: PrincipalKiem | None) -> bytes:
     dong = ["# Sinh bởi `tram chu cai-dat-tho` (spec 3 §7.3) — chỉ cho chạy lệnh DƯỚI principal không credential.",
             f"{quan_ly} ALL=({','.join(sorted(set(principal)))}) NOPASSWD:SETENV: ALL"]
-    if kiem:
-        dong.append(dong_sudoers_kiem(tram=tram, tram_kiem=kiem.ten, co_che=kiem.co_che))
+    # D159/D160: quyền kiểm chỉ do trình cài Uq quản lý; không cấp lại 501→503.
     return ("\n".join(dong) + "\n").encode()


@@ -71,7 +70,7 @@
           tep_root(soan / f"{NHAN_THO}.plist", DAEMON, pl, "0644")]
     viec = kiem_truoc(so, ds, quan_sat=quan_sat)
     for u in nguoi:
-        if quan_sat('user', u) is not None and nhom_phu(u, chay=chay) - {u, 'everyone', 'localaccounts'}:
+        if quan_sat('user', u) is not None and nhom_phu(u, chay=chay) - {u} - NHOM_NEN:
             raise ValueError('User cũ còn nhóm ngoài: chạy migration có audit/rollback trước cài lại')
     buoc = [("Đối soát sổ cài đặt (bản ghi dở dang của lần trước)", lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
     buoc += [(f"[{v}] {tn.kieu} {tn.ten}: {tn.mo_ta()}", lambda tn=tn: tao(so, tn, quan_sat=quan_sat, chay=chay))
```

`tram/chu/quan_kiem_membership.py`

```python
"""Membership có sổ riêng, nhận diện cả GUID user và nhóm trước khi gỡ."""
import subprocess

from tram.chu import dinh_danh
from tram.chu.tai_nguyen import TaiNguyen


def quan_sat(kieu, ten, *, nhe=False, chay=subprocess.run):
    if kieu != 'thanh_vien':
        return dinh_danh.quan_sat_that(kieu, ten, nhe=nhe)
    g, u = ten.split('/')
    if dinh_danh.nhom(g) is None:
        return None
    r = chay(['/usr/sbin/dseditgroup', '-o', 'checkmember', '-m', u, g],
             capture_output=True, text=True, timeout=30)
    if r.returncode == 0 and r.stdout.startswith('yes '):
        return {'user': dinh_danh.user(u), 'nhom': dinh_danh.nhom(g)}
    if r.returncode == 0 and r.stdout.startswith('no '):
        return None
    raise OSError('khong-doc-duoc-membership')


def tai_nguyen(u, g, doc):
    return TaiNguyen('thanh_vien', f'{g}/{u}', lambda i: [
        ['sudo', '/usr/sbin/dseditgroup', '-o', 'edit', '-a', u, '-t', 'user', g]],
        lambda i: {'user': doc('user', u), 'nhom': doc('nhom', g)})
```

`tram/chu/quan_kiem_sudoers.py`

```python
"""Đổi đúng dòng legacy đã có biên nhận; không phục hồi lối 501 chạy kiểm khi gỡ."""
from pathlib import Path

from tram.chu.cai_dat_kiem import tep_root
from tram.chu.tai_nguyen import tao, cua_tram
from tram.tho.quyen_kiem import dong_sudoers_kiem


LEGACY = Path('/etc/sudoers.d/tram-tho')
DICH = Path('/etc/sudoers.d/tram-quan-kiem')


def chuyen(so, tram, soan, *, quan_sat, chay):
    from tram.chu.so_cai_tho import SoCai
    with SoCai().giu() as legacy:
        _bo_cu(legacy, tram, soan, quan_sat=quan_sat, chay=chay)
    p = soan / 'quan.sudoers'
    p.write_text('Defaults:tram-quan-kiem !requiretty\n' +
                 dong_sudoers_kiem(tram='tram-quan-kiem', tram_kiem='tram-kiem', co_che='user') + '\n')
    tao(so, tep_root(p, DICH, p.read_bytes(), '0444', truoc=(['sudo', '/usr/sbin/visudo', '-cf', str(p)],)),
        quan_sat=quan_sat, chay=chay)


def _bo_cu(so, tram, soan, *, quan_sat, chay):
    hien = quan_sat('tep', str(LEGACY))
    if hien is not None:
        if not cua_tram(so, 'tep', str(LEGACY), hien):
            raise ValueError('sudoers-cu-khong-khop-so')
        b = chay(['sudo', '/bin/cat', str(LEGACY)], capture_output=True, check=True, timeout=30).stdout
        cu = b.decode().splitlines()
        cam = {dong_sudoers_kiem(tram=tram, tram_kiem='tram-kiem', co_che=k) for k in ('user', 'sandbox')}
        moi = ('\n'.join(x for x in cu if x not in cam) + '\n').encode()
        if any(tram in x and 'tram-kiem' in x for x in moi.decode().splitlines() if not x.startswith('#')):
            raise ValueError('sudoers-cu-khong-nhan-dien')
        p = soan / 'legacy.sudoers'
        p.write_bytes(moi)
        tao(so, tep_root(p, LEGACY, moi, '0440', truoc=(['sudo', '/usr/sbin/visudo', '-cf', str(p)],)),
            quan_sat=quan_sat, chay=chay)
```

`tram/chu/dung_quan_kiem.py`

```python
"""Dừng label cố định; chưa nạp cũng phải chứng minh vắng, không nuốt mọi lỗi bootout."""
from tram.giao_viec.do_launchd_g4 import _vang


def dung_daemon(chay):
    nhan = 'vn.tram.quan-kiem'
    chay(['sudo', '/bin/launchctl', 'bootout', f'system/{nhan}'], check=False, timeout=30)
    r = chay(['sudo', '/bin/launchctl', 'print', f'system/{nhan}'],
             capture_output=True, timeout=30)
    if not _vang(r.returncode, (r.stdout or b'') + (r.stderr or b''), nhan):
        raise OSError('chua-chung-minh-daemon-da-dung')
```

`tram/chu/cai_quan_kiem.py`

```python
"""Cài Uq/LaunchDaemon bằng KeHoach và sổ R2; không khởi động lúc lập kế hoạch."""
import json
import plistlib
import subprocess
from pathlib import Path

from tram.chu import dinh_danh
from tram.chu.dung_quan_kiem import dung_daemon
from tram.chu.cai_dat import KeHoach
from tram.chu.cai_dat_kiem import tep_root
from tram.chu.nhom_rieng import nhom_tram, user_nhom, siet_user
from tram.chu.so_cai_tho import doi_soat
from tram.chu.tai_nguyen import TaiNguyen, kiem_truoc, tao
from tram.duong_dan import tram_home, goc_repo
from tram.kiem.toolchain import PYTHON

UQ = 'tram-quan-kiem'
NHAN = 'vn.tram.quan-kiem'
BUNDLE = Path('/usr/local/tram/quan-kiem')
HOME_Q = Path('/private/var/db/tram-quan-kiem')
SOCKET = Path('/private/var/db/tram-quan-kiem-socket')
DAEMON = Path('/Library/LaunchDaemons/vn.tram.quan-kiem.plist')
SUDOERS = Path('/etc/sudoers.d/tram-quan-kiem')
ENTRY = b'import sys\nsys.path.insert(0, "/usr/local/tram/quan-kiem")\nfrom tram.quan_kiem.chay import main\nmain()\n'


def plist():
    return plistlib.dumps({'Label': NHAN, 'UserName': UQ, 'GroupName': UQ, 'SessionCreate': True,
        'ProgramArguments': [f'{PYTHON}/bin/python3.12', '-I', str(BUNDLE / 'chay.py')],
        'WorkingDirectory': '/var/empty', 'RunAtLoad': True, 'KeepAlive': {'SuccessfulExit': False},
        'EnvironmentVariables': {'HOME': str(HOME_Q), 'TRAM_HOME': str(HOME_Q),
                                 'PATH': '/usr/bin:/bin:/usr/sbin:/sbin'},
        'StandardOutPath': str(HOME_Q / 'daemon.log'), 'StandardErrorPath': str(HOME_Q / 'daemon.log')})


def thu_muc(p, chu, quan_sat, mode='0700'):
    return TaiNguyen('thu_muc', str(p), lambda i: [
        ['sudo', '/usr/bin/install', '-d', '-o', chu, '-g', 'wheel' if chu == 'root' else UQ, '-m', mode, str(p)]],
        lambda i: {'chu': None if chu == 'root' else chu,
                   'uid': 0 if chu == 'root' else (quan_sat('user', chu) or {}).get('uid')})


def lap(repo, tram, so, *, quan_sat=dinh_danh.quan_sat_that, chay=subprocess.run,
        policy=None, g4=True, bang_chung=None):
    from tram.tho.principal import USER_RE
    from tram.chu.quan_kiem_membership import tai_nguyen as member
    if not USER_RE.fullmatch(tram) or tram in (UQ, 'tram-kiem', 'root'):
        raise ValueError('tai-khoan-tram-sai')
    if quan_sat('user', UQ) is not None and not so.co_ghi('user', UQ):
        raise ValueError(f'Gỡ G3 trước: sudo {PYTHON}/bin/python3.12 -I -B cong-cu/g3-tai-khoan.py go')
    from tram.quan_kiem.policy import chup_policy, kiem_policy
    policy = chup_policy() if policy is None else kiem_policy(policy)
    soan = tram_home() / 'cai-quan-kiem'
    tep = {soan / 'chay.py': ENTRY, soan / DAEMON.name: plist()}
    ds = [nhom_tram(UQ), user_nhom(UQ, '/var/empty', so, quan_sat),
          thu_muc(HOME_Q, UQ, quan_sat), thu_muc(SOCKET, UQ, quan_sat, '0750'),
          thu_muc(BUNDLE, 'root', quan_sat, '0755')]
    for p in sorted(Path(repo).joinpath('tram').rglob('*.py')):
        if p.is_symlink():
            raise ValueError('bundle-co-symlink')
        rel = p.relative_to(repo)
        tep[soan / rel] = p.read_bytes()
    parents = {p.parent.relative_to(soan) for p in tep if p.parent != soan}
    for rel in sorted({q for p in parents for q in (p, *p.parents) if str(q) != '.'}, key=lambda p: len(p.parts)):
        ds.append(thu_muc(BUNDLE / rel, 'root', quan_sat, '0755'))
    for p, b in tep.items():
        dich = DAEMON if p.name == DAEMON.name else BUNDLE / p.relative_to(soan)
        ds.append(tep_root(p, dich, b, '0644'))
    ds.append(member(tram, UQ, quan_sat))
    kiem_truoc(so, ds, quan_sat=quan_sat)
    def config():
        u, t, g = quan_sat('user', UQ), quan_sat('user', tram), quan_sat('nhom', UQ)
        c = dict(uid_tram=t['uid'], uid_quan=u['uid'], gid_socket=g['gid'], home=str(HOME_Q),
                 goc='/Users/Shared/tram-kiem', socket=str(SOCKET / 'dieu-khien.sock'),
                 python=f'{PYTHON}/bin/python3.12', entry=str(BUNDLE / 'chay.py'),
                 policy=policy, home_tram=str(tram_home()),
                 g4=g4, bang_chung=bang_chung)
        p = soan / 'config.json'
        p.write_text(json.dumps(c))
        tao(so, tep_root(p, BUNDLE / p.name, p.read_bytes(), '0644'), quan_sat=quan_sat, chay=chay)
        from tram.chu.quan_kiem_sudoers import chuyen
        chuyen(so, tram, soan, quan_sat=quan_sat, chay=chay)
    buoc = [('Đối soát sổ R2', lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
    if quan_sat('tep', str(DAEMON), nhe=True) is not None:
        def dung_cu():
            from tram.chu.tai_nguyen import cua_tram
            if not cua_tram(so, 'tep', str(DAEMON), quan_sat('tep', str(DAEMON))):
                raise ValueError('daemon-cu-khong-khop-so')
            dung_daemon(chay)
        buoc.append(('Dừng daemon cũ đúng biên nhận trước thay mã', dung_cu))
    buoc += [(f'{tn.kieu} {tn.ten}: {tn.mo_ta()}',
              lambda tn=tn: tao(so, tn, quan_sat=quan_sat, chay=chay)) for tn in ds]
    buoc += [('Siết nhóm tiến trình mới Uq', lambda: siet_user(UQ, so, quan_sat, chay=chay)),
             ('Cài config root và chuyển sudoers 501→503 sang Uq→503, có sổ R2', config)]
    return KeHoach(tep, [['sudo', '/bin/launchctl', 'bootstrap', 'system', str(DAEMON)]],
                   ['Chỉ thực hiện sau dong-y; mặc định G4 dữ liệu giả, S6 còn đóng.',
                    f'Policy nguồn {goc_repo() / "du-an"}: ' + json.dumps(policy, ensure_ascii=False),
                    'Khởi động lại phiên trạm để nhận nhóm socket; không cấp ACL vào nhà Đại ca.'], buoc, 30)
```

`tram/chu/go_quan_kiem.py`

```python
"""Gỡ đúng tài nguyên Uq có sổ; không pkill, không khôi phục sudoers 501→503."""
from pathlib import Path

from tram.chu import dinh_danh
from tram.chu.dung_quan_kiem import dung_daemon
from tram.chu.cai_dat import KeHoach
from tram.chu.cai_quan_kiem import UQ, NHAN, BUNDLE, HOME_Q, SOCKET, DAEMON, SUDOERS
from tram.chu.so_cai_tho import doi_soat
from tram.kiem.bang_tien_trinh import chup_nhan
from tram.kiem.ngoai_le_uid import con_uid


def thuoc(m):
    if m.kieu in ('user', 'nhom'):
        return m.ten == UQ
    if m.kieu == 'thanh_vien':
        return m.ten.startswith(UQ + '/')
    p = Path(m.ten)
    return p in (HOME_Q, SOCKET, DAEMON, SUDOERS) or p == BUNDLE or BUNDLE in p.parents


def lenh(m):
    if m.kieu == 'thanh_vien':
        g, u = m.ten.split('/')
        return [['sudo', '/usr/sbin/dseditgroup', '-o', 'edit', '-d', u, '-t', 'user', g]]
    if m.kieu == 'user':
        return [['sudo', '/usr/sbin/sysadminctl', '-deleteUser', UQ, '-keepHome']]
    if m.kieu == 'nhom':
        return [['sudo', '/usr/sbin/dseditgroup', '-o', 'delete', UQ]]
    if m.ten in (str(HOME_Q), str(SOCKET)):
        return [['sudo', '/bin/rm', '-rf', m.ten]]
    return [['sudo', '/bin/rm', '-f', m.ten]] if m.kieu == 'tep' else [['sudo', '/bin/rmdir', m.ten]]


def lap_go(so, *, quan_sat, chay, chup=chup_nhan):
    ds = { (m.kieu, m.ten): m for m in so.muc().values() if m.su in ('du_dinh', 'da_tao') and thuoc(m) }
    def go(m):
        m = so.muc()[m.id]
        if m.su != 'da_tao':
            return
        h = quan_sat(m.kieu, m.ten)
        if h is not None and not dinh_danh.cung(m.kieu, m.dinh_danh, h):
            raise ValueError('tai-nguyen-da-doi-khong-go')
        if h is not None:
            if m.ten == str(DAEMON):
                dung_daemon(chay)
            if m.kieu == 'user' and con_uid(h['uid'], chup=chup, ten=UQ):
                raise ValueError('Uq-con-tien-trinh-khong-xoa-user')
            for a in lenh(m):
                chay(a, check=True, timeout=30)
            if quan_sat(m.kieu, m.ten) is not None:
                raise OSError('go-chua-xong')
        for cu in so.da_tao(m.kieu, m.ten):
            so.ket(cu.id, 'da_go')
    def thu_tu(m):
        if m.ten == str(DAEMON):
            return (0, 0)
        if m.ten == str(SUDOERS):
            return (1, 0)
        return ({'thanh_vien': 2, 'tep': 3, 'thu_muc': 4, 'user': 5, 'nhom': 6}[m.kieu], -len(Path(m.ten).parts))
    buoc = [('Đối soát sổ R2', lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
    def truoc_go():
        if ('tep', str(DAEMON)) in ds and quan_sat('tep', str(DAEMON)) is not None:
            m = so.muc()[ds['tep', str(DAEMON)].id]
            if not dinh_danh.cung('tep', m.dinh_danh, quan_sat('tep', str(DAEMON))):
                raise ValueError('daemon-da-doi-khong-go')
            dung_daemon(chay)
        u = quan_sat('user', UQ)
        if u and con_uid(u['uid'], chup=chup, ten=UQ):
            raise ValueError('Uq-con-worker-khong-xoa-du-lieu')
    buoc.append(('Dừng daemon sở hữu; xác nhận hết worker trước xoá dữ liệu', truoc_go))
    buoc += [(f'Gỡ {m.kieu} {m.ten}: {lenh(m)}', lambda m=m: go(m)) for m in sorted(ds.values(), key=thu_tu)]
    return KeHoach({}, [], ['Sẽ xoá dữ liệu lượt/log Uq; sao lưu chứng cứ trước dong-y. S6 giữ đóng.'], buoc)
```

`tram/chu/lenh_quan_kiem.py`

```python
"""python -m tram.chu.lenh_quan_kiem cai|go; in kế hoạch rồi chờ dong-y."""
import argparse
import getpass
import json
import subprocess
from pathlib import Path

from tram.chu.cai_dat import in_ke_hoach, thuc_hien
from tram.chu.cai_quan_kiem import lap
from tram.chu.go_quan_kiem import lap_go
from tram.chu.quan_kiem_membership import quan_sat
from tram.chu.so_cai_tho import SoCai


def main(argv=None, *, hoi=input):
    p = argparse.ArgumentParser()
    p.add_argument('viec', choices=['cai', 'go'])
    p.add_argument('--repo', type=Path, default=Path.cwd())
    p.add_argument('--bang-chung-g4', type=Path)
    a = p.parse_args(argv)
    def chay(cmd, **kw):
        return subprocess.run(cmd, **({'timeout': 30} | kw))
    from tram.duong_dan import tram_home
    with SoCai(tram_home() / 'cai-quan-kiem' / 'so-cai.jsonl').giu() as so:
        if a.viec == 'cai':
            kh = lap(a.repo, getpass.getuser(), so, quan_sat=quan_sat, chay=chay,
                     g4=a.bang_chung_g4 is None,
                     bang_chung=json.loads(a.bang_chung_g4.read_bytes()) if a.bang_chung_g4 else None)
        else:
            kh = lap_go(so, quan_sat=quan_sat, chay=chay)
        print(in_ke_hoach(kh))
        if hoi('Gõ dong-y để thực hiện: ').strip() != 'dong-y':
            return 1
        thuc_hien(kh, chay=chay)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
```

- [ ] **Step 4 — GREEN, rồi kiểm hồi quy cuối plan:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_policy.py tests/test_quan_kiem_cai.py tests/test_cai_dat_tho_kiem.py
```

## Task 5 — Chuyển production khỏi 501; fencing trước ghi kết quả

**Files:**

- Create `tests/test_quan_kiem_noi.py`
- Modify `tests/test_noi_giao_viec.py`
- Modify `tests/test_giao_kiem.py`
- Modify `tram/giao_viec/bo.py`
- Modify `tram/giao_viec/noi_that.py`
- Modify `tram/giao_viec/tick_pipeline.py`
- Modify `tram/giao_viec/kiem_san_sang.py`
- Modify `tram/giao_viec/lenh.py`
- Create `tram/quan_kiem/fencing.py`

- [ ] **Step 1 — test nguyên văn:**

`tests/test_quan_kiem_noi.py`

```python
from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.noi_that import dung_bo_that


def test_bo_that_chi_noi_socket_khong_giu_cong_local(monkeypatch):
    import tram.giao_viec.noi_that as m
    monkeypatch.setattr(m, 'nap_phu_thuoc_4c', lambda: None)
    b = dung_bo_that(CauHinhGiaoViec(), CauHinhTram())
    assert b.kiem_tu_xa is not None
    assert b.boc is None and b.don_sach is None and b.boc_luot is None
    assert type(b.cong).__name__ == 'CongTuXa'


def test_ket_qua_muon_khong_duoc_ghi(monkeypatch):
    from contextlib import contextmanager
    from types import SimpleNamespace
    import tram.quan_kiem.fencing as m
    writes, locked = [], []
    @contextmanager
    def transaction():
        locked.append(True)
        try:
            yield
        finally:
            locked.pop()
    def lay(id_):
        assert locked
        return SimpleNamespace(ket_thuc='thu_hoi')
    kho = SimpleNamespace(giao_dich=transaction, lay=lay, ghi_su_kien=lambda *a, **kw: writes.append(a))
    p = SimpleNamespace(giao_id='g', bead_id='b', luot=1)
    assert m.ghi_ket_qua(kho, SimpleNamespace(ten='d'), p, 'a'*40, {'dat': True}, None) == 'luot-cu'
    assert writes == [] and not locked
```

`tests/test_noi_giao_viec.py` — patch chính xác trên HEAD (không chép lại phần không đổi):

```diff
--- a/tests/test_noi_giao_viec.py
+++ b/tests/test_noi_giao_viec.py
@@ -63,7 +63,7 @@
     cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path / "k", principal_kiem=PK)
     bo = dung_bo_that(cg, tao_pt(tmp_path, {}).cau_hinh, thu_muc_du_an=tmp_path / "du-an")
     assert [d.ten for d in bo.cac_du_an()] == ["hr-x"] and "bỏ qua dự án hong" in capsys.readouterr().err
-    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.don_sach.args == (PK,)   # 3C-D5: theo UID
-    assert bo.kill == PK.kill_nhom
+    assert bo.kiem_tu_xa is not None and bo.boc is None and bo.don_sach is None
+    assert bo.cong.__class__.__name__ == "CongTuXa"
     assert bo.thu_muc_kiem == tmp_path / "k" and bo.doc_beads is None
     assert bo.tao_bd(bo.cac_du_an()[0]).actor == "tram/giao-viec" and Path(bo.tao_bd(bo.cac_du_an()[0]).repo) == tmp_path
```

`tests/test_giao_kiem.py` — patch chính xác trên HEAD (không chép lại phần không đổi):

```diff
--- a/tests/test_giao_kiem.py
+++ b/tests/test_giao_kiem.py
@@ -17,7 +17,7 @@
 def test_thieu_het_thi_do(tmp_path):
     ds = kiem_giao_viec(CauHinhGiaoViec(), [], goc_quyen=tmp_path)
     m = muc(ds)
-    assert (m["giao_viec.bat"], m["file quyền coder"], m["principal kiểm lại"]) == ("vang", "do", "do")
+    assert (m["giao_viec.bat"], m["file quyền coder"], m["Bộ quản lý kiểm"]) == ("vang", "do", "do")
     assert in_ket_qua(ds)[1] == 1


```

- [ ] **Step 2 — chạy RED trước mã:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_noi.py tests/test_noi_giao_viec.py tests/test_giao_kiem.py
```

RED đã quan sát trong phiên soạn:

```text
AttributeError: 'BoGiaoViec' object has no attribute 'kiem_tu_xa'; 1 failed.
```

- [ ] **Step 3 — mã nguyên văn:**

`tram/giao_viec/bo.py`

```python
"""Bộ giao việc — giao diện với phần 3 (spec 4 §13; hợp đồng 3a-1 G11): `chon(khe_id, han_muc)` gọi NGOÀI giao
dịch cấp phiếu (được đọc/ghi beads), `con_hop_le(de_xuat)` gọi TRONG giao dịch (chỉ đọc kho, nhanh).
4a-2: đọc lại Beads ngay trước cấp (`doc_lai.py`), bộ đệm beads của tram-api (`doc_beads.py`); nối vào tram-api ở
`noi_that.py`."""
import os
from collections.abc import Callable, Mapping
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from tram.beads.bd import LoiBd
from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.chon import khe_nhan, khoa_sap_xep
from tram.giao_viec.de_xuat import dung_de_xuat
from tram.giao_viec.de_xuat_spec import dung_de_xuat_spec
from tram.giao_viec.dieu_kien import ASSIGNEE
from tram.giao_viec.feature import con_dot_spec
from tram.giao_viec.doc_beads import DocBeads
from tram.giao_viec.doc_lai import con_nguyen
from tram.giao_viec.kho_kiem_san import kho_kiem_co_san
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
from tram.giao_viec.ngan_sach import du_mot_phieu
from tram.giao_viec.spec_merge import feature_da_merge
from tram.giao_viec.su_kien import su_kien_bead
from tram.giao_viec.ung_vien import liet_ke, viec_ton_cua
from tram.giao_viec.ung_vien_spec import liet_ke_spec
from tram.han_muc.mo_hinh import HanMuc
from tram.kiem.chay_lenh import _kill_nhom
from tram.phieu.kho import KhoPhieu
from tram.phieu.mo_hinh import DeXuatPhieu
from tram.phieu.trang_thai import trang_thai_khe


@dataclass
class BoGiaoViec:
    cac_du_an: Callable[[], list[DuAn]]
    tao_bd: Callable[[DuAn], object]                  # Bd(repo, actor="tram/giao-viec")
    mo_kho: Callable[[], KhoPhieu]
    ch: CauHinhTram
    dong_ho: Callable[[], datetime]
    kho_git: Callable[[DuAn], Path | None] = kho_kiem_co_san
    kiem_tu_xa: Callable | None = None
    boc: Callable[[list[str]], list[str]] | None = None   # principal `tram-kiem` (chờ S6); None: chưa kiểm lại
    env_goc: Mapping[str, str] = field(default_factory=lambda: dict(os.environ))
    doc_beads: DocBeads | None = None                     # 4a-2: bộ đệm beads của tram-api; None: đọc `bd` mỗi lần
    don_sach: Callable[[], None] | None = None            # 3c: giết mọi tiến trình `tram-kiem`, xác nhận sạch (D22)
    cong: object | None = None                            # 3C-D2: CongLuot — lượt trước chưa sạch thì không kiểm lại
    boc_luot: Callable[[Path], Callable] | None = None    # 3C-D1: PrincipalKiem.boc_luot — hồ sơ Seatbelt mỗi lượt
    adr_hop_le: Callable[[DuAn, object], bool] = lambda da, b: False
    kill: Callable[[int, int], None] = _kill_nhom        # 3a-2: kill nhóm qua principal kiểm
    thu_muc_kiem: Path | None = None                      # 4a-2: gốc bản chép kiểm lại; None: ~/.tram/kiem
    de_nghi: object | None = None                         # TC: NguonDeNghi; None: không ghi
    p4c: PhuThuoc4c = field(default_factory=PhuThuoc4c)

    def _da_nhan(self, bd, bead_id: str) -> bool:
        """`--claim` có ID thao tác là chính trạng thái đích: đã `in_progress` với assignee trạm → coi như xong."""
        try:
            bd.nhan_viec(bead_id)
            return True
        except LoiBd:
            try:
                b = bd.mot(bead_id)
            except LoiBd:
                return False
            return b.status == "in_progress" and b.assignee == ASSIGNEE

    def _chot(self, bd, uv, kho, kg) -> bool:
        """Đọc lại NGAY TRƯỚC cấp (4a-1 G3); bead `open` → `--claim` rồi đọc lại lần nữa (spec 4 §5.4)."""
        if not con_nguyen(bd, uv.du_an, uv.bead, buoc=uv.buoc, adr_hop_le=self.adr_hop_le,
                          da_merge=lambda beads: feature_da_merge(kho, uv.du_an, beads, kg)):
            return False
        if uv.buoc == "spec" or uv.bead.status != "open":
            return True
        if not self._da_nhan(bd, uv.bead.id):
            return False
        if self.doc_beads is not None:
            self.doc_beads.danh_dau_cu(uv.du_an.ten)
        return con_nguyen(bd, uv.du_an, uv.bead, sau_claim=True, buoc=uv.buoc, adr_hop_le=self.adr_hop_le,
                          da_merge=lambda beads: feature_da_merge(kho, uv.du_an, beads, kg))

    def chon(self, khe_id: str, han_muc: HanMuc | None) -> DeXuatPhieu | None:
        with closing(self.mo_kho()) as kho:
            cac_khe, ung_vien = trang_thai_khe(kho, bay_gio=self.dong_ho(), ch=self.ch), []
            for da in self.cac_du_an():
                if (kg := self.kho_git(da)) is None:
                    continue
                bd = self.tao_bd(da)
                try:
                    beads, san = self.doc_beads.lay(da, bd) if self.doc_beads else (bd.tat_ca(), bd.san_sang())
                except LoiBd:
                    continue
                merge = feature_da_merge(kho, da, beads, kg)
                ung_vien += [(uv, beads, bd, kg) for uv in liet_ke(kho, da, beads, san, merge)
                             + liet_ke_spec(kho, da, beads, san)]
            for uv, beads, bd, kg in sorted(ung_vien, key=lambda x: khoa_sap_xep(x[0])):
                if not khe_nhan(khe_id, han_muc, uv, cac_khe, self.ch):
                    continue
                ds = su_kien_bead(kho, uv.du_an.ten, uv.bead.id)
                dx = (dung_de_xuat_spec(uv, ds, kg, p4c=self.p4c, theo_id={b.id: b for b in beads}) if uv.buoc == "spec"
                      else dung_de_xuat(uv, ds, {b.id: b for b in beads}, kg, self.p4c, kho.db))
                if dx is None or not self._chot(bd, uv, kho, kg):
                    continue
                return dx
        return None

    def con_hop_le(self, dx: DeXuatPhieu) -> bool:
        """Kiểm lại nhanh trong giao dịch cấp phiếu: không còn công việc chờ/câu hỏi chưa chuyển escalation của bead,
        chưa có escalation mở trong sự kiện, còn ngân sách cho phiếu này."""
        da = next((d for d in self.cac_du_an() if d.ten == dx.du_an), None)
        if da is None:
            return False
        with closing(self.mo_kho()) as kho:
            ds = su_kien_bead(kho, dx.du_an, dx.bead_id)
            mo = {s.du_lieu["escalation_id"] for s in ds if s.loai == "escalation.tao"} - {
                s.du_lieu["escalation_id"] for s in ds if s.loai == "escalation.dong"}
            return (not mo and dx.bead_id not in viec_ton_cua(kho, dx.du_an)
                    and du_mot_phieu(kho, ds, dx.ngan_sach, da.giao.ngan_sach.bead)
                    and (dx.buoc != "spec" or con_dot_spec(ds)))
```

`tram/giao_viec/noi_that.py`

```python
"""Nối bộ giao việc vào tram-api (spec 4 §10, §13; 3a-1 G11) — CHỈ khi `giao_viec.bat: true` (sau mọi cổng):
`chon_phieu` = `bo.chon` và `con_hop_le_phieu` = `bo.con_hop_le` (router `/api/tho/nhip` truyền vào `cap_phieu`),
bọc an toàn — lỗi của phần 4 thành "không phát phiếu", không thành HTTP 500; hai luồng tick. `bo_giao` luôn được
gắn (cả khi tắt) để dashboard đọc lý do không giao. Dựng `BoGiaoViec` không gọi `bd`/Git nào."""
import sys
import threading
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import yaml

from tram.cau_hinh.giao_viec import CauHinhGiaoViec, nap_cau_hinh_giao_viec
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.bo import BoGiaoViec
from tram.giao_viec.noi_4c import nap_phu_thuoc_4c
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
from tram.giao_viec.dieu_kien import ASSIGNEE
from tram.giao_viec.doc_beads import DocBeads
from tram.giao_viec.luong import bat_dau_luong_giao
from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat


def _bao(ten: str, e: Exception) -> None:
    print(f"[giao-viec] {ten}: {type(e).__name__}: {e}", file=sys.stderr, flush=True)


def cac_du_an_that(thu_muc: Path | None = None) -> list:
    """Mọi `du-an/<ten>.yaml` (bỏ tên bắt đầu `_`); một file hỏng chỉ làm dự án đó bị bỏ qua.
    Lát 1a-2 (D31): dự án có `bat_ghi: false` không được giao việc — không vào danh sách."""
    from tram.cau_hinh.bat_ghi import bat_ghi
    from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
    ra = []
    for ten in liet_ke_du_an(thu_muc):
        if ten.startswith("_"):
            continue
        try:
            da = nap_du_an(ten, thu_muc=thu_muc)
            if bat_ghi(ten, thu_muc=thu_muc):
                ra.append(da)
        except (ValueError, OSError, KeyError, AttributeError, yaml.YAMLError) as e:
            _bao(f"bỏ qua dự án {ten}", e)
    return ra


def dung_bo_that(cg: CauHinhGiaoViec, ch: CauHinhTram, *, bo_dem=None,
                 thu_muc_du_an: Path | None = None) -> BoGiaoViec:
    from tram.beads.bd import Bd
    from tram.beads.bd_de_nghi import BdDeNghi
    from tram.cau_hinh.bat_ghi import bat_ghi
    from tram.de_nghi.vong import NguonDeNghi
    from tram.phieu.kho import mo_kho_phieu
    from tram.quan_kiem.client import CongTuXa, kiem_tu_xa
    cac = lambda: cac_du_an_that(thu_muc_du_an)
    return BoGiaoViec(cac_du_an=cac,
                      tao_bd=lambda da: Bd(da.duong_dan, actor=ASSIGNEE), mo_kho=mo_kho_phieu, ch=ch,
                      dong_ho=lambda: datetime.now(timezone.utc), kiem_tu_xa=kiem_tu_xa, cong=CongTuXa(),
                      doc_beads=DocBeads(bo_dem) if bo_dem is not None else None, thu_muc_kiem=cg.thu_muc_kiem,
                      p4c=nap_phu_thuoc_4c() if cg.bat else PhuThuoc4c(),
                      de_nghi=NguonDeNghi(tao_bd=lambda da: BdDeNghi(da.duong_dan), bat_ghi=bat_ghi))


def an_toan(ham: Callable, mac_dinh, ten: str) -> Callable:
    def boc(*a):
        try:
            return ham(*a)
        except Exception as e:                       # noqa: BLE001 — nhịp tim không được hỏng vì phần 4
            _bao(ten, e)
            return mac_dinh
    return boc


def noi_giao_viec(pt, dung: threading.Event, *, cg: CauHinhGiaoViec | None = None,
                  tao_bo: Callable = dung_bo_that) -> tuple[object, list[threading.Thread]]:
    cg = cg or nap_cau_hinh_giao_viec()
    bo = tao_bo(cg, pt.cau_hinh, bo_dem=pt.bo_dem)
    if not cg.bat:
        return replace(pt, bo_giao=bo), []
    luong = bat_dau_luong_giao(bo, dung, chu_ky=cg.chu_ky_giay)
    return replace(pt, bo_giao=bo, chon_phieu=an_toan(bo.chon, None, "chon"),
                   con_hop_le_phieu=an_toan(bo.con_hop_le, False, "con_hop_le")), luong
```

`tram/giao_viec/tick_pipeline.py`

```python
"""Vòng tick — phần đẩy pipeline (spec 4 §10 bước 1, §6.2, §6.4, §5.1 điều kiện 9): với mỗi bead trạm đang giữ
(`in_progress`, assignee trạm) tính `buoc_ke_tiep`: `kiem_lai` → chạy kiểm lại; `cot_3` → vào cột 3; `code`/`qc`
mà `not du_mot_phieu` → escalation `het-ngan-sach`. Dự án thiếu `moi_truong_kiem` → MỘT escalation mở mỗi dự án.
4a-2: `viec` chọn phần việc theo pha — pha nhanh chỉ `het_ngan_sach` (G5), pha Git làm phần còn lại."""
from datetime import datetime
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.deploy.cam import cam_tu_lenh
from tram.duong_dan import tram_home
from tram.giao_viec.dieu_kien import ASSIGNEE, ly_do_khong_giao
from tram.giao_viec.escalation import tao_escalation
from tram.giao_viec.kiem_lai import kiem_lai
from tram.giao_viec.ngan_sach import bat_dau_chu_ky, du_mot_phieu, ngan_sach_phieu
from tram.giao_viec.pipeline import buoc_ke_tiep, sha_code_hop_le
from tram.giao_viec.spec_merge import feature_da_merge
from tram.giao_viec.su_kien import SK, cua_so, ghi_mot_lan, moi_nhat, su_kien_bead
from tram.giao_viec.tick_cot_3 import vao_cot_3_an_toan
from tram.giao_viec.tieu_chi import digest_tieu_chi
from tram.giao_viec.ung_vien import trang_thai_bead, viec_ton_cua
from tram.phieu.kho import KhoPhieu

VIEC_NHANH = frozenset({"het_ngan_sach"})
VIEC_GIT = frozenset({"kiem_lai", "cot_3", "moi_truong"})


def _esc_moi_truong_dang_mo(kho: KhoPhieu, du_an: str) -> bool:
    tao = {r[0] for r in kho.db.execute("SELECT json_extract(du_lieu, '$.escalation_id') FROM su_kien WHERE du_an = ?"
                                        " AND loai = 'escalation.tao' AND json_extract(du_lieu, '$.ly_do') ="
                                        " 'thieu-moi-truong-kiem'", (du_an,))}
    dong = {r[0] for r in kho.db.execute("SELECT json_extract(du_lieu, '$.escalation_id') FROM su_kien WHERE"
                                         " du_an = ? AND loai = 'escalation.dong'", (du_an,))}
    return bool(tao - dong)


def _kiem_lai(bo, kho: KhoPhieu, da: DuAn, bd, b, ds: list[SK], kg: Path, luc: datetime) -> str:
    w = cua_so(ds)
    code = moi_nhat(w, "giao.nhan", lambda s: s.du_lieu.get("buoc") == "code")
    p, sha = kho.lay(code.du_lieu["giao_id"]).phieu, sha_code_hop_le(w)
    if p.can_lenh_kiem and bo.boc is None and bo.kiem_tu_xa is None:
        return "cho_boc"                                 # chưa có principal tram-kiem (S6) — không chạy dưới quyền trạm
    ham = bo.kiem_tu_xa or kiem_lai
    them = {'luot': p.luot} if bo.kiem_tu_xa is not None else {}
    kq = ham(kg, da, giao_id=p.giao_id, commit=sha, lenh_kiem=list(p.lenh_kiem),
                  lenh_cho_phep=list(p.lenh_cho_phep),
                  chay_lenh=p.can_lenh_kiem, thu_muc=bo.thu_muc_kiem or tram_home() / "kiem",
                  thu_muc_log=tram_home() / "log" / "kiem-lai", boc=bo.boc or (lambda a: a), env_goc=bo.env_goc,
                  don_sach=bo.don_sach, kill=bo.kill, cong=bo.cong, boc_luot=bo.boc_luot,
                  them_cam=cam_tu_lenh(kho.db, kg, da, sha), **them)
    if kq.loi is not None:
        tao_escalation(bd, kho, da.ten, b, ly_do=kq.loi, cau_hoi="", giao_id=p.giao_id, nguon=f"kl-{sha}", luc=luc)
        if kq.loi in ("thieu-moi-truong-kiem", "cay-khac-nguon"):
            return "escalation"                          # không ghi kiem.lai: trả lời xong thì kiểm lại (dòng 5)
    from tram.quan_kiem.fencing import ghi_ket_qua
    return ghi_ket_qua(kho, da, p, sha, {
        "giao_id": p.giao_id, "bead_id": b.id, "luot": p.luot, "commit": sha,
        "digest_tieu_chi": digest_tieu_chi(list(p.tieu_chi)), "dat": kq.dat,
        "ket_qua": list(kq.ket_qua), "digest_log": kq.digest_log, "cham_cam": list(kq.cham_cam)}, luc)


def day_pipeline(bo, kho: KhoPhieu, da: DuAn, bd, beads: list, san_sang: set[str], kg: Path | None,
                 luc: datetime, *, viec: frozenset[str] = VIEC_NHANH | VIEC_GIT) -> dict[str, int]:
    theo_id, ton, dem = {b.id: b for b in beads}, viec_ton_cua(kho, da.ten), {}
    merge = feature_da_merge(kho, da, beads, kg) if kg is not None else frozenset()
    for b in beads:
        ly = ly_do_khong_giao(b, theo_id, san_sang, da, merge)
        if ly == "thieu-moi-truong-kiem" and "moi_truong" in viec and not _esc_moi_truong_dang_mo(kho, da.ten):
            tao_escalation(bd, kho, da.ten, b, ly_do=ly, cau_hoi="", giao_id=None, nguon=f"du-an-{luc:%Y%m%d%H%M}",
                           luc=luc)
            dem["escalation"] = dem.get("escalation", 0) + 1
        if ly is not None or b.status != "in_progress" or b.assignee != ASSIGNEE:
            continue
        ds = su_kien_bead(kho, da.ten, b.id)
        buoc, kq = buoc_ke_tiep(ds, trang_thai_bead(kho, da.ten, b, theo_id, ton)), None
        if buoc == "kiem_lai" and kg is not None and "kiem_lai" in viec:
            kq = _kiem_lai(bo, kho, da, bd, b, ds, kg, luc)
        elif buoc == "cot_3" and kg is not None and "cot_3" in viec:
            kq = vao_cot_3_an_toan(bd, kho, kg, da, b, luc, gitnexus=bo.p4c.gitnexus)
        elif buoc in ("code", "qc") and "het_ngan_sach" in viec and not du_mot_phieu(
                kho, ds, ngan_sach_phieu(buoc, da.giao.ngan_sach), da.giao.ngan_sach.bead):
            kq = "het_ngan_sach" if tao_escalation(bd, kho, da.ten, b, ly_do="het-ngan-sach", cau_hoi="", giao_id=None,
                                                   nguon=f"ns-{bat_dau_chu_ky(ds)}", luc=luc) else None
        if kq:
            dem[kq] = dem.get(kq, 0) + 1
    return dem
```

`tram/giao_viec/kiem_san_sang.py`

```python
"""`tram giao kiem` — kiểm sẵn sàng của bộ giao việc trước khi bật `giao_viec.bat`: đây là BƯỚC KIỂM KHI CHẠY THẬT
của mọi adapter chờ cổng (S6 principal `tram-kiem`, S7 kho kiểm/remote, 3a-2 file quyền). Chưa chứng minh được → ĐỎ;
không đánh dấu sẵn sàng bằng bản giả. Mọi lần chạy thật đi qua `chay`/`chay_lenh` tiêm được (test dùng bản giả).
Lát 3c: các mục principal `tram-kiem` ở `kiem_principal.py` (3C-D6, hợp đồng P1 H7 — dưới khoá, chỉ khi cổng chưa
đóng, UID thực, probe qua lượt tạm trong hồ sơ Seatbelt)."""
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.giao_viec.git_kiem import kho_kiem
from tram.giao_viec.kho_kiem_tao import url_origin
from tram.giao_viec.kiem_principal import kiem_principal
from tram.giao_viec.quyen import KHONG_CO, phien_ban_quyen
from tram.tho.kiem_may import MucKiem


def _muc(ten: str, dat: bool, chi_tiet: str, *, khong_dat: str = "do") -> MucKiem:
    return MucKiem(ten, "xanh" if dat else khong_dat, chi_tiet)


def kiem_du_an(da: DuAn) -> list[MucKiem]:
    kg, mt = kho_kiem(da.ten), da.moi_truong_kiem
    if (kg / ".git").exists():
        cu, goc = url_origin(kg), url_origin(da.duong_dan)
        ra = [_muc(f"{da.ten}: kho kiểm", bool(cu) and cu == goc, f"origin {cu} — dự án {goc}")]
    else:
        ra = [_muc(f"{da.ten}: kho kiểm", False, f"chưa có — chạy `tram giao kho-kiem {da.ten}`")]
    return ra + [_muc(f"{da.ten}: moi_truong_kiem", mt is not None and mt.file.is_file(), str(mt.file if mt else "")),
                 _muc(f"{da.ten}: lệnh kiểm mặc định", bool(da.giao.lenh_kiem_mac_dinh),
                      "không có thì mỗi bead phải nêu lệnh trong design", khong_dat="vang")]


def kiem_giao_viec(cg: CauHinhGiaoViec, cac_du_an: list[DuAn], *, goc_quyen: Path | None = None,
                   **kw) -> list[MucKiem]:
    ra = [_muc("giao_viec.bat", cg.bat, "bật" if cg.bat else "tắt — tram-api không phát phiếu", khong_dat="vang")]
    ra += [_muc(f"file quyền {v}", phien_ban_quyen(v, goc=goc_quyen) != KHONG_CO, "vai/quyen/<vai>.json — 3a-2")
           for v in ("coder", "qc")]
    from tram.quan_kiem.client import CongTuXa
    try:
        tt = CongTuXa().trang_thai()['trang_thai']
        ra.append(_muc('Bộ quản lý kiểm', tt == 'mo', tt))
    except (OSError, ValueError, KeyError):
        ra.append(_muc('Bộ quản lý kiểm', False, 'không liên lạc được — không chạy kiểm cục bộ'))
    for da in cac_du_an:
        ra += kiem_du_an(da)
    return ra
```

`tram/giao_viec/lenh.py`

```python
"""Lệnh `tram giao tick [--thu]`, `tram giao kho-kiem <du_an> [--dong-y]`, `tram giao kiem` (spec 4 §10; 4a-2),
`tram giao mo-cong-kiem` (3C-D4: Đại ca mở lại cổng kiểm lại sau khi xem lý do đóng), `tram giao nghiem-thu-kiem`
(harness S6, `lenh_nghiem_thu.py`) —
chạy ở TÀI KHOẢN TRẠM. `tick` chạy ba pha như các luồng của tram-api, qua cùng khoá file (không trùng vòng đang chạy).
Bộ giao việc tắt (`giao_viec.bat: false`) thì chỉ cho `tick --thu` (không ghi beads, không chạy lệnh)."""
import argparse
import sys


def _bo():
    from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
    from tram.cau_hinh.tram import nap_cau_hinh_tram
    from tram.giao_viec.noi_that import dung_bo_that
    cg = nap_cau_hinh_giao_viec()
    return cg, dung_bo_that(cg, nap_cau_hinh_tram())


def _tick(args) -> int:
    from tram.giao_viec.luong import KHOA_DEPLOY, KHOA_GIT, KHOA_NHANH, chay_vong
    from tram.giao_viec.tick import vong_deploy, vong_git, vong_nhanh
    cg, bo = _bo()
    if not cg.bat and not args.thu:
        print("giao_viec.bat đang tắt — chỉ chạy được `tram giao tick --thu`.")
        return 1
    pha = [("nhanh", KHOA_NHANH, lambda: vong_nhanh(bo, thu=args.thu))]
    if not args.thu:
        pha += [("git", KHOA_GIT, lambda: vong_git(bo)), ("deploy", KHOA_DEPLOY, lambda: vong_deploy(bo))]
    for ten, khoa, lam in pha:
        kq = chay_vong(khoa, lam)
        print(f"pha {ten}: " + ("đang có vòng khác chạy — bỏ qua" if kq is None else str(kq or "không có việc")))
    return 0


def _kho_kiem(args) -> int:
    from tram.cau_hinh.du_an import nap_du_an
    from tram.giao_viec.kho_kiem_tao import in_ke_hoach, lap_ke_hoach, thuc_hien
    da = nap_du_an(args.du_an)
    try:
        kh = lap_ke_hoach(da)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    print(in_ke_hoach(kh))
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    print(f"Xong: origin/{da.nhanh_chinh} = {thuc_hien(kh, da.nhanh_chinh)}")
    return 0


def _kiem(args) -> int:
    from tram.giao_viec.kiem_san_sang import kiem_giao_viec
    from tram.tho.kiem_may import in_ket_qua
    cg, bo = _bo()
    van_ban, ma = in_ket_qua(kiem_giao_viec(cg, bo.cac_du_an()))
    print(van_ban)
    return ma


def _mo_cong(args) -> int:
    from tram.giao_viec.ban_chep import LoiBanChep, giu_khoa
    _, bo = _bo()
    if bo.cong is None:
        print("Chưa khai cach_ly.tram_kiem — không có cổng kiểm lại.")
        return 2
    print(f"Trạng thái hiện tại: {bo.cong.trang_thai()}")
    if not args.dong_y and input("Gõ dong-y để thu hồi, quan sát và mở lại: ").strip() != "dong-y":
        return 1
    try:
        bo.cong.mo_lai()
    except LoiBanChep as e:
        print(f"Vẫn đóng: {e}", file=sys.stderr)
        return 1
    print("Đã mở cổng kiểm lại.")
    return 0


def them_lenh_giao(sub) -> None:
    g = sub.add_parser("giao", help="Bộ giao việc (phần 4)").add_subparsers(dest="lenh_giao", required=True)
    t = g.add_parser("tick", help="Chạy một vòng tick (pha nhanh, pha Git, rồi pha deploy)")
    t.add_argument("--thu", action="store_true", help="Chỉ ghi sự kiện suy từ beads: không ghi beads, không chạy lệnh")
    t.set_defaults(ham=_tick)
    k = g.add_parser("kho-kiem", help="Tạo/cập nhật kho kiểm của trạm từ remote dự án (liệt kê, chờ dong-y)")
    k.add_argument("du_an")
    k.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ khi Đại ca đã đọc kế hoạch)")
    k.set_defaults(ham=_kho_kiem)
    g.add_parser("kiem", help="Kiểm sẵn sàng: xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ").set_defaults(ham=_kiem)
    c = g.add_parser("mo-cong-kiem", help="Thu hồi + quan sát tram-kiem rồi mở lại cổng kiểm lại (chờ dong-y)")
    c.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ khi Đại ca đã xem lý do đóng)")
    c.set_defaults(ham=_mo_cong)
    _them_nghiem_thu(g)


def _them_nghiem_thu(g) -> None:
    def lenh_nghiem_thu(args):
        print("D159: dùng python -m tram.quan_kiem.g4 qua bộ quản lý system; xem plan G4.")
        return 2
    h = g.add_parser("nghiem-thu-kiem", help="S6: harness kiểm lại trên kho nháp dưới principal thật (mã ≠ 0 nếu đỏ)")
    h.add_argument("--tai-sinh", action="store_true", help="Thử cài lịch cron/at/launchd như mã agent rồi chờ (G4)")
    h.add_argument("--cho", type=float, default=300.0, help="Giây chờ quá giờ hẹn của lịch (mặc định 300, ≥ 240)")
    h.add_argument("--trong", action="store_true", help=argparse.SUPPRESS)
    h.add_argument("--dau-ino", type=int, default=None, help=argparse.SUPPRESS)
    h.add_argument("--cha", type=int, default=None, help=argparse.SUPPRESS)
    h.set_defaults(ham=lenh_nghiem_thu)
```

`tram/quan_kiem/fencing.py`

```python
"""Nhận kết quả dưới BEGIN IMMEDIATE; phiếu đã bị thay không được công bố pass muộn."""
from tram.giao_viec.pipeline import sha_code_hop_le
from tram.giao_viec.su_kien import cua_so, su_kien_bead, da_co


def ghi_ket_qua(kho, da, p, sha, d, luc):
    with kho.giao_dich():
        moi = kho.lay(p.giao_id)
        if moi is None or moi.ket_thuc in ('thu_hoi', 'het_han') or \
                kho.luot_hien_hanh(da.ten, p.bead_id) != p.luot or \
                sha_code_hop_le(cua_so(su_kien_bead(kho, da.ten, p.bead_id))) != sha:
            return 'luot-cu'
        if not da_co(kho, da.ten, 'kiem.lai', {'giao_id': p.giao_id, 'commit': sha}):
            kho.ghi_su_kien(da.ten, 'kiem.lai', d, bead_id=p.bead_id, luc=luc, tac_nhan='tram/giao-viec')
    return 'kiem_lai'
```

- [ ] **Step 4 — GREEN, rồi kiểm hồi quy cuối plan:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_noi.py tests/test_noi_giao_viec.py tests/test_giao_kiem.py
```

## Task 6 — G4 tích hợp bản thật, không dựng bộ đo riêng

**Files:**

- Create `tests/test_quan_kiem_g4.py`
- Modify `tram/giao_viec/do_launchd_g4.py`
- Modify `tram/giao_viec/mau_g4.py`
- Create `tram/quan_kiem/doi_chung_g4.py`
- Create `tram/quan_kiem/g4.py`

- [ ] **Step 1 — test nguyên văn:**

`tests/test_quan_kiem_g4.py`

```python
from pathlib import Path
from types import SimpleNamespace

import pytest


def test_g4_giu_nguyen_policy_du_an(tmp_path, monkeypatch):
    import io
    import tarfile
    import json
    import tram.quan_kiem.g4 as m
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode='w') as f:
        t = tarfile.TarInfo('README')
        t.size = 4
        f.addfile(t, io.BytesIO(b'fake'))
    monkeypatch.setattr(m, 'git_nhap', lambda *a: 'a' * 40)
    monkeypatch.setattr(m, 'archive', lambda *a: b.getvalue())
    monkeypatch.setattr(m, 'Path', lambda x: tmp_path / 'dac' if x == '/Users/Shared/tram-g4-quan-kiem' else Path(x))
    policy = {'mac_dinh': ['python -m pytest'], 'cho_phep': ['python -m pytest']}
    c = {'home_tram': str(tmp_path / '.tram'), 'policy': {'repo': policy}}
    m.chuan_bi(tmp_path / 'g4', c, 'repo', tmp_path / 'fake')
    info = json.loads((tmp_path / 'g4/lan.json').read_text())
    assert info['du_an'] == 'repo' and info['policy'] == policy
    assert (tmp_path / 'g4/kho/README').read_bytes() == b'fake'


def test_bootout_vang_daemon_duoc_nhung_loi_quan_sat_khong_duoc():
    from tram.chu.dung_quan_kiem import dung_daemon
    calls = []
    def run(a, **kw):
        calls.append(a)
        return SimpleNamespace(returncode=113, stdout=b'',
                               stderr=b'Could not find service "vn.tram.quan-kiem" in domain for system\n')
    dung_daemon(run)
    assert calls[-1][-2:] == ['print', 'system/vn.tram.quan-kiem']
    with pytest.raises(OSError, match='chua-chung-minh'):
        dung_daemon(lambda *a, **kw: SimpleNamespace(returncode=1, stdout=b'', stderr=b'permission denied'))
```

- [ ] **Step 2 — chạy RED trước mã:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_g4.py
```

RED đã quan sát trong phiên soạn:

```text
test_g4_doc_co_doi_chung_va_chan_listing: AssertionError vì thiếu phép ls; 1 failed, 1 passed.
Sau review đổi mọi phép phủ định sang if-command-then-exit để không mắc ngoại lệ errexit của shell.
```

- [ ] **Step 3 — mã nguyên văn:**

`tram/giao_viec/do_launchd_g4.py`

```python
"""Ma trận launchctl G4 dùng sleep cố định; receipt trước ghi; không coi lỗi OS là Seatbelt chặn."""
import json
import os
import plistlib
import re
import shlex
import time
from tempfile import NamedTemporaryFile
from pathlib import Path

from tram.giao_viec.mau_g4 import ghi_receipt, nhan_luot


def _ghi(tep: Path, **gia_tri) -> None:
    data = json.loads(tep.read_text())
    data.update(gia_tri)
    with NamedTemporaryFile(mode='w', dir=tep.parent, delete=False) as f:
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
    Path(f.name).replace(tep)


def _vang(ma, out: bytes, nhan: str) -> bool:
    pattern = rb'Could not find service \"?' + re.escape(nhan.encode()) + rb'\"?(?: in domain[^\n]*)?\s*'
    return ma == 113 and re.fullmatch(pattern, out.strip()) is not None


def _quan_sat_don(pk, mien: list[str], nhan: str, chay, uids=None) -> tuple[list[dict], bool]:
    thay, sach = [], True
    for m in mien:
        uid_kiem = mien[0].split('/')[1]
        boc = pk.boc_lenh if m in (f'user/{uid_kiem}', f'gui/{uid_kiem}') else (lambda a: a)
        target = f'{m}/{nhan}'
        ma, out = chay(boc(['/bin/launchctl', 'print', target]))
        vang_mien = (m.startswith('gui/') and ma == 112 and out.strip() ==
                     f"Bad request.\nCould not find domain for user gui: {m.split('/')[1]}".encode())
        if _vang(ma, out, nhan) or vang_mien:
            continue
        pid = re.search(rb'^\s*pid = ([1-9][0-9]*)\s*$', out, re.M) if ma == 0 else None
        if ma != 0:
            sach = False
            continue
        row = {'mien': m, 'co_service': True, 'pid': int(pid[1]) if pid else None, 'danh_tinh': None}
        if pid:
            rc, ps = chay(['/bin/ps', '-p', pid[1].decode(), '-o', 'uid=,ruid=,lstart='])
            text = ps.decode(errors='replace').strip()
            if rc == 0 and re.fullmatch(r'\d+\s+\d+\s+\w{3}\s+\w{3}\s+\d+\s+[\d:]+\s+\d{4}', text):
                row['danh_tinh'] = text
                allowed = set(uids or (int(mien[0].split('/')[1]), int(mien[-1].split('/')[1])))
                uid, ruid = map(int, text.split()[:2])
                sach = sach and uid == ruid and uid in allowed
        sach = sach and row['danh_tinh'] is not None
        thay.append(row)
        chay(boc(['/bin/launchctl', 'bootout', target]))
        rc, con = chay(boc(['/bin/launchctl', 'print', target]))
        sach = sach and _vang(rc, con, nhan)
        if pid:
            rc, ps = chay(['/bin/ps', '-p', pid[1].decode(), '-o', 'uid=,ruid=,lstart='])
            sach = sach and rc == 1 and not ps.strip()
    return thay, sach


def do_launchd(pk, luot: Path, receipt: Path, uid: int, operator: int, chay, *, mien=None, uids=None) -> list[dict]:
    mien = mien or [f'user/{uid}', f'gui/{uid}', f'gui/{operator}']
    ghi_receipt(receipt, luot, uid, operator, mien=mien)
    nhan = nhan_luot(luot)
    rows = []
    for ho_so, boc in (('ngoai', pk.boc_lenh), ('trong', pk.boc_luot(luot))):
        for binary, exe in (('goc', '/bin/launchctl'), ('copy', str(luot / 'launchctl-copy'))):
            exec_ma, _ = chay(boc([exe, 'help', 'submit']))
            for op in ('submit', 'bootstrap'):
                bat_dau = time.monotonic()
                def case_chay(argv):
                    if time.monotonic() - bat_dau > 45:
                        raise TimeoutError('ca G4 hết ngân sách 60 giây')
                    return chay(argv)
                nguon = ('submit' if op == 'submit' else 'launchd') + ('copy' if binary == 'copy' else '')
                label = f'{nhan}.{nguon}'
                if op == 'submit':
                    argv = [exe, op, '-l', label, '--', '/bin/sleep', '10']
                else:
                    p = luot / f'{nguon}.plist'
                    data = plistlib.dumps({'Label': label, 'ProgramArguments': ['/bin/sleep', '10'],
                                           'RunAtLoad': True}).decode()
                    script = f'printf %s {shlex.quote(data)} > {shlex.quote(str(p))}'
                    rc, _ = case_chay(pk.boc_lenh(['/bin/sh', '-ec', script]))
                    if rc != 0:
                        raise ValueError('không dựng được plist G4')
                    argv = [exe, op, mien[0], str(p)]
                _ghi(receipt, trang_thai='can-don', ca_hien_tai=f'{ho_so}:{binary}:{op}')
                ma, _ = case_chay(boc(argv))
                thay, sach = _quan_sat_don(pk, mien, label, case_chay, uids)
                sach = sach and not (ma == 0 and not thay)  # Nhận job nhưng mất dấu miền: giữ fixture.
                ket_luan = 'chua-ket-luan'
                if ho_so == 'trong' and (ma == 0 or thay):
                    ket_luan = 'lot'
                elif sach and exec_ma == 0:
                    if ho_so == 'ngoai' and ma == 0 and thay:
                        ket_luan = 'doi-chung-duong'
                    elif ho_so == 'trong' and ma not in (None, 0):
                        ket_luan = 'cho-bang-chung-os'
                rows.append({'ket_luan': ket_luan, 'ho_so': ho_so, 'binary': binary, 'lenh': op, 'exec_ma': exec_ma,
                             'ma': ma, 'service': thay, 'don': sach})
                _ghi(receipt, trang_thai='da-don' if sach else 'can-don', ket_qua=rows)
                if not sach or (ho_so == 'trong' and (ma == 0 or thay)):
                    return rows
    return rows
```

`tram/giao_viec/mau_g4.py`

```python
"""Dựng dữ liệu giả của G4; không đọc dữ liệu cá nhân có sẵn."""
import json
import hashlib
import os
import re
import subprocess
import secrets
import shlex
from pathlib import Path


def tao_mau(pk, luot: Path, home: Path, tam: Path, chay, *, receipt: Path | None = None) -> dict:
    run = secrets.token_hex(12)
    cay_home, cay_dac = home / f'tram-g4-canary-{run}', tam / f'tram-g4-dac-{run}'
    if receipt is not None:
        with receipt.open('x') as f:
            json.dump({'luot': str(luot), 'home': str(cay_home), 'dac': str(cay_dac)}, f)
            f.flush()
            os.fchmod(f.fileno(), 0o600)
            os.fsync(f.fileno())
    dau = secrets.token_hex(32)
    for cay in (cay_home, cay_dac):
        cay.mkdir()
        cay.chmod(0o755)
        (cay / 'canary').write_text(dau)
        (cay / 'canary').chmod(0o644)
    q = shlex.quote
    mau, link = luot / 'mau', luot / 'canary-link'
    script = (f'mkdir -p {q(str(luot))} {q(str(luot) + ".nha/tmp")}; '
              f'printf %s {q(dau)} > {q(str(mau))}; '
              f'ln -s {q(str(cay_home / "canary"))} {q(str(link))}; '
              f'cp /bin/launchctl {q(str(luot / "launchctl-copy"))} && '
              f'cmp -s /bin/launchctl {q(str(luot / "launchctl-copy"))}')
    ma, _ = chay(pk.boc_lenh(['/bin/sh', '-ec', script]))
    if ma != 0:
        raise ValueError('không dựng được fixture G4; giữ cây để kiểm/dọn')
    tep_home, tep_dac = cay_home / 'canary', cay_dac / 'canary'
    firmlink = Path('/System/Volumes/Data') / tep_home.relative_to('/')
    return {'home': tep_home, 'dac': tep_dac, 'mau': mau, 'tep': [tep_home, link, firmlink, tep_dac, mau]}


def smoke_toolchain(pk, luot: Path, chay) -> dict[str, bool]:
    from tram.kiem.toolchain import PYTHON, UV, GIT, NODE, bien_kiem
    env = ['/usr/bin/env', '-i', f'HOME={luot}.nha', f'TMPDIR={luot}.nha/tmp',
           *(f'{k}={v}' for k, v in bien_kiem(f'{luot}.nha').items()), 'UV_OFFLINE=1']
    lenh = {
        'venv': [f'{PYTHON}/bin/python3.12', '-B', '-I', '-m', 'venv', '--without-pip', str(luot / 'venv')],
        'python': [str(luot / 'venv/bin/python'), '-I', '-B', '-c',
                   f'import sys; assert sys.base_prefix == {PYTHON!r}'],
        'uv': [f'{UV}/bin/uv', '--version'], 'git': [f'{GIT}/bin/git', '--version'],
        'node': [f'{NODE}/bin/node', '--version'], 'npm': [f'{NODE}/bin/npm', '--version'],
    }
    return {ten: chay(pk.boc_luot(luot)([*env, *argv]))[0] == 0 for ten, argv in lenh.items()}


def do_canary(pk, luot: Path, tep: list[Path], mau: Path, *, chay=subprocess.run) -> dict:
    """Bên gọi chuẩn bị LUOT/NHA, mẫu và canary; chỉ trả mã hữu hạn, lỗi/timeout thành None."""
    from tram.giao_viec.kich_ban_nghiem_thu import kich_ban_canary
    script = kich_ban_canary(tep, mau)
    ra = {}
    for ten, boc in (('ngoai', pk.boc_lenh), ('trong', pk.boc_luot(luot))):
        try:
            kq = chay(boc(['/bin/sh', '-c', script]), capture_output=True, text=True, timeout=15)
            dong = kq.stdout.splitlines()
            hop_le = len(dong) == len(tep) and all(
                re.fullmatch(rf'{i}:(match|different|no-match):(yes|no):(yes|no)', d) for i, d in enumerate(dong))
            ra[ten] = dong if kq.returncode == 0 and hop_le else None
        except (OSError, subprocess.SubprocessError):
            ra[ten] = None
    return ra


NGUON_LAUNCHD = ('submit', 'launchd', 'submitcopy', 'launchdcopy')


def nhan_luot(dau: Path) -> str:
    return 'vn.tram.nghiem-thu.' + hashlib.sha256(str(dau).encode()).hexdigest()[:24]


def ghi_receipt(tep: Path, dau: Path, uid_kiem: int, uid_tram: int, *, mien=None) -> None:
    if uid_kiem <= 0 or uid_tram <= 0 or uid_kiem == uid_tram:
        raise ValueError('UID nghiệm thu phải khác nhau và khác root')
    nhan = nhan_luot(dau)
    dich = [{'mien': m, 'nhan': f'{nhan}.{n}'} for m in
            (mien or (f'user/{uid_kiem}', f'gui/{uid_kiem}', f'gui/{uid_tram}')) for n in NGUON_LAUNCHD]
    with tep.open('x', encoding='utf-8') as f:
        json.dump({'run': nhan, 'trang_thai': 'chua-do', 'dich': dich}, f, ensure_ascii=False)
        f.flush()
        os.fchmod(f.fileno(), 0o600)
        os.fsync(f.fileno())


def lenh_don(receipt: dict) -> list[list[str]]:
    """Chỉ sinh argv để chủ miền duyệt/chạy; không biến exit 0 thành chứng cứ sạch."""
    run = receipt.get('run', '')
    if not re.fullmatch(r'vn\.tram\.nghiem-thu\.[a-f0-9]{24}', run):
        raise ValueError('run receipt sai dạng')
    ra = []
    for dich in receipt['dich']:
        mien, nhan = dich['mien'], dich['nhan']
        if not re.fullmatch(r'(?:(?:user|gui|login)/[1-9][0-9]*|system)', mien) or nhan not in {
            f'{run}.{n}' for n in NGUON_LAUNCHD
        }:
            raise ValueError('đích dọn không thuộc receipt của run')
        ra.append(['/bin/launchctl', 'bootout', f'{mien}/{nhan}'])
    return ra


def receipt_truoc_luot(dau: Path, uid_kiem: int) -> None:
    import os
    from tram.duong_dan import tram_home
    goc = tram_home() / 'log' / 'nghiem-thu'
    goc.mkdir(parents=True, exist_ok=True)
    ghi_receipt(goc / f'receipt-{nhan_luot(dau)}.json', dau, uid_kiem, os.getuid())
```

`tram/quan_kiem/doi_chung_g4.py`

```python
"""Đối chứng G4 tích hợp worker sản phẩm; chỉ dữ liệu cố định, không RPC chạy shell Uq."""
import ctypes
import json
import os
import pwd
from pathlib import Path

from tram.giao_viec.ban_chep import _chay
from tram.giao_viec.do_launchd_g4 import do_launchd
from tram.giao_viec.ngu_canh_kiem import SECURITY


def doi_chung(c, pk, wt, id_):
    sid, flags = ctypes.c_uint32(), ctypes.c_uint32()
    if ctypes.CDLL(SECURITY).SessionGetInfo(ctypes.c_int32(-1), ctypes.byref(sid), ctypes.byref(flags)):
        raise OSError('khong-doc-duoc-session')
    log = Path(c['home']) / 'log'
    log.mkdir(mode=0o700, exist_ok=True)
    uid = pwd.getpwnam(pk.ten).pw_uid
    def chay(a):
        r = _chay(a, kill=pk.kill_nhom, timeout=15)
        out = (r.stdout or b'') + (r.stderr or b'')
        driver = log / f'driver-{id_}.jsonl'
        with driver.open('a') as f:
            os.fchmod(f.fileno(), 0o600)
            if f.tell() < 65536:
                f.write(json.dumps({'argv': a, 'ma': r.returncode,
                                    'out': out[:2048].decode(errors='replace')}) + '\n')
        return r.returncode, out
    _chay(pk.boc_lenh(['/bin/cp', '/bin/launchctl', str(wt / 'launchctl-copy')]), kill=pk.kill_nhom, check=True)
    mien = [f'user/{uid}', f'gui/{uid}', f'user/{c["uid_quan"]}', f'gui/{c["uid_quan"]}',
            f'login/{sid.value}', 'system', f'gui/{c["uid_tram"]}']
    paths = [Path(c['home_tram']).parent / 'tram-g4-quan-kiem/canary',
             Path('/Users/Shared/tram-g4-quan-kiem/canary')]
    doc = []
    for p in paths:
        ma, b = chay(pk.boc_lenh(['/bin/cat', str(p)]))
        doc.append({'ma': ma, 'doc_mau': ma == 0 and b == b'TRAM-G4-NONSECRET\n'})
    (log / f'context-{id_}.json').write_text(json.dumps({
        'pid': os.getpid(), 'ppid': os.getppid(), 'uid': os.getuid(), 'gid': os.getgid(),
        'groups': os.getgroups(), 'asid': sid.value, 'flags': flags.value, 'canary_ngoai_ho_so': doc}))
    from tram.giao_viec.mau_g4 import do_canary, smoke_toolchain
    import shlex
    mau, link = wt / 'mau', wt / 'canary-link'
    script = (f"printf 'TRAM-G4-NONSECRET\\n' > {shlex.quote(str(mau))}; "
              f"ln -s {shlex.quote(str(paths[0]))} {shlex.quote(str(link))}")
    _chay(pk.boc_luot(wt)(['/bin/sh', '-ec', script]), kill=pk.kill_nhom, check=True)
    firmlink = Path('/System/Volumes/Data') / paths[0].relative_to('/')
    def run(a, **kw):
        r = _chay(a, kill=pk.kill_nhom, timeout=15)
        from types import SimpleNamespace
        return SimpleNamespace(returncode=r.returncode, stdout=r.stdout.decode())
    canary = do_canary(pk, wt, [paths[0], link, firmlink, paths[1], mau], mau, chay=run)
    expected = ['0:no-match:no:no', '1:no-match:no:yes', '2:no-match:no:no',
                '3:no-match:no:no', '4:match:yes:yes']
    if canary['trong'] != expected or not all(smoke_toolchain(pk, wt, chay).values()):
        raise OSError('g4-canary-hoac-cong-cu-khong-dat')
    (log / f'canary-{id_}.json').write_text(json.dumps(canary))
    rows = do_launchd(pk, wt, log / f'launchd-{id_}.json', uid, c['uid_quan'], chay,
                      mien=mien, uids=[uid, c['uid_quan'], c['uid_tram']])
    if not rows or any(not r['don'] or r['ket_luan'] == 'lot' for r in rows):
        raise OSError('g4-lot-hoac-don-chua-ro')
    if doc[0]['ma'] == 0 or not doc[1]['doc_mau']:
        raise OSError('g4-doi-chung-doc-khong-dat')
```

`tram/quan_kiem/g4.py`

```python
"""G4 dùng kho giả đã chuẩn bị cho đúng lệnh dự án; không thêm lệnh vào policy."""
import argparse
import io
import json
from pathlib import Path

from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.cau_hinh.du_an_giao import CauHinhGiao
from tram.giao_viec.kich_ban_nghiem_thu import git_nhap
from tram.quan_kiem.cau_hinh import nap
from tram.quan_kiem.client import kiem_tu_xa
from tram.quan_kiem.nguon import archive
from tram.quan_kiem.nhan import giai_nen


def chuan_bi(goc, c, ten, fixture):
    if ten not in c['policy']:
        raise ValueError('du-an-chua-dang-ky')
    # Người vận hành duyệt kho dữ liệu giả trước dong-y; không tự lấy repo dự án thật.
    source = git_nhap(fixture, 'rev-parse', 'HEAD').strip()
    data = archive(fixture, source)
    goc.mkdir(mode=0o700)
    kho = goc / 'kho'
    kho.mkdir()
    giai_nen(io.BytesIO(data), kho)
    git_nhap(kho, 'init', '-q', '-b', 'main')
    git_nhap(kho, 'add', '.')
    git_nhap(kho, '-c', 'user.name=Tram G4', '-c', 'user.email=g4@invalid', 'commit', '-qm', 'Fixture G4')
    sha = git_nhap(kho, 'rev-parse', 'HEAD').strip()
    git_nhap(kho, 'update-ref', 'refs/remotes/origin/main', sha)
    home = Path(c['home_tram']).parent / 'tram-g4-quan-kiem'
    dac = Path('/Users/Shared/tram-g4-quan-kiem')
    (goc / 'fixture.json').write_text(json.dumps({'home': str(home), 'dac': str(dac)}))
    for path in (home, dac):
        path.mkdir(mode=0o755)
        (path / 'canary').write_text('TRAM-G4-NONSECRET\n')
        (path / 'canary').chmod(0o644)
    (goc / 'env.testing').write_text('NGHIEM_THU=1\n')
    (goc / 'env.testing').chmod(0o600)
    (goc / 'lan.json').write_text(json.dumps({'sha': sha, 'du_an': ten, 'policy': c['policy'][ten]}))
    return sha


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('buoc', choices=['chuan-bi', 'sach'])
    p.add_argument('thu_muc', type=Path)
    p.add_argument('--du-an')
    p.add_argument('--fixture', type=Path)
    a = p.parse_args(argv)
    c = nap()
    if not c['g4']:
        raise ValueError('chi-chay-khi-cai-che-do-g4')
    if a.buoc == 'chuan-bi' and (a.du_an not in c['policy'] or a.fixture is None):
        p.error('chuan-bi cần --du-an đã đăng ký và --fixture là kho Git dữ liệu giả đã duyệt')
    print('G4 qua socket thật; kho giả:', a.fixture, 'dự án:', a.du_an)
    print('Policy:', json.dumps(c['policy'], ensure_ascii=False))
    if input('Gõ dong-y: ').strip() != 'dong-y':
        return 1
    g = a.thu_muc.resolve()
    if a.buoc == 'chuan-bi':
        chuan_bi(g, c, a.du_an, a.fixture)
        return 0
    info = json.loads((g / 'lan.json').read_bytes())
    ten, sha = info['du_an'], info['sha']
    if info['policy'] != c['policy'].get(ten):
        raise ValueError('policy-da-doi-do-lai-g4')
    policy = c['policy'][ten]
    da = DuAn(ten, g / 'kho', None, {}, moi_truong_kiem=MoiTruongKiem(g / 'env.testing', '.env.testing'),
              giao=CauHinhGiao(lenh_kiem_mac_dinh=tuple(policy['mac_dinh'])))
    from secrets import token_hex
    id_ = 'g4-' + token_hex(8)
    policy = c['policy'][ten]
    r = kiem_tu_xa(g / 'kho', da, giao_id=id_, luot=1, commit=sha, lenh_kiem=policy['mac_dinh'],
                   lenh_cho_phep=policy['cho_phep'], chay_lenh=True)
    print(json.dumps({'giao_id': id_, 'commit': sha, 'dat': r.dat, 'ket_qua': r.ket_qua}, ensure_ascii=False))
    return 0 if r.dat else 2


if __name__ == '__main__':
    raise SystemExit(main())
```

- [ ] **Step 4 — GREEN, rồi kiểm hồi quy cuối plan:**

```bash
tests/chan_host/chay.sh -q tests/test_quan_kiem_g4.py
```

## Task 7 — Cấp bộ phụ thuộc đã chốt cho lượt Ben Station, giữ nguyên hồ sơ v2

Đại ca cho làm thẳng plan ngắn + code ngày 19/10. Nguồn: thiết kế
`.handover/thao-luan-phu-thuoc/v1-codex.md` mục 1–3. Không commit, không sửa CURRENT_STATE/handovers.

1. **RED → GREEN đóng gói/cài:** thêm CLI `tram.chu.phu_thuoc_kiem soan|cai`, in kế hoạch/chờ
   `dong-y`. Chụp site-packages sạch (không bin/pyvenv.cfg/tram/editable/pyc) + node_modules,
   giữ link npm nội bộ. Manifest buộc bốn file nguồn, Python build/ABI, macOS/arch, uv/Node/npm,
   nhóm dev, flags npm, hash/size/byte/entry từng archive; tổng ≤1 GiB/100.000 entry.
   Cài R2 đúng hai archive + manifest dưới `/usr/local/tram/deps/ben-station/<hash>/`; bất biến,
   root:wheel 0644/0755, không ACL. Root chỉ chép bytes; lỗi giữ phần đã cài, không tự tải/cài gói.
2. **RED → GREEN policy/worker:** `lenh_quan_kiem cai --deps-manifest` đăng ký metadata root,
   gắn bundle vào digest client/server, replay và fingerprint G4. Không nhận đường/bundle từ client.
   Sau tree/env, helper tin cậy dưới `tram-kiem + boc_luot` kiểm bốn hash/runtime/đích trống;
   Uq kiểm bản root rồi cấp từng archive qua stdin; tạo `.venv` bằng Python pin
   `-I -m venv --without-pip`, giải site-packages và `frontend/node_modules` vào LUOT.
   Giữ trần source/env, hồ sơ v2, 900/3300 s, P1 và dọn toàn lượt.
3. **RED → GREEN runner/YAML:** nhánh `TRAM_KIEM_DA_CHUAN_BI=1` chọn Python LUOT, kiểm base
   prefix, giữ plugin/audithook/git giả/log/mã thoát/HOME/TMP; không uv/fallback. Tạo policy sáu
   lệnh đúng mục 2, `bat_ghi: false`. Env giả đặt `du-an/ben-station.env.testing` (không ở
   `.handover` bị Git bỏ qua), nguồn tuyệt đối trong YAML, mode 0600 khi vận hành.
4. **Ca đóng cổng:** thiếu/sai lock; đổi pyproject; sai ABI/hash/owner; link thoát; artifact quá lớn;
   `.venv`/node_modules có sẵn; env đè lock/đích chuẩn bị; preparation timeout. Hai lượt nhận bản
   riêng; ca hợp lệ import từ LUOT. Chỉ test liên quan + độ dài/vòng import, người điều phối chạy cả bộ.

Bản đồ tác động: `tram/chu/` lập/cài R2 → `tram/kiem/deps_*` dữ liệu/extractor stdlib →
`tram/quan_kiem/` policy + cấp bytes. Không sửa hồ sơ/nhận diện/thu hồi. Baseline **26 passed**,
0 dòng chặn/0 điểm mù. RED thật: `ModuleNotFoundError: No module named 'tram.kiem.deps_manifest'`.
Đợt đầu manifest/extractor: **22 passed**, 0 dòng chặn/0 điểm mù.

## G4 — năm bước trên bản thật, từng bước chờ Đại ca duyệt

Không chạy các lệnh này trong phiên review. G4 không tự bật S6. Lỗi quan sát/dọn giữ đóng.

1. **Chuẩn bị/cài.** D162 + siết đọc đã ghép và cài. Máy B còn tài khoản đo thì chạy bộ gỡ G3 đã sửa
   trong Task 4 một lần, rồi cài sản phẩm. Trình cài in toàn bộ policy từ `du-an/*.yaml` trước `dong-y`.
   Không có lệnh mặc định hợp lệ thì dừng; không tự tạo policy `sh *`. Đăng xuất/đăng nhập lại tài khoản
   trạm, khởi động lại dịch vụ trạm từ phiên mới để nhận nhóm socket; `id` trong Terminal cũ không đủ.
   Root bundle/plist/config/receipt phải đối soát được. `UserName=GroupName=tram-quan-kiem`,
   `SessionCreate=true`, miền system; UID đọc từ tài khoản, không hardcode 505.

```bash
export TRAM_PY="$PWD/.venv/bin/python"
"$TRAM_PY" -m tram.chu.lenh_quan_kiem cai --repo "$PWD" --deps-manifest "$DEP_MANIFEST"
export G4_QUAN_KIEM="$HOME/tram-g4-quan-kiem-run-20261019"
printf 'Tên dự án trong policy vừa duyệt: '; read -r G4_DU_AN
printf 'Đường tuyệt đối tới kho Git dữ liệu GIẢ đã duyệt: '; read -r G4_FIXTURE
"$TRAM_PY" -m tram.quan_kiem.g4 chuan-bi "$G4_QUAN_KIEM" --du-an "$G4_DU_AN" --fixture "$G4_FIXTURE"
```

Với Ben Station, chuẩn bị/cài bundle theo Task 7 trước; `DEP_MANIFEST` là đường CLI cài in ra.
Chọn `G4_DU_AN=ben-station`. Fixture giả mang cùng bốn file nguồn đã chốt trong manifest, đúng đường
bài kiểm và nguyên sáu lệnh policy; deps đi kênh artifact riêng, không nằm source/env upload.
Đo cold start/chuẩn bị, import native/build, canary nhà/mạng, từng lệnh + tổng và dọn sạch. Ngân sách
mục tiêu: chuẩn bị ≤300 s, Python từng nhóm ≤120 s, frontend từng lệnh ≤180 s, cả lượt ≤1500 s;
đây là mục tiêu cần đo, không thay trần cứng 900/3300 s. Sau đủ G4, thêm lượt bản sao SHA Ben Station
thật để chứng minh deps/test đủ; fixture nhỏ chưa chứng minh điều đó.

Kho fixture phải chứa bài kiểm nhỏ, dependency offline và file cấu hình để chạy **nguyên lệnh mặc định của
chính dự án**. Không dùng repo thật hoặc sửa policy để fixture xanh. Không có fixture phù hợp thì báo thiếu
điều kiện; không thay bằng lệnh khác. Dự án không có policy không được chạy. Mỗi dự án muốn mở phải có lượt
fixture với policy tương ứng; dấu vân tay gồm toàn bộ snapshot policy, đổi cấu hình phải cài/đo lại.

2. **Một lượt đúng + rào/canary.** Chạy CLI sau. Đối chiếu daemon PPID=1, Uq/nhóm riêng + nền OS
   `NHOM_NEN`, worker là con daemon, payload dưới 503. Ghi build 24G90, audit session + nguồn system,
   không chỉ so ASID. Sudo phải thành công từ daemon không TTY (`sudo -n`, rule NOPASSWD và
   `Defaults:tram-quan-kiem !requiretty`), không dựa timestamp Terminal. Kết quả phải đủ lệnh policy,
   tree đúng SHA, log probe canary/công cụ, receipt `xong/da_thu_hoi`, gốc lượt rỗng.

```bash
"$TRAM_PY" -m tram giao mo-cong-kiem
"$TRAM_PY" -m tram.quan_kiem.g4 sach "$G4_QUAN_KIEM"
sudo /bin/launchctl print system/vn.tram.quan-kiem
sudo -n -u tram-kiem -- /usr/bin/true
```

Lệnh cuối phải bị từ chối từ 501; nếu admin có quyền rộng/timestamp cho qua thì thu hồi timestamp và
kiểm effective sudoers, chưa được ký “không còn đường 501”. Không sửa sudoers toàn máy để che kết quả.
Probe cố định trong worker kiểm canary nhà, DAC-mở, symlink/firmlink, read/stat/list; mẫu trong LUOT phải đọc
được. Ngoài hồ sơ đọc đúng canary DAC nhưng không đọc canary nhà. Giữ ma trận launchctl gốc/copy,
submit/bootstrap trong/ngoài hồ sơ và đa miền: thiếu driver/không quan sát được là chưa đạt, không coi OS
reject là bằng chứng Seatbelt. Peer giả phải bị từ chối; 503/khe không qua DAC socket. Test offline bao phủ
UID sai; phép đo máy xác nhận peer hai đầu trả đúng UID. Không mở rộng quyền socket để thử.

3. **Một ca mất kênh.** Mở lượt fixture có bài kiểm chờ hữu hạn, xác nhận receipt `dang-chay`, Ctrl-C
   đúng client đó. Server thấy EOF → huỷ worker/thu hồi 503 trong 240 s + grace P1, receipt không pass,
   cổng đóng. Retry không spawn lượt thứ hai. Ca crash/replay/fencing khác giữ ở offline; không lặp cả
   ma trận OS. Nếu không kịp ngắt thì ca chưa đo, dùng fixture chờ dài hơn trong cùng lệnh policy.
4. **Reboot.** Sau Đại ca duyệt, reboot bằng giao diện macOS; daemon trở lại system, socket đúng quyền,
   cổng đóng. Mở lại qua CLI sau quan sát sạch, chạy một lượt fixture nữa: không tàn dư từ lượt trước.
   Worker Uq cũ hoặc đọc miền lỗi vẫn chặn mở; không nới D162 và không kill Uq toàn cục.
5. **Dọn/ký.** Lưu receipt/context/canary/driver/config/plist + fingerprint. In argv dọn từ
   `tram.giao_viec.mau_g4.lenh_don` với từng receipt `launchd-<id>.json`; người vận hành duyệt đúng label,
   đúng chủ miền, xác nhận service vắng và PID/birth identity hết. Không wildcard/pkill. Dọn đúng các cây
   trong `fixture.json` và `$G4_QUAN_KIEM`; giữ bản bằng chứng ở ngoài. Sau đó tạo mẫu bằng chứng:

```bash
"$TRAM_PY" -m tram.quan_kiem.bang_chung > "$HOME/tram-quan-kiem-bang-chung-g4.json"
```

Chỉ ký từng mục đạt bằng chứng: `nguon-system`, `rao-ho-so`, `doc-canary`, `cong-cu`, `nhieu-luot`
(lượt trước/sau reboot), `crash` (ca mất kênh), `reboot`, `don`. Chạy lại trình cài với snapshot policy
không đổi; fingerprint phải khớp, không sửa hash tay:

```bash
"$TRAM_PY" -m tram.chu.lenh_quan_kiem cai --repo "$PWD" \
  --deps-manifest "$DEP_MANIFEST" \
  --bang-chung-g4 "$HOME/tram-quan-kiem-bang-chung-g4.json"
```

Đường lui: `"$TRAM_PY" -m tram.chu.lenh_quan_kiem go`, in kế hoạch/chờ `dong-y`, gỡ đúng biên nhận.
Dừng daemon trước, xác nhận không còn worker Uq (Apple đúng D162 được qua), không khôi phục 501→503.
Không gỡ toolchain/hồ sơ/tài khoản 503 do lát siết đọc sở hữu.

## Kiểm chứng review vòng 1 — 19/10/2026

Mã chỉ áp tạm rồi hoàn nguyên. Python import từ worktree, venv dùng chung chỉ đọc:

```bash
export PYTHONPATH="$PWD"
export UV_CACHE_DIR=/tmp/quan-kiem-uv
export UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv'
export UV_NO_SYNC=1
tests/chan_host/chay.sh -q tests/test_quan_kiem*.py tests/test_noi_giao_viec.py \
  tests/test_giao_kiem.py tests/test_cai_dat_tho_kiem.py tests/test_nghiem_thu_doc_g4.py \
  tests/test_pipeline.py tests/test_cong_luot.py tests/test_do_dai_ma.py
```

**GREEN vòng 1: 124 passed in 2.85s**, nhật ký chặn 0 dòng mới, 0 điểm mù, 4 push giả lập
(không push thật). Có test socketpair gọi `getpeereid` thật; `test_do_dai_ma` đạt. Không đo daemon/Seatbelt thật.
RED collection thật: `ModuleNotFoundError: No module named 'tram.quan_kiem.policy'`.
RED hành vi thật khi bỏ kiểm lệnh mặc định phía daemon:
`test_server_bat_buoc_lenh_mac_dinh[lenh1-False]`, `AssertionError: assert True is False`, **1 failed, 6 passed**.
Không chỉ kiểm client: lệnh được allowlist nhưng thiếu lệnh mặc định vẫn phải từ chối.

Baseline đầy đủ đã khởi chạy nhưng bị ngắt sau **703 passed, 60 failed**, không phải full-suite result.
Ngoài `/bin/ps` bị sandbox chặn, `sysctl` đọc bảng tiến trình và phiên khởi động cũng trả PermissionError;
không được quy mọi lỗi chưa phân loại là do ps. Nhật ký 0 dòng mới, 4 điểm mù Python con, 122 push giả lập.
Lần đầu dùng cache mặc định lỗi quyền; lần kế thiếu PYTHONPATH import nhầm bản checkout trong venv;
đã sửa môi trường theo khối trên, không đổi bộ chặn/thu hồi. Sau hoàn nguyên, chạy
`tests/chan_host/chay.sh -q --maxfail=1`: **1 failed, 172 passed in 20.17s**; lỗi
`test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau` vì không xác nhận thu hồi cây.
Nhật ký 0 dòng mới, 0 điểm mù, 14 push giả lập. Không có bằng chứng full suite GREEN.

## Giới hạn và câu hỏi còn cần Đại ca chốt

- Nguồn policy là loader đang dùng bởi trạm (`liet_ke_du_an`/`nap_du_an`, theo `TRAM_REPO` hoặc `goc_repo()`),
  cùng các trường `de_xuat.py` → `tieu_chi.lenh_bat_buoc` dùng. `--repo` chỉ chọn mã bundle, không thay nguồn
  cấu hình. Kế hoạch in nguồn và snapshot để Đại ca đối chiếu trước `dong-y`; root sở hữu bản đã chấp thuận.
- Cần tên dự án ưu tiên và kho fixture giả chạy được đúng lệnh của nó. Không có dữ liệu đó trong checkout này;
  CLI đã nhận `--du-an`/`--fixture`, không có policy rộng dự phòng. Đề xuất chạy một dự án trước trong hôm nay.
- G4 mới chốt được hiệu lực nhóm, sudo không TTY, nguồn system, Seatbelt và phục hồi qua reboot. Test xanh
  không thay các bằng chứng đó. Nếu một miền không quan sát được thì giữ đóng, không thêm helper root.
- Trình gỡ G3 dùng Python 3.12 root đã cài ở lát siết đọc; `/usr/bin/python3` máy này là 3.9, không import được
  annotation của API D162. Cấm chạy lệnh gỡ bằng Python hệ thống cũ hoặc tự chép lại bộ lọc Apple.

## Ghi chú triển khai

- Task 7 (19/10, Đại ca yêu cầu plan ngắn + code): giữ code/test/YAML và `KET-QUA-CODEX.md` trong cây,
  không hoàn nguyên như phiên chỉ viết plan. Kiểm cuối: **180 passed**, 0 failed, 0 dòng chặn/0 điểm mù;
  chỉ nhóm phụ thuộc, quản lý kiểm, bộ chặn host, độ dài và vòng import; chưa chạy cả bộ/G4 máy thật.
- Chỉ giữ plan này và `REVIEW-CODEX.md`. Không commit, không CURRENT_STATE/handovers, không Beads ghi.
- D162 không còn là task; các task đánh số 1–6. `cong.py` chứa cả phục hồi, không module phục hồi riêng.
- Patch Modify có context nguyên văn; kiểm `git apply --check` trên đúng mốc trước áp. Những hunk đã có sau
  ghép D162 thì đối chiếu và bỏ riêng hunk đã áp, không chép đè toàn file lên code mới.
- Cài/gỡ tài khoản G3 và sản phẩm đều chờ `dong-y`; D162 chỉ miễn khi xác nhận, không thay lệnh thu hồi UID.

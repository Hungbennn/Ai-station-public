"""Hệ thống macOS GIẢ cho test cài/gỡ máy thợ (lát 3c R2, CHỈ DÙNG TRONG TEST): user, nhà, file root, thư mục — KHÔNG
sudo, không dscl/sysadminctl thật. `sysadminctl -addUser` trên user có sẵn KHÔNG báo lỗi (như máy thật: mã thoát
không đáng tin) — chỉ quan sát định danh mới biết user là của ai. `add_tao_nha`: giả lập `addUser` tự tạo nhà (S6 đo
hành vi thật); `dung_lai_uid`: UID mới = UID trống nhỏ nhất ≥ 501 (như macOS); `-deleteUser` không `-keepHome` xoá nhà;
`createhomedir` và `sudo -u <u> mkdir` tạo thư mục thuộc UID của user đó."""
import hashlib
import itertools
import subprocess
from pathlib import Path


class HeGia:
    def __init__(self, add_tao_nha: bool = False, dung_lai_uid: bool = False):
        self.nhom, self.gid, self.phu = {}, {}, {}
        self.user: dict[str, dict] = {}
        self.tep: dict[str, str] = {}
        self.thu_muc: dict[str, int] = {}
        self.chu: dict[str, int] = {}             # chủ của thư mục (mặc định root = 0)
        self.lenh: list[str] = []
        self.hong: set[str] = set()               # tiền tố lệnh (không kể sudo) trả lỗi
        self.truoc: dict[str, callable] = {}      # tiền tố lệnh → việc xảy ra ngay trước lệnh (đua)
        self.add_tao_nha, self.dung_lai_uid = add_tao_nha, dung_lai_uid
        self._so = itertools.count(501)

    def them_user(self, ten: str, ten_day_du: str = "người khác") -> None:
        dung = {u["uid"] for u in self.user.values()}
        uid = min(set(range(501, 600)) - dung) if self.dung_lai_uid else next(self._so)
        self.user[ten] = {"uid": uid, "guid": f"GUID-{ten}-{uid}", "ten_day_du": ten_day_du}

    def them_nha(self, ten: str, uid: int) -> None:
        self.thu_muc[f"/Users/{ten}"], self.chu[f"/Users/{ten}"] = next(self._so), uid

    def quan_sat(self, kieu: str, ten: str, *, nhe: bool = False) -> dict | None:
        if kieu == "nhom":
            return self.nhom.get(ten)
        if kieu == "user":
            return dict(self.user[ten]) if ten in self.user else None
        if kieu == "tep":
            return None if ten not in self.tep else {"uid": 0, **({} if nhe else {"sha256": self.tep[ten]})}
        return {"ino": self.thu_muc[ten], "uid": self.chu.get(ten, 0)} if ten in self.thu_muc else None

    def chay(self, c: list[str], check: bool = False, **kw) -> subprocess.CompletedProcess:
        self.lenh.append(" ".join(c))
        if c[:2] == ["/usr/bin/id", "-g"]:
            return subprocess.CompletedProcess(c, 0, str(self.gid[c[-1]]), "")
        if c[:2] == ["/usr/bin/id", "-Gn"]:
            return subprocess.CompletedProcess(c, 0, " ".join(self.phu.get(c[-1], set())), "")
        x = c[1:] if c[0] == "sudo" else c
        ai, x = (x[1], x[2:]) if x[0] == "-u" else (None, x)
        for tien_to, viec in self.truoc.items():
            if " ".join(x).startswith(tien_to):
                viec()
        ok = not any(" ".join(x).startswith(h) for h in self.hong) and self._lam(x, ai)
        if not ok and check:
            raise subprocess.CalledProcessError(1, c)
        return subprocess.CompletedProcess(c, 0 if ok else 1, "", "")

    def _lam(self, x: list[str], ai: str | None = None) -> bool:
        if x[:3] == ["/usr/sbin/dseditgroup", "-o", "create"]:
            self.nhom.setdefault(x[-1], {"gid": 700 + len(self.nhom), "guid": f"G-{x[-1]}",
                                        "ten_day_du": x[x.index("-r") + 1]})
        elif x[:3] == ["/usr/sbin/dseditgroup", "-o", "delete"]:
            self.nhom.pop(x[-1], None)
        elif x[:3] == ["/usr/sbin/dseditgroup", "-o", "edit"]:
            self.phu.get(x[x.index("-d") + 1], set()).discard(x[-1])
        elif x[:3] == ["/usr/bin/dscl", ".", "-create"]:
            self.gid[x[3].split("/")[-1]] = int(x[-1])
        elif x[:2] == ["sysadminctl", "-addUser"] and x[2] not in self.user:
            self.them_user(x[2], x[x.index("-fullName") + 1])
            nha = x[x.index("-home") + 1]
            if self.add_tao_nha and nha.startswith("/Users/") and nha not in self.thu_muc:
                self.them_nha(x[2], self.user[x[2]]["uid"])
        elif x[:2] == ["sysadminctl", "-deleteUser"]:
            self.user.pop(x[2], None)
            if "-keepHome" not in x:
                self.thu_muc.pop(f"/Users/{x[2]}", None)
        elif x[0] == "createhomedir" and x[-1] in self.user:
            if f"/Users/{x[-1]}" not in self.thu_muc:
                self.them_nha(x[-1], self.user[x[-1]]["uid"])
        elif x[:2] in (["install", "-d"], ["/bin/mkdir", "-m"]):
            self.thu_muc[x[-1]], self.chu[x[-1]] = next(self._so), self.user[ai]["uid"] if ai in self.user else 0
        elif x[0] == "install":
            self.tep[x[-1]] = hashlib.sha256(Path(x[-2]).read_bytes()).hexdigest()
        elif x[:2] == ["rm", "-f"]:
            self.tep.pop(x[2], None)
        elif x[:2] in (["/bin/rm", "-rf"], ["rm", "-rf"]):
            self.thu_muc.pop(x[2], None)
        elif x[0] == "rmdir":
            if any(p.startswith(x[1] + "/") for p in [*self.tep, *self.thu_muc]):
                return False
            self.thu_muc.pop(x[1], None)
        return True

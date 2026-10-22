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

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


from doi_ngu_token import dang_nhap


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
        b = subprocess.Popen(lenh_tho("nhan-token", "--may-b"), stdin=a.stdout,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        a.stdout.close()
        mb, ma = b.wait(timeout=30), a.wait(timeout=30)
        c.ghi("token-file", f"nguon={ma},dich={mb}")
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
    if len(sys.argv) != 2 or sys.argv[1] not in ("chuan-bi", "login-1", "login-2", "token",
            "dang-ky", "kho", "do-nen", "kiem", "s6", "bat-khe", "bat-tho", "bat-giao", "tat-giao", "dung"):
        print("Chọn đúng bước của sổ tay; không có bước chạy tất cả.")
        return 2
    if os.getuid() == 0 or Path.home() != Path("/Users/dai-ca"):
        print("Mở Terminal.app dưới hungle; không sudo toàn bộ script.")
        return 2
    os.chdir("/")  # Lệnh dưới user khe kế thừa cwd; nhà hungle đã chặn khe (EACCES nếu chạy từ ~).
    c, buoc = Chay(), sys.argv[1]
    try:
        c.tuong_tac("xac-thuc-sudo", ["sudo", "-v"])
        if buoc == "chuan-bi":
            chuan_bi(c)
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

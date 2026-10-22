"""Định danh tài nguyên hệ thống cho sổ cài đặt (lát 3c R2): user — UniqueID, GeneratedUID, RealName qua `dscl` (không
sudo); file — sha256 nội dung (file root không đọc được như sudoers 0440 thì `sudo shasum`); thư mục, nhà — inode + chủ.
`khop`: thứ vừa thấy có đúng thứ LẦN CÀI NÀY định tạo (user mang mã id trong RealName, file đúng nội dung, thư mục
và nhà là thư mục thật thuộc đúng UID mong đợi — R5: biên nhận user KHÔNG chứng minh nhà đã tạo xong). `dscl` lỗi
khác "không có bản ghi" → OSError: không suy "không còn" từ một lần đọc hỏng.
`cung`: thứ đang có có đúng thứ sổ đã ghi `da_tao` (user cùng UID + GeneratedUID — tên tái sử dụng thì khác)."""
import hashlib
import os
import stat
import subprocess
from pathlib import Path


def _doc_dscl(s: str) -> dict:
    gia, khoa = {}, None
    for d in s.splitlines():
        if d.startswith(" ") and khoa:
            gia[khoa] = (gia[khoa] + " " + d.strip()).strip()
            continue
        khoa, _, v = d.partition(":")
        gia[khoa] = v.strip()
    if not gia.get("UniqueID", "").isdigit() or not gia.get("GeneratedUID"):
        raise ValueError("dscl không trả UniqueID/GeneratedUID")
    return {"uid": int(gia["UniqueID"]), "guid": gia["GeneratedUID"], "ten_day_du": gia.get("RealName", "")}


def nhom(ten: str, *, chay=subprocess.run) -> dict | None:
    r = chay(["/usr/bin/dscl", ".", "-read", f"/Groups/{ten}", "PrimaryGroupID", "GeneratedUID", "RealName"],
             capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        gia = _doc_dscl(r.stdout.replace("PrimaryGroupID:", "UniqueID:"))
        gia["gid"] = gia.pop("uid")
        return gia
    if "eDSRecordNotFound" in (r.stdout or "") + (r.stderr or ""):
        return None
    raise OSError(f"Không đọc được nhóm {ten}; dừng")


def user(ten: str, *, chay=subprocess.run) -> dict | None:
    r = chay(["/usr/bin/dscl", ".", "-read", f"/Users/{ten}", "UniqueID", "GeneratedUID", "RealName"],
             capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        return _doc_dscl(r.stdout)
    if "eDSRecordNotFound" in (r.stdout or "") + (r.stderr or ""):
        return None
    raise OSError(f"dscl đọc /Users/{ten} lỗi (mã {r.returncode}) — không kết luận user không có")


def tep(p: Path, *, chay=subprocess.run, nhe: bool = False) -> dict | None:
    if not os.path.lexists(p):
        return None
    st = os.lstat(p)
    if not stat.S_ISREG(st.st_mode):
        return {"loai": "khac", "uid": st.st_uid}
    if nhe:
        return {"uid": st.st_uid}
    try:
        h = hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except PermissionError:
        h = chay(["sudo", "/usr/bin/shasum", "-a", "256", str(p)], capture_output=True, text=True, timeout=60,
                 check=True).stdout.split()[0]
    return {"sha256": h, "uid": st.st_uid}


def thu_muc(p: Path) -> dict | None:
    if not os.path.lexists(p):
        return None
    st = os.lstat(p)
    return {"ino": st.st_ino, "uid": st.st_uid} if stat.S_ISDIR(st.st_mode) else {"loai": "khac", "uid": st.st_uid}


def quan_sat_that(kieu: str, ten: str, *, nhe: bool = False) -> dict | None:
    """`nhe`: lúc lập kế hoạch — không gọi `sudo` (chỉ biết file có hay không)."""
    if kieu == "acl_search":
        from tram.chu.acl_tho import quan_sat
        return quan_sat(Path(ten))
    if kieu == "nhom":
        return nhom(ten)
    if kieu == "user":
        return user(ten)
    return tep(Path(ten), nhe=nhe) if kieu == "tep" else thu_muc(Path(ten))


def khop(kieu: str, mong: dict, hien: dict) -> bool:
    if hien.get("loai") == "khac":
        return False
    if kieu in ("acl_search", "thanh_vien"):
        return hien == mong
    if kieu in ("user", "nhom"):
        return hien.get("ten_day_du") == mong.get("ten_day_du")
    if kieu == "tep":
        return hien.get("sha256") == mong.get("sha256")
    return "ino" in hien and mong.get("uid") is not None and hien.get("uid") == mong.get("uid")


def cung(kieu: str, da: dict | None, hien: dict) -> bool:
    if not da or hien.get("loai") == "khac":
        return False
    if kieu in ("acl_search", "thanh_vien"):
        return hien == da
    if kieu in ("user", "nhom"):
        key = "gid" if kieu == "nhom" else "uid"
        return (hien.get(key), hien.get("guid")) == (da.get(key), da.get("guid"))
    return hien.get("sha256") == da.get("sha256") if kieu == "tep" else hien.get("ino") == da.get("ino")

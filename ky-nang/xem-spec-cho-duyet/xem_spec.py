#!/usr/bin/env python3
"""Đọc "Spec chờ duyệt" tại ĐÚNG commit trạm đã kiểm — skill `xem-spec-cho-duyet` trên máy A (spec 4 §7.3). CHỈ ĐỌC.

Không gọi API của trạm, không chạy `bd`, không commit/push/checkout, không sửa cây làm việc. Việc duy nhất có
ghi là `git fetch` nhánh `tram/spec-<feature>` (chỉ cập nhật FETCH_HEAD). Digest tính y hệt trạm
(`tram/giao_viec/ke_hoach.py::digest_ke_hoach`) để Đại ca biết bản đang đọc đúng là bản trên dashboard.
Chạy được với python3 ≥ 3.9 của macOS, chỉ dùng thư viện chuẩn. Mã thoát: 0 khớp, 2 không khớp/lỗi."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

MA = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
SHA = re.compile(r"^[0-9a-f]{7,40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
DUONG = re.compile(r"^docs/[A-Za-z0-9._/-]+\.md$")
GIT = ["git", "-c", "core.hooksPath=/dev/null"]


def git(repo, *args):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    return subprocess.run(GIT + ["-C", repo] + list(args), capture_output=True, env=env)


def doc_blob(repo, commit, duong):
    """Nội dung file THƯỜNG tại commit (không symlink/submodule); không có → None."""
    kq = git(repo, "ls-tree", "-z", commit, "--", duong)
    dong = [x for x in kq.stdout.split(b"\0") if x] if kq.returncode == 0 else []
    if len(dong) != 1:
        return None
    mode, loai, sha = dong[0].split(b"\t", 1)[0].split(b" ")
    if loai != b"blob" or mode not in (b"100644", b"100755"):
        return None
    return git(repo, "cat-file", "blob", sha.decode()).stdout.decode("utf-8", "replace")


def sach(x):
    """Dữ liệu không tin cậy: bỏ ký tự điều khiển/định dạng trước khi in ra phiên Claude."""
    return "".join(c for c in str(x) if c.isprintable())[:200]


def digest(van_ban):
    tho = json.dumps(json.loads(van_ban), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(tho.encode()).hexdigest()


def _dau_vao(a):
    if not (MA.match(a.du_an) and MA.match(a.feature) and SHA.match(a.commit) and DIGEST.match(a.digest)):
        return "Tham số không hợp lệ (du_an, feature, commit 7–40 hex, digest sha256:<64 hex>)"
    return None


def _kiem_commit(a, nhanh):
    if not a.khong_fetch:
        if git(a.repo, "fetch", "--quiet", "origin", "refs/heads/" + nhanh).returncode != 0:
            return "Không fetch được nhánh " + nhanh + " từ origin"
        if git(a.repo, "merge-base", "--is-ancestor", a.commit, "FETCH_HEAD").returncode != 0:
            return "Commit " + a.commit + " không nằm trên nhánh " + nhanh
    if git(a.repo, "cat-file", "-e", a.commit + "^{commit}").returncode != 0:
        return "Không có commit " + a.commit + " trong repo"
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Xem spec chờ duyệt (chỉ đọc)")
    for ten in ("du_an", "feature", "commit", "digest"):
        ap.add_argument(ten)
    ap.add_argument("dashboard", nargs="?", default="")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--khong-fetch", action="store_true")
    a = ap.parse_args(argv)
    nhanh = "tram/spec-" + a.feature
    loi = _dau_vao(a) or _kiem_commit(a, nhanh)
    van_ban = None if loi else doc_blob(a.repo, a.commit, "docs/plans/" + a.feature + ".beads.json")
    if loi or van_ban is None:
        print("LỖI: " + (loi or "Không thấy docs/plans/" + a.feature + ".beads.json tại commit"))
        return 2
    try:
        dg, kh = digest(van_ban), json.loads(van_ban)
    except ValueError:
        print("LỖI: *.beads.json không phải JSON")
        return 2
    khop = dg == a.digest
    print("Dự án " + a.du_an + " · feature " + a.feature + " · nhánh " + nhanh + " · commit " + a.commit)
    print("Digest bead đề xuất: " + dg + (" — KHỚP dashboard" if khop else " — KHÔNG KHỚP " + a.digest))
    du_file = True
    for ten in ("spec_file", "plan_file"):
        p = kh.get(ten) if isinstance(kh, dict) else None
        co = (isinstance(p, str) and bool(DUONG.match(p)) and ".." not in p.split("/")
              and doc_blob(a.repo, a.commit, p) is not None)
        du_file = du_file and co
        print(f"{ten}: {sach(p)}" + ("" if co else "  (THIẾU hoặc không hợp lệ)"))
        if co:
            print(f"  đọc toàn văn: git -C {a.repo} show {a.commit}:{p}")
    for b in (kh.get("bead") if isinstance(kh, dict) else None) or []:
        if not isinstance(b, dict):
            continue
        sau, nhan = ", ".join(map(sach, b.get("phu_thuoc") or [])), ", ".join(map(sach, b.get("nhan") or []))
        print(f"- [{sach(b.get('khoa'))}] {sach(b.get('loai'))} P{sach(b.get('uu_tien'))} · {sach(b.get('tieu_de'))}"
              f" · sau: {sau} · nhãn: {nhan}")
    if a.dashboard:
        print("Duyệt / Trả về: Đại ca tự bấm trên dashboard → " + sach(a.dashboard))
    return 0 if khop and du_file else 2


if __name__ == "__main__":
    sys.exit(main())

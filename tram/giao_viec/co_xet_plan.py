"""Chỉ ghi bằng chứng sau SHA trạm, bàn giao hợp lệ và stream model của quản lý thợ."""
import hashlib
import json
from types import SimpleNamespace

from tram.ban_giao.schema import kiem_ban_giao
from tram.giao_viec.co_plan import ghi_plan, review
from tram.giao_viec.co_phieu_plan import MUC
from tram.giao_viec.git_kiem import _git
from tram.giao_viec.su_kien import su_kien_bead, moi_nhat
from tram.giao_viec.xet_xong import _ban_giao
from tram.kiem.diff import tep_doi
from tram.tho.co_model import dung_model


def blob(kg, sha, file):
    dong = _git(kg, "ls-tree", "-z", sha, "--", file, timeout=60).stdout
    if not dong.startswith((b"100644 blob ", b"100755 blob ")) or dong.count(b"\0") != 1:
        raise ValueError("Plan phải là file thường")
    raw = _git(kg, "show", f"{sha}:{file}", timeout=60).stdout
    if not raw or len(raw) > 400_000:
        raise ValueError("Plan rỗng hoặc quá lớn")
    return raw


def xet_plan(kho, kg, p, bao, sha, luc):
    ds = su_kien_bead(kho, p.du_an, p.bead_id)
    chay = moi_nhat(ds, "chay.xong", lambda s: s.du_lieu.get("giao_id") == p.giao_id)
    if not chay or chay.du_lieu.get("ket_thuc") != "xong" or not dung_model(
            {"model": "opus"}, SimpleNamespace(co_assistant=True, model_lech=False,
                                               mo_hinh=chay.du_lieu.get("mo_hinh"))):
        return "plan-thieu-model", (), sha, None
    if not sha or bao.get("commit") != sha:
        return "plan-chua-cong-bo", (), sha, None
    file = f"docs/plans/{p.bead_id}." + ("md" if p.co["pha"] == "plan" else "review.json")
    if any(f != file and not f.startswith("docs/handovers/") for f in tep_doi(kg, p.repo.cha, sha)):
        return "plan-ngoai-pham-vi", (), sha, None
    bg = _ban_giao(bao)
    if bg is None or bg.commit != sha or bao.get("loi_ban_giao") or kiem_ban_giao(
            bg, p.tieu_chi, kg, lenh_bat_buoc=[], can_lenh_kiem=False, commit=sha):
        return "ban-giao-loi", (), sha, None
    try:
        raw = blob(kg, sha, file)
        if p.co["pha"] == "plan":
            text = raw.decode("utf-8")
            if any("## " + m not in text for m in MUC):
                raise ValueError("Thiếu mục plan")
            if p.co["co"] == "lon" and any(m not in text for m in ("Global Constraints", "Files", "Task", "```")):
                raise ValueError("Thiếu cấu trúc plan đầy đủ")
            ghi_plan(kho, p.du_an, p.bead_id, sha, file, hashlib.sha256(raw).hexdigest(), p.khe_id, p.co, luc)
        else:
            d = json.loads(raw)
            if not isinstance(d, dict) or set(d) != {"plan", "ket_luan", "phat_hien"} or d["plan"] != p.co["plan"]:
                raise ValueError("Review sai bản plan")
            ph = d["phat_hien"]
            if not isinstance(ph, list) or len(ph) > 30 or any(not isinstance(x, str) or len(x) > 2000 for x in ph):
                raise ValueError("Nhận xét review không hợp lệ")
            if d["ket_luan"] == "tra-ve" and not ph:
                raise ValueError("Trả về phải có nhận xét")
            review(kho, p.du_an, p.bead_id, d["plan"], p.khe_id, d["ket_luan"], p.giao_id, luc, commit=sha)
    except (ValueError, UnicodeError):
        return "plan-khong-hop-le", (), sha, None
    return None, (), sha, None

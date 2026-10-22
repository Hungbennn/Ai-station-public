import hashlib
import json
from bead_gia import KHOI_BAN_GIAO
from kho_phieu_gia import kho_tam, dat_phieu, LUC
from kho_kiem_gia import dung_kho
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.co_plan import ghi_plan, duyet
from tram.giao_viec.co_xet_plan import xet_plan
from tram.giao_viec.su_kien import su_kien_bead


def test_review_tu_sha_luu_nguon_nhan_xet_va_retry_khong_them_vong(tmp_path):
    k, kg = kho_tam(tmp_path), dung_kho(tmp_path)
    raw = "# Plan"
    sha_plan = kg.day("tram/spec-hr-r",{"docs/plans/hr-r.md":raw},tu=kg.main)
    q = {"co":"lon","pham_vi":["src/a.py"],"ban_luat":"v1", "model":"opus", "thieu":[]}
    ma = ghi_plan(k,"hr-codex","hr-r",sha_plan,"docs/plans/hr-r.md",
                  hashlib.sha256(raw.encode()).hexdigest(),"B/claude-2",q,LUC)
    duyet(k,"hr-codex","hr-r",ma,LUC)
    p = dat_phieu(k,bead_id="hr-r",buoc="spec",cha=sha_plan,co={**q,"pha":"review","plan":ma})
    bg_file = "docs/handovers/r.md"
    d = {"plan":ma,"ket_luan":"tra-ve","phat_hien":["Thiếu test lỗi đọc cấu hình."]}
    sha = kg.day(p.repo.nhanh,{"docs/plans/hr-r.review.json":json.dumps(d), bg_file:"Bàn giao"},tu=sha_plan)
    fetch(kg.kho)
    bg = {**KHOI_BAN_GIAO,"loai":"chinh-thuc","nhanh":p.repo.nhanh,"luot":p.luot,
          "commit":sha,"pr":None,"file_ban_giao":bg_file,"lenh_kiem":[],
          "doi_chieu_nghiem_thu":[{"tieu_chi":p.tieu_chi[0],"dat":True,"bang_chung":bg_file}]}
    with k.giao_dich():
        k.ghi_su_kien(p.du_an,"chay.xong",{"giao_id":p.giao_id,"ket_thuc":"xong", "mo_hinh":"claude-opus-4-6"},
                     luc=LUC,bead_id=p.bead_id)
    for _ in range(2):
        assert xet_plan(k,kg.kho,p,{"commit":sha,"ban_giao":bg},sha,LUC)[0] is None
    ds = [s for s in su_kien_bead(k,p.du_an,p.bead_id) if s.loai == "co.review"]
    assert len(ds) == 1 and ds[0].du_lieu["commit"] == sha
    assert "Thiếu test" not in json.dumps(ds[0].du_lieu,ensure_ascii=False)
    k.close()


def test_plan_khong_co_stream_opus_khong_ghi_bang_chung(tmp_path):
    from tram.giao_viec.co_xet_plan import xet_plan
    from kho_phieu_gia import kho_tam, dat_phieu
    from kho_kiem_gia import dung_kho
    k = kho_tam(tmp_path)
    kg = dung_kho(tmp_path)
    p = dat_phieu(k,buoc="spec",co={"pha":"plan", "model":"opus"})
    assert xet_plan(k,kg.kho,p,{"commit":kg.main},kg.main,LUC)[0] == "plan-thieu-model"
    assert not any(s.loai == "co.plan" for s in su_kien_bead(k,p.du_an,p.bead_id))
    k.close()

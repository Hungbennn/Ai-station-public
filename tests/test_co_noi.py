from dataclasses import replace
import pytest
from giao_viec_gia import dung, bug
from kho_phieu_gia import LUC
from tram.cau_hinh.theo_co import doc_theo_co
from tram.phieu.khe import dang_ky_khe
from tram.giao_viec.co_nguon import quyet_dinh, chan_buoc
from tram.giao_viec.su_kien import su_kien_bead


def thiet_lap(t):
    ch = doc_theo_co({"nhom": {"src/": "src"}, "nguy_hiem": ["secret/**"], "lenh_ca_bo": ["sh kiem.sh"]})
    t.da = replace(t.da, theo_co=ch)
    t.bo.cac_du_an = lambda: [t.da]
    with t.kho.giao_dich():
        dang_ky_khe(t.kho, "B", [dict(ten="claude-1", cli="claude", ten_goi_nho="c1",
                                    vai_uu_tien=["coder"], models=["opus"]),
                                dict(ten="claude-2", cli="claude", ten_goi_nho="c2",
                                     vai_uu_tien=["qc"], models=["sonnet"])], luc=LUC)


def viec(**kw):
    return bug(design="<!-- pham-vi-co:v1 -->\n- src/a.py\n<!-- /pham-vi-co -->", **kw)


def test_s7_loc_model_truoc_uu_tien_va_claim(tmp_path):
    t = dung(tmp_path, viec())
    try:
        thiet_lap(t)
        assert t.bo.chon("B/claude-1", None) is None
        assert t.g.beads["hr-1"].status == "open"
        assert t.kho.db.execute("SELECT count(*) FROM giu_ngan_sach").fetchone()[0] == 0
        dx = t.bo.chon("B/claude-2", None)
        assert dx.co["co"] == "nho" and dx.co["model"] == "sonnet"
        assert dx.co["effort"] == "medium"
        assert "QC" in dx.goi_ngu_canh
        assert t.bo.con_hop_le(dx)
        t.da = replace(t.da, theo_co=doc_theo_co({"nhom": {"src/": "src"}, "nho_file": 3}))
        assert not t.bo.con_hop_le(dx)
    finally:
        t.kho.close()


def test_vua_cho_plan_khong_claim(tmp_path):
    t = dung(tmp_path, viec(labels=["cot:ai-lam", "co:vua"]))
    try:
        thiet_lap(t)
        dx = t.bo.chon("B/claude-1", None)
        assert dx.buoc == "spec" and dx.co["pha"] == "plan"
        assert t.g.beads["hr-1"].status == "open"
    finally:
        t.kho.close()


def test_s8_khe_qc_khong_doi_danh_tinh(tmp_path):
    from tram.giao_viec.chon import UngVien, khe_nhan
    from tram.phieu.trang_thai import trang_thai_khe
    t = dung(tmp_path, viec())
    try:
        thiet_lap(t)
        uv = UngVien(t.da, viec(), "qc", False, frozenset({"B/claude-2"}))
        ds = trang_thai_khe(t.kho, bay_gio=LUC, ch=t.bo.ch)
        assert not khe_nhan("B/claude-2", None, uv, ds, t.bo.ch, model="sonnet")
        assert not khe_nhan("B/claude-1", None, uv, ds, t.bo.ch, model="sonnet")
    finally:
        t.kho.close()


def test_s9_diff_khong_mat_khi_sua_khai_bao(tmp_path, monkeypatch):
    from tram.giao_viec import co_nguon
    t = dung(tmp_path, viec())
    try:
        thiet_lap(t)
        with t.kho.giao_dich():
            t.kho.ghi_su_kien(t.da.ten, "giao.nhan", {"buoc": "code", "luot": 1,
                "giao_id": "g1", "cha": "a" * 40, "co": {"co": "nho"}}, luc=LUC, bead_id="hr-1")
            t.kho.ghi_su_kien(t.da.ten, "giao.cong_bo", {"luot": 1, "commit": "b" * 40}, luc=LUC, bead_id="hr-1")
        monkeypatch.setattr(co_nguon, "tep_doi", lambda *a: ["src/a.py", "secret/token"])
        b = viec()
        q = quyet_dinh(t.kho, t.da, b, {b.id:b}, t.k.kho)
        assert q["co"] == "lon"
        assert chan_buoc(t.kho, t.da, b, {b.id:b}, t.k.kho, LUC) == "xac-nhan-pham-vi"
        b = replace(b, design=b.design.replace("- src/a.py", "- src/a.py\n- secret/token"))
        q2 = quyet_dinh(t.kho, t.da, b, {b.id:b}, t.k.kho)
        assert q2["co"] == "lon" and q2["pham_vi"] == q["pham_vi"]
        assert chan_buoc(t.kho, t.da, b, {b.id:b}, t.k.kho, LUC) is not None
    finally:
        t.kho.close()


def test_san_nguy_hiem_cha(tmp_path):
    t = dung(tmp_path, viec(parent="cha"))
    try:
        thiet_lap(t)
        b = viec(parent="cha")
        cha = bug("cha", labels=["rui-ro:bao-mat"])
        assert quyet_dinh(t.kho, t.da, b, {b.id:b, "cha":cha}, t.k.kho)["co"] == "lon"
    finally:
        t.kho.close()


from dataclasses import replace
from types import SimpleNamespace
import json
import threading
import pytest
from tram.chay_cli.stream import DocStream
from tram.han_muc.claude import NguonHanMucClaude
from tram.tho.co_model import dung_model
from tram.giao_viec.pipeline import TrangThaiBead, buoc_ke_tiep
from tram.giao_viec.su_kien import SK
from tram.phieu.bao import ThanBao
from tram.giao_viec.co_de_xuat import con_quy_trinh


def test_model_thieu_khong_pha_duong_cu():
    d = DocStream(NguonHanMucClaude(), khe_id="B/c")
    d.an(json.dumps({"type":"system", "subtype":"init", "model":"claude-opus-4-6"}))
    d.an(json.dumps({"type":"assistant", "message":{"id":"x"}}))
    k = d.ket_qua(ma_thoat=0, bi_dung=False, thoi_gian_ms=0, digest_log="")
    assert k.mo_hinh == "claude-opus-4-6"
    assert dung_model(None, k) and not dung_model({"model":"opus"}, k)


def test_spike_moi_van_qc_va_kiem_lai_hong_khong_qc():
    ds = [SK(1,"giao.nhan",{"buoc":"code", "giao_id":"g", "luot":1, "co":{"co":"nho"}},""),
          SK(2,"giao.ket_thuc",{"giao_id":"g", "ket_thuc":"xong", "ly_do":None,"commit":"a"},""),
          SK(3,"kiem.lai",{"giao_id":"g", "luot":1,"commit":"a", "dat":True,"digest_tieu_chi":"t"},""),
          SK(4,"giao.cong_bo",{"commit":"a"},"")]
    tt = TrangThaiBead(False,False,False,False,"t",True)
    assert buoc_ke_tiep(ds, tt) == "qc"
    assert buoc_ke_tiep(ds, replace(tt, bi_chan=True)) == "cho"
    ds[2].du_lieu["dat"] = False
    assert buoc_ke_tiep(ds, tt) != "qc"
    ds[2].du_lieu["dat"] = True
    ds[0].du_lieu.pop("co")
    assert buoc_ke_tiep(ds, tt) == "cot_3"


def test_duyet_bi_thay_trong_khoang_chon_cap():
    q = {"co":"vua", "thieu":[], "pham_vi":["x"], "ban_luat":"v1", "plan":1}
    ds = [SK(1,"co.plan",{"co":"vua","pham_vi":["x"],"ban_luat":"v1"},""),
          SK(2,"co.duyet",{"plan":1},"")]
    assert con_quy_trinh(ds, SimpleNamespace(co=q))
    ds.append(SK(3,"co.plan",{"co":"vua","pham_vi":["x"],"ban_luat":"v1"},""))
    assert not con_quy_trinh(ds, SimpleNamespace(co=q))
    assert con_quy_trinh(ds, SimpleNamespace(co=None))


def test_sai_model_dung_truoc_bao_xong(monkeypatch):
    from tram.tho import phieu_chay as m
    from tram.chay_cli.giao_dien import KetQuaChay
    goi = []
    pc = SimpleNamespace(p=SimpleNamespace(co={"model":"opus"}))
    td = SimpleNamespace(can_hoi=False, xong={"noi_dung":"tự khai opus"},
                         bat_dau=lambda: td, ket_thuc=lambda: None)
    monkeypatch.setattr(m, "ly_do_khong_chay", lambda *a: None)
    monkeypatch.setattr(m, "TheoDoi", lambda *a, **k: td)
    monkeypatch.setattr(m, "chay_mot_lan", lambda *a: KetQuaChay(0,True,False,False,False,
                                                            mo_hinh="claude-sonnet-4-6"))
    monkeypatch.setattr(m, "ket_thuc_mem", lambda *a: goi.append(a[-1]))
    monkeypatch.setattr(m, "ket_thuc_xong", lambda *a: pytest.fail("không được xong"))
    assert m._mot_vong(pc, SimpleNamespace(dong_ho=lambda:None), SimpleNamespace(lenh=None)) == "sai-model"
    assert goi == ["sai-model"]
    ThanBao(khe_id="B/c", giao_id="g", luot=1, loai="bi", ly_do="sai-model", request_id="request1")


from dataclasses import replace
import json
import pytest
from giao_viec_gia import dung, bug
from kho_phieu_gia import LUC
from tram.giao_viec.co_plan import ghi_plan, duyet, review
from tram.giao_viec.co_nguon import quyet_dinh
from tram.giao_viec.su_kien import su_kien_bead
from tram.giao_viec.co_dem import cham_co
from tram.giao_viec.co_bao_ve import BEN, nguy_hiem
from tram.cau_hinh.du_an import nap_du_an
from tram.chay_cli.stream import DocStream
from tram.han_muc.claude import NguonHanMucClaude


def test_phu_thuoc_chua_biet_khong_cham_nho(tmp_path):
    from tram.beads.mo_hinh import PhuThuoc
    t = dung(tmp_path, viec())
    try:
        thiet_lap(t)
        b = replace(viec(), phu_thuoc=(PhuThuoc("mat", "related"),))
        q = quyet_dinh(t.kho, t.da, b, {b.id:b}, t.k.kho)
        assert "phu-thuoc" in q["thieu"] and q["co"] == "vua"
    finally:
        t.kho.close()


def test_nguy_hiem_bo_bao_ve_phu_kill_list():
    for path in ["tram/api/bao_mat.py", "tram/kiem/danh_tinh.py", "tram/chu/cai_dat_tho.py",
                 "tram/phieu/luoc_do.py", "tram/cong_bo/git.py", "tram/han_muc/luat.py",
                 "du-an/x.yaml", "tram/tho/principal.py", "tram/nho/bi_mat.py"]:
        assert nguy_hiem([path], (), ben=True)


def test_du_an_khong_cau_hinh_giu_none_va_sai_thi_loi(tmp_path):
    p = tmp_path / "x.yaml"
    p.write_text("ten: x\nduong_dan: /tmp/x\n")
    assert nap_du_an("x", thu_muc=tmp_path).theo_co is None
    p.write_text("ten: x\nduong_dan: /tmp/x\ntheo_co: null\n")
    with pytest.raises(ValueError):
        nap_du_an("x", thu_muc=tmp_path)


def test_luot_cu_khong_bi_gan_co_hoi_to(tmp_path):
    from tram.giao_viec.co_nguon import chan_buoc
    t = dung(tmp_path, viec())
    try:
        thiet_lap(t)
        with t.kho.giao_dich():
            t.kho.ghi_su_kien(t.da.ten,"giao.nhan",{"buoc":"code", "luot":1},luc=LUC,bead_id="hr-1")
        assert chan_buoc(t.kho,t.da,viec(),{"hr-1":viec()},t.k.kho,LUC) is None
    finally:
        t.kho.close()


def test_model_init_hien_thi_cu_van_giu():
    d = DocStream(NguonHanMucClaude(), khe_id="B/c")
    for model in ("claude-sonnet-4-6", "claude-opus-4-6"):
        d.an(json.dumps({"type":"system", "subtype":"init", "model":model}))
    assert d.mo_hinh == "claude-opus-4-6"


def test_plan_duyet_cho_phep_vua_va_lon_chay_ca_bo(tmp_path, monkeypatch):
    import hashlib
    from types import SimpleNamespace
    from tram.giao_viec import co_de_xuat
    t = dung(tmp_path, viec(labels=["cot:ai-lam", "co:lon"]))
    try:
        thiet_lap(t)
        b = t.g.beads["hr-1"]
        q = quyet_dinh(t.kho,t.da,b,{b.id:b},t.k.kho)
        raw = b"# Plan da xem"
        ma = ghi_plan(t.kho,t.da.ten,b.id,"a"*40,"docs/plans/b.md",
                      hashlib.sha256(raw).hexdigest(),"B/claude-2",q,LUC)
        duyet(t.kho,t.da.ten,b.id,ma,LUC)
        review(t.kho,t.da.ten,b.id,ma,"B/claude-1","dat","r1",LUC)
        monkeypatch.setattr(co_de_xuat,"_git",lambda *a,**kw:SimpleNamespace(stdout=raw))
        dx = t.bo.chon("B/claude-1",None)
        assert dx.co["model"] == "opus" and dx.lenh_kiem == ["sh kiem.sh"]
        assert "# Plan da xem" in dx.goi_ngu_canh
        assert t.bo.con_hop_le(dx)
    finally:
        t.kho.close()


from dataclasses import replace
from phieu_gia import de_xuat
from tram.giao_viec.chon import khe_nhan, UngVien
from tram.phieu.trang_thai import trang_thai_khe
from giao_viec_gia import dung
from kho_phieu_gia import LUC


def test_json_phieu_cu_khong_them_khoa():
    dx = de_xuat()
    assert "co" not in dx.model_dump()
    assert '"co"' not in dx.model_dump_json()
    assert de_xuat(co={"co":"nho"}).model_dump()["co"] == {"co":"nho"}


def test_khe_dang_lam_khong_claim_moi(tmp_path):
    t = dung(tmp_path, viec())
    try:
        thiet_lap(t)
        uv = UngVien(t.da,viec(),"code",False,frozenset())
        ds = trang_thai_khe(t.kho,bay_gio=LUC,ch=t.bo.ch)
        ds = [replace(k,trang_thai="lam") for k in ds]
        assert not khe_nhan("B/claude-2",None,uv,ds,t.bo.ch,model="sonnet")
    finally:
        t.kho.close()


from dataclasses import replace
import pytest
from test_bo_giao_viec_spec import F, KHE_SPEC
from giao_viec_gia import dung
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.ke_hoach import DeXuatBead
from tram.phieu.cap import cap_phieu
from kho_phieu_gia import LUC


def test_spec_cung_chon_model_nhung_khong_doi_quyen(tmp_path):
    t = dung(tmp_path,F,khe=KHE_SPEC)
    try:
        thiet_lap(t)
        fetch(t.k.kho)
        assert t.bo.chon("B/claude-2",None) is None  # khe này chỉ Sonnet; thiếu phạm vi ít nhất vừa
        dx = t.bo.chon("B/claude-1",None)
        assert dx.co["model"] == "opus" and dx.buoc == "spec"
        assert dx.co["effort"] == "high"
        assert not dx.lenh_cho_phep and not dx.can_lenh_kiem and not dx.can_moi_truong_kiem
        assert t.g.so_lan("nhan_viec") == 0
        assert cap_phieu(t.kho,"B/claude-1",dx,bay_gio=LUC,ch=t.bo.ch,
                         con_hop_le=t.bo.con_hop_le).phieu is not None
    finally:
        t.kho.close()


def test_agent_khong_de_xuat_nhan_co():
    for label in ("co:nho","co:vua","co:lon"):
        with pytest.raises(ValueError):
            DeXuatBead(khoa="a",tieu_de="A",loai="task",uu_tien=2,nghiem_thu="A",nhan=[label])


from dataclasses import replace
from giao_viec_gia import dung
from tram.giao_viec import co_nguon


def test_duong_bat_buoc_co_san_truoc_luot_dau(tmp_path,monkeypatch):
    t = dung(tmp_path,viec())
    try:
        thiet_lap(t)
        goi = []
        def cam(db, kg, da, sha):
            goi.append(sha)
            return ("src/a.py",)
        monkeypatch.setattr(co_nguon,"cam_tu_lenh",cam)
        q = co_nguon.quyet_dinh(t.kho,t.da,viec(),{"hr-1":viec()},t.k.kho)
        assert q["co"] == "lon" and goi
    finally:
        t.kho.close()


from tram.giao_viec.pipeline import TrangThaiBead, buoc_ke_tiep
from tram.giao_viec.su_kien import SK
from tram.giao_viec.co_nguon import can_code_lai


def test_nang_co_khong_tai_dung_lenh_kiem_cua_phieu_nho():
    ds = [SK(1,"giao.nhan",{"buoc":"code", "giao_id":"g", "luot":1,
                            "co":{"co":"nho", "ban_luat":"v1"}},""),
          SK(2,"giao.ket_thuc",{"giao_id":"g", "ket_thuc":"xong", "ly_do":None,"commit":"a"},""),
          SK(3,"co.can-code-lai",{"giao_id":"g"},"")]
    tt = TrangThaiBead(False,False,False,False,"t",False)
    assert can_code_lai(ds, {"co":"lon", "ban_luat":"v1"})
    assert buoc_ke_tiep(ds, tt) == "code"
    ds.append(SK(4,"giao.nhan",{"buoc":"code","giao_id":"g2","luot":2,
                                "co":{"co":"lon","ban_luat":"v1"}},""))
    assert not can_code_lai(ds, {"co":"lon", "ban_luat":"v1"})
    assert not can_code_lai(ds, {"co":"lon", "ban_luat":"v2"})


from dataclasses import replace
from bead_gia import KHOI_BAN_GIAO
from giao_viec_gia import dung
from kho_phieu_gia import LUC
from tram.phieu.cap import cap_phieu
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.co_xet_plan import xet_plan
from tram.giao_viec.su_kien import su_kien_bead, SK
from tram.giao_viec.de_xuat import cha_cua
from tram.giao_viec.co_de_xuat import con_quy_trinh
from tram.giao_viec.co_plan import ghi_plan, duyet


def test_nhan_plan_tu_sha_ban_giao_va_stream_quan_ly(tmp_path):
    t = dung(tmp_path,viec(labels=["cot:ai-lam","co:vua"]))
    try:
        thiet_lap(t)
        dx = t.bo.chon("B/claude-1",None)
        p = cap_phieu(t.kho,"B/claude-1",dx,bay_gio=LUC,ch=t.bo.ch,con_hop_le=t.bo.con_hop_le).phieu
        raw = "\n".join("## " + x + "\nNội dung." for x in
                         ("Mục tiêu","Phạm vi","Cách sửa","Kiểm chứng","Rủi ro","Đường lui"))
        bg_file = "docs/handovers/plan.md"
        sha = t.k.day(p.repo.nhanh,{"docs/plans/hr-1.md":raw,bg_file:"Bàn giao"},tu=p.repo.cha)
        fetch(t.k.kho)
        bg = {**KHOI_BAN_GIAO,"loai":"chinh-thuc","nhanh":p.repo.nhanh,"luot":p.luot,
              "commit":sha,"pr":None,"file_ban_giao":bg_file,"lenh_kiem":[],
              "doi_chieu_nghiem_thu":[{"tieu_chi":p.tieu_chi[0],"dat":True,"bang_chung":"docs/plans/hr-1.md"}]}
        with t.kho.giao_dich():
            t.kho.ghi_su_kien(t.da.ten,"chay.xong",{"giao_id":p.giao_id,"ket_thuc":"xong",
                             "mo_hinh":"claude-opus-4-6"},luc=LUC,bead_id=p.bead_id)
        assert xet_plan(t.kho,t.k.kho,p,{"commit":sha,"ban_giao":bg},sha,LUC)[0] is None
        ds = su_kien_bead(t.kho,t.da.ten,p.bead_id)
        plan = next(s for s in ds if s.loai == "co.plan")
        assert plan.du_lieu["commit"] == sha and plan.du_lieu["khe"] == p.khe_id
        assert not any(s.loai == "co.duyet" for s in ds)
        duyet(t.kho,t.da.ten,p.bead_id,plan.id,LUC)
        assert not con_quy_trinh(su_kien_bead(t.kho,t.da.ten,p.bead_id),dx)
    finally:
        t.kho.close()


def test_commit_plan_khong_thay_commit_code_khi_tiep_tuc():
    ds = [SK(1,"giao.nhan",{"luot":1,"buoc":"code"},""),
          SK(2,"giao.cong_bo",{"luot":1,"commit":"a"*40},""),
          SK(3,"giao.nhan",{"luot":2,"buoc":"spec","co":{"pha":"plan"}},""),
          SK(4,"giao.cong_bo",{"luot":2,"commit":"b"*40},"")]
    assert cha_cua(ds,"code",None,"main") == "a"*40


import hashlib
from dataclasses import replace
from giao_viec_gia import dung
from kho_phieu_gia import LUC
from tram.giao_viec.co_plan import ghi_plan, duyet, review
from tram.giao_viec.co_nguon import quyet_dinh
from tram.phieu.cap import cap_phieu
from tram.giao_viec.su_kien import su_kien_bead


def test_plan_tu_dong_dung_phieu_spec_va_ngan_sach_cu(tmp_path):
    t = dung(tmp_path,viec(labels=["cot:ai-lam","co:vua"]))
    try:
        thiet_lap(t)
        dx = t.bo.chon("B/claude-1",None)
        assert dx.buoc == "spec" and dx.co["pha"] == "plan" and dx.co["model"] == "opus"
        assert dx.co["effort"] == "high"
        assert not dx.lenh_cho_phep and not dx.can_lenh_kiem
        assert dx.ngan_sach.phut == t.da.giao.ngan_sach.qc.phut
        assert t.g.so_lan("nhan_viec") == 0
        p = cap_phieu(t.kho,"B/claude-1",dx,bay_gio=LUC,ch=t.bo.ch,
                       con_hop_le=t.bo.con_hop_le).phieu
        assert p and t.kho.db.execute("SELECT count(*) FROM giu_ngan_sach").fetchone()[0] == 1
    finally:
        t.kho.close()


def test_review_plan_khac_khe_va_dung_sau_ba_ket_luan(tmp_path):
    t = dung(tmp_path,viec(labels=["cot:ai-lam","co:lon"]))
    try:
        thiet_lap(t)
        b = t.g.beads["hr-1"]
        q = quyet_dinh(t.kho,t.da,b,{b.id:b},t.k.kho)
        for i in range(3):
            p = ghi_plan(t.kho,t.da.ten,b.id,t.k.main,"docs/plans/hr-1.md",str(i)*64,"B/claude-2",q,LUC)
            duyet(t.kho,t.da.ten,b.id,p,LUC)
            dx = t.bo.chon("B/claude-1",None)
            assert dx.buoc == "spec" and dx.co["pha"] == "review" and dx.co["plan"] == p
            assert dx.co["effort"] == "high"
            assert t.bo.chon("B/claude-2",None) is None
            review(t.kho,t.da.ten,b.id,p,"B/claude-1","tra-ve",str(i),LUC)
        assert t.bo.chon("B/claude-1",None) is None
        assert t.g.so_lan("nhan_viec") == 0
        ds = su_kien_bead(t.kho,t.da.ten,b.id)
        assert any(s.loai == "co.cho" and s.du_lieu["ly_do"] == "hoi-dai-ca-ba-vong" for s in ds)
        assert any(s.loai == "escalation.tao" for s in ds)
    finally:
        t.kho.close()




from dataclasses import replace
from giao_viec_gia import dung
from kho_phieu_gia import LUC
from tram.giao_viec.co_plan import ghi_plan, duyet
from tram.giao_viec.co_nguon import quyet_dinh, can_code_lai
from tram.giao_viec.su_kien import SK


def test_doi_nguong_khong_bat_code_lai_luot_da_xong():
    ds = [SK(1, 'giao.nhan', {'buoc':'code','co':{'co':'vua','ban_luat':'cu'}}, '')]
    assert not can_code_lai(ds, {'co':'vua','ban_luat':'moi'})


def test_plan_khong_noi_thang_du_lieu_vao_prompt(tmp_path, monkeypatch):
    import hashlib
    from types import SimpleNamespace
    from tram.giao_viec import co_de_xuat
    t = dung(tmp_path, viec(labels=['cot:ai-lam','co:vua']))
    try:
        thiet_lap(t)
        b = t.g.beads['hr-1']
        q = quyet_dinh(t.kho,t.da,b,{b.id:b},t.k.kho)
        raw = b'INJECT_FROM_PLAN'
        p = ghi_plan(t.kho,t.da.ten,b.id,'a'*40,'docs/plans/hr-1.md',hashlib.sha256(raw).hexdigest(),'B/claude-2',q,LUC)
        duyet(t.kho,t.da.ten,b.id,p,LUC)
        monkeypatch.setattr(co_de_xuat,'_git',lambda *a,**kw:SimpleNamespace(stdout=raw))
        dx = t.bo.chon('B/claude-1',None)
        from tram.cham_cot.prompt import boc_khong_tin_cay
        assert boc_khong_tin_cay(raw.decode()) in dx.goi_ngu_canh
    finally:
        t.kho.close()


def test_plan_phai_giu_duong_cam_du_an(tmp_path):
    from types import SimpleNamespace
    from bead_gia import KHOI_BAN_GIAO
    from tram.phieu.cap import cap_phieu
    from tram.giao_viec.git_kiem import fetch
    from tram.giao_viec.xu_ly_viec import _xet
    t = dung(tmp_path, viec(labels=['cot:ai-lam','co:vua']))
    try:
        thiet_lap(t)
        t.da = replace(t.da, giao=replace(t.da.giao, duong_dan_cam=('docs/handovers/cam.md',)))
        dx = t.bo.chon('B/claude-1',None)
        p = cap_phieu(t.kho,'B/claude-1',dx,bay_gio=LUC,ch=t.bo.ch,con_hop_le=t.bo.con_hop_le).phieu
        raw = '\n'.join('## '+x+'\nNoi dung' for x in ('Mục tiêu','Phạm vi','Cách sửa','Kiểm chứng','Rủi ro','Đường lui'))
        file = 'docs/handovers/cam.md'
        sha = t.k.day(p.repo.nhanh,{'docs/plans/hr-1.md':raw,file:'Cam'},tu=p.repo.cha)
        fetch(t.k.kho)
        bg = {**KHOI_BAN_GIAO,'loai':'chinh-thuc','nhanh':p.repo.nhanh,'luot':p.luot,'commit':sha,
              'pr':None,'file_ban_giao':file,'lenh_kiem':[],
              'doi_chieu_nghiem_thu':[{'tieu_chi':p.tieu_chi[0],'dat':True,'bang_chung':file}]}
        with t.kho.giao_dich():
            for loai,d in [('chay.xong',{'ket_thuc':'xong','mo_hinh':'claude-opus-4-6'}),
                           ('giao.cong_bo',{'commit':sha}),('bao.xong',{'commit':sha,'ban_giao':bg})]:
                t.kho.ghi_su_kien(t.da.ten,loai,{'giao_id':p.giao_id,'luot':p.luot,**d},luc=LUC,bead_id=p.bead_id)
        cv = SimpleNamespace(giao_id=p.giao_id,du_an=t.da.ten,bead_id=p.bead_id,ket_thuc='xong')
        assert _xet(t.kho,cv,t.da,t.k.kho,LUC)[0] == 'dong-file-cau-hinh'
    finally:
        t.kho.close()


def test_s9_sau_code_nang_co_phai_den_duoc_plan(tmp_path):
    from tram.giao_viec.git_kiem import fetch
    from tram.giao_viec.co_nguon import chan_buoc
    t = dung(tmp_path, viec())
    try:
        thiet_lap(t)
        t.da.theo_co['nhom']['secret/'] = 'secret'
        sha = t.k.day('tram/hr-1', {'secret/token': 'du lieu gia'}, tu=t.k.main)
        fetch(t.k.kho)
        with t.kho.giao_dich():
            for loai,d in [
                ('giao.nhan', {'buoc':'code','khe_id':'B/claude-2','cha':t.k.main,
                              'ngan_sach':{'so_lan_chay':1,'phut':1},
                              'co':{'co':'nho','ban_luat':t.da.theo_co['ban_luat']}}),
                ('giao.cong_bo', {'commit':sha}),
                ('giao.ket_thuc', {'ket_thuc':'xong','ly_do':None,'commit':sha})]:
                t.kho.ghi_su_kien(t.da.ten,loai,{'giao_id':'g1','luot':1,**d},luc=LUC,bead_id='hr-1')
        b = replace(t.g.beads['hr-1'], design='<!-- pham-vi-co:v1 -->\n- src/a.py\n- secret/token\n<!-- /pham-vi-co -->')
        t.g.beads[b.id] = b
        assert chan_buoc(t.kho,t.da,b,{b.id:b},t.k.kho,LUC) == 'cho-plan'
        dx = t.bo.chon('B/claude-1',None)
        assert dx is not None and dx.co['pha'] == 'plan'
    finally:
        t.kho.close()


def test_phieu_plan_khong_mang_vai_coder_va_tieu_chi_cu(tmp_path):
    t = dung(tmp_path,viec(labels=['cot:ai-lam','co:vua']))
    try:
        thiet_lap(t)
        dx = t.bo.chon('B/claude-1',None)
        assert '## Lớp 2 — Vai spec' in dx.goi_ngu_canh
        assert dx.tieu_chi[0] in dx.goi_ngu_canh
    finally:
        t.kho.close()


def test_co_khong_tu_noi_lenh_cho_spike_tai_lieu(tmp_path):
    t = dung(tmp_path, viec(issue_type="spike"))
    try:
        thiet_lap(t)
        # Phiếu spike hiện có không được chạy lệnh: cỡ không tự cấp thêm quyền.
        assert t.bo.chon("B/claude-2", None) is None
        assert t.g.so_lan("nhan_viec") == 0
    finally:
        t.kho.close()


def test_file_ban_giao_bat_buoc_khong_tinh_ngoai_pham_vi(tmp_path, monkeypatch):
    # bs-ie0 21/10: file bàn giao docs/handovers/ (bắt buộc) làm việc nhỏ kẹt "xac-nhan-pham-vi" ở lượt sau.
    from tram.giao_viec import co_nguon
    t = dung(tmp_path, viec())
    try:
        thiet_lap(t)
        with t.kho.giao_dich():
            t.kho.ghi_su_kien(t.da.ten, "giao.nhan", {"buoc": "code", "luot": 1,
                "giao_id": "g1", "cha": "a" * 40, "co": {"co": "nho"}}, luc=LUC, bead_id="hr-1")
            t.kho.ghi_su_kien(t.da.ten, "giao.cong_bo", {"luot": 1, "commit": "b" * 40}, luc=LUC, bead_id="hr-1")
        monkeypatch.setattr(co_nguon, "tep_doi", lambda *a: ["src/a.py", "docs/handovers/2026-10-21-hr-1.md"])
        b = viec()
        q = quyet_dinh(t.kho, t.da, b, {b.id: b}, t.k.kho)
        assert q["diff_ngoai"] == [] and q["dem"]["file"] == 1
        assert chan_buoc(t.kho, t.da, b, {b.id: b}, t.k.kho, LUC) != "xac-nhan-pham-vi"
    finally:
        t.kho.close()

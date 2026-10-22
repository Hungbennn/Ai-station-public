"""Bản giả CHỈ DÙNG TRONG TEST — không bao giờ import từ mã `tram/` (spec 3 §3 cổng 3: không đánh dấu sẵn sàng
triển khai bằng fixture giả)."""
from tram.chay_cli.giao_dien import KetQuaChay
from tram.han_muc.mo_hinh import CuaSo, HanMuc


class NguonHanMucGia:
    """Dòng `{"gia_han_muc": {"5h": 62.0}, "doc_luc": "…Z"}` → HanMuc; `{"gia_het": true}` → hết hạn mức."""

    def doc_dong(self, dong, *, khe_id, bay_gio):
        if "gia_han_muc" not in dong:
            return None
        return HanMuc(khe_id=khe_id, nguon="stream", cua_so=[
            CuaSo(loai=k, trang_thai="biet", phan_tram=v, doc_luc=dong["doc_luc"])
            for k, v in dong["gia_han_muc"].items()])

    def het_han_muc(self, dong):
        return bool(dong.get("gia_het"))


class ChayCLIGia:
    """Trả lần lượt các `KetQuaChay` đã soạn; ghi lại đối số mỗi lần gọi."""

    def __init__(self, *ket_qua: KetQuaChay):
        self.con_lai, self.da_goi = list(ket_qua), []

    def chay(self, argv, *, cwd, env, stdin, log, dung, nguon):
        self.da_goi.append({"argv": argv, "cwd": cwd, "env": env})
        return self.con_lai.pop(0)

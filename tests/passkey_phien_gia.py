"""Cookie jar của client test nghiệp vụ: đăng ký + assertion thật, không override cửa bảo mật."""
from passkey_gia import KhoaGia
from tram.passkey.dich_vu import DichVu
from webauthn.helpers import base64url_to_bytes


def dang_nhap_app(app, path):
    ch = app.state.pt.cau_hinh
    app.state.passkey_path = path
    dv = DichVu(path,ch.dai_ca_logins[0],ch.ten_may_b)
    k = KhoaGia()
    app.state.khoa_test = k
    o = dv.bat_dau('dang-ky',ma=dv.cap_ma())
    dv.ket_thuc(o['id'],k.tra(base64url_to_bytes(o['publicKey']['challenge']),dang_ky=True,
                             rp=ch.ten_may_b,origin='https://'+ch.ten_may_b))
    o = dv.bat_dau('phien')
    c = dv.ket_thuc(o['id'],k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                                rp=ch.ten_may_b,origin='https://'+ch.ten_may_b))['cookie']
    app.state.cookie_test = '__Host-tram-phien='+c
    return app


def headers_r(app, path, than):
    """Quyền R ký thật cho test nghiệp vụ đã mở phiên; không thay dependency sản phẩm."""
    from api_gia import DAI_CA
    from tram.passkey.chinh_sach import rang_buoc
    ch = app.state.pt.cau_hinh
    dv = DichVu(app.state.passkey_path, ch.dai_ca_logins[0], ch.ten_may_b)
    c = app.state.cookie_test.split('=', 1)[1]
    o = dv.bat_dau('r', cookie=c, rang=rang_buoc(path, than))
    a = app.state.khoa_test.tra(base64url_to_bytes(o['publicKey']['challenge']),
                               rp=ch.ten_may_b, origin='https://'+ch.ten_may_b)
    q = dv.ket_thuc(o['id'], a)['quyen']
    return {**DAI_CA, 'Cookie':app.state.cookie_test, 'X-Tram-Xac-Nhan':q}

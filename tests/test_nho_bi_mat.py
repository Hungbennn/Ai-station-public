"""Lát 1b-4 Task 0 (D23): bộ quét bí mật. Mọi chuỗi giống khoá đều GIẢ và ghép lúc chạy (`gia`) — file này không
chứa nguyên văn chuỗi nào giống khoá thật; phần thân lặp một ký tự để chỉ đúng nhóm đang thử được báo."""
import base64
import hashlib
import random
import string
import uuid

import pytest

from tram.nho.bi_mat import (LOAI_SU_KIEN, NGUONG_ENTROPY, NGUONG_ENTROPY_HEX, NHOM, LoiBiMat, chan_bi_mat,
                             entropy, quet)


def gia(*phan: str) -> str:
    return "".join(phan)


def ngau_nhien(n: int, bo=string.ascii_letters + string.digits, hat=7) -> str:
    r = random.Random(hat)
    return "".join(r.choice(bo) for _ in range(n))


KHOA_DA_BIET = [
    gia("sk-", "ant-", "x" * 30), gia("sk-", "x" * 40), gia("sk-", "proj-", "x" * 40),
    gia("gh", "p_", "x" * 36), gia("gh", "o_", "x" * 36), gia("gh", "u_", "x" * 36), gia("gh", "s_", "x" * 36),
    gia("github", "_pat_", "x" * 30), gia("xo", "xb-", "1" * 12), gia("xo", "xp-", "1" * 12),
    gia("xo", "xa-", "1" * 12),
    gia("AK", "IA", "X" * 16), gia("AS", "IA", "X" * 16), gia("AI", "za", "x" * 35),
    gia("1234", "5678", ":", "x" * 35), gia("https://api.telegram.org/bot", "123456789", ":", "x" * 35, "/getMe"),
    gia("ey", "J", "a" * 10, ".", "ey", "J", "b" * 10, ".", "c" * 10)]


@pytest.mark.parametrize("khoa", KHOA_DA_BIET)
def test_tien_to_khoa_da_biet(khoa):
    assert quet([f"Đã thử `{khoa}` trong cấu hình."]) == {"khoa_da_biet": 1}


@pytest.mark.parametrize("loai", ["RSA ", "OPENSSH ", "EC ", ""])
def test_khoi_khoa_rieng(loai):
    assert quet([gia("-----BEGIN ", loai, "PRIVATE", " KEY-----\nabc\n-----END ", loai, "PRIVATE KEY-----")]) == {
        "khoa_rieng": 1}


@pytest.mark.parametrize("s", [
    gia("pass", "word=abc"), gia("DB_PASS", "WORD: abc"), gia("pass", "wd = 'abc'"), gia("pw", "d: abc"),
    gia("client_sec", "ret = \"abc\""), gia("x-api", "-key: abc"), gia("\"api", "key\": \"abc\""),
    gia("API_", "KEY=abc"), gia("tok", "en: abc"), gia("Author", "ization: Bearer abc"), gia("bear", "er=abc"),
    gia("Author", "ization: Basic abc"),
    gia("postgres://", "u", ":", "p", "@db.local/hr"), gia("https://", "u", ":", "p", "@git.local"),
    gia("DATABASE_URL", "=", "x" * 8), gia("export S3_BUCKET", "=", "x" * 8)])
def test_gan_gia_tri_nhay_cam(s):
    assert quet([f"Ghi chú cấu hình:\n{s}\n"]) == {"gan_gia_tri": 1}


@pytest.mark.parametrize("s", [
    base64.urlsafe_b64encode(hashlib.sha256(b"gia-1").digest()).decode().rstrip("="),
    base64.b64encode(hashlib.sha256(b"gia-2").digest()[:30]).decode(),
    ngau_nhien(32), ngau_nhien(40, hat=8), hashlib.md5(b"gia-3").hexdigest()])
def test_chuoi_entropy_cao(s):
    assert quet([f"Giá trị thử: {s} (đã xoá)"]) == {"entropy_cao": 1}


@pytest.mark.parametrize("s", [
    hashlib.sha1(b"commit").hexdigest(), hashlib.sha256(b"digest").hexdigest(),
    f"sha256:{hashlib.sha256(b'd').hexdigest()}",
    str(uuid.uuid5(uuid.NAMESPACE_DNS, "ben-station")), "1" * 40,
    "Chạy `php artisan test --filter` thay phpunit; seeder chậm 40 giây.",
    "Hoa hồng tính trên giá sau giảm giá, không tính trên giá niêm yết.",
    "test_qc_dat_nap_ban_giao_cua_kiem_lai_cung_commit và test_kill_nhom_chay_cung_principal_khong_qua_shell xanh",
    "max_tokens=4096, token_vao: 1500; tokens đã dùng ít",
    "password=\"\" (rỗng), token: None, api_key = <khoá của Đại ca>",
    "Header `Authorization: Bearer <tram-nho-token>` lấy từ Keychain; secret: $TRAM_TOKEN",
    "/Users/dai-ca/Developer/Ben Station/.worktrees/p1b4/tram/nho/nguon_ban_giao_va_giao_viec.py",
    "frontend/src/van_phong/NhanVat3DTrongVanPhong.vue, docs/handovers/review-codex-dot3/REVIEW-CODEX-TONG-HOP.md",
    "docs/plans/2026-10-15-lat-1b-4-nguon-ky-uc-phan-3-4.md", "ssh://git@github.com:22/o/r.git"])
def test_khong_bao_nham(s):
    assert quet([s]) == {}


def test_dem_theo_nhom_va_so_luong():
    s = gia("gh", "p_", "x" * 36, " và ", "sk-", "x" * 40, "\n-----BEGIN ", "PRIVATE KEY-----")
    assert quet([s, gia("tok", "en=abc")]) == {"khoa_da_biet": 2, "khoa_rieng": 1, "gan_gia_tri": 1}
    assert list(quet([gia("tok", "en=abc"), s])) == ["khoa_da_biet", "khoa_rieng", "gan_gia_tri"]   # thứ tự NHOM


def test_entropy_va_nguong():
    assert entropy("aaaa") == 0 and entropy("ab") == 1 and entropy("abcd") == 2
    assert (NGUONG_ENTROPY, NGUONG_ENTROPY_HEX, LOAI_SU_KIEN) == (4.2, 3.0, "nho.bo_bi_mat")
    assert NHOM == ("khoa_da_biet", "khoa_rieng", "gan_gia_tri", "entropy_cao")


def test_loi_bi_mat_khong_mang_doan_khop():
    khoa = gia("gh", "p_", "Sentinel", "0" * 28)
    chan_bi_mat("ban_giao", ["Không có gì nhạy cảm."])                 # sạch: không ném
    with pytest.raises(LoiBiMat) as e:
        chan_bi_mat("ban_giao", ["sạch", f"vướng: {khoa}"])
    assert str(e.value) == "nguồn ban_giao có dấu hiệu bí mật: khoa_da_biet ×1"
    assert e.value.su_kien(42) == ("nho.bo_bi_mat", {"su_kien_id": 42, "loai_nguon": "ban_giao",
                                                     "nhom": {"khoa_da_biet": 1}})
    assert "Sentinel" not in repr(e.value) + repr(e.value.su_kien(42)) and not issubclass(LoiBiMat, ValueError)

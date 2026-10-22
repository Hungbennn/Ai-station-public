"""Kho vận hành của phần 3 trong `~/.tram/su-kien.db` (spec 3 §6.6, §10): bảng riêng ngoài nhật ký sự kiện.
Ràng buộc trong kho: tối đa MỘT phiếu hiệu lực cho mỗi bead, mỗi khe, mỗi `khoa_chong_trung` (chỉ mục có điều kiện)."""
LUOC_DO = """
CREATE TABLE IF NOT EXISTS phieu (
  giao_id TEXT PRIMARY KEY,
  du_an TEXT NOT NULL, bead_id TEXT NOT NULL, khe_id TEXT NOT NULL, may_id TEXT NOT NULL,
  luot INTEGER NOT NULL, khoa_chong_trung TEXT NOT NULL,
  noi_dung TEXT NOT NULL,              -- JSON phiếu đầy đủ, GỒM ma_giao — chỉ nằm ở bảng này
  trang_thai TEXT NOT NULL CHECK (trang_thai IN ('hieu_luc', 'ket_thuc')),
  ket_thuc TEXT CHECK (ket_thuc IN ('xong', 'bi', 'het_han_muc', 'thu_hoi')),
  dung_mem TEXT,                       -- 'can-hoi': trạm yêu cầu dừng mềm theo phiếu
  han_giu TEXT NOT NULL, cap_luc TEXT NOT NULL, nhip_cuoi TEXT, ket_thuc_luc TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS phieu_mot_bead ON phieu(du_an, bead_id) WHERE trang_thai = 'hieu_luc';
CREATE UNIQUE INDEX IF NOT EXISTS phieu_mot_khe ON phieu(khe_id) WHERE trang_thai = 'hieu_luc';
CREATE UNIQUE INDEX IF NOT EXISTS phieu_mot_khoa ON phieu(khoa_chong_trung) WHERE trang_thai = 'hieu_luc';
CREATE TABLE IF NOT EXISTS luot_bead (
  du_an TEXT NOT NULL, bead_id TEXT NOT NULL, luot INTEGER NOT NULL, PRIMARY KEY (du_an, bead_id));
CREATE TABLE IF NOT EXISTS so_giao (ngay TEXT PRIMARY KEY, so INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS giu_ngan_sach (
  giao_id TEXT PRIMARY KEY, so_lan_chay INTEGER NOT NULL, phut INTEGER NOT NULL, token_ra INTEGER NOT NULL,
  quyet_toan TEXT);
CREATE TABLE IF NOT EXISTS bao_tho (
  request_id TEXT PRIMARY KEY, giao_id TEXT NOT NULL, loai TEXT NOT NULL, digest TEXT NOT NULL,
  ket_qua TEXT NOT NULL, luc TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS lan_chay (
  request_id TEXT PRIMARY KEY, khe_id TEXT NOT NULL, giao_id TEXT NOT NULL, lan INTEGER NOT NULL, luc TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS lan_chay_khe ON lan_chay(khe_id, luc);
CREATE TABLE IF NOT EXISTS cong_viec_cho (
  id INTEGER PRIMARY KEY, giao_id TEXT NOT NULL UNIQUE, du_an TEXT NOT NULL, bead_id TEXT NOT NULL,
  ket_thuc TEXT NOT NULL, su_kien_id INTEGER NOT NULL, luc TEXT NOT NULL, xong_luc TEXT);
CREATE TABLE IF NOT EXISTS nhip_tim (
  khe_id TEXT PRIMARY KEY, luc TEXT NOT NULL, giao_id TEXT, luot INTEGER, buoc_tho TEXT NOT NULL, han_muc TEXT);
CREATE TABLE IF NOT EXISTS may_tho (
  may_id TEXT PRIMARY KEY, bam_token TEXT NOT NULL, tao_luc TEXT NOT NULL, go_luc TEXT);
"""

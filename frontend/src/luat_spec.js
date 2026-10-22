// Luật hiển thị luồng feature (spec 4 §7.3; spec 2 §5.2 "Spec chờ duyệt") — thuần, test bằng node --test.
const SHA = /^[0-9a-f]{7,40}$/
const DIGEST = /^sha256:[0-9a-f]{64}$/
const MA = /^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/

// Duyệt spec gửi kèm đúng bản Đại ca đang xem; server thấy bản khác → 409 (G11).
export function thanDuyet(muc) {
  if (muc.loai !== 'spec') return {}
  const ct = muc.chi_tiet || {}
  return { expected_commit: ct.commit ?? null, digest_bead: ct.digest_bead ?? null }
}

export function coTheDuyetSpec(muc) {
  const ct = muc.chi_tiet || {}
  return muc.loai === 'spec' && SHA.test(ct.commit || '') && DIGEST.test(ct.digest_bead || '')
}

// Lệnh dán vào phiên Claude trên máy A: skill chỉ đọc, kiểm lại digest rồi in link để Đại ca tự bấm Duyệt.
export function lenhMayA(muc, goc) {
  if (!coTheDuyetSpec(muc) || !MA.test(muc.du_an || '') || !MA.test(muc.bead_id || '')) return ''
  const ct = muc.chi_tiet
  return `/xem-spec-cho-duyet ${muc.du_an} ${muc.bead_id} ${ct.commit} ${ct.digest_bead} ${goc}/#/phe-duyet`
}

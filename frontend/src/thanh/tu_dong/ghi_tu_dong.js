// Thao tác ghi của trang Tự động và nút Deploy ở Phê duyệt (spec dieu-khien-tu-dong "Chỉnh trên dashboard qua cửa
// ghi", tu-deploy "Nút Deploy", D129): mọi POST qua api.ghi (X-Tram) + mã thao tác mới mỗi lần bấm; URL dựng từ TÊN
// DỰ ÁN CỦA ROUTE (`layTen`, Codex Q10), kết quả về khi đã sang dự án khác thì bỏ. Cài đặt gửi đủ khoá +
// `expected_version` của bản chụp lúc bắt đầu sửa (`ban`, Codex Q9; mặc định bản đang xem) — 409 → "Cài đặt đã đổi —
// tải lại", giữ ô nhập; TẠM DỪNG / Tiếp tục không kiểm phiên bản (như estop); Deploy gửi `expected_commit` (TM-3).
// Hỏi lại bằng hộp xác nhận của trình duyệt như estop; câu hỏi rỗng thì gửi luôn.
import { ref, onScopeDispose } from 'vue'
import { ghi, thanGhi, boQuyenGhi } from '../../api.js'
import { hoiDeploy, hoiTamDung, thanCaiDat } from '../../luat_trang_tu_dong.js'

export const CHU_XUNG_DOT = 'Cài đặt đã đổi — tải lại'

export function dungGhiTuDong(layDl, taiLai, layTen) {
  const dangGui = ref(false)
  const loi = ref('')
  const xungDot = ref(false)
  let cho = null
  function boCho() {
    if (cho) boQuyenGhi(cho.duong, cho.than)
    cho = null
  }
  onScopeDispose(boCho, true)

  async function lam(ten, duoi, than, hoi, cau409 = '', hanhDong = '') {
    if (hoi && !window.confirm(hoi)) return false
    const duong = `/api/du-an/${encodeURIComponent(ten)}/tu-dong/${duoi}`
    const key = JSON.stringify([duong, { ...than, ma_thao_tac: null }])
    if (cho?.key !== key) {
      boCho()
      cho = { key, duong, than: structuredClone(than), hanhDong }
    }
    const yc = cho
    dangGui.value = true
    loi.value = ''
    xungDot.value = false
    try {
      await ghi(duong, yc.than, { hanhDong: yc.hanhDong || (duoi === 'cai-dat' ? 'Đổi cài đặt tự động'
        : duoi === 'deploy' ? 'Deploy' : duoi === 'tiep-tuc' ? 'Tiếp tục tự động' : 'Tạm dừng tự động'),
      dich: `Dự án ${ten}` })
      if (cho === yc) boCho()
      if (ten === layTen()) await taiLai()
      return true
    } catch (e) {
      if (ten === layTen()) {
        xungDot.value = e.status === 409
        loi.value = xungDot.value && cau409 ? cau409 : e.message
      }
      return false
    } finally {
      dangGui.value = false
    }
  }
  function luu(doi, hoi, ban = layDl()) {
    const ten = layTen()
    if (!ban || ban.du_an !== ten) {               // chưa tải xong / dữ liệu của dự án khác: không gửi
      loi.value = CHU_XUNG_DOT
      xungDot.value = true
      return Promise.resolve(false)
    }
    const moi = thanCaiDat(ban.cai_dat, doi)
    const hanhDong = Object.keys(moi.lenh).some(k => moi.lenh[k] !== ban.cai_dat.lenh[k]) ? 'Sửa lệnh deploy'
      : moi.tu_deploy && !ban.cai_dat.tu_deploy ? 'Bật tự deploy' : 'Đổi cài đặt tự động'
    return lam(ten, 'cai-dat', thanGhi({ cai_dat: moi }, ban.phien_ban), hoi, CHU_XUNG_DOT, hanhDong)
  }
  function tamDung(bat) {
    const ten = layTen()
    const ds = !bat && layDl()?.doi_soat
    let doi_soat
    if (ds) {
      const commit = window.prompt(`Lượt ${ds.ma} chưa rõ. Sau khi kiểm bản thực tế và lượt đã dừng, `
        + `nhập đúng SHA ${ds.commit} hoặc ${ds.truoc}.`)
      if (![ds.commit, ds.truoc].includes(commit)) return Promise.resolve(false)
      doi_soat = { ma: ds.ma, commit }
    }
    return lam(ten, bat ? 'tam-dung' : 'tiep-tuc', thanGhi(doi_soat ? { doi_soat } : {}, ''),
      bat ? hoiTamDung(ten) : '')
  }
  function deploy(commit) {
    const ten = layTen()
    return lam(ten, 'deploy', thanGhi({ expected_commit: commit }, layDl()?.phien_ban ?? ''), hoiDeploy(ten, commit))
  }
  return { dangGui, loi, xungDot, luu, tamDung, deploy }
}

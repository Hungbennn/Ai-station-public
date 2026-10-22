// Form "Sửa 3 lệnh" của khối Cài đặt (Codex Q9): chụp {du_an, phien_ban, cai_dat} lúc MỞ form và giữ tới lúc gửi —
// SSE tải lại trang chen giữa không đổi phiên bản đang sửa, nên tab cũ nhận 409 thay vì ghi đè lệnh mới bằng nháp cũ.
// 409 → giữ nháp, khối hiện "Cài đặt đã đổi — tải lại" + nút "Tải lại": lấy bản mới làm gốc, nháp giữ nguyên, cạnh ô
// nào khác thì hiện lệnh đang lưu ở trạm (`doiChieu`) để Đại ca đối chiếu rồi lưu lại hoặc huỷ.
import { reactive, ref } from 'vue'
import { doiLenh, hoiLuuLenh } from '../../luat_trang_tu_dong.js'

const chup = (dl) => ({ du_an: dl.du_an, phien_ban: dl.phien_ban, cai_dat: JSON.parse(JSON.stringify(dl.cai_dat)) })

export function dungSuaLenh(layDl, g, taiLai) {
  const dangSua = ref(false)
  const o = reactive({ deploy: '', kiem_song: '', lui: '' })
  const doiChieu = ref(null)
  let goc = null
  const xoaLoi = () => { g.loi.value = ''; g.xungDot.value = false }

  function mo() {
    goc = chup(layDl())
    Object.assign(o, goc.cai_dat.lenh)
    doiChieu.value = null
    xoaLoi()
    dangSua.value = true
  }
  function dong() {
    goc = null
    doiChieu.value = null
    xoaLoi()
    dangSua.value = false
  }
  async function luu() {
    if (!goc) return
    const d = doiLenh(goc.cai_dat, o)
    if (await g.luu(d, hoiLuuLenh(d.tu_deploy === false), goc)) dong()
  }
  async function taiLaiGoc() {
    if (await taiLai() !== true) return
    const moi = layDl()
    if (!goc || !moi || moi.du_an !== goc.du_an) return
    goc = chup(moi)
    doiChieu.value = { ...goc.cai_dat.lenh }
    xoaLoi()
  }
  return { dangSua, o, doiChieu, mo, dong, luu, taiLaiGoc }
}

// Tránh va chạm cho nhãn HTML phủ trên cảnh Văn phòng — hàm thuần, chạy khi đổi cỡ khung (không chạy mỗi khung hình).
// Mỗi nhãn: { loai, w, h, x0, y0 (vị trí mong muốn, góc trên-trái), diemNeo: {x, y} (điểm gốc trên màn hình), khe? }.
// Thứ tự đặt (ưu tiên giữ chỗ): bong bóng → huy hiệu → tên nhân vật → huy hiệu Giám đốc → biển phòng.
// Vật cản thêm: hình chữ nhật thân nhân vật (biển phòng tránh mọi nhân vật; nhãn của một khe tránh thân khe khác).

const UU_TIEN = { bb: 0, hh: 1, ten: 2, gd: 3, bien: 4 }
const DEM = 4                                  // khoảng hở tối thiểu giữa hai nhãn (px)

function day(tu, den, buoc) { const r = []; for (let v = tu; v <= den; v += buoc) r.push(v); return r }
const MIEN = {
  bb: { dy: day(-140, 0, 4), dx: day(-120, 120, 8), wx: 1.6, wy: 1 },
  hh: { dy: day(-30, 30, 4), dx: day(-10, 40, 5), wx: 1, wy: 1 },
  ten: { dy: day(-30, 60, 3), dx: day(-48, 48, 6), wx: 1.4, wy: 1 },
  gd: { dy: day(-90, 90, 4), dx: day(-120, 120, 8), wx: 1, wy: 1 },
  bien: { dy: day(-170, 170, 4), dx: day(-200, 200, 8), wx: 1, wy: 1 },
}

const giao = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) *
  Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y))

export function boTriNhan(nhan, thanNv, W, H) {
  const daDat = []
  const duongChi = []
  const thuTu = [...nhan].sort((a, b) => UU_TIEN[a.loai] - UU_TIEN[b.loai])
  for (const n of thuTu) {
    const vatCan = [...daDat]
    for (const t of thanNv) if (n.loai === 'bien' || n.loai === 'gd' || t.khe !== n.khe) vatCan.push(t)
    const m = MIEN[n.loai]
    const ung = []
    for (const dy of m.dy) for (const dx of m.dx) ung.push([Math.abs(dx) * m.wx + Math.abs(dy) * m.wy, dx, dy])
    ung.sort((a, b) => a[0] - b[0])
    let tot = null
    let totPhat = Infinity
    for (const [gia, dx, dy] of ung) {
      const x = Math.min(Math.max(n.x0 + dx, 2), W - n.w - 2)
      const y = Math.min(Math.max(n.y0 + dy, 2), H - n.h - 2)
      const r = { x: x - DEM / 2, y: y - DEM / 2, w: n.w + DEM, h: n.h + DEM }
      let chong = 0
      for (const v of vatCan) chong += giao(r, v)
      if (chong === 0) { tot = [x, y]; break }
      const phat = chong * 50 + gia
      if (phat < totPhat) { totPhat = phat; tot = [x, y] }
    }
    ;[n.x, n.y] = tot
    daDat.push({ x: n.x - DEM / 2, y: n.y - DEM / 2, w: n.w + DEM, h: n.h + DEM })
    // đường chỉ mảnh khi nhãn bị dời xa chỗ mong muốn
    if (Math.hypot(n.x - n.x0, n.y - n.y0) > 10 && n.diemNeo) {
      const neo = n.diemNeo
      const cx = Math.min(Math.max(neo.x, n.x + 6), n.x + n.w - 6)
      const cy = Math.min(Math.max(neo.y, n.y), n.y + n.h)
      if (Math.hypot(cx - neo.x, cy - neo.y) > 6) duongChi.push([neo.x, neo.y, cx, cy])
    }
  }
  return duongChi
}

export function demChong(nhan) {
  let so = 0
  for (let i = 0; i < nhan.length; i++) for (let j = i + 1; j < nhan.length; j++) {
    if (giao({ x: nhan[i].x, y: nhan[i].y, w: nhan[i].w, h: nhan[i].h }, { x: nhan[j].x, y: nhan[j].y, w: nhan[j].w, h: nhan[j].h }) > 0) so++
  }
  return so
}

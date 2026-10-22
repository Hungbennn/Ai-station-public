import CaiDat from './trang/CaiDat.vue'
import CongViec from './trang/CongViec.vue'
import DoiNgu from './trang/DoiNgu.vue'
import DuAn from './trang/DuAn.vue'
import KyUc from './trang/KyUc.vue'
import PheDuyet from './trang/PheDuyet.vue'
import TongQuan from './trang/TongQuan.vue'
import TuDong from './trang/TuDong.vue'
import Usage from './trang/Usage.vue'

// Trang mở đầu là Tổng quan (D17). Ký ức giữ /nho (link cũ từ máy A, Telegram) và thêm bí danh /ky-uc (D38).
export const tuyen = [
  { path: '/', redirect: '/tong-quan' },
  { path: '/tong-quan', component: TongQuan },
  { path: '/du-an', component: DuAn },
  { path: '/du-an/:ten', component: TuDong },                                  // TM-4: trang Tự động của dự án
  { path: '/van-phong', component: () => import('./trang/VanPhong.vue') },   // lát 2c: nạp lười (three.js)
  { path: '/cong-viec', component: CongViec },
  { path: '/doi-ngu', component: DoiNgu },
  { path: '/nho', alias: '/ky-uc', component: KyUc },
  { path: '/usage', component: Usage },
  { path: '/phe-duyet', component: PheDuyet },
  { path: '/cai-dat', component: CaiDat },
  { path: '/tai-khoan/thiet-bi', component: () => import('./trang/ThietBi.vue') },
  { path: '/:khac(.*)*', redirect: '/tong-quan' },
]

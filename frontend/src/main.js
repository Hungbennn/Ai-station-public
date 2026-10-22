import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import KhungChinh from './KhungChinh.vue'
import './kieu/font-be-vietnam.css'
import './kieu/font-mono.css'
import './kieu/nen.css'
import './kieu/khung.css'
import './kieu/chung.css'
import { tuyen } from './tuyen.js'

// Đổi trang thì cuộn lên đầu như mockup (app.js `window.scrollTo(0, 0)`); chỉ đổi query thì giữ chỗ.
const cuon = (den, tu, daLuu) => daLuu || (den.path === tu.path ? false : { top: 0 })
createApp(KhungChinh).use(createRouter({ history: createWebHashHistory(), routes: tuyen, scrollBehavior: cuon }))
  .mount('#app')

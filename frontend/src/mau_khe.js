// Màu thân / tóc của nhân vật mỗi khe — dùng chung cảnh 3D, Đội ngũ AI, Tổng quan, Usage (mockup du-lieu.js KHE).
// Chọn theo băm FNV-1a của khe_id nên thêm khe mới không làm đổi màu khe cũ. Server không giữ màu (khảo sát §1.1).
export const BANG_MAU = [
  ['#c8623a', '#3a2620'], ['#d39a3c', '#2b2b33'], ['#4f7a99', '#1f2a33'], ['#5f8f5a', '#33261d'],
  ['#6a5bb5', '#1d1b2e'], ['#b8507a', '#2a1f24'], ['#3f8a8a', '#1f2a2a'], ['#a8744a', '#2e2420'],
]

export function fnv1a(s) {
  let h = 0x811c9dc5
  for (const c of String(s)) {
    h ^= c.codePointAt(0)
    h = Math.imul(h, 0x01000193) >>> 0
  }
  return h
}

export function mauKhe(kheId) {
  const [than, toc] = BANG_MAU[fnv1a(kheId) % BANG_MAU.length]
  return { than, toc }
}

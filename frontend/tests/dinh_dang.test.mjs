import assert from 'node:assert/strict'
import { test } from 'node:test'
import { conLai, gioPhut, gioReset, gon, ngayGio, ngayNgan, soDayDu, truocDay, usd } from '../src/dinh_dang.js'

test('số gọn như mockup Usage (D39)', () => {
  assert.equal(gon(4_200_000), '4,20 tr')
  assert.equal(gon(212_345), '212 n')
  assert.equal(gon(1_250_000_000), '1,25 tỷ')
  assert.equal(gon(999), '999')
  assert.equal(gon(null), '—')
  assert.equal(soDayDu(4200000), (4200000).toLocaleString('vi-VN'))
  assert.equal(usd(3.1), '$3.10')
  assert.equal(usd(0.4213), '$0.4213')
  assert.equal(usd(null), 'chưa có giá')
})

test('giờ theo Asia/Ho_Chi_Minh', () => {
  assert.equal(gioPhut('2026-10-15T15:14:00Z'), '22:14')
  assert.equal(gioPhut('2026-10-15T17:05:00Z'), '00:05')
  assert.equal(ngayGio('2026-10-15T13:58:00Z'), '15/10 20:58')
  assert.equal(ngayNgan('2026-10-02'), '02/10')
  assert.equal(gioPhut(null), '')
  assert.equal(gioPhut('rác'), '')
})

test('trước đây, còn lại, giờ reset', () => {
  const bay = '2026-10-15T15:17:00Z'
  assert.equal(truocDay('2026-10-15T15:16:54Z', bay), '6 giây trước')
  assert.equal(truocDay('2026-10-15T15:14:00Z', bay), '3 phút trước')
  assert.equal(truocDay('2026-10-13T15:14:00Z', bay), '2 ngày trước')
  assert.equal(truocDay('2026-10-16T00:00:00Z', bay), '')
  assert.equal(conLai('2026-10-15T17:12:00Z', bay), 'còn 2 giờ')
  assert.equal(conLai('2026-10-15T15:30:00Z', bay), 'còn 13 phút')
  assert.equal(conLai('2026-10-15T15:00:00Z', bay), '')
  assert.equal(gioReset('2026-10-15T16:40:00Z', bay), '23:40')
  assert.equal(gioReset('2026-10-19T00:00:00Z', bay), 'T2 07:00')
  assert.equal(gioReset(null, bay), '—')
})

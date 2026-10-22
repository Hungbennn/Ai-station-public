import { reactive } from 'vue'
export const quyenPasskey = reactive({ tt: null })
export function capNhat(tt) { quyenPasskey.tt = tt }
export function duocGhi(trangThai) {
  return Boolean(trangThai?.la_dai_ca && quyenPasskey.tt?.thiet_bi.length)
}

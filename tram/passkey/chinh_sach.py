"""Danh mục đóng: route mới phải khai mức; TM/TC nối bằng phụ thuộc tường minh."""
import hashlib
import json

TUYEN = {
    '/api/bead/{du_an}/{bead_id}/cot': 'N',
    '/api/bead/{du_an}/{bead_id}/chot': 'P',
    '/api/bead/{du_an}/{bead_id}/thu-lai': 'N',
    '/api/phe-duyet/{du_an}/{bead_id}/duyet': 'P',
    '/api/phe-duyet/{du_an}/{bead_id}/tra-ve': 'N',
    '/api/phe-duyet/{du_an}/{bead_id}/tra-loi': 'P',
    '/api/chu/estop': 'N',
    '/api/chu/tiep-tuc': 'P',
    '/api/khe/{may_id}/{ten}/tat': 'N',
    '/api/khe/{may_id}/{ten}/bat': 'P',
    '/api/khe/{may_id}/{ten}/cau-dao-dong': 'P',
    '/api/nho/xoa': 'P',
    '/api/nho/ghi': 'N',
    '/api/feature/yeu-cau/xem': 'N',
    '/api/feature/yeu-cau': 'N',
    '/api/dieu-phoi/nhip': 'M',
    '/api/ghep-may': 'M',
    '/api/tho/dang-ky': 'M',
    '/api/tho/nhip': 'M',
    '/api/tho/bao': 'M',
    '/api/tho/su-kien': 'M',
    '/api/tho/da-push': 'M',
    '/api/tho/da-dong': 'M',
}

TUYEN_TM_TC = {
    '/api/du-an/{ten}/tu-dong/cai-dat': 'P/R',
    '/api/du-an/{ten}/tu-dong/tam-dung': 'N',
    '/api/du-an/{ten}/tu-dong/tiep-tuc': 'P',
    '/api/tu-dong/tam-dung': 'N',
    '/api/tu-dong/tiep-tuc': 'P',
    '/api/du-an/{ten}/tu-dong/deploy': 'P',
    '/api/du-an/{ten}/tu-cap-nhat': 'P',
}


def rang_buoc(path, than):
    if not isinstance(than, dict) or not isinstance(than.get('ma_thao_tac'), str) or not than['ma_thao_tac']:
        raise ValueError('Thiếu mã thao tác')
    noi_dung = json.dumps(['POST', path, than], sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(noi_dung.encode()).hexdigest()

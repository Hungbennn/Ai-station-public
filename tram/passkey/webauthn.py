"""Adapter py_webauthn 3.0.1; lỗi không mang dữ liệu ceremony."""
import json
from webauthn import (generate_registration_options, generate_authentication_options,
                      verify_registration_response, verify_authentication_response, options_to_json)
from webauthn.helpers.structs import (AuthenticatorSelectionCriteria, PublicKeyCredentialDescriptor,
                                     UserVerificationRequirement)


class TuChoi(ValueError):
    pass


def tuy_chon(rp, login, nguoi, challenge, ids, tao):
    chung = dict(rp_id=rp, challenge=challenge, timeout=120000)
    ds = [PublicKeyCredentialDescriptor(id=i) for i in ids]
    if tao:
        opt = generate_registration_options(**chung, rp_name='Trạm', user_name=login, user_id=nguoi,
            exclude_credentials=ds, authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED))
    else:
        opt = generate_authentication_options(**chung, allow_credentials=ds,
                                             user_verification=UserVerificationRequirement.REQUIRED)
    return json.loads(options_to_json(opt))


def dang_ky(credential, challenge, rp):
    try:
        return verify_registration_response(credential=credential, expected_challenge=challenge,
            expected_rp_id=rp, expected_origin=f'https://{rp}', require_user_presence=True,
            require_user_verification=True)
    except Exception:
        raise TuChoi('Chưa xác nhận — thử lại') from None


def dang_nhap(credential, challenge, rp, public_key, dem):
    try:
        return verify_authentication_response(credential=credential, expected_challenge=challenge,
            expected_rp_id=rp, expected_origin=f'https://{rp}', credential_public_key=public_key,
            credential_current_sign_count=dem, require_user_verification=True)
    except Exception:
        raise TuChoi('Chưa xác nhận — thử lại') from None

"""Authenticator offline: private key chỉ nằm trong test, chữ ký ES256 thật."""
import hashlib
import json
import os

import cbor2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from webauthn.helpers import bytes_to_base64url as b64


class KhoaGia:
    def __init__(self):
        self.khoa = ec.generate_private_key(ec.SECP256R1())
        self.id = os.urandom(32)

    def tra(self, challenge, *, dang_ky=False, rp='b.test', origin='https://b.test', uv=True, up=True, dem=0):
        client = json.dumps({'type': 'webauthn.create' if dang_ky else 'webauthn.get',
                             'challenge': b64(challenge), 'origin': origin}).encode()
        auth = hashlib.sha256(rp.encode()).digest() + bytes([(1 if up else 0) | (4 if uv else 0) | (64 if dang_ky else 0)])
        auth += dem.to_bytes(4, 'big')
        if dang_ky:
            pub = self.khoa.public_key().public_numbers()
            cose = cbor2.dumps({1: 2, 3: -7, -1: 1, -2: pub.x.to_bytes(32, 'big'), -3: pub.y.to_bytes(32, 'big')})
            auth += bytes(16) + len(self.id).to_bytes(2, 'big') + self.id + cose
            # packed self-attestation có chữ ký thật, không chứng thư/thiết bị thật.
            sig = self.khoa.sign(auth + hashlib.sha256(client).digest(), ec.ECDSA(hashes.SHA256()))
            response = {'attestationObject': b64(cbor2.dumps(
                {'fmt': 'packed', 'authData': auth, 'attStmt': {'alg': -7, 'sig': sig}}))}
        else:
            sig = self.khoa.sign(auth + hashlib.sha256(client).digest(), ec.ECDSA(hashes.SHA256()))
            response = {'authenticatorData': b64(auth), 'signature': b64(sig), 'userHandle': None}
        return {'id': b64(self.id), 'rawId': b64(self.id), 'type': 'public-key',
                'response': {**response, 'clientDataJSON': b64(client)}}

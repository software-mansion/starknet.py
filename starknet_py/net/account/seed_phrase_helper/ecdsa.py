try:
    import starknet_py.net.account.seed_phrase_helper.ecdsa_openssl as _ecdsa
except:
    import starknet_py.net.account.seed_phrase_helper.ecdsa_python as _ecdsa

ECPointAffine = _ecdsa.ECPointAffine
EllipticCurve = _ecdsa.EllipticCurve
secp256k1 = _ecdsa.secp256k1
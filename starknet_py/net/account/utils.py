import hashlib

def arrayify(hexStringOrBigNumberOrArrayish):
    """ Returns array with Uint8 from int or hexadecimal number
    Args:
        hexStringOrBigNumberOrArrayish (str or int); example1: "123423"; example2: "0xffff"
    Returns:
        Uint8 array; example1: [1, 226, 31]; example2: [255, 255]
    """
    try:
        value = int(hexStringOrBigNumberOrArrayish)
    except:
        value = int(hexStringOrBigNumberOrArrayish, 16)
    if value == 0:
        return [0]
    
    hex_v = hex(value)[2::]

    if len(hex_v) % 2 != 0:
        hex_v = "0" + hex_v
    
    result = []

    for i in range(int(len(hex_v)/2)):
        offset = i*2
        result.append(int(hex_v[offset:offset+2], 16))
    
    return result

def concat(a: list, b: list):
    """concatenates two lists:
    example:
        concat([1, 2, 3], [4, 5, 6]) --> [1, 2, 3, 4, 5, 6]
    """
    return a + b

def get_payload_hash(payload: list):
    """returns sha256 hash of given Uint8 list
    Args:
        payload (list (Uint8))
    Returns
        hash (str)
    """
    m = hashlib.sha256()

    for value in payload:
        hex_value = hex(value)[2::]
        if len(hex_value) == 1:
            hex_value = "0"+ hex_value
        m.update(bytes.fromhex(hex_value))
    
    return m.hexdigest()

def hash_key_with_index(key, index):
    """Computes sha256 hash from given key and index
    Args:
        key (int / hex)
        index (int)
    Returns:
        hash (int)
    """
    payload = concat(arrayify(key), arrayify(index))

    payload_hash = get_payload_hash(payload)
    return(int(payload_hash, 16))

def grid_key(key_seed):
    """Compute Argent X private key from key_seed
    Args:
        key_seed (hex)
    Returns:
        argent_x_key (hex)
    """
    keyValueLimit = 0x800000000000010ffffffffffffffffb781126dcae7b2321e66a241adc64d2f
    sha256EcMaxDigest = 0x10000000000000000000000000000000000000000000000000000000000000000

    maxAllowedVal = sha256EcMaxDigest - (sha256EcMaxDigest % keyValueLimit)

    i = 0

    key = 0

    while True:
        key = hash_key_with_index(key_seed, i)
        i+=1
        if key <= maxAllowedVal:
            break
    
    res = hex(abs(key % keyValueLimit))
    return res 

def EIP2645Hashing(key0):
    """EIP-2645 hashing from key0 to braavos private key
    Args:
        key0 (hex)
    returns
        braavos_key (hex)
    """
    N = 2**256

    starkCurveOrder = 0x800000000000010FFFFFFFFFFFFFFFFB781126DCAE7B2321E66A241ADC64D2F

    N_minus_n = N - (N % starkCurveOrder)

    i = 0
    while True:
        x = concat(arrayify(key0), arrayify(i))

        key = int(get_payload_hash(x), 16)

        if key < N_minus_n:
            return hex(key % starkCurveOrder)


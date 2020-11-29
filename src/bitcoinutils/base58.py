from hashlib import sha256
from typing import Union

# `typing.AnyStr` is not exactly a `Union`...
AnyStr = Union[bytes, str]

BITCOIN_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


# Poor man's cache for character->alphabet position look-up
ALPHABET_INDEX_MAP = {
    BITCOIN_ALPHABET: {char: i for i, char in enumerate(BITCOIN_ALPHABET)},
}


def force_bytes(s: AnyStr) -> bytes:
    return s.encode("ascii") if isinstance(s, str) else s


def b58encode_num(num: int, alphabet: bytes = BITCOIN_ALPHABET) -> bytes:
    res = bytearray()

    x = num
    while x > 0:
        x, r = divmod(x, 58)
        res.append(alphabet[r])

    return bytes(reversed(res))


def b58encode(s: AnyStr, alphabet: bytes = BITCOIN_ALPHABET) -> bytes:
    s = force_bytes(s)
    prefix_len = len(s) - len(s.lstrip(b"\x00"))
    decimal = int.from_bytes(s, byteorder="big")

    return prefix_len * alphabet[0:1] + b58encode_num(decimal, alphabet)


def b58decode(s: AnyStr, alphabet: bytes = BITCOIN_ALPHABET) -> bytes:
    s = force_bytes(s)
    index_map = ALPHABET_INDEX_MAP[alphabet]

    orig_len = len(s)
    s = s.lstrip(alphabet[0:1])
    prefix_len = orig_len - len(s)

    decimal = 0
    for i, j in enumerate(reversed(s)):
        decimal += index_map[j] * (58 ** i)

    length = decimal.bit_length() // 8 + 1
    return prefix_len * b"\x00" + decimal.to_bytes(length, byteorder="big").lstrip(
        b"\x00"
    )


def b58encode_check(s: AnyStr, alphabet: bytes = BITCOIN_ALPHABET) -> bytes:
    s = force_bytes(s)

    digest = sha256(sha256(s).digest()).digest()
    return b58encode(s + digest[:4], alphabet)


def b58decode_check(s: AnyStr, alphabet: bytes = BITCOIN_ALPHABET) -> bytes:
    s = force_bytes(s)

    decoded = b58decode(s, alphabet)
    result, checksum = decoded[:-4], decoded[-4:]
    digest = sha256(sha256(result).digest()).digest()

    if digest[:4] != checksum:
        raise ValueError("Checksums do not match!")

    return result

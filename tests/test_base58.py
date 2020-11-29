from random import choices

import pytest
from hypothesis import example, given
from hypothesis.strategies import binary, integers

from bitcoinutils import base58
from bitcoinutils.base58 import BITCOIN_ALPHABET


def random_string_from_alphabet(k: int, alphabet: bytes = BITCOIN_ALPHABET) -> bytes:
    return b"".join(chr(c).encode("ascii") for c in choices(alphabet, k=k))


@given(binary(min_size=0, max_size=256))
@example(b"")
@example(b"\x00")
def test_b58encode_decode_is_invariant(s):
    assert s == base58.b58decode(base58.b58encode(s))


def test_b58encode_utf8_encode_throws_exc():
    with pytest.raises(ValueError):
        base58.b58encode("č")


@given(binary(min_size=0, max_size=256), integers(min_value=0, max_value=64))
@example(b"", 0)
def test_b58encode_leading_zeroes_convert_to_ones(s, i):
    prefixed = i * b"\x00" + s
    assert base58.b58encode(prefixed) == i * b"1" + base58.b58encode(s)


@given(integers(min_value=0, max_value=2048))
@example(0)
def test_b58decode_encode_is_invariant(i):
    encoded = random_string_from_alphabet(i)
    assert encoded == base58.b58encode(base58.b58decode(encoded))


@given(binary(min_size=0, max_size=256))
@example(b"")
@example(b"\x00")
def test_b58encode_check_decode_is_invariant(s):
    assert s == base58.b58decode_check(base58.b58encode_check(s))


@given(binary(min_size=0, max_size=256))
def test_b58encode_check_fails_with_fake_checksum(s):
    without_checksum = base58.b58encode_check(s)[-4:]
    fake_checksum = random_string_from_alphabet(4)
    with pytest.raises(ValueError):
        base58.b58decode_check(without_checksum + fake_checksum)

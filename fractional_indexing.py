# fractional_indexing/fractional_indexing.py

from math import floor
from typing import Optional, List

from .exceptions import OrderKeyError
from .utils import BASE_62_DIGITS, validate_order_key
from .handlers import (
    handle_end_key_only_case,
    handle_start_key_only_case,
    handle_both_keys_case,
    handle_generate_n_keys_with_end_none,
    handle_generate_n_keys_with_start_none
)


def generate_key_between(start_key: Optional[str], end_key: Optional[str], digits: str = BASE_62_DIGITS) -> str:
    """
    Generate an order key that lies between `start_key` and `end_key`.
    If both are None, returns the first possible key.
    """
    zero = digits[0]

    if start_key is not None:
        validate_order_key(start_key, digits)

    if end_key is not None:
        validate_order_key(end_key, digits)

    if start_key is not None and end_key is not None and start_key >= end_key:
        raise OrderKeyError(f'{start_key} >= {end_key}')

    if start_key is None:
        if end_key is None:
            return 'a' + zero
        return handle_end_key_only_case(end_key, digits)

    if end_key is None:
        return handle_start_key_only_case(start_key, digits)

    return handle_both_keys_case(start_key, end_key, digits)


def generate_n_keys_between(start_key: Optional[str], end_key: Optional[str], number_of_keys: int, digits: str = BASE_62_DIGITS) -> List[str]:
    """
    Generate `number_of_keys` distinct order keys between `start_key` and `end_key`.
    """
    if number_of_keys == 0:
        return []

    if number_of_keys == 1:
        return [generate_key_between(start_key, end_key, digits)]

    if end_key is None:
        return handle_generate_n_keys_with_end_none(start_key, number_of_keys, digits)

    if start_key is None:
        return handle_generate_n_keys_with_start_none(end_key, number_of_keys, digits)

    mid_index = floor(number_of_keys / 2)
    middle_key = generate_key_between(start_key, end_key, digits)

    return [
        *generate_n_keys_between(start_key, middle_key, mid_index, digits),
        middle_key,
        *generate_n_keys_between(middle_key, end_key, number_of_keys - mid_index - 1, digits)
    ]

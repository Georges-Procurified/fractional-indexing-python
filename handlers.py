# fractional_indexing/handlers.py

from typing import Optional, List

from .exceptions import OrderKeyError
from .utils import (
    get_integer_part,
    find_middle_key,
    decrement_integer,
    increment_integer,
    generate_key_between
)


def handle_end_key_only_case(end_key: str, digits: str) -> str:
    """Handle the case when only `end_key` is provided."""
    zero = digits[0]
    integer_part = get_integer_part(end_key)
    fractional_part = end_key[len(integer_part):]
    if integer_part == 'A' + (zero * 26):
        return integer_part + find_middle_key('', fractional_part, digits)
    if integer_part < end_key:
        return integer_part
    decremented = decrement_integer(integer_part, digits)
    if decremented is None:
        raise OrderKeyError('Cannot decrement anymore')
    return decremented


def handle_start_key_only_case(start_key: str, digits: str) -> str:
    """Handle the case when only `start_key` is provided."""
    integer_part = get_integer_part(start_key)
    fractional_part = start_key[len(integer_part):]
    incremented = increment_integer(integer_part, digits)
    return integer_part + find_middle_key(fractional_part, None, digits) if incremented is None else incremented


def handle_both_keys_case(start_key: str, end_key: str, digits: str) -> str:
    """Handle the case when both `start_key` and `end_key` are provided."""
    start_int_part = get_integer_part(start_key)
    start_frac_part = start_key[len(start_int_part):]
    end_int_part = get_integer_part(end_key)
    end_frac_part = end_key[len(end_int_part):]

    if start_int_part == end_int_part:
        return start_int_part + find_middle_key(start_frac_part, end_frac_part, digits)

    incremented = increment_integer(start_int_part, digits)

    if incremented is None:
        raise OrderKeyError('Cannot increment anymore')

    if incremented < end_key:
        return incremented

    return start_int_part + find_middle_key(start_frac_part, None, digits)


def handle_generate_n_keys_with_end_none(start_key: Optional[str], number_of_keys: int, digits: str) -> List[str]:
    """Handle case when generating keys with `end_key` as None."""
    current_key = generate_key_between(start_key, None, digits)
    result = [current_key]
    for _ in range(number_of_keys - 1):
        current_key = generate_key_between(current_key, None, digits)
        result.append(current_key)
    return result


def handle_generate_n_keys_with_start_none(end_key: Optional[str], number_of_keys: int, digits: str) -> List[str]:
    """Handle case when generating keys with `start_key` as None."""
    current_key = generate_key_between(None, end_key, digits)
    result = [current_key]
    for _ in range(number_of_keys - 1):
        current_key = generate_key_between(None, current_key, digits)
        result.append(current_key)
    return list(reversed(result))

"""
Provides functions for generating ordering strings

<https://github.com/httpie/fractional-indexing-python>.

<https://observablehq.com/@dgreensp/implementing-fractional-indexing>

"""
from math import floor
from typing import Optional, List
import decimal

__version__ = '0.1.3'
__licence__ = 'CC0 1.0 Universal'

BASE_62_DIGITS: str = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'


class OrderKeyError(Exception):
    """Custom error for invalid order keys."""
    pass


def round_half_up(value: float) -> int:
    """Round a float to the nearest integer, rounding halves up."""
    return int(
        decimal.Decimal(str(value)).quantize(
            decimal.Decimal('1'),
            rounding=decimal.ROUND_HALF_UP
        )
    )


def validate_integer(order_key: str) -> None:
    """Validate that the length of the integer part of the order key is correct."""
    if len(order_key) != get_integer_length(order_key[0]):
        raise OrderKeyError(f'Invalid integer part of order key: {order_key}')


def get_integer_length(first_char: str) -> int:
    """Return the length of the integer part based on the first character."""
    if 'a' <= first_char <= 'z':
        return ord(first_char) - ord('a') + 2
    elif 'A' <= first_char <= 'Z':
        return ord('Z') - ord(first_char) + 2
    raise OrderKeyError('Invalid order key head: ' + first_char)


def get_integer_part(order_key: str) -> str:
    """Extract the integer part of the order key."""
    integer_part_length = get_integer_length(order_key[0])
    if integer_part_length > len(order_key):
        raise OrderKeyError(f'Invalid order key: {order_key}')
    return order_key[:integer_part_length]


def validate_order_key(order_key: str, digits: str = BASE_62_DIGITS) -> None:
    """Check the validity of an order key."""
    zero = digits[0]
    smallest_valid_key = 'A' + (zero * 26)

    if order_key == smallest_valid_key:
        raise OrderKeyError(f'Invalid order key: {order_key}')

    integer_part = get_integer_part(order_key)
    fractional_part = order_key[len(integer_part):]

    if fractional_part and fractional_part[-1] == zero:
        raise OrderKeyError(f'Invalid order key: {order_key}')


def increment_integer(integer_str: str, digits: str) -> Optional[str]:
    """Increment the integer part of the order key."""
    zero = digits[0]
    validate_integer(integer_str)

    head, *digits_list = integer_str
    has_carry_over = True

    for i in reversed(range(len(digits_list))):
        current_digit = digits.index(digits_list[i]) + 1
        if current_digit == len(digits):
            digits_list[i] = zero
        else:
            digits_list[i] = digits[current_digit]
            has_carry_over = False
            break

    if has_carry_over:
        if head == 'Z':
            return 'a' + zero
        if head == 'z':
            return None
        next_head = chr(ord(head) + 1)
        if next_head > 'a':
            digits_list.append(zero)
        else:
            digits_list.pop()
        return next_head + ''.join(digits_list)

    return head + ''.join(digits_list)


def decrement_integer(integer_str: str, digits: str) -> Optional[str]:
    """Decrement the integer part of the order key."""
    validate_integer(integer_str)

    head, *digits_list = integer_str
    requires_borrow = True

    for i in reversed(range(len(digits_list))):
        current_digit = digits.index(digits_list[i]) - 1

        if current_digit == -1:
            digits_list[i] = digits[-1]
        else:
            digits_list[i] = digits[current_digit]
            requires_borrow = False
            break

    if requires_borrow:
        if head == 'a':
            return 'Z' + digits[-1]
        if head == 'A':
            return None
        next_head = chr(ord(head) - 1)
        if next_head < 'Z':
            digits_list.append(digits[-1])
        else:
            digits_list.pop()
        return next_head + ''.join(digits_list)

    return head + ''.join(digits_list)


def find_middle_key(start_key: str, end_key: Optional[str], digits: str) -> str:
    """
    Calculate the midpoint between two order keys.
    `start_key` must be lexicographically less than `end_key`.
    No trailing zeros allowed in the order key.
    """
    zero = digits[0]

    if end_key is not None and start_key >= end_key:
        raise OrderKeyError(f'{start_key} >= {end_key}')

    if start_key and start_key[-1] == zero or (end_key and end_key[-1] == zero):
        raise OrderKeyError('Trailing zero in order key')

    if end_key:
        common_prefix_len = 0
        for char_start, char_end in zip(start_key.ljust(len(end_key), zero), end_key):
            if char_start == char_end:
                common_prefix_len += 1
                continue
            break

        if common_prefix_len > 0:
            return end_key[:common_prefix_len] + find_middle_key(
                start_key[common_prefix_len:], end_key[common_prefix_len:], digits
            )

    # Different first digits or lack of digit
    digit_a = digits.index(start_key[0]) if start_key else 0
    digit_b = digits.index(end_key[0]) if end_key else len(digits)

    if digit_b - digit_a > 1:
        min_digit = round_half_up(0.5 * (digit_a + digit_b))
        return digits[min_digit]

    if end_key and len(end_key) > 1:
        return end_key[:1]

    return digits[digit_a] + find_middle_key(start_key[1:], None, digits)


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

def generate_n_keys_between(start_key: Optional[str], end_key: Optional[str], number_of_keys: int, digits: str = BASE_62_DIGITS) -> List[str]:
    """
    Generate `n` distinct order keys between `start_key` and `end_key`.
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
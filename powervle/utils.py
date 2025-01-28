def get_bits_from_int(num: int, length: int, start: int, end: int) -> int:
    mask = ~(~0 << (end - start))
    return (num >> (length - end)) & mask


def sign_extend(value: int, width: int) -> int:
    value &= (1 << width) - 1
    if value & (1 << (width - 1)):
        value -= 1 << width
    return value


def mask(value: int, width: int) -> int:
    return value & ((1 << width) - 1)

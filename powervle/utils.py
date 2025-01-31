def get_bits_from_int(num: int, length: int, *args) -> int:
    if type(args[0]) == int:
        start, end = args
        mask = ~(~0 << (end - start))
        return (num >> (length - end)) & mask
    elif type(args[0]) == tuple:
        result = 0
        for bits in args:
            start, end, shift = bits
            result |= get_bits_from_int(num, length, start, end) << shift
        return result
    else:
        raise TypeError


def sign_extend(value: int, width: int) -> int:
    value &= (1 << width) - 1
    if value & (1 << (width - 1)):
        value -= 1 << width
    return value


def mask(value: int, width: int) -> int:
    return value & ((1 << width) - 1)

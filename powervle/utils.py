def get_bits_from_int(num: int, length: int, start: int, end: int) -> int:
    mask = ~(~0 << (end - start))
    return (num >> (length - end)) & mask

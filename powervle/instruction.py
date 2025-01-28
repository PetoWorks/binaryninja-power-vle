from typing import Callable
from .utils import *


def scimm(mode: int, f: int, scl: int, ui8: int) -> int:
    scale = scl * 8
    scimm = ui8 << scale
    if f:
        scimm &= (1 << scale) - 1
        scimm &= ((1 << (56 - scale)) - 1) << (scale + 8)
    return scimm & ((1 << mode) - 1)


class Instruction:
    name: str
    category: str
    length: int
    fields: dict[str, tuple[int, int] | Callable]
    operands: list[str | bytes | int]

    def __init__(self, data: int):
        self.data = (data >> (32 - self.length * 8)) & ((1 << (self.length * 8)) - 1)

    def __getattr__(self, key: str):
        return self.get(key)

    def get(self, name: str) -> int | Callable | None:
        if name not in self.fields:
            return
        field = self.fields[name]
        if type(field) == tuple:
            return get_bits_from_int(self.data, self.length * 8, *field)
        else:
            return field(self)


def Inst(
    name: str,
    category: str,
    length: int,
    fields: dict,
    operands: list[str | bytes | int],
    **other
) -> type[Instruction]:

    for opr in operands:
        if opr not in fields:
            raise ValueError(f"instrucion {name} has invalid operand: {opr}")

    return type(f"Inst_{name}", (Instruction, ), {
        "name": name,
        "category": category,
        "length": length,
        "fields": fields,
        "operands": operands,
        **other
    })


def InstBD8(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 5),
        "BO16": (5, 6),
        "BI16": (6, 8),
        "XO": (6, 7),
        "LK": (7, 8),
        "BD8": (8, 16),
        "NIA": lambda s: lambda x, b: mask(b + sign_extend(s.BD8 << 1, 8), x),
    }, operands)


def InstBD15(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 10),
        "BO32": (10, 12),
        "BI32": (12, 16),
        "BD15": (16, 31),
        "LK": (31, 32),
        "NIA": lambda s: lambda x, b: mask(b + sign_extend(s.BD15 << 1, 15), x),
    }, operands)


def InstBD24(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "BD24": (7, 31),
        "LK": (31, 32),
        "NIA": lambda s: lambda x, b: mask(b + sign_extend(s.BD24 << 1, 24), x),
    }, operands)


def InstC(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 16),
        "LK": (15, 16),
    }, operands)


def InstIM5(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 6),
        "XO": (6, 7),
        "UI5": (7, 12),
        "RX": (12, 16),
    }, operands)


def InstOIM5(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 6),
        "XO": (6, 7),
        "OIM5": (7, 12),
        "RX": (12, 16),
        "OIMM": lambda s: s.OIM5 + 1
    }, operands)


def InstIM7(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 5),
        "UI7": (5, 12),
        "RX": (12, 16),
    }, operands)


def InstR(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 6),
        "XO": (6, 12),
        "RX": (12, 16),
    }, operands)


def InstRR(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 6),
        "XO": (6, 8),
        "Rc": (7, 8),
        "RY": (8, 12),
        "ARY": (8, 12),
        "RX": (12, 16),
        "ARX": (12, 16),
    }, operands)


def InstSD4(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 4),
        "SD4": (4, 8),
        "RZ": (8, 12),
        "RX": (12, 16),
        "SD4-sext": lambda s: sign_extend(s.SD4, 4)
    }, operands)


def InstD(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "RS": (6, 11),
        "TO": (6, 11),
        "FRT": (6, 11),
        "FRS": (6, 11),
        "BF": (6, 8),
        "L": (10, 11),
        "RA": (11, 16),
        "D": (16, 32),
        "SI": (16, 32),
        "UI": (16, 32),
        "SI-sext": lambda s: sign_extend(s.SI, 16),
        "D-sext": lambda s: sign_extend(s.D, 16),
    }, operands)


def InstD8(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "RS": (6, 11),
        "RA": (11, 16),
        "XO": (16, 24),
        "D8": (24, 32),
        "D8-sext": lambda s: sign_extend(s.D8, 8)
    }, operands)


def InstI16A(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "SI_6": (6, 11),
        "UI_6": (6, 11),
        "RA": (11, 16),
        "XO": (16, 21),
        "SI_21": (21, 32),
        "UI_21": (21, 32),
        "SI": lambda s: (s.SI_6 << 11) | s.SI_21,
        "UI": lambda s: (s.UI_6 << 11) | s.UI_21,
        "SI-sext": lambda s: sign_extend(s.SI, 16)
    }, operands)


def InstI16L(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "UI_11": (11, 16),
        "XO": (16, 21),
        "UI_21": (21, 32),
        "UI": lambda s: (s.UI_11 << 11) | s.UI_21,
    }, operands)


def InstM(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RS": (6, 11),
        "RA": (11, 16),
        "RB": (16, 21),
        "SH": (16, 21),
        "MB": (21, 26),
        "ME": (26, 31),
        "Rc": (31, 32),
        "XO": (31, 32)
    }, operands)


def InstSCI8(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "RS": (6, 11),
        "XO": (6, 11),
        "BF32": (9, 11),
        "RA": (11, 16),
        "XO_16_20": (16, 20),
        "XO_16_21": (16, 21),
        "Rc": (20, 21),
        "F": (21, 22),
        "SCL": (22, 24),
        "UI8": (24, 32),
        "SCIMM": lambda s: lambda b: scimm(b, s.F, s.SCL, s.UI8)
    }, operands)


def InstLI20(name: str, category: str, operands: list[str | bytes | int]) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "LI20_11": (11, 16),
        "XO": (16, 17),
        "LI20_17": (17, 21),
        "LI20_21": (21, 32),
        "LI20": lambda s: (s.LI20_17 << 16) | (s.LI20_11 << 11) | s.LI20_21,
        "LI20-sext": lambda s: sign_extend(s.LI20, 20)
    }, operands)

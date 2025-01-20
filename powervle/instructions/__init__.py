'''
Instruction base classes
'''

from binaryninja.architecture import InstructionInfo
from binaryninja.function import InstructionTextToken, InstructionTextTokenType
from binaryninja.lowlevelil import LowLevelILFunction


def _bits(num: int, length: int, start: int, end: int) -> int:
    mask = ~(~0 << (end - start))
    return (num >> (length - end)) & mask


class Instruction:
    name: str
    category: str
    fields: dict[str, tuple[int]]
    uses: tuple[str]
    length: int = 4

    @classmethod
    def fetch_fields(cls, data: int) -> dict[str, int]:
        return {field_name: _bits(data, 32, *cls.fields[field_name]) for field_name in cls.uses}

    @classmethod
    def get_instruction_info(cls, fields: dict[str, int], addr: int) -> InstructionInfo:
        return InstructionInfo(length=cls.length)

    @classmethod
    def get_instruction_text(cls, fields: dict[str, int], addr: int) -> tuple[list[InstructionTextToken], int]:
        return [InstructionTextToken(InstructionTextTokenType.TextToken, cls.name)], cls.length

    @classmethod
    def get_instruction_low_level_il(cls, fields: dict[str, int], addr: int, il: LowLevelILFunction) -> int:
        il.append(il.unimplemented())
        return cls.length


def InstTemp(name: str = "unknown", category: str = "UNK", length: int = 4) -> type[Instruction]:
    return type(f"InstTemp_{name}", (Instruction, ), {"name": name, "category": category, "length": length})


'''
VLE Instruction Formats
'''


class FormatBD8(Instruction):
    fields = {
        "BO16": (5, 6),
        "BI16": (6, 8),
        "BD8": (8, 16),
        "XO": (6, 7),
        "LK": (7, 8)
    }


class FormatC(Instruction):
    fields = {
        "LK": (15, 16)
    }


class FormatIM5(Instruction):
    fields = {
        "XO": (6, 7),
        "UI5": (7, 12),
        "RX": (12, 16),
    }


class FormatOIM5(Instruction):
    fields = {
        "XO": (6, 7),
        "OIM5": (7, 12),
        "RS": (12, 16)
    }


class FormatIM7(Instruction):
    fields = {
        "UI7": (5, 12),
        "RX": (12, 16)
    }


class FormatR(Instruction):
    fields = {
        "XO": (6, 12),
        "RX": (12, 16)
    }


class FormatRR(Instruction):
    fields = {
        "XO_6_8": (6, 8),
        "XO_6_7": (6, 7),
        "RC": (7, 8),
        "RY": (8, 12),
        "ARY": (8, 12),
        "RX": (12, 16),
        "ARX": (12, 16)
    }


class FormatSD4(Instruction):
    fields = {
        "SD4": (4, 8),
        "RZ": (8, 12),
        "RX": (12, 16)
    }


class FormatBD15(Instruction):
    fields = {
        "BO32": (10, 12),
        "BI32": (12, 16),
        "BD15": (16, 31),
        "LK": (31, 32)
    }


class FormatBD24(Instruction):
    fields = {
        "BD24": (7, 31),
        "LK": (31, 32)
    }


class FormatD8(Instruction):
    fields = {
        "RT": (6, 11),
        "RS": (6, 11),
        "RA": (11, 16),
        "XO": (16, 24),
        "D8": (24, 32)
    }


class FormatI16A(Instruction):
    fields = {
        "SI_6": (6, 11),
        "UI_6": (6, 11),
        "RA": (11, 16),
        "XO": (16, 21),
        "SI_21": (21, 32),
        "UI_21": (21, 32)
    }


class FormatI16L(Instruction):
    fields = {
        "RT": (6, 11),
        "UI_11": (11, 16),
        "XO": (16, 21),
        "UI_21": (21, 32)
    }


class FormatM(Instruction):
    fields = {
        "RS": (6, 11),
        "RA": (11, 16),
        "RB": (16, 21),
        "SH": (16, 21),
        "MB": (21, 26),
        "ME": (26, 31),
        "Rc": (31, 32),
        "XO": (31, 32)
    }


class FormatSCI8(Instruction):
    fields = {
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
        "UI8": (24, 32)
    }


class FormatLI20(Instruction):
    fields = {
        "RT": (6, 11),
        "LI20_11": (11, 16),
        "XO": (16, 17),
        "LI20_17": (17, 21),
        "LI20_21": (21, 32)
    }


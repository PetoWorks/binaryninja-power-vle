from typing import Any
from abc import ABC, abstractmethod
from functools import cache, cached_property
from enum import Enum


def _bits(num: int, start: int, end: int) -> int:
    mask = ~(~0 << (end - start))
    return (num >> start) & mask


class Instruction(ABC):
    fields: dict[str, tuple[int]]
    opcode: int

    def __init__(self, data: int):
        assert self.opcode == self.fetch_opcode(data)
        self._raw = data
    
    @cached_property
    def raw(self) -> int:
        return self._raw
    
    @cache
    def bits(self, start: int, end: int) -> int:
        return _bits(self.raw, start, end)

    @cache
    def get_field(self, name: str) -> int:
        bitrange = self.fields[name]
        if not bitrange:
            raise ValueError(f"Field {name} variadic")
        return self.bits(*bitrange)
    
    @abstractmethod
    def get_instruction_info(self, *_, **__) -> ...:
        ...

    @abstractmethod
    def get_instruction_text(self, *_, **__) -> ...:
        ...

    @abstractmethod
    def get_instruction_low_level_il(self, *_, **__) -> ...:
        ...


class FormatI(Instruction):
    fields = {
        "LI": (6, 30),
        "AA": (30, 31),
        "LK": (31, 32)
    }


class FormatB(Instruction):
    fields = {
        "BO": (6, 11),
        "BI": (11, 16),
        "BD": (16, 30),
        "AA": (30, 31),
        "LK": (31, 32)
    }


class FormatSC(Instruction):
    fields = {
        "LEV": (20, 27),
    }

    def __init__(self, data):
        super().__init__(data)
        assert self.bits(30, 31) == 1


class FormatD(Instruction):
    fields = {
        "RT": (6, 11),
        "RS": (6, 11),
        "TO": (6, 11),
        "FRS": (6, 11),
        "FRT": (6, 11),
        "BF": (6, 9),
        "L": (10, 11),
        "RA": (11, 16),
        "D": (16, 32),
        "SI": (16, 32),
        "UI": (16, 32)
    }


class FormatDS(Instruction):
    fields = {
        "RT": (6, 11),
        "RS": (6, 11),
        "RA": (11, 16),
        "DS": (16, 30),
        "XO": (30, 32)
    }


class FormatX(Instruction):
    fields = {
        "RT": (6, 11),
        "RS": (6, 11),
        "TO": (6, 11),
        "FRT": (6, 11),
        "FRS": (6, 11),
        "BT": (6, 11),
        "VRT": (6, 11),
        "VRS": (6, 11),
        "MO": (6, 11),
        "BF": (6, 9),
        "L": None,
        "TH": (7, 11),
        "CT": (7, 11),
        "RA": (11, 16),
        "FRA": (11, 16),
        "SR": (12, 16),
        "BFA": (11, 14),
        "RB": (16, 21),
        "NB": (16, 21),
        "SH": (16, 21),
        "FRB": (16, 21),
        "U": (16, 20),
        "E": (16, 17),
        "XO": (21, 31),
        "Rc": (31, 32)
    }


class FormatXL(Instruction):
    fields = {
        "BT": (6, 11),
        "BO": (6, 11),
        "BF": (6, 9),
        "BA": (11, 16),
        "BI": (11, 16),
        "BFA": (11, 14),
        "BB": (16, 21),
        "BH": (19, 21),
        "XO": (21, 31),
        "LK": (31, 32)
    }


class FormatXFX(Instruction):
    fields = {
        "RT": (6, 11),
        "DUI": (6, 11),
        "RS": (6, 11),
        "SPR": (11, 21),
        "TBR": (11, 21),
        "FXM": (12, 20),
        "DCR": (11, 21),
        "DCS": (11, 21),
        "DUIS": (11, 21),
        "XO": (31, 32)
    }


class FormatXFL(Instruction):
    fields = {
        "FLM": (7, 15),
        "FRB": (16, 21),
        "XO": (21, 31),
        "Rc": (31, 32)
    }


class FormatXS(Instruction):
    fields = {
        "RS": (6, 11),
        "RA": (11, 16),
        "SH": (16, 21),
        "XO": (21, 30),
        "SH30": (30, 31),
        "Rc": (31, 32)
    }


class FormatXO(Instruction):
    fields = {
        "RT": (6, 11),
        "RA": (11, 16),
        "RB": (16, 21),
        "OE": (21, 22),
        "XO": (22, 31),
        "Rc": (31, 32)
    }


class FormatA(Instruction):
    fields = {
        "FRT": (6, 11),
        "RT": (6, 11),
        "FRA": (11, 16),
        "RA": (11, 16),
        "FRB": (16, 21),
        "RB": (16, 21),
        "FRC": (21, 26),
        "BC": (21, 26),
        "XO": (26, 31),
        "Rc": (31, 32)
    }


class FormatM(Instruction):
    fields = {
        "RS": (6, 11),
        "RA": (11, 16),
        "RB": (16, 21),
        "SH": (16, 21),
        "MB": (21, 26),
        "ME": (26, 31),
        "Rc": (31, 32)
    }


class FormatMD(Instruction):
    fields = {
        "RS": (6, 11),
        "RA": (11, 16),
        "SH": (16, 21),
        "MB": (21, 27),
        "ME": (21, 27),
        "XO": (27, 30),
        "SH30": (30, 31),
        "Rc": (31, 32)
    }


class FormatMDS(Instruction):
    fields = {
        "RS": (6, 11),
        "RA": (11, 16),
        "SH": (16, 21),
        "MB": (21, 27),
        "ME": (21, 27),
        "XO": (27, 31),
        "Rc": (31, 32)
    }


class FormatVA(Instruction):
    fields = {
        "VRT": (6, 11),
        "VRA": (11, 16),
        "VRB": (16, 21),
        "VRC": (21, 26),
        "SHB": (22, 26),
        "XO": (27, 32),
    }


class FormatVC(Instruction):
    fields = {
        "VRT": (6, 11),
        "VRA": (11, 16),
        "VRB": (16, 21),
        "Rc": (21, 22),
        "XO": (22, 32)
    }


class FormatVX(Instruction):
    fields = {
        "VRT": (6, 11),
        "VRA": (11, 16),
        "SIM": (11, 16),
        "UIM": None,
        "VRB": (16, 21),
        "XO": (21, 32)
    }


class FormatEVX(Instruction):
    fields = {
        "RS": (6, 11),
        "RT": (6, 11),
        "BF": (6, 9),
        "RA": (11, 16),
        "UI": None,
        "SI": (11, 16),
        "RB": (16, 21),
        "XO": (21, 32),
    }


class FormatEVS(Instruction):
    fields = {
        "RT": (6, 11),
        "RA": (11, 16),
        "RB": (16, 21),
        "XO": (21, 29),
        "BFA": (29, 32)
    }
from .utils import *


def scimm(f: int, scl: int, ui8: int) -> int:
    scale = scl * 8
    scimm = ui8 << scale
    if f:
        scimm &= (1 << scale) - 1
        scimm &= ((1 << (56 - scale)) - 1) << (scale + 8)
    return scimm


class Instruction:
    name: str
    category: str
    length: int
    fields: dict[str, tuple[int, int]]
    operands: list[str]
    branch: bool = False
    conditional_branch: bool = False

    _bcmap = (
        ("ge", "le", "ne", "ns", "dnz"),
        ("lt", "gt", "eq", "so", "dz"),
    )

    def __init__(self, data: int, addr: int, x64: bool = False):
        self.data = (data >> (32 - self.length * 8)) & ((1 << (self.length * 8)) - 1)
        self.addr = addr
        self.x64 = x64

    def get_field_value(self, name: str) -> int | None:
        if (field := self.fields.get(name, None)) != None:
            return get_bits_from_int(self.data, self.length * 8, *field)

    def get_operand_value(self, name: str) -> int | str | None:
        if name in self.operands:
            if (value := self.get_field_value(name)) == None:
                return self.get_extended_operand_value(name)
            if name in ("RA", "RB", "RT", "RS"):
                return f"r{value}"
            elif name in ("RX", "RY", "RZ"):
                regnum = value & 0b111
                if value & 0b1000:
                    regnum += 24
                return f"r{regnum}"
            elif name in ("ARX", "ARY"):
                return f"r{8 + value}"
            elif name == "BT": # TODO: CR or FPSCR
                return f"cr{value >> 2}" # in "VLE"
            elif name in ("BF", "BFA"): # TODO: CR or FPSCR
                return f"cr{value}" # in "VLE"
            elif name in ("BA", "BB"):
                return f"cr{value >> 2}"
            elif name == "BF32":
                return f"cr{value}"
            elif name == "BI32":
                return f"cr{value >> 2}"
            elif name == "BI16":
                return f"cr0"
            elif name == "SD4":
                opcd = self.get_field_value("OPCD")
                if opcd == 8: # se_lbz
                    return value
                elif opcd == 9: # se_stb
                    return sign_extend(value, 4)
                elif opcd == 10: # se_lhz
                    return value << 1
                elif opcd == 11: # se_sth
                    return value << 1
                elif opcd == 12: # se_lwz
                    return value << 2
                elif opcd == 13: # se_stw
                    return value << 2
                return value
            elif name == "D8":
                return sign_extend(value, 8)
            elif name in ("SI", "D"):
                return sign_extend(value, 16)
            else:
                return value
    
    def get_extended_operand_value(self, name: str) -> int | str | None:
        if name == "target_addr":
            if (bd8 := self.get_field_value("BD8")) != None:
                offset = sign_extend(bd8 << 1, 9)
            elif (bd15 := self.get_field_value("BD15")) != None:
                offset = sign_extend(bd15 << 1, 16)
            elif (bd24 := self.get_field_value("BD24")) != None:
                offset = sign_extend(bd24 << 1, 25)
            else:
                return None
            return mask(self.addr + offset, 64 if self.x64 else 32)
        elif name == "oimm":
            return self.get_field_value("OIM5") + 1
        elif name == "sci8":
            F = self.get_field_value("F")
            SCL = self.get_field_value("SCL")
            UI8 = self.get_field_value("UI8")
            if None not in (F, SCL, UI8):
                return scimm(F, SCL, UI8)
        elif name == "LI20":
            li20 = self.get_field_value("li20")
            if li20 != None:
                return sign_extend(li20, 20)

    @property
    def mnemonic(self) -> str:
        ext, mnemonic = self.name.split("_") if self.name.find("_") != -1 else [None, self.name]
        if self.conditional_branch:
            mnemonic = mnemonic[:-1] + self.branch_condition
        if "LK" in self.operands:
            mnemonic += "l" if self.get_operand_value("LK") == 1 else ""
        if "Rc" in self.operands:
            mnemonic += "." if self.get_operand_value("Rc") == 1 else ""
        return mnemonic

    @property
    def branch_condition(self) -> str | None:
        if self.conditional_branch:
            if ((bo32 := self.get_field_value("BO32")) != None and 
                (bi32 := self.get_field_value("BI32")) != None):
                return self._bcmap[bo32 & 1][bi32 % 4 + ((bo32 & 2) << 1)]
            elif ((bo16 := self.get_field_value("BO16")) != None and
                  (bi16 := self.get_field_value("BI16")) != None):
                return self._bcmap[bo16][bi16]

    @property
    def branch_condition_index(self) -> int | None:
        if self.conditional_branch:
            ret = self.get_field_value("BI32")
            if ret == None:
                ret = self.get_field_value("BI16")
            return ret >> 2


def Inst(
    name: str,
    category: str,
    length: int,
    fields: dict,
    operands: list[str | bytes | int],
    **other
) -> type[Instruction]:

    return type(f"Inst_{name}", (Instruction, ), {
        "name": name,
        "category": category,
        "length": length,
        "fields": fields,
        "operands": operands,
        **other
    })


def InstBD8(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 5),
        "BO16": (5, 6),
        "BI16": (6, 8),
        "XO": (6, 7),
        "LK": (7, 8),
        "BD8": (8, 16),
    }, operands, **other)


def InstBD15(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 10),
        "BO32": (10, 12),
        "BI32": (12, 16),
        "BD15": (16, 31),
        "LK": (31, 32),
    }, operands, **other)


def InstBD24(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "BD24": (7, 31),
        "LK": (31, 32),
    }, operands, **other)


def InstC(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 16),
        "LK": (15, 16),
    }, operands, **other)


def InstIM5(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 6),
        "XO": (6, 7),
        "UI5": (7, 12),
        "RX": (12, 16),
    }, operands, **other)


def InstOIM5(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 6),
        "XO": (6, 7),
        "Rc": (6, 7),
        "OIM5": (7, 12),
        "RX": (12, 16),
    }, operands, **other)


def InstIM7(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 5),
        "UI7": (5, 12),
        "RX": (12, 16),
    }, operands, **other)


def InstR(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 6),
        "XO": (6, 12),
        "RX": (12, 16),
    }, operands, **other)


def InstRR(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 6),
        "XO": (6, 8),
        "Rc": (7, 8),
        "RY": (8, 12),
        "ARY": (8, 12),
        "RX": (12, 16),
        "ARX": (12, 16),
    }, operands, **other)


def InstSD4(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 2, {
        "OPCD": (0, 4),
        "SD4": (4, 8),
        "RZ": (8, 12),
        "RX": (12, 16),
    }, operands, **other)


def InstD(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
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
    }, operands, **other)


def InstD8(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "RS": (6, 11),
        "RA": (11, 16),
        "XO": (16, 24),
        "D8": (24, 32),
    }, operands, **other)


def InstI16A(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RA": (11, 16),
        "XO": (16, 21),
        "SI": ((6, 11, 11), (21, 32, 0)),
        "UI": ((6, 11, 11), (21, 32, 0)),
    }, operands, **other)


def InstI16L(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "XO": (16, 21),
        "UI": ((11, 16, 11), (21, 32, 0))
    }, operands, **other)


def InstM(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
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
    }, operands, **other)


def InstSCI8(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
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
    }, operands, **other)


def InstLI20(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "XO": (16, 17),
        "li20": ((17, 21, 16), (11, 16, 11), (21, 32, 0))
    }, operands, **other)

def InstX(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT" : (6, 11),
        "RA" : (11, 16),
        "RB" : (16, 21),
        "XO" : (21, 31),
        "NB" : (16, 21),
        "SR" : (12, 16),  
        "RS" : (6, 11),
        "Rc" : (31, 32),
        "SH" : (16, 21),
        "L" : (15, 16),
        #"L" : (10, 11),
        #"L" : (9, 11),
        "BF" : (6, 9),
        "FRA" : (11, 16),
        "FRB" : (16, 21),
        "BFA" : (11, 14),
        "U" : (16, 20),
        "TH" : (7, 11),
        "CT" : (7, 11),
        "TO" : (6, 11),
        "FRT" : (6, 11)
    }, operands, **other)

# EVX-Form
def InstEVX(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RS": (6, 11),
        "RT": (6, 11),
        "BF": (6, 9),
        "RA": (11, 16),
        "SI": (11, 16),
        "UI_11_16": (11, 16),
        "RB": (16, 21),
        "UI_16_21": (16, 21),
        "XO": (21, 32),
    }, operands, **other)

# EVS-Form
def InstEVS(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "RA": (11, 16),
        "RB": (16, 21),
        "XO": (21, 29),
        "BFA": (29, 32),
    }, operands, **other)

def InstXL(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "BT" : (6, 11),
        "BA" : (11, 16),
        "BB" : (16, 21),
        "XO" : (21, 31),
        "BO" : (6, 11),
        "BI" : (11, 16),
        "BH" : (19, 21),
        "LK" : (31, 32),
        "BF" : (6, 9),
        "BFA" : (11, 14)
    }, operands, **other)

def InstXO(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "RA": (11, 16),
        "RB": (16, 21),
        "OE": (21, 22),
        "XO": (22, 31),
        "Rc": (31, 32)
    }, operands, **other)

def InstXFX(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
        "RT": (6, 11),
        "DUI": (6, 11),
        "RS": (6, 11),
        "SPR": (11, 21),
        "TBR": (11, 21),
        "DCR": (11, 21),
        "DUIS": (11, 21),
        "FXM": (12, 20),
        "XO": (21, 31)
    }, operands, **other)

def InstA(name: str, category: str, operands: list[str | bytes | int], **other) -> type[Instruction]:
    return Inst(name, category, 4, {
        "OPCD": (0, 6),
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
    }, operands, **other)
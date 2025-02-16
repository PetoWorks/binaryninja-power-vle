from typing_extensions import Self
from enum import Flag, auto

from .instruction import (
    Instruction,
    InstBD15, InstBD24, InstBD8, InstC,
    InstD, InstD8, InstI16A, InstI16L,
    InstIM5, InstIM7, InstLI20,
    InstM, InstOIM5,
    InstR, InstRR,
    InstSCI8, InstSD4,
    InstX, InstXL
)

from .utils import get_bits_from_int


class PowerCategory(Flag):
    B = auto()
    S = auto()
    E = auto()
    ATB = auto()
    CS = auto()
    E_CD = auto()
    E_CI = auto()
    E_ED = auto()
    E_PD = auto()
    E_LE = auto()
    E_MF = auto()
    E_PM = auto()
    E_PC = auto()
    ECL = auto()
    EXC = auto()
    EXP = auto()
    FP = auto()
    FP_R = auto()
    LMV = auto()
    LMA = auto()
    LSQ = auto()
    MMC = auto()
    MA = auto()
    S_PM = auto()
    SP = auto()
    STM = auto()
    TRC = auto()
    VLE = auto()
    V = auto()
    WT = auto()
    X64 = auto()


class Map:

    def __init__(self, start: int, end: int, childs: dict[int, Self | type[Instruction]]):
        self.start = start
        self.end = end
        self.childs = childs

    def decode(self, data: int) -> type[Instruction] | None:
        key = get_bits_from_int(data, 32, self.start, self.end)
        if key in self.childs:
            child = self.childs[key]
            if isinstance(child, Map):
                return child.decode(data)
            else:
                return child

class Lv:
    start: int
    end: int
    childs: dict[int, type[Self] | type[Instruction]]

    @classmethod
    def map(cls, map: Map = None) -> Map:

        if map == None:
            map = Map(cls.start, cls.end, {})
        else:
            if map.start != cls.start or map.end != cls.end:
                raise ValueError("this level cannot be mapped into another")

        for k, v in cls.childs.items():
            if issubclass(v, Instruction):
                if k in map.childs:
                    raise ValueError(f"instruction map build collision: {v.name} -> {map.childs[k]}")
                else:
                    map.childs[k] = v
            elif issubclass(v, Lv):
                if k in map.childs:
                    if type(map.childs[k]) == Map:
                        map.childs[k] = v.map(map.childs[k])
                    else:
                        raise ValueError(f"instruction map build collision: {v} -> {map.childs[k].name}")
                else:
                    map.childs[k] = v.map()
            else:
                raise TypeError(f"unknown child type: {k}:{v}")
        
        return map


def Level(start: int, end: int, childs: dict[int, type[Lv] | type[Instruction]]) -> type[Lv]:
    return type(f"Level_{start}_{end}", (Lv, ), {"start": start, "end": end, "childs": childs})


class Decoder:

    VLE_INST_TABLE = Level(0, 4, { # opcode primary bits level (inst[0:4])

        0x0: Level(4, 8, { # next 4-bits of opcode (inst[4:8])
            0x0: Level(8, 12, { # next 4-bits of opcode (inst[8:12])
                0x0: Level(12, 16, { # next 4-bits of opcode (inst[12:16])
                    0x0: InstC("se_illegal", "VLE", []),
                    0x1: InstC("se_isync", "VLE", []),
                    0x2: InstC("se_sc", "VLE", []),
                    0x4: InstC("se_blr", "VLE", ["LK"], branch=True),
                    0x5: InstC("se_blr", "VLE", ["LK"], branch=True),
                    0x6: InstC("se_bctr", "VLE", ["LK"], branch=True),
                    0x7: InstC("se_bctr", "VLE", ["LK"], branch=True),
                    0x8: InstC("se_rfi", "VLE", []),
                    0x9: InstC("se_rfci", "VLE", []),
                    0xA: InstC("se_rfdi", "VLE", []),
                    0xB: InstC("se_rfmci", "VLE", []),
                }),
                0x2: InstR("se_not", "VLE", ["RX"]),
                0x3: InstR("se_neg", "VLE", ["RX"]),
                0x8: InstR("se_mflr", "VLE", ["RX"]),
                0x9: InstR("se_mtlr", "VLE", ["RX"]),
                0xA: InstR("se_mfctr", "VLE", ["RX"]),
                0xB: InstR("se_mtctr", "VLE", ["RX"]),
                0xC: InstR("se_extzb", "VLE", ["RX"]),
                0xD: InstR("se_extsb", "VLE", ["RX"]),
                0xE: InstR("se_extzh", "VLE", ["RX"]),
                0xF: InstR("se_extsh", "VLE", ["RX"]),
            }),
            0x1: InstRR("se_mr", "VLE", ["RX", "RY"]),
            0x2: InstRR("se_mtar", "VLE", ["ARX", "RY"]),
            0x3: InstRR("se_mfar", "VLE", ["RX", "ARY"]),
            0x4: InstRR("se_add", "VLE", ["RX", "RY"]),
            0x5: InstRR("se_mullw", "VLE", ["RX", "RY"]),
            0x6: InstRR("se_sub", "VLE", ["RX", "RY"]),
            0x7: InstRR("se_subf", "VLE", ["RX", "RY"]),
            0xC: InstRR("se_cmp", "VLE", ["RX", "RY"]),
            0xD: InstRR("se_cmpl", "VLE", ["RX", "RY"]),
            0xE: InstRR("se_cmph", "VLE", ["RX", "RY"]),
            0xF: InstRR("se_cmphl", "VLE", ["RX", "RY"]),
        }),

        0x1: Level(4, 6, { # opcode secondary bits level (inst[4:6])
            0b10: Level(16, 20, { # extra opcode primary bits level (inst[16:20])
                0x0: Level(20, 24, { # extra opcode secondary bits level (inst[20:24])
                    0x0: InstD8("e_lbzu", "VLE", ["RT", "RA", "D8"]),
                    0x1: InstD8("e_lhzu", "VLE", ["RT", "RA", "D8"]),
                    0x2: InstD8("e_lwzu", "VLE", ["RT", "RA", "D8"]),
                    0x3: InstD8("e_lhau", "VLE", ["RT", "RA", "D8"]),
                    0x4: InstD8("e_stbu", "VLE", ["RS", "RA", "D8"]),
                    0x5: InstD8("e_sthu", "VLE", ["RS", "RA", "D8"]),
                    0x6: InstD8("e_stwu", "VLE", ["RS", "RA", "D8"]),
                    0x8: InstD8("e_lmw", "VLE", ["RT", "RA", "D8"]),
                    0x9: InstD8("e_stmw", "VLE", ["RS", "RA", "D8"]),
                }),
                0x8: InstSCI8("e_addi", "VLE", ["RT", "RA", "sci8", "Rc"]),
                0x9: InstSCI8("e_addic", "VLE", ["RT", "RA", "sci8", "Rc"]),
                0xA: Level(20, 21, {
                    0: InstSCI8("e_mulli", "VLE", ["RT", "RA", "sci8"]),
                    1: Level(6, 7, {
                        0: InstSCI8("e_cmpi", "VLE", ["BF32", "RA", "sci8"]),
                        1: InstSCI8("e_cmpli", "VLE", ["BF32", "RA", "sci8"]),
                    }),
                }),
                0xB: InstSCI8("e_subfic", "VLE", ["RT", "RA", "sci8", "Rc"]),
                0xC: InstSCI8("e_andi", "VLE", ["RA", "RS", "sci8", "Rc"]),
                0xD: InstSCI8("e_ori", "VLE", ["RA", "RS", "sci8", "Rc"]),
                0xE: InstSCI8("e_xori", "VLE", ["RA", "RS", "sci8", "Rc"]),
            }),
            0b11: InstD("e_add16i", "VLE", ["RT", "RA", "SI"]),
        }),

        0x2: Level(0, 7, { # opcode bits with XO/RC bit (inst[0:7])
            0b0010000: InstOIM5("se_addi", "VLE", ["RX", "oimm"]),
            0b0010001: InstOIM5("se_cmpli", "VLE", ["RX", "oimm"]),
            0b0010010: InstOIM5("se_subi", "VLE", ["RX", "oimm", "Rc"]),
            0b0010011: InstOIM5("se_subi", "VLE", ["RX", "oimm", "Rc"]),
            0b0010101: InstIM5("se_cmpi", "VLE", ["RX", "UI5"]),
            0b0010110: InstIM5("se_bmaski", "VLE", ["RX", "UI5"]),
            0b0010111: InstIM5("se_andi", "VLE", ["RX", "UI5"]),
        }),

        0x3: Level(0, 6, { # opcode bits level (inst[0:6])
            0b001100: InstD("e_lbz", "VLE", ["RT", "RA", "D"]),
            0b001101: InstD("e_stb", "VLE", ["RS", "RA", "D"]),
            0b001110: InstD("e_lha", "VLE", ["RT", "RA", "D"]),
        }),

        0x4: Level(4, 6, { # secondary opcode level (inst[4:6])
            0b00: Level(4, 8, { # extend opcode level (inst[6:8])
                0x0: InstRR("se_srw", "VLE", ["RX", "RY"]),
                0x1: InstRR("se_sraw", "VLE", ["RX", "RY"]),
                0x2: InstRR("se_slw", "VLE", ["RX", "RY"]),
            }),
            0b01: Level(4, 8, { # ... continued
                0x4: InstRR("se_or", "VLE", ["RX", "RY"]),
                0x5: InstRR("se_andc", "VLE", ["RX", "RY"]),
                0x6: InstRR("se_and", "VLE", ["RX", "RY", "Rc"]),
                0x7: InstRR("se_and", "VLE", ["RX", "RY", "Rc"]),
            }),
            0b10: InstIM7("se_li", "VLE", ["RX", "UI7"]),
        }),

        0x5: Level(0, 6, { # opcode bits level (inst[0:6])
            0b010100: InstD("e_lwz", "VLE", ["RT", "RA", "D"]),
            0b010101: InstD("e_stw", "VLE", ["RS", "RA", "D"]),
            0b010110: InstD("e_lhz", "VLE", ["RT", "RA", "D"]),
            0b010111: InstD("e_sth", "VLE", ["RS", "RA", "D"]),
        }),

        0x6: Level(0, 7, { # opcode bits level with XO bit (inst[0:7])
            0b0110000: InstIM5("se_bclri", "VLE", ["RX", "UI5"]),
            0b0110001: InstIM5("se_bgeni", "VLE", ["RX", "UI5"]),
            0b0110010: InstIM5("se_bseti", "VLE", ["RX", "UI5"]),
            0b0110011: InstIM5("se_btsti", "VLE", ["RX", "UI5"]),
            0b0110100: InstIM5("se_srwi", "VLE", ["RX", "UI5"]),
            0b0110001: InstIM5("se_srawi", "VLE", ["RX", "UI5"]),
            0b0110110: InstIM5("se_slwi", "VLE", ["RX", "UI5"]),
        }),

        0x7: Level(0, 6, { # entire opcode level (inst[0:6])
            0b011100: Level(16, 17, { # first XO bit (inst[16:17])
                0: InstLI20("e_li", "VLE", ["RT", "LI20"]),
                1: Level(17, 21, { # last XO bits (inst[17:21])
                    0b0001: InstI16A("e_add2i.", "VLE", ["RA", "SI"]),
                    0b0010: InstI16A("e_add2is", "VLE", ["RA", "SI"]),
                    0b0011: InstI16A("e_cmp16i", "VLE", ["RA", "SI"]),
                    0b0100: InstI16A("e_mull2i", "VLE", ["RA", "SI"]),
                    0b0101: InstI16A("e_cmpl16i", "VLE", ["RA", "UI"]),
                    0b0110: InstI16A("e_cmph16i", "VLE", ["RA", "SI"]),
                    0b0111: InstI16A("e_cmphl16i", "VLE", ["RA", "UI"]),
                    0b1000: InstI16L("e_or2i", "VLE", ["RT", "UI"]),
                    0b1001: InstI16L("e_and2i.", "VLE", ["RT", "UI"]),
                    0b1010: InstI16L("e_or2is", "VLE", ["RT", "UI"]),
                    0b1100: InstI16L("e_lis", "VLE", ["RT", "UI"]),
                    0b1101: InstI16L("e_and2is.", "VLE", ["RT", "UI"]),
                })
            }),
            0b011101: Level(31, 32, {
                0: InstM("e_rlwimi", "VLE", ["RA", "RS", "SH", "MB", "ME"]),
                1: InstM("e_rlwinm", "VLE", ["RA", "RS", "SH", "MB", "ME"]),
            }),
            0b011110: Level(6, 7, {
                0: InstBD24("e_b", "VLE", ["target_addr", "LK"], branch=True),
                1: InstBD15("e_bc", "VLE", ["BI32", "target_addr", "LK"], conditional_branch=True),
            }),
            0b011111: Level(27, 31, { # last XO bits (inst[27:31])
                0x0: InstXL("e_mcrf", "VLE",  ["BF", "BFA"]),
                0x1: Level(21, 26, { 
                    0b00001: InstXL("e_crnor", "VLE",  ["BT", "BA", "BB"]),
                    0b00100: InstXL("e_crandc", "VLE",  ["BT", "BA", "BB"]),
                    0b00110: InstXL("e_crxor", "VLE",  ["BT", "BA", "BB"]),
                    0b00111: InstXL("e_crnand", "VLE",  ["BT", "BA", "BB"]),
                    0b01000: InstXL("e_crand", "VLE",  ["BT", "BA", "BB"]),
                    0b01001: InstXL("e_creqv", "VLE",  ["BT", "BA", "BB"]),
                    0b01101: InstXL("e_crorc", "VLE",  ["BT", "BA", "BB"]),
                    0b01110: InstXL("e_cror", "VLE",  ["BT", "BA", "BB"]),
                }),
                0x8: Level(21, 26, { 
                    0b00001: InstX("e_slwi", "VLE",  ["RA", "RS", "SH", "Rc"]),
                    0b01000: InstX("e_rlw", "VLE",  ["RA", "RS", "RB", "Rc"]),
                    0b01001: InstX("e_rlwi", "VLE",  ["RA", "RS", "SH", "Rc"]),
                    0b10001: InstX("e_srwi", "VLE", ["RA", "RS", "SH", "Rc"]),
                }),
                0xE: Level(25, 26, { 
                    0: InstX("e_cmph", "VLE",  ["BF", "RA", "RB"]),
                    1: InstX("e_cmphl", "VLE",  ["BF", "RA", "RB"]),
                }),
            }),
        }),
        
        0x8: InstSD4("se_lbz", "VLE", ["RZ", "RX", "SD4"]),
        0x9: InstSD4("se_stb", "VLE", ["RZ", "RX", "SD4"]),
        0xA: InstSD4("se_lhz", "VLE", ["RZ", "RX", "SD4"]),
        0xB: InstSD4("se_sth", "VLE", ["RZ", "RX", "SD4"]),
        0xC: InstSD4("se_lwz", "VLE", ["RZ", "RX", "SD4"]),
        0xD: InstSD4("se_stw", "VLE", ["RZ", "RX", "SD4"]),

        0xE: Level(4, 5, {
            0: InstBD8("se_bc", "VLE", ["BI16", "target_addr"], conditional_branch=True),
            1: InstBD8("se_b", "VLE", ["target_addr", "LK"], branch=True),
        })
    })

    VLE_INST_EXTRA = {
        PowerCategory.SP: Level(0, 4, {}),
        PowerCategory.V: Level(0, 4, {}),
    }

    def __init__(self, categories: PowerCategory = None):
        self.map = Decoder.VLE_INST_TABLE.map()
        self.x64 = PowerCategory.X64 in categories
        for cat in PowerCategory:
            if cat != PowerCategory.VLE and cat in categories:
                self.map = self.VLE_INST_EXTRA[cat].map(self.map)

    def __call__(self, data: bytes, addr: int = 0) -> Instruction | None:
        return self.decode(data, addr)

    def decode(self, data: bytes, addr: int = 0) -> Instruction | None:
        target = int.from_bytes(data[:4] if len(data) >= 4 else data + b'\0\0', 'big')
        instruction = self.map.decode(target)
        if instruction and len(data) >= instruction.length:
            return instruction(target, addr, self.x64)

from typing_extensions import Self
from enum import Flag, auto

from .instruction import (
    Instruction, InstTemp, InstBD15,
    InstBD24, InstBD8, InstC, InstD,
    InstD8, InstI16A, InstI16L, InstIM5,
    InstIM7, InstLI20, InstM, InstOIM5,
    InstR, InstRR, InstSCI8, InstSD4
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

    def decode(self, data: bytes) -> Instruction | None:
        key = get_bits_from_int(data, 32, self.start, self.end)
        if key in self.childs:
            child = self.childs[key]
            if isinstance(child, Map):
                return child.decode(data)
            else:
                return child(data)

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
                    0x0: InstC("se_illegal", "VLE"),
                    0x1: InstC("se_isync", "VLE"),
                    0x2: InstC("se_sc", "VLE"),
                    0x3: InstC("se_sc", "VLE"),
                    0x4: InstC("se_blr", "VLE"),
                    0x5: InstC("se_blr", "VLE"),
                    0x6: InstC("se_bctr", "VLE"),
                    0x7: InstC("se_bctr", "VLE"),
                    0x8: InstC("se_rfi", "VLE"),
                    0x9: InstC("se_rfci", "VLE"),
                    0xA: InstC("se_rfdi", "VLE"),
                    0xB: InstC("se_rfmci", "VLE"),
                }),
                0x2: InstR("se_not", "VLE"),
                0x3: InstR("se_neg", "VLE"),
                0x8: InstR("se_mflr", "VLE"),
                0x9: InstR("se_mtlr", "VLE"),
                0xA: InstR("se_mfctr", "VLE"),
                0xB: InstR("se_mtctr", "VLE"),
                0xC: InstR("se_extzb", "VLE"),
                0xD: InstR("se_extsb", "VLE"),
                0xE: InstR("se_extzh", "VLE"),
                0xF: InstR("se_extsh", "VLE"),
            }),
            0x1: InstRR("se_mr", "VLE"),
            0x2: InstRR("se_mtar", "VLE"),
            0x3: InstRR("se_mfar", "VLE"),
            0x4: InstRR("se_add", "VLE"),
            0x5: InstRR("se_mullw", "VLE"),
            0x6: InstRR("se_sub", "VLE"),
            0x7: InstRR("se_subf", "VLE"),
            0xC: InstRR("se_cmp", "VLE"),
            0xD: InstRR("se_cmpl", "VLE"),
            0xE: InstRR("se_cmph", "VLE"),
            0xF: InstRR("se_cmphl", "VLE"),
        }),

        0x1: Level(4, 6, { # opcode secondary bits level (inst[4:6])
            0b10: Level(16, 20, { # extra opcode primary bits level (inst[16:20])
                0x0: Level(20, 24, { # extra opcode secondary bits level (inst[20:24])
                    0x0: InstD8("e_lbzu", "VLE"),
                    0x1: InstD8("e_lhzu", "VLE"),
                    0x2: InstD8("e_lwzu", "VLE"),
                    0x3: InstD8("e_lhau", "VLE"),
                    0x4: InstD8("e_stbu", "VLE"),
                    0x5: InstD8("e_sthu", "VLE"),
                    0x6: InstD8("e_stwu", "VLE"),
                    0x8: InstD8("e_lmw", "VLE"),
                    0x9: InstD8("e_stmw", "VLE"),
                }),
                0x8: InstSCI8("e_addi", "VLE"),
                0x9: InstSCI8("e_addic", "VLE"),
                0xA: Level(20, 21, {
                    0: InstSCI8("e_mulli", "VLE"),
                    1: Level(6, 7, {
                        0: InstSCI8("e_cmpi", "VLE"),
                        1: InstSCI8("e_cmpli", "VLE"),
                    }),
                }),
                0xB: InstSCI8("e_subfic", "VLE"),
                0xC: InstSCI8("e_andi", "VLE"),
                0xD: InstSCI8("e_ori", "VLE"),
                0xE: InstSCI8("e_xori", "VLE"),
            }),
            0b11: InstD("e_add16i", "VLE"),
        }),

        0x2: Level(0, 7, { # opcode bits with XO/RC bit (inst[0:7])
            0b0010000: InstOIM5("se_addi", "VLE"),
            0b0010001: InstOIM5("se_cmpli", "VLE"),
            0b0010010: InstOIM5("se_subi", "VLE"),
            0b0010011: InstOIM5("se_subi", "VLE"),
            0b0010101: InstIM5("se_cmpi", "VLE"),
            0b0010110: InstIM5("se_bmaski", "VLE"),
            0b0010111: InstIM5("se_andi", "VLE"),
        }),

        0x3: Level(0, 6, { # opcode bits level (inst[0:6])
            0b001100: InstD("e_lbz", "VLE"),
            0b001101: InstD("e_stb", "VLE"),
            0b001110: InstD("e_lha", "VLE"),
        }),

        0x4: Level(4, 6, { # secondary opcode level (inst[4:6])
            0b00: Level(4, 8, { # extend opcode level (inst[6:8])
                0x0: InstRR("se_srw", "VLE"),
                0x1: InstRR("se_sraw", "VLE"),
                0x2: InstRR("se_slw", "VLE"),
            }),
            0b01: Level(4, 8, { # ... continued
                0x4: InstRR("se_or", "VLE"),
                0x5: InstRR("se_andc", "VLE"),
                0x6: InstRR("se_and", "VLE"),
                0x7: InstRR("se_and", "VLE"),
            }),
            0b10: InstIM7("se_li", "VLE"),
        }),

        0x5: Level(0, 6, { # opcode bits level (inst[0:6])
            0b010100: InstD("e_lwz", "VLE"),
            0b010101: InstD("e_stw", "VLE"),
            0b010110: InstD("e_lhz", "VLE"),
            0b010111: InstD("e_sth", "VLE"),
        }),

        0x6: Level(0, 7, { # opcode bits level with XO bit (inst[0:7])
            0b0110000: InstIM5("se_bclri", "VLE"),
            0b0110001: InstIM5("se_bgeni", "VLE"),
            0b0110010: InstIM5("se_bseti", "VLE"),
            0b0110011: InstIM5("se_btsti", "VLE"),
            0b0110100: InstIM5("se_srwi", "VLE"),
            0b0110001: InstIM5("se_srawi", "VLE"),
            0b0110110: InstIM5("se_slwi", "VLE"),
        }),

        0x7: Level(0, 6, { # entire opcode level (inst[0:6])
            0b011100: Level(16, 17, { # first XO bit (inst[16:17])
                0: InstLI20("e_li", "VLE"),
                1: Level(17, 21, { # last XO bits (inst[17:21])
                    0b0001: InstI16A("e_add2i.", "VLE"),
                    0b0010: InstI16A("e_add2is", "VLE"),
                    0b0011: InstI16A("e_cmp16i", "VLE"),
                    0b0100: InstI16A("e_mull2i", "VLE"),
                    0b0101: InstI16A("e_cmpl16i", "VLE"),
                    0b0110: InstI16A("e_cmph16i", "VLE"),
                    0b0111: InstI16A("e_cmphl16i", "VLE"),
                    0b1000: InstI16L("e_or2i", "VLE"),
                    0b1001: InstI16L("e_and2i.", "VLE"),
                    0b1010: InstI16L("e_or2is", "VLE"),
                    0b1100: InstI16L("e_lis", "VLE"),
                    0b1101: InstI16L("e_and2is.", "VLE"),
                })
            }),
            0b011101: Level(31, 32, {
                0: InstM("e_rlwimi", "VLE"),
                1: InstM("e_rlwinm", "VLE"),
            }),
            0b011110: Level(6, 7, {
                0: InstBD24("e_b", "VLE"),
                1: InstBD15("e_bc", "VLE"),
            }),
        }),
        
        0x8: InstSD4("se_lbz", "VLE"),
        0x9: InstSD4("se_stb", "VLE"),
        0xA: InstSD4("se_lhz", "VLE"),
        0xB: InstSD4("se_sth", "VLE"),
        0xC: InstSD4("se_lwz", "VLE"),
        0xD: InstSD4("se_stw", "VLE"),

        0xE: Level(4, 5, {
            0: InstBD8("se_bc", "VLE"),
            1: InstBD8("se_b", "VLE"),
        })
    })

    TBLS = {
        PowerCategory.SP: Level(0, 4, {}),
        PowerCategory.V: Level(0, 4, {}),
    }

    def __init__(self, categories: PowerCategory = None):
        self.map = Decoder.VLE_INST_TABLE.map()
        for cat in PowerCategory:
            if cat in categories:
                self.map = self.TBLS[cat].map(self.map)

    def decode(self, data: bytes) -> Instruction | None:
        target = int.from_bytes(data[:4] if len(data) >= 4 else data.ljust(4, b'\0'), 'big')
        return self.map.decode(target)

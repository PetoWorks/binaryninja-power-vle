from typing_extensions import Self
from enum import Flag, auto

from .instruction import (
    Instruction, InstBD15,
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
                    0x0: InstC("se_illegal", [], False, "VLE"),
                    0x1: InstC("se_isync", [], False, "VLE"),
                    0x2: InstC("se_sc", [], False, "VLE"),
                    0x3: InstC("se_sc", [], False, "VLE"),
                    0x4: InstC("se_blr", [], False, "VLE"),
                    0x5: InstC("se_blr", [], False, "VLE"),
                    0x6: InstC("se_bctr", [], False, "VLE"),
                    0x7: InstC("se_bctr", [], False, "VLE"),
                    0x8: InstC("se_rfi", [], False, "VLE"),
                    0x9: InstC("se_rfci", [], False, "VLE"),
                    0xA: InstC("se_rfdi", [], False, "VLE"),
                    0xB: InstC("se_rfmci", [], False, "VLE"),
                }),
                0x2: InstR("se_not", [], False, "VLE"),
                0x3: InstR("se_neg", [], False, "VLE"),
                0x8: InstR("se_mflr", [], False, "VLE"),
                0x9: InstR("se_mtlr", [], False, "VLE"),
                0xA: InstR("se_mfctr", [], False, "VLE"),
                0xB: InstR("se_mtctr", [], False, "VLE"),
                0xC: InstR("se_extzb", [], False, "VLE"),
                0xD: InstR("se_extsb", [], False, "VLE"),
                0xE: InstR("se_extzh", [], False, "VLE"),
                0xF: InstR("se_extsh", [], False, "VLE"),
            }),
            0x1: InstRR("se_mr", [], False, "VLE"),
            0x2: InstRR("se_mtar", [], False, "VLE"),
            0x3: InstRR("se_mfar", [], False, "VLE"),
            0x4: InstRR("se_add", [], False, "VLE"),
            0x5: InstRR("se_mullw", [], False, "VLE"),
            0x6: InstRR("se_sub", [], False, "VLE"),
            0x7: InstRR("se_subf", [], False, "VLE"),
            0xC: InstRR("se_cmp", [], False, "VLE"),
            0xD: InstRR("se_cmpl", [], False, "VLE"),
            0xE: InstRR("se_cmph", [], False, "VLE"),
            0xF: InstRR("se_cmphl", [], False, "VLE"),
        }),

        0x1: Level(4, 6, { # opcode secondary bits level (inst[4:6])
            0b10: Level(16, 20, { # extra opcode primary bits level (inst[16:20])
                0x0: Level(20, 24, { # extra opcode secondary bits level (inst[20:24])
                    0x0: InstD8("e_lbzu", [], False, "VLE"),
                    0x1: InstD8("e_lhzu", [], False, "VLE"),
                    0x2: InstD8("e_lwzu", [], False, "VLE"),
                    0x3: InstD8("e_lhau", [], False, "VLE"),
                    0x4: InstD8("e_stbu", [], False, "VLE"),
                    0x5: InstD8("e_sthu", [], False, "VLE"),
                    0x6: InstD8("e_stwu", [], False, "VLE"),
                    0x8: InstD8("e_lmw", [], False, "VLE"),
                    0x9: InstD8("e_stmw", [], False, "VLE"),
                }),
                0x8: InstSCI8("e_addi", [], False, "VLE"),
                0x9: InstSCI8("e_addic", [], False, "VLE"),
                0xA: Level(20, 21, {
                    0: InstSCI8("e_mulli", [], False, "VLE"),
                    1: Level(6, 7, {
                        0: InstSCI8("e_cmpi", [], False, "VLE"),
                        1: InstSCI8("e_cmpli", [], False, "VLE"),
                    }),
                }),
                0xB: InstSCI8("e_subfic", [], False, "VLE"),
                0xC: InstSCI8("e_andi", [], False, "VLE"),
                0xD: InstSCI8("e_ori", [], False, "VLE"),
                0xE: InstSCI8("e_xori", [], False, "VLE"),
            }),
            0b11: InstD("e_add16i", [], False, "VLE"),
        }),

        0x2: Level(0, 7, { # opcode bits with XO/RC bit (inst[0:7])
            0b0010000: InstOIM5("se_addi", [], False, "VLE"),
            0b0010001: InstOIM5("se_cmpli", [], False, "VLE"),
            0b0010010: InstOIM5("se_subi", [], False, "VLE"),
            0b0010011: InstOIM5("se_subi", [], False, "VLE"),
            0b0010101: InstIM5("se_cmpi", [], False, "VLE"),
            0b0010110: InstIM5("se_bmaski", [], False, "VLE"),
            0b0010111: InstIM5("se_andi", [], False, "VLE"),
        }),

        0x3: Level(0, 6, { # opcode bits level (inst[0:6])
            0b001100: InstD("e_lbz", [], False, "VLE"),
            0b001101: InstD("e_stb", [], False, "VLE"),
            0b001110: InstD("e_lha", [], False, "VLE"),
        }),

        0x4: Level(4, 6, { # secondary opcode level (inst[4:6])
            0b00: Level(4, 8, { # extend opcode level (inst[6:8])
                0x0: InstRR("se_srw", [], False, "VLE"),
                0x1: InstRR("se_sraw", [], False, "VLE"),
                0x2: InstRR("se_slw", [], False, "VLE"),
            }),
            0b01: Level(4, 8, { # ... continued
                0x4: InstRR("se_or", [], False, "VLE"),
                0x5: InstRR("se_andc", [], False, "VLE"),
                0x6: InstRR("se_and", [], False, "VLE"),
                0x7: InstRR("se_and", [], False, "VLE"),
            }),
            0b10: InstIM7("se_li", [], False, "VLE"),
        }),

        0x5: Level(0, 6, { # opcode bits level (inst[0:6])
            0b010100: InstD("e_lwz", [], False, "VLE"),
            0b010101: InstD("e_stw", [], False, "VLE"),
            0b010110: InstD("e_lhz", [], False, "VLE"),
            0b010111: InstD("e_sth", [], False, "VLE"),
        }),

        0x6: Level(0, 7, { # opcode bits level with XO bit (inst[0:7])
            0b0110000: InstIM5("se_bclri", [], False, "VLE"),
            0b0110001: InstIM5("se_bgeni", [], False, "VLE"),
            0b0110010: InstIM5("se_bseti", [], False, "VLE"),
            0b0110011: InstIM5("se_btsti", [], False, "VLE"),
            0b0110100: InstIM5("se_srwi", [], False, "VLE"),
            0b0110001: InstIM5("se_srawi", [], False, "VLE"),
            0b0110110: InstIM5("se_slwi", [], False, "VLE"),
        }),

        0x7: Level(0, 6, { # entire opcode level (inst[0:6])
            0b011100: Level(16, 17, { # first XO bit (inst[16:17])
                0: InstLI20("e_li", [], False, "VLE"),
                1: Level(17, 21, { # last XO bits (inst[17:21])
                    0b0001: InstI16A("e_add2i.", [], False, "VLE"),
                    0b0010: InstI16A("e_add2is", [], False, "VLE"),
                    0b0011: InstI16A("e_cmp16i", [], False, "VLE"),
                    0b0100: InstI16A("e_mull2i", [], False, "VLE"),
                    0b0101: InstI16A("e_cmpl16i", [], False, "VLE"),
                    0b0110: InstI16A("e_cmph16i", [], False, "VLE"),
                    0b0111: InstI16A("e_cmphl16i", [], False, "VLE"),
                    0b1000: InstI16L("e_or2i", [], False, "VLE"),
                    0b1001: InstI16L("e_and2i.", [], False, "VLE"),
                    0b1010: InstI16L("e_or2is", [], False, "VLE"),
                    0b1100: InstI16L("e_lis", [], False, "VLE"),
                    0b1101: InstI16L("e_and2is.", [], False, "VLE"),
                })
            }),
            0b011101: Level(31, 32, {
                0: InstM("e_rlwimi", [], False, "VLE"),
                1: InstM("e_rlwinm", [], False, "VLE"),
            }),
            0b011110: Level(6, 7, {
                0: InstBD24("e_b", [], False, "VLE"),
                1: InstBD15("e_bc", [], False, "VLE"),
            }),
        }),
        
        0x8: InstSD4("se_lbz", [], False, "VLE"),
        0x9: InstSD4("se_stb", [], False, "VLE"),
        0xA: InstSD4("se_lhz", [], False, "VLE"),
        0xB: InstSD4("se_sth", [], False, "VLE"),
        0xC: InstSD4("se_lwz", [], False, "VLE"),
        0xD: InstSD4("se_stw", [], False, "VLE"),

        0xE: Level(4, 5, {
            0: InstBD8("se_bc", [], False, "VLE"),
            1: InstBD8("se_b", [], False, "VLE"),
        })
    })

    TBLS = {
        PowerCategory.SP: Level(0, 4, {}),
        PowerCategory.V: Level(0, 4, {}),
    }

    def __init__(self, categories: PowerCategory = None):
        self.map = Decoder.VLE_INST_TABLE.map()
        for cat in PowerCategory:
            if cat != PowerCategory.VLE and cat in categories:
                self.map = self.TBLS[cat].map(self.map)

    def decode(self, data: bytes) -> Instruction | None:
        target = int.from_bytes(data[:4] if len(data) >= 4 else data.ljust(4, b'\0'), 'big')
        instruction = self.map.decode(target)
        if instruction and len(data) >= instruction.length:
            return instruction

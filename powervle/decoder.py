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
    InstX, InstXL,
    InstEVX, InstEVS, InstXFX, InstXO,
    InstA
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
        # SPE Category : SP, SP.FV, SP.FS, SP.FD
        PowerCategory.SP: Level(0, 4, { # opcode primary bits level (inst[0:6])
            0x1: Level(4, 6, {  # opcode secondary bits level (inst[4:6])
                0b00: Level(21, 24, { # First XO 3-bits inst[21:24]
                    0x2: Level(24, 28, { # Second XO 4-bits inst[24:28]
                        0x0: Level(28, 32, {    # Last XO 4-bits inst[28:32]
                            0x0: InstEVX("evaddw", "SP", ["RT", "RA", "RB"]),
                            0x2: InstEVX("evaddiw", "SP", ["RT", "RB", "UI_11_16"]),
                            0x4: InstEVX("evsubfw", "SP", ["RT", "RA", "RB"]),
                            0x6: InstEVX("evsubifw", "SP", ["RT", "UI_11_16", "RB"]),
                            0x8: InstEVX("evabs", "SP", ["RT", "RA"]),
                            0x9: InstEVX("evneg", "SP", ["RT", "RA"]),
                            0xA: InstEVX("evextsb", "SP", ["RT", "RA"]),
                            0xB: InstEVX("evextsh", "SP", ["RT", "RA"]),
                            0xC: InstEVX("evrndw", "SP", ["RT", "RA"]),
                            0xD: InstEVX("evcntlzw", "SP", ["RT", "RA"]),
                            0xE: InstEVX("evcntlsw", "SP", ["RT", "RA"]),
                            0xF: InstEVX("brinc", "SP", ["RT", "RA", "RB"]),
                        }),
                        0x1: Level(28, 32, {
                            0x1: InstEVX("evand", "SP", ["RT", "RA", "RB"]),
                            0x2: InstEVX("evandc", "SP", ["RT", "RA", "RB"]),
                            0x6: InstEVX("evxor", "SP", ["RT", "RA", "RB"]),
                            0x7: InstEVX("evor", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evnor", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("eveqv", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evorc", "SP", ["RT", "RA", "RB"]),
                            0xE: InstEVX("evnand", "SP", ["RT", "RA", "RB"]),
                        }),

                        0x2: Level(28, 32, {
                            0x0: InstEVX("evsrwu", "SP", ["RT", "RA", "RB"]),
                            0x1: InstEVX("evsrws", "SP", ["RT", "RA", "RB"]),
                            0x2: InstEVX("evsrwiu", "SP", ["RT", "RA", "UI_16_21"]),
                            0x3: InstEVX("evsrwis", "SP", ["RT", "RA", "UI_16_21"]),
                            0x4: InstEVX("evslw", "SP", ["RT", "RA", "RB"]),
                            0x6: InstEVX("evslwi", "SP", ["RT", "RA", "UI_16_21"]),
                            0x8: InstEVX("evrlw", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evsplati", "SP", ["RT", "SI"]),
                            0xA: InstEVX("evrlwi", "SP", ["RT", "RA", "UI_16_21"]),
                            0xB: InstEVX("evsplatfi", "SP", ["RT", "SI"]),
                            0xC: InstEVX("evmergehi", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evmergelo", "SP", ["RT", "RA", "RB"]),
                            0xE: InstEVX("evmergehilo", "SP", ["RT", "RA", "RB"]),
                            0xF: InstEVX("evmergelohi", "SP", ["RT", "RA", "RB"]),
                        }),

                        0x3: Level(28, 32, {
                            0x0: InstEVX("evcmpltu", "SP", ["BF", "RA", "RB"]),
                            0x1: InstEVX("evcmpgts", "SP", ["BF", "RA", "RB"]),
                            0x2: InstEVX("evcmpgtu", "SP", ["BF", "RA", "RB"]),
                            0x3: InstEVX("evcmplts", "SP", ["BF", "RA", "RB"]),
                            0x4: InstEVX("evcmpeq", "SP", ["BF", "RA", "RB"]),
                        }),
                        
                        0x7: Level(28, 29, { # EVS Form - Last XO 1-bit inst[28:29]
                            0x1: InstEVS("evsel", "SP", ["RT", "RA", "RB", "BFA"]),
                        }),

                        # SP.FV
                        0x8: Level(28, 32, {
                            0x0: InstEVX("evfsadd", "SP.FV", ["RT", "RA", "RB"]),
                            0x1: InstEVX("evfssub", "SP.FV", ["RT", "RA", "RB"]),
                            0x4: InstEVX("evfsabs", "SP.FV", ["RT", "RA"]),
                            0x5: InstEVX("evfsnabs", "SP.FV", ["RT", "RA"]),
                            0x6: InstEVX("evfsneg", "SP.FV", ["RT", "RA"]),
                            0x8: InstEVX("evfsmul", "SP.FV", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evfsdiv", "SP.FV", ["RT", "RA", "RB"]),
                            0xC: InstEVX("evfscmpgt", "SP.FV", ["BF", "RA", "RB"]),
                            0xD: InstEVX("evfscmplt", "SP.FV", ["BF", "RA", "RB"]),
                            0xE: InstEVX("evfscmpeq", "SP.FV", ["BF", "RA", "RB"]),
                        }),

                        0x9: Level(28, 32, {
                            0x0: InstEVX("evfscfui", "SP.FV", ["RT", "RB"]),
                            0x1: InstEVX("evfscfsi", "SP.FV", ["RT", "RB"]),
                            0x2: InstEVX("evfscfuf", "SP.FV", ["RT", "RB"]),
                            0x3: InstEVX("evfscfsf", "SP.FV", ["RT", "RB"]),
                            0x4: InstEVX("evfsctui", "SP.FV", ["RT", "RB"]),
                            0x5: InstEVX("evfsctsi", "SP.FV", ["RT", "RB"]),
                            0x6: InstEVX("evfsctuf", "SP.FV", ["RT", "RB"]),
                            0x7: InstEVX("evfsctsf", "SP.FV", ["RT", "RB"]),
                            0x8: InstEVX("evfsctuiz", "SP.FV", ["RT", "RB"]),
                            0xA: InstEVX("evfsctsiz", "SP.FV", ["RT", "RB"]),
                            0xC: InstEVX("evfststgt", "SP.FV", ["BF", "RA", "RB"]),
                            0xD: InstEVX("evfststlt", "SP.FV", ["BF", "RA", "RB"]),
                            0xE: InstEVX("evfststeq", "SP.FV", ["BF", "RA", "RB"]),
                        }),

                        0xC: Level(28, 32, {
                            0x0: InstEVX("efsadd", "SP.FS", ["RT", "RA", "RB"]),
                            0x1: InstEVX("efssub", "SP.FS", ["RT", "RA", "RB"]),
                            # 0x2E2: InstEVX("efscfuid", "SP.FS", []), # No Instruction Info
                            # 0x2E3: InstEVX("efscfsid", "SP.FS", []), # No Instruction Info
                            0x4: InstEVX("efsabs", "SP.FS", ["RT", "RA"]),
                            0x5: InstEVX("efsnabs", "SP.FS", ["RT", "RA"]),
                            0x6: InstEVX("efsneg", "SP.FS", ["RT", "RA"]),
                            0x8: InstEVX("efsmul", "SP.FS", ["RT", "RA", "RB"]),
                            0x9: InstEVX("efsdiv", "SP.FS", ["RT", "RA", "RB"]),
                            # 0x2EA: InstEVX("efsctuidz", "SP.FS", []), # No Instruction Info
                            # 0x2EB: InstEVX("efsctsidz", "SP.FS", []), # No Instruction Info
                            0xC: InstEVX("efscmpgt", "SP.FS", ["BF", "RA", "RB"]),
                            0xD: InstEVX("efscmplt", "SP.FS", ["BF", "RA", "RB"]),
                            0xE: InstEVX("efscmpeq", "SP.FS", ["BF", "RA", "RB"]),
                            0xF: InstEVX("efscfd", "SP.FD", ["RT", "RB"]),
                        }),

                        0xD: Level(28, 32, {
                            0x0: InstEVX("efscfui", "SP.FS", ["RT", "RB"]),
                            0x1: InstEVX("efscfsi", "SP.FS", ["RT", "RB"]),
                            0x2: InstEVX("efscfuf", "SP.FS", ["RT", "RB"]),
                            0x3: InstEVX("efscfsf", "SP.FS", ["RT", "RB"]),
                            0x4: InstEVX("efsctui", "SP.FS", ["RT", "RB"]),
                            0x5: InstEVX("efsctsi", "SP.FS", ["RT", "RB"]),
                            0x6: InstEVX("efsctuf", "SP.FS", ["RT", "RB"]),
                            0x7: InstEVX("efsctsf", "SP.FS", ["RT", "RB"]),
                            0x8: InstEVX("efsctuiz", "SP.FS", ["RT", "RB"]),
                            0xA: InstEVX("efsctsiz", "SP.FS", ["RT", "RB"]),
                            0xC: InstEVX("efststgt", "SP.FS", ["BF", "RA", "RB"]),
                            0xD: InstEVX("efststlt", "SP.FS", ["BF", "RA", "RB"]),
                            0xE: InstEVX("efststeq", "SP.FS", ["BF", "RA", "RB"]),
                        }),

                        0xE: Level(28, 32, {
                            0x0: InstEVX("efdadd", "SP.FD", ["RT", "RA", "RB"]),
                            0x1: InstEVX("efdsub", "SP.FD", ["RT", "RA", "RB"]),
                            0x2: InstEVX("efdcfuid", "SP.FD", ["RT", "RB"]),
                            0x3: InstEVX("efdcfsid", "SP.FD", ["RT", "RB"]),
                            0x4: InstEVX("efdabs", "SP.FD", ["RT", "RA"]),
                            0x5: InstEVX("efdnabs", "SP.FD", ["RT", "RA"]),
                            0x6: InstEVX("efdneg", "SP.FD", ["RT", "RA"]),
                            0x8: InstEVX("efdmul", "SP.FD", ["RT", "RA", "RB"]),
                            0x9: InstEVX("efddiv", "SP.FD", ["RT", "RA", "RB"]),
                            0xA: InstEVX("efdctuidz", "SP.FD", ["RT", "RB"]),
                            0xB: InstEVX("efdctsidz", "SP.FD", ["RT", "RB"]),
                            0xC: InstEVX("efdcmpgt", "SP.FD", ["BF", "RA", "RB"]),
                            0xD: InstEVX("efdcmplt", "SP.FD", ["BF", "RA", "RB"]),
                            0xE: InstEVX("efdcmpeq", "SP.FD", ["BF", "RA", "RB"]),
                            0xF: InstEVX("efdcfs", "SP.FD", ["RT", "RB"]),
                        }),

                        0xF: Level(28, 32, {
                            0x0: InstEVX("efdcfui", "SP.FD", ["RT", "RB"]),
                            0x1: InstEVX("efdcfsi", "SP.FD", ["RT", "RB"]),
                            0x2: InstEVX("efdcfuf", "SP.FD", ["RT", "RB"]),
                            0x3: InstEVX("efdcfsf", "SP.FD", ["RT", "RB"]),
                            0x4: InstEVX("efdctui", "SP.FD", ["RT", "RB"]),
                            0x5: InstEVX("efdctsi", "SP.FD", ["RT", "RB"]),
                            0x6: InstEVX("efdctuf", "SP.FD", ["RT", "RB"]),
                            0x7: InstEVX("efdctsf", "SP.FD", ["RT", "RB"]),
                            0x8: InstEVX("efdctuiz", "SP.FD", ["RT", "RB"]),
                            0xA: InstEVX("efdctsiz", "SP.FD", ["RT", "RB"]),
                            0xC: InstEVX("efdtstgt", "SP.FD", ["BF", "RA", "RB"]),
                            0xD: InstEVX("efdtstlt", "SP.FD", ["BF", "RA", "RB"]),
                            0xE: InstEVX("efdtsteq", "SP.FD", ["BF", "RA", "RB"]),
                        })

                    }),

                    0x3: Level(24, 28, {
                        0x0: Level(28, 32, {
                            0x0: InstEVX("evlddx", "SP", ["RT", "RA", "RB"]),
                            0x1: InstEVX("evldd", "SP", ["RT", "RA", "UI_16_21"]),
                            0x2: InstEVX("evldwx", "SP", ["RT", "RA", "RB"]),
                            0x3: InstEVX("evldw", "SP", ["RT", "RA", "UI_16_21"]),
                            0x4: InstEVX("evldhx", "SP", ["RT", "RA", "RB"]),
                            0x5: InstEVX("evldh", "SP", ["RT", "RA", "UI_16_21"]),
                            0x8: InstEVX("evlhhesplatx", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evlhhesplat", "SP", ["RT", "RA", "UI_16_21"]),
                            0xC: InstEVX("evlhhousplatx", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evlhhousplat", "SP", ["RT", "RA", "UI_16_21"]),
                            0xE: InstEVX("evlhhossplatx", "SP", ["RT", "RA", "RB"]),
                            0xF: InstEVX("evlhhossplat", "SP", ["RT", "RA", "UI_16_21"]),
                        }),

                        0x1: Level(28, 32, {
                            0x0: InstEVX("evlwhex", "SP", ["RT", "RA", "RB"]),
                            0x1: InstEVX("evlwhe", "SP", ["RT", "RA", "UI_16_21"]),
                            0x4: InstEVX("evlwhoux", "SP", ["RT", "RA", "RB"]),
                            0x5: InstEVX("evlwhou", "SP", ["RT", "RA", "UI_16_21"]),
                            0x6: InstEVX("evlwhosx", "SP", ["RT", "RA", "RB"]),
                            0x7: InstEVX("evlwhos", "SP", ["RT", "RA", "UI_16_21"]),
                            0x8: InstEVX("evlwwsplatx", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evlwwsplat", "SP", ["RT", "RA", "UI_16_21"]),
                            0xC: InstEVX("evlwhsplatx", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evlwhsplat", "SP", ["RT", "RA", "UI_16_21"]),
                        }),

                        0x2: Level(28, 32, {
                            0x0: InstEVX("evstddx", "SP", ["RS", "RA", "RB"]),
                            0x1: InstEVX("evstdd", "SP", ["RS", "RA", "UI_16_21"]),
                            0x2: InstEVX("evstdwx", "SP", ["RS", "RA", "RB"]),
                            0x3: InstEVX("evstdw", "SP", ["RS", "RA", "UI_16_21"]),
                            0x4: InstEVX("evstdhx", "SP", ["RS", "RA", "RB"]),
                            0x5: InstEVX("evstdh", "SP", ["RS", "RA", "UI_16_21"]),
                        }),

                        0x3: Level(28, 32, {
                            0x0: InstEVX("evstwhex", "SP", ["RS", "RA", "RB"]),
                            0x1: InstEVX("evstwhe", "SP", ["RS", "RA", "UI_16_21"]),
                            0x4: InstEVX("evstwhox", "SP", ["RS", "RA", "RB"]),
                            0x5: InstEVX("evstwho", "SP", ["RS", "RA", "UI_16_21"]),
                            0x8: InstEVX("evstwwex", "SP", ["RS", "RA", "RB"]),
                            0x9: InstEVX("evstwwe", "SP", ["RS", "RA", "UI_16_21"]),
                            0xC: InstEVX("evstwwox", "SP", ["RS", "RA", "RB"]),
                            0xD: InstEVX("evstwwo", "SP", ["RS", "RA", "UI_16_21"]),
                        }),
                    }),

                    0x4: Level(24, 28, {
                        0x0: Level(28, 32, {
                            0x3: InstEVX("evmhessf", "SP", ["RT", "RA", "RB"]),
                            0x7: InstEVX("evmhossf", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evmheumi", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmhesmi", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evmhesmf", "SP", ["RT", "RA", "RB"]),
                            0xC: InstEVX("evmhoumi", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evmhosmi", "SP", ["RT", "RA", "RB"]),
                            0xF: InstEVX("evmhosmf", "SP", ["RT", "RA", "RB"]),
                        }),

                        0x2: Level(28, 32, {
                            0x3: InstEVX("evmhessfa", "SP", ["RT", "RA", "RB"]),
                            0x7: InstEVX("evmhossfa", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evmheumia", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmhesmia", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evmhesmfa", "SP", ["RT", "RA", "RB"]),
                            0xC: InstEVX("evmhoumia", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evmhosmia", "SP", ["RT", "RA", "RB"]),
                            0xF: InstEVX("evmhosmfa", "SP", ["RT", "RA", "RB"]),
                        }),

                        0x4: Level(28, 32, {
                            0x7: InstEVX("evmwhssf", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evmwlumi", "SP", ["RT", "RA", "RB"]),
                            0xC: InstEVX("evmwhumi", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evmwhsmi", "SP", ["RT", "RA", "RB"]),
                            0xF: InstEVX("evmwhsmf", "SP", ["RT", "RA", "RB"]),
                        }),

                        0x5: Level(28, 32, {
                            0x3: InstEVX("evmwssf", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evmwumi", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmwsmi", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evmwsmf", "SP", ["RT", "RA", "RB"]),
                        }),

                        0x6: Level(28, 32, {
                            0x7: InstEVX("evmwhssfa", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evmwlumia", "SP", ["RT", "RA", "RB"]),
                            0xC: InstEVX("evmwhumia", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evmwhsmia", "SP", ["RT", "RA", "RB"]),
                            0xF: InstEVX("evmwhsmfa", "SP", ["RT", "RA", "RB"]),
                        }),

                        0x7: Level(28, 32, {
                            0x3: InstEVX("evmwssfa", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evmwumia", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmwsmia", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evmwsmfa", "SP", ["RT", "RA", "RB"]),
                        }),

                        0xC: Level(28, 32, {
                            0x0: InstEVX("evaddusiaaw", "SP", ["RT", "RA"]),
                            0x1: InstEVX("evaddssiaaw", "SP", ["RT", "RA"]),
                            0x2: InstEVX("evsubfusiaaw", "SP", ["RT", "RA"]),
                            0x3: InstEVX("evsubfssiaaw", "SP", ["RT", "RA"]),
                            0x4: InstEVX("evmra", "SP", ["RT", "RA"]),
                            0x6: InstEVX("evdivws", "SP", ["RT", "RA", "RB"]),
                            0x7: InstEVX("evdivwu", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evaddumiaaw", "SP", ["RT", "RA"]),
                            0x9: InstEVX("evaddsmiaaw", "SP", ["RT", "RA"]),
                            0xA: InstEVX("evsubfumiaaw", "SP", ["RT", "RA"]),
                            0xB: InstEVX("evsubfsmiaaw", "SP", ["RT", "RA"]),
                        }),
                    }),

                    0x5: Level(24, 28, {
                        0x0: Level(28, 32, {
                            0x0: InstEVX("evmheusiaaw", "SP", ["RT", "RA", "RB"]),
                            0x1: InstEVX("evmhessiaaw", "SP", ["RT", "RA", "RB"]),
                            0x3: InstEVX("evmhessfaaw", "SP", ["RT", "RA", "RB"]),
                            0x4: InstEVX("evmhousiaaw", "SP", ["RT", "RA", "RB"]),
                            0x5: InstEVX("evmhossiaaw", "SP", ["RT", "RA", "RB"]),
                            0x7: InstEVX("evmhossfaaw", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evmheumiaaw", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmhesmiaaw", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evmhesmfaaw", "SP", ["RT", "RA", "RB"]),
                            0xC: InstEVX("evmhoumiaaw", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evmhosmiaaw", "SP", ["RT", "RA", "RB"]),
                            0xF: InstEVX("evmhosmfaaw", "SP", ["RT", "RA", "RB"]),
                        }),

                        0x2: Level(28, 32, {
                            0x8: InstEVX("evmhegumiaa", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmhegsmiaa", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evmhegsmfaa", "SP", ["RT", "RA", "RB"]),
                            0xC: InstEVX("evmhogumiaa", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evmhogsmiaa", "SP", ["RT", "RA", "RB"]),
                            0xF: InstEVX("evmhogsmfaa", "SP", ["RT", "RA", "RB"]),
                        }),

                        0x4: Level(28, 32, {
                            0x0: InstEVX("evmwlusiaaw", "SP", ["RT", "RA", "RB"]),
                            0x1: InstEVX("evmwlssiaaw", "SP", ["RT", "RA", "RB"]),
                            # 0x4: InstEVX("evmwhusiaaw", "SP", []),    # No Instruction Info
                            # 0x7: InstEVX("evmwhssfaaw", "SP", []),    # No Instruction Info
                            0x8: InstEVX("evmwlumiaaw", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmwlsmiaaw", "SP", ["RT", "RA", "RB"]),
                            # 0xC: InstEVX("evmwhumiaaw", "SP", []),    # No Instruction Info
                            # 0xD: InstEVX("evmwhsmiaaw", "SP", []),    # No Instruction Info
                            # 0xF: InstEVX("evmwhsmfaaw", "SP", []),    # No Instruction Info
                        }),

                        0x5: Level(28, 32, {
                            0x3: InstEVX("evmwssfaa", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evmwumiaa", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmwsmiaa", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evmwsmfaa", "SP", ["RT", "RA", "RB"]),
                        }),

                        0x8: Level(28, 32, {
                            0x0: InstEVX("evmheusianw", "SP", ["RT", "RA", "RB"]),
                            0x1: InstEVX("evmhessianw", "SP", ["RT", "RA", "RB"]),
                            0x3: InstEVX("evmhessfanw", "SP", ["RT", "RA", "RB"]),
                            0x4: InstEVX("evmhousianw", "SP", ["RT", "RA", "RB"]),
                            0x5: InstEVX("evmhossianw", "SP", ["RT", "RA", "RB"]),
                            0x7: InstEVX("evmhossfanw", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evmheumianw", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmhesmianw", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evmhesmfanw", "SP", ["RT", "RA", "RB"]),
                            0xC: InstEVX("evmhoumianw", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evmhosmianw", "SP", ["RT", "RA", "RB"]),
                            0xF: InstEVX("evmhosmfanw", "SP", ["RT", "RA", "RB"]),
                        }),

                        0xA: Level(28, 32, {
                            0x8: InstEVX("evmhegumian", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmhegsmian", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evmhegsmfan", "SP", ["RT", "RA", "RB"]),
                            0xC: InstEVX("evmhogumian", "SP", ["RT", "RA", "RB"]),
                            0xD: InstEVX("evmhogsmian", "SP", ["RT", "RA", "RB"]),
                            0xF: InstEVX("evmhogsmfan", "SP", ["RT", "RA", "RB"]),
                        }),

                        0xC: Level(28, 32, {
                            0x0: InstEVX("evmwlusianw", "SP", ["RT", "RA", "RB"]),
                            0x1: InstEVX("evmwlssianw", "SP", ["RT", "RA", "RB"]),
                            # 0x4: InstEVX("evmwhusianw", "SP", []),    # No Instruction Info
                            # 0x5: InstEVX("evmwhssianw", "SP", []),    # No Instruction Info
                            # 0x7: InstEVX("evmwhssfanw", "SP", []),    # No Instruction Info
                            0x8: InstEVX("evmwlumianw", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmwlsmianw", "SP", ["RT", "RA", "RB"]),
                            # 0xC: InstEVX("evmwhumianw", "SP", []),    # No Instruction Info
                            # 0xD: InstEVX("evmwhsmianw", "SP", []),    # No Instruction Info
                            # 0xF: InstEVX("evmwhsmfanw", "SP", []),    # No Instruction Info
                        }),

                        0xD: Level(28, 32, {
                            0x3: InstEVX("evmwssfan", "SP", ["RT", "RA", "RB"]),
                            0x8: InstEVX("evmwumian", "SP", ["RT", "RA", "RB"]),
                            0x9: InstEVX("evmwsmian", "SP", ["RT", "RA", "RB"]),
                            0xB: InstEVX("evmwsmfan", "SP", ["RT", "RA", "RB"]),
                        }),
                    }),
                }),
            })
        }),
        
        # Category B
        PowerCategory.B: Level(0, 4, {
            0x7: Level(0, 6, {
                0b011111: Level(27, 31, {
                    0x0: Level(21, 27, {
                        0b000000: InstX("cmp", "B", ["BF", "L", "RA", "RB"]),
                        0b000010: InstX("cmpl", "B", ["BF", "L", "RA", "RB"]),
                        0b001001: Level(11, 12, {
                            0: InstXFX("mtcrf", "B", ["RS", "FXM"]),
                            1: InstXFX("mtocrf", "B", ["FXM", "RS"]),
                        }),
                        0b100000: InstX("mcrxr", "B", ["BF"]),
                    }),

                    0x3: Level(21, 27, {
                        0b000001: Level(11, 12, {
                            0: InstXFX("mfcr", "B", ["RT"]),
                            1: InstXFX("mfocrf", "B", ["RT", "FXM"]),
                        }),
                        0b000101: InstX("mfmsr", "B", ["RT"]),
                        0b010101: InstXFX("mfspr", "B", ["RT", "SPR"]),
                        0b011101: InstXFX("mtspr", "B", ["SPR", "RS"]),
                    }),

                    0x4: Level(21, 27, {
                        0b000000: InstX("tw", "B", ["TO", "RA", "RB"]),
                        0b000001: InstX("lwarx", "B", ["RT", "RA", "RB"]),
                    }),

                    0x6: Level(21, 27, {
                        0b000011: InstX("dcbst", "B", ["RA", "RB"]),
                        0b000101: InstX("dcbf", "B", ["L", "RA", "RB"]),
                        0b001001: InstX("stwcx.", "B", ["RS", "RA", "RB"]),
                        0b001111: InstX("dcbtst", "B", ["TH", "RA", "RB"]),
                        0b010001: InstX("dcbt", "B", ["TH", "RA", "RB"]),
                        0b100001: InstX("lwbrx", "B", ["RT", "RA", "RB"]),
                        0b100101: InstX("sync", "B", ["L"]),
                        0b101001: InstX("stwbrx", "B", ["RS", "RA", "RB"]),
                        0b110001: InstX("lhbrx", "B", ["RT", "RA", "RB"]),
                        0b111001: InstX("sthbrx", "B", ["RS", "RA", "RB"]),
                        0b111101: InstX("icbi", "B", ["RA", "RB"]),
                        0b111111: InstX("dcbz", "B", ["RA", "RB"]),
                    }),

                    0x7: Level(21, 27, {
                        0b000001: InstX("lwzx", "B", ["RT", "RA", "RB"]),
                        0b000011: InstX("lwzux", "B", ["RT", "RA", "RB"]),
                        0b000101: InstX("lbzx", "B", ["RT", "RA", "RB"]),
                        0b000111: InstX("lbzux", "B", ["RT", "RA", "RB"]),
                        0b001001: InstX("stwx", "B", ["RS", "RA", "RB"]),
                        0b001011: InstX("stwux", "B", ["RS", "RA", "RB"]),
                        0b001101: InstX("stbx", "B", ["RS", "RA", "RB"]),
                        0b001111: InstX("stbux", "B", ["RS", "RA", "RB"]),
                        0b010001: InstX("lhzx", "B", ["RT", "RA", "RB"]),
                        0b010011: InstX("lhzux", "B", ["RT", "RA", "RB"]),
                        0b010101: InstX("lhax", "B", ["RT", "RA", "RB"]),
                        0b010111: InstX("lhaux", "B", ["RT", "RA", "RB"]),
                        0b011001: InstX("sthx", "B", ["RS", "RA", "RB"]),
                        0b011011: InstX("sthux", "B", ["RS", "RA", "RB"]),
                    }),

                    0x8: Level(21, 27, {
                        0b000001: InstX("slw", "B", ["RA", "RS", "RB", "Rc"]),
                        0b100001: InstX("srw", "B", ["RA", "RS", "RB", "Rc"]),
                        0b110001: InstX("sraw", "B", ["RA", "RS", "RB", "Rc"]),
                        0b110011: InstX("srawi", "B", ["RA", "RS", "SH", "Rc"]),

                        # XO-form OE (inst[21:22]) and XO
                        0b000000: InstXO("subfc", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b100000: InstXO("subfco", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b000010: InstXO("subf", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b100010: InstXO("subfo", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b000110: InstXO("neg", "B", ["RT", "RA", "OE", "Rc"]),
                        0b100110: InstXO("nego", "B", ["RT", "RA", "OE", "Rc"]),
                        0b001000: InstXO("subfe", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b101000: InstXO("subfeo", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b001100: InstXO("subfze", "B", ["RT", "RA", "OE", "Rc"]),
                        0b101100: InstXO("subfzeo", "B", ["RT", "RA", "OE", "Rc"]),
                        0b001110: InstXO("subfme", "B", ["RT", "RA", "OE", "Rc"]),
                        0b101110: InstXO("subfmeo", "B", ["RT", "RA", "OE", "Rc"]),

                    }),

                    0xA: Level(21, 27, {
                        0b000001: InstX("cntlzw", "B", ["RA", "RS", "Rc"]),
                        0b000111: InstX("popcntb", "B", ["RA", "RS"]),
                        0b111001: InstX("extsh", "B", ["RA", "RS", "Rc"]),
                        0b111011: InstX("extsb", "B", ["RA", "RS", "Rc"]),

                        # XO-Form
                        0b000000: InstXO("addc", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b100000: InstXO("addco", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b001000: InstXO("adde", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b101000: InstXO("addeo", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b001100: InstXO("addze", "B", ["RT", "RA", "OE", "Rc"]),
                        0b101100: InstXO("addzeo", "B", ["RT", "RA", "OE", "Rc"]),
                        0b001110: InstXO("addme", "B", ["RT", "RA", "OE", "Rc"]),
                        0b101110: InstXO("addmeo", "B", ["RT", "RA", "OE", "Rc"]),
                        0b010000: InstXO("add", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        0b110000: InstXO("addo", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                    }),

                    0xB: Level(22, 27, {
                        0b00000: InstXO("mulhwu", "B", ["RT", "RA", "RB", "Rc"]),
                        0b00100: InstXO("mulhw", "B", ["RT", "RA", "RB", "Rc"]),
                        0b01110: Level(21, 22, {
                            0: InstXO("mullw", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                            1: InstXO("mullwo", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        }),
                        0b11100: Level(21, 22, {
                            0: InstXO("divwu", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                            1: InstXO("divwuo", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        }),
                        0b11110: Level(21, 22, {
                            0: InstXO("divw", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                            1: InstXO("divwo", "B", ["RT", "RA", "RB", "OE", "Rc"]),
                        }),

                    }),

                    0xC: Level(21, 27, {
                        0b000001: InstX("and", "B", ["RA", "RS", "RB", "Rc"]),
                        0b000011: InstX("andc", "B", ["RA", "RS", "RB", "Rc"]),
                        0b000111: InstX("nor", "B", ["RA", "RS", "RB", "Rc"]),
                        0b010001: InstX("eqv", "B", ["RA", "RS", "RB", "Rc"]),
                        0b010011: InstX("xor", "B", ["RA", "RS", "RB", "Rc"]),
                        0b011001: InstX("orc", "B", ["RA", "RS", "RB", "Rc"]),
                        0b011011: InstX("or", "B", ["RA", "RS", "RB", "Rc"]),
                        0b011101: InstX("nand", "B", ["RA", "RS", "RB", "Rc"]),
                    }),

                    0xF: Level(26, 27, {
                        0: InstA("isel", "B", ["RT", "RA", "RB", "BC"]),
                    }),
                }),
            }),
        }),

        #PowerCategory.V: Level(0, 4, {}),
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

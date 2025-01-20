'''
Instruction base classes
'''

from binaryninja.architecture import InstructionInfo
from binaryninja.function import InstructionTextToken
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
    def fetch_opcode(cls, data: int) -> int:
        return _bits(data, 32, *cls.fields["OPCD"])

    @classmethod
    def fetch_fields(cls, data: int) -> dict[str, int]:
        return {field_name: _bits(data, 32, *cls.fields[field_name]) for field_name in cls.uses}

    @classmethod
    def get_instruction_info(cls, fields: tuple[str, int], addr: int) -> InstructionInfo:
        return InstructionInfo(length=cls.length)

    @classmethod
    def get_instruction_text(cls, fields: tuple[str, int], addr: int) -> tuple[list[InstructionTextToken], int]:
        raise NotImplementedError

    @classmethod
    def get_instruction_low_level_il(cls, fields: tuple[str, int], addr: int, il: LowLevelILFunction) -> int:
        raise NotImplementedError


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


'''
Decoder Implementations
'''


class Level:

    def __init__(self, start: int, end: int, childs: dict):
        self.start = start
        self.end = end
        self.childs = childs

    def validate(self, inst: type[Instruction], **options) -> type[Instruction]:
        if inst.category not in options['categories']:
            return InstTemp()
        return inst

    def decode(self, data: int, **options) -> type[Instruction]:

        key = _bits(data, 32, self.start, self.end)
        if key not in self.childs:
            return InstTemp()

        child = self.childs[key]
        if type(child) == Level:
            return child.decode(data, **options)
        else:
            return self.validate(child, **options)


class Select(Level):

    def __init__(self, childs: list):
        self.childs = childs
    
    def decode(self, data: int, **options) -> type[Instruction]:
        for dup in self.childs:
            if type(dup) == Level:
                return dup.decode(data, **options)
            else:
                if self.validate(dup, **options).name != "unknown":
                    return dup
        return InstTemp()


class Decoder:

    # opcode primary bits level (inst[0:4])
    root = Level(0, 4, {

        # next 4-bits of opcode (inst[4:8])
        0x0: Level(4, 8, {
            # next 4-bits of opcode (inst[8:12])
            0x0: Level(8, 12, {
                # next 4-bits of opcode (inst[12:16])
                0x0: Level(12, 16, {
                    0x0: InstTemp("se_illegal", "VLE", 2),
                    0x1: InstTemp("se_isync", "VLE", 2),
                    0x2: InstTemp("se_sc", "VLE", 2),
                    0x3: InstTemp("se_sc", "VLE", 2),
                    0x4: InstTemp("se_blr", "VLE", 2),
                    0x5: InstTemp("se_blr", "VLE", 2),
                    0x6: InstTemp("se_bctr", "VLE", 2),
                    0x7: InstTemp("se_bctr", "VLE", 2),
                    0x8: InstTemp("se_rfi", "VLE", 2),
                    0x9: InstTemp("se_rfci", "VLE", 2),
                    0xA: InstTemp("se_rfdi", "VLE", 2),
                    0xB: InstTemp("se_rfmci", "VLE", 2),
                }),
                0x2: InstTemp("se_not", "VLE", 2),
                0x3: InstTemp("se_neg", "VLE", 2),
                0x8: InstTemp("se_mflr", "VLE", 2),
                0x9: InstTemp("se_mtlr", "VLE", 2),
                0xA: InstTemp("se_mfctr", "VLE", 2),
                0xB: InstTemp("se_mtctr", "VLE", 2),
                0xC: InstTemp("se_extzb", "VLE", 2),
                0xD: InstTemp("se_extsb", "VLE", 2),
                0xE: InstTemp("se_extzh", "VLE", 2),
                0xF: InstTemp("se_extsh", "VLE", 2),
            }),
            0x1: InstTemp("se_mr", "VLE", 2),
            0x2: InstTemp("se_mtar", "VLE", 2),
            0x3: InstTemp("se_mfar", "VLE", 2),
            0x4: InstTemp("se_add", "VLE", 2),
            0x5: InstTemp("se_mullw", "VLE", 2),
            0x6: InstTemp("se_sub", "VLE", 2),
            0x7: InstTemp("se_subf", "VLE", 2),
            0xC: InstTemp("se_cmp", "VLE", 2),
            0xD: InstTemp("se_cmpl", "VLE", 2),
            0xE: InstTemp("se_cmph", "VLE", 2),
            0xF: InstTemp("se_cmphl", "VLE", 2),
        }),

        # opcode secondary bits level (inst[4:6])
        0x1: Level(4, 6, {
            # TODO 0b00: Select()...
            # extra opcode primary bits level (inst[16:20])
            0b10: Level(16, 20, {
                # extra opcode secondary bits level (inst[20:24])
                0x0: Level(20, 24, {
                    0x0: InstTemp("e_lbzu", "VLE", 4),
                    0x1: InstTemp("e_lhzu", "VLE", 4),
                    0x2: InstTemp("e_lwzu", "VLE", 4),
                    0x3: InstTemp("e_lhau", "VLE", 4),
                    0x4: InstTemp("e_stbu", "VLE", 4),
                    0x5: InstTemp("e_sthu", "VLE", 4),
                    0x6: InstTemp("e_stwu", "VLE", 4),
                    0x8: InstTemp("e_lmw", "VLE", 4),
                    0x9: InstTemp("e_stmw", "VLE", 4),
                }),
                0x8: InstTemp("e_addi", "VLE", 4),
                0x9: InstTemp("e_addic", "VLE", 4),
                0xA: Level(20, 21, {
                    0: InstTemp("e_mulli", "VLE", 4),
                    1: Level(6, 7, {
                        0: InstTemp("e_cmpi", "VLE", 4),
                        1: InstTemp("e_cmpli", "VLE", 4),
                    }),
                }),
                0xB: InstTemp("e_subfic", "VLE", 4),
                0xC: InstTemp("e_andi", "VLE", 4),
                0xD: InstTemp("e_ori", "VLE", 4),
                0xE: InstTemp("e_xori", "VLE", 4),
            }),
            0b11: InstTemp("e_add16i", "VLE", 4),
        }),

        # opcode bits with XO/RC bit (inst[0:7])
        0x2: Level(0, 7, {
            0b0010000: InstTemp("se_addi", "VLE", 2),
            0b0010001: InstTemp("se_cmpli", "VLE", 2),
            0b0010010: InstTemp("se_subi", "VLE", 2),
            0b0010011: InstTemp("se_subi", "VLE", 2),
            0b0010101: InstTemp("se_cmpi", "VLE", 2),
            0b0010110: InstTemp("se_bmaski", "VLE", 2),
            0b0010111: InstTemp("se_andi", "VLE", 2),
        }),

        # opcode bits level (inst[0:6])
        0x3: Level(0, 6, {
            0b001100: InstTemp("e_lbz", "VLE", 4),
            0b001101: InstTemp("e_stb", "VLE", 4),
            0b001110: InstTemp("e_lha", "VLE", 4),
        }),

        # secondary opcode level (inst[4:6])
        0x4: Level(4, 6, {
            # extend opcode level (inst[6:8])
            0b00: Level(4, 8, {
                0x0: InstTemp("se_srw", "VLE", 2),
                0x1: InstTemp("se_sraw", "VLE", 2),
                0x2: InstTemp("se_slw", "VLE", 2),
            }),
            # ... continued
            0b01: Level(4, 8, {
                0x4: InstTemp("se_or", "VLE", 2),
                0x5: InstTemp("se_andc", "VLE", 2),
                0x6: InstTemp("se_and", "VLE", 2),
                0x7: InstTemp("se_and", "VLE", 2),
            }),
            0b10: InstTemp("se_li", "VLE", 2),
        }),

        # opcode bits level (inst[0:6])
        0x5: Level(0, 6, {
            0b010100: InstTemp("e_lwz", "VLE", 4),
            0b010101: InstTemp("e_stw", "VLE", 4),
            0b010110: InstTemp("e_lhz", "VLE", 4),
            0b010111: InstTemp("e_sth", "VLE", 4),
        }),

        # opcode bits level with XO bit (inst[0:7])
        0x6: Level(0, 7, {
            0b0110000: InstTemp("se_bclri", "VLE", 2),
            0b0110001: InstTemp("se_bgeni", "VLE", 2),
            0b0110010: InstTemp("se_bseti", "VLE", 2),
            0b0110011: InstTemp("se_btsti", "VLE", 2),
            0b0110100: InstTemp("se_srwi", "VLE", 2),
            0b0110001: InstTemp("se_srawi", "VLE", 2),
            0b0110110: InstTemp("se_slwi", "VLE", 2),
        }),

        # entire opcode level (inst[0:6])
        0x7: Level(0, 6, {
            # first XO bit (inst[16:17])
            0b011100: Level(16, 17, {
                0: InstTemp("e_li", "VLE", 4),
                # last XO bits (inst[17:21])
                1: Level(17, 21, {
                    0b0001: InstTemp("e_add2i.", "VLE", 4),
                    0b0010: InstTemp("e_add2is", "VLE", 4),
                    0b0011: InstTemp("e_cmp16i", "VLE", 4),
                    0b0100: InstTemp("e_mull2i", "VLE", 4),
                    0b0101: InstTemp("e_cmpl16i", "VLE", 4),
                    0b0110: InstTemp("e_cmph16i", "VLE", 4),
                    0b0111: InstTemp("e_cmphl16i", "VLE", 4),
                    0b1000: InstTemp("e_or2i", "VLE", 4),
                    0b1001: InstTemp("e_and2i.", "VLE", 4),
                    0b1010: InstTemp("e_or2is", "VLE", 4),
                    0b1100: InstTemp("e_lis", "VLE", 4),
                    0b1101: InstTemp("e_and2is.", "VLE", 4),
                })
            }),
            0b011101: Level(31, 32, {
                0: InstTemp("e_rlwimi", "VLE", 4),
                1: InstTemp("e_rlwinm", "VLE", 4),
            }),
            0b011110: Level(6, 7, {
                0: InstTemp("e_b", "VLE", 4),
                1: InstTemp("e_bc", "VLE", 4),
            }),
            # TODO 0b011111: Level(),
        }),
        
        0x8: InstTemp("se_lbz", "VLE", 2),
        0x9: InstTemp("se_stb", "VLE", 2),
        0xA: InstTemp("se_lhz", "VLE", 2),
        0xB: InstTemp("se_sth", "VLE", 2),
        0xC: InstTemp("se_lwz", "VLE", 2),
        0xD: InstTemp("se_stw", "VLE", 2),

        0xE: Level(4, 5, {
            0: InstTemp("se_bc", "VLE", 2),
            1: InstTemp("se_b", "VLE", 2),
        })
    })

    @classmethod
    def decode(cls, data: bytes, **options) -> type[Instruction]:
        inst = int.from_bytes(data[:4] if len(data) >= 4 else data.ljust(4, b'\0'), 'big')
        return cls.root.decode(inst, **options)

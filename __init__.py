from typing import Tuple, List

from binaryninja.architecture import Architecture, RegisterInfo, InstructionInfo
from binaryninja.function import InstructionTextToken
from binaryninja.lowlevelil import LowLevelILFunction
from binaryninja.enums import Endianness, FlagRole

from .powervle.decoder import Decoder


class PowerVLE(Architecture):
    name = "power-vle"
    endianness = Endianness.BigEndian
    address_size = 4
    default_int_size = 4
    instr_alignment = 2
    max_instr_length = 4

    regs = {
        'cr0': RegisterInfo("cr0", 4, 0),
        'cr1': RegisterInfo("cr1", 4, 0),
        'cr2': RegisterInfo("cr2", 4, 0),
        'cr3': RegisterInfo("cr3", 4, 0),
        'cr4': RegisterInfo("cr4", 4, 0),
        'cr5': RegisterInfo("cr5", 4, 0),
        'cr6': RegisterInfo("cr6", 4, 0),
        'cr7': RegisterInfo("cr7", 4, 0),
        'lr': RegisterInfo("lr", 4, 0),
        'ctr': RegisterInfo("ctr", 4, 0),
        'r0': RegisterInfo("r0", 4, 0),
        'r1': RegisterInfo("r1", 4, 0),
        'r2': RegisterInfo("r2", 4, 0),
        'r3': RegisterInfo("r3", 4, 0),
        'r4': RegisterInfo("r4", 4, 0),
        'r5': RegisterInfo("r5", 4, 0),
        'r6': RegisterInfo("r6", 4, 0),
        'r7': RegisterInfo("r7", 4, 0),
        'r8': RegisterInfo("r8", 4, 0),
        'r9': RegisterInfo("r9", 4, 0),
        'r10': RegisterInfo("r10", 4, 0),
        'r11': RegisterInfo("r11", 4, 0),
        'r12': RegisterInfo("r12", 4, 0),
        'r13': RegisterInfo("r13", 4, 0),
        'r14': RegisterInfo("r14", 4, 0),
        'r15': RegisterInfo("r15", 4, 0),
        'r16': RegisterInfo("r16", 4, 0),
        'r17': RegisterInfo("r17", 4, 0),
        'r18': RegisterInfo("r18", 4, 0),
        'r19': RegisterInfo("r19", 4, 0),
        'r20': RegisterInfo("r20", 4, 0),
        'r21': RegisterInfo("r21", 4, 0),
        'r22': RegisterInfo("r22", 4, 0),
        'r23': RegisterInfo("r23", 4, 0),
        'r24': RegisterInfo("r24", 4, 0),
        'r25': RegisterInfo("r25", 4, 0),
        'r26': RegisterInfo("r26", 4, 0),
        'r27': RegisterInfo("r27", 4, 0),
        'r28': RegisterInfo("r28", 4, 0),
        'r29': RegisterInfo("r29", 4, 0),
        'r30': RegisterInfo("r30", 4, 0),
        'r31': RegisterInfo("r31", 4, 0),
    }

    stack_pointer = "r1"

    flags = [
        'lt', 'gt', 'eq', 'so',
        'cr1lt', 'cr1gt', 'cr1eq', 'cr1so',
        'cr2lt', 'cr2gt', 'cr2eq', 'cr2so',
        'cr3lt', 'cr3gt', 'cr3eq', 'cr3so',
        'cr4lt', 'cr4gt', 'cr4eq', 'cr4so',
        'cr5lt', 'cr5gt', 'cr5eq', 'cr5so',
        'cr6lt', 'cr6gt', 'cr6eq', 'cr6so',
        'cr7lt', 'cr7gt', 'cr7eq', 'cr7so',
        'xer_so', 'xer_ov', 'xer_ca'
    ]

    flag_roles = {
        'lt': FlagRole.NegativeSignFlagRole,
        'gt': FlagRole.SpecialFlagRole,
        'eq': FlagRole.ZeroFlagRole,
        'so': FlagRole.SpecialFlagRole,
        'cr1lt': FlagRole.NegativeSignFlagRole,
        'cr1gt': FlagRole.SpecialFlagRole,
        'cr1eq': FlagRole.ZeroFlagRole,
        'cr1so': FlagRole.SpecialFlagRole,
        'cr2lt': FlagRole.NegativeSignFlagRole,
        'cr2gt': FlagRole.SpecialFlagRole,
        'cr2eq': FlagRole.ZeroFlagRole,
        'cr2so': FlagRole.SpecialFlagRole,
        'cr3lt': FlagRole.NegativeSignFlagRole,
        'cr3gt': FlagRole.SpecialFlagRole,
        'cr3eq': FlagRole.ZeroFlagRole,
        'cr3so': FlagRole.SpecialFlagRole,
        'cr4lt': FlagRole.NegativeSignFlagRole,
        'cr4gt': FlagRole.SpecialFlagRole,
        'cr4eq': FlagRole.ZeroFlagRole,
        'cr4so': FlagRole.SpecialFlagRole,
        'cr5lt': FlagRole.NegativeSignFlagRole,
        'cr5gt': FlagRole.SpecialFlagRole,
        'cr5eq': FlagRole.ZeroFlagRole,
        'cr5so': FlagRole.SpecialFlagRole,
        'cr6lt': FlagRole.NegativeSignFlagRole,
        'cr6gt': FlagRole.SpecialFlagRole,
        'cr6eq': FlagRole.ZeroFlagRole,
        'cr6so': FlagRole.SpecialFlagRole,
        'cr7lt': FlagRole.NegativeSignFlagRole,
        'cr7gt': FlagRole.SpecialFlagRole,
        'cr7eq': FlagRole.ZeroFlagRole,
        'cr7so': FlagRole.SpecialFlagRole,
        'xer_so': FlagRole.SpecialFlagRole,
        'xer_ov': FlagRole.OverflowFlagRole,
        'xer_ca': FlagRole.CarryFlagRole
    }

    flag_write_types = [
        'none',
        'cr0_signed', 'cr1_signed', 'cr2_signed', 'cr3_signed',
        'cr4_signed', 'cr5_signed', 'cr6_signed', 'cr7_signed',
        'cr0_unsigned', 'cr1_unsigned', 'cr2_unsigned', 'cr3_unsigned',
        'cr4_unsigned', 'cr5_unsigned', 'cr6_unsigned', 'cr7_unsigned',
        'cr0_float', 'cr1_float', 'cr2_float', 'cr3_floatt',
        'cr4_float', 'cr5_float', 'cr6_float', 'cr7_float',
        'xer', 'xer_ca', 'xer_ov_so',
        'mtcr0', 'mtcr1', 'mtcr2', 'mtcr3',
        'mtcr4', 'mtcr5', 'mtcr6', 'mtcr7',
        'invl0', 'invl1', 'invl2', 'invl3',
        'invl4', 'invl5', 'invl6', 'invl7',
        'invall'
    ]

    flags_written_by_flag_write_type = {
        'none': [],
        'cr0_signed': ['lt', 'gt', 'eq', 'so'],
        'cr1_signed': ['cr1lt', 'cr1gt', 'cr1eq', 'cr1so'],
        'cr2_signed': ['cr2lt', 'cr2gt', 'cr2eq', 'cr2so'],
        'cr3_signed': ['cr3lt', 'cr3gt', 'cr3eq', 'cr3so'],
        'cr4_signed': ['cr4lt', 'cr4gt', 'cr4eq', 'cr4so'],
        'cr5_signed': ['cr5lt', 'cr5gt', 'cr5eq', 'cr5so'],
        'cr6_signed': ['cr6lt', 'cr6gt', 'cr6eq', 'cr6so'],
        'cr7_signed': ['cr7lt', 'cr7gt', 'cr7eq', 'cr7so'],
        'cr0_unsigned': ['lt', 'gt', 'eq', 'so'],
        'cr1_unsigned': ['cr1lt', 'cr1gt', 'cr1eq', 'cr1so'],
        'cr2_unsigned': ['cr2lt', 'cr2gt', 'cr2eq', 'cr2so'],
        'cr3_unsigned': ['cr3lt', 'cr3gt', 'cr3eq', 'cr3so'],
        'cr4_unsigned': ['cr4lt', 'cr4gt', 'cr4eq', 'cr4so'],
        'cr5_unsigned': ['cr5lt', 'cr5gt', 'cr5eq', 'cr5so'],
        'cr6_unsigned': ['cr6lt', 'cr6gt', 'cr6eq', 'cr6so'],
        'cr7_unsigned': ['cr7lt', 'cr7gt', 'cr7eq', 'cr7so'],
        'cr0_float': ['lt', 'gt', 'eq', 'so'],
        'cr1_float': ['cr1lt', 'cr1gt', 'cr1eq', 'cr1so'],
        'cr2_float': ['cr2lt', 'cr2gt', 'cr2eq', 'cr2so'],
        'cr3_float': ['cr3lt', 'cr3gt', 'cr3eq', 'cr3so'],
        'cr4_float': ['cr4lt', 'cr4gt', 'cr4eq', 'cr4so'],
        'cr5_float': ['cr5lt', 'cr5gt', 'cr5eq', 'cr5so'],
        'cr6_float': ['cr6lt', 'cr6gt', 'cr6eq', 'cr6so'],
        'cr7_float': ['cr7lt', 'cr7gt', 'cr7eq', 'cr7so'],
        'xer': ['xer_so', 'xer_ov', 'xer_ca'],
        'xer_ca': ['xer_ca'],
        'xer_ov_so': ['xer_so', 'xer_ov'],
        'mtcr0': ['lt', 'gt', 'eq', 'so'],
        'mtcr1': ['cr1lt', 'cr1gt', 'cr1eq', 'cr1so'],
        'mtcr2': ['cr2lt', 'cr2gt', 'cr2eq', 'cr2so'],
        'mtcr3': ['cr3lt', 'cr3gt', 'cr3eq', 'cr3so'],
        'mtcr4': ['cr4lt', 'cr4gt', 'cr4eq', 'cr4so'],
        'mtcr5': ['cr5lt', 'cr5gt', 'cr5eq', 'cr5so'],
        'mtcr6': ['cr6lt', 'cr6gt', 'cr6eq', 'cr6so'],
        'mtcr7': ['cr7lt', 'cr7gt', 'cr7eq', 'cr7so'],
        'invl0': ['lt', 'gt', 'eq', 'so'],
        'invl1': ['cr1lt', 'cr1gt', 'cr1eq', 'cr1so'],
        'invl2': ['cr2lt', 'cr2gt', 'cr2eq', 'cr2so'],
        'invl3': ['cr3lt', 'cr3gt', 'cr3eq', 'cr3so'],
        'invl4': ['cr4lt', 'cr4gt', 'cr4eq', 'cr4so'],
        'invl5': ['cr5lt', 'cr5gt', 'cr5eq', 'cr5so'],
        'invl6': ['cr6lt', 'cr6gt', 'cr6eq', 'cr6so'],
        'invl7': ['cr7lt', 'cr7gt', 'cr7eq', 'cr7so'],
        'invall': [
            'lt', 'gt', 'eq', 'so',
            'cr1lt', 'cr1gt', 'cr1eq', 'cr1so',
            'cr2lt', 'cr2gt', 'cr2eq', 'cr2so',
            'cr3lt', 'cr3gt', 'cr3eq', 'cr3so',
            'cr4lt', 'cr4gt', 'cr4eq', 'cr4so',
            'cr5lt', 'cr5gt', 'cr5eq', 'cr5so',
            'cr6lt', 'cr6gt', 'cr6eq', 'cr6so',
            'cr7lt', 'cr7gt', 'cr7eq', 'cr7so',
            'xer_so', 'xer_ov', 'xer_ca'
        ]
    }

    def get_instruction_info(self, data: bytes, addr: int) -> InstructionInfo | None:
        return Decoder.get_instruction_info(data, addr, categories=("VLE", ))

    def get_instruction_text(self, data: bytes, addr: int) -> Tuple[List[InstructionTextToken], int] | None:
        return Decoder.get_instruction_text(data, addr, categories=("VLE", ))
    
    def get_instruction_low_level_il(self, data: bytes, addr: int, il: LowLevelILFunction) -> int | None:
        return Decoder.get_instruction_low_level_il(data, addr, il, categories=("VLE", ))


PowerVLE.register()
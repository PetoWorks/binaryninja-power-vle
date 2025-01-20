from typing import Tuple, List

from binaryninja.architecture import Architecture, RegisterInfo, InstructionInfo
from binaryninja.function import InstructionTextToken
from binaryninja.lowlevelil import LowLevelILFunction
from binaryninja.enums import Endianness

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

    def get_instruction_info(self, data: bytes, addr: int) -> InstructionInfo | None:
        return Decoder.get_instruction_info(data, addr, categories=("VLE", ))

    def get_instruction_text(self, data: bytes, addr: int) -> Tuple[List[InstructionTextToken], int] | None:
        return Decoder.get_instruction_text(data, addr, categories=("VLE", ))
    
    def get_instruction_low_level_il(self, data: bytes, addr: int, il: LowLevelILFunction) -> int | None:
        return Decoder.get_instruction_low_level_il(data, addr, il, categories=("VLE", ))


PowerVLE.register()
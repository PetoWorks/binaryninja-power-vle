from typing import Tuple, List

from binaryninja import architecture, function, lowlevelil, enums
from binaryninja.log import log_warn

from .powervle.decoder import Decoder, PowerCategory
from .powervle.instruction import Instruction as PowerVLEInstr


def get_expr(
    il: lowlevelil.LowLevelILFunction, operand: lowlevelil.ILRegisterType, size: int
) -> lowlevelil.ExpressionIndex:

    if isinstance(operand, int):
        return il.const(size, operand)
    elif isinstance(operand, lowlevelil.ILRegister):
        return il.reg(size, operand)
    elif isinstance(operand, lowlevelil.ILFlag):
        return il.flag(operand)
    raise TypeError(f"invalid operand type. {type(operand)}, {operand}")


def get_expr_op(
    il: lowlevelil.LowLevelILFunction, op: lowlevelil.LowLevelILOperation,
    operands: list[lowlevelil.ILRegisterType], size: int
) -> lowlevelil.ExpressionIndex:

    if len(operands) == 0:
        return il.expr(op, size=size)

    elif len(operands) == 1:
        if op == lowlevelil.LowLevelILOperation.LLIL_SET_REG:
            return get_expr(operands[0], size)

    elif len(operands) <= 4:
        return il.expr(op, *[get_expr(il, opr, size) for opr in operands], size=size)
    
    else:
        raise ValueError


class PowerVLE(architecture.Architecture):
    name = "power-vle"
    endianness = enums.Endianness.BigEndian
    address_size = 4
    default_int_size = 4
    instr_alignment = 2
    max_instr_length = 4

    regs = {
        'lr': architecture.RegisterInfo("lr", 4, 0),
        'ctr': architecture.RegisterInfo("ctr", 4, 0),
        'r0': architecture.RegisterInfo("r0", 4, 0),
        'r1': architecture.RegisterInfo("r1", 4, 0),
        'r2': architecture.RegisterInfo("r2", 4, 0),
        'r3': architecture.RegisterInfo("r3", 4, 0),
        'r4': architecture.RegisterInfo("r4", 4, 0),
        'r5': architecture.RegisterInfo("r5", 4, 0),
        'r6': architecture.RegisterInfo("r6", 4, 0),
        'r7': architecture.RegisterInfo("r7", 4, 0),
        'r8': architecture.RegisterInfo("r8", 4, 0),
        'r9': architecture.RegisterInfo("r9", 4, 0),
        'r10': architecture.RegisterInfo("r10", 4, 0),
        'r11': architecture.RegisterInfo("r11", 4, 0),
        'r12': architecture.RegisterInfo("r12", 4, 0),
        'r13': architecture.RegisterInfo("r13", 4, 0),
        'r14': architecture.RegisterInfo("r14", 4, 0),
        'r15': architecture.RegisterInfo("r15", 4, 0),
        'r16': architecture.RegisterInfo("r16", 4, 0),
        'r17': architecture.RegisterInfo("r17", 4, 0),
        'r18': architecture.RegisterInfo("r18", 4, 0),
        'r19': architecture.RegisterInfo("r19", 4, 0),
        'r20': architecture.RegisterInfo("r20", 4, 0),
        'r21': architecture.RegisterInfo("r21", 4, 0),
        'r22': architecture.RegisterInfo("r22", 4, 0),
        'r23': architecture.RegisterInfo("r23", 4, 0),
        'r24': architecture.RegisterInfo("r24", 4, 0),
        'r25': architecture.RegisterInfo("r25", 4, 0),
        'r26': architecture.RegisterInfo("r26", 4, 0),
        'r27': architecture.RegisterInfo("r27", 4, 0),
        'r28': architecture.RegisterInfo("r28", 4, 0),
        'r29': architecture.RegisterInfo("r29", 4, 0),
        'r30': architecture.RegisterInfo("r30", 4, 0),
        'r31': architecture.RegisterInfo("r31", 4, 0),
    }

    stack_pointer = "r1"

    flags = [
        'cr0lt', 'cr0gt', 'cr0eq', 'cr0so',
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
        'cr0lt': enums.FlagRole.NegativeSignFlagRole,
        'cr0gt': enums.FlagRole.SpecialFlagRole,
        'cr0eq': enums.FlagRole.ZeroFlagRole,
        'cr0so': enums.FlagRole.SpecialFlagRole,
        'cr1lt': enums.FlagRole.NegativeSignFlagRole,
        'cr1gt': enums.FlagRole.SpecialFlagRole,
        'cr1eq': enums.FlagRole.ZeroFlagRole,
        'cr1so': enums.FlagRole.SpecialFlagRole,
        'cr2lt': enums.FlagRole.NegativeSignFlagRole,
        'cr2gt': enums.FlagRole.SpecialFlagRole,
        'cr2eq': enums.FlagRole.ZeroFlagRole,
        'cr2so': enums.FlagRole.SpecialFlagRole,
        'cr3lt': enums.FlagRole.NegativeSignFlagRole,
        'cr3gt': enums.FlagRole.SpecialFlagRole,
        'cr3eq': enums.FlagRole.ZeroFlagRole,
        'cr3so': enums.FlagRole.SpecialFlagRole,
        'cr4lt': enums.FlagRole.NegativeSignFlagRole,
        'cr4gt': enums.FlagRole.SpecialFlagRole,
        'cr4eq': enums.FlagRole.ZeroFlagRole,
        'cr4so': enums.FlagRole.SpecialFlagRole,
        'cr5lt': enums.FlagRole.NegativeSignFlagRole,
        'cr5gt': enums.FlagRole.SpecialFlagRole,
        'cr5eq': enums.FlagRole.ZeroFlagRole,
        'cr5so': enums.FlagRole.SpecialFlagRole,
        'cr6lt': enums.FlagRole.NegativeSignFlagRole,
        'cr6gt': enums.FlagRole.SpecialFlagRole,
        'cr6eq': enums.FlagRole.ZeroFlagRole,
        'cr6so': enums.FlagRole.SpecialFlagRole,
        'cr7lt': enums.FlagRole.NegativeSignFlagRole,
        'cr7gt': enums.FlagRole.SpecialFlagRole,
        'cr7eq': enums.FlagRole.ZeroFlagRole,
        'cr7so': enums.FlagRole.SpecialFlagRole,
        'xer_so': enums.FlagRole.SpecialFlagRole,
        'xer_ov': enums.FlagRole.OverflowFlagRole,
        'xer_ca': enums.FlagRole.CarryFlagRole
    }

    flag_write_types = [
        'none',
        'cr0s', 'cr1s', 'cr2s', 'cr3s', 'cr4s', 'cr5s', 'cr6s', 'cr7s',
        'cr0u', 'cr1u', 'cr2u', 'cr3u', 'cr4u', 'cr5u', 'cr6u', 'cr7u',
        'cr0f', 'cr1f', 'cr2f', 'cr3f', 'cr4f', 'cr5f', 'cr6f', 'cr7f',
        'xer', 'xer_ca', 'xer_ov_so',
        'mtcr0', 'mtcr1', 'mtcr2', 'mtcr3', 'mtcr4', 'mtcr5', 'mtcr6', 'mtcr7',
        'invl0', 'invl1', 'invl2', 'invl3', 'invl4', 'invl5', 'invl6', 'invl7', 'invall'
    ]

    flags_written_by_flag_write_type = {
        'none': [],

        'cr0s': ['cr0lt', 'cr0gt', 'cr0eq', 'cr0so'], 'cr1s': ['cr1lt', 'cr1gt', 'cr1eq', 'cr1so'],
        'cr2s': ['cr2lt', 'cr2gt', 'cr2eq', 'cr2so'], 'cr3s': ['cr3lt', 'cr3gt', 'cr3eq', 'cr3so'],
        'cr4s': ['cr4lt', 'cr4gt', 'cr4eq', 'cr4so'], 'cr5s': ['cr5lt', 'cr5gt', 'cr5eq', 'cr5so'],
        'cr6s': ['cr6lt', 'cr6gt', 'cr6eq', 'cr6so'], 'cr7s': ['cr7lt', 'cr7gt', 'cr7eq', 'cr7so'],

        'cr0u': ['cr0lt', 'cr0gt', 'cr0eq', 'cr0so'], 'cr1u': ['cr1lt', 'cr1gt', 'cr1eq', 'cr1so'],
        'cr2u': ['cr2lt', 'cr2gt', 'cr2eq', 'cr2so'], 'cr3u': ['cr3lt', 'cr3gt', 'cr3eq', 'cr3so'],
        'cr4u': ['cr4lt', 'cr4gt', 'cr4eq', 'cr4so'], 'cr5u': ['cr5lt', 'cr5gt', 'cr5eq', 'cr5so'],
        'cr6u': ['cr6lt', 'cr6gt', 'cr6eq', 'cr6so'], 'cr7u': ['cr7lt', 'cr7gt', 'cr7eq', 'cr7so'],

        'cr0f': ['cr0lt', 'cr0gt', 'cr0eq', 'cr0so'], 'cr1f': ['cr1lt', 'cr1gt', 'cr1eq', 'cr1so'],
        'cr2f': ['cr2lt', 'cr2gt', 'cr2eq', 'cr2so'], 'cr3f': ['cr3lt', 'cr3gt', 'cr3eq', 'cr3so'],
        'cr4f': ['cr4lt', 'cr4gt', 'cr4eq', 'cr4so'], 'cr5f': ['cr5lt', 'cr5gt', 'cr5eq', 'cr5so'],
        'cr6f': ['cr6lt', 'cr6gt', 'cr6eq', 'cr6so'], 'cr7f': ['cr7lt', 'cr7gt', 'cr7eq', 'cr7so'],

        'xer': ['xer_so', 'xer_ov', 'xer_ca'],
        'xer_ca': ['xer_ca'],
        'xer_ov_so': ['xer_so', 'xer_ov'],

        'mtcr0': ['cr0lt', 'cr0gt', 'cr0eq', 'cr0so'], 'mtcr1': ['cr1lt', 'cr1gt', 'cr1eq', 'cr1so'],
        'mtcr2': ['cr2lt', 'cr2gt', 'cr2eq', 'cr2so'], 'mtcr3': ['cr3lt', 'cr3gt', 'cr3eq', 'cr3so'],
        'mtcr4': ['cr4lt', 'cr4gt', 'cr4eq', 'cr4so'], 'mtcr5': ['cr5lt', 'cr5gt', 'cr5eq', 'cr5so'],
        'mtcr6': ['cr6lt', 'cr6gt', 'cr6eq', 'cr6so'], 'mtcr7': ['cr7lt', 'cr7gt', 'cr7eq', 'cr7so'],

        'invl0': ['cr0lt', 'cr0gt', 'cr0eq', 'cr0so'], 'invl1': ['cr1lt', 'cr1gt', 'cr1eq', 'cr1so'],
        'invl2': ['cr2lt', 'cr2gt', 'cr2eq', 'cr2so'], 'invl3': ['cr3lt', 'cr3gt', 'cr3eq', 'cr3so'],
        'invl4': ['cr4lt', 'cr4gt', 'cr4eq', 'cr4so'], 'invl5': ['cr5lt', 'cr5gt', 'cr5eq', 'cr5so'],
        'invl6': ['cr6lt', 'cr6gt', 'cr6eq', 'cr6so'], 'invl7': ['cr7lt', 'cr7gt', 'cr7eq', 'cr7so'],
        'invall': [
            'cr0lt', 'cr0gt', 'cr0eq', 'cr0so', 'cr1lt', 'cr1gt', 'cr1eq', 'cr1so',
            'cr2lt', 'cr2gt', 'cr2eq', 'cr2so', 'cr3lt', 'cr3gt', 'cr3eq', 'cr3so',
            'cr4lt', 'cr4gt', 'cr4eq', 'cr4so', 'cr5lt', 'cr5gt', 'cr5eq', 'cr5so',
            'cr6lt', 'cr6gt', 'cr6eq', 'cr6so', 'cr7lt', 'cr7gt', 'cr7eq', 'cr7so',
            'xer_so', 'xer_ov', 'xer_ca'
        ]
    }

    categories = PowerCategory.VLE

    def __init__(self):
        super().__init__()
        self.decoder = Decoder(self.categories)

    @classmethod
    def extend(cls, name: str, categories: PowerCategory):
        cat = PowerCategory.VLE & categories
        return type(f"PowerVLE_{name}", (PowerVLE, ), {'name': name, 'categories': cat})

    def decode(self, data: bytes) -> PowerVLEInstr | None:
        return self.decoder.decode(data)

    def get_instruction_info(self, data: bytes, addr: int) -> architecture.InstructionInfo | None:
        instruction = self.decode(data)
        if instruction:
            info = architecture.InstructionInfo()
            info.length = instruction.length
            if instruction.name == "...": # add branch here!
                info.add_branch(...)
            return info

    def get_instruction_text(self, data: bytes, addr: int) -> Tuple[List[architecture.InstructionTextToken], int] | None:

        instruction = self.decode(data)
        if not instruction:
            return

        tokens = []

        mnemonic = instruction.name
        if instruction.rc:
            mnemonic += "." if instruction.get("Rc") != 0 else ""

        tokens.append(architecture.InstructionTextToken(enums.InstructionTextTokenType.OpcodeToken, mnemonic))

        for operand in instruction.operands:
            if operand == "":
                ...
                tokens.append(...)
            elif operand == "":
                ...
                tokens.append(...)
            else:
                log_warn(...)
                return
        
        return tokens

    def get_instruction_low_level_il(self, data: bytes, addr: int, il: lowlevelil.LowLevelILFunction) -> int | None:
        ...

    def get_flag_write_low_level_il(
        self, op: lowlevelil.LowLevelILOperation, size: int, write_type: architecture.FlagWriteTypeName,
        flag: architecture.FlagType, operands: list[lowlevelil.ILRegisterType], il: lowlevelil.LowLevelILFunction
    ) -> lowlevelil.ExpressionIndex:

        if write_type.startswith("mtcr"):
            return il.unimplemented() # TODO

        if write_type.startswith("inv"):
            return il.unimplemented()

        if write_type.startswith("cr"):
            cond = write_type[-2:]
            suf = write_type[-1]
            fn = None

            if cond == "lt":
                if suf == "s":
                    fn = il.compare_signed_less_than
                elif suf == "u":
                    fn = il.compare_unsigned_less_than
                elif suf == "f":
                    fn = il.float_compare_less_than
            
            elif cond == "gt":
                if suf == "s":
                    fn = il.compare_signed_greater_than
                elif suf == "u":
                    fn = il.compare_unsigned_greater_than
                elif suf == "f":
                    fn = il.float_compare_greater_than
            
            elif cond == "eq":
                if suf == "s" or suf == "u":
                    fn = il.compare_equal
                elif suf == "f":
                    fn = il.float_compare_equal
            
            if fn:
                left = get_expr_op(il, op, operands, size)
                write = il.const(size, 0)
                return fn(size, left, write)

        return super().get_flag_write_low_level_il(op, size, write_type, flag, operands, il)


PowerVLE.register()
# PowerVLE.extend("power-vle-extended", ...)
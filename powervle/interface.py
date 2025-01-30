from typing import Tuple, List

from binaryninja.log import log_warn, log_error, log_debug

from binaryninja.architecture import (
    FlagType, FlagWriteTypeName,
    Architecture, Endianness, RegisterInfo,
    InstructionInfo, InstructionTextToken
)

from binaryninja.lowlevelil import (
    ILRegisterType, ExpressionIndex,
    LowLevelILFunction, ILRegister, ILFlag,
    LowLevelILOperation
)

from binaryninja.enums import (
    FlagRole, InstructionTextTokenType, BranchType
)

from .decoder import Decoder, PowerCategory
from .lowlevelil import InstLiftTable
from .utils import *


def get_expr(il: LowLevelILFunction, operand: ILRegisterType, size: int) -> ExpressionIndex:
    if isinstance(operand, int):
        return il.const(size, operand)
    elif isinstance(operand, ILRegister):
        return il.reg(size, operand)
    elif isinstance(operand, ILFlag):
        return il.flag(operand)
    raise TypeError(f"invalid operand type. {type(operand)}, {operand}")


def get_expr_op(
    il: LowLevelILFunction, op: LowLevelILOperation, operands: list[ILRegisterType], size: int
) -> ExpressionIndex:

    if len(operands) == 0:
        return il.expr(op, size=size)

    elif len(operands) == 1:
        if op == LowLevelILOperation.LLIL_SET_REG:
            return get_expr(operands[0], size)

    elif len(operands) <= 4:
        return il.expr(op, *[get_expr(il, opr, size) for opr in operands], size=size)
    
    else:
        raise ValueError


class PowerVLE(Architecture):
    name = "power-vle"
    endianness = Endianness.BigEndian
    address_size = 4
    default_int_size = 4
    instr_alignment = 2
    max_instr_length = 4

    regs = {
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
        'cr0lt': FlagRole.NegativeSignFlagRole,
        'cr0gt': FlagRole.SpecialFlagRole,
        'cr0eq': FlagRole.ZeroFlagRole,
        'cr0so': FlagRole.SpecialFlagRole,
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
        self.decode = Decoder(self.categories)

    @classmethod
    def extend(cls, name: str, categories: PowerCategory):
        cat = PowerCategory.VLE & categories
        return type(f"PowerVLE_{name}", (PowerVLE, ), {'name': name, 'categories': cat})

    def get_instruction_info(self, data: bytes, addr: int) -> InstructionInfo | None:

        info = InstructionInfo()

        instruction = self.decode(data, addr)
        if not instruction:
            info.length = 4
            return info

        info.length = instruction.length

        if instruction.branch:

            if "NIA" in instruction.operands:
                nia = instruction.NIA
                if nia != (addr + instruction.length):
                    info.add_branch(BranchType.CallDestination if instruction.LK else BranchType.UnconditionalBranch, nia)
                    return info
            
            elif not instruction.LK:

                if instruction.name == "se_blr":
                    info.add_branch(BranchType.FunctionReturn)
                    return info
                
                elif instruction.name == "se_bctr":
                    info.add_branch(BranchType.IndirectBranch)
                    return info

            info.add_branch(BranchType.UnresolvedBranch)
            return info
        
        elif instruction.conditional_branch:
            nia = instruction.NIA
            if nia != (addr + instruction.length):
                info.add_branch(BranchType.TrueBranch, nia)
                info.add_branch(BranchType.FalseBranch, addr + instruction.length)
                return info
        
        return info

    def get_instruction_text(self, data: bytes, addr: int) -> Tuple[List[InstructionTextToken], int] | None:

        instruction = self.decode(data, addr)
        if not instruction:
            return [InstructionTextToken(InstructionTextTokenType.TextToken, "#UNAVAILABLE")], 4

        tokens = []

        mnemonic = instruction.mnemonic
        tokens.append(InstructionTextToken(InstructionTextTokenType.InstructionToken, mnemonic))

        skipped = 0
        for index, operand in enumerate(instruction.operands):

            if operand in ("Rc", "LK"):
                skipped += 1
                continue

            if (index - skipped) == 0:
                tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, " " * (12 - len(mnemonic))))
            else:
                tokens.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "))

            if operand in ("RA", "RT", "RS"):
                regnum = instruction.get(operand)
                token = (InstructionTextTokenType.RegisterToken, f"r{regnum}")

            elif operand in ("ARX", "ARY"):
                regnum = 8 + instruction.get(operand)
                token = (InstructionTextTokenType.RegisterToken, f"r{regnum}")

            elif operand in ("RX", "RY", "RZ"):
                value = instruction.get(operand)
                if value < 0b1000:
                    regnum = value
                else:
                    regnum = 24 + (value & 0b111)
                token = (InstructionTextTokenType.RegisterToken, f"r{regnum}")

            elif operand == "BF32":
                token = (InstructionTextTokenType.RegisterToken, f"cr{instruction.BF32}")

            elif operand == "NIA":
                token = (InstructionTextTokenType.CodeRelativeAddressToken, hex(instruction.NIA), instruction.NIA)

            else:
                opr = instruction.get(operand)
                if opr == None:
                    log_warn(f"There are unimplemented field: {mnemonic} {operand}")
                    log_debug(f"{instruction.name} {instruction.fields}")
                    token = (InstructionTextTokenType.TextToken, "#UNAVAILABLE")
                else:
                    token = (InstructionTextTokenType.IntegerToken, hex(opr), opr)

            tokens.append(InstructionTextToken(*token))

        return tokens, instruction.length

    def get_instruction_low_level_il(self, data: bytes, addr: int, il: LowLevelILFunction) -> int | None:

        instruction = self.decode(data, addr)
        if not instruction:
            return 4

        if instruction.name in InstLiftTable and InstLiftTable[instruction.name]:
            InstLiftTable[instruction.name](instruction, il)
        else:
            il.unimplemented()

        return instruction.length

    def get_flag_write_low_level_il(
        self, op: LowLevelILOperation, size: int, write_type: FlagWriteTypeName,
        flag: FlagType, operands: list[ILRegisterType], il: LowLevelILFunction
    ) -> ExpressionIndex:

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

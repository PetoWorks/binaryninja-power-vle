from typing import Tuple, List
from binaryninja import LowLevelILOperation
from binaryninja import Intrinsic, IntrinsicInfo, Type
from binaryninja.log import log_warn, log_error, log_debug, log_info

from binaryninja.architecture import (
    FlagType, FlagWriteTypeName,
    Architecture, Endianness, RegisterInfo,
    InstructionInfo, InstructionTextToken
)

from binaryninja.callingconvention import (
    CallingConvention
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
            return get_expr(il, operands[0], size)

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
        # spr
        'cr'    : RegisterInfo("cr", 4, 0),

        'xer'   : RegisterInfo("xer", 4, 0),
        'lr'    : RegisterInfo("lr", 4, 0),
        'ctr'   : RegisterInfo("ctr", 4, 0),

        'srr0'  : RegisterInfo("srr0", 4, 0), 
        'srr1'  : RegisterInfo("srr1", 4, 0),
        'pid'   : RegisterInfo("pid", 4, 0),

        'csrr0' : RegisterInfo("csrr0", 4, 0), 
        'csrr1' : RegisterInfo("csrr1", 4, 0),
        'dsrr0' : RegisterInfo("dsrr0", 4, 0), 
        'dsrr1' : RegisterInfo("dsrr1", 4, 0),
        'mcsrr0': RegisterInfo("mcsrr0", 4, 0), 
        'mcsrr1': RegisterInfo("mcsrr1", 4, 0),

        'msr'   : RegisterInfo("msr", 4, 0),
        'esr'   : RegisterInfo("esr", 4, 0),
        'ivpr'  : RegisterInfo("ivpr", 4, 0),
        'ppr'   : RegisterInfo("ppr", 4, 0),
        'sprg0' : RegisterInfo("sprg0", 4, 0),
        'sprg1' : RegisterInfo("sprg1", 4, 0),
        'dbcr0' : RegisterInfo("dbcr0", 4, 0),
        'ivor0' : RegisterInfo("ivor0", 4, 0),
        'ivor1' : RegisterInfo("ivor1", 4, 0),
        'ivor2' : RegisterInfo("ivor2", 4, 0),
        'ivor3' : RegisterInfo("ivor3", 4, 0),
        'ivor4' : RegisterInfo("ivor4", 4, 0),
        'ivor5' : RegisterInfo("ivor5", 4, 0),
        'ivor6' : RegisterInfo("ivor6", 4, 0),
        'ivor7' : RegisterInfo("ivor7", 4, 0),
        'ivor8' : RegisterInfo("ivor8", 4, 0),
        'ivor9' : RegisterInfo("ivor9", 4, 0),
        'ivor10': RegisterInfo("ivor10", 4, 0),
        'ivor11': RegisterInfo("ivor11", 4, 0),
        'ivor12': RegisterInfo("ivor12", 4, 0),
        'ivor13': RegisterInfo("ivor13", 4, 0),
        'ivor14': RegisterInfo("ivor14", 4, 0),
        'ivor15': RegisterInfo("ivor15", 4, 0),
        'ivor33': RegisterInfo("ivor33", 4, 0),
        'ivor34': RegisterInfo("ivor34", 4, 0),
        'ivor35': RegisterInfo("ivor35", 4, 0),
        'iac8'  : RegisterInfo("iac8", 4, 0),
        'svr'   : RegisterInfo("svr", 4, 0),

        # gpr
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

        # Vector Registers
        'v0': RegisterInfo("v0", 16, 0),
        'v1': RegisterInfo("v1", 16, 0),
        'v2': RegisterInfo("v2", 16, 0),
        'v3': RegisterInfo("v3", 16, 0),
        'v4': RegisterInfo("v4", 16, 0),
        'v5': RegisterInfo("v5", 16, 0),
        'v6': RegisterInfo("v6", 16, 0),
        'v7': RegisterInfo("v7", 16, 0),
        'v8': RegisterInfo("v8", 16, 0),
        'v9': RegisterInfo("v9", 16, 0),
        'v10': RegisterInfo("v10", 16, 0),
        'v11': RegisterInfo("v11", 16, 0),
        'v12': RegisterInfo("v12", 16, 0),
        'v13': RegisterInfo("v13", 16, 0),
        'v14': RegisterInfo("v14", 16, 0),
        'v15': RegisterInfo("v15", 16, 0),
        'v16': RegisterInfo("v16", 16, 0),
        'v17': RegisterInfo("v17", 16, 0),
        'v18': RegisterInfo("v18", 16, 0),
        'v19': RegisterInfo("v19", 16, 0),
        'v20': RegisterInfo("v20", 16, 0),
        'v21': RegisterInfo("v21", 16, 0),
        'v22': RegisterInfo("v22", 16, 0),
        'v23': RegisterInfo("v23", 16, 0),
        'v24': RegisterInfo("v24", 16, 0),
        'v25': RegisterInfo("v25", 16, 0),
        'v26': RegisterInfo("v26", 16, 0),
        'v27': RegisterInfo("v27", 16, 0),
        'v28': RegisterInfo("v28", 16, 0),
        'v29': RegisterInfo("v29", 16, 0),
        'v30': RegisterInfo("v30", 16, 0),
        'v31': RegisterInfo("v31", 16, 0),
        'vscr'  : RegisterInfo("vscr", 4, 0),
        'vrsave': RegisterInfo("vrsave", 4, 0),

        # SP Category
        'acc'       : RegisterInfo("acc", 4, 0),
        'spefscr'   : RegisterInfo("spefscr", 4, 0),   # Special Register
        
        # E.CD Category - Special Register
        'dcdbtrh'   : RegisterInfo("dcdbtrh", 4, 0),
        'dcdbtrl'   : RegisterInfo("dcdbtrl", 4, 0),
        'icdbdr'    : RegisterInfo("icdbdr", 4, 0),
        'icdbtrh'   : RegisterInfo("icdbtrh", 4, 0),
        'icdbtrl'   : RegisterInfo("icdbtrl", 4, 0),

        # E.PM Category
        'pmgc0': RegisterInfo("pmgc0", 4, 0),

        'pmlca0' : RegisterInfo("pmlca0", 4, 0),  'pmlca1' : RegisterInfo("pmlca1", 4, 0),
        'pmlca2' : RegisterInfo("pmlca2", 4, 0),  'pmlca3' : RegisterInfo("pmlca3", 4, 0),
        'pmlca4' : RegisterInfo("pmlca4", 4, 0),  'pmlca5' : RegisterInfo("pmlca5", 4, 0),
        'pmlca6' : RegisterInfo("pmlca6", 4, 0),  'pmlca7' : RegisterInfo("pmlca7", 4, 0),
        'pmlca8' : RegisterInfo("pmlca8", 4, 0),  'pmlca9' : RegisterInfo("pmlca9", 4, 0),
        'pmlca10': RegisterInfo("pmlca10", 4, 0), 'pmlca11': RegisterInfo("pmlca11", 4, 0),
        'pmlca12': RegisterInfo("pmlca12", 4, 0), 'pmlca13': RegisterInfo("pmlca13", 4, 0),
        'pmlca14': RegisterInfo("pmlca14", 4, 0), 'pmlca15': RegisterInfo("pmlca15", 4, 0),

        'pmlcb0' : RegisterInfo("pmlcb0", 4, 0),  'pmlcb1' : RegisterInfo("pmlcb1", 4, 0),
        'pmlcb2' : RegisterInfo("pmlcb2", 4, 0),  'pmlcb3' : RegisterInfo("pmlcb3", 4, 0),
        'pmlcb4' : RegisterInfo("pmlcb4", 4, 0),  'pmlcb5' : RegisterInfo("pmlcb5", 4, 0),
        'pmlcb6' : RegisterInfo("pmlcb6", 4, 0),  'pmlcb7' : RegisterInfo("pmlcb7", 4, 0),
        'pmlcb8' : RegisterInfo("pmlcb8", 4, 0),  'pmlcb9' : RegisterInfo("pmlcb9", 4, 0),
        'pmlcb10': RegisterInfo("pmlcb10", 4, 0), 'pmlcb11': RegisterInfo("pmlcb11", 4, 0),
        'pmlcb12': RegisterInfo("pmlcb12", 4, 0), 'pmlcb13': RegisterInfo("pmlcb13", 4, 0),
        'pmlcb14': RegisterInfo("pmlcb14", 4, 0), 'pmlcb15': RegisterInfo("pmlcb15", 4, 0),

        'pmc0' : RegisterInfo("pmc0", 4, 0),  'pmc1' : RegisterInfo("pmc1", 4, 0),
        'pmc2' : RegisterInfo("pmc2", 4, 0),  'pmc3' : RegisterInfo("pmc3", 4, 0),
        'pmc4' : RegisterInfo("pmc4", 4, 0),  'pmc5' : RegisterInfo("pmc5", 4, 0),
        'pmc6' : RegisterInfo("pmc6", 4, 0),  'pmc7' : RegisterInfo("pmc7", 4, 0),
        'pmc8' : RegisterInfo("pmc8", 4, 0),  'pmc9' : RegisterInfo("pmc9", 4, 0),
        'pmc10': RegisterInfo("pmc10", 4, 0), 'pmc11': RegisterInfo("pmc11", 4, 0),
        'pmc12': RegisterInfo("pmc12", 4, 0), 'pmc13': RegisterInfo("pmc13", 4, 0),
        'pmc14': RegisterInfo("pmc14", 4, 0), 'pmc15': RegisterInfo("pmc15", 4, 0),
    }

    stack_pointer = "r1"
    link_reg = "lr"

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
        'xer_ca': FlagRole.CarryFlagRole,
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

    intrinsics = {
        'isync' : IntrinsicInfo([], []),
        'rfi'   : IntrinsicInfo([], []),
        'rfci'  : IntrinsicInfo([], []),
        'rfdi'  : IntrinsicInfo([], []),
        'rfmci' : IntrinsicInfo([], []),
        'sync'  : IntrinsicInfo([], []),
        'wait'  : IntrinsicInfo([], []),
        'cntlzw'  : IntrinsicInfo([], []),
    }

    categories = [PowerCategory.VLE, PowerCategory.B, PowerCategory.SP,
                  PowerCategory.E, PowerCategory.E_CD, PowerCategory.E_CI,
                  PowerCategory.E_CL, PowerCategory.E_PD, PowerCategory.E_PC,
                  PowerCategory.E_PM, PowerCategory.MA, PowerCategory.WT]

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
            info.length = 2
            return info

        info.length = instruction.length

        if not (instruction.branch or instruction.conditional_branch):
            return info

        target_addr = instruction.get_operand_value("target_addr")
        link = instruction.get_operand_value("LK")

        if target_addr == None:

            if link == 0:
                if instruction.name == "se_blr":
                    info.add_branch(BranchType.FunctionReturn)
                elif instruction.name == "se_bctr":
                    info.add_branch(BranchType.IndirectBranch)
                return info

            info.add_branch(BranchType.UnresolvedBranch)
            return info
        
        if target_addr == (addr + instruction.length):
            return info
        
        if instruction.branch:
            if link:
                info.add_branch(BranchType.CallDestination, target_addr)
            else:
                info.add_branch(BranchType.UnconditionalBranch, target_addr)
        
        elif instruction.conditional_branch:
            if link:
                info.add_branch(BranchType.UnresolvedBranch, target_addr)
            else:
                info.add_branch(BranchType.TrueBranch, target_addr)
                info.add_branch(BranchType.FalseBranch, addr + instruction.length)

        return info

    def get_instruction_text(self, data: bytes, addr: int) -> Tuple[List[InstructionTextToken], int] | None:

        instruction = self.decode(data, addr)
        if not instruction:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, "undef")], 2

        tokens = []
        skip_operands = []

        mnemonic = instruction.mnemonic

        if mnemonic in ["mtspr", "mfspr"]:
            spr_extended_mnemonics = ["xer", "lr", "ctr", "srr0", "srr1", "pid"]
            
            for index, name in enumerate(instruction.operands):
                if name == "SPR":
                    spr = instruction.get_operand_value(name)
                    log_info(f"spr: {spr}")
                    if spr in spr_extended_mnemonics:
                        mnemonic = mnemonic[:2] + spr
                        log_info(f"extended mnenonic: {mnemonic}")
                        skip_operands.append(index)
                    break
        
        if mnemonic == "mtcrf":
            fxm = instruction.get_operand_value(instruction.operands[0])
            if fxm == 0b11111111:
                mnemonic = mnemonic[:-1]
                skip_operands.append(0)
                
        tokens.append(InstructionTextToken(InstructionTextTokenType.InstructionToken, mnemonic))
        
        actual_index = 0
        for index, name in enumerate(instruction.operands):
            if (name in ("Rc", "LK", "OE")) or (index in skip_operands):
                continue

            if actual_index == 0:
                tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, " " * (10 - len(mnemonic))))
            else:
                tokens.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "))

            actual_index += 1

            operand = instruction.get_operand_value(name)
            if operand == None:
                log_warn(f"instruction {instruction.name} has invalid operand {name}")
                token = (InstructionTextTokenType.TextToken, f"#INVALID({name})")
            elif name == "target_addr":
                token = (InstructionTextTokenType.CodeRelativeAddressToken, hex(operand), operand)
            elif type(operand) == str:
                token = (InstructionTextTokenType.RegisterToken, operand)
            else:
                token = (InstructionTextTokenType.IntegerToken, hex(operand), operand)

            tokens.append(InstructionTextToken(*token))

        return tokens, instruction.length

    def get_instruction_low_level_il(self, data: bytes, addr: int, il: LowLevelILFunction) -> int | None:

        instruction = self.decode(data, addr)
        if not instruction:
            il.append(il.unimplemented())
            return 4

        if instruction.name in InstLiftTable and InstLiftTable[instruction.name]:
            InstLiftTable[instruction.name](instruction, il)
        else:
            il.append(il.unimplemented())

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
            cond = flag[-2:]
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
                right = il.const(size, 0)
                return fn(size, left, right)
            
        if flag == "xer_ca":
            if op == LowLevelILOperation.LLIL_ASR:

                if isinstance(operands[1], int):
                    mask = (1 << operands[1]) - 1
                    if ~mask:
                        return il.const(0, 0)
                    maskExpr = il.const(size, mask)
                else:
                    maskExpr = get_expr(il, operands[1], size)
                    maskExpr = il.sub(size, 
                        il.shift_left(size,
                            il.const(size, 1),
                            maskExpr),
                        il.const(size, 1)
                   )
                return il.and_expr(0,
                    il.compare_signed_less_than(size,
                        il.get_expr(il, operands[0], size),
                        il.const(size, 0)
                    ),
                    il.compare_not_equal(size,
                        il.and_expr(size,
                            il.get_expr(il, operands[0], size),
                            maskExpr),
                        il.const(size, 0)
                    )
                )

        return super().get_flag_write_low_level_il(op, size, write_type, flag, operands, il)

class DefaultCallingConvention(CallingConvention):
    name = 'default'
    # dedicated: r1, r2, r13

    # Nonvolatile registers
    callee_saved_regs = ['r14', 'r15', 'r16', 'r17', 'r18', 'r19', 'r20', 'r21', 'r22',
                         'r23', 'r24', 'r25', 'r26', 'r27', 'r28', 'r29', 'r30', 'r31']
    # Volatile registers
    caller_saved_regs = ['r0', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'lr', 'ctr']
 
    int_arg_regs = ['r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10']
    
    int_return_reg = 'r3'

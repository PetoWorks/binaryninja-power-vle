from typing import Callable

from binaryninja.lowlevelil import LowLevelILFunction

from ..instruction import Instruction
from .branch import( 
    lift_bd24_branch_instructions,
    lift_bd8_branch_instructions,
    lift_bd15_branch_instructions,
    lift_bd8_cond_branch_instructions,
    lift_branch_instructions,
    lift_branch_lr_instructions
)

from .cond_register import(
    lift_cr_instructions,
    lift_move_cr_instruction
)

InstLiftFuncType = Callable[[Instruction, LowLevelILFunction], None] 

InstLiftTable: dict[str, InstLiftFuncType] = {
    
    "se_isync"   : lambda inst, il: il.append(il.intrinsic([], "isync", [])),
    # Chatper 4.2 Instructions
    "se_blr"     : lift_branch_instructions,
    "se_bctr"    : lift_branch_instructions,
    "e_b"        : lift_bd24_branch_instructions,
    "e_bl"       : lift_bd24_branch_instructions,
    "se_b"       : lift_bd8_branch_instructions,
    "se_bl"      : lift_bd8_branch_instructions,
    "e_bc"       : lift_bd15_branch_instructions,
    "e_bcl"      : lift_bd15_branch_instructions,
    "se_bc"      : lift_bd8_cond_branch_instructions,
    "se_bctr"    : lift_branch_instructions,
    "se_bctrl"   : lift_branch_instructions,
    "se_blr"     : lift_branch_lr_instructions,
    "se_blrl"    : lift_branch_lr_instructions,
    # Chapter 4.3 Instructions
    "se_sc"      : lambda inst, il: il.append(il.system_call()),
    "se_illegal" : lambda inst, il: il.append(il.undefined()),
    "se_rfmci"   : lambda inst, il: il.append(il.intrinsic([], "rfmci", [])),
    "se_rfci"    : lambda inst, il: il.append(il.intrinsic([], "rfci", [])),
    "se_rfi"     : lambda inst, il: il.append(il.intrinsic([], "rfi", [])),
    "se_rfdi"    : lambda inst, il: il.append(il.intrinsic([], "rfdi", [])),
    #Chapter 4.4 Condition Register Instructions
    "e_crand"    : lift_cr_instructions,
    "e_crandc"   : lift_cr_instructions,
    "e_creqv"    : lift_cr_instructions,
    "e_crnand"   : lift_cr_instructions,
    "e_crnor"    : lift_cr_instructions,
    "e_cror"     : lift_cr_instructions,
    "e_crorc"    : lift_cr_instructions,
    "e_crxor"    : lift_cr_instructions,
    "e_mcrf"     : lift_move_cr_instruction
}
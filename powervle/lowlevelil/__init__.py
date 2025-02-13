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
}
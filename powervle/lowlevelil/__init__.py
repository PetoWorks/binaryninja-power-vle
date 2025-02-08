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
from .system_linkage import(
    lift_system_call, 
    lift_illegal_instruction,
    lift_machine_check_return,
    lift_critical_return, 
    lift_return_from_interrupt, 
    lift_debug_return
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
    "se_sc"      : lift_system_call,
    "se_illegal" : lift_illegal_instruction,
    "se_rfmci"   : lift_machine_check_return,
    "se_rfci"    : lift_critical_return,
    "se_rfi"     : lift_return_from_interrupt,
    "se_rfdi"    : lift_debug_return,
}
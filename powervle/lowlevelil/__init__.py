from typing import Callable

from binaryninja.lowlevelil import LowLevelILFunction

from ..instruction import Instruction
from .branch import lift_branch_instructions

InstLiftFuncType = Callable[[Instruction, LowLevelILFunction], None]

InstLiftTable: dict[str, InstLiftFuncType] = {
    "se_illegal" : lambda inst, il: il.append(il.undefined()),
    "se_isync"   : lambda inst, il: il.append(il.intrinsic([], "isync", [])),
    "se_sc"      : lambda inst, il: il.append(il.system_call()),
    "se_blr"     : lift_branch_instructions,
    "se_bctr"    : lift_branch_instructions,
    "se_rfi"     : lambda inst, il: il.append(il.ret(il.unimplemented())),
    "se_rfci"    : None,
    "se_rfdi"    : None,
    "se_rfmci"   : None,
}
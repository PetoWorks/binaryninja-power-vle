from typing import Callable

from binaryninja.lowlevelil import LowLevelILFunction

from ..instruction import Instruction
from .branch import lift_branch_instructions
from .logical import lift_logical_instructions
from .shift import lift_shift_instructions

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
    "e_and2i."   : lift_logical_instructions,
    "e_and2is."  : lift_logical_instructions,
    "e_andi"     : lift_logical_instructions,
    "se_andi"    : lift_logical_instructions,
    "e_or2i"     : lift_logical_instructions,
    "e_or2is"    : lift_logical_instructions,
    "e_ori"      : lift_logical_instructions,
    "e_xori"     : lift_logical_instructions,
    "se_and"     : lift_logical_instructions,
    "se_andc"    : lift_logical_instructions,
    "se_or"      : lift_logical_instructions,
    "se_not"     : lift_logical_instructions,
    "se_bclri"   : lift_logical_instructions,
    "se_bgeni"   : lift_logical_instructions,
    "se_bmaski"  : lift_logical_instructions,
    "se_bseti"   : lift_logical_instructions,
    "se_extsb"   : lift_logical_instructions,
    "se_extsh"   : lift_logical_instructions,
    "se_extzb"   : lift_logical_instructions,
    "se_extzh"   : lift_logical_instructions,
    "e_li"       : lift_logical_instructions,
    "se_li"      : lift_logical_instructions,
    "e_lis"      : lift_logical_instructions,
    "se_mfar"    : lift_logical_instructions,
    "se_mr"      : lift_logical_instructions,
    "se_mtar"    : lift_logical_instructions,
    "e_rlwimi"   : lift_shift_instructions,
    "e_rlwinm"   : lift_shift_instructions,
    "se_slwi"    : lift_shift_instructions,
    "se_slw"     : lift_shift_instructions,
    "se_srawi"   : lift_shift_instructions,
    "se_sraw"    : lift_shift_instructions,
    "se_srwi"    : lift_shift_instructions,
    "se_srw"     : lift_shift_instructions,
}
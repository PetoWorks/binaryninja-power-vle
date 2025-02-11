from typing import Callable

from binaryninja.lowlevelil import LowLevelILFunction

from ..instruction import Instruction
from .branch import lift_branch_instructions

from .arithmetic import (lift_add_instructions,
                         lift_sub_instructions,
                         lift_mul_instructions)
from .compare import lift_compare_instructions
from .load import lift_load_instructions

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

    "se_add"    : lift_add_instructions,
    "e_add16i"  : lift_add_instructions,
    "e_add2i"   : lift_add_instructions,
    "e_add2is"  : lift_add_instructions,
    "e_addi"    : lift_add_instructions,
    "se_addi"   : lift_add_instructions,
    "e_addic"   : lift_add_instructions, 

    "se_sub"    : lift_sub_instructions,
    "se_subf"   : lift_sub_instructions,
    "e_subfic"  : lift_sub_instructions,
    "se_subi"   : lift_sub_instructions,

    "e_mulli"   : lift_mul_instructions,
    "e_mull2i"  : lift_mul_instructions,
    "se_mullw"  : lift_mul_instructions,
    "se_neg"    : lift_mul_instructions,

    "se_btsti"  : lift_compare_instructions,
    "e_cmp16i"  : lift_compare_instructions,
    "e_cmpi"    : lift_compare_instructions,
    "se_cmp"    : lift_compare_instructions,
    "se_cmpi"   : lift_compare_instructions,
    "e_cmpl16i" : lift_compare_instructions,
    "e_cmpli"   : lift_compare_instructions,
    "se_cmpl"   : lift_compare_instructions,
    "se_cmpli"  : lift_compare_instructions,
    "e_cmph"    : lift_compare_instructions, # TODO
    "se_cmph"   : lift_compare_instructions,
    "e_cmph16i" : lift_compare_instructions,
    "e_cmphl"   : lift_compare_instructions, # TODO
    "se_cmphl"  : lift_compare_instructions,
    "e_cmphl16i": lift_compare_instructions,

    "e_lbz" : lift_load_instructions,
    "se_lbz" : lift_load_instructions,
    "e_lbzu" : lift_load_instructions,
    "e_lha" : lift_load_instructions,
    "e_lhz" : lift_load_instructions,
    "se_lhz" : lift_load_instructions,
    "e_lhau" : lift_load_instructions,
    "e_lhzu" : lift_load_instructions,
    "e_lwz" : lift_load_instructions,
    "se_lwz" : lift_load_instructions,
    "e_lwzu" : lift_load_instructions

}
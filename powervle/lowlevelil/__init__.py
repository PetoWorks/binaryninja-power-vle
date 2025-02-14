from typing import Callable

from binaryninja.lowlevelil import LowLevelILFunction

from ..instruction import Instruction
from .branch import lift_branch_instructions
from .logical import lift_logical_instructions
from .arithmetic import (lift_add_instructions,
                         lift_sub_instructions,
                         lift_mul_instructions)
from .compare import lift_compare_instructions
from .load import lift_load_instructions
from .multiple import lift_multiple_instructions

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
    "e_cmph"    : lift_compare_instructions, 
    "se_cmph"   : lift_compare_instructions,
    "e_cmph16i" : lift_compare_instructions,
    "e_cmphl"   : lift_compare_instructions, 
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
    "e_lwzu" : lift_load_instructions,

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

    "e_lmw": lift_multiple_instructions,
    "e_stmw": lift_multiple_instructions
}
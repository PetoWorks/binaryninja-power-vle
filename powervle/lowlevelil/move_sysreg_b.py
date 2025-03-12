from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

def lift_b_move_sysreg_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
    
    if inst.name == "mtspr":
        spr = inst.get_spr_name(oper_0)
        rs = inst.get_operand_value(oper_1)

        ei0 = il.set_reg(il.arch.address_size, spr, il.reg(il.arch.address_size, rs))
        
        il.append(ei0)
    
    elif inst.name == "mfspr":
        rt = inst.get_operand_value(oper_0)
        spr = inst.get_spr_name(oper_1)

        ei0 = il.set_reg(il.arch.address_size, rt, il.reg(il.arch.address_size, spr))

        il.append(ei0)

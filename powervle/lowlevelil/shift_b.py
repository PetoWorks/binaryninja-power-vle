from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

def lift_b_shift_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0:   oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
    
    if inst.name in ["slw", "srw"]:
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        ei0 = il.and_expr(4, il.reg(4, rb), il.const(4, 0x3f))
        if inst.name == "slw":
            ei0 = il.shift_left(4, il.reg(4, rs), ei0)
        else:
            ei0 = il.logical_shift_right(4, il.reg(4, rs), ei0)
        
        ei0 = il.set_reg(4, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name == "srawi":
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        sh = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        ei0 = il.arith_shift_right(4, il.reg(4, rs), il.const(4, sh), 'xer_ca')
        ei0 = il.set_reg(4, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name == "sraw":
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        ei0 = il.and_expr(4, il.reg(4, rb), il.const(4, 0x1f))
        ei0 = il.arith_shift_right(4, il.reg(4, rs), ei0, 'xer_ca')
        ei0 = il.set_reg(4, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)
from binaryninja.lowlevelil import LowLevelILFunction, ExpressionIndex
from ..instruction import Instruction

def lift_b_logical_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0:   oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
    
    if inst.name in ["and", "nand", "andc"]:
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        ei0 = il.reg(il.arch.address_size, rb)
        if inst.name == "andc":
            ei0 = il.not_expr(il.arch.address_size, ei0)

        ei0 = il.and_expr(
            il.arch.address_size,
            il.reg(il.arch.address_size, rs),
            ei0,
        )

        if inst.name == "nand":
            ei0 = il.not_expr(il.arch.address_size, ei0)

        ei0 = il.set_reg(il.arch.address_size, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name in ["or", "nor", "orc"]:
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        ei0 = il.reg(il.arch.address_size, rb)

        if inst.name == "orc":
            ei0 = il.not_expr(il.arch.address_size, ei0)

        ei0 = il.or_expr(
            il.arch.address_size,
            il.reg(il.arch.address_size, rs),
            ei0,
        )

        if inst.name == "nor":
            ei0 = il.not_expr(il.arch.address_size, ei0)

        ei0 = il.set_reg(il.arch.address_size, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name in ["xor", "eqv"]:
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        ei0 = il.xor_expr(
            il.arch.address_size,
            il.reg(il.arch.address_size, rs),
            il.reg(il.arch.address_size, rb),
        )

        if inst.name == "eqv":
            ei0 = il.not_expr(il.arch.address_size, ei0)

        ei0 = il.set_reg(il.arch.address_size, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name in ["extsb", "extsh"]:
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        rc = inst.get_operand_value(oper_2)

        ei0 = il.reg(il.arch.address_size, rs)
        if inst.name == "extsb":
            ei0 = il.low_part(1, ei0)
        else:
            ei0 = il.low_part(2, ei0)
        
        ei0 = il.sign_extend(il.arch.address_size, ei0)
        ei0 = il.set_reg(il.arch.address_size, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)
from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

# 5.5 Fixed-Point Arithmetic Instructions
def lift_add_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
    if inst.name == "se_add": # Add Short Form
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ry = inst.get_operand_value(oper_1)
        ei0 = il.add(4, il.reg(4, rx), il.reg(4, ry))
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    elif inst.name == "e_add16i": # Add immediate
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        si = inst.get_operand_value(oper_2)
        ei0 = il.add(4, il.reg(4, ra), il.const(4, si))
        ei0 = il.set_reg(4, rt, ei0)
        il.append(ei0)
    # Add (2 operand) Immediate and Record
    # Add (2 operand) Immediate Shifted
    elif inst.name in ["e_add2i.", "e_add2is"]: 
        assert len(inst.operands) == 2
        ra = inst.get_operand_value(oper_0)
        si = inst.get_operand_value(oper_1)
        if inst.name == "e_add2is":
            ei0 = il.const(4, si << 16)
            flags = None
        else:
            ei0 = il.const(4, si)
            flags = "cr0s"
        ei0 = il.add(4, il.reg(4, ra), ei0)
        ei0 = il.set_reg(4, ra, ei0, flags)
        il.append(ei0)
    elif inst.name in ["e_addi", "e_addic"]: # Add Scaled Immediate
        assert len(inst.operands) == 4
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        sci8 = inst.get_operand_value(oper_2)
        if inst.name == "e_addi":
            ei0 = il.add(4, il.reg(4, ra), il.const(4, sci8))
        else:
            ei0 = il.add(4, il.reg(4, ra), il.const(4, sci8), "xer_ca")
        if inst.get_operand_value(oper_3) : # Rc
            ei0 = il.set_reg(4, rt, ei0, "cr0s")
        else:
            ei0 = il.set_reg(4, rt, ei0)
        il.append(ei0)
    elif inst.name == "se_addi": # Add Immediate Short Form
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        oimm = inst.get_operand_value(oper_1)
        ei0 = il.add(4, il.reg(4, rx), il.const(4, oimm))
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    else:
        il.append(il.unimplemented())


def lift_sub_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]

    # InstRR("se_sub", "VLE", ["RX", "RY"]): Subtract
    # InstRR("se_subf", "VLE", ["RX", "RY"]): Subtract From Short Form
    if inst.name in ["se_sub", "se_subf"]:
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ry = inst.get_operand_value(oper_1)
        ei0 = il.sub(4, il.reg(4, rx), il.reg(4, ry))
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    elif inst.name == "e_subfic": # Subtract From Scaled Immediate Carrying
        assert len(inst.operands) == 4
        rt = inst.get_operand_value(oper_0)
        sci8 = inst.get_operand_value(oper_2)
        ra = inst.get_operand_value(oper_1)
        ei0 = il.sub(4, il.const(4, sci8), il.reg(4, ra), "xer_ca")
        if inst.get_operand_value(oper_3):
            ei0 = il.set_reg(4, rt, ei0, "cr0s")
        else:
            ei0 = il.set_reg(4, rt, ei0)
        il.append(ei0)
    elif inst.name == "se_subi": # Subtract Immediate
        assert len(inst.operands) == 3
        rx = inst.get_operand_value(oper_0)
        oimm = inst.get_operand_value(oper_1)
        ei0 = il.sub(4, il.reg(4, rx), il.const(4, oimm))
        if inst.get_operand_value(oper_2):
            ei0 = il.set_reg(4, rx, ei0, "cr0s")
        else:
            ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)

def lift_mul_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
    if inst.name == "e_mulli": # Multiply Low Scaled Immediate
        assert len(inst.operands) == 3
        ei0 = il.reg(4, inst.get_operand_value(oper_1))
        ei0 = il.mult(16, ei0, il.const(4, inst.get_operand_value(oper_2))) 
        il.append(il.set_reg(4, inst.get_operand_value(oper_0), ei0)) 
    if inst.name == "e_mull2i": # Multiply (2 operand) Low Immediate
        assert len(inst.operands) == 2
        ra = inst.get_operand_value(oper_0)
        si = inst.get_operand_value(oper_1)
        ei0 = il.mult(16, il.reg(4, ra), il.const(4, si)) 
        il.append(il.set_reg(4, ra, ei0))
    if inst.name == "se_mullw": # Multiply Low Word Short Form
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ry = inst.get_operand_value(oper_1)
        ei0 = il.mult(8, il.reg(4, rx), il.reg(4, ry))
        il.append(il.set_reg(4, rx, ei0))
    if inst.name == "se_neg": # Negate Short Form
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)
        ei0 = il.neg_expr(4, il.reg(4, inst.get_operand_value(oper_0)))
        il.append(il.set_reg(4, rx, ei0))
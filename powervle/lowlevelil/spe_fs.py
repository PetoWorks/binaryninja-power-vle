from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

# Float Scalar Single Instructions             
def lift_sp_fss_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
    
    # Floating-Point Single-Precision Absolute Value: InstEVX("efsabs", "SP.FS", ["RT", "RA"])
    if inst.name == "efsabs":
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        ei0 = il.float_abs(4, il.reg(4, ra))
        ei1 = il.set_reg(4, rt, ei0)
        il.append(ei1)
    # Floating-Point Single-Precision Negative Absolute Value: InstEVX("efsnabs", "SP.FS", ["RT", "RA"])
    elif inst.name == "efsnabs":
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        ei0 = il.float_abs(4, il.reg(4, ra))
        ei0 = il.float_neg(4, ei0)
        ei1 = il.set_reg(4, rt, ei0)
        il.append(ei1)
    # Floating-Point Single-Precision Negate: InstEVX("efsneg", "SP.FS", ["RT", "RA"])
    elif inst.name == "efsneg":
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        ei0 = il.float_neg(4, il.reg(ra))
        ei0 = il.set_reg(4, rt, ei0)
        il.append(ei0)

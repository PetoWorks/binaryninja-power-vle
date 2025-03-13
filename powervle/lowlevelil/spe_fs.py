from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

# Float Scalar Single Instructions             
def lift_sp_fss_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
    
    # Floating-Point Single-Precision Add: InstEVX("efsadd", "SP.FS", ["RT", "RA", "RB"])
    if inst.name == "efsadd":
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei0 = il.float_add(4, il.reg(4, ra), il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # FINV FINVS FOVF FOVFS FUNF FUNFS FG FX FINXS
        il.append(ei1)
    
    # Floating-Point Single-Precision Subtract: InstEVX("efssub", "SP.FS", ["RT", "RA", "RB"])
    elif inst.name == "efssub":
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei0 = il.float_sub(4, il.reg(4, ra), il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # FINV FINVS FOVF FOVFS FUNF FUNFS FG FX FINXS
        il.append(ei1)
    # Floating-Point Single-Precision Multiply: InstEVX("efsmul", "SP.FS", ["RT", "RA", "RB"])
    elif inst.name == "efsmul":
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei0 = il.float_mult(4, il.reg(4, ra), il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # FINV FINVS FOVF FOVFS FUNF FUNFS FG FX FINXS
        il.append(ei1)
    # Floating-Point Sigle-Precision Divide: InstEVX("efsdiv", "SP.FS", ["RT", "RA", "RB"])
    elif inst.name == "efsdiv":
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei0 = il.float_div(4, il.reg(4, ra), il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # FINV FINVS FG FX FINXS FDBZ FDBZS FOVF FOVFS FUNF FUNFS
        il.append(ei1)
    # Floating-Point Single-Precision Multiply-Add: InstEVX("efsmadd", "SP.FS", ["RT", "RA", "RB"])
    elif inst.name == "efsmadd":
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei0 = il.float_mult(4, il.reg(4, ra), il.reg(4, rb))
        ei0 = il.float_add(4, ei0, il.reg(4, rt))
        ei1 = il.set_reg(4, rt, ei0)
        # FINV FINVS FOVF FOVFS FUNF FUNFS FG FX FINXS
        il.append(ei1)
    # Floating-Point Single-Precision Absolute Value: InstEVX("efsabs", "SP.FS", ["RT", "RA"])
    elif inst.name == "efsabs":
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
        ei0 = il.float_neg(4, il.reg(4, ra))
        ei0 = il.set_reg(4, rt, ei0)
        il.append(ei0)

    # Convert Floating-Point Single-Precision from Unsigned Integer: InstEVX("efscfui", "SP.FS", ["RT", "RB"])
    # Convert Floating-Point Single-Precision from Signed Integer: InstEVX("efscfsi", "SP.FS", ["RT", "RB"])
    # Convert Floating-Point Single-Precision to Unsigned Integer with Round toward Zero: InstEVX("efsctuiz", "SP.FS", ["RT", "RB"])
    # Convert Floating-Point Single-Precision to Signed Integer with Round toward Zero: InstEVX("efsctsiz", "SP.FS", ["RT", "RB"])
    
    # Floating-Point Single-Precision Test Greater Than: InstEVX("efststgt", "SP.FS", ["BF", "RA", "RB"])
    # Floating-Point Single-Precision Test Less Than: InstEVX("efststlt", "SP.FS", ["BF", "RA", "RB"])
    # Floating-Point Single-Precision Test Equal: InstEVX("efststeq", "SP.FS", ["BF", "RA", "RB"])
    else:
        il.append(il.unimplemented())

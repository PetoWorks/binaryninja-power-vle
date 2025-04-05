from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

# EFPU (Embedded Floating-Point Unit)        
def lift_efpu_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
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
        # TODO: FINV FINVS FOVF FOVFS FUNF FUNFS FG FX FINXS
        il.append(ei1)
    
    # Floating-Point Single-Precision Subtract: InstEVX("efssub", "SP.FS", ["RT", "RA", "RB"])
    elif inst.name == "efssub":
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei0 = il.float_sub(4, il.reg(4, ra), il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # TODO: FINV FINVS FOVF FOVFS FUNF FUNFS FG FX FINXS
        il.append(ei1)
    # Floating-Point Single-Precision Multiply: InstEVX("efsmul", "SP.FS", ["RT", "RA", "RB"])
    elif inst.name == "efsmul":
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei0 = il.float_mult(4, il.reg(4, ra), il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # TODO: FINV FINVS FOVF FOVFS FUNF FUNFS FG FX FINXS
        il.append(ei1)
    # Floating-Point Sigle-Precision Divide: InstEVX("efsdiv", "SP.FS", ["RT", "RA", "RB"])
    elif inst.name == "efsdiv":
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei0 = il.float_div(4, il.reg(4, ra), il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # TODO: FINV FINVS FG FX FINXS FDBZ FDBZS FOVF FOVFS FUNF FUNFS
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
        # TODO: FINV FINVS FOVF FOVFS FUNF FUNFS FG FX FINXS
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

    # Convert Floating-Point Single-Precision from Signed Integer: InstEVX("efscfsi", "SP.FS", ["RT", "RB"])
    elif inst.name == "efscfsi":
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        rb = inst.get_operand_value(oper_1)

        # ei0 = CnvtI32ToFP32(RB, S, LO, I)
        ei0 = il.float_convert(4, il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # TODO: FINXS, FG, FX
        il.append(ei1) 
    # Convert Floating-Point Single-Precision from Unsigned Integer: InstEVX("efscfui", "SP.FS", ["RT", "RB"])
    elif inst.name == "efscfui":
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        rb = inst.get_operand_value(oper_1)
 
        # ei0 = CnvtI32ToFP32(RB, U, LO, I)
        ei0 = il.float_convert(4, il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # TODO: FINXS, FG, FX
        il.append(ei1)
    # Convert Floating-Point Single-Precision to Signed Integer with Round toward Zero: InstEVX("efsctsiz", "SP.FS", ["RT", "RB"])
    elif inst.name == "efsctsiz":
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        rb = inst.get_operand_value(oper_1)
   
        # ei0 = il.CnvtFP32ToI32Sat (RB, S, LO, ZER, I)
        ei0 = il.float_to_int(4, il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # TODO: FINV, FINVS, FINXS, FG, FX
        il.append(ei1)
    # Convert Floating-Point Single-Precision to Unsigned Integer with Round toward Zero: InstEVX("efsctuiz", "SP.FS", ["RT", "RB"])
    elif inst.name == "efsctuiz":
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        rb = inst.get_operand_value(oper_1)

        # ei0 = il.CnvtFP32ToI32Sat (RB, U, LO, ZER, I)
        ei0 = il.float_to_int(4, il.reg(4, rb))
        ei1 = il.set_reg(4, rt, ei0)
        # TODO: FINV, FINVS, FINXS, FG, FX
        il.append(ei1)
    # Floating-Point Single-Precision Test Greater Than: InstEVX("efststgt", "SP.FS", ["BF", "RA", "RB"])
    elif inst.name == "efststgt":
        assert len(inst.operands) == 3
        bf = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei2 = il.float_sub(4, il.reg(4, ra), il.reg(4, rb), f"{bf}tstgt")
        il.append(ei2)
    # Floating-Point Single-Precision Test Less Than: InstEVX("efststlt", "SP.FS", ["BF", "RA", "RB"])
    elif inst.name == "efststlt":
        assert len(inst.operands) == 3
        bf = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei2 = il.float_sub(4, il.reg(4, ra), il.reg(4, rb), f"{bf}tstlt")
        il.append(ei2)
    # Floating-Point Single-Precision Test Equal: InstEVX("efststeq", "SP.FS", ["BF", "RA", "RB"])
    elif inst.name == "efststeq":
        assert len(inst.operands) == 3
        bf = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        ei2 = il.float_sub(4, il.reg(4, ra), il.reg(4, rb), f"{bf}tsteq")
        il.append(ei2)
    else:
        il.append(il.unimplemented())
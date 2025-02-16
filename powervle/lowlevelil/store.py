from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

def lift_store_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0:   oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
    
    if inst.name in ["e_stb", "e_sth", "e_stw"]:
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d = inst.get_operand_value(oper_2)

        ei0 = None
        EA = il.add(4, il.reg(4, ra), il.const(4, d))

        if inst.name == "e_stb":    # Byte
            ei0 = il.low_part(1, il.reg(4, rs))
            ei0 = il.store(1, EA, ei0)
        elif inst.name == "e_sth":  # Half Word
            ei0 = il.low_part(2, il.reg(4, rs))
            ei0 = il.store(2, EA, ei0)
        else:                       # Word
            ei0 = il.store(4, EA, il.reg(4, rs))
        
        il.append(ei0)
    
    elif inst.name in ["e_stbu", "e_sthu", "e_stwu"]:
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d8 = inst.get_operand_value(oper_2)

        EA = il.add(4, il.reg(4, ra), il.const(4, d8))
        ei0 = None

        if inst.name == "e_stbu":   # Byte
            ei0 = il.low_part(1, il.reg(4, rs))
            ei0 = il.store(1, EA, ei0)
        elif inst.name == "e_sthu": # Half Word
            ei0 = il.low_part(2, il.reg(4, rs))
            ei0 = il.store(2, EA, ei0)
        else:                       # Word
            ei0 = il.store(4, EA, il.reg(4, rs))
              
        il.append(ei0)

        ei0 = il.set_reg(4, ra, EA)
        il.append(ei0)
    

    elif inst.name in ["se_stb", "se_sth", "se_stw"]:
        assert len(inst.operands) == 3
        rz = inst.get_operand_value(oper_0)
        rx = inst.get_operand_value(oper_1)
        sd4 = inst.get_operand_value(oper_2)

        EA = il.add(4, il.reg(4, rx), il.const(4, sd4))
        ei0 = None

        if inst.name == "se_stb":   # Byte
            ei0 = il.low_part(1, il.reg(4, rz))
            ei0 = il.store(1, EA, ei0)
        elif inst.name == "se_sth": # Half Word
            ei0 = il.low_part(2, il.reg(4, rz))
            ei0 = il.store(2, EA, ei0)
        else:                       # Word
            ei0 = il.store(4, EA, il.reg(4, rz))
        
        il.append(ei0)
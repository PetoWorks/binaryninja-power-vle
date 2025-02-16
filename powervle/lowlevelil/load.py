from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

## 5.1 Fixed-Point Load Instructions
def lift_load_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0:   oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
    # Load Byte and Zero: InstD("e_lbz", "VLE", ["RT", "RA", "D"])
    # Load Byte and Zero with Update: InstD8("e_lbzu", "VLE", ["RT", "RA", "D8"])
    if inst.name in ["e_lbz", "e_lbzu"] :
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d = inst.get_operand_value(oper_2)
        if inst.name == "e_lbzu" :
            if (ra == 0) or (ra == rt):
                il.append(il.undefined())
                return
        if ra == 0:
            EA = il.const(4, d)
        else :
            EA = il.add(4, il.reg(4, ra), il.const(4, d))
        
        ei0 = il.load(1, EA)
        ei0 = il.set_reg(4, rt, il.zero_extend(4, ei0))
        il.append(ei0)
        if inst.name == "e_lbzu": # update
            ei0 = il.set_reg(4, ra, EA)
            il.append(ei0)

    # Load Halfword Algebraic: InstD("e_lha", "VLE", ["RT", "RA", "D"])
    # Load Halfword and Zero: InstD("e_lhz", "VLE", ["RT", "RA", "D"])
    # Load Halfword Algebraic with Update: InstD8("e_lhau", "VLE", ["RT", "RA", "D8"])
    # Load Halfword and Zero with Update: InstD8("e_lhzu", "VLE", ["RT", "RA", "D8"])
    elif inst.name in ["e_lha", "e_lhz", "e_lhau", "e_lhzu"] :                                   
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d = inst.get_operand_value(oper_2)
        if inst.name in ["e_lhau", "e_lhzu"]:
            if ra == 0 or ra == rt:
                il.append(il.undefined())
                return
        if ra == 0:
            EA = il.const(4, d)
        else :
            EA = il.add(4, il.reg(4, ra), il.const(4, d))
        ei0 = il.load(2, EA)
        if inst.name in ["e_lhz", "e_lhzu"]:
            ei0 = il.zero_extend(4, ei0)
        else: 
            ei0 = il.sign_extend(4, ei0)
        ei0 = il.set_reg(4, rt, ei0)
        il.append(ei0)
        if inst.name in ["e_lhau", "e_lhzu"]:
            ei0 = il.set_reg(4, ra, EA)
            il.append(ei0)

    # Load Byte and Zero Short Form: InstSD4("se_lbz", "VLE", ["RZ", "RX", "SD4"])
    # Load Halfword and Zero Short Form: InstSD4("se_lhz", "VLE", ["RZ", "RX", "SD4"])
    # # Load Word and Zero Short Form: InstSD4("se_lwz", "VLE", ["RZ", "RX", "SD4"])
    elif inst.name in ["se_lbz", "se_lhz", "se_lwz"]:      
        assert len(inst.operands) == 3
        rz = inst.get_operand_value(oper_0)
        rx = inst.get_operand_value(oper_1)
        sd4 = inst.get_operand_value(oper_2)
        if inst.name == "se_lbz":
            ei0 = il.const(4, sd4)
        elif inst.name == "se_lhz":
            ei0 = il.const(4, sd4 << 1)
        else:
            ei0 = il.const(4, sd4 << 2) # "se_lwz"
        EA = il.add(4, il.reg(4, rx), ei0)
        if inst.name == "se_lbz":
            ei0 = il.load(1, EA)
        else :
            ei0 = il.load(2, EA) # "se_lhz", "se_lwz"
        ei0 = il.set_reg(4, rz, il.zero_extend(4, ei0))
        il.append(ei0)

    # Load Word and Zero: InstD("e_lwz", "VLE", ["RT", "RA", "D"])
    # Load Word and Zero with Update: InstD8("e_lwzu", "VLE", ["RT", "RA", "D8"])
    elif inst.name in ["e_lwz", "e_lwzu"] : 
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d = inst.get_operand_value(oper_2)
        if inst.name == "e_lwzu" :
            if (ra == 0) or (ra == rt):
                il.append(il.undefined())
                return
        if ra == 0:
            EA = il.const(4, d)
        else :
            EA = il.add(4, il.reg(4, ra), il.const(4, d))
        ei0 = il.load(4, EA)
        ei0 = il.set_reg(4, rt, il.zero_extend(4, ei0))
        il.append(ei0)
        if inst.name == "e_lwzu": # update
            ei0 = il.set_reg(4, ra, EA)
            il.append(ei0)
    
    else:
        il.append(il.unimplemented())
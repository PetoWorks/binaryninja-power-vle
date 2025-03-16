from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

def lift_compare_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
    if inst.name == "se_btsti": # Bit Test Immediate: InstIM5("se_btsti", "VLE", ["RX", "UI5"])
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ui5 = inst.get_operand_value(oper_1)
        ei0 = il.test_bit(4, il.reg(4, rx), il.const(4, ui5))
        il.append(ei0)
    elif inst.name in ["e_cmp16i", "e_cmph16i", "e_cmpl16i", "e_cmphl16i"] :   # Compare Immediate Word
                                                    # Compare Halfword Immediate
                                                    # Compare Logical Immediate Word
                                                    # Compare Halfword Logical Immediate
        assert len(inst.operands) == 2
        if inst.name in ["e_cmph16i", "e_cmphl16i"]:
            ei0 = il.reg(2, inst.get_operand_value(oper_0))
        else :
            ei0 = il.reg(4, inst.get_operand_value(oper_0))
        if inst.name in ["e_cmpl16i", "e_cmphl16i"]:
            flags = "cr0u"
        else:
            flags = "cr0s"
        ei1 = il.sub(4, ei0, il.const(4, inst.get_operand_value(oper_1)), flags)
        il.append(ei1)
    
    # InstSCI8("e_cmpi", "VLE", ["BF32", "RA", "sci8"]): Compare Scaled Immediate Word
    # InstSCI8("e_cmpli", "VLE", ["BF32", "RA", "sci8"]): Compare Logical Scaled Immediate Word
    elif inst.name in ["e_cmpi", "e_cmpli"]:                   
        assert len(inst.operands) == 3
        ra = inst.get_operand_value(oper_1)
        sci8 = inst.get_operand_value(oper_2)      
        if inst.name == "e_cmpli":
            flags = inst.get_operand_value(oper_0) + "u"
        else:
            flags = inst.get_operand_value(oper_0) + "s"
        ei0 = il.sub(4, il.reg(4, ra), il.const(4, sci8), flags)
        il.append(ei0)
    elif inst.name in ["se_cmp", "se_cmpl", "se_cmph", "se_cmphl"]: # Compare Word
                                # Compare Logical Word
                                # Compare Halfword Short Form
                                # Compare Halfword Logical Short Form
        assert len(inst.operands) == 2       
        if inst.name == "se_cmph":
            ei0 = il.sign_extend(4, il.reg(2, inst.get_operand_value(oper_0)))
            ei1 = il.sign_extend(4, il.reg(2, inst.get_operand_value(oper_1)))
        elif inst.name == "se_cmphl":
            ei0 = il.reg(2, inst.get_operand_value(oper_0))
            ei1 = il.reg(2, inst.get_operand_value(oper_1))
        else:
            ei0 = il.reg(4, inst.get_operand_value(oper_0))
            ei1 = il.reg(4, inst.get_operand_value(oper_1))
        if inst.name in ["se_cmpl", "se_cmphl"]:
            flags = "cr0u"
        else:
            flags = "cr0s"
        ei2 = il.sub(4, ei0, ei1, flags)
        il.append(ei2)
    elif inst.name in ["se_cmpi", "se_cmpli"]:  # Compare Immediate Word Short Form
                                                # Compare Logical Immediate Word
        assert len(inst.operands) == 2
        if inst.name == "se_cmpi":
            flags = "cr0s"
        else:
            flags = "cr0u"
        ei0 = il.reg(4, inst.get_operand_value(oper_0))
        ei1 = il.const(4, inst.get_operand_value(oper_1))
        ei2 = il.sub(4, ei0, ei1, flags)
        il.append(ei2)

    # InstX("e_cmph", "VLE",  ["BF", "RA", "RB"]): Compare Halfword
    # InstX("e_cmphl", "VLE",  ["BF", "RA", "RB"]): 
    elif inst.name in ["e_cmph", "e_cmphl"]:
        assert len(inst.operands) == 3
        bf = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        if inst.name == "e_cmph":
            ei0 = il.sign_extend(4, il.reg(2, ra))
            ei1 = il.sign_extend(4, il.reg(2, rb))
        else:
            ei0 = il.zero_extend(4, il.reg(2, ra))
            ei1 = il.zero_extend(4, il.reg(2, rb))
        ei2 = il.sub(4, ei0, ei1, f"{bf}s")
        il.append(ei2)

    else:
        il.append(il.unimplemented())
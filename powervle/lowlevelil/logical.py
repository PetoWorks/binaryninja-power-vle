from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction


def lift_logical_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0:   oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]

    if inst.name in ["e_and2i.", "e_and2is."]:
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        ui = inst.get_operand_value(oper_1)

        if inst.name == "e_and2i.":
            ei0 = il.const(4, ui)
        else:
            ei0 = il.const(4, ui << 16)

        ei0 = il.and_expr(4, il.reg(4, rt), ei0)
        ei0 = il.set_reg(4, rt, ei0, 'cr0s')
        il.append(ei0)
    
    elif inst.name == "e_andi":
        assert len(inst.operands) == 4
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        sci8 = inst.get_extended_operand_value(oper_2)  # sci8
        rc = inst.get_operand_value(oper_3)           # Rc

        ei0 = il.and_expr(4, il.reg(4, rs), il.const(4, sci8))
        ei0 = il.set_reg(4, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name == "se_andi":
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ui5 = inst.get_operand_value(oper_1)

        ei0 = il.and_expr(4, il.reg(4, rx), il.const(4, ui5))
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    
    elif inst.name in ["e_or2i", "e_or2is"]:
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        ui = inst.get_operand_value(oper_1)

        if inst.name == "e_or2i":
            ei0 = il.const(4, ui)
        else:
            ei0 = il.const(4, ui << 16)

        ei0 = il.or_expr(4, il.reg(4, rt), ei0)
        ei0 = il.set_reg(4, rt, ei0)
        il.append(ei0)
    
    elif inst.name == "e_ori":
        assert len(inst.operands) == 4
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        sci8 = inst.get_extended_operand_value(oper_2)  # sci8
        rc = inst.get_operand_value(oper_3)           # Rc

        ei0 = il.or_expr(4, il.reg(4, rs), il.const(4, sci8))
        ei0 = il.set_reg(4, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name == "e_xori":
        assert len(inst.operands) == 4
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        sci8 = inst.get_extended_operand_value(oper_2)  # sci8
        rc = inst.get_operand_value(oper_3)           # Rc 

        ei0 = il.xor_expr(4, il.reg(4, rs), il.const(4, sci8))
        ei0 = il.set_reg(4, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name == "se_and":
        assert len(inst.operands) == 3
        rx = inst.get_operand_value(oper_0)
        ry = inst.get_operand_value(oper_1)
        rc = inst.get_operand_value(oper_2)
        ei0 = il.and_expr(4, il.reg(4, rx), il.reg(4, ry))
        ei0 = il.set_reg(4, rx, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name == "se_andc":
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ry = inst.get_operand_value(oper_1)

        ei0 = il.not_expr(4, il.reg(4, ry))
        ei0 = il.and_expr(4, il.reg(4, rx), ei0)
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    
    elif inst.name == "se_or":
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ry = inst.get_operand_value(oper_1)

        ei0 = il.or_expr(4, il.reg(4, rx), il.reg(4, ry))
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)

    elif inst.name == "se_not":
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)

        ei0 = il.not_expr(4, il.reg(4, rx))
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)

    elif inst.name == "se_bclri":
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ui5 = inst.get_operand_value(oper_1)

        ei0 = il.const(4, ((1 << (31 - ui5)) ^ 0xffffffff))
        ei0 = il.and_expr(4, il.reg(4, rx), ei0)
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    
    elif inst.name == "se_bgeni":
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ui5 = inst.get_operand_value(oper_1)

        ei0 = il.const(4, 1 << (31 - ui5))
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    
    elif inst.name == "se_bmaski":
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ui5 = inst.get_operand_value(oper_1)

        ei0 = il.const(4, (0xffffffff >> (32 - ui5)) if ui5 else 0xffffffff)
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    
    elif inst.name == "se_bseti":
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ui5 = inst.get_operand_value(oper_1)
        
        ei0 = il.const(4, 1 << (31 - ui5))
        ei0 = il.or_expr(4, il.reg(4, rx), ei0)
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    
    elif inst.name in ["se_extzb", "se_extzh"]:
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)

        if inst.name == "se_extzb":
            ei0 = il.low_part(1, il.reg(4, rx))
        else:
            ei0 = il.low_part(2, il.reg(4, rx))

        ei0 = il.zero_extend(4, ei0)
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)

    elif inst.name in ["se_extsb", "se_extsh"]:
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)

        if inst.name == "se_extsb":
            ei0 = il.low_part(1, il.reg(4, rx))
        else:
            ei0 = il.low_part(2, il.reg(4, rx))
        
        ei0 = il.sign_extend(4, ei0)
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    
    elif inst.name == "e_li":
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        li20 = inst.get_extended_operand_value(oper_1)

        ei0 = il.set_reg(4, rt, il.const(4, li20))
        il.append(ei0)
    
    elif inst.name == "se_li":
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ui7 = inst.get_operand_value(oper_1)

        ei0 = il.set_reg(4, rx, il.const(4, ui7))
        il.append(ei0)

    elif inst.name == "e_lis":
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        ui = inst.get_operand_value(oper_1)

        ei0 = il.set_reg(4, rt, il.const(4, ui << 16))
        il.append(ei0)
    
    elif inst.name == "se_mfar":
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ary = inst.get_operand_value(oper_1)

        ei0 = il.set_reg(4, rx, il.reg(4, ary))
        il.append(ei0)
    
    elif inst.name == "se_mr":
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ry = inst.get_operand_value(oper_1)

        ei0 = il.set_reg(4, rx, il.reg(4, ry))
        il.append(ei0)

    elif inst.name == "se_mtar":
        assert len(inst.operands) == 2
        arx = inst.get_operand_value(oper_0)
        ry = inst.get_operand_value(oper_1)

        ei0 = il.set_reg(4, arx, il.reg(4, ry))
        il.append(ei0)

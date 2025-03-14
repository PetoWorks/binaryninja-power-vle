from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

def lift_move_sysreg_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
    
    if inst.name == "se_mflr":
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)

        ei0 = il.set_reg(4, rx, il.reg(4, "lr"))
        il.append(ei0)
    
    elif inst.name == "se_mtlr":
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)
        
        ei0 = il.set_reg(4, "lr", il.reg(4, rx))
        il.append(ei0)
    
    elif inst.name == "se_mfctr":
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)

        ei0 = il.set_reg(4, rx, il.reg(4, "ctr"))
        il.append(ei0)
    
    elif inst.name == "se_mtctr":
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)

        ei0 = il.set_reg(4, "ctr", il.reg(4, rx))
        il.append(ei0)
    
        # Move To Special Purpose Register: InstXFX("mtspr", "B", ["SPR", "RS"])
    elif inst.name == "mtspr":
        assert len(inst.operands) == 2
        spr = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        if spr in il.arch.regs :
            ei0 = il.set_reg(4, spr, il.reg(4, rs))
        else:
            ei0 = il.unimplemented()
        il.append(ei0)

    # Move From Special Purpose Register: InstXFX("mfspr", "B", ["RT", "SPR"])
    elif inst.name == "mfspr":
        assert len(inst.operands) == 2
        rt = inst.get_operand_value(oper_0)
        spr = inst.get_operand_value(oper_1)
        if spr in il.arch.regs:
            ei0 = il.set_reg(4, rt, il.reg(4, spr))
        else:
            ei0 = il.unimplemented()
        il.append(ei0)

    # Move From Machine State Regsiter: InstX("mfmsr", "B", ["RT"])
    elif inst.name == "mfmsr":
        assert len(inst.operands) == 1
        rt = inst.get_operand_value(oper_0)
        ei0 = il.set_reg(4, rt, il.reg(4, "msr"))
        il.append(ei0)

    # Move From Condition Register: InstXFX("mfcr", "B", ["RT"])
    elif inst.name == "mfcr":
        assert len(inst.operands) == 1
        rt = inst.get_operand_value(oper_0)
        ei0 = il.set_reg(4, rt, il.reg(4, "cr"))
        il.append(ei0)

    # Move To Condition Register Fields: InstXFX("mtcrf", "B", ["FXM", "RS"])
    elif inst.name == "mtcrf":
        assert len(inst.operands) == 1
        fxm = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        mask = 0x80
        for i in range(8):
            if mask & fxm:
                ei0 = il.or_expr(4, il.reg(4, rs), il.const(4, 0), f"mtcr{i}")
                il.append(ei0)
            mask >>= 1

    # Move To Machine State Register: InstX("mtmsr", "E", ["RS"])
    elif inst.name == "mtmsr":
        assert len(inst.operands) == 1
        rs = inst.get_operand_value(oper_0)
        ei0 = il.reg(4, rs)
        ei1 = il.set_reg(4, "msr", ei0)
        il.append(ei1)
    
    else:
        il.append(il.unimplemented())
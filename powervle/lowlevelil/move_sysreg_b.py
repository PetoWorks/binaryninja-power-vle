from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction
from binaryninja.log import log_warn, log_error, log_debug

def lift_b_move_sysreg_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
    
    # Move To Special Purpose Register: InstXFX("mtspr", "B", ["SPR", "RS"])
    if inst.name == "mtspr":
        spr = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        if spr in il.arch.regs :
            ei0 = il.set_reg(4, spr, il.reg(4, rs))
        else:
            ei0 = il.unimplemented()
        il.append(ei0)

    # Move From Special Purpose Register: InstXFX("mfspr", "B", ["RT", "SPR"])
    elif inst.name == "mfspr":
        rt = inst.get_operand_value(oper_0)
        spr = inst.get_operand_value(oper_1)
        if spr in il.arch.regs:
            ei0 = il.set_reg(4, rt, il.reg(4, spr))
        else:
            ei0 = il.unimplemented()
        il.append(ei0)

    # Move From Machine State Regsiter: InstX("mfmsr", "B", ["RT"])
    elif inst.name == "mfmsr":
        rt = inst.get_operand_value(oper_0)
        ei0 = il.set_reg(4, rt, il.reg(4, "msr"))
        il.append(ei0)

    # Move To Condition Register Fields: InstXFX("mtcrf", "B", ["FXM", "RS"])
    elif inst.name == "mtcrf":
        fxm = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        mask = 0x80
        for i in range(8):
            if mask & fxm:
                ei0 = il.or_expr(4, il.reg(4, rs), il.const(4, 0), f"mtcr{i}")
                il.append(ei0)
            mask >>= 1

    # Move From Condition Register: InstXFX("mfcr", "B", ["RT"])
    elif inst.name == "mfcr":
        rt = inst.get_operand_value(oper_0)
        ei0 = il.set_reg(4, rt, il.reg(4, "cr"))
        il.append(ei0)
    
    else:
        il.append(il.unimplemented())
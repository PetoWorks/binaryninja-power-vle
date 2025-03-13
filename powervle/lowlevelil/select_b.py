from binaryninja.lowlevelil import LowLevelILFunction, LowLevelILLabel
from ..instruction import Instruction

def lift_b_select_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
    
    # Integer Select: InstA("isel", "B", ["RT", "RA", "RB", "BC"])
    if inst.name == "isel":
        assert len(inst.operands) == 4
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        bc = inst.get_operand_value(oper_3)

        trueLable =  LowLevelILLabel()
        falseLable = LowLevelILLabel()
        doneLable = LowLevelILLabel()

        # bc = 0 ~ 31
        crBit = bc
        cr = crBit // 4
        cond = crBit % 4

        if cond == 0:
            ei0 = il.flag(f"cr{cr}lt")
        elif cond == 1:
            ei0 = il.flag(f"cr{cr}gt")
        elif cond == 2:
            ei0 = il.flag(f"cr{cr}eq")
        else:
            ei0 = il.flag(f"cr{cr}so")
        
        if ra == 0:
            ei1 = il.const(4, 0)
        else:
            ei1 = il.reg(4, ra)
        ei2 = il.reg(4, rb)
        il.append(il.if_expr(ei0, trueLable, falseLable))

        # true case
        il.mark_label(trueLable)
        ei0 = il.set_reg(4, rt, ei1)
        il.append(ei0)
        il.append(il.goto(doneLable))

        # false case
        il.mark_label(falseLable)
        ei0 = il.set_reg(4, rt, ei2)
        il.append(ei0)
        il.append(il.goto(doneLable))

        # done
        il.mark_label(doneLable)

    else:
        il.append(il.unimplemented())
from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

def lift_b_compare_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0:   oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
    
    if inst.name in ["cmp", "cmpl"]:
        assert len(inst.operands) == 4
        bf = inst.get_operand_value(oper_0)
        l = inst.get_operand_value(oper_1)
        ra = inst.get_operand_value(oper_2)
        rb = inst.get_operand_value(oper_3)

        ei0 = il.reg(il.arch.address_size, ra)
        ei1 = il.reg(il.arch.address_size, rb)
        if inst.name == "cmp":
            flags = f"{bf}s"
        else:
            flags = f"{bf}u"

        ei0 = il.sub(il.arch.address_size, ei0, ei1, flags)

        il.append(ei0)
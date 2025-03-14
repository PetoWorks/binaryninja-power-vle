from binaryninja.lowlevelil import LowLevelILFunction, LowLevelILLabel
from ..instruction import Instruction

def lift_clz_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]

    # Count Leading Zeros Word: InstX("cntlzw", "B", ["RA", "RS", "Rc"])
    if inst.name == "cntlzw":
        assert len(inst.operands) == 3
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        rc = inst.get_operand_value(oper_2)

        n = 0
        RS = il.reg(4, rs)
        for i in range(32):
            if (RS & (1 << i)) == 0:
                n += 1
            else:
                break
        ei0 = il.set_reg(4, ra, il.const(4, n), 'cr0s' if rc else None)

        #ei0 = il.intrinsic([ra], "cntlzw", [RS], 'cr0s' if rc else None)
        il.append(ei0)

    else:
        il.append(il.unimplemented())   
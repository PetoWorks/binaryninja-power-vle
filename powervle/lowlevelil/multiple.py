from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

regs = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', \
        'r10', 'r11', 'r12', 'r13', 'r14', 'r15', 'r16', 'r17', 'r18', 'r19', \
        'r20', 'r21', 'r22', 'r23', 'r24', 'r25', 'r26', 'r27', 'r28', 'r29', \
        'r30', 'r31']
## 5.4 Fixed-Point Load and Store Multiple Instructions
def lift_multiple_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0:   oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
    # Load Multiple Word: InstD8("e_lmw", "VLE", ["RT", "RA", "D8"])
    if inst.name == "e_lmw":
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d8 = inst.get_operand_value(oper_2)
        i = regs.index(rt)
        if ra in regs[i:]:
            il.append(il.unimplemented())
            return
        if ra == 0:
            EA = il.const(4, 0)
        else :
            EA = il.reg(4, ra)
        EA = il.add(4, EA, il.const(4, d8))
        
        while i <= regs.index('r31'):
            ei0 = il.set_reg(4, regs[i], il.zero_extend(4, il.load(4, EA)))
            il.append(ei0)
            i += 1
            EA = il.add(4, EA, il.const(4, 4))

    # Store Multiple Word: InstD8("e_stmw", "VLE", ["RS", "RA", "D8"])
    elif inst.name == "e_stmw":
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d8 = inst.get_operand_value(oper_2)
        i = regs.index(rs)
        if ra == 0:
            EA = il.const(4, 0)
        else :
            EA = il.reg(4, ra)
        EA = il.add(4, EA, il.const(4, d8))      

        while i <= regs.index('r31'):
            ei0 = il.store(4, EA, il.reg(4, regs[i]))
            il.append(ei0)       
            i += 1
            EA = il.add(4, EA, il.const(4, 4))

    else:
        il.append(il.unimplemented())
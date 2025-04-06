from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction
from binaryninja.log import log_warn, log_error, log_debug
from ..utils import sign_extend

GPR = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', \
        'r10', 'r11', 'r12', 'r13', 'r14', 'r15', 'r16', 'r17', 'r18', 'r19', \
        'r20', 'r21', 'r22', 'r23', 'r24', 'r25', 'r26', 'r27', 'r28', 'r29', \
        'r30', 'r31']

def get_EA(il: LowLevelILFunction, ra, d8):
    if ra == 0:
        EA = il.const(4, d8)
    else :
        EA = il.add(4, il.reg(4, ra), il.const(4, d8))
    return EA

## 5.4 Fixed-Point Load and Store Multiple Instructions
def lift_multiple_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0:   oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
    # Load Multiple Word: InstD8("e_lmw", "VLE", ["RT", "RA", "D8"])
    if inst.name == "e_lmw": # e_lmw r13, r30, 0x4
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d8 = inst.get_operand_value(oper_2)

        r = GPR.index(rt)        
        EA = get_EA(il, ra, d8)
        while r <= 31:
            ei0 = il.set_reg(4, GPR[r], il.zero_extend(4, il.load(4, EA)))
            il.append(ei0)
            r += 1
            d8 += 4
            EA = get_EA(il, ra, d8)

    # Load Multiple Volatile GPR Word: InstD8("e_lmvgprw", "VLE", ["RA", "D8"])
    elif inst.name == "e_lmvgprw":
        assert len(inst.operands) == 2
        ra = inst.get_operand_value(oper_0)
        d8 = inst.get_operand_value(oper_1)

        EA = get_EA(il, ra, d8)
        ei0 = il.set_reg(4, 'r0', il.load(4, EA))
        il.append(ei0)
        
        i = 3
        while i <= 12:
            d8 += 4
            EA = get_EA(il, ra, d8)
            ei0 = il.set_reg(4, GPR[i], il.load(4, EA))
            il.append(ei0)
            i += 1

    # Load Multiple Volatile SPR Word: InstD8("e_lmvsprw", "VLE", ["RA", "D8"])
    # Load Multiple Volatile SRR Word: InstD8("e_lmvsrrw", "VLE", ["RA", "D8"])
    # Load Multiple Volatile CSRR Word: InstD8("e_lmvcsrrw", "VLE", ["RA", "D8"])
    # Load Multiple Volatile DSRR Word: InstD8("e_lmvdsrrw", "VLE", ["RA", "D8"])
    # Load Multiple Volatile MCSRR Word: InstD8("e_lmvmcsrrw", "VLE", ["RA", "D8"])
    elif inst.name in ["e_lmvsprw", "e_lmvsrrw", "e_lmvcsrrw", "e_lmvdsrrw", "e_lmvmcsrrw"]:
        assert len(inst.operands) == 2
        ra = inst.get_operand_value(oper_0)
        d8 = inst.get_operand_value(oper_1)

        special = []
        if inst.name == "e_lmvsprw":
            special = ["cr", "lr", "ctr", "xer"]
        elif inst.name == "e_lmvssrw":
            special = ["srr0", "srr1"]
        elif inst.name == "e_lmvcsrrw":
            special = ["csrr0", "csrr1"]
        elif inst.name == "e_lmvdsrrw":
            special = ["dsrr0", "dsrr1"]
        elif inst.name == "e_lmvmcsrrw":
            special = ["mcsrr0", "mcsrr1"]

        for ei0 in special:
            EA = get_EA(il, ra, d8)
            ei1 = il.set_reg(4, ei0, il.load(4, EA))
            il.append(ei1)
            d8 += 4

    # Store Multiple Word: InstD8("e_stmw", "VLE", ["RS", "RA", "D8"])
    elif inst.name == "e_stmw":
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d8 = inst.get_operand_value(oper_2)
        i = GPR.index(rs)
        EA = get_EA(il, ra, d8)
        while i <= 31:
            ei0 = il.store(4, EA, il.reg(4, GPR[i]))
            il.append(ei0)
            i += 1
            d8 += 4
            EA = get_EA(il, ra, d8)

    # Store Multiple Volatile GPR Word: InstD8("e_stmvgprw", "VLE", ["RA", "D8"])
    elif inst.name == "e_stmvgprw":
        assert len(inst.operands) == 2
        ra = inst.get_operand_value(oper_0)
        d8 = inst.get_operand_value(oper_1)

        EA = get_EA(il, ra, d8)
        ei0 = il.store(4, EA, il.reg(4, 'r0'))
        il.append(ei0)
        
        i = 3
        while i <= 12:
            d8 += 4
            EA = get_EA(il, ra, d8)
            ei0 = il.store(4, EA, il.reg(4, GPR[i]))
            il.append(ei0)
            i += 1
    
    # Store Multiple Volatile SPR Word: InstD8("e_stmvsprw", "VLE", ["RA", "D8"])
    # Store Multiple Volatile SRR Word: InstD8("e_stmvsrrw", "VLE", ["RA", "D8"])
    # Store Multiple Volatile CSRR Word: InstD8("e_stmvcsrrw", "VLE", ["RA", "D8"])
    # Store Multiple Volatile DSRR Word: InstD8("e_stmvdsrrw", "VLE", ["RA", "D8"])
    # Store Multiple Volatile MCSRR Word: InstD8("e_stmvmcsrrw", "VLE", ["RA", "D8"])
    elif inst.name in ["e_stmvsprw", "e_stmvsrrw", "e_stmvcsrrw", "e_stmvdsrrw", "e_stmvmcsrrw"]:
        assert len(inst.operands) == 2
        ra = inst.get_operand_value(oper_0)
        d8 = inst.get_operand_value(oper_1)

        special = []
        if inst.name == "e_stmvsprw":
            special = ["cr", "lr", "ctr", "xer"]
        elif inst.name == "e_stmvssrw":
            special = ["srr0", "srr1"]
        elif inst.name == "e_stmvcsrrw":
            special = ["csrr0", "csrr1"]
        elif inst.name == "e_stmvdsrrw":
            special = ["dsrr0", "dsrr1"]
        elif inst.name == "e_stmvmcsrrw":
            special = ["mcsrr0", "mcsrr1"]

        for ei0 in special:
            EA = get_EA(il, ra, d8)
            ei1 = il.store(4, EA, il.reg(4, ei0))
            il.append(ei1)
            d8 += 4

    else:
        il.append(il.unimplemented())
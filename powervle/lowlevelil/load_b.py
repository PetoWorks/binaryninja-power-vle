from binaryninja.lowlevelil import LowLevelILFunction, ExpressionIndex
from ..instruction import Instruction
from binaryninja.log import log_warn, log_error, log_debug

def byte_reverse_register(il: LowLevelILFunction, reg: str, size: int) -> ExpressionIndex:
    swap = None

    for src_idx in range(size):
        ei0 = il.reg(4, reg)
        dst_idx = size - src_idx - 1

        if dst_idx > src_idx:
            mask = il.const(4, 0xff << (src_idx * 8))
            ei0 = il.And(4, ei0, mask)
            ei0 = il.shift_left(4, ei0, il.const(4, (dst_idx - src_idx) * 8))
        elif src_idx > dst_idx:
            mask = il.const(4, 0xff << (dst_idx * 8))
            ei0 = il.logical_shift_right(4, ei0, il.const(4, (src_idx - dst_idx) * 8))
            ei0 = il.And(4, ei0, mask)
        
        if swap == None:
            swap = ei0
        else:
            swap = il.or_expr(4, swap, ei0)
    
    return swap

def lift_b_load_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
    
    if inst.name in ["lbzx", "lbzux"]:
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)

        EA = il.add(il.arch.address_size, il.reg(il.arch.address_size, ra), il.reg(il.arch.address_size, rb))
        ei0 = il.load(1, EA)
        ei0 = il.set_reg(il.arch.address_size, rt, il.zero_extend(il.arch.address_size, ei0))
        il.append(ei0)

        if inst.name == "lbzux":
            ei0 = il.set_reg(il.arch.address_size, ra, EA)
            il.append(ei0)
    
    elif inst.name in ["lhzx", "lhzux", "lhax", "lhaux"]:
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)

        EA = il.add(il.arch.address_size, il.reg(il.arch.address_size, ra), il.reg(il.arch.address_size, rb))
        ei0 = il.load(2, EA)
        if inst.name in ["lhzx", "lhzux"]:
            ei0 = il.set_reg(il.arch.address_size, rt, il.zero_extend(il.arch.address_size, ei0))
        else:
            ei0 = il.set_reg(il.arch.address_size, rt, il.sign_extend(il.arch.address_size, ei0))
        
        il.append(ei0)
        if inst.name in ["lhzux", "lhaux"]:
            ei0 = il.set_reg(il.arch.address_size, ra, EA)
            il.append(ei0)
    
    elif inst.name in ["lwzx", "lwzux"]:
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)

        EA = il.add(il.arch.address_size, il.reg(il.arch.address_size, ra), il.reg(il.arch.address_size, rb))
        ei0 = il.load(4, EA)
        ei0 = il.set_reg(il.arch.address_size, rt, ei0)
        il.append(ei0)

        if inst.name == "lwzux":
            ei0 = il.set_reg(il.arch.address_size, ra, EA)
            il.append(ei0)
    
    elif inst.name in ["lhbrx", "lwbrx"]:
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)

        EA = il.add(il.arch.address_size, il.reg(il.arch.address_size, ra), il.reg(il.arch.address_size, rb))
        if inst.name == "lhbrx":
            ei0 = il.load(2, EA)
            ei0 = il.zero_extend(il.arch.address_size, ei0)
        else:
            ei0 = il.load(4, EA)

        ei0 = il.set_reg(il.arch.address_size, rt, ei0)
        il.append(ei0)

        if inst.name == "lhbrx":
            swap = byte_reverse_register(il, rt, 2)
        else:
            swap = byte_reverse_register(il, rt, 4)

        il.append(il.set_reg(il.arch.address_size, rt, swap))

    # cache bypass decoration load word: InstX("lwdcbx", "B", ["RT", "RA", "RB"])
    elif inst.name == "lwdcbx":
        assert len(inst.operands) == 3
        rt = inst.get_operand_value(oper_0) # target register
        ra = inst.get_operand_value(oper_1) # decoration
        rb = inst.get_operand_value(oper_2) # effective address

        decoration = il.reg(4, ra)
        deco_cmd = (decoration >> 28) & 0xF
        EA = il.reg(4, rb)

        # Simple Load (SLD)
        if deco_cmd == 0x0:
            if (decoration >> 16) == 0:
                il.append(il.set_reg(4, rt, il.load(4, EA)))
            else:
                il.append(il.unimplemented())
        # Registers-and-memory exchange (SWAP)
        elif deco_cmd == 0x5:
            ei0 = il.set_reg(4, rt, il.load(4, EA))
            il.append(ei0)
            WD28 = decoration & 0x0FFFFFFF
            ei0 = il.zero_extend(4, il.const(4, WD28))
            ei1 = il.store(4, EA, ei0)
            il.append(ei1)
        # Load-and-Set-1 (LAS1)
        elif deco_cmd == 0x6:
            ei0 = il.load(4, EA)
            ei1 = il.set_reg(4, rt, ei0)
            il.append(ei1)
            BIT = (decoration >> 21) & 0x1F
            mask = il.const(4, 1 << (31 - BIT))
            ei0 = il.or_expr(4, ei0, mask)
            ei1 = il.store(4, EA, ei0)
            il.append(ei1)
        else:
            il.append(il.unimplemented())
        
    else:
        il.append(il.unimplemented())
from binaryninja.lowlevelil import LowLevelILFunction, ExpressionIndex
from ..instruction import Instruction

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

def lift_b_store_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
    
    if inst.name in ["stbx", "stbux"]:
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)

        EA = il.add(il.arch.address_size, il.reg(il.arch.address_size, ra), il.reg(il.arch.address_size, rb))
        ei0 = il.low_part(1, il.reg(il.arch.address_size, rs))
        ei0 = il.store(1, EA, ei0)
        il.append(ei0)

        if inst.name == "stbux":
            ei0 = il.set_reg(il.arch.address_size, ra, EA)
            il.append(ei0)
    
    elif inst.name in ["sthx", "sthux"]:
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)

        EA = il.add(il.arch.address_size, il.reg(il.arch.address_size, ra), il.reg(il.arch.address_size, rb))
        ei0 = il.low_part(2, il.reg(il.arch.address_size, rs))
        ei0 = il.store(2, EA, ei0)
        il.append(ei0)

        if inst.name == "sthux":
            ei0 = il.set_reg(il.arch.address_size, ra, EA)
            il.append(ei0)
    
    elif inst.name in ["stwx", "stwux"]:
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)

        EA = il.add(il.arch.address_size, il.reg(il.arch.address_size, ra), il.reg(il.arch.address_size, rb))
        ei0 = il.store(4, EA, il.reg(il.arch.address_size, rs))
        il.append(ei0)

        if inst.name == "stwux":
            ei0 = il.set_reg(il.arch.address_size, ra, EA)
            il.append(ei0)
    
    elif inst.name in ["sthbrx", "stwbrx"]:
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)

        EA = il.add(il.arch.address_size, il.reg(il.arch.address_size, ra), il.reg(il.arch.address_size, rb))
        if inst.name == "sthbrx":
            swap = byte_reverse_register(il, rs, 2)
            ei0 = il.store(2, EA, ei0)
        else:
            swap = byte_reverse_register(il, rs, 4)
            ei0 = il.store(4, EA, swap)
        
        il.append(ei0)       
            
    else:
        il.append(il.unimplemented())
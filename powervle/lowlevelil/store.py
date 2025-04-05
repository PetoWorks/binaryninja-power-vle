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

def lift_store_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0:   oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
    
    if inst.name in ["e_stb", "e_sth", "e_stw"]:
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d = inst.get_operand_value(oper_2)

        ei0 = None
        EA = il.add(4, il.reg(4, ra), il.const(4, d))

        if inst.name == "e_stb":    # Byte
            ei0 = il.low_part(1, il.reg(4, rs))
            ei0 = il.store(1, EA, ei0)
        elif inst.name == "e_sth":  # Half Word
            ei0 = il.low_part(2, il.reg(4, rs))
            ei0 = il.store(2, EA, ei0)
        else:                       # Word
            ei0 = il.store(4, EA, il.reg(4, rs))
        
        il.append(ei0)
    
    elif inst.name in ["e_stbu", "e_sthu", "e_stwu"]:
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        d8 = inst.get_operand_value(oper_2)

        EA = il.add(4, il.reg(4, ra), il.const(4, d8))
        ei0 = None

        if inst.name == "e_stbu":   # Byte
            ei0 = il.low_part(1, il.reg(4, rs))
            ei0 = il.store(1, EA, ei0)
        elif inst.name == "e_sthu": # Half Word
            ei0 = il.low_part(2, il.reg(4, rs))
            ei0 = il.store(2, EA, ei0)
        else:                       # Word
            ei0 = il.store(4, EA, il.reg(4, rs))
              
        il.append(ei0)

        ei0 = il.set_reg(4, ra, EA)
        il.append(ei0)
    

    elif inst.name in ["se_stb", "se_sth", "se_stw"]:
        assert len(inst.operands) == 3
        rz = inst.get_operand_value(oper_0)
        rx = inst.get_operand_value(oper_1)
        sd4 = inst.get_operand_value(oper_2)

        EA = il.add(4, il.reg(4, rx), il.const(4, sd4))
        ei0 = None

        if inst.name == "se_stb":   # Byte
            ei0 = il.low_part(1, il.reg(4, rz))
            ei0 = il.store(1, EA, ei0)
        elif inst.name == "se_sth": # Half Word
            ei0 = il.low_part(2, il.reg(4, rz))
            ei0 = il.store(2, EA, ei0)
        else:                       # Word
            ei0 = il.store(4, EA, il.reg(4, rz))
        
        il.append(ei0)
    
    elif inst.name in ["stbx", "stbux"]:
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
    
    # Vector Store Doubleword of Dobuleword: InstEVX("evstdd", "SP", ["RS", "RA", "UI_16_21"])
    elif inst.name == "evstdd":
        assert len(inst.operands) == 3
        rs = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        ui = inst.get_operand_value(oper_2)

        if ra == 0:
            EA = il.zero_extend(4, il.const(4, ui*8))
        else :
            EA = il.add(4, il.reg(4, ra), il.zero_extend(4, il.const(4, ui*8)))
        ei0 = il.store(4, EA, il.reg(4, rs))
        il.append(ei0)
        
    else:
        il.append(il.unimplemented())
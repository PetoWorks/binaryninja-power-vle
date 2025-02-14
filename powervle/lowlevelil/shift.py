from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

INT32_MAX = 0xffffffff
uint32 = lambda num: num & INT32_MAX

def gen_mask(mb: int, me: int) -> int:
    mask_begin = uint32(INT32_MAX >> mb)
    mask_end = uint32(INT32_MAX << (31 - me))

    return (mask_begin & mask_end) if mb <= me else (mask_begin | mask_end)

def lift_shift_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):         # get operands with length of operands
        if i == 0:   oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
        elif i == 4: oper_4 = inst.operands[4]
    
    if inst.name == "e_rlwimi":     # Rotate Left Word Immediate then Mask Insert
        assert len(inst.operands) == 5
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        sh = inst.get_operand_value(oper_2)
        mb = inst.get_operand_value(oper_3)
        me = inst.get_operand_value(oper_4)

        mask = gen_mask(mb, me)
        ei0 = il.reg(4, rs)

        if sh != 0:
            if (mask & (uint32(INT32_MAX >> (32 - sh)))) == 0:
                ei0 = il.shift_left(4, ei0, il.const(4, sh))

            elif (mask & (uint32(INT32_MAX << sh))) == 0:
                ei0 = il.logical_shift_right(4, ei0, il.const(4, 32 - sh))

            else:
                ei0 = il.rotate_left(4, ei0, il.const(4, sh))
        
        ei0 = il.and_expr(4, ei0, il.const(4, mask))

        invert_mask = uint32(~mask)    
        ei1 = il.and_expr(4, il.reg(4, ra), il.const(4, invert_mask))

        ei0 = il.or_expr(4, ei0, ei1)
        ei0 = il.set_reg(4, ra, ei0)

        il.append(ei0)
    
    elif inst.name == "e_rlwinm":       # Roate Left Word Immediate then AND with mask
        assert len(inst.operands) == 5
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        sh = inst.get_operand_value(oper_2)
        mb = inst.get_operand_value(oper_3)
        me = inst.get_operand_value(oper_4)

        mask = gen_mask(mb, me)
        ei0 = il.reg(4, rs)

        if sh != 0:
            if (mask & uint32(INT32_MAX >> (32 - sh))) == 0:
                ei0 = il.shift_left(4, ei0, il.const(4, sh))

            elif (mask & uint32(INT32_MAX << sh)) == 0:
                ei0 = il.logical_shift_right(4, ei0, il.const(4, 32 - sh))
            
            else:
                ei0 = il.rotate_left(4, ei0, il.const(4, sh))

        if mask != INT32_MAX:
            ei0 = il.and_expr(4, ei0, il.const(4, mask))
        
        ei0 = il.set_reg(4, ra, ei0)
        il.append(ei0)
    
    # se_slwi : Shift Left Word Immediate Short Form
    # se_srwi : Shift Right Word Immediate Short Form
    elif inst.name in ["se_slwi", "se_srwi"]:
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ui5 = inst.get_operand_value(oper_1)

        if inst.name == "se_slwi":
            ei0 = il.shift_left(4, il.reg(4, rx), il.const(4, ui5))
        else:
            ei0 = il.logical_shift_right(4, il.reg(4, rx), il.const(4, ui5))

        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    
    # se_slw : Shift Left Word Immediate Short Form
    # se_srw : Shift Right Word Immediate Short Form
    elif inst.name in ["se_slw", "se_srw"]:
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ry = inst.get_operand_value(oper_1)

        ei0 = il.and_expr(4, il.reg(4, ry), il.const(4, 0x3f))
        if inst.name == "se_slw":
            ei0 = il.shift_left(4, il.reg(4, rx), ei0)
        else:
            ei0 = il.logical_shift_right(4, il.reg(4, rx), ei0)

        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    
    elif inst.name == "se_srawi":   # Shift Right Algebraic Word Immediate
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ui5 = inst.get_operand_value(oper_1)
        
        ei0 = il.arith_shift_right(4, il.reg(4, rx), il.const(4, ui5), 'xer_ca')
        ei0 = il.set_reg(4, rx, ei0)
        il.append(ei0)
    
    elif inst.name == "se_sraw":    # Shift Right Algebraic Word
        assert len(inst.operands) == 2
        rx = inst.get_operand_value(oper_0)
        ry = inst.get_operand_value(oper_1)

        ei0 = il.and_expr(4, il.reg(4, ry), il.const(4, 0x1f))
        ei0 = il.arith_shift_right(4, il.reg(4, rx), ei0, 'xer_ca')
        ei0 = il.set_reg(4, rx, ei0)

        il.append(ei0)
    
    # Rotate Left Word: InstX("e_rlw", "VLE",  ["RA", "RS", "RB", "Rc"])
    # Rotate Left Word Immediate: InstX("e_rlwi", "VLE",  ["RA", "RS", "SH", "Rc"])
    elif inst.name in ["e_rlw", "e_rlwi"]:
        assert len(inst.operands) == 4
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        rc = inst.get_operand_value(oper_3)
        if inst.name == "e_rlw":
            ei0 = il.reg(1, inst.get_operand_value(oper_2)) # rb
        else : # "e_rlwi"
            ei0 = il.const(4, inst.get_operand_value(oper_2)) # sh
        ei0 = il.rotate_left(4, il.reg(4, rs), ei0)
        il.set_reg(4, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)

    # Shift Left Word Immediate: InstX("e_slwi", "VLE",  ["RA", "RS", "SH", "Rc"])
    # Shift Right Word Immediate: InstX("e_srwi", "VLE", ["RA", "RS", "SH", "Rc"])
    elif inst.name in ["e_slwi", "e_srwi"]:
        assert len(inst.operands) == 4
        ra = inst.get_operand_value(oper_0)
        rs = inst.get_operand_value(oper_1)
        sh = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        if inst.name == "e_slwi":
            ei0 = il.shift_left(4, il.reg(4, rs), il.const(4, sh))
        else:
            ei0 = il.logical_shift_right(4, il.reg(4, rs), il.const(4, sh))

        ei0 = il.set_reg(4, ra, ei0, 'cr0s' if rc else None)
        il.append(ei0)

    else:
        il.append(il.unimplemented())
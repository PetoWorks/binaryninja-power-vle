from binaryninja.lowlevelil import LowLevelILFunction, ExpressionIndex
from ..instruction import Instruction

def lift_b_add_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
        elif i == 4: oper_4 = inst.operands[4]
    
    if inst.name in ["add", "addo"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        oe = inst.get_operand_value(oper_3)
        rc = inst.get_operand_value(oper_4)

        ei0 = il.add(
            il.arch.address_size,
            il.reg(il.arch.address_size, ra),
            il.reg(il.arch.address_size, rb),
            'xer_ov_so' if oe == 1 else None
        )

        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name in ["addc", "addco", "adde", "addeo"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        oe = inst.get_operand_value(oper_3)
        rc = inst.get_operand_value(oper_4)

        flags = 'xer_ca'
        if oe == 1:
            flags = 'xer'
        
        if inst.name in ["addc", "addco"]:
            ei0 = il.add(
                il.arch.address_size,
                il.reg(il.arch.address_size, ra),
                il.reg(il.arch.address_size, rb),
                flags
            )
        else:
            ei0 = il.add_carry(
                il.arch.address_size,
                il.reg(il.arch.address_size, ra),
                il.reg(il.arch.address_size, rb),
                il.flag('xer_ca'),
                flags
            )

        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name in ["addme", "addmeo", "addze", "addzeo"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        oe = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        if inst.name in ["addme", "addmeo"]:
            ei0 = il.const(il.arch.address_size, -1)
        else:
            ei0 = il.const(il.arch.address_size, 0)

        flags = 'xer_ca'
        if oe == 1:
            flags = 'xer'
        
        ei0 = il.add_carry(
            il.arch.address_size,
            il.reg(il.arch.address_size, ra),
            ei0,
            il.flag(flags),
            flags
        )

        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc == 1 else None)
        il.append(ei0)
    
    else:
        il.append(il.unimplemented())

def lift_b_sub_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
        elif i == 4: oper_4 = inst.operands[4]
    
    if inst.name in ["subf", "subfo"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        oe = inst.get_operand_value(oper_3)
        rc = inst.get_operand_value(oper_4)

        ei0 = il.sub(
            il.arch.address_size,
            il.reg(il.arch.address_size, rb),
            il.reg(il.arch.address_size, ra),
            'xer_ov_so' if oe == 1 else None
        )

        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name in ["subfc", "subfco"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        oe = inst.get_operand_value(oper_3)
        rc = inst.get_operand_value(oper_4)

        flags = 'xer_ca'
        if oe == 1:
            flags = 'xer'

        ei0 = il.sub(
            il.arch.address_size,
            il.reg(il.arch.address_size, rb),
            il.reg(il.arch.address_size, ra),
            flags
        )

        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name in ["subfe", "subfeo"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        oe = inst.get_operand_value(oper_3)
        rc = inst.get_operand_value(oper_4)

        flags = 'xer_ca'
        if oe == 1:
            flags = 'xer'
        
        ei0 = il.sub_borrow(
            il.arch.address_size,
            il.reg(il.arch.address_size, rb),
            il.reg(il.arch.address_size, ra),
            il.flag('xer_ca'),
            flags
        )

        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name in ["subfme", "subfmeo", "subfze", "subfzeo"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        oe = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        flags = 'xer_ca'
        if oe == 1:
            flags = 'xer'

        if inst.name in ["subfme", "subfmeo"]:
            ei0 = il.const(il.arch.address_size, -1)
        else:
            ei0 = il.const(il.arch.address_size, 0)
        
        ei0 = il.sub_borrow(
            il.arch.address_size,
            ei0,
            il.reg(il.arch.address_size, ra),
            il.flag('xer_ca'),
            flags
        )

        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc == 1 else None)
        il.append(ei0)
    
    else:
        il.append(il.unimplemented())

def lift_b_neg_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]

    if inst.name in ["neg", "nego"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        oe = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        flags = None
        if oe == 1:
            flags = 'xer_ov_so'
        
        ei0 = il.neg_expr(
            il.arch.address_size,
            il.reg(il.arch.address_size, ra),
            flags
        )

        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc else None)
        il.append(ei0)

def lift_b_mul_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
        elif i == 4: oper_4 = inst.operands[4]
    
    if inst.name in ["mullw", "mullwo"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        oe = inst.get_operand_value(oper_3)
        rc = inst.get_operand_value(oper_4)

        flags = None
        if oe == 1:
            flags = 'xer_ov_so'

        ei0 = il.mult(
            il.arch.address_size,
            il.reg(il.arch.address_size, ra),
            il.reg(il.arch.address_size, rb),
            flags
        )
        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc else None)
        il.append(ei0)
    
    elif inst.name in ["mulhw", "mulhwu"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        rc = inst.get_operand_value(oper_3)

        if inst.name == "mulhw":
            ei0 = il.mult_double_prec_signed(
                il.arch.address_size,
                il.reg(il.arch.address_size, ra),
                il.reg(il.arch.address_size, rb),
            )
        else:
            ei0 = il.mult_double_prec_unsigned(
                il.arch.address_size,
                il.reg(il.arch.address_size, ra),
                il.reg(il.arch.address_size, rb),
            )

        ei0 = il.low_part(4, il.logical_shift_right(8, ei0, il.const(1, 32)))
        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc else None)

        il.append(ei0)
    
    else:
        il.append(il.unimplemented())

def lift_b_div_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]
        elif i == 2: oper_2 = inst.operands[2]
        elif i == 3: oper_3 = inst.operands[3]
        elif i == 4: oper_4 = inst.operands[4]
    
    if inst.name in ["divw", "divwo", "divwu", "divwuo"]:
        rt = inst.get_operand_value(oper_0)
        ra = inst.get_operand_value(oper_1)
        rb = inst.get_operand_value(oper_2)
        oe = inst.get_operand_value(oper_3)
        rc = inst.get_operand_value(oper_4)

        flags = None
        if oe == 1:
            flags = 'xer_ov_so'

        if inst.name in ["divw", "divwo"]:
            ei0 = il.div_signed(
                il.arch.address_size,
                il.reg(il.arch.address_size, ra),
                il.reg(il.arch.address_size, rb),
                flags
            )
        else:
            ei0 = il.div_unsigned(
                il.arch.address_size,
                il.reg(il.arch.address_size, ra),
                il.reg(il.arch.address_size, rb),
                flags
            )

        ei0 = il.set_reg(il.arch.address_size, rt, ei0, 'cr0s' if rc else None)
        il.append(ei0)
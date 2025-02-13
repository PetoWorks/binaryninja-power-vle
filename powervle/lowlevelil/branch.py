from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

#--------------------------- Chapter 4.2 Branch Instructions ---------------------------#

def lift_bd24_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    if not isinstance(il, LowLevelILFunction):
        print(f"[Error] Expected LowLevelILFunction, but got {type(il)}")
        return 
    
    bd24 = inst.get_field_value("BD24")
    lk = inst.get_field_value("LK") if "LK" in inst.operands else 0

    if bd24 is None:
        il.append(il.unimplemented())
        return

    offset = il.sign_extend(4, il.const(4, bd24 << 1))
    target_addr = il.current_address + offset
    next_instr_addr = il.current_address + 4

    if int(lk) == 1:
        il.append(il.set_reg(4, "lr", next_instr_addr))
        il.append(il.call(il.const(4, target_addr)))
    else:
        il.append(il.jump(il.const(4, target_addr)))

def lift_bd8_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    if not isinstance(il, LowLevelILFunction):
        print(f"[Error] Expected LowLevelILFunction, but got {type(il)}")
        return
    
    bd8 = inst.get_field_value("BD8")
    lk = inst.get_field_value("LK") if "LK" in inst.operands else 0  

    if bd8 is None:
        il.append(il.unimplemented())
        return

    offset = il.sign_extend(4, il.const(4, bd8 << 1))
    target_addr = il.current_address + offset
    next_instr_addr = il.current_address + 2

    if int(lk) == 1:
        il.append(il.set_reg(4, "lr", next_instr_addr))
        il.append(il.call(il.const(4, target_addr)))
    else:
        il.append(il.jump(il.const(4, target_addr)))

def lift_bd15_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    if not isinstance(il, LowLevelILFunction):
        print(f"[Error] Expected LowLevelILFunction, but got {type(il)}")
        return

    bo32 = inst.get_field_value("BO32")
    bi32 = inst.get_field_value("BI32")
    bd15 = inst.get_field_value("BD15")
    lk = inst.get_field_value("LK")

    if bo32 is None or bi32 is None or bd15 is None:
        il.append(il.unimplemented())
        return
    
    offset = (bd15 << 1)
    if bd15 & (1 << 14):
        offset -= (1 << 15)
    target_addr = il.current_address + offset
    next_instr_addr = il.current_address + 4


    if (bo32 & 1) != 0:
        new_ctr = il.sub(4, il.reg(4, "ctr"), il.const(4, 1))
        il.append(il.set_reg(4, "ctr", new_ctr))
   
    ctr_ok = il.or_expr(4,
        il.compare_equal(4, il.const(4, bo32 & 1), il.const(4, 0)),  
        il.xor_expr(4, il.compare_not_equal(4, il.reg(4, "ctr"), il.const(4, 0)), il.const(4, (bo32 >> 1) & 1))
    )

    cr_field_index = bi32 // 4
    bit_index = bi32 % 4
    flag_suffixes = ["lt", "gt", "eq", "so"]
    cond_flag = f"cr{cr_field_index}{flag_suffixes[bit_index]}"

    cond_ok = il.or_expr(4,
        il.compare_equal(4, il.const(4, bo32 & 1), il.const(4, 0)),  
        il.compare_equal(4, il.flag(cond_flag), il.const(4, (bo32 >> 1) & 1))  
    )
    branch_cond = il.and_expr(4, ctr_ok, cond_ok)
    
    if lk == 1:
        il.append(il.set_reg(4, "lr", il.const(4, next_instr_addr)))
        il.append(il.call(il.const(4, next_instr_addr)))
    else:
        il.append(il.if_expr(branch_cond, il.jump(il.const(4, target_addr)), il.jump(il.const(4, next_instr_addr))))

def lift_bd8_cond_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    if not isinstance(il, LowLevelILFunction):
        print(f"[Error] Expected LowLevelILFunction, but got {type(il)}")
        return

    bo16 = inst.get_field_value("BO16")
    bi16 = inst.get_field_value("BI16")
    if bo16 is None or bi16 is None:
        il.append(il.unimplemented())
        return
    # bd8필드를 get_field_value로 가져오면 AttributeError 발생
    bd8 = inst.get_operand_value("BD8")
    if bd8 is None:
        il.append(il.unimplemented())
        return

    offset = (bd8 << 1)
    if bd8 & (1 << 7):
        offset -= (1 << 8)

    target_addr = il.current_address + offset
    next_instr_addr = il.current_address + 2

    cr_field_index = bi16 // 4
    bit_index = bi16 % 4
    flag_suffixes = ["lt", "gt", "eq", "so"]
    cond_flag = f"cr{cr_field_index}{flag_suffixes[bit_index]}"

    cond_ok = il.compare_equal(1, il.flag(cond_flag), il.const(1, bo16 & 1))

    lk = inst.get_field_value("LK") if "LK" in inst.operands else 0
    if int(lk) == 1:
        il.append(il.set_reg(4, "lr", il.const(4, next_instr_addr)))
        il.append(il.if_expr(cond_ok, il.call(il.const(4, target_addr)), il.call(il.const(4, next_instr_addr))))
    else:
        il.append(il.if_expr(cond_ok, il.jump(il.const(4, target_addr)), il.jump(il.const(4, next_instr_addr))))

def lift_branch_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    lk = inst.get_field_value("LK") if "LK" in inst.operands else 0

    target_expr = il.and_expr(4, il.reg(4, "ctr"), il.const(4, 0xFFFFFFFE))
    next_instr_addr = il.current_address + 2
    if int(lk) == 1:
        il.append(il.set_reg(4, "lr", il.const(4, next_instr_addr)))
        il.append(il.call(il.const(4, target_expr)))
    else: 
        il.append(il.jump(il.const(4, target_expr)))

def lift_branch_lr_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    lk = inst.get_field_value("LK") if "LK" in inst.operands else 0
    
    orig_lr = il.reg(4, "lr")
    target_addr = il.and_expr(4, orig_lr, il.const(4, 0xFFFFFFFE))
    next_instr_addr = il.current_address + 2
    if int(lk) == 1:
        il.append(il.set_reg(4, "lr", il.const(4, next_instr_addr)))
        il.append(il.call(il.const(4, target_addr)))
    else:
        il.append(il.jump(il.const(4, target_addr)))
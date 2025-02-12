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
    # BD24 || 0b0 처리 및 sign-extend
    offset = il.sign_extend(4, il.const(4, bd24 << 1))
    target_addr = il.add(4, il.const(4, il.current_address), offset)
    next_instr_addr = il.add(4, il.const(4, il.current_address), il.const(4, 4))
    if int(lk) == 1:
        il.append(il.set_reg(4, "lr", next_instr_addr))
    il.append(il.jump(target_addr))

def lift_bd8_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    if not isinstance(il, LowLevelILFunction):
        print(f"[Error] Expected LowLevelILFunction, but got {type(il)}")
        return
    
    bd8 = inst.get_field_value("BD8")
    lk = inst.get_field_value("LK") if "LK" in inst.operands else 0  

    if bd8 is None:
        il.append(il.unimplemented())
        return
    # 8비트 -> 32비트 sign-extend
    offset = il.sign_extend(4, il.const(4, bd8 << 1))
    target_addr = il.add(4, il.const(4, il.current_address), offset)
    next_instr_addr = il.add(4, il.const(4, il.current_address), il.const(4, 2))  

    if int(lk) == 1:
        il.append(il.set_reg(4, "lr", next_instr_addr))
    il.append(il.jump(target_addr))

def lift_bd15_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    if not isinstance(il, LowLevelILFunction):
        print(f"[Error] Expected LowLevelILFunction, but got {type(il)}")
        return
    # 필드 값 추출
    bo32 = inst.get_field_value("BO32")
    bi32 = inst.get_field_value("BI32")
    bd15 = inst.get_field_value("BD15")
    lk = inst.get_field_value("LK")

    if bo32 is None or bi32 is None or bd15 is None:
        il.append(il.unimplemented())
        return
    
    offset = il.sign_extend(4, il.const(4, bd15 << 1))
    target_addr = il.add(4, il.const(4, il.current_address), offset)
    next_instr_addr = il.add(4, il.const(4, il.current_address), il.const(4, 4)) 

    # BO32_0이 1이면 CTR 감소
    if (bo32 & 1) != 0:
        new_ctr = il.sub(4, il.reg(4, "CTR"), il.const(4, 1))
        il.append(il.set_reg(4, "CTR", new_ctr))
   
    ctr_ok = il.or_expr(4,
        il.compare_equal(4, il.const(4, bo32 & 1), il.const(4, 0)),  
        il.xor_expr(4, il.compare_not_equal(4, il.reg(4, "CTR"), il.const(4, 0)), il.const(4, (bo32 >> 1) & 1))
    )

    cr_field_index = bi32 // 4
    bit_index = bi32 % 4
    flag_suffixes = ["lt", "gt", "eq", "so"]
    cond_flag = f"cr{cr_field_index}{flag_suffixes[bit_index]}"

    cond_ok = il.or_expr(4,
        il.compare_equal(4, il.const(4, bo32 & 1), il.const(4, 0)),  # BO32_0 == 0이면 무조건 실행
        il.compare_equal(4, il.flag(cond_flag), il.const(4, (bo32 >> 1) & 1))  # CR(BI32+32)와 BO32_1 비교
    )
    branch_cond = il.and_expr(4, ctr_ok, cond_ok)
    il.append(il.if_expr(branch_cond, il.jump(target_addr), il.jump(next_instr_addr)))
    if lk == 1:
        il.append(il.set_reg(4, "lr", next_instr_addr))

def lift_bd8_cond_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    if not isinstance(il, LowLevelILFunction):
        print(f"[Error] Expected LowLevelILFunction, but got {type(il)}")
        return

    # 피연산자 이름 대신에 실제 필드 값 가져오도록 수정함
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

    offset = il.sign_extend(4, il.const(1, bd8 << 1))

    target_addr = il.add(4, il.const(4, il.current_address), offset)
    next_instr_addr = il.add(4, il.const(4, il.current_address), il.const(4, 2))

    cr_field_index = bi16 // 4
    bit_index = bi16 % 4
    flag_suffixes = ["lt", "gt", "eq", "so"]
    cond_flag = f"cr{cr_field_index}{flag_suffixes[bit_index]}"

    cond_ok = il.compare_equal(1, il.flag(cond_flag), il.const(1, bo16 & 1))
    il.append(il.if_expr(cond_ok, il.jump(target_addr), il.jump(next_instr_addr)))

    lk = inst.get_field_value("LK") if "LK" in inst.operands else 0
    if int(lk) == 1:
        il.append(il.set_reg(4, "lr", next_instr_addr))

def lift_branch_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    size = 2
    lk = inst.get_field_value("LK") if "LK" in inst.operands else 0
    # CTR_0:62 || 0b0 구현
    target_expr = il.and_expr(4, il.reg(4, "ctr"), il.const(4, ~1))
    if int(lk) == 1:
        next_instr_addr = il.add(size, il.const(size, il.current_address), il.const(size, 2))
        il.append(il.set_reg(4, "lr", next_instr_addr))
    il.append(il.jump(target_expr))

def lift_branch_lr_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    size = 2
    lk = inst.get_field_value("LK") if "LK" in inst.operands else 0
    
    orig_lr = il.reg(4, "lr")
    target_addr = il.and_expr(4, orig_lr, il.const(4, ~1))
    
    if int(lk) == 1:
        next_instr_addr = il.add(size, il.const(size, il.current_address), il.const(size, 2))
        il.append(il.set_reg(4, "lr", next_instr_addr))
    il.append(il.jump(target_addr))
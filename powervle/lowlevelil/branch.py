from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

#--------------------------- Chapter 4.2 Branch Instructions ---------------------------#

def lift_bd24_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    # print(f"[DEBUG] lift_bd24_branch_instructions called with il={type(il)}, inst={type(inst)}")
    bd24_value = inst.get_operand_value("target_addr")
    if bd24_value is None:
        il.append(il.unimplemented())
        return
    if isinstance(bd24_value, str):
        # print(f"[INFO] Handling symbolic branch target: {bd24_value}")
        try:
            addr = int(bd24_value, 0)
        except ValueError:
            print(f"[ERROR] Unable to convert symbolic branch target to an integer: {bd24_value}")
            il.append(il.unimplemented())
            return
        target_label = il.get_label_for_address(il.arch, addr)
        if target_label is None:
            print(f"[ERROR] No label found for {bd24_value}")
            il.append(il.unimplemented())
            return
        il.append(il.jump(target_label))
        return

    bd24 = bd24_value
    # print(f"[DEBUG] Converted bd24 value: {bd24}, type: {type(bd24)}")
    lk = inst.get_operand_value("LK")
    if lk is None:
        lk = 0
    offset = (bd24 << 1) 
    target_addr = il.add(4, il.current_address, il.const(4, offset))
    next_instr_addr = il.add(4, il.current_address, il.const(4, 4))

    if int(lk) == 1:
        il.append(il.set_reg(4, "lr", next_instr_addr))

    il.append(il.jump(target_addr))

def lift_bd8_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    if not isinstance(il, LowLevelILFunction):
        print(f"[Error] Expected LowLevelILFunction, but got {type(il)}")
        return

    if not hasattr(inst, "operands"):
        il.append(il.unimplemented()) 
        return
    bd8 = inst.get_operand_value("target_addr")
    lk = inst.get_operand_value("LK") if "LK" in inst.operands else 0  

    if bd8 is None:
        il.append(il.unimplemented())
        return
    target_addr = il.const(4, bd8)
    
    next_instr_addr = il.add(4, il.current_address, il.const(4, 2))  

    if int(lk or 0) == 1:
        il.append(il.set_reg(4, "lr", next_instr_addr))

    il.append(il.jump(target_addr))

def lift_bd15_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    if not isinstance(il, LowLevelILFunction):
        print(f"[Error] Expected LowLevelILFunction, but got {type(il)}")
        return

    if not hasattr(inst, "operands"):
        il.append(il.unimplemented())
        return

    bo32 = inst.operands[0] if len(inst.operands) > 0 else 0
    bi32 = inst.operands[1] if len(inst.operands) > 1 else 0
    bd15 = inst.operands[2] if len(inst.operands) > 2 else None
    lk = inst.operands[3] if len(inst.operands) > 3 else 0  

    if bd15 is None:
        il.append(il.unimplemented())
        return

    offset = (bd15 << 1) | 0x0
    target_addr = il.add(4, il.current_address, il.const(4, offset))

    next_instr_addr = il.add(4, il.current_address, il.const(4, 4)) 

    if bo32 == 1:
        il.append(il.set_reg(4, "CTR", il.sub(4, il.reg(4, "CTR"), il.const(4, 1))))

    ctr_ok = il.or_expr(4, il.compare_equal(4, il.const(4, bo32), il.const(4, 0)),
                        il.xor_expr(4, il.compare_not_equal(4, il.reg(4, "CTR"), il.const(4, 0)), 
                                    il.const(4, (bo32 >> 1) & 1)))

    cond_ok = il.or_expr(4, il.compare_equal(4, il.const(4, bo32), il.const(4, 0)),
                         il.compare_equal(4, il.reg(4, f"CR{bi32 + 32}"), il.const(4, (bo32 >> 1) & 1)))

    branch_cond = il.and_expr(4, ctr_ok, cond_ok)

    il.append(il.if_expr(branch_cond, il.jump(target_addr), il.jump(next_instr_addr)))

    if lk == 1:
        il.append(il.set_reg(4, "LR", next_instr_addr))

def lift_bd8_cond_branch_instructions(inst: Instruction, il: LowLevelILFunction):
    if not isinstance(il, LowLevelILFunction):
        print(f"[Error] Expected LowLevelILFunction, but got {type(il)}")
        return

    if not hasattr(inst, "operands"):
        il.append(il.unimplemented())
        return

    bo16 = inst.operands[0] if len(inst.operands) > 0 else 0
    bi16 = inst.operands[1] if len(inst.operands) > 1 else 0
    bd8 = inst.operands[2] if len(inst.operands) > 2 else None

    if bd8 is None:
        il.append(il.unimplemented())
        return

    offset = (bd8 << 1) | 0x0
    target_addr = il.add(4, il.current_address, il.const(4, offset))

    next_instr_addr = il.add(4, il.current_address, il.const(4, 2))  

    cond_ok = il.compare_equal(4, il.reg(4, f"CR{bi16 + 32}"), il.const(4, bo16))

    il.append(il.if_expr(cond_ok, il.jump(target_addr), il.jump(next_instr_addr)))

def lift_branch_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    arch_size = il.arch.address_size
    lk = inst.get_operand_value("LK") if "LK" in inst.operands else 0
    mask = (1 << (arch_size * 8)) - 2
    target_expr = il.and_expr(arch_size, il.reg(arch_size, "ctr"), il.const(arch_size, mask))
    if int(lk) == 1:
        next_instr_addr = il.add(arch_size, il.current_address, il.const(arch_size, 2))
        il.append(il.set_reg(arch_size, "lr", next_instr_addr))
    il.append(il.jump(target_expr))

def lift_branch_lr_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    arch_size = il.arch.address_size
    lk = inst.get_operand_value("LK")
    if lk is None:
        lk = 0
    orig_lr = il.reg(arch_size, "lr")

    mask = (1 << (arch_size * 8)) - 2  
    target_addr = il.and_expr(arch_size, orig_lr, il.const(arch_size, mask))
    
    if int(lk) == 1:
        next_instr_addr = il.add(arch_size, il.current_address, il.const(arch_size, 2))
        il.append(il.set_reg(arch_size, "lr", next_instr_addr))
    il.append(il.jump(target_addr))
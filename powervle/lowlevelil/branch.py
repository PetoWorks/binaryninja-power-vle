from binaryninja.lowlevelil import LowLevelILFunction, LowLevelILLabel
from ..instruction import Instruction


def lift_branch_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    target_address = inst.get_operand_value("target_addr")
    next_address = inst.addr + inst.length
    if not target_address:
        il.append(il.unimplemented())
        return
    
    if inst.get_operand_value("LK") == 0:
        il.append(il.jump(il.const_pointer(il.arch.address_size, target_address)))
    else:
        il.append(il.set_reg(il.arch.address_size, "lr", il.const_pointer(il.arch.address_size, next_address)))
        il.append(il.call(il.const_pointer(il.arch.address_size, target_address)))


def lift_cond_branch_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    target_address = inst.get_operand_value("target_addr")
    if not target_address:
        il.append(il.unimplemented())
        return
    
    next_address = inst.addr + inst.length

    if target_address == next_address:
        il.append(il.nop())
        return
    
    bc = inst.branch_condition
    negate = False
    crnum = inst.branch_condition_index

    if bc == "ge":
        negate = True
        flag = "lt"
    elif bc == "le":
        negate = True
        flag = "gt"
    elif bc == "ne":
        negate = True
        flag = "eq"
    elif bc == "lt":
        flag = "lt"
    elif bc == "gt":
        flag = "gt"
    elif bc == "eq":
        flag = "eq"
    elif bc == "so":
        flag = "so"
    elif bc == "ns":
        negate = True
        flag = "so"
    elif bc == "dz":
        cond = il.compare_equal(4, il.reg(4, "ctr"), il.const(4, 0))
    elif bc == "dnz":
        cond = il.compare_not_equal(4, il.reg(4, "ctr"), il.const(4, 0))
    elif bc == "dnzt":
        # Todo ?
        il.append(il.unimplemented())
    else: 
        il.append(il.unimplemented())
        return

    if bc in ["ge", "le", "ne", "lt", "gt", "eq", "so", "ns"]:
        cond = il.flag(f"cr{crnum}{flag}")
        if negate:
            cond = il.not_expr(0, cond)

    if inst.get_operand_value("LK") == 1:
        il.append(il.set_reg(il.arch.address_size, "lr", il.const_pointer(il.arch.address_size, next_address)))
    
    # cond = il.flag(f"cr{crnum}{flag}")
    # if negate:
    #     cond = il.not_expr(0, cond)
    
    new_true_label = False
    true_label = il.get_label_for_address(il.arch, target_address)
    if true_label == None:
        new_true_label = True
        true_label = LowLevelILLabel()
    
    new_false_label = False
    false_label = il.get_label_for_address(il.arch, next_address)
    if false_label == None:
        new_false_label = True
        false_label = LowLevelILLabel()

    il.append(il.if_expr(cond, true_label, false_label))
    
    if new_true_label:
        il.mark_label(true_label)
        il.append(il.jump(il.const_pointer(il.arch.address_size, target_address)))
    
    if new_false_label:
        il.mark_label(false_label)


def lift_indirect_branch_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    next_address = inst.addr + inst.length
    if inst.name == "se_blr":
        if inst.get_operand_value("LK"):
            il.append(il.set_reg(il.arch.address_size, "lr", il.const_pointer(il.arch.address_size, next_address)))
            il.append(il.ret(il.reg(il.arch.address_size, "lr")))
        else:
            il.append(il.ret(il.reg(il.arch.address_size, "lr")))
    elif inst.name == "se_bctr":
        if inst.get_operand_value("LK"):
            il.append(il.call(il.reg(il.arch.address_size, "ctr")))
        else:
            il.append(il.jump(il.reg(il.arch.address_size, "ctr")))
    else:
        il.append(il.unimplemented())

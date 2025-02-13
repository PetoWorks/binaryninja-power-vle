from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

def lift_cr_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    bt = inst.get_field_value("BT")
    ba = inst.get_field_value("BA")
    bb = inst.get_field_value("BB")

    if bt is None or ba is None or bb is None:
        il.append(il.unimplemented())
        return

    ba_flag = f"cr{ba // 4}{['lt', 'gt', 'eq', 'so'][ba % 4]}"
    bb_flag = f"cr{bb // 4}{['lt', 'gt', 'eq', 'so'][bb % 4]}"
    bt_flag = f"cr{bt // 4}{['lt', 'gt', 'eq', 'so'][bt % 4]}"

    if inst.name == "e_crand":
        and_result = il.and_expr(1, il.flag(ba_flag), il.flag(bb_flag))
        il.append(il.set_flag(bt_flag, and_result))

    elif inst.name == "e_crandc":
        result_expr = il.and_expr(1, il.flag(ba_flag), il.not_expr(1, il.flag(bb_flag)))
        il.append(il.set_flag(bt_flag, result_expr))
        
    elif inst.name == "e_creqv":
        xor_result = il.xor_expr(1, il.flag(ba_flag), il.flag(bb_flag))
        result_expr = il.not_expr(1, xor_result)
        il.append(il.set_flag(bt_flag, result_expr))

    elif inst.name == "e_crnand":
        and_result = il.and_expr(1, il.flag(ba_flag), il.flag(bb_flag))
        nand_result = il.not_expr(1, and_result)
        il.append(il.set_flag(bt_flag, nand_result))
    
    elif inst.name == "e_crnor":
        or_result = il.or_expr(1, il.flag(ba_flag), il.flag(bb_flag))
        nor_result = il.not_expr(1, or_result)
        il.append(il.set_flag(bt_flag, nor_result))
    
    elif inst.name == "e_cror":
        or_result = il.or_expr(1, il.flag(ba_flag), il.flag(bb_flag))
        il.append(il.set_flag(bt_flag, or_result))
    
    elif inst.name == "e_crorc":
        or_result = il.or_expr(1, il.flag(ba_flag), il.not_expr(1, il.flag(bb_flag)))
        il.append(il.set_flag(bt_flag, or_result))
    
    elif inst.name == "e_crxor":
        xor_result = il.xor_expr(1, il.flag(ba_flag), il.flag(bb_flag))
        il.append(il.set_flag(bt_flag, xor_result))
    
def lift_move_cr_instruction(inst: Instruction, il: LowLevelILFunction) -> None:
    bf = inst.get_field_value("BF")
    bfa = inst.get_field_value("BFA")

    if bf is None or bfa is None:
        il.append(il.unimplemented())
        return
    
    bfa_flag = f"cr{bfa}"
    bf_flag = f"cr{bf}"

    il.append(il.set_flag(bf_flag, il.flag(bfa_flag)))
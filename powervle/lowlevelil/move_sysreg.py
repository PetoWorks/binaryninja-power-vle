from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

def lift_move_sysreg_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    oper_0 = inst.operands[0]
    
    if inst.name == "se_mflr":
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)

        ei0 = il.set_reg(4, rx, il.reg(4, "lr"))
        il.append(ei0)
    
    elif inst.name == "se_mtlr":
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)
        
        ei0 = il.set_reg(4, "lr", il.reg(4, rx))
        il.append(ei0)
    
    elif inst.name == "se_mfctr":
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)

        ei0 = il.set_reg(4, rx, il.reg(4, "ctr"))
        il.append(ei0)
    
    elif inst.name == "se_mtctr":
        assert len(inst.operands) == 1
        rx = inst.get_operand_value(oper_0)

        ei0 = il.set_reg(4, "ctr", il.reg(4, rx))
        il.append(ei0)
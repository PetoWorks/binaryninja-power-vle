from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction
from binaryninja.log import log_warn, log_error, log_debug

def lift_e_move_sysreg_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    for i in range(len(inst.operands)):
        if i == 0: oper_0 = inst.operands[0]
        elif i == 1: oper_1 = inst.operands[1]

    # InstX("mbar", "E", ["MO"])
    if inst.name == "mbar":
        assert len(inst.operands) == 1
        mo = inst.get_operand_value(oper_0)
    
    # InstX("mtmsr", "E", ["RS", "L"])
    elif inst.name == "mtmsr":
        assert len(inst.operands) == 2
        rs = inst.get_operand_value(oper_0)
        l = inst.get_operand_value(oper_1)
        
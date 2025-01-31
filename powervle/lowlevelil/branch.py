from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

def lift_branch_instructions(inst: Instruction, il: LowLevelILFunction) -> None:

    link = inst.get_operand_value("LK")
    target_addr = inst.get_operand_value("target_addr")

    if inst.branch:
        if target_addr == None:
            if inst.name == "se_bctr":
                ctr = il.reg(4, "ctr")
                il.append(il.call(ctr) if link else il.jump(ctr))
            elif inst.name == "se_blr":
                if link:
                    il.append(il.set_reg(4, "lr", il.const_pointer(inst.addr + inst.length)))
                else:
                    il.append(il.ret(il.reg(4, "lr")))
            else:
                il.append(il.unimplemented())
        else:
            il.append(il.jump(il.const_pointer(4, target_addr)))

    elif inst.conditional_branch:
        # TODO
        il.append(il.unimplemented())

    else:
        il.append(il.unimplemented())

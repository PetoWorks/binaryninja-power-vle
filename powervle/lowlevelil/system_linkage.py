from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

#--------------------------- Chapter 4.3 System Linkage Instructions ---------------------------#

def lift_system_call(inst: Instruction, il: LowLevelILFunction) -> None:
    il.append(il.intrinsic([], "syscall", [])) 

def lift_illegal_instruction(inst: Instruction, il: LowLevelILFunction) -> None:
    il.append(il.unimplemented())

def lift_machine_check_return(inst: Instruction, il: LowLevelILFunction) -> None:
    il.append(il.intrinsic([], "mcret", []))

def lift_critical_return(inst: Instruction, il: LowLevelILFunction) -> None:
    il.append(il.intrinsic([], "cret", []))

def lift_return_from_interrupt(inst: Instruction, il: LowLevelILFunction) -> None:
    il.append(il.intrinsic([], "rfi", []))

def lift_debug_return(inst: Instruction, il: LowLevelILFunction) -> None:
    il.append(il.intrinsic([], "dret", []))
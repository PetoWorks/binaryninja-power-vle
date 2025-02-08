from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

#--------------------------- Chapter 4.3 System Linkage Instructions ---------------------------#

def lift_system_call(inst: Instruction, il: LowLevelILFunction) -> None:
    cia = inst.addr
    il.append(il.set_reg(8, "srr1", il.reg(8, "msr")))
    il.append(il.set_reg(8, "srr0", il.const(8, cia + 2)))
    ivpr = il.reg(8, "ivpr")
    ivor8 = il.reg(8, "ivor8")
    effective_addr = il.or_expr(
        8,
        il.and_expr(8, ivpr, il.const(8, 0xFFFF0000)),
        il.shl(8, il.and_expr(8, ivor8, il.const(8, 0xFF)), il.const(8, 4))
    )
    il.append(il.jump(effective_addr))
    new_msr = il.const(8, 0)
    il.append(il.set_reg(8, "msr", new_msr))

def lift_illegal_instruction(inst: Instruction, il: LowLevelILFunction) -> None:
    cia = inst.addr
    il.append(il.set_reg(8, "srr0", il.const(8, cia + inst.length)))
    il.append(il.set_reg(8, "srr1", il.reg(8, "msr")))
    il.append(il.set_reg(8, "esr", il.const(8, 0xDEAD)))
    il.append(il.set_reg(8, "msr", il.const(8, 0)))
    il.append(il.undefined())    

def lift_machine_check_return(inst: Instruction, il: LowLevelILFunction) -> None:
    arch_size = il.arch.address_size 
    il.append(il.set_reg(arch_size, "msr", il.reg(arch_size, "mcsrr1")))
    target_expr = il.and_expr(arch_size, il.reg(arch_size, "mcsrr0"), il.const(arch_size, 0xFFFFFFFE))
    il.append(il.intrinsic([], "isync", [])) 
    il.append(il.goto(target_expr))

def lift_critical_return(inst: Instruction, il: LowLevelILFunction) -> None:
    arch_size = il.arch.address_size  
    il.append(il.set_reg(arch_size, "msr", il.reg(arch_size, "csrr1")))
    mask = (1 << (arch_size * 8)) - 2
    target_expr = il.and_expr(arch_size, il.reg(arch_size, "csrr0"), il.const(arch_size, mask))
    il.append(il.intrinsic([], "isync", []))
    il.append(il.jump(target_expr))

def lift_return_from_interrupt(inst: Instruction, il: LowLevelILFunction) -> None:
    arch_size = il.arch.address_size 
    il.append(il.set_reg(arch_size, "msr", il.reg(arch_size, "srr1")))
    mask = ~1  
    target_expr = il.and_expr(arch_size, il.reg(arch_size, "srr0"), il.const(arch_size, mask))
    il.append(il.intrinsic([], "isync", []))
    target_label = il.get_label_for_address(il.arch, target_expr)
    if target_label:
        il.append(il.goto(target_label))
    else:
        il.append(il.jump(target_expr))

def lift_debug_return(inst: Instruction, il: LowLevelILFunction) -> None:
    arch_size = il.arch.address_size 
    il.append(il.set_reg(arch_size, "msr", il.reg(arch_size, "dsrr1")))
    mask = (1 << (arch_size * 8)) - 2
    target_expr = il.and_expr(arch_size, il.reg(arch_size, "dsrr0"), il.const(arch_size, mask))
    il.append(il.goto(target_expr))
    il.append(il.intrinsic([], "isync", []))
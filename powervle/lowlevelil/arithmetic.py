from binaryninja.lowlevelil import LowLevelILFunction
from ..instruction import Instruction

# 5.5 Fixed-Point Arithmetic Instructions
def _handle_add_operation(il, op1, op2, dst, is_const=False, flags=None, record=False, shift=0):
   if is_const:
       op2_val = op2 << shift
       result = il.add(4, il.reg(4, op1), il.const(4, op2_val), flags)
   else:
       result = il.add(4, il.reg(4, op1), il.reg(4, op2), flags)
       
   il.append(il.set_reg(4, dst, result, "cr0s" if record else None))
   return result

def lift_add_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
   add_instructions = {
       "se_add": {              # Add Short Form
           "op1": "RX",
           "op2": "RY", 
           "dst": "RX",
           "is_const": False
       },
       "e_add16i": {            # Add immediate
           "op1": "RA",
           "op2": "SI",
           "dst": "RT",
           "is_const": True
       },
       "e_add2i": {             # Add (2 operand) Immediate and Record
           "op1": "RA",
           "op2": "SI",
           "dst": "RA",
           "is_const": True,
           "record": True
       },
       "e_add2is": {            # Add (2 operand) Immediate Shifted
           "op1": "RA",
           "op2": "SI",
           "dst": "RA",
           "is_const": True,
           "shift": 16
       },
       "e_addi": {              # Add Scaled Immediate
           "op1": "RA",
           "op2": "sci8",
           "dst": "RT",
           "is_const": True,
           "record_field": "Rc"
       },
       "se_addi": {             # Add Immediate Short Form
           "op1": "RX",
           "op2": "oimm",
           "dst": "RX",
           "is_const": True
       },
       "e_addic": {             # Add Scaled Immediate Carrying
           "op1": "RA",
           "op2": "sci8",
           "dst": "RT",
           "is_const": True,
           "flags": "xer_ca",
           "record_field": "Rc"
       }
   }

   if inst.name not in add_instructions:
       il.append(il.unimplemented())
       return

   params = add_instructions[inst.name]
   op1 = inst.get_operand_value(params["op1"])
   op2 = inst.get_operand_value(params["op2"])
   dst = inst.get_operand_value(params["dst"])
   
   record = False
   if "record" in params:
       record = params["record"]
   elif "record_field" in params:
       record = inst.get_operand_value(params["record_field"])

   _handle_add_operation(
       il, op1, op2, dst,
       is_const=params.get("is_const", False),
       flags=params.get("flags"),
       record=record,
       shift=params.get("shift", 0)
   )

def _handle_sub_operation(il, op1, op2, dst, is_const=0, flags=None, record=False):
   if is_const:
        if is_const == 1:
            result = il.sub(4, il.const(4, op1), il.reg(4, op2), flags)
        else:
            result = il.sub(4, il.reg(4, op1), il.const(4, op2), flags)
   else:
       result = il.sub(4, il.reg(4, op1), il.reg(4, op2), flags)
       
   il.append(il.set_reg(4, dst, result, "cr0s" if record else None))
   return result

def lift_sub_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    sub_instructions = {
        "se_sub": {             # Subtract
            "op1": "RX",
            "op2": "RY",
            "dst": "RX",
        },
        "se_subf": {            # Subtract From Short Form
            "op1": "RY",
            "op2": "RX",
            "dst": "RX",
        },
        "e_subfic": {           # Subtract From Scaled Immediate Carrying
            "op1": "sci8",
            "op2": "RA",
            "dst": "RT",
            "is_const": 1,
            "flags": "xer_ca",
            "record_field": "Rc"
        },
        "se_subi": {            # Subtract Immediate
            "op1": "RX",
            "op2": "oimm",
            "dst": "RX",
            "is_const": 2,
            "record_field": "Rc"
        }
    }
    
    if inst.name not in sub_instructions:
        il.append(il.unimplemented())
        return
    
    params = sub_instructions[inst.name]
    op1 = inst.get_operand_value(params["op1"])
    op2 = inst.get_operand_value(params["op2"])
    dst = inst.get_operand_value(params["dst"])
    
    record = False
    if "record_field" in params:
        record = inst.get_operand_value(params["record_field"])
    
    _handle_sub_operation(
        il, op1, op2, dst,
        is_const=params.get("is_const", 0),
        flags=params.get("flags"),
        record=record,
    )

def lift_mul_instructions(inst: Instruction, il: LowLevelILFunction) -> None:
    if inst.name == "e_mullli": # Multiply Low Scaled Immediate
        op1 = inst.get_operand_value("RA")
        op2 = inst.get_operand_value("sci8")
        dst = inst.get_operand_value("RT")
        result = il.mult(16, il.reg(4, op1), il.const(4, op2)) # TODO (size)
        il.append(il.set_reg(4, dst, result)) 
    elif inst.name == "e_mull2i": # Multiply (2 operand) Low Immediate
        op1 = inst.get_operand_value("RA")
        op2 = inst.get_operand_value("SI")
        dst = op1
        result = il.mult(16, il.reg(4, op1), il.const(4, op2)) # TODO (size)
        il.append(il.set_reg(4, dst, result))
    elif inst.name == "se_mullw": # Multiply Low Word Short Form
        op1 = inst.get_operand_value("RX")
        op2 = inst.get_operand_value("RY")
        dst = op1
        result = il.mult(8, il.reg(4, op1), il.reg(4, op2)) # TODO (size)
        il.append(il.set_reg(4, dst, result))
    elif inst.name == "se_neg": # Negate Short Form
        op1 = inst.get_operand_value("RX")
        dst = op1
        result = il.neg_expr(4, il.reg(4, op1))
        il.append(il.set_reg(4, dst, result))
    else:
        il.append(il.unimplemented())
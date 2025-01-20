from typing import Tuple, List

from binaryninja.architecture import InstructionInfo, InstructionTextToken, InstructionTextTokenType
from binaryninja.lowlevelil import LowLevelILFunction

from . import FormatIM7


class Inst_SE_LI(FormatIM7):
    name = "se_li"
    category = "VLE"
    uses = ("UI7", "RX")

    @classmethod
    def get_instruction_info(cls, fields: dict[str, int], addr: int) -> InstructionInfo:
        return InstructionInfo(cls.length)

    @classmethod
    def get_instruction_text(cls, fields: dict[str, int], addr: int) -> Tuple[List[InstructionTextToken], int]:
        return [
            InstructionTextToken(InstructionTextTokenType.InstructionToken, "se_li"),
            InstructionTextToken(InstructionTextTokenType.TextToken, " "),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, cls.gpr2str(fields['RX'])),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{fields['UI7']}", value=fields['UI7'])
        ], cls.length

    @classmethod
    def get_instruction_low_level_il(cls, fields: dict[str, int], addr: int, il: LowLevelILFunction) -> int:
        il.append(
            il.set_reg(4, cls.gpr2str(fields['RX']), il.const(4, fields['UI7']))
        )
        return cls.length

from .instructions import InstTempHalf, InstTempWord


class Decoder:

    default = {

        # opcode primary bits level (opcode[0:4])

        0b0000: {
            # entire opcode level (opcode[0:15|16])
            0x0000: InstTempHalf,
            0x0001: InstTempHalf,
            0x0002: InstTempHalf,
            0x0004: InstTempHalf,
            0x0006: InstTempHalf,
            0x0008: InstTempHalf,
            0x0009: InstTempHalf,
            0x000A: InstTempHalf,
            0x000B: InstTempHalf,
            0x0020: InstTempHalf,
            0x0030: InstTempHalf,
            0x0080: InstTempHalf,
            0x0090: InstTempHalf,
            0x00A0: InstTempHalf,
            0x00B0: InstTempHalf,
            0x00C0: InstTempHalf,
            0x00D0: InstTempHalf,
            0x00E0: InstTempHalf,
            0x00F0: InstTempHalf,
            0x0100: InstTempHalf,
            0x0200: InstTempHalf,
            0x0300: InstTempHalf,
            0x0400: InstTempHalf,
            0x0500: InstTempHalf,
            0x0600: InstTempHalf,
            0x0700: InstTempHalf,
            0x0C00: InstTempHalf,
            0x0D00: InstTempHalf,
            0x0E00: InstTempHalf,
            0x0F00: InstTempHalf
        },

        0b0001: {
            0b00: {
                "VEC&LIM": {
                    # TODO
                },
                "SP": {
                    # TODO
                }
            },
            0b10: {
                # extra opcode level
                0x00: InstTempWord,
                0x01: InstTempWord,
                0x02: InstTempWord,
                0x03: InstTempWord,
                0x04: InstTempWord,
                0x05: InstTempWord,
                0x06: InstTempWord,
                0x07: InstTempWord,
                0x08: InstTempWord,
                0x09: InstTempWord,
                0x80: InstTempWord,
                0x90: InstTempWord,
                0xA0: InstTempWord,
                0xA8: {
                    # SCI8-form select bits (6:9)
                    0: InstTempWord,
                    1: InstTempWord
                },
                0xB0: InstTempWord,
                0xC0: InstTempWord,
                0xD0: InstTempWord,
                0xE0: InstTempWord
            },
            0b11: InstTempWord
        },

        0b0010: {
            # entire opcode (opcode[0:6]) || XO/RC bit level
            0b0010000: InstTempHalf,
            0b0010001: InstTempHalf,
            0b0010010: InstTempHalf, # se_subi
            0b0010011: InstTempHalf, # se_subi.
            0b0010101: InstTempHalf,
            0b0010110: InstTempHalf,
            0b0010111: InstTempHalf
        },

        0b0011: {
            # entire opcode level (opcode[0:6])
            0b001100: InstTempWord,
            0b001101: InstTempWord,
            0b001110: InstTempWord
        },

        0b0100: {
            # secondary opcode level (opcode[4:6])
            0b00: {
                # XO level
                0b00: InstTempHalf,
                0b01: InstTempHalf,
                0b10: InstTempHalf
            },
            0b01: {
                # XO/RC level
                0b00: InstTempHalf,
                0b01: InstTempHalf,
                0b10: InstTempHalf, # se_and
                0b11: InstTempHalf  # se_and.
            },
            0b10: InstTempHalf
        },

        0b0101: {
            # entire opcode level (opcode[0:6])
            0b010100: InstTempWord,
            0b010101: InstTempWord,
            0b010110: InstTempWord,
            0b010111: InstTempWord
        },

        0b0110: {
            # entire opcode level (opcode[0:6]) + XO bit
            0b0110000: InstTempHalf,
            0b0110001: InstTempHalf,
            0b0110010: InstTempHalf,
            0b0110011: InstTempHalf,
            0b0110100: InstTempHalf,
            0b0110101: InstTempHalf,
            0b0110110: InstTempHalf
        },

        0b0111: {
            # entire opcode level (opcode[0:6])
            0b011100: {
                # XO bit level
                0: InstTempWord,
                1: {
                    0b0001: InstTempWord,
                    0b0010: InstTempWord,
                    0b0011: InstTempWord,
                    0b0100: InstTempWord,
                    0b0101: InstTempWord,
                    0b0110: InstTempWord,
                    0b0111: InstTempWord,
                    0b1000: InstTempWord,
                    0b1001: InstTempWord,
                    0b1010: InstTempWord,
                    0b1100: InstTempWord,
                    0b1101: InstTempWord
                }
            },
            0b011101: {
                # XO bit level
                0: InstTempWord,
                1: InstTempWord
            },
            0b011110: {
                # XO bit level
                0: InstTempWord,
                1: InstTempWord
            },
            0b011111: {
                # primary XO bit level
                0b00000: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b10000: InstTempWord,
                },
                0b00001: {
                    0b00001: InstTempWord,
                    0b00100: InstTempWord,
                    0b00110: InstTempWord,
                    0b00111: InstTempWord,
                    0b01000: InstTempWord,
                    0b01001: InstTempWord,
                    0b01101: InstTempWord,
                    0b01110: InstTempWord,
                },
                0b00011: {
                    0b00100: InstTempWord,
                    0b00101: InstTempWord,
                    0b01000: InstTempWord,
                    0b01001: InstTempWord,
                    0b01010: InstTempWord,
                    0b01100: InstTempWord,
                    0b01101: InstTempWord,
                    0b01110: InstTempWord
                },
                0b00100: {
                    0b00000: InstTempWord,
                    0b00010: InstTempWord
                },
                0b00110: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b00100: InstTempWord,
                    0b00101: InstTempWord,
                    0b00111: InstTempWord,
                    0b01000: InstTempWord,
                    0b01010: InstTempWord,
                    0b01100: InstTempWord,
                    0b01110: InstTempWord,
                    0b01111: InstTempWord,
                    0b11110: InstTempWord,
                    0b11111: InstTempWord
                },
                0b00111: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b00010: InstTempWord,
                    0b00011: InstTempWord,
                    0b00100: InstTempWord,
                    0b00101: InstTempWord,
                    0b00110: InstTempWord,
                    0b00111: InstTempWord,
                    0b01000: InstTempWord,
                    0b01001: InstTempWord,
                    0b01011: InstTempWord,
                    0b01111: InstTempWord,
                    0b10000: InstTempWord,
                    0b10001: InstTempWord,
                    0b10100: InstTempWord,
                    0b10101: InstTempWord,
                    0b11000: InstTempWord,
                    0b11001: InstTempWord,
                    0b11100: InstTempWord,
                    0b11101: InstTempWord
                },
                0b01000: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b00011: InstTempWord,
                    0b00100: InstTempWord,
                    0b00110: InstTempWord,
                    0b00111: InstTempWord,
                    0b10000: InstTempWord,
                    0b10001: InstTempWord,
                    0b10011: InstTempWord,
                    0b10100: InstTempWord,
                    0b10110: InstTempWord,
                    0b10111: InstTempWord
                },
                0b01001: {
                    0b00000: InstTempWord,
                    0b00010: InstTempWord,
                    0b00111: InstTempWord,
                    0b01110: InstTempWord,
                    0b01111: InstTempWord,
                    0b10000: InstTempWord,
                    0b10010: InstTempWord,
                    0b10111: InstTempWord,
                    0b11110: InstTempWord,
                    0b11111: InstTempWord
                },
                0b01010: {
                    0b00000: InstTempWord,
                    0b00100: InstTempWord,
                    0b00110: InstTempWord,
                    0b00111: InstTempWord,
                    0b01000: InstTempWord,
                    0b10000: InstTempWord,
                    0b10010: InstTempWord,
                    0b10111: InstTempWord,
                    0b11110: InstTempWord,
                    0b11111: InstTempWord
                },
                0b01011: {
                    0b00000: InstTempWord,
                    0b00010: InstTempWord,
                    0b00111: InstTempWord,
                    0b01110: InstTempWord,
                    0b01111: InstTempWord,
                    0b10000: InstTempWord,
                    0b10010: InstTempWord,
                    0b10111: InstTempWord,
                    0b11110: InstTempWord,
                    0b11111: InstTempWord
                },
                0b01110: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b00010: InstTempWord,
                    0b00110: InstTempWord,
                    0b00111: InstTempWord,
                    0b01010: InstTempWord,
                    0b01110: InstTempWord
                },

                0b01111: InstTempWord,

                0b10000: {
                    0b00000: InstTempWord,
                    0b00100: InstTempWord
                },
                0b10010: {
                    0b00010: InstTempWord,
                    0b00011: InstTempWord,
                    0b00100: InstTempWord,
                    0b00101: InstTempWord,
                    0b00110: InstTempWord,
                    0b00111: InstTempWord,
                    0b01000: InstTempWord,
                    0b01001: InstTempWord,
                    0b01011: InstTempWord,
                    0b01100: InstTempWord,
                    0b01101: InstTempWord,
                    0b01111: InstTempWord,
                    0b11000: InstTempWord,
                    0b11001: InstTempWord,
                    0b11100: InstTempWord,
                    0b11101: InstTempWord,
                    0b11110: InstTempWord,
                    0b11111: InstTempWord
                },
                0b10011: {
                    0b00000: InstTempWord,
                    0b00010: InstTempWord,
                    0b01000: InstTempWord,
                    0b01010: InstTempWord,
                    0b01011: InstTempWord,
                    0b01110: InstTempWord,
                    0b10010: InstTempWord,
                    0b10100: InstTempWord,
                    0b11010: InstTempWord,
                    0b11100: InstTempWord
                },
                0b10100: {
                    0b00000: InstTempWord,
                    0b00010: InstTempWord,
                    0b01001: InstTempWord,
                    0b10000: InstTempWord,
                    0b10100: InstTempWord
                },
                0b10101: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b00100: InstTempWord,
                    0b00101: InstTempWord,
                    0b01010: InstTempWord,
                    0b01011: InstTempWord,
                    0b01110: InstTempWord,
                    0b01111: InstTempWord,
                    0b10000: InstTempWord,
                    0b10010: InstTempWord,
                    0b10100: InstTempWord,
                    0b10110: InstTempWord
                },
                0b10110: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b00010: InstTempWord,
                    0b00011: InstTempWord,
                    0b00100: InstTempWord,
                    0b00110: InstTempWord,
                    0b00111: InstTempWord,
                    0b01000: InstTempWord,
                    0b01001: InstTempWord,
                    0b01010: InstTempWord,
                    0b01011: InstTempWord,
                    0b01101: InstTempWord,
                    0b01110: InstTempWord,
                    0b10000: InstTempWord,
                    0b10001: InstTempWord,
                    0b10010: InstTempWord,
                    0b10100: InstTempWord,
                    0b10111: InstTempWord,
                    0b11000: InstTempWord,
                    0b11001: InstTempWord,
                    0b11010: InstTempWord,
                    0b11100: InstTempWord,
                    0b11110: InstTempWord,
                    0b11111: InstTempWord
                },
                0b10111: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b00010: InstTempWord,
                    0b00011: InstTempWord,
                    0b00100: InstTempWord,
                    0b00101: InstTempWord,
                    0b00110: InstTempWord,
                    0b00111: InstTempWord,
                    0b01000: InstTempWord,
                    0b01001: InstTempWord,
                    0b01010: InstTempWord,
                    0b01011: InstTempWord,
                    0b01100: InstTempWord,
                    0b01101: InstTempWord,
                    0b01110: InstTempWord,
                    0b01111: InstTempWord,
                    0b10000: InstTempWord,
                    0b10001: InstTempWord,
                    0b10010: InstTempWord,
                    0b10011: InstTempWord,
                    0b10100: InstTempWord,
                    0b10101: InstTempWord,
                    0b10110: InstTempWord,
                    0b10111: InstTempWord,
                    0b11001: InstTempWord,
                    0b11101: InstTempWord,
                    0b11110: InstTempWord
                },
                0b11000: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b01000: InstTempWord,
                    0b01001: InstTempWord,
                    0b10000: InstTempWord,
                    0b10001: InstTempWord,
                    0b11000: InstTempWord,
                    0b11001: InstTempWord
                },
                0b11010: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b00011: InstTempWord,
                    0b11000: InstTempWord,
                    0b11001: InstTempWord,
                    0b11100: InstTempWord,
                    0b11101: InstTempWord,
                    0b11110: InstTempWord
                },
                0b11011: {
                    0b00000: InstTempWord,
                    0b10000: InstTempWord,
                    0b11001: InstTempWord
                },
                0b11100: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b00011: InstTempWord,
                    0b01000: InstTempWord,
                    0b01001: InstTempWord,
                    0b01100: InstTempWord,
                    0b01101: InstTempWord,
                    0b01110: InstTempWord
                },
                0b11101: {
                    0b00000: InstTempWord,
                    0b00100: InstTempWord,
                    0b01000: InstTempWord,
                    0b01100: InstTempWord
                },
                0b11110: {
                    0b00000: InstTempWord,
                    0b00001: InstTempWord,
                    0b00010: InstTempWord,
                    0b00011: InstTempWord,
                    0b00100: InstTempWord,
                    0b00101: InstTempWord,
                    0b00110: InstTempWord,
                    0b00111: InstTempWord,
                    0b01000: InstTempWord,
                    0b01001: InstTempWord,
                    0b01010: InstTempWord,
                    0b01011: InstTempWord,
                    0b01100: InstTempWord,
                    0b01101: InstTempWord,
                    0b01110: InstTempWord,
                    0b01111: InstTempWord
                },
                0b11111: {
                    0b00000: InstTempWord,
                    0b00010: InstTempWord,
                    0b00011: InstTempWord,
                    0b00100: InstTempWord,
                    0b00101: InstTempWord,
                    0b00110: InstTempWord,
                    0b00111: InstTempWord,
                    0b01000: InstTempWord,
                    0b01001: InstTempWord,
                    0b01010: InstTempWord,
                    0b01011: InstTempWord,
                    0b01100: InstTempWord,
                    0b01101: InstTempWord,
                    0b10010: InstTempWord,
                    0b10110: InstTempWord,
                    0b11110: InstTempWord,
                    0b11111: InstTempWord
                }
            }
        },

        0b1000: InstTempHalf,
        0b1001: InstTempHalf,
        0b1010: InstTempHalf,
        0b1011: InstTempHalf,
        0b1100: InstTempHalf,
        0b1101: InstTempHalf,

        0b1110: {
            # secondary opcode level (opcode[4:5])
            0: InstTempHalf, # se_bc
            1: InstTempHalf # se_b[l]
        }
    }
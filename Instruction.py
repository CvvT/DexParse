__author__ = 'CwT'

OPCODE = {0: "nop", 1: "move", 2: "move/from16", 5: "move-wide/from16", 7: "move-object", 8: "move-object/from16",
          0xa: "move-result", 0xb: "move-result-wide", 0xc: "move-result-object", 0xd: "move-exception",
          0xe: "return-void", 0xf: "return", 0x10: "return-wide", 0x11: "return-object",
          0x12: "const/4", 0x13: "const/16", 0x1a: "const-string", 0x1c: "const-class",
          0x1f: "check-cast", 0x22: "new-instance", 0x23: "new-array", 0x28: "goto",
          0x32: "if-eq", 0x33: "if-ne", 0x34: "if-lt", 0x35: "if-ge", 0x36: "if-gt", 0x37: "if-le",
          0x38: "if-eqz", 0x39: "if-nez", 0x3a: "if-ltz", 0x3b: "if-gez", 0x3c: "if-gtz", 0x3d: "if-lez",
          0x44: "aget", 0x45: "aget-wide", 0x46: "aget-object", 0x47: "aget-boolean",
          0x48: "aget-byte", 0x49: "aget-char", 0x4a: "aget-short",
          0x4b: "aput", 0x4c: "aput-wide", 0x4d: "aput-object", 0x4e: "aput-boolean",
          0x4f: "aput-byte", 0x50: "aput-char", 0x51: "aput-short",
          0x52: "iget", 0x53: "iget-wide", 0x54: "iget-object", 0x55: "iget-boolean",
          0x56: "iget-byte", 0x57: "iget-char", 0x58: "iget-short",
          0x59: "iput", 0x5a: "iput-wide", 0x5b: "iput-object", 0x5c: "iput-boolean",
          0x5d: "iput-byte", 0x5e: "iput-char", 0x5f: "iput-short",
          0x60: "sget", 0x61: "sget-wide", 0x62: "sget-object", 0x63: "sget-boolean",
          0x64: "sget-byte", 0x65: "sget-char", 0x66: "sget-short", 0x67: "sput", 0x68: "sput-wide",
          0x69: "sput-object", 0x6a: "sput-boolean", 0x6b: "sput-byte", 0x6c: "sput-char", 0x6d: "sput-short",
          0x6e: "invoke-virtual", 0x6f: "invoke-super", 0x70: "invoke-direct", 0x71: "invoke-static", 0x72: "invoke-interface",
          0x74: "invoke-virtual/range", 0x75: "invoke-super/range", 0x76: "invoke-direct/range",
          0x77: "invoke-static/range", 0x78: "invoke-interface/range",
          0x7b: "neg-int", 0x7c: "not-int", 0x7d: "neg-long", 0x7e: "not-long", 0x7f: "neg-float", 0x80: "neg-double",
          0x81: "int-to-long", 0x82: "int-to-float", 0x83: "int-to-double", 0x84: "long-to-int", 0x85: "long-to-float",
          0x86: "long-to-double", 0x87: "float-to-int", 0x88: "float-to-long", 0x89: "float-to-double", 0x8a: "double-to-int",
          0x8b: "double-to-long", 0x8c: "double-to-float", 0x8d: "int-to-byte", 0x8e: "int-to-char", 0x8f: "int-to-short",
          0x90: "add-int", 0x91: "sub-int", 0x92: "mul-int", 0x93: "div-int", 0x94: "rem-int", 0x95: "and-int",
          0x96: "or-int", 0x97: "xor-int", 0x98: "shl-int", 0x99: "shr-int", 0x9a: "ushr-int", 0x9b: "add-long",
          0x9c: "sub-long", 0x9d: "mul-long", 0x9e: "div-long", 0x9f: "rem-long", 0xa0: "and-long", 0xa1: "or-long",
          0xa2: "xor-long", 0xa3: "shl-long", 0xa4: "shr-long", 0xa5: "ushr-long", 0xa6: "add-float", 0xa7: "sub-float",
          0xa8: "mul-float", 0xa9: "div-float", 0xaa: "rem-float", 0xab: "add-double", 0xac: "sub-double", 0xad: "mul-double",
          0xae: "div-double", 0xaf: "rem-double",
          0xb0: "add-int/2addr", 0xb1: "sub-int/2addr", 0xb2: "mul-int/2addr", 0xb3: "div-int/2addr", 0xb4: "rem-int/2addr",
          0xb5: "and-int/2addr", 0xb6: "or-int/2addr", 0xb7: "xor-int/2addr", 0xb8: "shl-int/2addr", 0xb9: "shr-int/2addr",
          0xba: "ushr-int/2addr", 0xbb: "add-long/2addr", 0xbc: "sub-long/2addr", 0xbd: "mul-long/2addr",
          0xbe: "div-long/2addr", 0xbf: "rem-long/2addr", 0xc0: "and-long/2addr", 0xc1: "or-long/2addr", 0xc2: "xor-long/2addr",
          0xc3: "shl-long/2addr", 0xc4: "shr-long/2addr", 0xc5: "ushr-long/2addr", 0xc6: "add-float/2addr", 0xc7: "sub-float/2addr",
          0xc8: "mul-float/2addr", 0xc9: "div-float/2addr", 0xca: "rem-float/2addr", 0xcb: "add-double/2addr",
          0xcc: "sub-double/2addr", 0xcd: "mul-double/2addr", 0xce: "div-double/2addr", 0xcf: "rem-double/2addr",
          0xd0: "add-int/lit16", 0xd1: "rsub-int", 0xd2: "mul-int/lit16", 0xd3: "div-int/lit16", 0xd4: "rem-int/lit16",
          0xd5: "and-int/lit16", 0xd6: "or-int/lit16", 0xd7: "xor-int/lit16",
          0xd8: "add-int/lit8", 0xd9: "rsub-int/lit8", 0xda: "mul-int/lit8", 0xdb: "div-int/lit8", 0xdc: "rem-int/lit8",
          0xdd: "and-int/lit8", 0xde: "or-int/lit8", 0xdf: "xor-int/lit8", 0xe0: "shl-int/lit8", 0xe1: "shl-int/lit8",
          0xe2: "ushr-int/lit8",
          }

class Instruction:
    def __init__(self):
        self.insns = []
        self.str_ins = ""
        self.dst = -1
        self.src = -1
        self.target = -1

    def init(self, param_insns, index):
        start = index
        one = param_insns[index]
        index += 1
        opcode = one & 0xff
        one >>= 8
        if opcode in (0, 0xe):
            self.str_ins = OPCODE[opcode]
        elif opcode == 1:
            index = self.parse(param_insns, index, one, opcode, 0)
        elif opcode == 2:
            index = self.parse(param_insns, index, one, opcode, 1)
        elif opcode == 5:
            index = self.parse(param_insns, index, one, opcode, 1)
        elif opcode == 7:
            index = self.parse(param_insns, index, one, opcode, 0)
        elif opcode == 8:
            index = self.parse(param_insns, index, one, opcode, 1)
        elif opcode in range(0xa, 0xe):
            index = self.parse(param_insns, index, one, opcode, 2)
        elif opcode in range(0xf, 0x12):
            index = self.parse(param_insns, index, one, opcode, 8)
        elif opcode == 0x12:
            index = self.parse(param_insns, index, one, opcode, 0)
        elif opcode == 0x13:
            index = self.parse(param_insns, index, one, opcode, 1)
        elif opcode == 0x1a:
            index = self.parse(param_insns, index, one, opcode, 1)
        elif opcode == 0x1c:
            index = self.parse(param_insns, index, one, opcode, 1)
        elif opcode == 0x1f:
            index = self.parse(param_insns, index, one, opcode, 1)
        elif opcode == 0x22:
            index = self.parse(param_insns, index, one, opcode, 1)
        elif opcode == 0x23:
            index = self.parse(param_insns, index, one, opcode, 4)
        elif opcode == 0x28:
            index = self.parse(param_insns, index, one, opcode, 2)
        elif opcode in range(0x32, 0x38):
            index = self.parse(param_insns, index, one, opcode, 4)
        elif opcode in range(0x38, 0x3e):
            index = self.parse(param_insns, index, one, opcode, 1)
        elif opcode in range(0x44, 0x52):
            index = self.parse(param_insns, index, one, opcode, 3)
        elif opcode in range(0x52, 0x60):
            index = self.parse(param_insns, index, one, opcode, 4)
        elif opcode in range(0x60, 0x6e):
            index = self.parse(param_insns, index, one, opcode, 1)
        elif opcode in range(0x6e, 0x73):
            index = self.parse(param_insns, index, one, opcode, 5)
        elif opcode in range(0x7b, 0x90):
            index = self.parse(param_insns, index, one, opcode, 0)
        elif opcode in range(0x90, 0xb0):
            index = self.parse(param_insns, index, one, opcode, 7)
        elif opcode in range(0xb0, 0xd0):
            index = self.parse(param_insns, index, one, opcode, 0)
        elif opcode in range(0xd0, 0xd8):
            index = self.parse(param_insns, index, one, opcode, 4)
        elif opcode in range(0xd8, 0xe3):
            index = self.parse(param_insns, index, one, opcode, 7)
        else:
            print("ERROR: didn't classified the opcode", opcode)
        for i in range(start, index):
            self.insns.append(param_insns[i])
        return index

    def parse(self, param_insns, index, one, opcode, kind):
        if kind == 0:   # opcode vx, vy
            self.src = (one >> 4) & 0xf
            self.dst = one & 0xf
            self.str_ins = OPCODE[opcode] + " " + str(self.dst) + ", " + str(self.src)
        elif kind == 1:     # opcode vx/vxx, vyy(id)
            self.dst = one
            self.src = int(param_insns[index])
            index += 1
            self.str_ins = OPCODE[opcode] + " " + str(self.dst) + ", " + str(self.src)
        elif kind == 2:     # opcode vx/vxx
            self.dst = one
            self.str_ins = OPCODE[opcode] + " " + str(self.dst)
        elif kind == 3:     # opcode vx, vy, vz
            self.dst = one
            one = int(param_insns[index])
            self.src = one & 0xff
            self.target = (one >> 8) & 0xff
            self.str_ins = OPCODE[opcode] + " " + str(self.dst) + ", " + str(self.src) + ", " + str(self.target)
            index += 1
        elif kind == 4:  # opcode vx, vy, id(lit)
            self.dst = one & 0xf
            self.src = (one >> 4) & 0xf
            self.target = int(param_insns[index])
            index += 1
            self.str_ins = OPCODE[opcode] + " " + str(self.dst) + ", " + str(self.src) + ", " + str(self.target)
        elif kind == 5:     # invoke-kind {vC, vD, vE, vF, vG}, meth@BBBB
            self.src = (one >> 4) & 0xf     # use for count parameter
            self.target = int(param_insns[index])
            param = int(param_insns[index+1])
            index += 2
            self.str_ins = OPCODE[opcode] + " {"
            if self.src > 0:
                self.str_ins += str(param & 0xf)
            if self.src > 1:
                self.str_ins += ", " + str((param >> 4) & 0xf)
            if self.src > 2:
                self.str_ins += ", " + str((param >> 8) & 0xf)
            if self.src > 3:
                self.str_ins += ", " + str((param >> 12) & 0xf)
            if self.src > 4:
                self.str_ins += ", " + str(one & 0xf)
            self.str_ins += "}, " + str(self.target)
        elif kind == 6:     # invoke-kind/range {vCCCC .. vNNNN}, meth@BBBB
            self.src = one  # use for count parameter
            self.target = int(param_insns[index])
            param = int(param_insns[index+1])
            index += 2
            self.str_ins = OPCODE[opcode] + " {"
            if self.src > 0:
                self.str_ins += str(param) + " ... " + str(param + self.src - 1)
            self.str_ins += "}, " + str(self.target)
        elif kind == 7:     # opcode vXX, vYY, vZZ
            self.dst = one
            self.src = param_insns[index] & 0xff
            self.target = (param_insns[index] >> 8) & 0xff
            self.str_ins = OPCODE[opcode] + " " + str(self.dst) + ", " + str(self.src) + ", " + str(self.target)
        elif kind == 8:     # opcode vxx
            self.dst = one
            self.str_ins = OPCODE[opcode] + " " + str(self.dst)
        else:
            print("ERROR: didn't classified this kind")
        return index

# notice that: each instruction store as short(little)
class InstructionSet:
    def __init__(self, insns):
        length = len(insns)
        index = 0
        self.set = []
        while index < length:
            tmp = Instruction()
            index = tmp.init(insns, index)
            self.set.append(tmp)
            print(tmp.str_ins, hex(tmp.insns[0] & 0xff), len(tmp.insns))

    def printf(self):
        length = len(self.set)
        for i in range(0, length):
            print(self.set[i].str_ins)

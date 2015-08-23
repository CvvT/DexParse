#! /usr/bin/python
# coding=utf-8
import struct
import os
import hashlib
import Instruction

Access_Flag = {'public': 1, 'private': 2, 'protected': 4, 'static': 8, 'final': 0x10,
               'synchronized': 0x20, 'volatile': 0x40, 'bridge': 0x40, 'transient': 0x80,
               'varargs': 0x80, 'native': 0x100, 'interface': 0x200, 'abstract': 0x400,
               'strictfp': 0x800, 'synthetic': 0x1000, 'annotation': 0x2000, 'enum': 0x4000,
               'constructor': 0x10000, 'declared_synchronized': 0x20000}

TypeDescriptor = {'void': 'V', 'boolean': 'Z', 'byte': 'B', 'short': 'S', 'char': 'C',
                  'int': 'I', 'long': 'J', 'float': 'F', 'double': 'D', 'boolean[]': '[Z',
                  'byte[]': '[B', 'short[]': '[S', 'char[]': '[C', 'int[]': 'I',
                  'long[]': '[J', 'float[]': '[F', 'double[]': 'D'}

ShortyDescriptor = {'void': 'V', 'boolean': 'Z', 'byte': 'B', 'short': 'S', 'char': 'C',
                    'int': 'I', 'long': 'J', 'float': 'F', 'double': 'D'}

ACSII = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 0,
         'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}

def checksum(f, len):
    a = 1
    b = 0
    f.seek(12)
    print("file size is :", len)
    for i in range(12, len):
        onebyte = struct.unpack("B", f.read(1))[0]
        a = (a + onebyte) % 65521
        b = (b + a) % 65521
    return b << 16 | a

def get_file_sha1(f):
    f.seek(32)  # skip magic, checksum, sha
    sha = hashlib.sha1()
    while True:
        data = f.read(1024)
        if not data:
            break
        sha.update(data)
    return sha.hexdigest()

def rightshift(value, n):
    mask = 0x80000000
    check = value & mask
    if check != mask:
        return value >> n
    else:
        submask = mask
        for loop in range(0, n):
            submask = (submask | (mask >> loop))
        strdata = struct.pack("I", submask | (value >> n))
        ret = struct.unpack("i", strdata)[0]
        return ret

def readunsignedleb128(file):
    res = struct.unpack("B", file.read(1))[0]
    if res > 0x7f:
        cur = struct.unpack("B", file.read(1))[0]
        res = (res & 0x7f) | ((cur & 0x7f) << 7)
        if cur > 0x7f:
            cur = struct.unpack("B", file.read(1))[0]
            res |= (cur & 0x7f) << 14
            if cur > 0x7f:
                cur = struct.unpack("B", file.read(1))[0]
                res |= (cur & 0x7f) << 21
                if cur > 0x7f:
                    cur = struct.unpack("B", file.read(1))[0]
                    res |= cur << 28
    if res == 44370793110:
        print(file.tell())
    return res

def readsignedleb128(file):
    res = struct.unpack("B", file.read(1))[0]
    if res <= 0x7f:
        res = rightshift((res << 25), 25)
    else:
        cur = struct.unpack("B", file.read(1))[0]
        res = (res & 0x7f) | ((cur & 0x7f) << 7)
        if cur <= 0x7f:
            res = rightshift((res << 18), 18)
        else:
            cur = struct.unpack("B", file.read(1))[0]
            res |= (cur & 0x7f) << 14
            if cur <= 0x7f:
                res = rightshift((res << 11), 11)
            else:
                cur = struct.unpack("B", file.read(1))[0]
                res |= (cur & 0x7f) << 21
                if cur <= 0x7f:
                    res = rightshift((res << 4), 4)
                else:
                    cur = struct.unpack("B", file.read(1))[0]
                    res |= cur << 28
    return res

def writesignedleb128(num, file):
    if num >= 0:
        writeunsignedleb128(num, file)
    else:
        mask = 0x80000000
        for i in range(0, 32):
            tmp = num & mask
            mask >>= 1
            if tmp == 0:
                break
        loop = 32 - i + 1
        while loop > 7:
            cur = num & 0x7f | 0x80
            num >>= 7
            file.write(struct.pack("B", cur))
            loop -= 7
        cur = num & 0x7f
        file.write(struct.pack("B", cur))

def signedleb128forlen(num):
    if num >= 0:
        return unsignedleb128forlen(num)
    else:
        mask = 0x80000000
        for i in range(0, 32):
            tmp = num & mask
            mask >>= 1
            if tmp == 0:
                break
        loop = 32 - i + 1
        if loop % 7 == 0:
            return loop / 7
        else:
            return loop / 7 + 1

def writeunsignedleb128(num, file):
    if num <= 0x7f:
        file.write(struct.pack("B", num))
    else:
        cur = num & 0x7F | 0x80
        file.write(struct.pack("B", cur))
        num >>= 7
        if num <= 0x7f:
            file.write(struct.pack("B", num))
        else:
            cur = num & 0x7f | 0x80
            file.write(struct.pack("B", cur))
            num >>= 7
            if num <= 0x7f:
                file.write(struct.pack("B", num))
            else:
                cur = num & 0x7f | 0x80
                file.write(struct.pack("B", cur))
                num >>= 7
                if num <= 0x7f:
                    file.write(struct.pack("B", num))
                else:
                    cur = num & 0x7f | 0x80
                    file.write(struct.pack("B", cur))
                    num >>= 7
                    file.write(struct.pack("B", num))

def unsignedleb128forlen(num):
    len = 1
    temp = num
    while num > 0x7f:
        len += 1
        num >>= 7
    if len > 5:
        print("error for unsignedleb128forlen", temp)
        os._exit(num)
    return len

def writeunsignedleb128p1alignshort(num, file):
    num += 1
    if num <= 0x7f:
        if file.tell() % 2 == 1:
            file.write(struct.pack("B", num))
        else:
            # print(hex(num))
            file.write(struct.pack("B", num | 0x80))
            file.write(struct.pack("B", 0))
    else:
        cur = num & 0x7F | 0x80
        file.write(struct.pack("B", cur))
        num >>= 7
        if num <= 0x7f:
            if file.tell() % 2 == 1:
                file.write(struct.pack("B", num))
            else:
                file.write(struct.pack("B", num | 0x80))
                file.write(struct.pack("B", 0))
        else:
            cur = num & 0x7f | 0x80
            file.write(struct.pack("B", cur))
            num >>= 7
            if num <= 0x7f:
                if file.tell() % 2 == 1:
                    file.write(struct.pack("B", num))
                else:
                    file.write(struct.pack("B", num | 0x80))
                    file.write(struct.pack("B", 0))
            else:
                cur = num & 0x7f | 0x80
                file.write(struct.pack("B", cur))
                num >>= 7
                if num <= 0x7f:
                    if file.tell() % 2 == 1:
                        file.write(struct.pack("B", num))
                    else:
                        file.write(struct.pack("B", num | 0x80))
                        file.write(struct.pack("B", 0))
                else:
                    cur = num & 0x7f | 0x80
                    file.write(struct.pack("B", cur))
                    num >>= 7
                    if file.tell() % 2 == 1:
                        file.write(struct.pack("B", num))
                    else:
                        file.write(struct.pack("B", num | 0x80))
                        file.write(struct.pack("B", 0))


def readunsignedleb128p1(file):
    res = readunsignedleb128(file)
    return res - 1

def writeunsignedleb128p1(num, file):
    writeunsignedleb128(num+1, file)

def unsignedleb128p1forlen(num):
    return unsignedleb128forlen(num+1)

def getutf8str(file):
    string = []
    while 1:
        onebyte = struct.unpack("B", file.read(1))[0]
        if onebyte == 0:
            break
        string.append(onebyte)
    return bytearray(string).decode("utf-8")

def getstr(bytes):
    return bytearray(bytes).decode("utf-8")

class EncodedArray:
    def __init__(self, file):
        self.size = readunsignedleb128(file)
        self.values = []
        for i in range(0, self.size):
            self.values.append(EncodedValue(file))

    def copytofile(self, file):
        writeunsignedleb128(self.size, file)
        for i in range(0, self.size):
            self.values[i].copytofile(file)

    def makeoffset(self, off):
        off += unsignedleb128forlen(self.size)
        for i in range(0, self.size):
            off = self.values[i].makeoffset(off)
        return off

    def printf(self):
        print("encoded array size", self.size)

class EncodedValue:
    def __init__(self, file):
        self.onebyte = struct.unpack("B", file.read(1))[0]
        self.type = self.onebyte & 0x1F
        self.arg = (self.onebyte >> 5) & 0x7
        self.value = []
        if self.type == 0x00:
            # print 'here 0x00 VALUE_BYTE in class : '  + str(curClass_idx)
            if self.arg != 0:
                print ("[-] Ca ,get error in VALUE_BYTE")
                os._exit(1)                
            self.value.append(struct.unpack("B", file.read(1))[0])             
        elif self.type == 0x02:
            # print 'here 0x02 VALUE_SHORT in class : '  + str(curClass_idx)  
            if self.arg >= 2:
                print ("[-] Ca ,get error in VALUE_SHORT at class : ")
                os._exit(1)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x03:
            # print 'here 0x03 VALUE_CHAR in class : '  + str(curClass_idx)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x04:
            # print 'here 0x04 VALUE_INT in class : '  + str(curClass_idx)
            if self.arg >= 4:
                print ("[-] Ca ,get error in VALUE_INT at class : ")
                os._exit(1)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x06:
            # print 'here 0x06 VALUE_LONG in class : '  + str(curClass_idx)
            if self.arg >= 8:
                print ("[-] Ca ,get error in VALUE_LONG at class : ")
                os._exit(1)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x10:
            # print 'here 0x10 VALUE_FLOAT in class : '  + str(curClass_idx)  
            if self.arg >= 4:
                print ("[-] Ca ,get error in VALUE_FLOAT at class : ")
                os._exit(1)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x11:
            # print 'here 0x11 VALUE_DOUBLE in class : '  + str(curClass_idx)
            if self.arg >= 8:
                print ("[-] Ca ,get error in VALUE_DOUBLE at class : ")
                os._exit(1)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x17:
            # print 'here 0x17 VALUE_STRING in class : '  + str(curClass_idx) 
            if self.arg >= 4:
                print ("[-] Ca ,get error in VALUE_STRING at class : ")
                os._exit(1)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x18:
            # print 'here 0x18 VALUE_TYPE in class : '  + str(curClass_idx)
            if self.arg >= 4:
                print ("[-] Ca ,get error in VALUE_TYPE at class : ")
                os._exit(1)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x19:
            # print 'here 0x19 VALUE_FIELD in class : '  + str(curClass_idx)  
            if self.arg >= 4:
                print ("[-] Ca ,get error in VALUE_FIELD at class : ")
                os._exit(1)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x1a:
            # print 'here 0x1a VALUE_METHOD in class : '  + str(curClass_idx)
            if self.arg >= 4:
                print ("[-] Ca ,get error in VALUE_METHOD at class : ")
                os._exit(1)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x1b:
            # print 'here 0x1b VALUE_ENUM in class : '  + str(curClass_idx)
            if self.arg >= 4:
                print ("[-] Ca ,get error in VALUE_ENUM at class : ")
                os._exit(1)
            for i in range(0, self.arg+1):
                self.value.append(struct.unpack("B", file.read(1))[0])
        elif self.type == 0x1c:
            # print 'here 0x1c VALUE_ARRAY in class : '  + str(curClass_idx)
            if self.arg != 0x00:
                print ("[-] Ca ,get error in VALUE_ARRAY")
                os._exit(1)
            self.value.append(EncodedArray(file))
        elif self.type == 0x1d:
            # print 'here 0x1d VALUE_ANNOTATION in class : '  + str(curClass_idx)
            if self.arg != 0:
                os._exit()
            self.value.append(EncodedAnnotation(file))
            # if case(0x1e):
                # print 'here 0x1e VALUE_NULL in class : '  + str(curClass_idx)
            #     break
            # if case(0x1f):
                # print 'here 0x1f VALUE_BOOLEAN in class : '  + str(curClass_idx) 
            #     break

    def copytofile(self, file):
        file.write(struct.pack("B", self.onebyte))
        if self.type <= 0x1b:
            for i in range(0, self.arg+1):
                file.write(struct.pack("B", self.value[i]))
        elif self.type == 0x1c:
            self.value[0].copytofile(file)
        elif self.type == 0x1d:
            self.value[0].copytofile(file)

    def makeoffset(self, off):
        off += 1
        if self.type <= 0x1b:
            off += self.arg+1
        elif self.type == 0x1c:
            off = self.value[0].makeoffset(off)
        elif self.type == 0x1d:
            off = self.value[0].makeoffset(off)
        return off

    def printf(self):
        print("encoded value :", self.type, self.arg)


# ----------------------------------------------------------------------------------------
class AnnotationElement:
    def __init__(self, file):
        self.name_idx = readunsignedleb128(file)
        self.value = EncodedValue(file)

    def copytofile(self, file):
        writeunsignedleb128(self.name_idx, file)
        self.value.copytofile(file)

    def makeoffset(self, off):
        off += unsignedleb128forlen(self.name_idx)
        off = self.value.makeoffset(off)
        return off

class EncodedAnnotation:
    def __init__(self, file):
        self.type_idx = readunsignedleb128(file)
        self.size = readunsignedleb128(file)
        self.elements = []  # annotation_element[size]
        for i in range(0, self.size):
            self.elements.append(AnnotationElement(file))

    def copytofile(self, file):
        writeunsignedleb128(self.type_idx, file)
        writeunsignedleb128(self.size, file)
        for i in range(0, self.size):
            self.elements[i].copytofile(file)

    def makeoffset(self, off):
        off += unsignedleb128forlen(self.type_idx)
        off += unsignedleb128forlen(self.size)
        for i in range(0, self.size):
            off = self.elements[i].makeoffset(off)
        return off

class DexHeader:
    def __init__(self, file, mode=0):
        if mode == 0:
            self.start = file.tell()
            self.magic = []
            self.magic.append(chr(struct.unpack("B", file.read(1))[0]))
            self.magic.append(chr(struct.unpack("B", file.read(1))[0]))
            self.magic.append(chr(struct.unpack("B", file.read(1))[0]))
            self.magic.append(chr(struct.unpack("B", file.read(1))[0]))
            self.version = []
            self.version.append(chr(struct.unpack("B", file.read(1))[0]))
            self.version.append(chr(struct.unpack("B", file.read(1))[0]))
            self.version.append(chr(struct.unpack("B", file.read(1))[0]))
            self.version.append(chr(struct.unpack("B", file.read(1))[0]))
            self.checksum = struct.unpack("I", file.read(4))[0]
            self.signature = file.read(20)
            self.file_size = struct.unpack("I", file.read(4))[0]
            self.header_size = struct.unpack("I", file.read(4))[0]
            self.endian_tag = hex(struct.unpack("I", file.read(4))[0])
            self.link_size = struct.unpack("I", file.read(4))[0]
            self.link_off = struct.unpack("I", file.read(4))[0]
            self.map_off = struct.unpack("I", file.read(4))[0]
            self.string_ids_size = struct.unpack("I", file.read(4))[0]
            self.string_ids_off = struct.unpack("I", file.read(4))[0]
            self.type_ids_size = struct.unpack("I", file.read(4))[0]
            self.type_ids_off = struct.unpack("I", file.read(4))[0]
            self.proto_ids_size = struct.unpack("I", file.read(4))[0]
            self.proto_ids_off = struct.unpack("I", file.read(4))[0]
            self.field_ids_size = struct.unpack("I", file.read(4))[0]
            self.field_ids_off = struct.unpack("I", file.read(4))[0]
            self.method_ids_size = struct.unpack("I", file.read(4))[0]
            self.method_ids_off = struct.unpack("I", file.read(4))[0]
            self.class_defs_size = struct.unpack("I", file.read(4))[0]
            self.class_defs_off = struct.unpack("I", file.read(4))[0]
            self.data_size = struct.unpack("I", file.read(4))[0]
            self.data_off = struct.unpack("I", file.read(4))[0]
            self.len = file.tell() - self.start

    def create(self, dexfile):
        self.magic = []
        self.magic.append('d')
        self.magic.append('e')
        self.magic.append('x')
        self.magic.append(0x0A)
        self.version = []
        self.version.append('0')
        self.version.append('3')
        self.version.append('5')
        self.version.append(0)
        self.checksum = 1234
        self.signature = "idontknow"
        self.file_size = 1234
        self.header_size = 112
        self.endian_tag = 0x12345678
        self.link_size = 0
        self.link_off = 0
        # self.map_off = dexfile.dexmaplist

    def copytofile(self, file):
        file.seek(self.start, 0)
        file.write(struct.pack("B", ord(self.magic[0])))
        file.write(struct.pack("B", ord(self.magic[1])))
        file.write(struct.pack("B", ord(self.magic[2])))
        file.write(struct.pack("B", ord(self.magic[3])))
        file.write(struct.pack("B", ord(self.version[0])))
        file.write(struct.pack("B", ord(self.version[1])))
        file.write(struct.pack("B", ord(self.version[2])))
        file.write(struct.pack("B", ord(self.version[3])))
        file.write(struct.pack("I", self.checksum))
        file.write(self.signature)
        file.write(struct.pack("I", self.file_size))
        file.write(struct.pack("I", self.header_size))
        file.write(struct.pack("I", int(self.endian_tag, 16)))
        file.write(struct.pack("I", self.link_size))
        file.write(struct.pack("I", self.link_off))
        file.write(struct.pack("I", self.map_off))
        file.write(struct.pack("I", self.string_ids_size))
        file.write(struct.pack("I", self.string_ids_off))
        file.write(struct.pack("I", self.type_ids_size))
        file.write(struct.pack("I", self.type_ids_off))
        file.write(struct.pack("I", self.proto_ids_size))
        file.write(struct.pack("I", self.proto_ids_off))
        file.write(struct.pack("I", self.field_ids_size))
        file.write(struct.pack("I", self.field_ids_off))
        file.write(struct.pack("I", self.method_ids_size))
        file.write(struct.pack("I", self.method_ids_off))
        file.write(struct.pack("I", self.class_defs_size))
        file.write(struct.pack("I", self.class_defs_off))
        file.write(struct.pack("I", self.data_size))
        file.write(struct.pack("I", self.data_off))

    def makeoffset(self, dexmaplist):
        self.string_ids_size = dexmaplist[1].size
        self.string_ids_off = dexmaplist[1].offset
        self.type_ids_size = dexmaplist[2].size
        self.type_ids_off = dexmaplist[2].offset
        self.proto_ids_size = dexmaplist[3].size
        self.proto_ids_off = dexmaplist[3].offset
        self.field_ids_size = dexmaplist[4].size
        self.field_ids_off = dexmaplist[4].offset
        self.method_ids_size = dexmaplist[5].size
        self.method_ids_off = dexmaplist[5].offset
        self.class_defs_size = dexmaplist[6].size
        self.class_defs_off = dexmaplist[6].offset
        self.data_off = dexmaplist[0x1000].offset
        self.data_size = 0
        self.map_off = dexmaplist[0x1000].offset
        self.file_size = 0

    def printf(self):
        print ("DEX FILE HEADER:")
        print ("magic: ", self.magic)
        print ("version: ", self.version)
        print ("checksum: ", self.checksum)
        print ("signature: ", self.signature)
        print ("file_size: ", self.file_size)
        print ("header_size: ", self.header_size)
        print ("endian_tag: ", self.endian_tag)
        print ("link_size: ", self.link_size)
        print ("link_off: ", self.link_off)
        print ("map_off: ", self.map_off)
        print ("string_ids_size: ", self.string_ids_size)
        print ("string_ids_off: ", self.string_ids_off)
        print ("type_ids_size: ", self.type_ids_size)
        print ("type_ids_off: ", self.type_ids_off)
        print ("proto_ids_size: ", self.proto_ids_size)
        print ("proto_ids_off: ", self.proto_ids_off)
        print ("field_ids_size: ", self.field_ids_size)
        print ("field_ids_off: ", self.field_ids_off)
        print ("method_ids_size: ", self.method_ids_size)
        print ("method_ids_off: ", self.method_ids_off)
        print ("class_defs_size: ", self.class_defs_size)
        print ("class_defs_off: ", self.class_defs_off)
        print ("data_size: ", self.data_size)
        print ("data_off: ", self.data_off)

class DexStringID:
    def __init__(self, file, mode=1):
        if mode == 1:
            self.stringDataoff = struct.unpack("I", file.read(4))[0]  # in file
            file.seek(self.stringDataoff, 0)
            self.size = readunsignedleb128(file)
            self.str = getutf8str(file)
            self.ref = None
        else:
            self.stringDataoff = 0
            self.size = 0
            self.str = ""
            self.ref = None

    def addstrID(self, str):
        self.ref = str
        self.str = getstr(str.str)

    def copytofile(self, file):
        # self.stringDataoff = self.ref.start
        file.write(struct.pack("I", self.ref.start))

    def getreference(self, dexmaplist):
        self.ref = dexmaplist[0x2002].getreference(self.stringDataoff)

    def printf(self):
        print ("size: ", self.size, " str: ", self.str, "dataof: ", self.stringDataoff)

class DexTypeID:
    def __init__(self, file, str_table, mode=1):
        if mode == 1:
            self.descriptorIdx = struct.unpack("I", file.read(4))[0]   # in file
            self.str = str_table[self.descriptorIdx].str
        else:
            self.descriptorIdx = 0
            self.str = ""

    def addtype(self, index, string):
        self.descriptorIdx = index
        self.str = string

    def copytofile(self, file):
        file.write(struct.pack("I", self.descriptorIdx))

    def printf(self):
        print ("type id: ", self.str)

class DexProtoId:
    def __init__(self, file, str_table, type_table, mode=1):
        if mode == 1:
            self.shortyIdx = struct.unpack("I", file.read(4))[0]   # in file
            self.returnTypeIdx = struct.unpack("I", file.read(4))[0]   # in file
            self.parametersOff = struct.unpack("I", file.read(4))[0]   # in file
            self.name = str_table[self.shortyIdx].str
            self.returnstr = type_table[self.returnTypeIdx].str
            self.ref = None
        else:
            self.shortyIdx = 0
            self.returnTypeIdx = 0
            self.parametersOff = 0
            self.ref = None

    def addproto(self, idx, typeidx, reference):
        self.shortyIdx = idx
        self.returnTypeIdx = typeidx
        self.ref = reference

    def copytofile(self, file):
        file.write(struct.pack("I", self.shortyIdx))
        file.write(struct.pack("I", self.returnTypeIdx))
        if self.ref is not None:
            file.write(struct.pack("I", self.ref.start))
        else:
            file.write(struct.pack("I", 0))

    def getreference(self, dexmaplist):
        self.ref = dexmaplist[0x1001].getreference(self.parametersOff)

    def printf(self):
        print ("return Type:", self.returnstr)
        print ("methodname:", self.name)
        if self.ref is not None:
            self.ref.printf()

class DexFieldId:
    def __init__(self, file, str_table, type_table, mode=1):
        if mode == 1:
            self.classIdx = struct.unpack("H", file.read(2))[0]    # in file
            self.typeIdx = struct.unpack("H", file.read(2))[0]  # in file
            self.nameIdx = struct.unpack("I", file.read(4))[0]  # in file
            self.classstr = type_table[self.classIdx].str
            self.typestr = type_table[self.typeIdx].str
            self.name = str_table[self.nameIdx].str

    def addfield(self, classidx, typeidx, nameidx):
        self.classIdx = classidx
        self.typeIdx = typeidx
        self.nameIdx = nameidx

    def copytofile(self, file):
        file.write(struct.pack("H", self.classIdx))
        file.write(struct.pack("H", self.typeIdx))
        file.write(struct.pack("I", self.nameIdx))

    def printf(self):
        print ("classstr:", self.classstr)
        print ("typestr:", self.typestr)
        print ("name:", self.name)
        print ()

class DexMethodId:
    def __init__(self, file, str_table, type_table, proto_table, mode=1):
        if mode == 1:
            self.classIdx = struct.unpack("H", file.read(2))[0]    # in file
            self.protoIdx = struct.unpack("H", file.read(2))[0]    # in file
            self.nameIdx = struct.unpack("I", file.read(4))[0]  # in file
            self.classstr = type_table[self.classIdx].str
            self.name = str_table[self.nameIdx].str
        else:
            self.classIdx = 0
            self.protoIdx = 0
            self.nameIdx = 0

    def addmethod(self, class_idx, proto_idx, name_idx):
        self.classIdx = class_idx
        self.protoIdx = proto_idx
        self.nameIdx = name_idx

    def copytofile(self, file):
        file.write(struct.pack("H", self.classIdx))
        file.write(struct.pack("H", self.protoIdx))
        file.write(struct.pack("I", self.nameIdx))

    def printf(self):
        print ("classstr:", self.classstr)
        print ("name:", self.name)
        print ()

class DexClassDef:
    def __init__(self, file, str_table, type_table, mode=1):
        if mode == 1:
            self.classIdx = struct.unpack("I", file.read(4))[0]  # in file
            self.accessFlags = struct.unpack("I", file.read(4))[0]  # in file
            self.superclassIdx = struct.unpack("I", file.read(4))[0]  # in file
            self.interfacesOff = struct.unpack("I", file.read(4))[0]  # in file
            self.sourceFileIdx = struct.unpack("I", file.read(4))[0]  # in file
            self.annotationsOff = struct.unpack("I", file.read(4))[0]  # in file
            self.classDataOff = struct.unpack("I", file.read(4))[0]  # in file
            self.staticValuesOff = struct.unpack("I", file.read(4))[0]  # in file
            self.classstr = type_table[self.classIdx].str
            self.superclassstr = type_table[self.superclassIdx].str
            if self.sourceFileIdx == 0xFFFFFFFF:
                self.sourceFilestr = "NO_INDEX"
            else:
                self.sourceFilestr = str_table[self.sourceFileIdx].str
        else:
            self.classIdx = 0
            self.accessFlags = 0
            self.superclassIdx = 0
            self.interfacesOff = 0
            self.sourceFileIdx = 0
            self.annotationsOff = 0
            self.classDataOff = 0
            self.staticValuesOff = 0
        self.interfacesRef = None
        self.annotationsRef = None
        self.classDataRef = None
        self.staticValuesRef = None

    def addclassdef(self, classidx, access, superclass, source):
        self.classIdx = classidx
        self.accessFlags = access
        self.superclassIdx = superclass
        self.sourceFileIdx = source

    def addclassdefref(self, interref, annoref, classref, staticref):
        self.interfacesRef = interref
        self.annotationsRef = annoref
        self.classDataRef = classref
        self.staticValuesRef = staticref

    # get class data reference by its name,e.g. Lcom/cc/test/MainActivity;
    def getclassdefref(self, str):
        if self.classstr == str and self.classDataOff > 0:
            return self.classDataRef
        return None

    def copytofile(self, file):
        file.write(struct.pack("I", self.classIdx))
        file.write(struct.pack("I", self.accessFlags))
        file.write(struct.pack("I", self.superclassIdx))
        if self.interfacesRef is not None:
            file.write(struct.pack("I", self.interfacesRef.start))
            # print(self.interfacesRef.start)
        else:
            file.write(struct.pack("I", 0))
        file.write(struct.pack("I", self.sourceFileIdx))
        if self.annotationsRef is not None:
            file.write(struct.pack("I", self.annotationsRef.start))
            # print(self.annotationsRef.start)
        else:
            file.write(struct.pack("I", 0))
        if self.classDataRef is not None:
            file.write(struct.pack("I", self.classDataRef.start))
        else:
            file.write(struct.pack("I", 0))
        if self.staticValuesRef is not None:
            file.write(struct.pack("I", self.staticValuesRef.start))
        else:
            file.write(struct.pack("I", 0))

    def getreference(self, dexmaplist):
        self.interfacesRef = dexmaplist[0x1001].getreference(self.interfacesOff)
        if 0x2006 in dexmaplist.keys():
            self.annotationsRef = dexmaplist[0x2006].getreference(self.annotationsOff)
        self.classDataRef = dexmaplist[0x2000].getreference(self.classDataOff)
        if 0x2005 in dexmaplist.keys():
            self.staticValuesRef = dexmaplist[0x2005].getreference(self.staticValuesOff)

    def printf(self):
        print ("classtype:", self.classIdx, self.classstr)
        print("access flag:", self.accessFlags)
        print ("superclasstype:", self.superclassIdx, self.superclassstr)
        print ("iterface off", self.interfacesOff)
        print("source file index", self.sourceFilestr)
        print("annotations off", self.annotationsOff)
        print("class data off", self.classDataOff)
        print("static values off", self.staticValuesOff)
        if self.interfacesRef is not None:
            self.interfacesRef.printf()
        if self.annotationsRef is not None:
            self.annotationsRef.printf()
        if self.classDataRef is not None:
            self.classDataRef.printf()
        if self.staticValuesRef is not None:
            self.staticValuesRef.printf()

class StringData:
    def __init__(self, file, mode = 1):
        if mode == 1:
            self.start = file.tell()
            self.len = 0
            self.size = readunsignedleb128(file)  # in file
            self.str = []  # getutf8str(file)  # in file
            while 1:
                onebyte = struct.unpack("B", file.read(1))[0]
                if onebyte == 0:
                    break
                self.str.append(onebyte)
        else:
            self.start = 0
            self.len = 0
            self.size = 0
            self.str = []

    def addstr(self, str):
        self.size = len(str)
        self.str = bytearray(str)

    def copytofile(self, file):
        writeunsignedleb128(self.size, file)
        for i in range(0, len(self.str)):
            file.write(struct.pack("B", self.str[i]))
        file.write(struct.pack("B", 0))

    def makeoffset(self, off):
        self.start = off
        self.len = len(self.str) + unsignedleb128forlen(self.size)
        return off + self.len + 1   # 1 byte for '\0'

    def modify(self, str):
        self.size = len(str)
        self.str = bytearray(str)

    def printf(self):
        print (getstr(self.str))

class TypeItem:  # alignment: 4 bytes
    def __init__(self, file, type_table, mode=1):
        if mode == 1:
            self.start = file.tell()
            self.size = struct.unpack("I", file.read(4))[0]  # in file
            self.list = []
            self.str = []
            self.len = 0
            for i in range(0, self.size):
                self.list.append(struct.unpack("H", file.read(2))[0])  # in file
                self.str.append(type_table[self.list[i]].str)
            if self.size % 2 == 1:
                struct.unpack("H", file.read(2))   # for alignment
        else:
            self.start = 0
            self.size = 0
            self.list = None
            self.str = None
            self.len = 0

    def addtypeItem(self, type_list, str_list):
        self.size = len(type_list)
        self.list = type_list
        self.str = str_list

    def copytofile(self, file):
        file.write(struct.pack("I", self.size))
        for i in range(0, self.size):
            file.write(struct.pack("H", self.list[i]))
        if self.size % 2 == 1:
            file.write(struct.pack("H", 0))

    def equal(self, param_list, length):
        if length != self.size:
            return False
        for i in range(0, self.size):
            if param_list[i] != self.str[i]:
                return False
        return True

    def makeoffset(self, off):
        align = off % 4
        if align != 0:
            off += (4 - align)
        self.len = 4 + 2 * self.size
        self.start = off
        return off + self.len

    def printf(self):
        for i in range(0, self.size):
            print (self.list[i], self.str[i])

# alignment: 4bytes
class AnnotationsetItem:
    def __init__(self, file):
        self.start = file.tell()
        self.len = 0
        self.size = struct.unpack("I", file.read(4))[0]   # in file
        self.entries = []  # annotation_off, offset of annotation_item
        self.ref = []
        for i in range(0, self.size):
            self.entries.append(struct.unpack("I", file.read(4))[0])

    def copytofile(self, file):
        file.write(struct.pack("I", self.size))
        for i in range(0, self.size):
            file.write(struct.pack("I", self.ref[i].start))

    def makeoffset(self, off):
        align = off % 4
        if align != 0:
            off += (4 - align)
        self.start = off
        self.len = 4 + 4 * self.size
        return off + self.len

    def getreference(self, dexmaplist):
        for i in range(0, self.size):
            self.ref.append(dexmaplist[0x2004].getreference(self.entries[i]))

    def printf(self):
        print ("size: ", self.size)
        
# alignment: 4bytes
class AnnotationsetrefList:
    def __init__(self, file):
        self.start = file.tell()
        self.size = struct.unpack("I", file.read(4))[0]  # in file
        self.list = []  # annotaions_off, offset of annotation_set_item
        self.ref = []
        self.len = 0
        for i in range(0, self.size):
            self.list.append(struct.unpack("I", file.read(4))[0])

    def copytofile(self, file):
        file.write(struct.pack("I", self.size))
        for i in range(0, self.size):
            if self.ref[i] is not None:
                file.write(struct.pack("I", self.ref[i].start))
            else:
                file.write(struct.pack("I", 0))

    def makeoffset(self, off):
        align = off % 4
        if align != 0:
            off += (4 - align)
        self.start = off
        self.len = 4 + 4 * self.size
        return off + self.len

    def getreference(self, dexmaplist):
        for i in range(0, self.size):
            self.ref.append(dexmaplist[0x1003].getreference(self.list[i]))

    def printf(self):
        print ("size: ", self.size)

class Encodedfield:
    def __init__(self, file, mode=1):
        if mode == 1:
            self.start = file.tell()
            self.len = 0
            self.field_idx_diff = readunsignedleb128(file)
            self.access_flags = readunsignedleb128(file)
        else:
            self.len = 0
            self.field_idx_diff = 0
            self.access_flags = 1
        self.field_idx = 0      # need to set later

    def __lt__(self, other):    # for sort
        return self.field_idx_diff < other.field_idx_diff

    def addfield(self, idx, flag):
        self.field_idx = idx
        self.access_flags = int(flag)

    def copytofile(self, file):
        writeunsignedleb128(self.field_idx_diff, file)
        writeunsignedleb128(self.access_flags, file)

    def makeoffset(self, off):
        self.start = off
        self.len += unsignedleb128forlen(self.field_idx_diff)
        self.len += unsignedleb128forlen(self.access_flags)
        return off + self.len

    def printf(self):
        print ("diff: ", self.field_idx_diff)
        print ("access: ", self.access_flags)

class Encodedmethod:
    def __init__(self, file, mode=1):
        if mode == 1:
            self.start = file.tell()
            self.len = 0
            self.method_idx_diff = readunsignedleb128(file)
            self.access_flags = readunsignedleb128(file)
            self.code_off = readunsignedleb128(file)
            self.coderef = None
        else:
            self.len = 0
            self.method_idx_diff = 0
            self.access_flags = 0
            self.coderef = 0
        self.method_idx = 0     # need to set later
        self.modified = 0   # if set this var, means that code_off will moodified to zero

    def addmethod(self, method_idx, access, ref):
        self.method_idx = method_idx
        self.access_flags = int(access)
        self.coderef = ref

    def copytofile(self, file):
        writeunsignedleb128(self.method_idx_diff, file)
        writeunsignedleb128(self.access_flags, file)
        if self.modified == 1:
            writeunsignedleb128(0, file)
        elif self.coderef is not None:
            writeunsignedleb128(self.coderef.start, file)
        else:
            writeunsignedleb128(0, file)

    def makeoffset(self, off):
        self.start = off
        self.len += unsignedleb128forlen(self.method_idx_diff)
        self.len += unsignedleb128forlen(self.access_flags)
        if self.modified == 1:
            self.len += unsignedleb128forlen(0)
        elif self.coderef is not None:
            self.len += unsignedleb128forlen(self.coderef.start)
        else:
            self.len += unsignedleb128forlen(0)
        return off + self.len

    def getreference(self, dexmaplist):
        self.coderef = dexmaplist[0x2001].getreference(self.code_off)

    def printf(self):
        print ("method_idx_diff: ", self.method_idx_diff)
        print("method idx:", self.method_idx)
        print ("access: ", self.access_flags)
        print ("code off: ", self.code_off)


# alignment:none
class ClassdataItem:
    def __init__(self, file, mode=1):
        if mode == 1:
            self.start = file.tell()
            self.len = 0
            self.static_field_size = readunsignedleb128(file)
            self.instance_fields_size = readunsignedleb128(file)
            self.direct_methods_size = readunsignedleb128(file)
            self.virtual_methods_size = readunsignedleb128(file)
            self.static_fields = []
            self.instance_fields = []
            self.direct_methods = []
            self.virtual_methods = []
            for i in range(0, self.static_field_size):
                self.static_fields.append(Encodedfield(file))
            for i in range(0, self.instance_fields_size):
                self.instance_fields.append(Encodedfield(file))
            for i in range(0, self.direct_methods_size):
                self.direct_methods.append(Encodedmethod(file))
            for i in range(0, self.virtual_methods_size):
                self.virtual_methods.append(Encodedmethod(file))
        else:
            self.static_field_size = 0
            self.instance_fields_size = 0
            self.direct_methods_size = 0
            self.virtual_methods_size = 0
            self.static_fields = []
            self.instance_fields = []
            self.direct_methods = []
            self.virtual_methods = []

    def addstaticfield(self, field_idx, accessflag):
        self.static_field_size += 1
        field = Encodedfield(None, 2)
        field.addfield(field_idx, accessflag)
        self.static_fields.append(field)

    def addinstancefield(self, field_idx, accessflag):
        self.instance_fields_size += 1
        field = Encodedfield(None, 2)
        field.addfield(field_idx, accessflag)
        self.instance_fields.append(field)

    def adddirectmethod(self, method_idx, accessflag, code_ref):
        method = Encodedmethod(None, 2)
        method.addmethod(method_idx, accessflag, code_ref)
        self.direct_methods_size += 1
        self.direct_methods.append(method)

    def addvirtualmethod(self, method_idx, accessflag, code_ref):
        method = Encodedmethod(None, 2)
        method.addmethod(method_idx, accessflag, code_ref)
        self.virtual_methods_size += 1
        self.virtual_methods.append(method)

    def commit(self):   # call this when everything done, just for static field by now
        if self.static_field_size > 0:
            # self.static_fields.sort() # since each field added has the largest index
            # there is no need to sort the list
            last = 0
            for i in range(0, self.static_field_size):
                self.static_fields[i].field_idx_diff = self.static_fields[i].field_idx - last
                last = self.static_fields[i].field_idx
        if self.instance_fields_size > 0:
            last = 0
            for i in range(0, self.instance_fields_size):
                self.instance_fields[i].field_idx_diff = self.instance_fields[i].field_idx - last
                last = self.instance_fields[i].field_idx
        if self.direct_methods_size > 0:
            last = 0
            for i in range(0, self.direct_methods_size):
                self.direct_methods[i].method_idx_diff = self.direct_methods[i].method_idx - last
                last = self.direct_methods[i].method_idx
        if self.virtual_methods_size > 0:
            last = 0
            for i in range(0, self.virtual_methods_size):
                self.virtual_methods[i].method_idx_diff = self.virtual_methods[i].method_idx - last
                last = self.virtual_methods[i].method_idx

    def copytofile(self, file):
        writeunsignedleb128(self.static_field_size, file)
        writeunsignedleb128(self.instance_fields_size, file)
        writeunsignedleb128(self.direct_methods_size, file)
        writeunsignedleb128(self.virtual_methods_size, file)
        for i in range(0, self.static_field_size):
            self.static_fields[i].copytofile(file)
        for i in range(0, self.instance_fields_size):
            self.instance_fields[i].copytofile(file)
        for i in range(0, self.direct_methods_size):
            self.direct_methods[i].copytofile(file)
        for i in range(0, self.virtual_methods_size):
            self.virtual_methods[i].copytofile(file)

    # besides adding refenrence, also need to set the correct index
    def getreference(self, dexmaplist):
        last = 0
        for i in range(0, self.static_field_size):
            self.static_fields[i].field_idx = last + self.static_fields[i].field_idx_diff
            last = self.static_fields[i].field_idx
        last = 0
        for i in range(0, self.instance_fields_size):
            self.instance_fields[i].field_idx = last + self.instance_fields[i].field_idx_diff
            last = self.instance_fields[i].field_idx
        last = 0
        for i in range(0, self.direct_methods_size):
            self.direct_methods[i].getreference(dexmaplist)
            self.direct_methods[i].method_idx = last + self.direct_methods[i].method_idx_diff
            last = self.direct_methods[i].method_idx
        last = 0
        for i in range(0, self.virtual_methods_size):
            self.virtual_methods[i].getreference(dexmaplist)
            self.virtual_methods[i].method_idx = last + self.virtual_methods[i].method_idx_diff
            last = self.virtual_methods[i].method_idx

    def makeoffset(self, off):
        self.start = off
        off += unsignedleb128forlen(self.static_field_size)
        off += unsignedleb128forlen(self.instance_fields_size)
        off += unsignedleb128forlen(self.direct_methods_size)
        off += unsignedleb128forlen(self.virtual_methods_size)
        for i in range(0, self.static_field_size):
            off = self.static_fields[i].makeoffset(off)
        for i in range(0, self.instance_fields_size):
            off = self.instance_fields[i].makeoffset(off)
        for i in range(0, self.direct_methods_size):
            off = self.direct_methods[i].makeoffset(off)
        for i in range(0, self.virtual_methods_size):
            off = self.virtual_methods[i].makeoffset(off)
        self.len = off - self.start
        return off

    def printf(self):
        print ("static field size: ", self.static_field_size)
        print ("instance fields size: ", self.instance_fields_size)
        print ("direct methods size: ", self.direct_methods_size)
        print ("virtual methods size: ", self.virtual_methods_size)
        for i in range(0, self.static_field_size):
            self.static_fields[i].printf()
        for i in range(0, self.instance_fields_size):
            self.instance_fields[i].printf()
        for i in range(0, self.direct_methods_size):
            self.direct_methods[i].printf()
        for i in range(0, self.virtual_methods_size):
            self.virtual_methods[i].printf()

class TryItem:
    def __init__(self, file):
        self.start = file.tell()
        self.start_addr = struct.unpack("I", file.read(4))[0] # in file
        self.insn_count = struct.unpack("H", file.read(2))[0]    # in file
        self.handler_off = struct.unpack("H", file.read(2))[0]    # in file
        self.len = 0

    def copytofile(self, file):
        file.write(struct.pack("I", self.start_addr))
        file.write(struct.pack("H", self.insn_count))
        file.write(struct.pack("H", self.handler_off))

    def makeoffset(self, off):
        self.start = off
        self.len = 4 + 2 + 2
        return off + self.len

    def printf(self):
        print ("start_Addr: ", self.start_addr)
        print ("insn_count: ", self.insn_count)
        print ("handler_off: ", self.handler_off)
        print ()

class EncodedTypeAddrPair:
    def __init__(self, file):
        self.type_idx = readunsignedleb128(file)
        self.addr = readunsignedleb128(file)

    def copytofile(self, file):
        writeunsignedleb128(self.type_idx, file)
        writeunsignedleb128(self.addr, file)

    def makeoffset(self, off):
        off += unsignedleb128forlen(self.type_idx)
        off += unsignedleb128forlen(self.addr)
        return off

    def printf(self):
        print ("type idx: ", self.type_idx)
        print ("addr: ", self.addr)
        print ()

class EncodedhandlerItem:
    def __init__(self, file):
        self.start = file.tell()
        self.len = 0
        self.size = readsignedleb128(file)
        self.handlers = []
        # print("start handler item", abs(self.size))
        for i in range(0, abs(self.size)):
            self.handlers.append(EncodedTypeAddrPair(file))
        if self.size <= 0:
            self.catch_all_addr = readunsignedleb128(file)

    def copytofile(self, file):
        writesignedleb128(self.size, file)
        for i in range(0, abs(self.size)):
            self.handlers[i].copytofile(file)
        if self.size <= 0:
            writeunsignedleb128(self.catch_all_addr, file)

    def makeoffset(self, off):
        self.start = off
        off += signedleb128forlen(self.size)
        for i in range(0, abs(self.size)):
            off = self.handlers[i].makeoffset(off)
        if self.size <= 0:
            off += unsignedleb128forlen(self.catch_all_addr)
        self.len = off - self.start
        return off

class EncodedhandlerList:
    def __init__(self, file):
        self.start = file.tell()
        self.len = 0
        self.size = readunsignedleb128(file)
        self.list = []
        for i in range(0, self.size):
            self.list.append(EncodedhandlerItem(file))

    def copytofile(self, file):
        file.seek(self.start, 0)
        writeunsignedleb128(self.size, file)
        for i in range(0, self.size):
            self.list[i].copytofile(file)

    def makeoffset(self, off):
        self.start = off
        off += unsignedleb128forlen(self.size)
        for i in range(0, self.size):
            off = self.list[i].makeoffset(off)
        return off

# alignment: 4bytes
class CodeItem:
    def __init__(self, file, mode=1):
        if mode == 1:
            self.start = file.tell()
            self.len = 0
            self.register_size = struct.unpack("H", file.read(2))[0]    # in file
            self.ins_size = struct.unpack("H", file.read(2))[0]    # in file
            self.outs_size = struct.unpack("H", file.read(2))[0]    # in file
            self.tries_size = struct.unpack("H", file.read(2))[0]    # in file
            self.debug_info_off = struct.unpack("I", file.read(4))[0]  # in file
            self.insns_size = struct.unpack("I", file.read(4))[0]  # in file
            self.insns = []
            self.debugRef = None
            for i in range(0, self.insns_size):
                self.insns.append(struct.unpack("H", file.read(2))[0])
            if self.tries_size != 0 and self.insns_size % 2 == 1:
                self.padding = struct.unpack("H", file.read(2))[0]
            self.tries = []
            for i in range(0, self.tries_size):
                self.tries.append(TryItem(file))
            if self.tries_size != 0:
                self.handler = EncodedhandlerList(file)
            align = file.tell() % 4    # for alignment
            if align != 0:
                file.read(4-align)
        else:
            self.start = 0
            self.len = 0
            self.register_size = 0
            self.ins_size = 0
            self.outs_size = 0
            self.tries_size = 0
            self.debug_info_off = 0
            self.insns_size = 0
            self.insns = []
            self.debugRef = None
            self.padding = 0
            self.tries = []
            self.handler = None

    def addcode(self, reg_size, insize, outsize, triessize, debugoff, inssize, insnslist, debugref, trieslist, handlerref):
        self.register_size = reg_size
        self.ins_size = insize
        self.outs_size = outsize
        self.tries_size = triessize
        self.debug_info_off = debugoff
        self.insns_size = inssize
        self.insns = insnslist
        self.debugRef = debugref
        self.tries = trieslist
        self.handler = handlerref

    def copytofile(self, file):
        file.seek(self.start, 0)
        file.write(struct.pack("H", self.register_size))
        file.write(struct.pack("H", self.ins_size))
        file.write(struct.pack("H", self.outs_size))
        file.write(struct.pack("H", self.tries_size))
        if self.debugRef is not None:
            file.write(struct.pack("I", self.debugRef.start))
        else:
            file.write(struct.pack("I", 0))
        file.write(struct.pack("I", self.insns_size))
        for i in range(0, self.insns_size):
            file.write(struct.pack("H", self.insns[i]))
        if self.tries_size != 0 and self.insns_size % 2 == 1:
            file.write(struct.pack("H", self.padding))
        for i in range(0, self.tries_size):
            self.tries[i].copytofile(file)
        if self.tries_size != 0:
            self.handler.copytofile(file)
        align = file.tell() % 4    # for alignment
        if align != 0:
            for i in range(0, 4-align):
                file.write(struct.pack("B", 0))
        # print("code item addr:", file.tell())

    def makeoffset(self, off):
        align = off % 4
        if align != 0:
            off += (4 - align)
        self.start = off
        off += (4 * 2 + 2 * 4)  # 4 ushort and 2 uint
        off += (2 * self.insns_size)
        if self.tries_size != 0 and self.insns_size % 2 == 1:   # for padding
            off += 2
        for i in range(0, self.tries_size):
            off = self.tries[i].makeoffset(off)
        if self.tries_size != 0:
            off = self.handler.makeoffset(off)
        self.len = off - self.start
        return off

    def getreference(self, dexmaplist):
        self.debugRef = dexmaplist[0x2003].getreference(self.debug_info_off)

    def printf(self):
        print("registers_size:", self.register_size)
        print("ins_size, outs_size, tries_size:", self.ins_size, self.outs_size, self.tries_size)
        print("debug info of:", self.debug_info_off)
        print("insn_size:", self.insns_size)
        for i in range(0, self.insns_size):
            print(self.insns[i])
        tmp = Instruction.InstructionSet(self.insns)
        tmp.printf()

# alignment: none
class AnnotationItem:
    Visibity = {0: 'VISIBITITY_BUILD', 1: 'VISIBILITY_RUNTIME', 2: 'VISIBILITY_SYSTEM'}
    
    def __init__(self, file):
        self.start = file.tell()
        self.len = 0
        self.visibility = struct.unpack("B", file.read(1))[0]  # infile
        self.annotation = EncodedAnnotation(file)

    def copytofile(self, file):
        file.write(struct.pack("B", self.visibility))
        self.annotation.copytofile(file)

    def makeoffset(self, off):
        self.start = off
        off += 1
        off = self.annotation.makeoffset(off)
        self.len = off - self.start
        return off

# alignment: none
class EncodedArrayItem:
    def __init__(self, file):
        self.start = file.tell()
        self.len = 0
        self.value = EncodedArray(file)

    def copytofile(self, file):
        self.value.copytofile(file)

    def makeoffset(self, off):
        # if self.start == 1096008:
        self.start = off
        off = self.value.makeoffset(off)
        self.len = off - self.start
        return off

    def printf(self):
        print("None for EncodedArrayItem by now")

class FieldAnnotation:
    def __init__(self, file):
        self.field_idx = struct.unpack("I", file.read(4))[0]   # in file
        self.annotations_off = struct.unpack("I", file.read(4))[0]   # in file, offset of annotation_set_item
        self.annotations_off_ref = None

    def copytofile(self, file):
        file.write(struct.pack("I", self.field_idx))
        file.write(struct.pack("I", self.annotations_off_ref.start))

    def makeoffset(self, off):
        off += 4 * 2
        return off

    def getreference(self, dexmaplist):
        self.annotations_off_ref = dexmaplist[0x1003].getreference(self.annotations_off)

class MethodAnnotation:
    def __init__(self, file):
        self.method_idx = struct.unpack("I", file.read(4))[0]   # in file
        self.annotations_off = struct.unpack("I", file.read(4))[0]   # in file
        self.annotations_off_ref = None

    def copytofile(self, file):
        file.write(struct.pack("I", self.method_idx))
        file.write(struct.pack("I", self.annotations_off_ref.start))

    def makeoffset(self, off):
        off += 4 * 2
        return off

    def getreference(self, dexmaplist):
        self.annotations_off_ref = dexmaplist[0x1003].getreference(self.annotations_off)

class ParamterAnnotation:
    def __init__(self, file):
        self.method_idx = struct.unpack("I", file.read(4))[0]   # in file
        self.annotations_off = struct.unpack("I", file.read(4))[0]   # in file. offset of "annotation_set_ref_list"
        self.annotations_off_ref = None

    def copytofile(self, file):
        file.write(struct.pack("I", self.method_idx))
        file.write(struct.pack("I", self.annotations_off_ref.start))

    def makeoffset(self, off):
        off += 4 * 2
        return off

    def getreference(self, dexmaplist):
        self.annotations_off_ref = dexmaplist[0x1002].getreference(self.annotations_off)

# alignment: 4 bytes
class AnnotationsDirItem:
    def __init__(self, file):
        self.start = file.tell()
        self.len = 0
        self.class_annotations_off = struct.unpack("I", file.read(4))[0]   # in file
        self.fields_size = struct.unpack("I", file.read(4))[0]   # in file
        self.annotated_methods_size = struct.unpack("I", file.read(4))[0]   # in file
        self.annotate_parameters_size = struct.unpack("I", file.read(4))[0]   # in file
        self.field_annotations = []  # field_annotation[size]
        self.method_annotations = []
        self.parameter_annotations = []
        self.class_annotations_ref = None
        for i in range(0, self.fields_size):
            self.field_annotations.append(FieldAnnotation(file))
        for i in range(0, self.annotated_methods_size):
            self.method_annotations.append(MethodAnnotation(file))
        for i in range(0, self.annotate_parameters_size):
            self.parameter_annotations.append(ParamterAnnotation(file))

    def copytofile(self, file):
        if self.class_annotations_ref is not None:
            file.write(struct.pack("I", self.class_annotations_ref.start))
        else:
            file.write(struct.pack("I", self.class_annotations_off))
        file.write(struct.pack("I", self.fields_size))
        file.write(struct.pack("I", self.annotated_methods_size))
        file.write(struct.pack("I", self.annotate_parameters_size))
        for i in range(0, self.fields_size):
            self.field_annotations[i].copytofile(file)
        for i in range(0, self.annotated_methods_size):
            self.method_annotations[i].copytofile(file)
        for i in range(0, self.annotate_parameters_size):
            self.parameter_annotations[i].copytofile(file)

    def makeoffset(self, off):
        self.start = off
        off += 4 * 4
        for i in range(0, self.fields_size):
            off = self.field_annotations[i].makeoffset(off)
        for i in range(0, self.annotated_methods_size):
            off = self.method_annotations[i].makeoffset(off)
        for i in range(0, self.annotate_parameters_size):
            off = self.parameter_annotations[i].makeoffset(off)
        self.len = off - self.start
        return off

    def getreference(self, dexmaplist):
        self.class_annotations_ref = dexmaplist[0x1003].getreference(self.class_annotations_off)
        for i in range(0, self.fields_size):
            self.field_annotations[i].getreference(dexmaplist)
        for i in range(0, self.annotated_methods_size):
            self.method_annotations[i].getreference(dexmaplist)
        for i in range(0, self.annotate_parameters_size):
            self.parameter_annotations[i].getreference(dexmaplist)

    def printf(self):
        print("None for AnnotationDirItem by now")

# alignment: none           
class DebugInfo:
    def __init__(self, file, mode=1):
        if mode == 1:
            self.start = file.tell()
            self.len = 0
            self.line_start = readunsignedleb128(file)
            self.parameters_size = readunsignedleb128(file)
            self.parameter_names = []
            for i in range(0, self.parameters_size):
                self.parameter_names.append(readunsignedleb128p1(file))
            self.debug = []
            while 1:
                onebyte = struct.unpack("B", file.read(1))[0]
                self.debug.append(onebyte)
                if onebyte == 0:
                    break
                elif onebyte == 1:
                    self.debug.append(readunsignedleb128(file))
                elif onebyte == 2:
                    self.debug.append(readsignedleb128(file))
                elif onebyte == 3:
                    self.debug.append(readunsignedleb128(file))
                    self.debug.append(readunsignedleb128p1(file))
                    self.debug.append(readunsignedleb128p1(file))
                elif onebyte == 4:
                    self.debug.append(readunsignedleb128(file))
                    self.debug.append(readunsignedleb128p1(file))
                    self.debug.append(readunsignedleb128p1(file))
                    self.debug.append(readunsignedleb128p1(file))
                elif onebyte == 5:
                    self.debug.append(readunsignedleb128(file))
                elif onebyte == 6:
                    self.debug.append(readunsignedleb128(file))
                elif onebyte == 9:
                    self.debug.append(readunsignedleb128p1(file))
        else:
            self.start = 0
            self.len = 0
            self.line_start = 0
            self.parameters_size = 0
            self.parameter_names = []
            self.debug = []

    def adddebugitem(self, linestart, paramsize, names_list, debug_list):
        self.line_start = linestart
        self.parameters_size = paramsize
        self.parameter_names = names_list
        self.debug = debug_list

    def copytofile(self, file):
        file.seek(self.start, 0)
        writeunsignedleb128(self.line_start, file)
        writeunsignedleb128(self.parameters_size, file)
        for i in range(0, self.parameters_size):
            # print(self.parameter_names[i])
            # if i == self.parameters_size-1:
                # writeunsignedleb128p1alignshort(self.parameter_names[i], file)
            # else:
            writeunsignedleb128p1(self.parameter_names[i], file)
        index = 0
        while 1:
            onebyte = self.debug[index]
            file.write(struct.pack("B", onebyte))
            index += 1
            if onebyte == 0:
                break
            elif onebyte == 1:
                writeunsignedleb128(self.debug[index], file)
                index += 1
            elif onebyte == 2:
                writesignedleb128(self.debug[index], file)
                index += 1
            elif onebyte == 3:
                writeunsignedleb128(self.debug[index], file)
                writeunsignedleb128p1(self.debug[index+1], file)
                writeunsignedleb128p1(self.debug[index+2], file)
                index += 3
            elif onebyte == 4:
                writeunsignedleb128(self.debug[index], file)
                writeunsignedleb128p1(self.debug[index+1], file)
                writeunsignedleb128p1(self.debug[index+2], file)
                writeunsignedleb128p1(self.debug[index+3], file)
                index += 4
            elif onebyte == 5:
                writeunsignedleb128(self.debug[index], file)
                index += 1
            elif onebyte == 6:
                writeunsignedleb128(self.debug[index], file)
                index += 1
            elif onebyte == 9:
                writeunsignedleb128p1(self.debug[index], file)
                index += 1

    def printf(self):
        print(self.line_start, self.parameters_size)

    def makeoffset(self, off):
        self.start = off
        off += unsignedleb128forlen(self.line_start)
        off += unsignedleb128forlen(self.parameters_size)
        for i in range(0, self.parameters_size):
            off += unsignedleb128p1forlen(self.parameter_names[i])
        index = 0
        while 1:
            onebyte = self.debug[index]
            off += 1
            index += 1
            if onebyte == 0:
                break
            elif onebyte == 1:
                off += unsignedleb128forlen(self.debug[index])
                index += 1
            elif onebyte == 2:
                off += signedleb128forlen(self.debug[index])
                index += 1
            elif onebyte == 3:
                off += unsignedleb128forlen(self.debug[index])
                off += unsignedleb128p1forlen(self.debug[index+1])
                off += unsignedleb128p1forlen(self.debug[index+2])
                index += 3
            elif onebyte == 4:
                off += unsignedleb128forlen(self.debug[index])
                off += unsignedleb128p1forlen(self.debug[index+1])
                off += unsignedleb128p1forlen(self.debug[index+2])
                off += unsignedleb128p1forlen(self.debug[index+3])
                index += 4
            elif onebyte == 5:
                off += unsignedleb128forlen(self.debug[index])
                index += 1
            elif onebyte == 6:
                off += unsignedleb128forlen(self.debug[index])
                index += 1
            elif onebyte == 9:
                off += unsignedleb128p1forlen(self.debug[index])
                index += 1
        self.len = off - self.start
        return off

class DexMapItem:
    Constant = {0: 'TYPE_HEADER_ITEM', 1: 'TYPE_STRING_ID_ITEM', 2: 'TYPE_TYPE_ID_ITEM',
                3: 'TYPE_PROTO_ID_ITEM', 4: 'TYPE_FIELD_ID_ITEM', 5: 'TYPE_METHOD_ID_ITEM',
                6: 'TYPE_CLASS_DEF_ITEM', 0x1000: 'TYPE_MAP_LIST', 0x1001: 'TYPE_TYPE_LIST',
                0x1002: 'TYPE_ANNOTATION_SET_REF_LIST', 0x1003: 'TYPE_ANNOTATION_SET_ITEM',
                0x2000: 'TYPE_CLASS_DATA_ITEM', 0x2001: 'TYPE_CODE_ITEM', 0x2002: 'TYPE_STRING_DATA_ITEM',
                0x2003: 'TYPE_DEBUG_INFO_ITEM', 0x2004: 'TYPE_ANNOTATION_ITEM', 0x2005: 'TYPE_ENCODED_ARRAY_ITEM',
                0x2006: 'TYPE_ANNOTATIONS_DIRECTORY_ITEM'}
    
    def __init__(self, file):
        self.type = struct.unpack("H", file.read(2))[0]
        self.unused = struct.unpack("H", file.read(2))[0]
        self.size = struct.unpack("I", file.read(4))[0]
        self.offset = struct.unpack("I", file.read(4))[0]
        self.item = []
        self.len = 0  # the length of the item

    def addstr(self, str):  # return index of the string, I put it on the last position simply
        if self.type == 0x2002:
            strdata = StringData(None, 2)   # new a empty class
            strdata.addstr(str)
            self.item.append(strdata)
            self.size += 1
            return strdata
        else:
            print("error in add string")
            return None

    def addstrID(self, strdata):
        if self.type == 1:
            stringid = DexStringID(None, 2)
            stringid.addstrID(strdata)
            self.item.append(stringid)
            self.size += 1
        else:
            print("error in add string id")

    def addtypeID(self, field):
        if self.type == 4:
            self.item.append(field)
            self.size += 1
        else:
            print("error in add type id")

    def addclassdata(self, classdata):
        if self.type == 0x2000:
            self.item.append(classdata)
            self.size += 1
        else:
            print("error in add class data")

    def addtypeid(self, index, str):
        if self.type == 2:
            type = DexTypeID(None, None, 2)
            type.addtype(index, str)
            self.item.append(type)
            self.size += 1
        else:
            print("error in add type id")

    def addmethodid(self, class_idx, proto_idx, name_idx):
        method = DexMethodId(None, None, None, None, 2)
        method.addmethod(class_idx, proto_idx, name_idx)
        print("add method id", proto_idx)
        self.item.append(method)
        self.size += 1

    def addclassdef(self, classdef):
        if self.type == 6:
            self.item.append(classdef)
            self.size += 1
        else:
            print("error in add class def")

    def addprotoid(self, short_idx, type_idx, paramref):
        if self.type == 3:
            proto = DexProtoId(None, None, None, 2)
            proto.addproto(short_idx, type_idx, paramref)
            self.item.append(proto)
            self.size += 1
        else:
            print("error in add proto id")

    def addtypelist(self, typeitem):
        if self.type == 0x1001:
            self.item.append(typeitem)
            self.size += 1
        else:
            print("error in add type list")

    def addcodeitem(self, codeitem):
        if self.type == 0x2001:
            self.item.append(codeitem)
            self.size += 1
        else:
            print("error in add code item")

    def adddebugitem(self, debugitem):
        if self.type == 0x2003:
            self.item.append(debugitem)
            self.size += 1
        else:
            print("error in add debug item")

    def copytofile(self, file):
        file.seek(self.offset, 0)
        if self.type <= 0x2006:
            align = file.tell() % 4
            if align != 0:
                for i in range(0, 4-align):
                    file.write(struct.pack("B", 0))
            print("copytofile:", DexMapItem.Constant[self.type], file.tell())
            for i in range(0, self.size):
                self.item[i].copytofile(file)
                # if self.type == 0x2002:
                #     print("for debug", i, getstr(self.item[i].str))
                
    def printf(self, index):
        print ("type: ", DexMapItem.Constant[self.type])
        print ("size: ", self.size)
        print ("offset: ", self.offset)
        if self.type == index:
            for i in range(0, self.size):
                self.item[i].printf()
            print ()

    def setitem(self, file, dexmapitem):
        file.seek(self.offset)
        for i in range(0, self.size):
            if self.type == 1:  # string
                file.seek(self.offset+i*4, 0)
                self.item.append(DexStringID(file))
            elif self.type == 2:
                file.seek(self.offset+i*4, 0)
                self.item.append(DexTypeID(file, dexmapitem[1].item))  # make sure has already build string table
            elif self.type == 3:
                file.seek(self.offset+i*12, 0)
                self.item.append(DexProtoId(file, dexmapitem[1].item, dexmapitem[2].item))
            elif self.type == 4:
                file.seek(self.offset+i*8, 0)
                self.item.append(DexFieldId(file, dexmapitem[1].item, dexmapitem[2].item))
            elif self.type == 5:
                file.seek(self.offset+i*8, 0)
                self.item.append(DexMethodId(file, dexmapitem[1].item, dexmapitem[2].item, dexmapitem[3].item))
            elif self.type == 6:
                file.seek(self.offset+i*32, 0)
                self.item.append(DexClassDef(file, dexmapitem[1].item, dexmapitem[2].item))
            elif self.type == 0x1001:   # TYPE_TYPE_LIST
                self.item.append(TypeItem(file, dexmapitem[2].item))
            elif self.type == 0x1002:   # TYPE_ANNOTATION_SET_REF_LIST
                self.item.append(AnnotationsetrefList(file))
            elif self.type == 0x1003:   # TYPE_ANNOTATION_SET_ITEM
                self.item.append(AnnotationsetItem(file))
            elif self.type == 0x2000:   # TYPE_CLASS_DATA_ITEM
                self.item.append(ClassdataItem(file))
            elif self.type == 0x2001:   # TYPE_CODE_ITEM
                self.item.append(CodeItem(file))
            elif self.type == 0x2002:   # TYPE_STRING_DATA_ITEM
                self.item.append(StringData(file))
            elif self.type == 0x2003:   # TYPE_DEBUG_INFO_ITEM
                self.item.append(DebugInfo(file))
            elif self.type == 0x2004:   # TYPE_ANNOTATION_ITEM
                self.item.append(AnnotationItem(file))
            elif self.type == 0x2005:   # TYPE_ENCODED_ARRAY_ITEM
                self.item.append(EncodedArrayItem(file))
            elif self.type == 0x2006:  # TYPE_ANNOTATIONS_DIRECTORY_ITEM
                self.item.append(AnnotationsDirItem(file))

    def makeoffset(self, off):
        if self.type < 0x2000 or self.type == 0x2001 or self.type == 0x2006:
            align = off % 4
            if align != 0:
                off += (4 - align)
        self.offset = off
        if self.type == 0:  # header
            self.len = 112
        elif self.type == 1:    # string id
            self.len = 4 * self.size
        elif self.type == 2:    # type id
            self.len = 4 * self.size
        elif self.type == 3:   # proto id
            self.len = 12 * self.size
        elif self.type == 4:    # field id
            self.len = 8 * self.size
        elif self.type == 5:    # method id
            self.len = 8 * self.size
        elif self.type == 6:    # class def
            self.len = 32 * self.size
        elif self.type == 0x1000:   # map list, resolve specially in dexmaplist class
            pass
        elif 0x1001 <= self.type <= 0x2006:   # type list, annotation ref set list, annotation set item...
            for i in range(0, self.size):
                off = self.item[i].makeoffset(off)
                # if self.type == 0x2002:
                #     print("for debug", i, off)
            self.len = off - self.offset
        if self.type == 0x2000:
            print("the off is:", off)
        if self.type <= 6:
            return off + self.len
        else:
            return off

    def getref(self, dexmaplist):
        for i in range(0, self.size):
            self.item[i].getreference(dexmaplist)

    def getreference(self, addr):
        if addr == 0:
            return None
        i = 0
        for i in range(0, self.size):
            if self.item[i].start == addr:
                return self.item[i]
        if i >= self.size:
            os._exit(addr)
        return None

    def getrefbystr(self, str):  # for modify the string data
        if self.type == 0x2002:
            for i in range(0, self.size):
                if getstr(self.item[i].str) == str:
                    return self.item[i]
        else:
            print("error occur here", self.type)
            return None

    def getindexbyname(self, str):  # search for type id item
        for i in range(0, self.size):
            if self.item[i].str == str:
                print("find index of", DexMapItem.Constant[self.type], str)
                return i
        print("did not find it in", DexMapItem.Constant[self.type])
        return -1

    def getindexbyproto(self, short_idx, return_type_idx, param_list, length):  # called by item, index of 3
        for i in range(0, self.size):
            if short_idx == self.item[i].shortyIdx and return_type_idx == self.item[i].returnTypeIdx:
                if self.item[i].ref is not None:
                    if self.item[i].ref.equal(param_list, length):
                        return i
        return -1

class DexMapList:
    Seq = (0, 1, 2, 3, 4, 5, 6, 0x1000, 0x1001, 0x1002, 0x1003, 0x2001, 0x2000, 0x2002,
           0x2003, 0x2004, 0x2005, 0x2006)

    def __init__(self, file, offset):
        file.seek(offset, 0)
        self.start = offset
        self.size = struct.unpack("I", file.read(4))[0]
        mapitem = []
        self.dexmapitem = {}
        for i in range(0, self.size):
            mapitem.append(DexMapItem(file))
        for i in range(0, self.size):
            mapitem[i].setitem(file, self.dexmapitem)
            self.dexmapitem[mapitem[i].type] = mapitem[i]

    def copy(self, file):
        for i in range(0, len(DexMapList.Seq)):
            index = DexMapList.Seq[i]
            if index in self.dexmapitem.keys():
                print(index, "start at:", file.tell())
                if index != 0x1000:
                    self.dexmapitem[index].copytofile(file)
                else:
                    self.copytofile(file)

    def copytofile(self, file):
        print("output map list", file.tell())
        file.seek(self.start, 0)
        file.write(struct.pack("I", self.size))
        for i in range(0, len(DexMapList.Seq)):
            index = DexMapList.Seq[i]
            if index in self.dexmapitem.keys():
                # print(self.dexmapitem[index].type)
                file.write(struct.pack("H", self.dexmapitem[index].type))
                file.write(struct.pack("H", self.dexmapitem[index].unused))
                file.write(struct.pack("I", self.dexmapitem[index].size))
                file.write(struct.pack("I", self.dexmapitem[index].offset))

    def makeoff(self):
        off = 0
        for i in range(0, len(DexMapList.Seq)):
            index = DexMapList.Seq[i]
            if index in self.dexmapitem.keys():
                align = off % 4
                if align != 0:
                    off += (4 - align)
                if index != 0x1000:
                    off = self.dexmapitem[index].makeoffset(off)
                else:
                    off = self.makeoffset(off)
        return off

    def makeoffset(self, off):
        self.start = off
        off += (4 + self.size * 12)
        self.dexmapitem[0x1000].offset = self.start
        return off

    def getreference(self):
        self.dexmapitem[1].getref(self.dexmapitem)
        self.dexmapitem[3].getref(self.dexmapitem)
        self.dexmapitem[6].getref(self.dexmapitem)
        if 0x1002 in self.dexmapitem.keys():
            self.dexmapitem[0x1002].getref(self.dexmapitem)
        if 0x1003 in self.dexmapitem.keys():
            self.dexmapitem[0x1003].getref(self.dexmapitem)
        self.dexmapitem[0x2000].getref(self.dexmapitem)
        self.dexmapitem[0x2001].getref(self.dexmapitem)
        if 0x2006 in self.dexmapitem.keys():
            self.dexmapitem[0x2006].getref(self.dexmapitem)

    def getrefbystr(self, str):
        return self.dexmapitem[0x2002].getrefbystr(str)

    def printf(self, index):
        print ("DexMapList:")
        print ("size: ", self.size)
        for i in self.dexmapitem:
            self.dexmapitem[i].printf(index)

# default: 0 create from file 1 create from memory        
class DexFile:
    def __init__(self, filename, mode=0):
        if mode == 0:
            file = open(filename, 'rb')
            self.dexheader = DexHeader(file)
            self.dexmaplist = DexMapList(file, self.dexheader.map_off)
            self.dexmaplist.dexmapitem[0].item.append(self.dexheader)
            self.dexmaplist.getreference()
            file.close()

    def copytofile(self, filename):
        if os.path.exists(filename):
            os.remove(filename)
        file = open(filename, 'wb+')
        file.seek(0, 0)
        self.makeoffset()
        self.dexmaplist.copy(file)
        rest = self.dexheader.file_size -file.tell()
        for i in range(0, rest):
            file.write(struct.pack("B", 0))
        file_sha = get_file_sha1(file)
        tmp = bytes(file_sha)
        i = 0
        file.seek(12)
        while i < 40:
            num = (ACSII[tmp[i]] << 4) + ACSII[tmp[i+1]]
            file.write(struct.pack("B", num))
            i += 2
        csum = checksum(file, self.dexheader.file_size)
        print("checksum:", hex(csum), "file size:", self.dexheader.file_size)
        file.seek(8)
        file.write(struct.pack("I", csum))
        file.close()

    def printf(self, index):
        if index == 0:
            self.dexheader.printf()
        else:
            self.dexmaplist.printf(index)

    def printclasscode(self, class_name, method_name):
        index = self.dexmaplist.dexmapitem[2].getindexbyname(class_name)
        if index < 0:
            print("did not find the class", class_name)
            return
        count = self.dexmaplist.dexmapitem[6].size
        classcoderef = None
        for i in range(0, count):
            if self.dexmaplist.dexmapitem[6].item[i].classIdx == index:
                print("the class def index is :", i)
                self.dexmaplist.dexmapitem[6].item[i].printf()
                classdataref = self.dexmaplist.dexmapitem[6].item[i].classDataRef
                flag = False
                if classdataref is not None:
                    for i in range(0, classdataref.direct_methods_size):
                        methodref = self.dexmaplist.dexmapitem[5].item[classdataref.direct_methods[i].method_idx]
                        print(methodref.name, classdataref.direct_methods[i].method_idx)
                        if methodref.name == method_name:
                            print("find the direct method:", methodref.classstr, methodref.name,
                                  classdataref.direct_methods[i].access_flags, classdataref.direct_methods[i].code_off)
                            classcoderef = classdataref.direct_methods[i].coderef
                            if classcoderef is not None:
                                classcoderef.printf()
                            else:
                                print("the code item is None")
                            flag = True
                            break
                    if flag:
                        break
                    print("did not find the direct method")
                    for j in range(0, classdataref.virtual_methods_size):
                        methodref = self.dexmaplist.dexmapitem[5].item[classdataref.virtual_methods[j].method_idx]
                        print(methodref.name)
                        if methodref.name == method_name:
                            print("find the virtual method:", methodref.classstr, methodref.name,
                                classdataref.virtual_methods[j].access_flags, classdataref.virtual_methods[j].code_off)
                            classcoderef = classdataref.virtual_methods[j].coderef
                            classcoderef.printf()
                            flag = True
                            break
                    if flag is False:
                        print("did not find the virtual method")
                # if flag:    # find the class data item, now get and print the code item
                #     classcoderef.printf()
                #     print("print done")
                # else:
                #     print("sonething wrong here")
                    # with open(method_name, "wb") as file:
                    #     classcoderef.copytofile(file)
                    #     file.close()
                break
        if classcoderef is not None:
            classcoderef.printf()

    def makeoffset(self):
        off = self.dexmaplist.makeoff()
        align = off % 4
        if align != 0:
            off += (4 - align)
        self.dexheader.makeoffset(self.dexmaplist.dexmapitem)
        self.dexheader.file_size = off
        self.dexheader.data_size = off - self.dexheader.map_off

    def modifystr(self, src, dst):
        strData = self.dexmaplist.getrefbystr(src)
        if strData is not None:
            print("find string", src)
            strData.modify(dst)

    def addstr(self, str):
        strdata = self.dexmaplist.dexmapitem[0x2002].addstr(str)
        strdata.printf()
        self.dexmaplist.dexmapitem[1].addstrID(strdata)
        return self.dexmaplist.dexmapitem[1].size-1  # return the index of the str

    def addtype(self, str):
        index = self.addstr(str)
        self.dexmaplist.dexmapitem[2].addtypeid(index, str)
        return self.dexmaplist.dexmapitem[2].size-1

    def addfield(self, classidx, type_str, name_str):
        field = DexFieldId(None, None, None, 2)
        str_idx = self.dexmaplist.dexmapitem[1].getindexbyname(name_str)
        if str_idx < 0:
            str_idx = self.addstr(name_str)
        if type_str in TypeDescriptor.keys():   # transform the type str to type descriptor
            type_str = TypeDescriptor[type_str]
        type_idx = self.dexmaplist.dexmapitem[2].getindexbyname(type_str)
        if type_idx < 0:
            print("did not find this type in type ids", type_str)
            type_idx = self.addtype(type_str)
        field.addfield(classidx, type_idx, str_idx)
        self.dexmaplist.dexmapitem[4].addtypeID(field)
        return self.dexmaplist.dexmapitem[4].size-1

    # classtype: Lcom/cc/test/Dexparse;
    def addclass(self, classtype, accessflag, superclass, sourcefile):
        item = DexClassDef(None, None, None, 2)
        strdata = self.dexmaplist.getrefbystr(classtype)
        if strdata is not None:
            print("This class is existing", classtype)
            return
        type_index = self.addtype(classtype)
        super_index = self.dexmaplist.dexmapitem[2].getindexbyname(superclass)
        if super_index < 0:  # did not find it
            print("This super class is not exiting", superclass)
            return
        source_index = self.dexmaplist.dexmapitem[1].getindexbyname(sourcefile)
        if source_index < 0:
            source_index = self.addstr(sourcefile)
        item.addclassdef(type_index, accessflag, super_index, source_index)
        self.dexmaplist.dexmapitem[6].addclassdef(item)
        return item

    def addclassData(self, classdataref):
        self.dexmaplist.dexmapitem[0x2000].addclassdata(classdataref)

    # add proto id and return the index,
    # if already exist just return the index
    def addproto(self, proto_list, return_str):
        size = len(proto_list)
        proto = ""
        if return_str in ShortyDescriptor.keys():
            proto += ShortyDescriptor[return_str]
        else:
            proto += "L"
        for i in range(0, size):
            str = proto_list[i]
            if str in ShortyDescriptor.keys():
                proto += ShortyDescriptor[str]
            else:
                proto += 'L'    # for reference of class or array
        short_idx = self.dexmaplist.dexmapitem[1].getindexbyname(proto)
        if short_idx < 0:
            print("did not find this string in string ids", proto)
            short_idx = self.addstr(proto)
        if return_str in TypeDescriptor.keys():     # transform to type descriptor
            return_str = TypeDescriptor[return_str]
        type_idx = self.dexmaplist.dexmapitem[2].getindexbyname(return_str)
        if type_idx < 0:
            print("did not find this type in type ids", return_str)
            type_idx = self.addtype(return_str)
        proto_idx = self.dexmaplist.dexmapitem[3].getindexbyproto(short_idx, type_idx, proto_list, size)
        if proto_idx >= 0:
            return proto_idx
        typeItem = TypeItem(None, None, 2)
        type_list = []
        str_list = []
        for i in range(0, size):
            type_str = proto_list[i]
            if type_str in TypeDescriptor.keys():
                type_str = TypeDescriptor[type_str]
            type_index = self.dexmaplist.dexmapitem[2].getindexbyname(type_str)
            if type_index < 0:
                print("did not find this param in type ids", type_str)
                type_index = self.addtype(type_str)
            type_list.append(type_index)
            str_list.append(type_str)
        typeItem.addtypeItem(type_list, str_list)
        self.dexmaplist.dexmapitem[0x1001].addtypelist(typeItem)
        self.dexmaplist.dexmapitem[3].addprotoid(short_idx, type_idx, typeItem)
        return self.dexmaplist.dexmapitem[3].size-1

    def addmethod(self, class_idx, proto_list, return_str, name):
        name_idx = self.dexmaplist.dexmapitem[1].getindexbyname(name)
        if name_idx < 0:
            name_idx = self.addstr(name)
        self.dexmaplist.dexmapitem[5].addmethodid(class_idx, self.addproto(proto_list, return_str), name_idx)
        return self.dexmaplist.dexmapitem[5].size-1

    def addcode(self, ref):
        self.dexmaplist.dexmapitem[0x2001].addcodeitem(ref)

    def adddebug(self, debugitem):
        self.dexmaplist.dexmapitem[0x2003].adddebugitem(debugitem)

    def getmethodItem(self, class_name, method_name):
        index = self.dexmaplist.dexmapitem[2].getindexbyname(class_name)
        if index < 0:
            print("did not find the class", class_name)
            return
        else:
            print("find the class, index is :", index)
        count = self.dexmaplist.dexmapitem[6].size
        encoded_method = None
        method_idx = 0
        def_idx = 0
        for i in range(0, count):
            if self.dexmaplist.dexmapitem[6].item[i].classIdx == index:
                def_idx = i
                self.dexmaplist.dexmapitem[6].item[i].printf()
                classdataref = self.dexmaplist.dexmapitem[6].item[i].classDataRef
                flag = False
                if classdataref is not None:
                    for i in range(0, classdataref.direct_methods_size):
                        methodref = self.dexmaplist.dexmapitem[5].item[classdataref.direct_methods[i].method_idx]
                        print(methodref.name, classdataref.direct_methods[i].method_idx)
                        if methodref.name == method_name:
                            print("find the direct method:", methodref.classstr, methodref.name,
                                  classdataref.direct_methods[i].access_flags, classdataref.direct_methods[i].code_off)
                            encoded_method = classdataref.direct_methods[i]
                            method_idx = classdataref.direct_methods[i].method_idx
                            flag = True
                            break
                    if flag:
                        break
                    print("did not find the direct method")
                    for j in range(0, classdataref.virtual_methods_size):
                        methodref = self.dexmaplist.dexmapitem[5].item[classdataref.virtual_methods[j].method_idx]
                        print(methodref.name)
                        if methodref.name == method_name:
                            print("find the virtual method:", methodref.classstr, methodref.name,
                                classdataref.virtual_methods[j].access_flags, classdataref.virtual_methods[j].code_off)
                            encoded_method = classdataref.virtual_methods[j]
                            method_idx = classdataref.virtual_methods[j].method_idx
                            flag = True
                            break
                    if flag is False:
                        print("did not find the virtual method")
                break
        return {"method": encoded_method, "classidx": index, "methodidx": method_idx, "defidx": def_idx}

    def verifyclass(self, def_idx):
        classdef = self.dexmaplist.dexmapitem[6].item[def_idx]
        classdef.accessFlags |= 0x00010000

    def gettypeid(self, type):
        return self.dexmaplist.dexmapitem[2].getindexbyname(type)

def jiaguAll(dexfile, outfile):
    method_list = []    # record all method need to protect
    tmp_method = dexfile.getmethodItem("Lcom/cc/test/MainActivity;", "onCreate")
    method_list.append({"access": tmp_method["method"].access_flags, "ref": tmp_method["method"].coderef,
                        "classidx": tmp_method["classidx"], "methodidx": tmp_method["methodidx"]})
    tmp_method["method"].access_flags = int(Access_Flag['native'] | Access_Flag['public'])
    tmp_method["method"].modified = 1
    # change the access flag, make it native
    dexfile.makeoffset()    # make offset
    if os.path.exists(outfile):  # if exists, delete it
        print("the file is exist, just replace it")
        os.remove(outfile)
    file = open(outfile, 'wb+')
    file.seek(0, 0)
    size = len(method_list)
    filesize = dexfile.dexheader.file_size  # in order to adjust the dex file
    dexfile.dexheader.file_size += 16 * size     # each injected data need 16 bytes
    dexfile.dexmaplist.copy(file)
    file.seek(filesize, 0)
    print("file size :", filesize, " size : ", size)
    for i in range(0, size):
        file.write(struct.pack("I", method_list[i]["classidx"]))
        file.write(struct.pack("I", method_list[i]["methodidx"]))
        file.write(struct.pack("I", method_list[i]["access"]))
        file.write(struct.pack("I", method_list[i]["ref"].start))
        print("inject data :", method_list[i]["classidx"], method_list[i]["methodidx"])
        # assume that the code ref is not None, otherwise it make no sense(no need to protect)
    file_sha = get_file_sha1(file)
    tmp = bytes(file_sha)
    i = 0
    file.seek(12)
    while i < 40:
        num = (ACSII[tmp[i]] << 4) + ACSII[tmp[i+1]]
        file.write(struct.pack("B", num))
        i += 2
    csum = checksum(file, dexfile.dexheader.file_size)
    print("checksum:", hex(csum), "file size:", dexfile.dexheader.file_size)
    file.seek(8)
    file.write(struct.pack("I", csum))
    file.close()

if __name__ == '__main__':
    dexfile = DexFile("classes.dex")
    # jiaguAll(dexfile, "classescp.dex")
    # dexfile.printclasscode("Lcom/cc/test/MainActivity;", "onCreate")
    # dexfile.printf(3)
    # dexfile.addstr("DexParse.java")
    # dexfile.addstr("Lcom/cc/test/DexParse.java")
    # dexfile.modifystr("A Text From CwT", "A Text From DexParse")
    # dexfile.printf()
    # note: you need to delete file classescp.dex first, otherwise
    # new dex file will append the old one
    # dexfile.copytofile("classescp.dex")

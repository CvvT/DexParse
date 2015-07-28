# !/usr/bin/env python
# -*- coding: utf_8 -*-
# Date: 2014/11/26
#
import hashlib
import struct
import os
import base64

ACSII = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 0,
         'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}

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

def get_file_sha1(f):
    f.read(32)  # skip magic, checksum, sha
    sha = hashlib.sha1()
    while True:
        data = f.read(1024)
        if not data:
            break
        sha.update(data)
    return sha.hexdigest()

class Instruction:
    def __init__(self):
        self.insns = []
        self.str = ""
        self.dst = 0
        self.src = 0

    def init(self):
        func(self)

    def printf(self):
        print(self.str, self.dst, self.src)

# with open("classes.dex", "rb") as f:
#     file_sha = get_file_sha1(f)
#     print(file_sha)
#     tmp = bytes(file_sha)
#     i = 0
#     while i < 40:
#         num = (ACSII[tmp[i]] << 4) + ACSII[tmp[i+1]]
#         print(hex(num))
#         i += 2

def func(ins):
    ins.str = "hello"
    ins.dst = "12"
    ins.src = "1"

def checksum(f, len):
    a = 1
    b = 0
    f.seek(12)
    for i in range(12, len):
        onebyte = struct.unpack("B", f.read(1))[0]
        a = (a + onebyte) % 65521
        b = (b + a) % 65521
    return b << 16 | a

with open("classescp.dex", "rb") as file:
    print(hex(checksum(file, 1509064)))

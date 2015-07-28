#! /usr/bin/python
#coding=utf-8
import os
import struct

file1 = "classes.dex"
file2 = "classescp.dex"
f1 = open(file1, 'rb')
f2 = open(file2, 'rb')
# f1.seek(709456)
end = 580208
start = 580208
# f2.seek(start)

len1 = os.path.getsize(file1)
len2 = os.path.getsize(file2)
if len1 < len2:
    len = len1
else:
    len = len2

f2.seek(872304)
f1.seek(1063648)
len = 1100440 - 1063648
for i in range(0, len):
    c1 = f1.read(1)
    c2 = f2.read(1)
    if c1 != c2:
        print("diff at addr", hex(i))
        print("diff at addr", i)  # 877537
        os._exit()
        
print("Succeed")
f1.close()
f2.close()
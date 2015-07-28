__author__ = 'CwT'
from DexParse import *

def addJunkopcode(dexfile, class_name, method_name):
    tmp_method = dexfile.getmethodItem(class_name, method_name)
    coderef = tmp_method["method"].coderef
    coderef.insns.insert(0, 0)
    coderef.insns.insert(0, 0x7171)
    coderef.insns.insert(0, 4)
    coderef.insns.insert(0, 0x3c)
    coderef.insns.insert(0, 0x5012)
    coderef.insns_size += 5

def modifyopcode(dexfile, class_name, method_name):
    tmp_method = dexfile.getmethodItem(class_name, method_name)
    coderef = tmp_method["method"].coderef
    coderef.insns[4] = 0x3a

if __name__ == '__main__':
    dexfile = DexFile("classes.dex")
    modifyopcode(dexfile, "Lcom/baidu/protect/StubApplication;", "<clinit>")
    dexfile.copytofile("classescp.dex")

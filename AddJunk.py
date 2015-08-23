__author__ = 'CwT'
from DexParse import *

array = [0x32, 0xa,     # if-eq v0, v0, 8
         0x26, 0x3, 0x0,    # fill-array-data v0, 3
         0x0300, 0x2, 0x1, 0x0, 0x0  # fill-array-data-payload 0x0300, width, size, data[]
         ]

array2 = [0x32, 0xd,  # if-eq v0, v0, 8
          0x1023, 0x06d7,  # new-array v0, v1, typeid
          0x26, 0x3, 0x0,  # fill-array-data v0, 3
          0x0300, 0x1, 0x2, 0x0, 0x0,  # fill-array-data-payload 0x0300, width, size, data[]
          ]

def addJunkopcode(dexfile, class_name, method_name):
    tmp_method = dexfile.getmethodItem(class_name, method_name)
    coderef = tmp_method["method"].coderef
    dexfile.verifyclass(tmp_method["defidx"])
    index = dexfile.gettypeid("[B")
    if index < 0:
        index = dexfile.gettypeid("[C")
        if index < 0:
            pass
    print("find index: ", index)
    for i in range(0, len(array2)):
        coderef.insns.insert(i, array2[i])
    num = coderef.insns_size * 2  # byte number
    coderef.insns[3] = index
    coderef.insns[9] = num & 0xffff
    coderef.insns[10] = (num >> 16) & 0xffff
    coderef.insns_size += 12

def modifyopcode(dexfile, class_name, method_name):
    tmp_method = dexfile.getmethodItem(class_name, method_name)
    coderef = tmp_method["method"].coderef
    coderef.insns[4] = 0x3a

if __name__ == '__main__':
    dexfile = DexFile("classes.dex")
    # modifyopcode(dexfile, "Lcom/cc/test/MainActivity;", "onCreate")
    addJunkopcode(dexfile, "Lcom/cc/test/MainActivity;", "onCreateOptionsMenu")
    dexfile.copytofile("classescp.dex")

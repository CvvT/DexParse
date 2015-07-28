__author__ = 'CwT'

from DexParse import *

if __name__ == '__main__':
    dexfile = DexFile("classes.dex")
    # @Params: classname, acces_flag(public, private...), parent_class_name, Filename
    classitem = dexfile.addclass("Lcom/cc/test/DexParse;", Access_Flag["public"],
    "Ljava/lang/Object;", "DexParse.java")
    classdata = ClassdataItem(None, 2)
    dexfile.addclassData(classdata)
    classdata.addstaticfield(dexfile.addfield(classitem.classIdx, "int", "IntFromCwt"),
                             Access_Flag['public'] | Access_Flag["static"])
    classdata.addinstancefield(dexfile.addfield(classitem.classIdx, "boolean", "BoolFromCwt"),
                               Access_Flag["private"])
    param_list = []
    # param_list.append("[Lcom/lang/String;")
    # param_list.append("boolean")    # prepare for parameter list
    code = CodeItem(None, 2)
    # @param register_size, in_size, out_size, tries_size, debug_off,
    # insns_size, insns_list, debugref, tries_list, handler
    insns = []
    tries = []
    insns.append(0xe)  # return void
    debug = DebugInfo(None, 2)
    names_list = []
    debug_list = [0]
    debug.adddebugitem(0, 0, names_list, debug_list)
    dexfile.adddebug(debug)
    code.addcode(1, 1, 0, 0, 0, len(insns), insns, debug, tries, None)
    dexfile.addcode(code)
    method_idx = dexfile.addmethod(classitem.classIdx, param_list, "void", "main")
    classdata.adddirectmethod(method_idx, Access_Flag['public'] | Access_Flag['static'], code)
    classdata.commit()
    classitem.addclassdefref(None, None, classdata, None)

    tmp_method = dexfile.getmethodItem("Lcom/cc/test/MainActivity;", "onCreate")
    coderef = tmp_method['method'].coderef
    coderef.insns.insert(0, 0)
    coderef.insns.insert(0, method_idx)
    coderef.insns.insert(0, 0x71)
    coderef.insns_size += 3
    dexfile.copytofile("classescp.dex")

# DexParse
Parse and tamper DEX<br>
  1. Add/modify instructions/strings/fields/methods/classes
  2. disassemble to smali

update 2015.10.30<br>
最近在阅读dexlib2的源码，才发现大牛写的代码质量就是高，相比之下自己的代码凌乱难以扩展，于是我决定弃坑了，这个项目不再继续研究了，打算开个新坑，基于dexlib2的dex tamper tool，目前支持两个dex文件合并（目的是为了植入代码），当然目前只能合并，如何调用仍需研究，希望能够实现的功能包括：<br>
1.代码混淆（类名替换、字符串加密、流程替换、花指令）<br>
2.植入代码<br>

DexParse：<br>
根据Android官方文档定义解析Dex格式文件，目前支持：<br>
1.修改字符串，添加字符串<br>
2.插入类，包括成员变量和方法<br>
3.输入指定方法名，输出smali代码（bytecode to smali，只是简单一对一翻译没有进行跳转、sting id、type id解析等处理）<br>
4.修改类方法<br>
5.修改后可生成新的dex文件<br>
<br>
AddClass：<br>
展示如何通过已定义的接口增加一个类、方法（这里有个问题：我将字符串都插入到string list的末尾导致没有按照字典序排序，不符合Dex格式规范，但是如果排序又需要对所有string index进行修改，这里虽然可以插入一个类，然并卵，正在考虑不添加字符串，利用已有的字符串添加一个类不知道是否可行？）

AddJunk：
展示如何给一个方法添加指令，＊＊＊＊本意是打算添加垃圾代码使反编译工具实效，果然也是然并卵，这种bug早就被修复了＊＊＊＊＊
8月23日更新：最近发现了Dalvik中fill-array-data-payload这种伪指令，尝试使用这条指令加入垃圾指令，经测试可以使得baksmali，dex2jar无法正常工作。但是在修改过程中遇到的一个问题就是会抛出verifyError，经过一番搜索可以通过修改access_flag讲类修改成已验证，但是我不太明白为什么会抛出异常,以及修改access_flag的原因，希望有大侠能够指点！


Instruction：
翻译所需的bytecode指令

注：由于代码比较混乱可能难以理解
Tks！^_^


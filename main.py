import subprocess
import argparse

DEFAULT_INCLUDES = ["malloc.h","memory.h","stdint.h"]

AVAILABLE_MACROS = {
  "vec":    {"type": "vec"  , "file": "vector_macro.h" ,"define_macros": ["VECTOR_STRUCT_DEF","VECTOR_FUNCTION_DEF"] ,"includes": DEFAULT_INCLUDES},
  "array":  {"type": "array", "file": "array_macro.h"  ,"define_macros": ["ARRAY_STRUCT_DEF","ARRAY_FUNCTION_DEF"]   ,"includes": DEFAULT_INCLUDES},
}

def macro_expan(struct, T, T_include):
    includes = []
    if AVAILABLE_MACROS[struct]["includes"] is not None: 
        includes.extend(AVAILABLE_MACROS[struct]["includes"])
    if T_include is not None:
        includes.extend(T_include)
    
    T = T.replace(' ', '_')
    macro = open(AVAILABLE_MACROS[struct]["file"],'r',encoding='utf-8').read()

    define_struct_macro = AVAILABLE_MACROS[struct]["define_macros"][0] + "(" + T + ")"
    define_funcs_macro  = AVAILABLE_MACROS[struct]["define_macros"][1] + "(" + T + ")"

    #feed that to cpp
    pre_expanded_text = macro + '\n' + define_struct_macro + '\n' + define_funcs_macro

    cpp_procced_text = subprocess.run(['cpp', '-E', '-P', '-pipe'], input=bytes(pre_expanded_text, 'utf-8'), stdout=subprocess.PIPE)
    format_procced_text = subprocess.run(['clang-format','--style=LLVM'], input=cpp_procced_text.stdout, stdout=subprocess.PIPE)

    comment = "/*" + struct + " " + T + "*/\n"
    expanded_text = comment + format_procced_text.stdout.decode('utf-8')

    return {"text": expanded_text, "headers": includes}


parser = argparse.ArgumentParser(description="expander")
parser.add_argument("-Output",help="Output file")
parser.add_argument("-Struct",help="Struct you want to generate")
parser.add_argument("-Type",help="Type of the struct you want to generate the stuct for")
args = parser.parse_args()


output = []
output.append(macro_expan("vec", "int", None))
output.append(macro_expan("vec", "float", None))
output.append(macro_expan("vec", "VkBuffer", ["vulkan/vulkan.h",]))
output_headers = []
for o in output:
    output_headers.extend(o["headers"])
output_headers = list(set(output_headers))



output_text = "#pragma once\n\n"
output_text += "\n".join( "#include" + " \"" + x + "\""  for x in output_headers) + "\n\n"
output_text += "\n".join(x["text"] for x in output) + "\n"



if args.Output is None:
    print(output_text)
else:
    open(args.Output,'w',encoding="utf-8").write(output_text)

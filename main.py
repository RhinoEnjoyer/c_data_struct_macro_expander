#Prime pasta

import subprocess
import argparse
import os
import re
class Template_Class:
    name :str
    prototype_file :str
    prototype_text :str
    define_macro :str
    extra_macros :list
    dependencies :list
    templates :list

    def __init__(self, name, prototype_filepath, define_macro):
        self.name = name
        self.prototype_file = prototype_filepath
        self.prototype_text = open(prototype_filepath,'r',encoding='utf-8').read()
        self.define_macro = define_macro
        self.dependencies = []
        self.templates = []

        INCLUDE_REGEX = r"\/\/#include\s+(?:<|\")(\w+.h)(?:>|\")\n"
        matches = re.finditer(INCLUDE_REGEX, self.prototype_text,re.MULTILINE)
        for m in matches:
            self.dependencies.append(m.group(1))

        EXTRA_DEFINE_REGEX = r"\/\/(#define\s+.*)"
        matches = re.finditer(EXTRA_DEFINE_REGEX, self.prototype_text,re.MULTILINE)
        self.extra_macros = []
        for m in matches:
            self.extra_macros.append(m.group(1))

    def __str__(self):
        return f"Template_Class(name='{self.name}', prototype_file='{self.prototype_file}', define_macro={self.define_macro}, dependencies={self.dependencies})"

class Template_Entry:
    struct :str
    type_t :str
    dependencies :list

    def __init__(self,struct,type_t,dependencies):
        self.struct = struct
        self.type_t = type_t
        self.dependencies = dependencies

def setup_argument_parser():
    parser = argparse.ArgumentParser(description="expander")
    parser.add_argument("-Output",help="Output directory")
    parser.add_argument("-Struct",help="Struct you want to generate")
    parser.add_argument("-Type",help="Type of the struct you want to generate the stuct for")
    return parser.parse_args()

def template_class_dict_from_list(template_list,template_entries):
    dictionary = {template.name: template for template in template_list}
    
    for te in template_entries:
        dictionary[te.struct].templates.append(te)

    return dictionary 

def macro_expan(template_dict,struct, T, T_include):
    includes = []
    if template_dict[struct].dependencies is not None: 
        includes.extend(template_dict[struct].dependencies)
    if T_include is not None:
        includes.extend(T_include)

    T = T.replace(' ', '_')
    macro = template_dict[struct].prototype_text

    define_macro = template_dict[struct].define_macro + "(" + T + ")"

    #feed that to cpp
    pre_expanded_text = macro + '\n' + define_macro + '\n'

    cpp_procced_text = subprocess.run(['cpp', '-E', '-P', '-pipe'], input=bytes(pre_expanded_text, 'utf-8'), stdout=subprocess.PIPE)
    format_procced_text = subprocess.run(['clang-format','--style=LLVM'], input=cpp_procced_text.stdout, stdout=subprocess.PIPE)

    comment = "/*" + struct + " " + T + "*/\n"
    expanded_text = comment + format_procced_text.stdout.decode('utf-8')

    return {"text": expanded_text, "headers": includes}

def expand_macros(template_dict):
    out = {}
    # out = []
    for td in template_dict:
        out[td] = []
        for t in template_dict[td].templates:
            # out.append(macro_expan(template_dict,t.struct, t.type_t, t.dependencies)) 
            out[td].append(macro_expan(template_dict,t.struct, t.type_t, t.dependencies)) 
    return out

def get_unique_headers(out):
    out_headers = []
    for o in out:
        out_headers.extend(o["headers"])
    return list(set(out_headers))

def get_final_text(pragma, out_structs, out_headers, out_extra_macros):
    text = ""
    if pragma is True: 
        text += "#pragma once\n\n"
    
    text += '\n'.join( "#include" + " \"" + x + "\""  for x in out_headers) + '\n\n'
    text += '\n'.join(out_extra_macros) + '\n\n'
    text += '\n'.join(x["text"] + "\n\n\n\n" for x in out_structs) + '\n'
    return text



#TODO: read a project's files and determine based on that what needs to be generated


args = setup_argument_parser()
print("Current directory: " + os.getcwd())
out_dir = ""
if args.Output is not None and os.path.isdir(args.Output) is True:
    out_dir = args.Output
    print("Output directory: " + out_dir)


template_list = []
template_list.append(Template_Entry("vec", "str", ["../types.h"]))
template_list.append(Template_Entry("vec", "uint32_t", ["stdint.h",]))
template_list.append(Template_Entry("vec", "VkDeviceQueueCreateInfo", ["vulkan/vulkan.h",]))
template_list.append(Template_Entry("vec", "VkSurfaceFormatKHR", ["vulkan/vulkan.h",]))
template_list.append(Template_Entry("vec", "VkSubpassDependency", ["vulkan/vulkan.h",]))
template_list.append(Template_Entry("vec", "VkAttachmentDescription", ["vulkan/vulkan.h",]))

template_list.append(Template_Entry("array", "VkImage", ["vulkan/vulkan.h",]))
template_list.append(Template_Entry("array", "VkImageView", ["vulkan/vulkan.h",]))
template_list.append(Template_Entry("array", "VkSurfaceFormatKHR", ["vulkan/vulkan.h",]))
template_list.append(Template_Entry("array", "VkPresentModeKHR", ["vulkan/vulkan.h",]))

available_template_list = [
  Template_Class("vec","./vector_macro.h","VECTOR_DEFINE"),
  Template_Class("array","./array_macro.h","ARRAY_DEFINE"),
]
available_template_dict = template_class_dict_from_list(available_template_list,template_list)


output_structs = expand_macros(available_template_dict)
for o_struct in output_structs:
    out_header_file_name = out_dir + o_struct + "_containers.h"
    output_headers = get_unique_headers(output_structs[o_struct])
    output_text = get_final_text(True,output_structs[o_struct], output_headers, available_template_dict[o_struct].extra_macros) + '\n'
    open(out_header_file_name,'w',encoding="utf-8").write(output_text)

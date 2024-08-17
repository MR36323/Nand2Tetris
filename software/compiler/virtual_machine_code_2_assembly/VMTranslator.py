from VmParser import Parser
from CodeWriter import Writer
import sys
import os

def main():
    # Check if 1th command line argument is file or directory name 
    name = sys.argv[1]
    if os.path.isdir(name):
        # Hack code name is <directoryname.asm>
        hack_code_name = f"{name}/{name.split('/')[-1]}.asm"            
        # Create list of vm_code filenames
        vm_code_filenames = [f"{name}/{file}" for file in os.listdir(name) if file.endswith(".vm")]
    elif os.path.isfile(name):    
        # Hack code name is  <filename.asm>
        hack_code_name = f"{name.replace('.vm', '.asm')}"
        # Create list of vm_code filenames
        vm_code_filenames = [name]

    # Create writer object that generates hack file 
    hack_code = Writer(hack_code_name) 
    # Write booting code
    if os.path.isdir(name):
        hack_code.writeInit()

    # Translate each vm file into hack code
    for file in vm_code_filenames:
        # Create parser object of current vm_code
        vm_code = Parser(file)
        # Set file name to current file name
        hack_code.setFileName(file.split("/")[-1].replace(".vm", ""))
        # Feed each line of vm_code into hack_code
        while True:
            # Initialize variables of current line and args
            line_type = vm_code.commandType()
            arg1 = vm_code.arg1()
            arg2 = vm_code.arg2()
            # Feed correct variables into hack_code
            if line_type == "C_ARITHMETIC":
                hack_code.writeArithmetic(arg1)
            elif line_type == "C_PUSH":
                line_type = line_type.lower().replace("c_", "")
                hack_code.writePushPop(line_type, arg1, arg2)
            elif line_type == "C_POP":
                line_type = line_type.lower().replace("c_", "")
                hack_code.writePushPop(line_type, arg1, arg2)
            elif line_type == "C_LABEL":
                hack_code.writeLabel(arg1)
            elif line_type == "C_GOTO":
                hack_code.writeGoto(arg1)
            elif line_type == "C_IF":
                hack_code.writeIf(arg1)
            elif line_type == "C_FUNCTION":
                hack_code.writeFunction(arg1, arg2)
            elif line_type == "C_CALL":
                if not arg2:
                    arg2 = 0
                hack_code.writeCall(arg1, arg2)
            elif line_type == "C_RETURN":
                hack_code.writeReturn()
            # Stop feeding when no more vm_code lines 
            if not vm_code.hasMoreCommands:
                break
            vm_code.advance()
    
    # Close hack file
    hack_code.close()

if __name__ == "__main__":
    main()
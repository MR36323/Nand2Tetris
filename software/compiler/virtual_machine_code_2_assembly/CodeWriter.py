class Writer():
    def __init__(self, asm_name):
        self.asm_file = open(asm_name, "a")
        self.current_vm_file = ""
        self.cmplx_cmnd_count = 0
        self.return_count = 0

    # Name of current VM file
    def setFileName(self, file_name):
        self.current_vm_file = file_name   

    # Writes booting code
    def writeInit(self):
        # Setup stack pointer and call Sys.init          
        self.asm_file.write(f"//Booting code\n")
        sp = f"@256\nD=A\n@SP\nM=D\n"  
        self.asm_file.write(f"{sp}")
        self.writeCall("Sys.init", 0)

    # Writes arithmetic commands    
    def writeArithmetic(self, command):
      
        # Two-place, one-place, and complex ALU commands
        ALU_cmnds_2_plce = {'add': '+', 
                           'sub': '-', 
                           'and': '&', 
                           'or': '|'
                        }
        ALU_cmnds_1_plce = {'neg': '-', 
                           'not': '!'
                        }
        ALU_cmnds_cmplx = {'eq': 'EQ', 
                        'gt': 'GT', 
                        'lt': 'LT',
                        }   
        
        # Hack code for popping from stack to R13 or R14
        popR13 = f"@SP\nM=M-1\n@SP\nA=M\nD=M\n@R13\nM=D\n"
        popR14 = f"@SP\nM=M-1\n@SP\nA=M\nD=M\n@R14\nM=D\n"
        # Hack code for pushing value of D-register onto stack
        pushD = f"@SP\nA=M\nM=D\n@SP\nM=M+1\n"        
        
        # More specific Hack code
        hack_code = ""
        if command in ALU_cmnds_2_plce:
            # Code for setting D-register to R13 <command> R14
            command = ALU_cmnds_2_plce[command]
            command_op = f"@R13\nD=M\n@R14\nD=M{command}D\n"
            hack_code = popR13 + popR14 + command_op + pushD
        
        elif command in ALU_cmnds_1_plce:
            # Code for setting D-register to <command> R13
            command = ALU_cmnds_1_plce[command]
            command_op = f"@R13\nD={command}M\n"
            hack_code = popR13 + command_op + pushD
        
        elif command in ALU_cmnds_cmplx:
            # Code for: 
            # (i) Setting D-register to R13 minus R14 
            # (ii) If ARG1 is =, <, or > ARG2, then value of D-register is =, <, or > 0
            # (iii) If D-register is =, <, or > 0, D=-1, else D=0
            command = ALU_cmnds_cmplx[command]
            minus = f"@R13\nD=M\n@R14\nD=M-D\n"
            command_op = f"@{command}{self.cmplx_cmnd_count}\nD;J{command}\nD=0\n@cmplx_END{self.cmplx_cmnd_count}\n0;JMP\n({command}{self.cmplx_cmnd_count})\nD=-1\n(cmplx_END{self.cmplx_cmnd_count})\n"
            hack_code = popR13 + popR14 + minus + command_op + pushD
            self.cmplx_cmnd_count += 1
        
        # Write to file with comment
        self.asm_file.write(f"//{command}\n")
        self.asm_file.write(f"{hack_code}") 

    # Writes Hack code that tells the machine to push something from memory segment[index] 
    # onto stack, or to pop something from the stack onto memory segment[index], to self.file 
    def writePushPop(self, command, segment, index): 
        # Segment pointers correspond to RAM[1] - RAM[4], which store other RAM addresses
        segment_pointers = {'local': 'LCL',
                            'argument': 'ARG',
                            'this': 'THIS',
                            'that': 'THAT'
        }
        if segment in segment_pointers:
            segment = segment_pointers[segment]
            # <push segment i> means pushing RAM[segment_pointer + i] onto stack
            if command == 'push':
                hack_code = f"@{index}\nD=A\n@{segment}\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            # <pop segment i> means poping value from stack onto RAM[segment_pointer + i]
            elif command == 'pop':
                hack_code = f"@{index}\nD=A\n@{segment}\nM=M+D\n@SP\nM=M-1\n@SP\nA=M\nD=M\n@{segment}\nA=M\nM=D\n@{index}\nD=A\n@{segment}\nM=M-D\n" 
        
        # Temp variables are stored in RAM[5] - RAM[12]
        elif segment == "temp":
            # <push segment i> means pushing RAM[5 + i] onto stack
            if command == 'push':
                hack_code = f"@{int(index)+5}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            # <pop segment i> means poping value from stack onto RAM[5 + i]
            elif command == 'pop':
                hack_code = f"@SP\nM=M-1\n@SP\nA=M\nD=M\n@{int(index)+5}\nM=D\n"
        
        elif segment == "constant":
            # <push constant i> means pushing i onto stack
            if command == 'push':
                hack_code = f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" 
       
        # Statick variables are stored in RAM[16] - RAM[255]. The hack assembler turns every
        # non-label alphanumeric value into an int, starting from 16. 
        # So, n == assembled(<file_name.index>)
        elif segment == "static":
            name = f"{self.current_vm_file.split('/')[-1].lstrip('.vm')}.{index}"
            if command == 'push':
                # <push static i> means pushing RAM[n] onto stack
                hack_code = f"@{name}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            elif command == 'pop':
                # <pop static i> means poping value from stack into RAM[n]
                hack_code = f"@SP\nM=M-1\n@SP\nA=M\nD=M\n@{name}\nM=D\n"
        
        elif segment == "pointer":
            # <push pointer 0/1> means pushing RAM[3/4] (i.e. base address of THIS/THAT segment) onto stack
            if command == 'push':
                hack_code = f"@{int(index)+3}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            # <pop pointer 0/1> means pop a value onto off stack, onto RAM[3/4] (i.e. changing base address of THIS/THAT segment)
            elif command == 'pop':
                hack_code = f"@SP\nM=M-1\n@SP\nA=M\nD=M\n@{int(index)+3}\nM=D\n"
        
        self.asm_file.write(f"//{command} {segment} {index}\n")
        self.asm_file.write(f"{hack_code}")

    # Writes label command
    def writeLabel(self, label):
        label = f"{self.current_vm_file}${label}".upper()
        self.asm_file.write(f"//Label\n") # comment
        self.asm_file.write(f"({label})\n")

    # Writes goto command
    def writeGoto(self, label):
        label = f"{self.current_vm_file}${label}".upper()
        self.asm_file.write(f"//Goto\n")  # comment
        self.asm_file.write(f"@{label}\n0;JMP\n")

    # Writes if command
    def writeIf(self, label):
        label = f"{self.current_vm_file}${label}".upper()
        self.asm_file.write(f"//If-goto\n")  # comment
        self.asm_file.write(f"@SP\nM=M-1\n@SP\nA=M\nD=M\n@{label}\nD;JNE\n")
     
    #Writes call command
    def writeCall(self, function, args):
        # Push caller's frame onto stack - 
        # Save caller's return address
        return_address = f"rtrn_{self.return_count}"
        self.return_count += 1
        rtrn_adrss = f"@{return_address}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        # Save caller's LCL
        cllr_LCL = f"@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        # Save caller's ARG
        cllr_ARG = f"@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        # Save caller's THIS
        cllr_THIS = f"@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        # Save caller's THAT
        cllr_THAT = f"@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        
        # Set up callee - 
        # Reposition ARG
        cllee_ARG = f"@SP\nD=M\n@5\nD=D-A\n@{args}\nD=D-A\n@ARG\nM=D\n"
        # Reposition LCL
        cllee_LCL = f"@SP\nD=M\n@LCL\nM=D\n"
        # Transfer control to callee
        goto_function = f"@{function}\n0;JMP\n"
        # Callees return here 
        rtrn_here = f"({return_address})\n"
        
        # Write to hack file
        hack_code_1 = f"{rtrn_adrss}{cllr_LCL}{cllr_ARG}{cllr_THIS}{cllr_THAT}"
        hack_code_2 = f"{cllee_ARG}{cllee_LCL}{goto_function}{rtrn_here}"
        self.asm_file.write(f"//Call\n")  # comment
        self.asm_file.write(f"{hack_code_1}{hack_code_2}")

    # Writes function command
    def writeFunction(self, function, local_vars):
        # Write to hack file
        self.asm_file.write(f"//Function\n")  # comment
        self.asm_file.write(f"({function})\n")  # function label
        # Push local_vars zeros onto stack
        push_0 = f"@SP\nA=M\nM=0\n@SP\nM=M+1\n"
        for _ in range(int(local_vars)):   
            self.asm_file.write(f"{push_0}")

    # Writes return command
    def writeReturn(self):
        # Intialize temporary variable FRAME/R13 = LCL
        frame = f"@LCL\nD=M\n@R13\nM=D\n"
        # Return address goes into temporary variable RET/R14
        ret_ad = f"@R13\nD=M\n@5\nA=D-A\nD=M\n@R14\nM=D\n"
        # Return the return value to the caller
        ret_val = f"@ARG\nD=M\n@R15\nM=D\n@SP\nM=M-1\n@SP\nA=M\nD=M\n@R15\nA=M\nM=D\n"
        # Restore caller stack pointer
        sp_restore = f"@ARG\nD=M\n@SP\nM=D+1\n"
        # Restore caller THAT
        THAT_restore = f"@R13\nD=M\n@1\nA=D-A\nD=M\n@THAT\nM=D\n"
        # Restore caller THIS
        THIS_restore = f"@R13\nD=M\n@2\nA=D-A\nD=M\n@THIS\nM=D\n"
        # Restore caller ARG
        ARG_restore = f"@R13\nD=M\n@3\nA=D-A\nD=M\n@ARG\nM=D\n"
        # Restore caller LCL
        LCL_restore = f"@R13\nD=M\n@4\nA=D-A\nD=M\n@LCL\nM=D\n"
        # Go to caller's return address
        rtrn = f"@R14\nA=M\n0;JMP\n"

        # Write to hack file
        hack_code_1 = f"{frame}{ret_ad}{ret_val}{sp_restore}{THAT_restore}"
        hack_code_2 = f"{THIS_restore}{ARG_restore}{LCL_restore}{rtrn}"
        self.asm_file.write(f"//Return\n")  # comment
        self.asm_file.write(f"{hack_code_1}{hack_code_2}")
    
    # Close asm_file
    def close(self):
        self.asm_file.close()
class Parser():
    def __init__(self, vm_code):    
        # Current line of VM code
        self.index = 0
        # This is false only if current line is last line
        self.hasMoreCommands = True
        # Open file of vm_code
        try:
            with open(vm_code) as vm_file:
                lines = [line for line in vm_file.read().splitlines()]
                lines = [line for line in lines if not (line == "" or line.startswith("//"))]
                lines = [line.split("//")[0].strip() for line in lines]                                           
                self.lines = lines
        except FileNotFoundError:
            print("file not found")
            pass
        
    def advance(self):
        self.index = self.index + 1
        self.hasMoreCommands = self.index < (len(self.lines) - 1) 

    def commandType(self):
        # Arithmetic commands are one word, which is the command. Push, pop, function, and call
        # have three words, the command and two args. All else have two words, the command and an arg.
        commands = {
            'add': "C_ARITHMETIC",
            'sub': "C_ARITHMETIC",
            'neg': "C_ARITHMETIC",
            'eq': "C_ARITHMETIC",
            'gt': "C_ARITHMETIC",
            'lt': "C_ARITHMETIC",
            'and': "C_ARITHMETIC",
            'or': "C_ARITHMETIC",
            'not': "C_ARITHMETIC",
            'push': "C_PUSH",
            'pop': "C_POP",
            'label': "C_LABEL",
            'goto': "C_GOTO",
            'if-goto': "C_IF",
            'function': "C_FUNCTION",
            'call': "C_CALL",
            'return': "C_RETURN"
            }
        for command in commands:
            if self.lines[self.index].startswith(command) and not self.lines[self.index].startswith("//"):
                return commands[command]
        return None
    
    def arg1(self):
        # If command is arithemtic, return the entire line i.e. the command itself
        if self.commandType() == "C_ARITHMETIC":
            return self.lines[self.index]
        # Else, return 1th element of line i.e. the first argument 
        elif self.commandType():
            try:
                return self.lines[self.index].split()[1]
            except IndexError:
                return None

    def arg2(self):
        # Nothing to return if command is arithmetic
        if self.commandType() == "C_ARITHMETIC":
            return None
        # Else, return 2th element of line i.e. the second argument 
        elif self.commandType():
            try:
                return self.lines[self.index].split()[2]
            except IndexError:
                return None
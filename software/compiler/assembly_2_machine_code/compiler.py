import sys

def main():
    # open asm file
    asmfile = sys.argv[1]
    with open(f'{asmfile}') as f:
        asm_code = f.read()
    # remove blank lines and comments
    asm_code = [line for line in asm_code.splitlines() if line != "" and not line.strip().startswith("//")]
    asm_code = [line.split("//")[0].strip() for line in asm_code]
    # parse code
    parsed_code = [parser(line.strip()) for line in asm_code]
    # handle labels, variables, and constants
    numerized_code = numerize(parsed_code)  
    # decode
    decoded_code = [decode(line) for line in numerized_code]
    # concatenate 
    concd_code = [conc(line) + '\n' for line in decoded_code]
    # write code to file
    hackfile = asmfile.replace(".asm", ".hack")
    with open(f'{hackfile}', 'w') as f:
        f.writelines(concd_code)

def parser(line):
    # don't parse labels
    if line.startswith("("):
        return line
    # parse A-instructions
    elif "@" in line:
        a_bit = "0"
        a_value = line.strip("@")
        return [a_bit, a_value]
    # parse C-instructions 
    elif "A" or "D" or "M" in line:
        dest = ""
        comp = ""
        jump = ""
        if "=" in line and ";" in line: 
            dest = line.split(";")[0].split("=")[0]
            comp = line.split(";")[0].split("=")[1]
            jump = line.split(";")[1]
        elif "=" in line:  
            dest = line.split("=")[0]
            comp = line.split("=")[1]
            jump = "null" 
        elif ";" in line:
            dest = "null"
            comp = line.split(";")[0]
            jump = line.split(";")[1]
        return ["111", dest, comp, jump]

def numerize(code):
    symbol_table = {'R0': 0,
                    'R1': 1,
                    'R2': 2,
                    'R3': 3,
                    'R4': 4,
                    'R5': 5,
                    'R6': 6,
                    'R7': 7,
                    'R8': 8,
                    'R9': 9,
                    'R10': 10,
                    'R11': 11,
                    'R12': 12,
                    'R13': 13,
                    'R14': 14,
                    'R15': 15,
                    'SP': 0,
                    'LCL': 1,
                    'ARG': 2,
                    'THIS': 3,
                    'THAT': 4, 
                    'SCREEN': 16384,
                    'KBD': 24576
    }
    line_counter = 0
    variable_value_counter = 16
    code_copy = []
    for line in code:
        try:
            symbol_table[f'{line.lstrip("(").rstrip(")")}'] = line_counter
        except AttributeError:
            line_counter += 1
    for line in code:
        if line[0] == ("0") and line[1] in symbol_table and line[1][0].isalpha():
            line[1] = symbol_table[f'{line[1]}']
            code_copy.append(line)
        elif line[0] == ("0") and line[1] not in symbol_table and line[1][0].isalpha():
            symbol_table[f'{line[1]}'] = variable_value_counter
            line[1] = symbol_table[f'{line[1]}']
            variable_value_counter += 1
            code_copy.append(line)
        elif line[0] == ("0") and line[1].isnumeric():
            code_copy.append(line)
        elif len(line) == 4:
            code_copy.append(line)
    return code_copy

def decode(line):

    dest_table = {'null': '000',
                  'M': '001',
                  'D': '010',
                  'MD': '011',
                  'A': '100',
                  'AM': '101',
                  'AD': '110',
                  'AMD': '111'
                }
    comp_table = {'0': '0101010',
                  '1': '0111111',
                  '-1': '0111010',
                  'D': '0001100',
                  'A': '0110000',
                  'M': '1110000',
                  '!D': '0001101',
                  '!A':'0110001',
                  '!M':'1110001',
                  '-D': '0001111',
                  '-A': '0110011',
                  '-M': '1110011',
                  'D+1': '0011111',
                  'A+1': '0110111',
                  'M+1': '1110111',
                  'D-1': '0001110',
                  'A-1': '0110010',
                  'M-1': '1110010',
                  'D+A': '0000010',
                  'D+M': '1000010',
                  'D-A': '0010011',
                  'D-M': '1010011',
                  'A-D': '0000111',
                  'M-D': '1000111',
                  'D&A': '0000000',
                  'D&M': '1000000',
                  'D|A': '0010101',
                  'D|M': '1010101'}
    jump_table = {'null': '000',
                  'JGT': '001',
                  'JEQ': '010',
                  'JGE': '011',
                  'JLT': '100',
                  'JNE': '101',
                  'JLE': '110',
                  'JMP': '111'}
    # in case of A-instruction, turn number into 15 bit binary value 
    if len(line) == 2:
        line[1] = int(line[1])
        if 0 <= line[1]:
            line[1] = line[1] % (2 ** 15)
            line[1] = bin(line[1]).lstrip('0b')
            line[1] = ("0" * (15 - len(line[1]))) + line[1]
        else:
            val = line[1] + (2 * line[1])
            val = line[1] % ((2 ** 15) - 1)
            line[1] = line[1] - val
            line[1] = bin(line[1]).lstrip('0b')
        return line 
    # in case of c insctruction, just change each instruction
    else:
        for field in dest_table:
            if field == line[1]:
                line[1] = dest_table[field]
        for field in comp_table:
            if field == line[2]:
                line[2] = comp_table[field]
        for field in jump_table:
            if field == line[3]:
                line[3] = jump_table[field]
        return line            
        
def conc(line):
    if len(line) == 4:
        concdline = line[0] + line[2] + line[1] + line[3]
    else:
        concdline = line[0] + line[1]
    return concdline

if __name__ == "__main__":
    main()
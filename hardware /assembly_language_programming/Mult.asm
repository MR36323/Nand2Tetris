    @R2
    M=0

    @i
    M=1
    @sum
    M=0

(LOOP)
    @i
    D=M
    @R0
    D=D-M
    @END
    D;JGT

    @R1
    D=M
    @sum
    M=M+D
    @i
    M=M+1

    @sum
    D=M
    @R2
    M=D

    @LOOP
    0;JMP

(END)  
    @END
    0;JMP
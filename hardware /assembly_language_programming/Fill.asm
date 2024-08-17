// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.


(INFINITELOOP)
// Check whether key is being pressed
    @KBD
    D=M
    @NOKEY
    D;JEQ

// Key has been pressed
    @i
    M=0   
(BLACKLOOP)
    @i
    D=M
    @8191
    D=D-A
    @INFINITELOOP
    D;JGT
// Make screen black
    @i
    D=M   
    @SCREEN
    A=A+D
    M=-1
// Increment counter
    @i
    M=M+1
// Jump to start of blackloop   
@BLACKLOOP       
    0;JMP
    
// Key has not been pressed
(NOKEY) 
    @j
    M=0   
(WHITELOOP)
    @j
    D=M
    @8191
    D=D-A
    @INFINITELOOP
    D;JGT
// Make screen white
    @j
    D=M   
    @SCREEN
    A=A+D
    M=0
// Increment counter
    @j
    M=M+1
// Jump to start of blackloop   
@WHITELOOP       
    0;JMP             
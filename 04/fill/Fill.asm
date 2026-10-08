// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
// Fill.asm
// Press any key: screen becomes black
// Release key: screen becomes white

(LOOP)
    // Check keyboard
    @KBD
    D=M
    @WHITE
    D;JEQ

    // Key pressed: black (-1)
    @COLOR
    M=-1
    @DRAW
    0;JMP

(WHITE)
    // No key pressed: white (0)
    @COLOR
    M=0

(DRAW)
    // Start of screen memory
    @SCREEN
    D=A
    @ADDR
    M=D

(DRAW_LOOP)
    // Check if address reached KBD (24576)
    @ADDR
    D=M
    @KBD
    D=D-A
    @LOOP
    D;JEQ

    // Write color to screen
    @COLOR
    D=M
    @ADDR
    A=M
    M=D

    // Move to next screen address
    @ADDR
    M=M+1

    @DRAW_LOOP
    0;JMP
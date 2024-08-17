# Nand2Tetris
Files for the Nand 2 Tetris Project

This repository contains my files for the Nand to Tetris (N2T) project. N2T involves designing a simple 16 bit computer, Hack, before creating a multi-stage compiler that allows the running, on Hack, of a simple object-oriented language, Jack. 

The hardware part of the project uses a straightforward hardware description language (HDL) to design Hack, from the nand gate upwards. There is also a small amount of coding in Hack’s assembly language. The software part of the project involves writing an application and simple operating system, in Jack, as well as designing a Jack compiler. The compiler translates:

	(1) Jack code to a stack-based virtual machine code
	(2) virtual machine code to the Hack assembly code
	(3) Hack assembly code to the Hack machine code 

Upon completing the project, this repository will contain HDL files, Hack assembly files, Jack files, and Python files (for the compiler).  

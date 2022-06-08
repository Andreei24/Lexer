# Lexer
A basic lexer used to break down a text into lexemes using regex.

Running the program requires 3 files as input:
  .lex file in which there is a number of tokens: <NAME> <REGEX>;
  .in file containing text
  .out file where the program will write pairs of <Token name, Lexem>
  
  
Implementation details:
  The program reads each line from the .lex file and transforms it into an NFA. The next step turns the NFA into a DFA using subset construction and is stored in an array.
  For each character in the input text read from the .in file, the program checks if there is any DFA that has a transition on the read char from its current state.
  When no DFA has a transition from its state on the read character and if any DFA accepted the string so far, the program will write in the .out file the name of the DFA
  that accepted and the accepted string. If no DFAs accepted, an error message is printed.

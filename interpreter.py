"""
=============================================================
NDLmini Interpreter (Main Driver)
=============================================================

Entry point for the NDLmini proof interpreter. If no input 
file is provided, a default sample proof is run (below).

This module should not need changing, but feel free to edit
the imports and source string when testing your solution.

Usage:
    python3 interpreter.py <source_file>
"""

import sys
from lexer import validate_input
from lexer import Lexer
from coursework2 import main  # NOTE: Feel free to change this!

# Default source NDLmini string if no target file is specified in params
source:str = ("""
    GIVEN A
    DERIVE A
    CONCLUDE
    """)

# Read NDLmini source from file, if provided
if len(sys.argv) > 1:
    try:
        with open(sys.argv[1]) as f: source = f.read()
    except OSError as e:
        print(f"Error reading file '{sys.argv[1]}': {e}")
        sys.exit(1)

# === Preprocessing
source = validate_input(source)

# === Tokenization 
lexer = Lexer()
token_stream = lexer.lex(source)

# === Drives coursework: Syntax, semantic, and logical analysis etc.
main(token_stream)
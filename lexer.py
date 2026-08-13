"""
=============================================================
NDLmini Lexer (Tokenization & Input Normalization)
=============================================================

Implements input preprocessing and lexical analysis to 
convert human-readable input into a structured format for
processing by your NDLmini PDA in states.py

NOTE: Do NOT edit this module.

Key Methods:
    validate_input(str) -> str

    Lexer.lex(str) -> TokenStream: The main entry point for 
        tokenizing an input string
"""

import re
from typing import List, Tuple
from tokens import *

"""
====================== TOKEN PATTERNS ======================
Constant mapping of token types to regex patterns as:
    TOKEN_PATTERNS:Tuple(TOKEN_NAME:str, REGEX_PATTERN:regex) 
    
Order matters as earlier entries have higher priority
"""
TOKEN_PATTERNS = [
	    (TOKENS.GIVEN,     r"GIVEN"),         # keywords
		(TOKENS.DERIVE,    r"DERIVE"),
		(TOKENS.ASSUME,    r"ASSUME"),
		(TOKENS.END,       r"END"),
		(TOKENS.APPLY,     r"APPLY"),
		(TOKENS.CONCLUDE,  r"CONCLUDE"),
        (TOKENS.LET,       r"LET"),            # subs
        (TOKENS.ASSIGN,    r"\="),
		(TOKENS.AND_INTRO, r"AND_INTRO"),      # inference rules
		(TOKENS.AND_ELIM,  r"AND_ELIM"),     
		(TOKENS.OR_INTRO,  r"OR_INTRO"),     
		(TOKENS.OR_ELIM,   r"OR_ELIM"),   
		(TOKENS.IMP_INTRO, r"IMP_INTRO"), 
		(TOKENS.IMP_ELIM,  r"IMP_ELIM"),  
		(TOKENS.NOT_INTRO, r"NOT_INTRO"), 
		(TOKENS.NOT_ELIM,  r"NOT_ELIM"),   
		(TOKENS.AND,       r"(\&\&)|(AND)"),   # logical ops
		(TOKENS.OR,        r"(\|\|)|(OR)"),
		(TOKENS.IMP,       r"(\-\>)|(IMP)"),
		(TOKENS.NOT,       r"(\!)|(NOT)"),
		(TOKENS.COMMA,     r"\,"),
		(TOKENS.ID,        r"[a-zA-Z0-9_]+"), # Must be penultimate
	]

"""
====================== LEXER ======================
The lexer is done for you and should not need changing!
"""

class Lexer:
    """
    A regex-based lexer for NDLmini.

    Attributes:
        token_patterns: List[Tuple[str, str]] 

    Methods:
        lex(source: str) -> TokenStream: Main lexing function
    """
    def __init__(self, token_patterns: List[Tuple[str, str]] = TOKEN_PATTERNS):
        self.token_patterns = [
            (name, re.compile(pattern))
            for name, pattern in token_patterns
        ]

    def lex(self, source: str) -> TokenStream:
        """
        Main lexing function
        @param source : str  - input, to be lexed; assumes this has been validated
	    @return TokenStream  - Token stream, to be parsed
        @raise  SyntaxError  - on regex match failed
        """
        tokens: List[Token] = []  # return
        for line_num, line in enumerate(source.splitlines(), start = 1):
            pos = 0
            length = len(line)
            while pos < length:
                # Skip whitespace
                if line[pos].isspace():
                    pos += 1
                    continue
                # Extract next lexeme (until whitespace)
                start = pos
                while pos < length and not line[pos].isspace(): pos += 1
                lexeme = line[start:pos]
                tokens.append(self._match_token(lexeme, line_num))

        return TokenStream(tokens)
    
    
    def _match_token(self, lexeme: str, line: int) -> Token:
        """
        Takes a str and returns the exact token match
        @param  lexeme : str 
        @return Token        - match
        @raise  SyntaxError  - on regex match failed
        """
        for symbol, regex in self.token_patterns:
            if regex.fullmatch(lexeme):
                return Token(
                    symbol = symbol,
                    value = lexeme,
                    line = line,
                )
        # No match found
        raise SyntaxError(f"Unexpected character \"{lexeme}\" on deduction line {line}.")
	
	
"""
====================== INPUT VALIDATION ======================
Input preprocessing is done for you and should not need changing!
"""
def validate_input(source: str) -> str:
    """
    Normalizes and cleans the source string:
        - Normalize line endings (CRLF & CR into LF)
        - Remove block comments: ### ... ###
        - Remove line comments: # ... EoL
        - Remove empty lines
        - Strip leading/trailing whitespace per line
        - Replace tabs and multiple spaces with single spaces
        - Adds a space before each comma (if there is not already one) for lexing

    @param  source : str  - input, to be cleaned
    @return str           - validated str, ready to be lexed
    """
    # Convert CRLF and CR to LF
    source = source.replace("\r\n", "\n").replace("\r", "\n")

    # Non-greedy match of ### ... ###
    source = re.sub(r"###.*?###", "", source, flags=re.DOTALL)

    # Remove everything from # to end of line
    source = re.sub(r"#.*", "", source)

    cleaned_lines = []

    for line in source.split("\n"):
        # Strip leading & trailing whitespace
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Replace tabs & multiple spaces with a single space
        line = re.sub(r"[ \t]+", " ", line)
        # Add space before comma (if missing)
        line = re.sub(r"(?<!\s),", " ,", line)
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
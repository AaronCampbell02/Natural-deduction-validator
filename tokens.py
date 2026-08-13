"""
=============================================================
NDLmini Lexer (Tokenization & Input Normalization)
=============================================================

Stores token data and structures

NOTE: Do NOT edit this module.

Classes:
    TOKENS: A constant class containing string id
        representations of the language tokens

    Token: Represents a token, encapsulating 
        its type (symbol), value (lexeme), and line number

    TokenStream: A utility class that wraps a list of tokens; 
        provides methods for token and list manipulation
"""


from dataclasses import dataclass

"""
====================== TOKEN DATA : Σ ======================
"""
class TOKENS:
    """
    Constant collection of token types in the form TOKENS.VAL:str
    """
    GIVEN       = "GIVEN"
    DERIVE      = "DERIVE"
    ASSUME      = "ASSUME"
    END         = "END"
    APPLY       = "APPLY"
    CONCLUDE    = "CONCLUDE"
    LET         = "LET"
    ASSIGN      = "ASSIGN"
    AND_INTRO   = "AND_INTRO"
    AND_ELIM    = "AND_ELIM"
    OR_INTRO    = "OR_INTRO"
    OR_ELIM     = "OR_ELIM"
    IMP_INTRO   = "IMP_INTRO"
    IMP_ELIM    = "IMP_ELIM"
    NOT_INTRO   = "NOT_INTRO"
    NOT_ELIM    = "NOT_ELIM"
    AND         = "AND"
    OR          = "OR"
    IMP         = "IMP"
    NOT         = "NOT"
    COMMA       = "COMMA"
    ID          = "ID"
    EoF         = "EoF"
    UNDEFINED   = "UNDEFINED"
    OPS                 = {NOT, AND, OR, IMP}
    BIN_OPS             = {AND, OR, IMP}
    COMMUTATIVE_OPS     = {AND, OR}
    NONCOMMUTATIVE_OPS  = {IMP}
    INF_RULES   = {
            AND_INTRO, AND_ELIM,
            OR_INTRO , OR_ELIM ,    
            IMP_INTRO, IMP_ELIM,   
            NOT_INTRO, NOT_ELIM
        }

@dataclass
class Token:
    """
    Represents a token, containing information about 
        its type (from TOKENS), 
        value (raw string), 
        and the line number from which it was extracted

    Methods:
        equals(symbol: str, value: str = TOKENS.UNDEFINED) -> bool:
            Compares the token against a given symbol with an optional value for full equivalence
        is_one_of(*symbols) -> bool:
            Checks if the token's symbol matches any of the provided symbols
    """
    symbol: str     # token type
    value:  str     # lexeme
    line:   int     # corresponding proof line

    def equals(self, symbol:str, value:str = TOKENS.UNDEFINED) -> bool:
        """
        Checks equivelence based on string comparison
        :param symbol: str 
        :param value: str - is ignored if not provided
        """
        if value == TOKENS.UNDEFINED: 
            return self.symbol == symbol
        else:                         
            return (self.value == value) and (self.symbol == symbol)
        
    def __eq__(self, other) -> bool:
        """
        Allows for the following usages:
            Token == Token
            Token == TOKENS.STR 
        """
        if type(other) == str:
            return self.equals(other)
        elif type(other) == Token:
            return self.equals(other.symbol, other.value)
        else:
            return False  # Type mismatch

    def is_one_of(self, *symbols) -> bool:
        """
        Equivelence check based on multiple str comparisons on symbol only
            i.e. does the symbol of this token match any of the those provided?
        
        :param symbols:: List<str>
                       | str*
        :return: True if there is a symbol match
        """
        if len(symbols) == 1 and isinstance(symbols[0], (list, tuple, set)):
            symbols = symbols[0]
        return self.symbol in symbols
    
    def __str__(self):
        if self.symbol == self.value:
            return self.value
        else:
            return f"{self.symbol}({self.value})"
 
class TokenStream:
    """
    Token list wrapper with built-in utilities such as 
        next(), peek(), consume(), etc.
    """
    tokens: list[Token]  # raw token list

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.length = len(tokens)

    def next(self, is_consuming:bool = True) -> Token:
        """
        Get next token in stream, consume by default
        :param isAdvancing: True means consuming, just peeking otherwise
        :return: Token next in the queue
        """
        if self.is_eof():  return Token(TOKENS.EoF,"EoF",-1)
        tok = self.tokens[self.pos]
        if (is_consuming):  self.pos += 1
        return tok

    def consume(self, n: int = 1) -> list[Token]:
        """
        Consume the next n tokens    
        :return: List[Token] of the next n tokens  
        """
        return [self.next() for _ in range(n)]
    
    def peek(self, n:int = 1) -> list[Token]:
        """:return List[Token] of the next n tokens (without consuming)"""
        toks = []
        for i in range(self.pos, self.pos+n):
            # add an EoF Tok to list if index is OoB
            if (i >= self.length):  toks.append(Token(TOKENS.EoF,"EoF",-1))
            else                 :  toks.append(self.tokens[i])
        return toks
    
    def peek_next(self) -> Token:
        """:return: next Token without consuming."""
        return self.peek()[0]

    def is_eof(self) -> bool:
        """:return: True if the end of the stream has been reached."""
        return self.pos >= self.length
        
    def __str__(self):
        return (', '.join(str(tok) for tok in self.tokens))

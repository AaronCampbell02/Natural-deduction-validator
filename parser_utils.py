"""
=============================================================
NDLmini Parser Utils (Helper Functions)
=============================================================

A collection of static helper functions, useful for keeping
PDA traversal readable. 

NOTE: Do NOT edit this module.
"""

from tokens import *
from logic import *

"""
====================== ERROR HELPERS ======================
"""
class AutomatonSyntaxError(Exception):
    def __init__(self, expected:str, state:str, instead:Token, append_msg:str=""):
        """
        Helper function to raise a structured syntax error
        Usage:
            raise AutomatonSyntaxError(...)
        :param expected: str of expected symbol
        :param state: str state in which the error occured
        :param instead: Token consumed instead of the expected symbol
        :param append_msg: optional appended str message
        """
        super().__init__(f"Expected {expected} in State {state}, instead got \'{str(instead)}\' on deduction line {instead.line}. {append_msg}")

"""
====================== TRAVERSAL HELPERS ======================
Helper functions for consuming tokens 
    (and converting to a logical represention from logic.py)
"""

# <literal> = NOT? ID(str)
def consume_lit(stream: TokenStream) -> Literal:
    """
    Consumes the next Literal from the token stream with maximal munch, 
    and returns it as a logic object. Two cases to consider:
        <atom> 
        NOT <atom>
    :param stream: from TokenStream consume <literal> (1 - 2 tokens)
    :return: Literal               
    :raise SyntaxError: on regex mismatch
    """
    toks = stream.peek(2)
    # Atom only
    if (toks[0].equals(TOKENS.ID)): 
        stream.consume(1)    
        return Literal(toks[0].value)
    # Negation
    elif (toks[0].equals(TOKENS.NOT) and toks[1].equals(TOKENS.ID)):
        stream.consume(2)    
        return Literal(toks[1].value, True)
    raise SyntaxError(f"Expected Literal(ID), instead got {toks[0].value} on deduction line {toks[0].line}.")

# <formula> = <lit> (<bin-op> <lit>)?
def consume_formula(stream: TokenStream) -> Formula:
    """
    Consumes the next Formula from the token stream with maximal munch, 
    and returns it as a logic object. Two cases to consider:
        <literal> 
        <literal> <bin-op> <literal> 
    :param stream: from TokenStream consume <formula> (1 - 5 tokens)
    :return: Formula
    :raise SyntaxError:
    """
    lit: Literal = consume_lit(stream)
    # Check for a binary operator
    if stream.peek_next().is_one_of(TOKENS.BIN_OPS):
        op = stream.next().symbol # consume operator
        lit1 = consume_lit(stream)
        return Formula(lit, op, lit1)
    return Formula(lit)


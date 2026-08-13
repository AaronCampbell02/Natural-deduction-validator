"""
=============================================================
NDLmini Logic (Logical System and Representation)
=============================================================

Defines the core logical data structures used by NDLmini:
    Atoms     - ID(str)
    Literals  - (NOT)? ATOM(id)
    Formulas  - LIT(id, is_neg?) OP(str) LIT(id, is_neg?)

Each contains structural equivalence checking with 
self.equals(...) and string conversion with self.__str__(). 

NOTE: Do NOT edit this module. Version 1.1a.

Classes:
    Atom: atomic proposition identified by a string id

    Literal: an atom or its negation

    Formula: Constructs logical formulas, which can be either 
        a single literal or a binary operation combining two 
        literals.

    Contradiction(Formula): a child of Formula indicating 
        falsehood, used in negation rules
"""

from __future__ import annotations 
from tokens import TOKENS
from typing import Optional

"""
====================== ERROR HANDLER ======================
"""
class LogicalError(Exception):
     def __init__(self, message): super().__init__(message)

"""
====================== ATOM ======================
"""
# ID(str)
class Atom:
    """
    Represents an atomic proposition

    Methods:
        equals(atom: Atom) -> bool: Compares this atom with another atom for ID equality
        __str__() -> str: Returns the string representation of the atom (ID)
    """
    id: str  # The identifier of the atom as a string constant

    def __init__(self, id:str):
        self.id = id 

    def equals(self, atom:Atom) -> bool:
        return self.id == atom.id
    
    def __str__(self) -> str:
        return self.id
    
    def __hash__(self):
        return hash(self.id)

"""
====================== LITERAL ======================
"""
# (NOT)? ATOM(str)
class Literal:
    """
    Represents a literal: 
        either an atom,
        or the negation of an atom

    Methods:
        equals(lit: Literal) -> bool: Compares this literal with another literal for structual logical equality
        __str__() -> str: Returns the string representation of the literal
        getNegation() -> Literal: Returns the negation of the current literal
    """
    atom:  Atom  # The atomic proposition that this literal represents
    is_neg: bool  # A flag indicating if the literal is negated (e.g. NOT A)

    def __init__(self, id:str, is_neg:bool = False):
        self.atom = Atom(id)
        self.is_neg = is_neg

    def equals(self, lit:Literal) -> bool:
        """
        Compares this literal with another literal for structual logical equality
            e.g. (NOT A).equals(NOT A)
        """
        return (self.atom.equals(lit.atom) and self.is_neg == lit.is_neg)
    
    def __eq__(self, other) -> bool:
        """
        Allows comparison between Literals and Formulas.
        Usages:
            Literal == Literal
            Literal == Formula
        """
        if type(other) == Literal:
            return self.equals(other)
        elif isinstance(other, Formula) and (other.lit_L is not None and not other.is_binary):
            return self.equals(other.lit_L)
        else:
            return False  # Otherwise (inequality, type mismatch etc.)
    
    def __str__(self) -> str:
        return f"NOT {self.atom.__str__()}" if self.is_neg else self.atom.__str__()

    def get_negation(self) -> Literal:
        """
        Returns the negation of this literal
        :return: negation of this literal
        """
        return Literal(self.atom.id, not self.is_neg)
    
    def __hash__(self):
        return hash((hash(self.atom), self.is_neg))

"""
====================== FORMULA ======================
"""
# LIT(str, is_neg?) OP(str) LIT(str, is_neg?)
class Formula:
    """
    Represents a logical formula:
        either a single literal,
        or a binary operation between two literals.
        Can also be special case of Formula() with all None values

    Methods:
        to_literal() -> Literal: casts self to Literal; raise LogicalError if it is not unary component
        equals(f: Formula) -> bool: Checks if this formula is structurally equivalent to another formula.
        __str__() -> str: Returns the string representation of the formula.
    """
    lit_L:    Optional[Literal]  # The first literal in the formula (i.e. on the left)
    lit_R:    Optional[Literal]  # The second literal (if and only if the formula is binary, or None otherwise)
    op:       Optional[str]      # The operator between the two literals (iff is binary, None otherwise)
    is_binary: bool              # A flag indicating if the formula has a binary component

    def __init__(self, lit_L:Optional[Literal] = None, op:Optional[str] = None, lit_R:Optional[Literal] = None):
        self.is_binary = False

        # Null formula
        if lit_L == None: 
            pass
        
        # Single literal formula
        self.lit_L = lit_L
        
        # Formula with a binary component
        if (lit_R != None) and (op != None): 
            self.lit_R = lit_R
            self.op = op
            self.is_binary = True

    def equals(self, other: Formula) -> bool:
        """
        Checks whether this formula is structurally equivalent to another formula
            i.e. they have the same syntactic shape, up to commutativity
            e.g. (A AND B).equals(B AND A)

        NB: this method does not check full semantic (logical) equivalence
            e.g. (P -> P) is not considered equivalent to (NOT P OR P)
            ...but (NOT P OR Q) is equivalent to (Q OR NOT P) by commutativity

        :param other: Formula to compare against
        :return: True iff the formulas are structurally equivalent, False otherwise 
        """

        # Null check
        if self.is_null() and other.is_null(): 
            return True
        elif self.is_null() or other.is_null(): 
            return False
        try:
            # Henceforth, both are not None
            assert self.lit_L is not None and other.lit_L is not None
        
            # One is binary, the other is not, ergo trivially not equal
            if self.is_binary != other.is_binary: return False

            # Both are atomic (single literal)
            if not self.is_binary: return self.lit_L.equals(other.lit_L)

            # Henceforth, both are binary
            assert self.lit_R is not None and other.lit_R is not None

            # Operators must match, we are checking structural equivelence only
            if self.op != other.op: return False
            
            # Non-commutative: order matters
            if self.op in TOKENS.NONCOMMUTATIVE_OPS:
                return (
                    self.lit_L.equals(other.lit_L) and
                    self.lit_R.equals(other.lit_R)
                )
            # Commutative: order does not matter
            if self.op in TOKENS.COMMUTATIVE_OPS:
                return (
                    (
                        self.lit_L.equals(other.lit_L) and
                        self.lit_R.equals(other.lit_R)
                    ) or (
                        self.lit_L.equals(other.lit_R) and
                        self.lit_R.equals(other.lit_L)
                    )
                )
        except: pass
        return False  # Safety fallback (unknown operator)

    def __hash__(self):
        if self.is_binary:

            if self.op in TOKENS.COMMUTATIVE_OPS:
                return hash(self.lit_L) + hash(self.op) + hash(self.lit_R)
            else:
                return hash((
                    hash(self.lit_L), 
                    hash(self.op),
                    hash(self.lit_R)
                ))
        else:
            return hash(self.lit_L)

    def __eq__(self, other) -> bool:
        """
        Allows comparison between Literals and Formulas.
        Usages:
            Formula == Formula
            Formula == Literal
        """
        if type(other) == Formula:
            return self.equals(other)
        elif type(other) == Literal:
            return self.equals(Formula(other))
        else:
            return False  # Type mismatch

    def is_null(self) -> bool:
        return self.lit_L == None

    def __str__(self) -> str:
        if self.is_null():
            return "NULL"
        elif self.is_binary: 
            return (f"{self.lit_L.__str__()} {self.op} {self.lit_R.__str__()}")
        else:
            return self.lit_L.__str__()
        
    def to_literal(self) -> Literal:
        """Attempt to cast self to a Literal."""
        if self.is_binary:
            raise LogicalError(f"Cannot cast binary Formula {self} to a Literal.")
        elif self.lit_L == None:
            raise LogicalError(f"Cannot cast null Formula {self} to a Literal.")
        else:
            return self.lit_L



"""
====================== CONTRADICTION ======================
"""
CONTRADICTION = "⊥"
class Contradiction(Formula):
    """
    A specific type of Formula that represents the logical constant false (⊥):
        a single atomic formula with no binary components.
    """
    def __init__(self):
        self.lit_L = Literal(CONTRADICTION)
        self.is_binary = False
    def __str__(self) -> str:
        return "⊥"
    def __eq__(self, other) -> bool:
        return super().equals(other)
    def __hash__(self):
        return super().__hash__()
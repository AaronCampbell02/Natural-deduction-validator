"""
=============================================================
CS143-15 Coursework: Part Two
=============================================================

Complete Part Two of the coursework here! 

NOTE: coursework1.py and coursework2.py are the only files 
you should edit (excluding interpreter.py for changing the
target coursework file or default input string)

Entry point:
    main(...) called from interpreter.py

Preamble:

This program implements a proof validator for NDLmini, the syntax of the proof was previously implemented through coursework1.py.
Changes made to coursework2.py implemented logical verification to validate the proof, by applying inference rules and scopes based on global values and assumptions.
The program is designed such that inner scopes can access outer scopes, but formulas derived in a sub proof are not accessible outside.
Each inference rule is implemented through its own specific function, ensuring modularization and simplified testing.
Tests used for Coursework2.py are in /proofs/tasks/errorcase2, this ensured the program was tested against a set of valid and invalid proofs.

1 - The proof system specifically for NDLmini is sound as formulas are only added when provided as premises or produced by pretested inference rules.
Each inference rule determines formulas are of the right shape and in scope before yielding the output.
A proof is only accepted when the syntax and logic are valid, this means assumptions are closed and the goal is derived in the global scope.

2 - While the system for NDLmini is sound, the system is not complete.
This is because it doesn't support propositional logic, formulas can't be nested and assumptions are limited to literals and double negation is not representable.

3 - The language/validator could be improved by supporting nested formulae to closer represent natural language.
The error messages could also be improved by including line numbers, or clearer errors. In addition, the final reporting in main could better distinguish between a proof that derives the goal and a proof that is rejected overall because of a syntax or scope error.
Furthermore, the line if is_in_scope(goal): could be improved to decisively check the global and premise scope, as issues may arise if the scope is not closed.

"""

from pushdown import *
from tokens import *
from logic import *
from parser_utils import *

# Initialise a new PDA 
my_automaton: PushdownAutomaton = PushdownAutomaton()

# Declaring and initialising global variables for handling proof logic
goal: Formula = Formula()
premises: set[Formula] = set()
derived:  set[Formula] = set()
assumptions: dict[tuple[Literal, ...], set[Formula]] = {}

def add_derivation(f: Formula):
    """
    Adds a formula to the current scope
    :param f: Formula to be added
    """
    stack = my_automaton.get_stack()
    scope = tuple(stack) # gets currents scope

    #if no scope then in global scope otherwise in the local scope
    if scope: 
        assumptions[scope].add(f)
    else:
        derived.add(f)

def is_in_scope(f: Formula, scope_list: list[Literal] = []) -> bool:
    """
    Checks if a specified formula is in scope
    :param f: Formula to check 
    :return: True if the formula was found
    """
    # if the scope is empty get scope from stack
    if scope_list == []:
        scope_list = my_automaton.get_stack()

    current = list(scope_list) # copy the scope list - to avoid manipulating it

    #check current scope then each parent scope - increasing scope throughout
    while current:
        scope = tuple(current)
        if (scope in assumptions) and (f in assumptions[scope]):
            return True
        current.pop()

    return (f in premises) or (f in derived) # if the formula is in derive or premises return true else false

def apply_and_intro(f_L: Formula, f_R: Formula) -> Formula:
    """
    This function checks if both formulas are unary and if they are in scope
    returning specific logic errors if these conditions aren't met

    If this is true the function returns the conjuction of two formulas as a new formula
    """

    if (f_L.is_binary or f_R.is_binary):
        raise LogicalError("And introduction requires two unary formulas.")

    if not (is_in_scope(f_L) and is_in_scope(f_R)):
        raise LogicalError("And introduction requires both formulas to be in scope.")

    lit_L = f_L.to_literal()
    lit_R = f_R.to_literal()
    return Formula(lit_L, TOKENS.AND, lit_R)

def apply_and_elim(f_L: Formula, f_R: Formula) -> Formula:

    """
    This function checks if the there is a conjuctive formula, and if the conjuctive formula is in scope.
    It also checks if the other formula is unary (contains no operators)
    It then checks one of literals of the conjuctive formula matches the unary literal

    If so it returns the opposite conjuct of the literal provided  
    
    """
    # determine which formula is unary and which is conjuctive
    if f_L.is_binary and f_L.op == TOKENS.AND:
        conj = f_L
        unary = f_R
    elif f_R.is_binary and f_R.op == TOKENS.AND:
        conj = f_R
        unary = f_L
    else:
        raise LogicalError("And elimination requires a conjunctive formula.")

    if not is_in_scope(conj):
        raise LogicalError("And elimination requires conjunctive formula to be in scope.")

    if unary.is_binary:
        raise LogicalError("And elimination requires a unary formula.")

    uval = unary.to_literal() # convert unary value to literal

    #return formula as opposite conjuct if literal matches a conjunct
    if uval == conj.lit_L:
        return Formula(conj.lit_R)
    elif uval == conj.lit_R:
        return Formula(conj.lit_L)
    else:
        raise LogicalError("And elimination requires a formula to match a literal in the conjunctive formula.")

def apply_or_intro(f_L: Formula, f_R: Formula) -> Formula:
    """
    
    Or introduction requires at least one of the disjuncts are in scope and that both formulas are unary

    If this is true the formula is returned with the two unary values connected via an or

    """

    if (f_L.is_binary or f_R.is_binary):
        raise LogicalError("Or introduction requires two unary formulas.")
    
    if not (is_in_scope(f_L) or is_in_scope(f_R)):
        raise LogicalError("Or introduction requires one formula to be in scope")

    lit_L = f_L.to_literal()
    lit_R = f_R.to_literal()
    return Formula(lit_L, TOKENS.OR, lit_R)


def apply_or_elim(f_L: Formula, f_R: Formula) -> Formula:
    """

    Or elimination checks if both formulas are in scope, that one formula is disjunctive and the other is unary
    The unary formula must be a negation and the negation of the unary formula must match a disjunct

    The opposite disjunct is then returned as a formula

    e.g.

    or_elim NOT A , A OR B
    yields B

    """
    if not (is_in_scope(f_L) and is_in_scope(f_R)):
        raise LogicalError("Or elimination requires both formulas to be in scope.")

    # Identify the disjunct and unary negation values
    if f_L.is_binary and f_L.op == TOKENS.OR:
        disj = f_L
        uNeg = f_R
    elif f_R.is_binary and f_R.op == TOKENS.OR:
        disj = f_R
        uNeg = f_L
    else:
        raise LogicalError("Or elimination requires a disjunctive formula.")

    if uNeg.is_binary:
        raise LogicalError("Or elimination requires a unary formula.")

    lit = uNeg.to_literal() # convert unary negation to literal

    # check if value is negated
    if not lit.is_neg:
        raise LogicalError("Or elimination requires one formula to be a negation.")

    inverse = lit.get_negation()

    #return formulas if literal matches a negated disjunct
    if inverse == disj.lit_L:
        return Formula(disj.lit_R)
    if inverse == disj.lit_R:
        return Formula(disj.lit_L)

    raise LogicalError("Or elimination requires a formula to match a literal in the disjunctive formula.")

def apply_imp_intro(f_L: Formula, f_R: Formula) -> Formula:
    """

    Implies introduction can occur in 4 different cases

        B is globally derived
        B is derived under A

        B is assumed under A
        A is assumed and B is in scope

    results in A -> B

    This can be determined by two cases as long as both formulas are unary

    Checking B is in scope either globally or under A

    Checking if the current scope contains A and B is in scope

    """

    #checks both formulas are unary
    if f_L.is_binary or f_R.is_binary:
        raise LogicalError("Implies introduction requires two unary formulas.")
    
    litL = f_L.to_literal()
    litR = f_R.to_literal()

    # checks if the right formula is in scope where the left literal is assumed - if so we can introduce left -> right
    # also covers global scope via is_in_scope() method
    if is_in_scope(f_R, [litL]):
        return Formula(litL, TOKENS.IMP, litR)
    

    # if left literal in current scope and so is the right formula
    # we can introduce left -> right
    currentScope = my_automaton.get_stack()
    if litL in currentScope and is_in_scope(f_R, currentScope):
        return Formula(litL, TOKENS.IMP, litR)

    raise LogicalError("Implies introduction requires the consequent to be in scope given the antecedent.")

def apply_imp_elim(f_L: Formula, f_R: Formula) -> Formula:
    """

    Implies elimination requires both formulas to be in scope, with one formula being unary and the other an implication

    The unary value must match the left value of the implication

    if it does the right value of the implication is returned

    """
    #determine both formulas are in scope
    if not (is_in_scope(f_L) and is_in_scope(f_R)):
        raise LogicalError("Implies elimination requires both formulas to be in scope.")
    
    # Identify the implication and unary value
    if f_L.is_binary and f_L.op == TOKENS.IMP:
        imp = f_L
        unary = f_R
    elif f_R.is_binary and f_R.op == TOKENS.IMP:
        imp = f_R
        unary = f_L
    else:
        raise LogicalError("Implies elimination requires a binary implication.")

    #checks if unary value is actually unary
    if unary.is_binary:
        raise LogicalError("Implies elimination requires a unary formula.")

    lit = unary.to_literal() # convert unary negation to literal

    #return formulas if literal matches a negated disjunct
    if lit == imp.lit_L:
        return Formula(imp.lit_R)

    raise LogicalError("Implies elimination requires the unary formula to match the left value of the implication.")


def apply_not_intro(f_L: Formula, f_R: Formula) -> Formula:
    """

    Confirms f_L is assumed
    Checks if a contradiction is present when f_L is the most recent assumption
    returns not f_L

    E.G - below is accepted as P is the most recent assumption

    GIVEN P IMP Q
    DERIVE NOT Q IMP NOT P

    ASSUME NOT Q
        ASSUME P
            APPLY IMP_ELIM P, P IMP Q # yields Q
            APPLY NOT_ELIM Q, NOT Q
        END
        APPLY NOT_INTRO P, P
    END
    APPLY IMP_INTRO NOT Q, NOT P
    CONCLUDE


    Based of specification it also check that f_R == f_L, desipite the f_R value being negligible

    """
    #checks if unary
    if f_L.is_binary:
        raise LogicalError("Not introduction requires a unary formula.")
    
    if f_L != f_R:
        raise LogicalError("Not introduction requires both input formulas to be the same.")
    
    litL = f_L.to_literal()

    # actively limits scope search to just litL as long as it is the most recent assumption
    # not globally or with a reduced scope - avoiding use of is_in_scope() due to this reason

    for scope, formulas in assumptions.items():
        if scope and scope[-1] == litL and Contradiction() in formulas:
            return Formula(litL.get_negation())
    
    raise LogicalError ("Contradiction is not in scope under the assumption of f_L")


def apply_not_elim(f_L: Formula, f_R: Formula) -> Formula:
    """

    Not elimination requires two unary formulae, which are both in scope
    If this is confirmed one formula must be equivalent to the negation of the other

    """

    #check both are unary
    if (f_L.is_binary or f_R.is_binary):
        raise LogicalError("Not elimination requires two unary formulas.")

    #check if in scope
    if not (is_in_scope(f_L) and is_in_scope(f_R)):
        raise LogicalError ("Not elimination requires both formulas to be in the current scope")

    litL = f_L.to_literal()
    litR = f_R.to_literal()

    #test negation of formula is equivalent to other
    if litL.get_negation() == litR:
        return Contradiction()

    raise LogicalError ("Not elimination requires one formula to be equivalent to the negation of the other formula")




def main(stream: TokenStream):
    """
    Entry point, takes an input stream and inputs it to the automaton
    :param stream: TokenStream to parse
    """
    my_automaton.set_start_state(Q_START())
    my_automaton.set_accept_state(Q_ACCEPT())

    is_accepted = my_automaton.parse(stream)

    if is_accepted:
        print(f"The input [{stream}] is ACCEPTED.")
    else:
        print(f"The input [{stream}] is REJECTED.")

    # Print the result of logical verification
    if is_in_scope(goal):
        print(f"The goal {goal} was SUCCESSFULLY derived.")
    else:
        print(f"The goal {goal} was NOT derived.")

"""
====================== State Definitions ======================
"""

class Q_START(State):
    def step(self, stream: TokenStream) -> State:
        """
        Initial state - transition functions: 
            δ(Q_START, GIVEN) = Q_PREMISES
            δ(Q_START, DERIVE) = Q_GOAL
        """
        next_tok = stream.next()  # Consume next token

        if next_tok == TOKENS.GIVEN: 
            return Q_PREMISES()    # 1. If given transition to Q_PREMISES
        elif next_tok == TOKENS.DERIVE: 
            return Q_GOAL()  # 2. Else if derive transition to Q_GOAL
        else:
            raise SyntaxError(f"Expected GIVEN or DERIVE in {self}, got {next_tok}.")
    

class Q_ACCEPT(State):  
    def step(self, stream: TokenStream) -> State:
        """
        There are no transitions out of this state
        :raise AutomatonSyntaxError: If there are any remaining symbols 
        """
        if not stream.is_eof():  # Tokens still remain in the stream
            raise AutomatonSyntaxError(
                    "End of Input", str(self), stream.next()  # Expected End of Input in Q_ACCEPT
                )  
        return self  # Safety net - should be unreachable

class Q_PREMISES(State):
    def step(self, stream: TokenStream) -> State:
        """
        Transition functions: 
            1. δ(Q_PREMISES, <formula>) = Q_START
        """

        formula = consume_formula(stream) # Consumes formula - has error detection
        print(f"Adding premise: {formula}")
        premises.add(formula) # add to premises

        return Q_START()

class Q_GOAL(State):
    def step(self, stream: TokenStream) -> State:
        """
        Transition functions: 
            1. δ(Q_PREMISES, <formula>) = Q_PROOF
        """

        formula = consume_formula(stream) # Consumes formula - has error detection
        print(f"Setting goal: {formula}")
        global goal
        goal = formula # assigns formula to global goal variable (defined at the start)

        return Q_PROOF()

class Q_PROOF(State):
    def step(self, stream: TokenStream) -> State:
        """
        Transition functions: 
            1. δ(Q_PROOF, CONCLUDE) = Q_ACCEPT
            2. δ(Q_PROOF, APPLY) = Q_INFERENCE
            3. δ(Q_PROOF, ASSUME) = Q_SUBPROOF_OPEN
            4. δ(Q_PROOF, END) = Q_PROOF ; pop(<lit>)
        """

        next_tok = stream.next()  # Consume next token

        if next_tok == TOKENS.CONCLUDE: 
            return Q_ACCEPT()    # 1. If CONCLUDE transition to Q_ACCEPT
        elif next_tok == TOKENS.APPLY:
            return Q_INFERENCE() #2 If apply transition to inference
        elif next_tok == TOKENS.ASSUME:
            return Q_SUBPROOF_OPEN() #3 If assume transition to subproof
        elif next_tok == TOKENS.END:
            my_automaton.pop() # 4 If END pop current subproof and return to proof state
            return Q_PROOF()
        else:
            raise SyntaxError(f"Expected CONCLUDE or APPLY or ASSUME or END in {self}, got {next_tok}.")

        return self

class Q_INFERENCE(State):
    def step(self, stream: TokenStream) -> State:
        
        """
        Transition functions: 
            1. δ(Q_INFERENCE, <inference-rule> <formula> COMMA <formula>) = Q_PROOF

        Determines if a valid inference rule, if so adds output for the corresponding inference rule to derivations
        """

        iRule = stream.next()
        if not iRule.is_one_of(TOKENS.INF_RULES):
            raise SyntaxError(f"Expected inference rule in {self}, got {iRule}.")

        formula_L = consume_formula(stream) # Consumes formula
        
        next_tok = stream.next()  # Consume next token
        if next_tok != TOKENS.COMMA:
            raise SyntaxError(f"Expected COMMA in {self}, got {next_tok}.")

        formula_R = consume_formula(stream) # Consumes formula

        if iRule == TOKENS.AND_INTRO:
            formula_yield = apply_and_intro(formula_L, formula_R)  # apply and intro rule
        elif iRule == TOKENS.AND_ELIM:
            formula_yield = apply_and_elim(formula_L, formula_R) # apply and elim rule
        elif iRule == TOKENS.OR_INTRO:
            formula_yield = apply_or_intro(formula_L, formula_R) # apply or intro rule
        elif iRule == TOKENS.OR_ELIM:
            formula_yield = apply_or_elim(formula_L, formula_R) # apply or elim rule
        elif iRule == TOKENS.IMP_INTRO:
            formula_yield = apply_imp_intro(formula_L, formula_R) # apply imp intro rule
        elif iRule == TOKENS.IMP_ELIM:
            formula_yield = apply_imp_elim(formula_L, formula_R) # apply imp elim rule
        elif iRule == TOKENS.NOT_INTRO:
            formula_yield = apply_not_intro(formula_L, formula_R) # apply not intro rule
        elif iRule == TOKENS.NOT_ELIM:
            formula_yield = apply_not_elim(formula_L, formula_R) # apply not elim rule
        else:
            raise LogicalError(f"inference rule not accounted for: {iRule}.")
        
        print(f"{iRule} yield: {formula_yield}")
        add_derivation(formula_yield)

        return Q_PROOF()
        
class Q_SUBPROOF_OPEN(State):
    def step(self, stream: TokenStream) -> State:
        """
        Transition functions: 
            1. δ(Q_SUBPROOF_OPEN, <lit>) = Q_PROOF; push (<lit>)
        """
        lit = consume_lit(stream) # consume literal and push to stack
        my_automaton.push(lit)

        stack = my_automaton.get_stack()
        scope = tuple(stack)

        if scope not in assumptions:
            assumptions[scope] = {Formula(lit)}
        
        print(f"Entering scope ({', '.join(str(lit) for lit in scope)})")

        return Q_PROOF()
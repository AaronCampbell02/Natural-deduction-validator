"""
=============================================================
CS143-15 Coursework: Part One
=============================================================

Complete Part One of the coursework here! 

NOTE: coursework1.py and coursework2.py are the only files 
you should edit (excluding interpreter.py for changing the
target coursework file or default input string)

Entry point:
    main(...) called from interpreter.py

Pre - amble

This program simulates a PDA to process the syntax of NDLmini proofs via representing states as classes, using the step method to move between states.
The PDA is deterministic due to only have one possible outcome per token.

The syntax of a NDLmini proof is broken down into premises until the proof goal
this is followed by the proof until the CONCLUDE token.

The premises are parsed via looping between the start and premises state until DERIVE, where state is changed to the goal state. 

The syntax of the proof is parsed via proof state, which is set after the goal state consumes a formula. Proofs are parsed by:
•	Accepting - when conclude is the next token
•	Inference rules - when APPLY is the next token, two formulas, a comma and the rule are consumed
•	Sub proofs - when ASSUME is parsed
Sub proofs are parsed via implementation of a stack through the PDA, when Assume is read the literal is pushed, when END is parsed the literal is popped.

The stack must be empty when concluding and not be popped from when empty.

The program was tested for various syntax on /proofs/tasks/errorcases, to make more robust.

"""

from pushdown import *      # State and PDA base classes
from tokens import *        # TOKENS, Token, TokenStream
from logic import *         # Literal, Formula, Contradiction
from parser_utils import *  # Parsing error and traversal helpers

# Initialise a new PDA 
my_automaton: PushdownAutomaton = PushdownAutomaton()

def main(stream: TokenStream):
    """
    Entry point, takes an input stream and inputs it to the automaton
    :param stream: TokenStream to parse
    """
    # Assign start state Q_START and accept state Q_ACCEPT 
    my_automaton.set_start_state(Q_START())
    my_automaton.set_accept_state(Q_ACCEPT())

    # Parse the input stream using the PDA
    is_accepted = my_automaton.parse(stream)

    # Print the result
    if is_accepted:
        print(f"The input [{stream}] is ACCEPTED.")
    else:
        print(f"The input [{stream}] is REJECTED.")

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

        consume_formula(stream) # Consumes formula - has error detection

        return Q_START()

class Q_GOAL(State):
    def step(self, stream: TokenStream) -> State:
        """
        Transition functions: 
            1. δ(Q_PREMISES, <formula>) = Q_PROOF
        """

        consume_formula(stream) # Consumes formula

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


class Q_INFERENCE(State):
    def step(self, stream: TokenStream) -> State:
        
        """
        Transition functions: 
            1. δ(Q_INFERENCE, <inference-rule> <formula> COMMA <formula>) = Q_PROOF
        """

        iRule = stream.next()
        if not iRule.is_one_of(TOKENS.INF_RULES):
            raise SyntaxError(f"Expected inference rule in {self}, got {iRule}.")

        consume_formula(stream) # Consumes formula
        
        next_tok = stream.next()  # Consume next token
        if next_tok != TOKENS.COMMA:
            raise SyntaxError(f"Expected COMMA in {self}, got {next_tok}.")

        consume_formula(stream) # Consumes formula

        return Q_PROOF()
        
class Q_SUBPROOF_OPEN(State):
    def step(self, stream: TokenStream) -> State:
        """
        Transition functions: 
            1. δ(Q_SUBPROOF_OPEN, <lit>) = Q_PROOF; push (<lit>)
        """
        lit = consume_lit(stream) # consume literal and push to stack
        my_automaton.push(lit)

        return Q_PROOF()
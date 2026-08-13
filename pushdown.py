
"""
=============================================================
NDLmini Pushdown (Automaton & State)
=============================================================

Implements the pushdown automaton (PDA) that drives parsing.

NOTE: Do NOT edit this module.

Classes:
    State(abstract):
        Base class for all concrete PDA states; each state
        implements step(...), which consumes input tokens
        and returns the next state

    PushdownAutomaton:
        Machine for emulating a PDA
"""

from __future__ import annotations 
from abc import ABC, abstractmethod
from tokens import TokenStream
from logic import Literal

"""
====================== ABSTRACT STATE DATA =====================
Abstract class that all States inherit from
"""
class State(ABC):
    """Base State class for all concrete states (Q)"""
    def __new__(cls):
        """Singleton implementation such that all references to MyState() refer to the same instance"""
        if not hasattr(cls, 'inst'):
            cls.inst = super().__new__(cls)
        return cls.inst
    
    @abstractmethod
    def step(self, stream: TokenStream) -> State:
        """
        Defines the outward transitions from this state 
        :return: the next state
        :raise SyntaxError: on invalid input
        """
        pass

    def __str__(self):
        """Returns the name of the class"""
        return self.__class__.__name__ 

"""
====================== PUSHDOWN AUTOMATON ======================
"""
class PushdownAutomaton:
    """
    Drives the parser via state traversal
    Methods:
        parse(...)
        is_empty()
        pop()
        push(...)
        peek()
    """
    def __init__(self):
        self._stack : list[Literal]  # Note: Python doesn't distinguish between lists and stacks!
        self._start_state : State 
        self._accept_state : State

    def _reset_context(self):
        self._stack = []

    def set_start_state(self, q_start: State):
        self._start_state = q_start
    
    def set_accept_state(self, q_accept: State):
        self._accept_state = q_accept

    def _parse(self, stream: TokenStream) -> bool:
        # In the case of no start or accept state, the machine trivially does not accept any strings
        if not self._start_state or not self._accept_state:
            raise SyntaxError("Start and/or Accept state not defined.")

        self._reset_context()
        currentState = self._start_state

        # Iterate until stream is empty
        while not stream.is_eof():
            currentState = currentState.step(stream)

        # Return True iff in accept state and stack is empty
        if not self.is_empty():
            raise SyntaxError(f"Stack not empty at conclusion: [{', '.join(map(str,self._stack))}].")
        else:
            return currentState is self._accept_state
        
    def parse(self, stream: TokenStream) -> bool:
        """
        Consumes tokens until end of stream
        :param stream: TokenStream
        :return: True if the input is accepted, False otherwise
        """
        try:
            return self._parse(stream)
        except Exception as e:
            print(f"\033[1m{type(e).__name__}\033[0m: {e}")
            return False 


    def is_empty(self) -> bool:
        return len(self._stack) == 0
    
    def pop(self) -> Literal:
        """
        Pops the stack
        :return: Literal at top of stack
        :raise SyntaxError: if the stack is empty
        """
        if len(self._stack) == 0: 
            raise SyntaxError(f"Stack underflow in {self.__class__.__name__}: Cannot pop from an empty stack!")
        return self._stack.pop()

    def peek(self) -> Literal:
        """
        Peek at the top element of the stack
        :return: Literal at top of stack (or None)
        """
        if len(self._stack) == 0: 
            raise SyntaxError(f"Stack underflow in {self.__class__.__name__}: Cannot peek an empty stack.")
        return self._stack[-1]  # return end of stack 

    def push(self, lit:Literal):
        """
        Pushes a new assumption
        """
        self._stack.append(lit)

    def get_stack(self) -> list[Literal]:
        return self._stack
# Natural-deduction-validator
This project parses natural deduction proofs and verifies if they are valid proofs.

Proofs are verified both logically (whether they hold) and syntactically (via a push down automata).
All proofs are built from inference rules:

AND_INTRO, AND_ELIM, OR_INTRO, OR_ELIM, IMP_INTRO, IMP_ELIM, NOT_INTRO, NOT_ELIM

https://en.wikipedia.org/wiki/Rule_of_inference

The pushdown automata ensures scopes match, by pushing and popping based upon Assume/End

coursework1.py provides syntax parsing
coursework2.py implements logical validation by application of inference rules

Proofs are written as followed
Given ... Derive ...
with a sequence of Apply rule f1 f2, assume lit

///
GIVEN P
GIVEN Q
DERIVE P AND Q
APPLY AND_INTRO P, Q
CONCLUDE
///

The program is run by the command

python interpreter.py

Edit the target proof in interpreter.py

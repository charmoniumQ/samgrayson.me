---
layout: page
title: Prolog tutorial
---

Two weeks ago Dr. Gupta introduced the language Prolog in his talk. I think it
is a pretty neat language for doing math. You can try it out online
[here](http://swish.swi-prolog.org/). (click the x and then `create a program
here`). Your program is a list of clauses where the left-hand side is a
predicate and the right-hand side is a boolean expression, and they are
separated by a colon-equals. The colon-equals acts like a "is implied by"
operator. Then you get to have some queries which are arbitrary boolean
expressions. Prolog will try and find the variable assignments for which the
expression is provable.

Words that start with a capital are considered universally quantified
variables. Lowercase words are predicates or constants which work how you would
expect. Comma means "and" and semicolon means "or". You have basic arithmetic
operators (+, -, * /, mod).

For example, type the following rules in as your program

    even(N) :- 0 is N mod 2.
    odd(N)  :- 1 is N mod 2.

I interpret the previous program as saying "If N mod 2 is 0, then even(N)." Then
at the query box, you can type in

    even(2).

Prolog will happily say "true". We can use an undefined variable in our query
and Prolog will tell us the values for which it is provable. Clicking the next
button will tell prolog to show additional values of X.

    between(0, 10, X), even(X).

Now, I want to test the Collatz conjecture

    even(N) :- 0 is N mod 2.
    odd(N)  :- 1 is N mod 2.
    
    collatz(1) :- true, !.                            % first rule
    collatz(X) :- even(X), !, Y is X/2, collatz(Y).   % second rule
    collatz(X) :- odd(X), !, Y is 3*X+1, collatz(Y).  % third rule

Ignore the exclamation mark for now. If your query is

    collatz(10).

Prolog tries to prove it (that's called prologs goal). It can't prove it with the first rule, so it tries to prove it by the second rule. Prolog's new goal is `even(10), Y is 10/2, collatz(Y)`. It easily proves `even(10)` and the second part is like a "let" that doesn't need to be proven. The only tough part is `collatz(5)`. The first rule does not apply, Prolog tries the second rule, but the goal fails. Prolog says "even though proving `collatz(5)` with the second rule failed, I can still try a different way". This is called backtracking. Now it tries to prove `collatz(5)` with the third rule. It has the goals `odd(5)`, `Y is 3*5+1`, which are both proven, and `collatz(16)`. Now it still can't apply the first rule, but it fits the second rule and prolog does that four times, at which point it has the goal `collatz(1)` which it proves with the first rule. Try running the query and using 'step forward'

    trace, collatz(10).

You will notice that prolog is basically constructing a tree, where it tries to prove the thing on the left by proving multiple things on the right recursively. If it can't, it backs up until the last place in which a decision point was made, and tries making the other decision. This is a very powerful recursive method for proving statements and writing programs.

Do you think you can write a predicate `gcd(A, B, X)` that is true iff X is the gcd of A and B using the Euclidean algorithm?

Try [this](http://www.cpp.edu/~jrfisher/www/prolog_tutorial/contents.html) to learn more. They have some pretty cool examples including graph coloring, towers of Hanoi, and making change for a dollar.

---
layout: post
title:  "The Y-combinator"
tags: [programming, math]
excerpt:
unpublished: true
---

# Into to Lisp

If you do not know Lisp but have learned another language, this section will introduce you. If you are comfortable with Lisp, skip this section. I will be using [Racket](http://racket-lang.org/).

Instead of $f(x, y, z)$ as you would in maths or in Java, you say `(f x y z)`. That would be replaced with whatever `f` returns. These can be nested. For example, to compose `f` with `g`, I could say `(f (g x))`.

Equality-testing (`=`) and plus (`+`) are just functions `(= (+ 3 2 5) 10)` would evaluate to 'true'. In the future, I will use `;>` to mean 'evaluates to'. Note that the semicolon begins a line-comment.

`if` is a syntax form that looks like a function that takes three arguments: a condition, a thing to do if true, and a thing to do if false.

```scheme
(if (= 3 (+ 1 2))
    "hello"
    "world") ;> "hello"
```

That's it for syntax. The rest is just functions and special-functions.

## `define`s

You can define immutable variables like

```scheme
(define x 3)
(+ x 10) ;> 13
```

You can define your own functions like:

```scheme
(define (foo x)
  (if (= x 0)
      "x is zero"
      "x is not zero"))

(foo 2) ;> "x is not zero"
```

## Lambda functions

Consider the function:

```scheme
(define (f-of-2-3 f)
  (f 2 3))
```

Notice that `f-of-2-3` takes a function as its argument and applies it to (2, 3). For example:

```scheme
(f-of-2-3 +) ;> 5
(f-of-2-3 *) ;> 6
(f-of-2-3 expt) ;> 8

(define (norm x y)
  (+ (* x x) (* y y)))

(f-of-2-3 norm) ;> 13
```

Note that `norm` is kind of verbose; it may be useful to define a function without having to explicitly name it. This is what `lambda`s are used for. First you say the names of the arguments, and then you write an expression in terms of those. This is consistent with the rules of lambda-calculus.

```scheme
(f-of-2-3
  (lambda
    (x y)                     ; this function takes in x and y
    (+ (* x x) (* y y))))     ; and returns x^2 + y^2
                              ; and that function gets sent into f-of-2-3
;> 13
```

Note that a `λ` may be used in place of the word `lambda`.

You should know about `let`.

```scheme
(let ([x 4]
      [y 2])
     (+ x y)) ;> 6
```

Some things are used so often that there are short-hand functions for them. Namely `(zero? x)` is the same as `(= x 0)` and `(sub1 x)` is the same as `(- x 1)`.

That's it. You're ready to go.

# Repeated functions

## Approximate the Golden-Ratio

If you start with $x = 1$, and repeatedly assign $x := 1 + 1 / x$, you will approach the Golden-Ratio, $\phi$.

```scheme
(define (φ-approx n)
  (if (zero? n)
      1
      (+ 1 (/ 1 (φ-approx (sub1 n))))))

;   1 + 1/(φ-approx 2)
; = 1 + 1/(1 + 1/(φ-approx 1))
; = 1 + 1/(1 + 1/(1 + 1))
(φ-approx 3) ;> 1 2/3
```

Now for that approximation of the Golden-Ratio.

```scheme
(φ-approx 20) ;> 1 6765/10946
```

Whoops. Racket is printing out the mixed-number  because decimals are inexact

```scheme
(exact->inexact (φ-approx 100))
;> 1.618033985017358
```

## Approximate the Golden-Ratio redux

It turns out a lot of things have the form:

> Let f(x) = blah. Then f(f(f(...f(x)...))) approaches some thing.

That "thing" is called "the [fixed-point](https://en.wikipedia.org/wiki/Fixed_point_(mathematics)) of f"

So I am going to write a function that will repeatedly apply a function a base-case, n-times `(repeat n base f)`. See if you can write this function, following the pattern of `φ-approx`.

```scheme
(define (repeat n base f)
  ; start with the if-statement like in φ-approx
  (if (zero? n)
      ; if we have hit the base case,
      base
      ; otherwise repeat n - 1 times, and do f of that.
      (f (repeat (sub1 n) base f))))
```

Now I'm going to test it with the Golden-Ratio approximation

```scheme
(define (φ-approx2 n)
  (define (f x) (+ 1 (/ 1 x)))
  (repeat n 1 f))

(exact->inexact (φ-approx2 20))
;> 1.618033985017358
```

## Fibonacci

Can you compute the Fibonacci series using repeat?

Hint: You can say `(list 4 5)` and `(first (list 4 5)) => 4` but `(second (list 4 5)) => 5`. The return value of `f` should be a pair, and we will repeat `f` `n` times.

Answer:

```scheme
(define (fibonacci n)
  ; I am defining a function inside another function
  ; That's ok. It works as you would expect.
  (define (f pair)
    (let* ([f_n   (first  pair)]
           [f_n+1 (second pair)]
           [f_n+2 (+ f_n f_n+1)])
      (list f_n+1 f_n+2)))
  ; now pass that into repeat
  (first (repeat n (list 0 1) f)))

(fibonacci 10) ;> 55
```

## Factorial

How about factorial? Use a pair as the fixed point again.

Hint: the return value should be $(m, n!/m!)$ and $m$ should decrease by one every function-call. When $m$ gets to 1, you would have $(1, n!)$

Answer:

```scheme
(define (factorial n)
  (define (f pair)
    (let ([n (first pair)]
          [prod (second pair)])
      (list (sub1 n) (* prod n))))
  (second (repeat n (list n 1) f)))

(factorial 6)
```

# The Y-combinator

What if the fixed-point itself is actually a function? Not a number or a list of numbers, but a function. You may be wondering what the practical application I'll get to that at the end.

Traditionally, the factorial function would be defined as

```scheme
(define (factorial2 n)
  (if (zero? n)
      1
      (* n (factorial2 (sub1 n)))))
```

But notice it also follows this pattern:

```scheme
(define (factorial3 n)
  (if (zero? n)
      1
      (* n (let ([n (sub1 n)])) ; do n times factorial of n-1
        ; copy-paste definition of factorial3 here.
        (if (zero? n)
            1
            (* n (let ([n (sub1 n)])
                   ; copy-paste definition of factorial3 here.
                   (if (zero? n)
                       1
                       (error "ran out of room."))))))))

(factorial3 0) ;> 1
(factorial3 1) ;> 1
(factorial3 2) ;> 2
(factorial3 3) ;> error: ran out of room
```

I could write a function that:

- takes in an `f`

- and evaluates to a function that takes in an `n`

- and if `n` = 0, evaluates to `1`

- otherwise evaluates `n` times the `(f (sub1 n))`

```scheme
(λ (f)
  (λ (n
      (if (zero? n)
          1
          (* n (f (sub1 n)))))))
```

Let's call that `recur-f`. Notice that `recur-f` *works on `recur-f`*.

That is, `(recur-f (recur-f (recur-f (recur-f ...[n-times]))))` would evaluate to a function that computes the factorial of any number less than n. If you put in a number greater than `n`, it runs out of `recur-f`'s.

```scheme
(define (factorial4 n)
  (let* ([base-f (λ (f)
                   ; since the fixed-point is a function, the base-case is a function as well
                   (error "ran out of room."))]
         [recur-f (λ (f)
                   ; Since the fixed-point is a function
                   ; recur-f gets to take in a function, f
                   ; which it can choose to call later on.
                   (λ (n)
                     (if (zero? n)
                         1
                         (* n (f (sub1 n))))))]
         ; since the fixed-point is a function
         ; (repeat ...) returns a function
         ; I want to save the function and call it later
         [constructed-f (repeat 10 base-f recur-f)])

    (constructed-f n)))

(factorial4 6) ;> 24
```

It works, except:

```scheme
(factorial4 11) ;> error: ran out of room
```

That is because I repeated recur-f 10 times. So eventually base-f was used as f in the expression `(f (sub1 n))`.

What if there was a version of repeat that repeated `f` as many times as were necessary to evaluate the computation? It would keep doing `(f (f (f ...)))` until the function's expression does not call `f` (i.e., recurses until the computation halts). That is, it would compute the "fixed-point" of `f`.

This is called it the [Y-combinator](https://en.wikipedia.org/wiki/Fixed-point_combinator) by the mathematician [Haskell Curry](https://en.wikipedia.org/wiki/Haskell_Curry), often named `fix`.

```scheme
(define fix
  (lambda (f)
    (f (lambda (x) ((fix f) x)))))
```

`(fix f)` evaluates to `(f (lambda (x) ((fix f) x)))`. From there, we have two cases: `f` uses its argument or it doesn't.

- If `f` uses its argument, its argument expands to `(lambda (x) ((fix f) x))`. This is how `(fix f)` calls itself.

- If `f` does not depend on its argument, (e.g., `(define f (lambda (unused-variable) constant))`), `(f foo)` need not evaluate `foo`. `f` simply returns `constant`. This breaks the otherwise infinite recursion.

Let's use this in our example:

```scheme
(define factorial5
  (fix
   ; This part is exactly the same as recur-f
   (λ (f)
     (λ (n)
       (if (zero? n)
           1
           (* n (f (sub1 n))))))))

(factorial5 6) ;> 120
```

`factorial5` is exactly like `factorial4`, but it is only bounded by the limitations of your hardware. It needs no base-f because `fix` keeps doing `recur-f` until the computation does not recurse. So it would ever reach the `base-f` (like an unbounded version of `factorial4`).

# Implications

You can define a complete programming language with just `λ` and parentheses (called lambda-calculus).

`define` is (most-of-the-time) just a convenience. I could replace every instance of `factorial5` with the literal definition of `factorial5`.

The exception is for recursive functions like `factorial2`.

```scheme
; Recall:
(define (factorial2 n)
  (if (zero? n)
      1
      (* n (factorial2 (sub1 n)))))
```

`factorial2` is used _in the definition_ of `factorial2`, so I could not replace it with its definition.  So it might appear that recursion is something
different—too complicated to be represented in lambda-calculus. If you think about it, **recursion depends on naming things**. You have to name it something so that it can call itself.

But the Y-combinator allows us to do recursion, functions that call themselves, without having to refer to the name of the function in its definition. **It gives us recursion without names**; Other theorems show that lambda-calculus is Turing-complete, as a result of the Y-combinator.

If you are writing a new programming language like lisp, the interpreter just needs to know how to evaluate lambda-expressions and the rest of it (if's and define's and for's) can be library-functions.

## Nash Equilibria

Suppose we are playing a 2-player game, where each player decides a strategy and always adheres to it.

Let `(f a b)` be a function that returns the pair containing player 1's optimal strategy assuming player 2 is using strategy `b`, and player 2's optimal strategy assuming player 1 is using strategy `a`.

Note: "`a` is a strategy" may be too abstract to understand. In some games, there is only 1 valid strategy, but it takes some real-valued parameter or parameters. To make it less abstract, think of `a` as player 1's chosen parameter. If player 2 knows player 1 chooses `a`, what should their paramter be?

The fixed-point of `f`, starting from some _a priori_ values is `((fix f) a-initial b-initial)`, and it is called a [Nash Equilibrium](https://en.wikipedia.org/wiki/Nash_equilibria). [John Nash](https://en.wikipedia.org/wiki/John_Forbes_Nash_Jr.) was awarded the 1994 Nobel Prize in Economics for his work showing that all games that meet some bare-bones criteria have a Nash Equilibrium. That is certainly not what I would have expected (details on [Wikipedia](https://en.wikipedia.org/wiki/Nash_equilibrium?oldformat=true#Existence)).

> The concept [of Nash Equilbria] has been used to analyze hostile situations such as wars and arms races (see prisoner's dilemma), and also how conflict may be mitigated by repeated interaction (see tit-for-tat). It has also been used to study to what extent people with different preferences can cooperate (see battle of the sexes), and whether they will take risks to achieve a cooperative outcome (see stag hunt). It has been used to study the adoption of technical standards, and also the occurrence of bank runs and currency crises (see coordination game). Other applications include traffic flow (see Wardrop's principle), how to organize auctions (see auction theory), the outcome of efforts exerted by multiple parties in the education process, regulatory legislation such as environmental regulations (see tragedy of the commons), natural resource management, analysing strategies in marketing, even penalty kicks in football (see matching pennies), energy systems, transportation systems, evacuation problems and wireless communications.

-- [Wikipedia on Nash Equilbirium](https://en.wikipedia.org/wiki/Nash_equilibrium)

## In Nix

Nix is a lazy functional programming language that is specialized for configuration management (that's the really short version). Nix uses fixed-point to enable action-at-a-distance, which is essential to its usefulness as a configuration management tool.

Before proceeding, I must briefly explain the parts of Nix syntax I will use (a guided tutorial on the rest of the syntax can be found [here](https://learnxinyminutes.com/docs/nix/)):

Nix uses `#` for line-comments and `/* ... */` for block comments, like an unholy mashup of Python and C. I will use `#>` for "evaluates to".
Lambda functions are denoted with a colon. Function calls are denoted a space, with parentheses for grouping.
```nix
double = x: x*2
double (double 3) #> 3*2*2 = 12
```

There isn't really a way to write a lambda function that takes multiple arguments; instead we just write a function that returns a function:

```nix
add3 = a: b: c: a + b + c
(add3 4) #> <<function looking for input>>
((add3 4) 5) #> <<function looking for input>>
(((add3 4) 5) 6) #> 10
add3 4 5 6 #> 10
```

Nix has syntax for associative arrays whose keys are strings:

```nix
my-array = {a = 2; b = 4;}
my-array.a #> 2

your-array = my-array // {c = 5; a = 4;}
/* double-slash "merges" the arrays */
your-array.c #> 5

/* note that the right-hand side of // "wins" in name conflicts */
your-array.a #> 4
```

Finally, we have let-statements.

```nix
(let
  a = 4;
  b = 5;
in a + b) #> 9
```

[Nix's standard library defines the Y-combinator](https://github.com/NixOS/nixpkgs/blob/f3a93440fbfff8a74350f4791332a19282cc6dc8/lib/fixed-points.nix#L75), calling it `fix`

```nix
fix = f: let x = f x; in x;
```

Suppose we have

```nix
f = self: { a = 7; b = self.a + 2; }
/* `self` is a good variable name for the thing we are doing */

(fix f).b #> 9
```

Then, `fix f` evaluates to `(f (f (f (f ...))))`, but in this case 3 levels are enough, since `(f (f f))` evaluates to `{ a = 7; b = 9; }` and this does not depend on `f`.

This example stolen from [Nix discourse](https://discourse.nixos.org/t/how-is-fixed-point-used-for-overriding-nixpkgs-packages/35476/4), where it is discussed more thoroughly.

One usecase is customizing the Nixpkgs. Nixpkgs is a huge associative array, where each element maps a package name to the recipe one would use to build it, called a *derivation*. Users may want to customize Nixpkgs by replacing or modifying some package.

You could naïvely replace individual packages: if you wanted to replace Firefox: `nixpkgs // { gcc = my-customized-gcc; }`. This strategy is not composable. Suppose one sysadmin modifies gcc (perhaps tuning it to your CPU family), one would have to replace *every* package that uses gcc in its compile stage. In systems software, we often deal with core inftrastructure packages like gcc or Python, where we can't enumerate (open world assumption) or don't want to enumerate (closed world, but too dang many!) every downstream package (e.g., changing glibc → Musl or Python → PyPy).

The solution, is of course, use the Y-combinator!

Let's suppose our default initial package set was a function from `fixed-point` to an associative array of package names to derivations:

```nix
initial-pkg-set = fixed-point: {
  gcc = stock-gcc;

  /* many apps use gcc in its compilation. */
  bash = some-compile-function fixed-point.gcc;
  htop = some-other-compile-function fixed-point.gcc;
};
```

That would be in stock Nixpkgs, which is not possible for our sysadmin to change in this example. Instead, our sysadmin would write an _overlay_. An overlay is a function of two arguments, which expects that its first argument is equal to its fixed-point, and its second argument is the initial value of Nixpkgs. Both arguments should be associative mappings of package names to derivation. For example:

```nix
gcc-overlay = fixed-point: initial-value: { gcc = my-customized-gcc }
```

Nixpkgs standard library also defines a helper function called [`extends`](https://github.com/NixOS/nixpkgs/blob/f3a93440fbfff8a74350f4791332a19282cc6dc8/lib/fixed-points.nix#L241C1-L254C7):

```nix

/*
  Arg `overlay` should be a function of 2 args, like the overlays we discussed above.
  Arg `f` should a function from the fixed-point to the "initial state".
  Arg `fixed-point` should be the fixed-point.
  We should just supply the first two arguments, and then send the result to `fix`, which will set and return the third argument.
*/
extends = overlay: f: fixed-point:
  let
    prev = f fixed-point;
  in
  prev // overlay fixed-point prev
;
```

And now, we can compose the package set with our overlay:

```nix
fix (extends gcc-overlay initial-package-set);
```

There's also a [compose for overlays in Nix's stdlib](https://github.com/NixOS/nixpkgs/blob/f3a93440fbfff8a74350f4791332a19282cc6dc8/lib/fixed-points.nix#L261C1-L265C36):

```
/* Just give two arguments (two overlays), and send the result to `extends`.
  The result is basically a single overlay that has the effect of doing both overlays, in order.
*/
composeExtensions =
  overlay1: overlay2: fixed-point: initial-value:
    let overlay1-applied = overlay1 fixed-point initial-value;
        after-overlay1 = initial-value // overlay1-applied;
    in overlay1-applied // overlay2 fixed-point after-overlay1;
```

When composing overlays, it is far more common to see the two arguments to the overlay called `final` and `prev`. `prev` is the result of all applying prior overlays, while `final` is the result of all overlays (including the current).

Overlays seem to defy a linear sense of time. There is a cycle in the dataflow graph, where the output to a function is also its input. It is as if we know what the output of the function is while we are computing the output of the function. But we are really just iterating the function over and over again until the we arrive at a fixed-point (if we ever do), at which point, the output equals the input.

![Dataflow graph of overlays](https://nixos.wiki/images/5/5f/Dram-overlay-final-prev.png)

Nix does all the fancy Y-combinator stuff behind the scenes. All a user does is supply a list of overlays in the order they want them applied.

In [the Nixpkgs manual](https://ryantm.github.io/nixpkgs/using/overlays/), the authors give the example of setting the default BLAS/LAPACK provider. The initial package set assigns a default value for `blas`; packages in the initial package set call `fixed-point.blas`; a sysadmin can write an overlay that redefines `blas`; Finally, NixOS will apply the overlay, and the right `blas` is provided.

For more details, see [this blog](https://blog.layus.be/posts/2020-06-12-nix-overlays.html).

## Gödel

With recursion, one can construct infinite-loops.

```scheme
((Y (λ (f) (λ (x) (f x)))) 2)
```

In `factorial5` we have, `(if (zero? n) 1 (* n (f (sub1 n))))`. Thus `factorial5` has a base-case when `n` is zero, `if`-condition is true and it does not recurse. No such base-case in the infinite-loop. It will recurse on itself for all of eternity trying to answer the question "what is f of 2?" by asking "what is f of 2?"

There are deductive systems based on lambda-calculus. You can form the sentence, "If this sentence is true, then X" ([Curry's paradox](https://en.wikipedia.org/wiki/Curry%27s_paradox)), and deduce X, for all X.

But if you think about it more, this all just goes back to Gödel.

Gödel says that if the computation-system is complete, it could infinite-loop, and exactly when it does loop is undecidable.

Gödel says that if the deductive-system is complete, it is contradictory.

# Epilogue

I hope that sparks your interest in theoretical computer science and programming in Lisp :

Let me know if you have any questions or suggestions to make it easier to read.

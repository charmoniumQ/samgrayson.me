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

In situations like this, it may be useful to define a function without having to explicitly name it. This is what `lambda`s are used for. First you say the names of the arguments, and then you write an expression in terms of those. This is consistent with the rules of lambda-calculus.

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
  (repeat n 1 f)))

(exact->inexact (φ-approx2 20))
;> 1.618033985017358
```

## Fibonacci

Can you compute the Fibonacci series using repeat?

Hint: You can say `(list 4 5)` and `(first (list 4 5)) => 4` but `(second (list 4 5)) => 5`. The fixed point should be a pair.

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

Hint: the fixed-point should be $(m, n!/m!)$ and $m$ should decrease by one every function-call. When $m$ gets to 1, you would have $(1, n!)$

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
      (* n (let ([n (sub1 n)]) ; do n times factorial of n-1
        ; copy-paste definition of factorial3 here.
        (if (zero? n)
            1
            (* n (let ([n (sub1 n)])
                   ; copy-paste definition of factorial3 here.
                   (if (zero? n)
                       1
                       (error "ran out of room.")))))))))

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
  (λ (n)
      (if (zero? n)
          1
          (* n (f (sub1 n))))
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

What if there was a version of repeat that repeated `f` as many times as were necessary for the computation? It would keep doing `(f (f (f ...)))` until the function's expression does not call f.

Note that when `n` = 3, it depends on `(f 2)` and that depends on `(f 1)` and that depends on `(f 0)`, but *that* does not call `f`.

I was not the first person to think of this. Haskell Curry was. He called it the [Y-combinator](https://en.wikipedia.org/wiki/Fixed-point_combinator).

```scheme
(define Y
  ((λ (f)
     (f f))
   (λ (z)
     (λ (f)
       (f (λ (x) (((z z) f) x)))))))
```

I must admit, don't fully understand the definition of it (which I got from Wikipedia); but I understand how to use it.

```scheme
(define factorial5
  (Y
   ; This part is exactly the same as recur-f
   (λ (f)
     (λ (n)
       (if (zero? n)
           1
           (* n (f (sub1 n))))))))

(factorial5 6)
```

`factorial5` is exactly like `factorial4`, but it is only bounded by the limitations of your hardware. It needs no base-f because Y keeps doing `recur-f` until the computation does not recurse. So it would ever reach the `base-f` (like an unbounded version of `factorial4`).

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

I hope that sparks your interest in theoretical computer science and programming in Lisp :)

Let me know if you have any questions or suggestions to make it easier to read.

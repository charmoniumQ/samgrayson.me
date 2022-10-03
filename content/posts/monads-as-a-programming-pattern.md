---
layout: post
title: Monads as a Programming Pattern
tags: [programming]
image:
  url: /raw-binary/monads-as-a-programming-pattern/toolbox.png
  alt: A carpentry toolbox with tools.
  attribution:
    url: https://www.maxpixel.net//Toolbox-Handyman-Construction-Tools-Builder-3411589
    text: CC0 Public Domain via Max Pixel
teaser: >
  This article is written from a programmer's perspective, where a monad is a <i>software engineering pattern</i>. It's just another tool for your box.
date-published: 2019-08-06
other_routes:
  - 2019-08-06-monads-as-a-programming-pattern/index.html
---

## Overview

This article is written from a programmer's perspective, where a monad is a [_software engineering pattern_](https://en.wikipedia.org/wiki/Software_design_pattern). Like other patterns, you may have already used it without knowing it was the monad pattern. There is still  value in studying such patterns, because then you can use it more fluidly. There is a mathematical [category-theory definition](https://ncatlab.org/nlab/show/monad), but you can use them effectively without understanding that (so don't @ me, Brendan).

**Imprecise definition:** A monad is a type that wraps an object of another type. There is no direct way to get that 'inside' object. Instead you ask the monad to act on it for you. Monadic classes are a lot like classes implementing the [visitor pattern](https://en.wikipedia.org/wiki/Visitor_pattern), but monads are capable of returning something wrapped in another monad. This essential property makes functions on monads composable. I'll get to a precise definition after you understand the imprecise one through some examples.

## Examples

### Maybe/Nullable/Optional monad

Our first example is Maybe. I will write its interface in pseudocode resembling Java.

```java
class Maybe<T> {
    static Maybe<T> Nothing;
    static Maybe<T> Some(T value);
    Maybe<V> apply(Function<T, Maybe<V>> func);
}
```

As promised, the Maybe monad can contain another object, and we can ask it to act indirectly. Notice that apply doesn't take a function from `T -> V`, but rather from `T -> Maybe<V>`. It unboxes the inside object, executes the function and returns the new box. This allows monads to be chained together.

```java
// Let's assume getInput asks the user for input,
// and returns Some(value) if the user enters a valid value.
// Otherwise it returns Nothing.

Maybe<int> wrappedA = getInput();
Maybe<int> wrappedB = getInput();
Maybe<int> wrappedRatio = wrappedA.apply((int a) -> {
    wrappedB.apply((int b) -> {
        // maybeDivide returns a Maybe<int>
        // because if the denominator is zero, it returns Nothing.
        return maybeDivide(a, b);
    });
});
```

If `apply` took `T -> V`, this would evaluate to a `Maybe<Maybe<int>>`, which quickly becomes unwieldy. Also note that a function `T -> V` can still be used; just compose it with `Some`:

```java
// let func: T -> V
result = wrapped.apply((T a) -> Some(func(a)));
// result is Maybe<V>, as desired
```

### List/Collection monad

In the previous example, you might think a monad is just an interface for [aggregating (in the OOP sense)](https://en.wikipedia.org/wiki/Object_composition#Aggregation) another object, but here is a monad that is more general than that.

```java
class Collection<T> {
    // makes collection containing one element
    static Collection<T> makeCollection(T initialElement);

    // runs func on every element and concatenates the results
    Collection<V> flatMap(Function<T, Collection<V>> func);


    // runs func on every element
    Collection<V> map(Function<T, V> func) {
        // implemented by calling flatMap
        flatMap((T element) -> makeCollection(func(element)));
    }
}
```

Instead of calling the operator `apply`, I called it `flatMap` as [the name is well-known](https://stackoverflow.com/questions/26684562/whats-the-difference-between-map-and-flatmap-methods-in-java-8). Again, `flatMap` is more general because it can implement `map`, but not the other way around (you'd need `map` **and** something like Python's [`itertools.chain.from_iterables`](https://docs.python.org/3.7/library/itertools.html#itertools.chain.from_iterable)).

### Promise/Awaitable monad

In the previous two examples, you may have wanted a method that exposes the wrapped value(s), maybe `getValues`. The whole point of the monad pattern is to avoid that urge, and . It's like [data-hiding (in the OOP sense)](https://en.wikipedia.org/wiki/Information_hiding). Instead of accessing elements directly, you chain on your computations through `apply`/`flatMap`/`then`. The Promise monad is an example where you physically can't ask for the wrapped values, because it might not exist yet! [A common question](https://stackoverflow.com/q/45378267/1078199) is how to get the value _out_ of the promise for subsequent computation, but the answer is instead to put the subsequent computation _into_ the promise, using `.then`.

```java
class Promise<T> {
    static Promise<T> makePromise(T value);
    Promise<V> then(Function<T, Promise<V>> func);
}
main() {
    Promise<int> sum = getInput().then((int x) -> {
        return getInput().then((int y) -> {
            // this would be cleaner with Promise.all
            // but that would obfuscate the point I am trying to make here
            return makePromise(x + y);
        });
    });
}
```

Streams naturally arise as well; They are just promises that get `resolve`d multiple times.

## Precise definition

Borrowing heavily from [Wikipedia](https://en.wikipedia.org/wiki/Monad_(functional_programming)#Definition), a monad is three things&hellip;

- A generic type `M` .
- A function, often called `wrap`, `of` ([JS fantasy-land](https://github.com/fantasyland/fantasy-land)), or `return` ([Haskell](https://downloads.haskell.org/~ghc/latest/docs/html/libraries/base-4.12.0.0/Control-Monad.html#v:return)), with signature is `T -> M<T>`. In my examples this is, `Maybe.Some` , `Collection.makeCollection`, and `Promise.makePromise`. This convertor takes a regular value and wraps it in a monadic one.
- A combinator, often called `bind`, `chain` ([JS fantasy-land](https://github.com/fantasyland/fantasy-land)) or spelled as an infix operator, `>>=` ([Haskell](https://downloads.haskell.org/~ghc/latest/docs/html/libraries/base-4.12.0.0/Control-Monad.html#v:-62--62--61-)), with signature `(M<T>, T -> M<V>) -> M<V>`. In my examples this is, `Maybe.apply` , `Collection.flatMap`, and `Promise.then`. This combinator unwraps the monad, does an operation, and returns the monad of the result.

&hellip; that respects these three laws&hellip;

- `wrap` is the left-identity of `bind`: `wrap(a).bind((T x) -> f(x))` evaluates to the same thing as `f(a)`. This means that `wrap` really just packages its input into a container.
- `wrap` is the right-identity of `bind`: `monadicObj.bind((T x) -> wrap(x))` evaluates to the same thing as `monadicObj`. This means that `bind` really does unwrap the container properly, accessing the insides.
-  `bind` is associative:

```java
monadicObj.bind(
                (T x) -> f(x).bind(
                                   (T y) -> g(y)))
```

evaluates to the same thing as

```java
monadicObj.bind((T x) -> f(x))
          .bind((T y) -> g(y))
```

This last law is why people like Promises; they turn horizontally [nested callbacks into vertically chained callbacks](https://medium.com/@justintulk/flattening-nested-promises-in-javascript-88f04793ded7), saving us from the [Pyramid of Doom](https://en.wikipedia.org/wiki/Pyramid_of_doom_(programming)):

<a href="https://qr.ae/TWvqL3">
<img src="/raw-binary/monads-as-a-programming-pattern/pyramid_of_doom.png" alt="pyramid of doom" />
</a>

These laws let me write functions that will work with _any_ monad. For example, I mentioned implementing `map` on some specific monads. Now I'll implement it for all monads that follow the monad-laws.

```java
// I'll assume that all monads in this language implement the interface Monad<T>

Monad<V> map(Monad<T> input, Function<T, V> func) {
    return input.bind((T elem) => Monad.wrap(func(elem)));
}
```

### Category Theory

The concept of monads comes from [category theory](https://en.wikipedia.org/wiki/Monad_(category_theory)). Their use in computer programming was first explicated rather recently, in 1989 ([CiteSeerX 10.1.1.26.2787](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.26.2787)). The monad has friends which are also borrowed into programming: monoids, functors, and applicatives. Although the math is important and valuable I think the monad pattern can be used effectively without knowledge of category theory, just as a programmer can effectively use the `lambda`-functions without understanding [λ-calculus](https://en.wikipedia.org/wiki/Lambda_calculus). The concept from category theory is just inspiration. The laws I stated above are enough for program-correctness.

If a construct does not satisfy the monad laws, it technically isn't a monad, but it might still be monad-inspired. In most JS libraries, `.then` can take `A -> Monad<B>` AND `A -> B` (not monad-compliant). This design choice breaks associativity for objects with a property named `then` ([1](https://stackoverflow.com/a/45772042/1078199), [2](https://stackoverflow.com/a/50173415/1078199)). This is not necessarily wrong or bad. I personally find it a pragmatic decision that often simplifies code, even though it is less theoretically nice. [Some JS libraries](https://github.com/briancavalier/creed) do fit the mathematical monad bill. Even Haskell's so-called `IO Monad` [may not even be a proper category-theory monad](https://www.quora.com/How-would-you-explain-a-concept-of-monads-to-a-non-CS-person).

## Syntax

`bind` is so commonly used that Haskell has special syntax for it: [do-notation](https://en.wikibooks.org/wiki/Haskell/do_notation). Python, JavaScript, and Rust have this [syntactic sugar](https://en.wikipedia.org/wiki/Syntactic_sugar) as well, but in disguise as I will show you shortly.

### Haskell's do-notation

```haskell
-- remember `>>=` in Haskell means `.bind` in Java,
-- and `\x ->` is the start of a lambda, like `((T x) ->` in Java.
monadicObj >>= \varName -> doStuff(varName)
```

is [semantically equivalent](https://en.wikipedia.org/wiki/Semantics_(computer_science)) to

```haskell
do {
    varName <- monadicObj;
    doStuff(varName)
}
```

So a program that gets to integers written using the vanilla syntax looks like this:

```haskell
-- x and y are just regular ints (remember the signature of >>= (AKA bind)).
getInput >>= \x -> 
              getInput >>= \y ->
                  return (x + y)
                  -- We have to return a monad<int>
                  -- (remember the signature of bind)

-- Remember that `return` is not a keyword in Haskell; just a regular function
-- It refers to the function that wraps a regular value in a monad.
```

And this is the semantically equivalent using do-notation:

```haskell
do {
    x <- getInput;   -- Everything after here goes after: getInput >>= \x -> ...
    y <- getInput;   -- Everything after here goes after: getInput >>= \y -> ...
    return x + y
    -- x and y are just regular ints, not wrapped ints.
}
```

It is a weird transformation, but you can see its utility: we can---to some extent---forget that `getLine` returns wrapped values; `x` is just a regular `int`. This makes writing monadic code as natural as operating on regular values.

### State

Note that `getInput` is a pure function: it takes a function of type `Int -> Void` and calls it with an argument and returns `void`. Although the returned value is always the same (`void`), the argument it passes could be different in subsequent calls. This is how we can model what would otherwise be a non-deterministic function in a pure-functional way. Pure functional programming languages represent [the whole outside world](https://en.wikibooks.org/wiki/Haskell/Understanding_monads/IO#The_universe_as_part_of_our_program) as a monadic context. Programs just bind computation onto this context.

### Control-flow

Monads are often called [programmable semicolons](http://www.thisurlisfalse.com/programmable-semicolon-monads-in-haskell/), because the monad's `bind` controls the subsequent computation.

```haskell
list = [1, 2, 3]
squares = do {
    x <- list;
    -- the List monad controls the code at this point
    -- in fact, it runs once for each element in the list.
    return [x**2]
}
```

This allows for complex control-flow operations (such as coroutines) to be implemented at the user-level in a monad instead of the language-level. Languages without do-notation have to bend over backwards to emulate it in specific cases, as we will see.

### C#/Python/JavaScript await keyword

The `await` keyword in other languages emulates do-notation for Promise monads. Consider JavaScript's [`await`](https://javascript.info/async-await); It makes everything after the `await` the body of a function that is inputted to `.then`.

```javascript
async function func() {
    return getInput.then((x) =>
        getInput.then((y) =>
            makePromise(x + y)
        )
    );
}
```

is equivalent to:

```javascript
async function foo() {
    x = await getInput();
    y = await getInput();
    return x + y;
}
```

`await` in Python and other languages does this too---but it is less apparent because callback-based promises are less prominent in those language communities. What do-notation does for all monads, `await` does for `async` monads: it makes writing asynchronous code almost as natural as writing synchronous code.

### Rust question-mark operator

Rust does [not have exceptions](https://doc.rust-lang.org/book/ch09-00-error-handling.html) (!), so you might think error-handling would be painful; you would have to anticipate failure at every possible failure point.

Rust has a [question-mark operator](https://m4rw3r.github.io/rust-questionmark-operator) which emulates do-notation for their `Option` monad (which is also known as `Nullable` or `Maybe` in other languages). The question-mark operator makes the lack of exceptions palatable. It lets us call functions which might not succeed with impunity.

We must explicitly handle every error:

```rust
fn foo() -> int {
    let wrappedA = trySuspiciousOperation();
    // Maybe you don't know Rust.
    // Just know that this is called "pattern matching on a tagged union."
    // It asks if wrappedA looks like Some(_) or Nothing.
    match wrappedA {
        Some(a) => {
            let wrappedB = trySuspiciousOperation();
            match wrappedB {
                Some(b) => {
                    return Some(a + b);
                }
                Nothing => {
                    return Nothing;
                }
            }
        }
        Nothing => {
            return Nothing;
        }
    }
}
```

However, we can rewrite the code like this:

```rust
fn foo() -> Option<int> {
    let a = trySuspiciousOperation()?;
    let b = trySuspiciousOperation()?;
    return a + b;
}

// Even this code is non-idiomatic; do not emulate
```

As you can see, these language features are just special cases of the more general do-notation. There is [a proposal to incorporate do-notation into Rust](https://varkor.github.io/blog/2018/11/10/monadic-do-notation-in-rust-part-i.html). Since Rust has a different semantic model than Haskell, there are devils in multiple details of the proposal.

## Looking forward

Here are some ways of thinking about monads. There are other ways to think about monads; I just picked three that make sense to me and seem exhaustive.

1. Sometimes the monad acts like a container of another type, as in the Collection monad. This is why some people emphatically exclaim eureka's like "a monad is just like [a burrito](https://blog.plover.com/prog/burritos.html)", "[a spacesuit](http://telofy.soup.io/post/23797479/Think-of-a-monad-as-a-spacesuit)", or "[a burrito in a spacesuit](https://www.reddit.com/r/haskell/comments/1bymg1/monads_are_burritos_in_spacesuits_full_of_nuclear/)." These people miss that it can be anything else; in many use-cases the monad can't simply 'contain' it. While the authors might understand this, a novice reader likely won't.
2. In these non-containing use-cases, the monad can act like a potential for there being a value, kind of like a Promise. Often monads in this case have the same semantics as "[continuations](https://en.wikipedia.org/wiki/Continuation-passing_style)" or callbacks: I don't have the value, but I can have the guy who does call (haha) you.
3. Sometimes a monad can act like the context for data. This last case is used in functional programming languages to isolate impure side-effects of functions. `getLine` in Haskell returns a `string` in an [`IO`](https://en.wikibooks.org/wiki/Haskell/Understanding_monads/IO) monad. Perhaps you would have a Thread monad, that represents thread-local data (the thread is context for the data). You can't operate on the data because it is not in your thread, but you can ask the other thread to operate on it for you. I chose not to elaborate examples of this use-case because it is less applicable outside of ML-family languages.

Now you know the pattern. It is useful to recognize in the wild, and it is a good tool in the box.

### Maybe this explanation is bad

It seems everyone who learns about monads goes through [this cycle](https://stackoverflow.com/a/19551168/1078199):

> 1.  person X doesn't understand monads
> 2.  person X works long and hard, and groks monads
> 3.  person X experiences amazing feeling of enlightenment, wonders why others are not similarly enlightened
> 4.  person X gives horrible, incomplete, inaccurate, oversimplified, and confusing explanation of monads to others which probably makes them think that monads are stupid, dumb, worthless, overcomplicated, unnecessary, something incorrect, or a mental wank-ercise

It happens so much, there are names for it: some call it [The Curse of the Monad](https://www.youtube.com/watch?v=dkZFtimgAcM), others [The Monad Tutorial Fallacy](https://byorgey.wordpress.com/2009/01/12/abstraction-intuition-and-the-monad-tutorial-fallacy/). There is even the meme "monads are just monoids on the category of endofunctors; What part of that don't you understand?"

It took me three tries over the past five years to understand monads. Of all the presentations I had read,

1. None made it feel like an abstraction of a programming pattern.
2. None pointed out how I was already using monadic-inspired constructs in my code.
3. None pointed out the connection with `await`.

The first point was a pragmatic choice to emphasize the utility of a monad, and the latter two are ways of connecting it to things the reader probably already understands.
I acknowledge that this article probably won't help most people because I might not be good at explaining how I learned this thing, and there is a large possibility that I don't have the same learning style as you. However, I do hope the act of reading it inspires an original thought in at least a few readers or even one; That will make all this worthwhile.

## Further reading
- [You Could Have Invented Monads! (And Maybe You Already Have.)](http://blog.sigfpe.com/2006/08/you-could-have-invented-monads-and.html) This is the best tutorial I have read through for its brevity and the challenges it gives the reader.
- [Monad tutorials timeline](https://wiki.haskell.org/Monad_tutorials_timeline) This is a somewhat opinionated list of many blogposts like this one. Given the variety of pedagogical choices, there is likely one that is suited to your learning style.
- [Wikibooks Haskell/Category Theory](https://en.wikibooks.org/wiki/Haskell/Category_theory) This is more technical, delving into the actual category theory. [A different chapter](https://en.wikibooks.org/wiki/Haskell/Applicative_functors#A_sliding_scale_of_power) draws a progression from functors to applicatives to monads. The series is great if you want a deeper dive.
- [Category Theory for Programmers](https://bartoszmilewski.com/2014/10/28/category-theory-for-programmers-the-preface/) I've only the first half, but this seems like the most complete way to learn this while keeping ones sanity (as opposed to reading a math book on category theory).

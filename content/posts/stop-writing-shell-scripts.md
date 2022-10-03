---
layout: post
title: Stop writing shell scripts
tags: [programming]
image:
  url: /raw-binary/stop-writing-shell-scripts/moneyball.png
  alt: "Billy Bean classifies programming languages: “There're strongly typed languages, weakly typed languages, fifty feet of crap, and then there's shell.”"
  attribution:
    text: own work
date-published: 2021-01-01
other_routes:
  - /2021-01-01-shell/index.html
teaser: >
  UNIX shell isn't a real programming language, so stop using like one!
---

UNIX shell isn't a real programming language, so stop using like one!

Don't get me wrong, shell is extremely useful and powerful. However, it is less _maintainable_ than scripts written in real programming languages. If you can afford to baby-sit the task and don't need it to be maintainable, then shell scripts are a fine choice.

The distinguishing factor between these "real" programming languages and shell, for the purposes of this article, is the ability to define datatypes. As Billy Beane famously remarked, "There are strongly typed languages and weakly typed ones [both permit user-defined datatypes]; Then there's 50 feet of crap, and _then_ there's shell."

<img src="/raw-binary/stop-writing-shell-scripts//moneyball.png" />

A cornerstone of UNIX wisdom is that "plaintext is the universal interface." Hence, it is not strongly typed; it's _stringly_ typed.
- After all, floats, ints, strings can all be encoded as strings.
- Lists of such can be colon-separated (like `$PATH`), space-separated (like shell arguments), tab-separated (like `ls -l $file`), or line-separated (like `find`).
- Lists of lists of such can be represented as a line-separated list of tab-separated lists (like `ls -l`).
I call these _simple datatypes_. Representing _complex datatypes_ is done on an even more ad hoc basis.

### Simple datatypes

Even within simple datatypes, life is hard: if `var="name with space"`, then `command $var` expands to `command name with space` (`$var` is a makeshift list) rather than `command "name with space"` by default, when the programmer usually intends the latter. While this behavior can be avoided with quotes around `"$var"`, this default makes it easier to write shell scripts incorrectly in a way you won't notice until you try a specially-crafted string.

Quoting does not even solve the problem completely. Suppose `var='a "b c"'`. Then `"$var"` expands to one argument (`a "b c"`), while `$var` expands to three (`a`, `"b`, and `c"`). According to the all-knowing [Stack Overflow](https://superuser.com/questions/1066455/how-to-split-a-string-with-quotes-like-command-arguments-in-bash), there is no variant which expands to two arguments (`a` and `b c`) short of writing your own lexer in shell or calling `eval`.

A [defender of shell](https://news.ycombinator.com/item?id=8442467) says "We should strive to build our software... so that exceptions like a filename with an odd character in it just don't exist. Until we reach that point, computers will continue to frustrate their users for no good reason." But there **is** a better way! It's using a real programming language.

The thorns of shell programming infect the rest of the system. For example, `$PATH` contains a colon-separated list-of-strings. What if one of those strings needs to have a colon in it? `scp` also uses a colon to separate two elements of a pair (the hostname and the path), but what if the filename contains a colon? Colon is technically [a reserved character](https://en.wikipedia.org/wiki/Filename#Comparison_of_filename_limitations), but this reservation is (usually) not checked when creating a file--apparently the system prefers to silently fail later on instead.

Good luck using a string in shell to hold non-trivial encodings or binary data.

### Complex datatypes

Complex datatypes are even more ad hoc. While Zsh and Bash _do_ have arrays and associative arrays, there is no way to pass them between functions or compose them (no array of arrays). Perhaps, the designers of shell did not envision so many tools requiring complex datatypes. But today, a plethora tools I use regularly do. Instead of plaintext, many newer tools (`kubectl`, `gcloud`) often have an option to output structured data as JSON to losslessly emit data for a real programming language.

The shell's inability to natively represent datatypes affects how people think about the rest of the system. For example, how should the kernel communicate complex datastructures to userspace? Influenced by shell, which can't define data structures, many Unices use the filesytem ([sysfs](https://en.wikipedia.org/wiki/Sysfs) and [procfs](https://en.wikipedia.org/wiki/Procfs)) to communicate structured data. Unfortunately, over the years this has accumulated [a plethora of different ad hoc representations](https://lwn.net/Articles/378884/) in Linux, and it is nearly impossible to [take a consistent snapshot](https://lwn.net/Articles/356152/) of the data.

I have a friend who says any system operation I can do in Python, he can do in an `awk`/`sed` one-liner. As a one-off command, I understand that's a useful skill. But if you need to do this task in a stored procedure, this is the _least_ maintainable option. If anyone needs to tweak the task (including the original author after one month), they usually have to figure out what it does and _rewrite another one_, hopefully in a real language this time.

Even [Eric S. Raymond](https://en.wikipedia.org/wiki/Eric_S._Raymond), classic UNIX hacker, weighed in against shell:

> As a general scripting language shell sucks *really badly* compared to anything new-school. Performance, portability, you name it, it's a mess.  It's not so much the shell interpreters itself that are the portabilty [sic] problem, but (as Magnus implicitly points out) all those userland dependencies on sed and tr and awk and even variants of expr(!) that get dragged in the second you try to get any actual work done.
>
> Some old-school Unix habits have persisted long past the point that they're even remotely sane.  Shell programming at any volume above a few lines of throwaway code is one of them - it's *nuts* and we should *stop doing it*.
>
> Eric S. Raymond in [LWN](https://lwn.net/Articles/527308/)

### Knuth vs McIlroy is orthogonal to ditching shell

Someone is bound to mention the famous spar between Doug McIlroy and Donald Knuth (much has been written regarding this: [summary](http://www.leancrew.com/all-this/2011/12/more-shell-less-egg/), [Knuth was framed](https://buttondown.email/hillelwayne/archive/donald-knuth-was-framed/), [Knuth wasn't framed](https://www.spinellis.gr/blog/20200225/), [HN debate](https://news.ycombinator.com/item?id=18699718)). Donald Knuth was asked to compute word frequencies from its input ("a" => 10, "the" => 7, "them" => 3, ...). He wrote a 6-page Pascal program from scratch and invented a novel datastructure. Doug McIlroy wrote a 6-line shell program which did the same thing.

```shell
tr -cs A-Za-z '\n' |
tr A-Z a-z |
sort |
uniq -c |
sort -rn |
sed ${1}q
```

The transferrable point of McIlroy's comment was that Knuth built everything from scratch to maximize asymtotic performance, while McIlroy wrote an equivalent although less performant solution by cobbling together existing tools. Nothing about it is inherent to shell or pipes. I would offer this Python program:

```python
import sys, collections, re
N = int(sys.argv[1])
text = sys.stdin.read()
words = re.findall("[a-z]+", text.lower())
counter = collections.Counter(words)
print(counter.most_common(N))
```

I believe it carries the same lesson from McIlroy's solution (since it reuses tools: [regular expressions](https://docs.python.org/3/library/re.html) and [collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter)), but unlike McIlroy's solution, it's easier to read, easier to modify (try making it split words containing apostrophes more intelligently), gives better error messages (try passing in a non-integer argument), and it's about [4 times faster](https://stackoverflow.com/a/56958255/1078199).

### Poor datatypes implies poor programming-language constructs

Not everyone likes exceptions, but you have to agree a _stacktrace_ is useful (for example, pass a non-integer argument to the previous program). Shell by default doesn't even stop for errors, and if you unset that default (`set -e`), it doesn't tell you what line errored out. You have to enable printing all lines (potentially many!) with `set -x` to get remotely useful diagnostics.

It is difficult to do parallelism in shell. Because shell is based on fork-and-exec, there is no such thing as lightweight thread-level parallelism. As for process-level parallelism, you've got the option to manually pass around pids (`command & ; pid="${!}"`), use `xargs`, or use [GNU Parallel](https://www.gnu.org/software/parallel/). It's only fun for the very simplest kinds of problems.

In many shell expressions, undefined variables behave the same as the empty-string (no datatype to represent `null`). This has led to horrible bugs that delete [the whole home directory](https://github.com/valvesoftware/steam-for-linux/issues/3671).

Lack of datatypes implies the inability to statically **or** dynamically check types. Even Python can emit type-errors dynamically.

And all variables are a global by default??

# Actionable Advice

1. Stop writing shell scripts! Instead reach for a _real_ language like Python. You can still benefit from reusing software, but at a language-level.

2. Write functions instead of scripts, function parameters instead of script arguments, `return` instead of `echo`, and objects instead of stringified data. This makes your software easier to reuse than a shell script.

3. If you have to call out to shell, bubble-wrap the shell command in a regular function. This is good software engineering, it permits you to switch to a native API call later on, and `clang(..., debugging_symbols=True)` is far more readable than `clang ... -g` if you don't remember what `-g` stands for.

    ```python
    def clang(
            sources: List[Path],
            executable: Path = Path("a.out"),
            includes: List[Path] = [],
            libs: List[str] = [],
            optimizations: Mapping[str, bool] = {},
            opt_level: Union[int, str] = 0,
            debugging_symbols: bool = False,
    ) -> None:
        subprocess.run([
            "clang",
            *sources,
            *[f"-I{include}" for include in includes],
            *[f"-l{lib}" for lib in libs],
            *[
                "-f" + ("" if enabled else "no-") + optimization.replace('_', '-')
                for optimization, enabled in optimizations.items()
            ],
            f"-O{opt_level}",
            *(["-g"] if debugging_symbols else []),
            "-o", executable,
        ])
    ```

4. If you _have_ to talk to some other program by a command-line interface,

    - Implement a language-level interface first, and then a command-line interface that sanatizes the inputs and calls into the language-level interface. It's good software engineering practice, and it also gives other programs the option of composing at the language-level. I like to use [`click`](https://click.palletsprojects.com/en/7.x/) for the CLI.

    - Add a `--output={json,text,auto}`. `json` is good if the other program is written in a real programming language (they can just `json.load(sys.stdin)`). It also permits using [`jq`](https://stedolan.github.io/jq/) to slice-and-dice the JSON instead of `sed`/`awk` to slice-and-dice the text. `auto` can decided between them by checking if stdin is a TTY. Many UNIX tools already do something analogous to decide if they should colorize the output.

    - stderr can be plaintext---that is probably going to be read by a human.

    - Don't use raw `print`s. You can use [tqdm](https://tqdm.github.io/docs/tqdm/), [logging](https://docs.python.org/3/howto/logging.html#logging-basic-tutorial), [warnings](https://docs.python.org/3/library/warnings.html), and exceptions instead. This makes it easier to gracefully reuse your code in another project.

    ```python
    # Language-level interface
    def do_cool_thing(args):
        ...
    
    def print_cool_thing(thing):
        ...

    # Command-line interface
    if __name__ == '__main__':
        # importing typer here permits clients to use the
		# language-level interface without installing typer.
        import typer
    
        # typer parses a CLI options and generates `--help` text
        # and parses args for us
    
        def main(n: int, input: Path, fmt: str = "auto"):
            if format == "auto":
                format = "text" if sys.stdout.isatty() else "json"

            result = do_cool_thing(...)

            if format == "json":
                json.dump(sys.stdout, result)
            elif format == "text":
                print_cool_thing(result)
            else:
                raise ValueError(f"Unrecognized format: {format}")
    ```

5. Packages are the only piece I don't have a good strategy for yet. Here are the strategies I have tried:

    - Using a shebang that activates your environment, e.g. [Nix Shebang](http://iam.travishartwell.net/2015/06/17/nix-shell-shebang/), [Pipenv shebang](https://pypi.org/project/pipenv-shebang/). This is probably the best option.

    ```shell
    #! /usr/bin/env nix-shell
    #! nix-shell -i python3 -p python3 python34Packages.pygobject3 libnotify gobjectIntrospection gdk_pixbuf
    import gi
	```

    - `try` importing a package, and if that fails tell the user what to install. This option is only feasible for a few dependencies.

    - Using a runner like [pipx](https://pypa.github.io/pipx/). This is clumsy for frequently used scripts because you have to write `pipx` before them.

    - Using `virtualenv` (perhaps managed by Pipenv or Poetry). You can activate the env from within the script by writing `sys.path.insert(0, ...)` (if you can assume the user has the right version of Python). It's kind of ugly.

    - Using `cx_freeze` to compile your script into an executable.

6. More advice regarding the CLI can be found at [clig.dev](https://clig.dev/).

I've implemented these ideas in many projects, including my most recent: [ILLIXR](https://illixr.github.io/). We used to have a shell script to build-and-run the system, then a `Makefile`, and then I upgraded it following the guidelines in this section to a [launcher script](https://github.com/ILLIXR/ILLIXR/tree/master/runner/runner/main.py). The script makes it far easier to launch ILLIXR different configurations programatically.

### Cons of a Real Language

- I must concede that the UNIX REPL, despite its warts, is efficient for those who invest time in it. It is useful to build a script out of commands one can test at a REPL.

  - Perhaps real-language REPLs will become more ergonomic (like [Xonsh](https://xon.sh/)), and satisfy the need for rapid prototyping while using real datatypes.

- Python is far more complex and difficult to implement from scratch than a shell.

- Python scripts are somewhat less portable since they depend on Python, but they are also somewhat more portable since Python is a compatibility layer over the underlying OS (most Python scripts are trivially Windows and UNIX compatibile!).

- It may be less debuggable, because the intermediates are not human-readable plaintext.

  - This can be partly mitigated in two ways: In a language context, one can give objects a printable representation with`__str__/to_string` (often defined automatically); between processes, one can change`--format=json` to `--format=text`.

- Writing small shell utilities makes it easier to interact with other languages. Perhaps, _this_ is Doug McIlroy's vision. Not just reusing software but doing so at the CLI-level rather than language-level.

  - This can be partly mitigated by writing a language-interface first and a shell-interface on top. This is common practice, as demonstrated by [tqdm](https://tqdm.github.io/), [Pyserial's miniterm](https://pyserial.readthedocs.io/en/latest/tools.html#module-serial.tools.miniterm), [jinja-cli](https://pypi.org/project/jinja-cli/), and [`http.server`](https://docs.python.org/3/library/http.server.html).

### A new vision for shell?

The case against using the UNIX shell as a REPL is less clear cut. Most of my arguments regarding maintainability and edge-cases carry less weight at the REPL since they only have to work once, under an engineer's supervision. Any change to the shell threatens the existing repertoire of "muscle memory," honed over decades. But even only as a hypothetical consideration, it is worth imagining what shell _could_ be if it supported datatypes natively.

Inventing a language is hard work, so why not reuse an existing one? Most existing languages are a bit too verbose, butone can write a front-end with syntactic sugar. This is exactly what [Xonsh](https://xon.sh/) does for Python and [Ammonite](http://ammonite.io/#Ammonite-Shell) does for Scala. Although the resulting syntax may resemble UNIX shell, real datatypes are flowing through the pipes. See [Beyond Bash](https://docs.google.com/presentation/d/11vZzXCfAA0aOFAuHA0nAvAzALGFGCH-dqHxx6XMgbk8) for an exposition of this philosophy by Ammonite's creator.

A more revolutionary approach is to fulfill the vision of shell, but in a modern context with datatypes. This is what PowerShell tries to be.

> I originally took the UNIX tools and made them available on Windows, and then it just didn't work. Right? Because there's a core architectural difference between Windows and Linux. On Linux, everything's an ASCII text file... In Windows, everything's an API that returns structured data... I came up with this idea of PowerShell... It's a pipeline of objects and with the objects, you know, there's none of the prayer-based parsing.
>
> --Jeffrey Snover in an interview with [To Be Continuous](https://www.heavybit.com/library/podcasts/to-be-continuous/ep-37-the-man-behind-windows-powershell/)

# Discussions

This is not an original idea, but I think my presentation of it is unique.

- [This HN thread](https://news.ycombinator.com/item?id=3329668) is particularly prescient. 
  - `jhpriestley` reads McIlroy's point about composition specifically to shell, while I would say that reusing language libraries is "composition" as well.
  - `nwmcsween` says exactly what I was thinking, "Composition should be of libraries or algorithms not arbitrary black box programs with n different options". But I would amend this to say that black-box composition is a _fallback_ if you have to go between languages and don't have enough time to write a native API.

- Ted Kaminski applies a similar critique [to UNIX philosophy](https://www.tedinski.com/2018/05/08/case-study-unix-philosophy.html) more broadly; he says what I am trying to far more generally and eloquently. I have chosen to focus my ire on just shell scripts because I hope to make more progress arguing the most narrow, concrete, and practical point first.

- [This HN Thread](https://news.ycombinator.com/item?id=8437687) also features a lively debate.
  - `felixgallo` points out that teaching shell is easier than teaching a map, reduce, and filter. I won't argue the subjective point of which is easier, but it is incontroversial that most CS students are more interested in learning a real language than shell for employability reasons.
  - `rsync` says there is no better alternative, while `felixgallo` claims one is 20 years away, since existing tools would have to be ported. Here's the better alternative: Python for scripts, Xonsh for REPL. It already has an equivalent of most tools (`ls -> os.listdir`, `tr -> re.sub`, etc.), the tools can be trivially ported (like `wc -l -> open(...).read().count("\n")`), or existing tools can just be wrapped in a function that calls out to shell.

- [Beyond Bash by Li Haoyi](https://docs.google.com/presentation/d/11vZzXCfAA0aOFAuHA0nAvAzALGFGCH-dqHxx6XMgbk8) is a more persuasive argument on why Bash is insufficient and why Scala is a better replacement than Python. With a special library, Scala scripts are less than twice as verbose as the equivalent Bash script. The author raises an important question: For a webservice striving to have availability, how can one be confident that a deployment workflow _works_? With Bash-based Puppet scripts, there are a ton of subtle pitfalls and input-dependent "gotchas" (e.g. spaces in strings), and the whole thing is untestable. Not only is Scala a real progrmaming language that has sane datatypes, Scala has an advanced yet ergonomic type-checker which can be leveraged to eliminate many classes of runtime errors.

- In an entertaining talk called [The Unix Chainsaw](https://www.youtube.com/watch?v=sCZJblyT_XM), Gary Bernhardt espouses a seemingly opposite viewpoint, but I think it is mostly consistent with my view.
  1. Gary Bernhardt shows examples where shell is extremely useful and powerful.
  2. However, I would caveat that shell is often less maintainable than a real programming language (thesis of this post).
  3. Gary Berhardt points out that not all things need to be maintainable (they can be "half-assed"). I have to agree. Many people use shell one-liners for things they only have to do once.
  5. My problem is when shell scripts start taking the place of a real program. This goes back to Li Haoyi's point, "how can you be sure that a tool is going to still work with new inputs if it is written in shell?"
  6. So it boils down to learn both so you can _use the right tool for the job_.

I am genuinely interested in opposing opinions, so drop a comment explaining why shell scripts are useful. Disqus's free tier now has disgusting ads, so I switched away from it. You can comment in one of these places instead:

- [HackerNews](https://news.ycombinator.com/item?id=25604501)
- [Twitter](https://twitter.com/charmoniumQ/status/1345049520602828801)

<img src="/raw-binary/stop-writing-shell-scripts//winter-is-coming.jpg" />

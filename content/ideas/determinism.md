When we say determinstic, we must clarify with respect to what variables. A random sort is non-deterministic as a function of the input array, but deterministic as a function of the input array and the state of the pseudo-random number generator.

For the sake of this post, I will assume that there are no hardware failures. In reality, a stray cosmic ray shooting through the universe might chance upon a microscopic wire in the computer, flipping a bit in the machine. This is not as unlikely if you consider a huge supercomputer with a huge number of nodes with a long-running computation. However, it is improbable on a small computation, and there are error-correcting techniques to detect this on large ones.

In order to reproduce a program execution, we need to capture enough variables that the program is deterministic with respect to those variables.

1. Executing in a new stackframe. This isolates the stack-based variables in the current frame, and nothing else.

2. Executing in a new stack. This is what spawning a thread does; it starts a computation on a fresh stack. This isolates stack-based variables in every frame.

3. Executing in a new process. This implies executing in a new stack, since the stack points into the process memory space, and it isolates all of the variables. Also process-level facilities, such as open files (file-descriptor table).

4. Executing with a fixed `env`.

5. Executing with a fixed file system.

6. Executing with a fixed OS state.

7. Executing with a fixed network state.

- Nix > Docker for reproducibility
  - https://www.mpscholten.de/docker/2016/01/27/you-are-most-likely-misusing-docker.html
  - Suppose A deps on C@1.0.0 and B deps on C@2.0.0. Installing B breaks A.
    - Find real cases.
    - Tags in docker somewhat minimize this.
  - `apt update` is non-deterministic.
    - Find real cases where people use `apt update` in supposedly-reproducible scripts, and where the dep version has changed.
  - Bigger images.
  - Replace Yadage or plug in to Packtivity?
  - Cost overhead
  - Ease of use? Ease of building?
  - Ease of using hardware resources?

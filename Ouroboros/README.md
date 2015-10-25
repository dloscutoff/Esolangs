# Ouroboros

An esoteric programming language wherein the code is a bunch of [snakes eating their own tails](http://en.wikipedia.org/wiki/Ouroboros).

### How it works

An Ouroboros program is a series of lines, each of which represents an independent ouroboros snake. Commands are single characters. The *head* is the first character of the line, and the *tail* is the last character. Each snake starts by not having swallowed any of its tail yet. The `(` and `)` commands make it swallow or regurgitate sections of its tail, thus changing the flow of execution.

By way of illustration:

    Abcdefghij  How the code is written (A is head, j is tail)

    Abcd
    j  e        How the code is treated, in its initial state
    ihgf

    jiAbc
      h d       Code after swallowing two characters
      gfe

Control flow starts at the head and proceeds toward the tail. If it reaches the end of the snake or a section that has been eaten, it returns to the head. If the instruction pointer is ever swallowed, that snake dies (stops executing instructions). Regurgitating more than the snake has swallowed causes the tail to come back to its initial position. (It's an ouroboros, it has to have its tail in its mouth!)

Each snake executes instructions in parallel with the others, with snakes from top to bottom each executing one instruction on each tick. Each snake has a stack, and there is also a shared stack that allows for inter-snake commerce. Empty stacks act as if they contain infinite zeroes (though the true length is accessible using L/l).

### Commands

Literals:

    0-9 Push value (multiple digits work as a single multi-digit number)
    a-f Push 10-15
    ""  Push ASCII values of all characters between quotes, reversed for easy printing

Stack operations:

    \   Swap top two items on stack
    @   Rotate top three items on stack
    ;   Pop stack and discard
    .   Duplicate top of stack
    $   Toggle whether active stack is the shared stack or own stack (initially own stack)
    s   Set own stack active
    S   Set shared stack active
    m   Pop own stack and push to shared stack
    M   Pop shared stack and push to own stack
    y   Push copy of top of own stack to shared stack
    Y   Push copy of top of shared stack to own stack
    l   Push length of own stack to active stack
    L   Push length of shared stack to active stack

Control flow operations:

    (   Pop stack and eat that many instructions of tail
    )   Pop stack and regurgitate that many instructions of tail
    w   Pop stack and wait that many ticks before resuming execution

Math:

    +   Pop stack twice and add
    -   Pop stack twice and subtract
    *   Pop stack twice and multiply
    /   Pop stack twice and divide
    %   Pop stack twice and mod
    _   Negate top of stack
    I   Truncate top of stack to integer
    =   Pop stack twice and push 1 if equal, 0 otherwise
    <   Pop stack twice and push 1 if less than, 0 otherwise
    >   Pop stack twice and push 1 if greater than, 0 otherwise
    !   Logically negate top of stack
    ?   Push a random number between 0 and 1

Input/output:

    n   Pop stack and output as a number
    o   Pop stack and output as a character
    r   Read next nonnegative integer from input and push (-1 on eof)
    i   Read character from input and push (-1 on eof)

### Example programs

Print digits 0 through 9:

    .n1+.9>(

Hello world, straightforward version:

    "Hello, World!"ooooooooooooo1(

Hello world, shorter version using two snakes:

    S"Hello, World!"1(
    13wSoL!(

Fibonacci sequence (endless):

    1y(
    S.@\.nao+

[Collatz orbit](http://en.wikipedia.org/wiki/Collatz_conjecture) of input number:

    rm1(
    S.nao.2<22*(.2%.@@.3*1+@@*@2/\!*+

Test whether input number is prime:

    Sr0s1(
    )S1+.@@.@@%!Ms+S.@@.@>6*(6s2=n1(

Cat:

    i.1+!2*(o

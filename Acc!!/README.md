# *Acc!!*

A programming language designed to be [apparently unusable](https://codegolf.stackexchange.com/q/61804/16766)--but only *apparently*.

## The name

*Acc!!* is named for one of its defining features, the accumulator. It is also the sound you might make after trying to program in it. The language's mascot is the chronically hairball-ridden [Bill the Cat](https://en.wikipedia.org/wiki/Bill_the_Cat).

![Bill the Cat][1]

The name *Acc!!* should be italicized, with two exclamation points. If technical difficulties prevent the use of italics, they may be omitted, although this makes Bill unhappy. *Acc!*, with one exclamation point, is an earlier version of the language; it was rejected as being [insufficiently unusable](https://codegolf.stackexchange.com/a/62404/16766).

## How it works

### Commands

Commands are parsed line by line. There are three types of command:

1. `Count <var> while <cond>`

Counts `<var>` up from 0 as long as `<cond>` is nonzero, equivalent to C++ `for(int <var>=0; <cond>; <var>++)`. The loop counter can be any single lowercase letter. The condition can be any expression, not necessarily involving the loop variable. The loop halts when the condition's value becomes 0.

Loops require K&R-style curly braces (in particular, [the Stroustrup variant](https://en.wikipedia.org/wiki/Indent_style#Variant:_Stroustrup)):

    Count i while i-5 {
     ...
    }

Loop variables are only available inside their loops; attempting to reference them afterwards causes an error.

2. `Write <charcode>`

Outputs a single character with the given ASCII/Unicode value to stdout. The charcode can be any expression.

3. Expression

Any expression standing by itself is evaluated and assigned to the accumulator (which is accessible as `_`). Thus, e.g., `3` is a statement that sets the accumulator to 3; `_ + 1` increments the accumulator; and `_ * N` reads a character and multiplies the accumulator by its charcode.

**Note:** the accumulator is the only variable that can be directly assigned to; loop variables and `N` can be used in calculations but not modified.

The accumulator is initially 0.

### Expressions

An expression can include integer literals, loop variables (`a-z`), `_` for the accumulator, and the special value `N`, which reads a character and evaluates to its charcode each time it is used.

Operators are:

- `+`, addition
- `-`, subtraction; unary negation
- `*`, multiplication
- `/`, integer division
- `%`, modulo
- `^`, exponentiation

Parentheses can be used to enforce precedence of operations. Any other character in an expression is a syntax error.

### Whitespace and comments

Leading and trailing whitespace and empty lines are ignored. Whitespace in loop headers must be exactly as shown above, including a single space between the loop header and opening curly brace. Whitespace inside expressions is optional.

`#` begins a single-line comment.

### Input/Output

Each time `N` is referenced in an expression, *Acc!!* reads one character from stdin. **Note:** this means you only get one shot to read each character; the next time you use `N`, you'll be reading the next one. `N` evaluates to the charcode of the character. If end-of-file has been reached (e.g. if stdin was redirected from a file or if the user enters an EOF manually), `N` evaluates to 0.

A character can be output by passing its charcode to the `Write` statement.

### Interpreter

The interpreter (written in Python 3) translates *Acc!!* code into Python and `exec`s it. It is invoked as follows:

    python acc.py program.acc

If a filename is not supplied on the command line, the interpreter will prompt for a filename.

## How do I program in this monstrosity?

Programming in *Acc!!* typically involves manipulating the accumulator to store multiple values at once. For inspiration, take a look at the sample programs and the explanation of the third-highest-number program on the [original StackExchange post](https://codegolf.stackexchange.com/a/62493/16766).

## Turing-completeness

The author believes *Acc!!* to be Turing-complete. He has not yet completed a proof, but believes cyclic tag systems are a promising emulation target.

[1]: http://i.stack.imgur.com/fYRFJ.gif
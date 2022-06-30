# (re)generate

A language for generating strings from regular expressions.

## The basics

Regenerate takes a regular expression and outputs the strings that are fully matched by it.

### Outputting matches

If you run `regenerate.py` with a regular expression as its argument, you'll get a string that matches that regex:

    > python3 regenerate.py 'ab+c'
    abc

By default, Regenerate only outputs the first match it finds. To output more, use the `-l` (limit) flag:

    > python3 regenerate.py -l 4 'ab+c'
    abc
    abbc
    abbbc
    abbbbc

To output all possible matches, use the `-a` flag. (Note: if you use an unbounded quantifier, you will get infinite output!)

Regenerate supports the typical regex operations:

    > python3 regenerate.py -l 12 'a*(b{1,2}|[c-e])f?'
    b
    bf
    bb
    bbf
    c
    cf
    d
    df
    e
    ef
    ab
    abf

Metacharacters can be escaped using backslashes:

    > python3 regenerate.py '\(a\)'
    (a)

The current list of metacharacters that need to be escaped is `()[]{}*+?|\$#!`. The characters `.` and `^` are not metacharacters, unlike in most regex flavors. The escape sequence `\n` matches a newline.

### Invocation methods

You can specify a filename instead of the regex. If the file `test+.rgx` contains the regex `ab+c`, then:

    > python3 regenerate.py -l 2 test+.rgx
    abc
    abbc

For less ambiguity, use the `-f` flag to specify a filename and the `-r` flag to specify a regex:

    > python3 regenerate.py -l 2 -f test+.rgx
    abc
    abbc
    > python3 regenerate.py -l 2 -r test+.rgx
    test.rgx
    testt.rgx

Use the `-i` flag to input the regex from stdin:

    > echo -n 'ab+c' | python3 regenerate.py -l 2 -i
    abc
    abbc

For more information about command-line options, run `python3 regenerate.py -h`.

### Capture groups and inputs

Any parenthesized subexpression in the regex forms a capture group. Capture groups are numbered left to right, based on the order of their opening parentheses, starting at 1. The contents of capture group N can be inserted again using the backreference `$N`:

    > python3 regenerate.py -a -r '(ab?)_$1'
    a_a
    ab_ab

If a capture group is matched multiple times, the backreference contains the most recent match:

    > python3 regenerate.py -a -r '(a|b){2}_$1'
    aa_a
    ab_b
    ba_a
    bb_b

If a capture group has not yet been matched, an attempt to backreference it *fails*. Use `|` to provide an alternative:

    > python3 regenerate.py -r '(Group 3: ($3|not matched yet) -- (Hello, world)\n){2}'
    Group 3: not matched yet -- Hello, world
    Group 3: Hello, world -- Hello, world

Inputs to the program can be given on the command line. They are accessible via the special backreferences `$~1`, `$~2`, and so on:

    > python3 regenerate.py -r '1 $~1 2 $~2{2}' abc xyz
    1 abc 2 xyzxyz

### Numeric expressions

Inside curly braces, backreferences are interpreted numerically:

    > python3 regenerate.py -r '(4) a{$1}'
    4 aaaa

This feature is particularly useful for taking numbers as program inputs:

    > python3 regenerate.py -r 'a{$~1}' 5
    aaaaa

Curly braces can evaluate simple arithmetic expressions:

    > python3 regenerate.py -r 'a{3*$~1+1}' 2
    aaaaaaa
    > python3 regenerate.py -r 'a{3*($~1+1)}' 2
    aaaaaaaaa

Use `${...}` to match the result of an arithmetic expression as a string rather than using it as a repetition count:

    > python3 regenerate.py -r '$~1 squared is ${$~1*$~1}' 5
    5 squared is 25

A backreference that starts with `#` instead of `$` gives the length of the backreferenced string instead of the string itself:

    > python3 regenerate.py -r '$~1 has #~1 characters' 'Hello, world!'
    Hello, world! has 13 characters
    > python3 regenerate.py -r '(\+-{#~1+2}\+)\n\| $~1 \|\n$1' 'Hello, world!'
    +---------------+
    | Hello, world! |
    +---------------+

### Short-circuiting alternation

The `!` operator is similar to `|`, but it matches at most one of its alternatives. The difference only becomes apparent when multiple matches are requested.

    > python3 regenerate.py -a -r '$1|x{1,2}'
    x
    xx
    > python3 regenerate.py -a -r '$1!x{1,2}'
    x
    xx

Here, `|` and `!` behave identically. In both cases, the first alternative (a backreference to a nonexistent group) fails, and the alternation operator tries the second alternative instead.

    > python3 regenerate.py -a -r 'x{1,2}|y{1,2}'
    x
    xx
    y
    yy
    > python3 regenerate.py -a -r 'x{1,2}!y{1,2}'
    x
    xx

When the first alternative succeeds, `|` goes on to try the second alternative, but `!` stops and does not try the second alternative. (This behavior is inspired by the "cut" from Prolog, which also uses the `!` character.)

Since they are both types of alternation, `|` and `!` have the same precedence and are left-associative: `a!b|c` parses as `a!(b|c)`, and `a|b!c` parses as `a|(b!c)`.

## Example programs

[Hello, world](https://esolangs.org/wiki/Hello,_world!):

    Hello, world\!

[99 Bottles of Beer](https://codegolf.stackexchange.com/q/64198/16766):

    (((99)( bottle)s( of beer))( on the wall)), $2.\n(Take one down and pass it around, (((${$10-1}|${$3-1})$4s{1-1/$10}$5)$6).\n\n$8, $9.\n){98}Go to the store and buy some more, $1.

[Print a 3D shape](https://codegolf.stackexchange.com/q/217933/16766):

    (( {#2-1}| {$~1-1})(//$3|)(^L){$~1}\n){$~1}(( $6|)(\\{#7-2}|\\{#3})( "){$~1}\n){$~1}

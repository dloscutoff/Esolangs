# tinylisp

A minimalist Lisp dialect.

### Syntax

Tokens in tinylisp are `(`, `)`, or any string of one or more printable ASCII characters except parentheses or whitespace. (I.e. the following regex: `[()]|[^()\s]+`.) Any token that consists *entirely* of digits is an integer literal. (Leading zeros are okay.) Any token that contains non-digits is a name, even numeric-looking examples like `123abc`, `3.14`, and `-10`. All whitespace is ignored; its only effect is to separate tokens.

A tinylisp program consists of a series of expressions. Each expression is either an integer, a name, or an s-expression (list). Lists consist of zero or more expressions wrapped in parentheses. No separator is used between items. Here are examples of expressions:

    4
    tinylisp!!
    ()
    (c b a)
    (q ((1 2)(3 4)))

### Data types

Data types in tinylisp are integers, names, lists, and builtin functions and macros. Lists can contain any number of values of any type and can be nested arbitrarily deeply.

The empty list `()`--also referred to as nil--and the integer `0` are the only values that are considered logically false; all other integers, nonempty lists, builtins, and all unevaluated names are logically true.

### Evaluation

Expressions in a program are evaluated in order and the results of each sent to stdout.

- An integer literal evaluates to itself.
- The empty list `()` evaluates to itself.
- A list of one or more items treats its first item as a function or macro and calls it with the remaining items as arguments.
- A name evaluates to the value bound to that name in the local scope. If the name is not defined in the local scope, it evaluates to the value bound to it at global scope. Referencing a name not defined at local or global scope is an error. Names at intermediate nested scopes cannot be accessed.

### Built-in functions and macros

There are nine built-in functions in tinylisp. A function evaluates each of its arguments before applying some operation to them and returning the result.

- `c` - construct list. Takes a value and a list and returns a new list obtained by prepending the value to the front of the list.
- `h` - head (car, in Lisp terminology). Takes a list and returns the first item in it, or nil if given nil.
- `t` - tail (cdr, in Lisp terminology). Takes a list and returns a new list containing all but the first item, or nil if given nil.
- `a` - add. Takes two integers and returns the first plus the second.
- `s` - subtract. Takes two integers and returns the first minus the second.
- `l` - less than. Takes two integers; returns 1 if the first is less than the second, 0 otherwise.
- `e` - equal. Takes two values; returns 1 if the two are identical, 0 otherwise.
- `v` - eval. Takes a value, representing an expression, and evaluates it. E.g. doing `(v (q (c a b)))` is the same as doing `(c a b)`; `(v 1)` gives `1`.
- `disp`. Takes a value and writes it to stdout, followed by a newline. Returns nil.
- `type`. Takes a value and returns one of four type names: `Int`, `Name`, `List`, or `Builtin`.

"Value" here refers to any integer, name, list, or builtin.

There are four built-in macros in tinylisp. A macro, unlike a function, does not evaluate its arguments before applying operations to them.

- `q` - quote. Takes an expression and returns it unevaluated. Evaluating `(1 2 3)` gives an error because it tries to call `1` as a function or macro, but `(q (1 2 3))` returns the list `(1 2 3)`. Evaluating `a` gives the value bound to the name `a`, but `(q a)` gives the name itself.
- `i` - if. Takes a condition expression, an if-true expression, and an if-false expression. Evaluates the condition first. If the result is falsy (`0` or nil), evaluates and returns the if-false expression. Otherwise, evaluates and returns the if-true expression. Note that the expression that is not returned is never evaluated.
- `d` - def. Takes a name and an expression. Evaluates the expression and binds it to the name *at global scope*, then returns the name. A name cannot be redefined once it has been defined. Note: it is not necessary to quote the name before passing it to `d`, though it is necessary to quote the expression if it's a list or name you don't want evaluated: e.g., `(d x (q (1 2 3)))`.
- `load`. Takes a filename, reads that file, and evaluates the contents as tinylisp code.

### Defining functions and macros

Starting from these builtins, tinylisp can be extended by defining new functions and macros. These have no dedicated data type; they are simply lists with a certain structure:

- A function is a list of two items. The first is either a list of parameter names, or a single name which will receive a list of any arguments passed to the function (thus allowing for variable-arity functions). The second is an expression which is the function body.
- A macro is the same as a function, except that it contains a third element (nil, by convention) before the parameter name(s).

For example, the following expression is a function that adds two integers:

    (q               List must be quoted to prevent evaluation
     (
      (x y)          Parameter names
      (s x (s 0 y))  Expression (in infix, x-(0-y))
     )   
    )

And a macro that takes any number of arguments and evaluates and returns the first one:

    (q               List must be quoted to prevent evaluation
     (
      ()             Having a value here makes it a macro, not a function
      args           Name for list of all args
      (v (h args))   Expression: eval(head(args))
     )
    )

Functions and macros can be called directly, bound to names using `d`, and passed to other functions or macros.

Function parameters are local variables (actually constants, since they can't be modified). They are in scope while the body of that call of that function is being executed, and out of scope during any deeper calls and after the function returns. They can "shadow" globally defined names, thereby making the global name temporarily unavailable. For example, the following code returns 5, not 41:

    (d x 42)
    
    (d f
     (q (
      (x)
      (s x 1))))
    
    (f 6)

However, this code returns 41, because `x` at call level 1 is not accessible from call level 2:

    (d x 42)
    
    (d f
     (q (
      (x)
      (g 15))))
    
    (d g
     (q (
      (y)
      (s x 1))))

Recursion is the only repetition construct in tinylisp. The interpreter does [tail-call elimination](https://en.wikipedia.org/wiki/Tail_call), allowing unlimited recursion depth for properly written functions.

### Running tinylisp

There are two ways of running tinylisp code: from a file, or from the interactive REPL prompt.

- To run code from one or more files, pass the filenames as command-line arguments to the interpreter: `python3 tinylisp.py file1.tl file2.tl`.
- To run code from the interactive prompt, run the interpreter without command-line arguments.

(Note that you can run code from a file when in interactive mode using the `load` macro.)

The interactive prompt provides these additional commands:

- `(help)` displays a help document.
- `(restart)` clears all user-defined names, starting over from scratch.
- `(quit)` ends the session.

Note: the interactive prompt reads one line at a time. In a file, an expression can span multiple lines; but at the prompt, *the end of a line is considered the end of the expression*, and any open parentheses are auto-closed. Lines can still contain multiple expressions, which are evaluated in order as usual.
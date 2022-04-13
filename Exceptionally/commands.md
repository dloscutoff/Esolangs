Commands in Exceptionally come in four types: binary, comparison, unary, and special.

## Binary

Binary commands apply a two-argument function to the register value and their argument, assigning the result of the function back to the register.

Command | Name      | Description
--------|-----------|------------
`+`     | add       | Adds two numbers; concatenates two strings or two lists
`-`     | sub       | Subtracts two numbers
`*`     | mul       | Multiplies two numbers; repeats a string/list by a number
`/`     | div       | Divides two numbers
`%`     | mod       | Takes one number modulo another; substitutes a value into a printf-style format string
`^`     | pow       | Takes one number to the power of another
`,`     | fromto    | Range from the first number (inclusive) to the second number (exclusive)
`:`     | item      | Gets the character of a string or item of a list at the given index
`[`     | slicefrom | Gets a slice of a string/list starting at the given index
`]`     | sliceto   | Gets a slice of a string/list ending just before the given index
`@`     | find      | Finds the first index at which an item/substring appears
`#`     | count     | Counts the number of occurrences of an item/substring
`\|`    | split     | Splits a string on occurrences of a substring
`$`     | join      | Joins a string/list of strings on a given string
`&`     | pair      | Wraps two values in a two-item list
`~`     | append    | Appends a value to the right end of a list

Note that the arguments to `join` are reversed from Python's order: `$"_"` joins the register on underscores, essentially translating to `reg = "_".join(reg)`.

## Comparison

Comparison commands apply a two-argument boolean function to the register value and their argument, raising an exception if the result is false and doing nothing if it is true.

Command | Name      | Description
--------|-----------|------------
`=`     | equal     | Asserts that the register is equal to the argument
`<`     | less      | Asserts that the register is less than the argument
`>`     | greater   | Asserts that the register is greater than the argument

## Unary

Unary commands apply a one-argument function to their argument, assigning the result of the function back to their argument (either a variable, or the register if no argument is given).

Command | Name      | Description
--------|-----------|------------
`U`     | up        | Increments a number; converts a string to uppercase
`D`     | down      | Decrements a number; converts a string to lowercase
`R`     | rangeto   | Range from 0 (inclusive) to a number (exclusive)
`A`     | asc       | Converts a character to its codepoint
`C`     | chr       | Converts a codepoint to a character
`I`     | int       | Converts a string/number to an integer
`S`     | str       | Converts a value to a string
`V`     | eval      | Evaluates a string as a Whython expression
`L`     | len       | Takes the length of a string/list
`F`     | flip      | Reverses a string/list; negates a number
`O`     | order     | Sorts a string/list
`E`     | elems     | Converts a string/list to a list of its elements
`W`     | wrap      | Wraps a value in a one-item list

## Special

Special commands don't fit any of the other categories, usually because they have some kind of side effect.

Command | Name      | Description
--------|-----------|------------
`{`     | load      | Copies the argument's value into the register
`}`     | store     | Copies the register's value into the argument
`!`     | skip      | Adds the argument's value to the instruction pointer
`G`     | get       | Reads a line of stdin and stores it in the argument
`P`     | put       | Prints the argument's value to stdout with a trailing newline


# Exceptionally

A language that uses exceptions for control flow.

## Language overview

A program in Exceptionally contains of a series of *lines*, each consisting of one or more *commands* connected by *operators*. The lines are executed one by one. When the instruction pointer reaches the end of the program, it wraps around to the beginning. The program thus forms an infinite loop; the only way to break out of the loop is by causing an error. Every Exceptionally program either terminates with an exception or does not terminate.

### Commands

Each command consists of a single character, optionally followed by an *argument*. The argument can be a number literal, a string literal, or a variable name.

Number literals can be integers, like `42`, or floats, like `4.2`. Floats less than 1 can be written as `0.42` or `.42`. Negative numbers are marked with underscores: `_42`.

String literals begin and end with `"`. They can contain any character except `"` and `\`. There are no escape sequences.

Variable names can be any run of one or more lowercase letters.

Commands come in two main categories: binary (using symbols) and unary (using uppercase letters). Binary commands modify the value of the *register*, a special variable (named `reg`) which is initially set to 0. For example, the command `+5` adds `5` to the register, while the command `+x` adds the current value of the variable `x` to the register. Unary commands modify their argument directly: for example, `Ix` converts the variable `x` to an integer.

A command without an explicit argument uses the register as its argument. For example, while the command `*3` multiplies the register by 3, the command `*` multiplies the register by itself. Similarly, `Dx` decrements the variable `x`, while `D` decrements the register.

Comparison commands are like binary commands, except they do not modify the register's value; instead, they merely raise an exception if the comparison fails. For example, `>1` raises an exception if the register's value is not greater than 1; if it is greater than 1, the command does nothing.

A few commands don't fit neatly into the above categories. The command `{` (load) copies a value into the register: `{5` sets the register to 5, while `{x` sets it to the value of `x`. Similarly, `}` (store) copies the register's value into a variable. Input and output are achieved via the `G` (get) and `P` commands. Finally, the Skip command `!` provides simple control flow by skipping forward a given number of lines (relative goto). It does so by modifying the instruction pointer, a special variable named `ip`.

For a full list of commands, see [commands.md](./commands.md).

### Operators

There are two operators used to chain commands together in Exceptionally: `?` and `;`.

If a line consists of two commands connected with the `?` operator, the first command is executed. If that succeeds, the rest of the line is ignored, and execution continues with the next line. If the first command causes an exception, the second command is executed instead. A line can contain any number of commands chained with `?`. If the last command is reached and it also causes an exception, then the program halts.

For example, consider the line `/x ? <"Division by zero"`. The command `/x` attempts to divide the register by the value of `x`. If `x` is zero, this operation will trigger an exception, in which case the second command `<"Division by zero"` is executed, printing an error message (and leaving the value of the register unchanged).

The `;` operator is higher-precedence than `?`; it simply executes commands in sequence until one of them causes an exception. Consider the line `/ ; <"Nonzero" ? <"Zero"`. The command `/` attempts to divide the register by itself. If the register is zero, this triggers an exception, in which case execution jumps after the `?` operator to the command `<"Zero"`. If the register is not zero, there is no exception; execution proceeds to the command `<"Nonzero"` and from there to the next line, ignoring `<"Zero"`.

### Miscellaneous

Exceptionally has comments that start with `'` and go until the next newline.

Whitespace is generally unimportant in Exceptionally. This program to output the square of an input number and halt:

    G
    I
    *
    P
    /0

could also be written as `GI*P/0`. Newlines that end comments, and whitespace in strings, are the only significant whitespace.

## The implementation

Exceptionally is implemented in [Whython](https://github.com/pxeger/whython), a modified version of Python 3. If you have Whython installed and configured to run as `whython`, you can run the interpreter like so:

    > whython exceptionally.why program.exc

If no filename is given, the interpreter reads the Exceptionally program from stdin.

The interpreter supports two flags. The `-V` or `--version` flag prints the version number and exits. The `-q` or `--quiet` flag suppresses the exception traceback. This flag must be specified before the filename:

    > whython exceptionally.why -q program.exc

If you don't have Whython installed, you can run it at [Attempt This Online](https://ato.pxeger.com/about). Here is [an adapted version of the Exceptionally interpreter](https://ato.pxeger.com/run?1=nVhbcxs1FB5e_cRPEAolu4ntJg_MMJuaUELKZKYkmZiUYTauR7FlW3Rv1WpjGxP-CC99YfhHPPTXcI52pb3Facs-xKujc_3ORdr89c9ysVaLOHr3_vN_RZjEUhHJO8Vbuk47nVenV8Ozi3MyIPSg_3X_gHY635-dP7_6FSibDoGH7lOPUDad0m6-7uE6zW7Neg_XYRaY9VNcT8WdWT_R-7GVf43rJF6adRfXMxmHKjYkD0lC8dAQfG0zEBOOjIY6stRS9DutTUTW3A4SJnEWKUP5Q4slgbCUL5HyWywiQ_hK-8iENIQ_NQhJwq3i-07n5OKny-dXZ0ONX4HWABn524xZPJ4hJeBpagjfImEuOVNclsqu66g_1wbTiRE60WEsrEM_aJTjpXX5VBsOeGjtvNBQBCIxhB-1YW7DPtMwl8C8zD21Ki9wHcupdZNeIUWyaF5BfKjhVJbnGteZNfpK-3VX4vELEpaSJWXsL67PT4Zl7FhsHglYeDtlZNUla4-syD5ZFwqw9lrbPbuNpdja3rPbWJmt7aeldPyA7Sd2u6jTBkcgUuVoWBwkuG7BrUu4qc1fj0wgtqDbPF6NqW1y5XtWjy735n4fiHzlrI0veQu0uDS55MrbosWlySWXbpUG07qPVGdleHT3NHh8_DFeF930QKJLhPJGarEMBjYhurFaDM_svumzFsu3lgW7zCNQ56ZCsKtK_ry6Dskx4BDESy4dE2LebXn6TSqw3Wqyvuf1Dkcg3VsZl7iqsYgoyZRVCu-13URChwKs4CAxGvKerHJRmsOfwmTnU2B3iZgRkYooVSya6LqEHnUJD1JOLFehz3R0HoqvlyYFWSMeyE-ORQb5K7HQDV1l9Fcj095TPiMKlKaJCLgziafc9fSeJU7HgYh4CiPAz6WQCVb40w_AcZE4rt6AqDQRwpIqXQq1cOgx1ei06Ee0sIOPZAIiH64jxVanUsbSmdFLGc8lC8mERVGsyC2fi4igLNmgMv9gdE9zs8sFeKktlBrBlZB4AzhS-yFTEzC429-jXVIJ0DyVcPywD2XvuN6oHljJGikRZbxqpnAGKoXQ4yNa171DTnIREc0Jg3rhdyLOUoKI1hhjyBdTANTAKNzq4-E278AZRKoOxCdADKEXABtvDMLmgSvLuOIpXD_QaEkB0hHNy9gQa_LNmvKx-_YHZEbJpqr7nlArh9qaoA6xkEg8A0gjvmyj2bTTz-eZQyvxTOIwZBBxG3Cd1HwTkppfueoewNGRBDC6EAPJ51hoT1IH3rpkw-T83qVwLOWCfqFqVAmobqC8qWw3cginYNtCKflhK9ePR6GVFnGUBq4_IgJM-iXdrjmfkYXO7So2j6goINY6HlFx_4gKGx_oekTFF4-oEAnKw9_9tifNEn2o205XCZ_AaDcGu2QG5_vUa80zfD7Y8DvkkkmwoRbcKNxNCfiVhTxS2-egpONj59i7me7d9N3jm-n-w0Nxh5xFis-5xOE9C2KmoMvgrGZBjc3YA1fD_lzGWXMm7ZBruOrIdBJLDmU4FRNAM9V9O2dK3HESZeEtl81BZhTXzowxdduDreICdSgkx4pKDrmD4xXkuvhp5MImbdZgEx2f9X4fbQXlnIX84wF4yMAu9V_Tm5vRHt3dYmMImYbT4pPhfmhQnsdWpkvgqGdZoFKiYmwDuE00cK9CWesTDKNVH5CkaA263nA4l1lKdIAcyjp9A02iFlAyIXJMFkwyKHyZ_p9jV49yaEERRwQPCmdjerI_iyXYdMDrgfHcve9WErztuKno1LySq0xGLfb8ciSzSF-LuuRtJrgavGCAc5G0pDhAB80rVHGDWpeg8RWfODS_qvwsM-4R_O5yXp6dnw59kYzcIxwtA-LoAXPowvSFr7183y2-xuyjv8katA3VvNQzXjX2cYDB5kGLjJkGeoN8n8fAVxOeqNq9Cq8KGooHRl6nU6RVUkr_ztSs9827_Of9ZxdA6nRAwXgcQRuNx3rijschE9F4XAxek0i8bqZrOLjl_A4HoLlflvs4su2quIA5tPdK93rvDsoN0lsdGPlBhHMYQ4JNFgRrsin-y1IdvmiYr-Cj6sD9aLtvc7samKpVTYBgMOeWaOX7SZwYK_X-NXK63PIqrReiW8Bb4Psf). Put your Exceptionally code in the Code box, your input in the Input box, and click Execute. If you want to use a flag, put it in the Arguments box in this format: `["-q"]`.

## Example programs

[Hello, world](https://esolangs.org/wiki/Hello,_world!):

    P"Hello, world!"/

[Collatz conjecture](https://codegolf.stackexchange.com/questions/12177/collatz-conjecture-oeis-a006577), without whitespace:

    GI}n>1?Pi;L{i?{0U}i{n%2=0?!3{n/2!3{n*3U!1

With whitespace and comments:

    ' Read initial number from stdin
    G
    ' Convert to an integer
    I
    ' Store a copy in n
    }n
    ' Assert that the number is greater than 1
    >1
    ' If the assertion fails, ouput i and try to get the len of the register, erroring and halting the program
      ? Pi ; L
    ' Otherwise, keep going; load i into the register, or load 0 if i is undefined
    {i ? {0
    ' Increment
    U
    ' Store back in i
    }i
    ' Load n into the register
    {n
    ' Mod 2
    %2
    ' Is this equal to 0? If not, skip the next three lines
    =0 ? !3
    ' Load n
    {n
    ' Divide by 2
    /2
    ' Skip the next three lines
    !3
    ' Load n
    {n
    ' Multiply by 3
    *3
    ' Increment
    U
    ' Skip the next line (that is, skip the first line when the program loops)
    !1

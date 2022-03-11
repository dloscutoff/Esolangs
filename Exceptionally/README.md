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

If you don't have Whython installed, you can run it at [Attempt This Online](https://ato.pxeger.com/about). Here is [an adapted version of the Exceptionally interpreter](https://staging.ato.pxeger.com/run?1=nVjNcts2EJ5edeojoHBTk7ak2IfOdOgorus6Hc-ktseq0-nQigamIAkJSTAgaElV3RfpJZdOn6Avk6fpAiTAP8lJyoMp7C7259sfgP7rn8V8Jec8fv_hy39ZlHAhkaCd4le6SjudV2fXw_PLCzRA-KD_bf8Adzo_nF-cXP8GlHUHwYP3sYcwmUxwN1_31DrN7sx6T62jLDTrp2o9Yfdm_UTzud3_Wq0TvjDrrlpPBY8kNyRPkZikkSH42mbIAqoEDXVkqeXW77U2FltzO4oQ8CyWhvKH3paEzFK-VpQ3nMWG8I32kTBhCH9qEJKEWsUPnc7p5c9XJ9fnQ41fgdZACdJ3GbF4PFOUkKapITxXhJmgRFJRKrupo36ihLgAawjtoCimEY9Z4KGTNGAsFznVkc2tjz9q4PnCRnGmfQlpZE2_0OiELDGEn7Qv1CJxrpEvsXqZO29VXhZuWc_xtaIIEs8qSRhqhKWVuVHrzBp9pf26LyH6VREWgiQlHC9uLk6HJRyq_jwUkuhuQtCyi1YeWqJ9tCoUqHJssXuWraqzxd6zbFWsLfbTcjffYPuJZRel25AIWSodDYujCK5bSOuqbmrzVyMTiK3xtoxXE2qbXPqe1aM7oMnvA5EunZXxJe-KlpQml1J5p7SkNLmU0t3TEFr1FdVZGhndUA0ZX72M10WDbUh0iVDeWy2RwcAmRPdaS-CZ5ZvWa4k8LytCdVHJz6vpEB1D3CFfUOGYkPLuytNtoFftVdvre17vcAS7e0vjApU1ERYnmbRK8_6q8jHOoUxhcNMJIOoiNkUsZXEqSRzoGoN-cxENU4qsVKHPdGfupq-XBs6s4StgnceZQS7KOHVzVgX95ci06oROkQSlacJC6gR8Ql1P8yxxMg5ZTFNoZz_fpYRgpV79EBxnieNqBkSliRCWkOmCybmDj7GLuGjTj3BhRz2CMIh8uIolWZ4JwYUzxVeCzwSJUEDimEt0R2csRmovWitl_sHoAedmF3PwUlsoNYIrEfIGcGL2IyIDMLjb34NxXAnQPJVw_KgPJey43qgeWCkaSxZntGqmcAaqAOHjI1zXvYNO8y0sniGCEkHvGc9SpBCtCXLIF5EA1MAo3Orj4TbvwBmFVB2Iz4AYQi8ANt4YhM0DN5JxxVO4XSijJQVIRzgvY0Os7W_WlK86a3-Aphitq7ofELb7lLYmqENVSIhPAdKYLtpoNu3089nk4Eo8AY8iAhG3AddJzZmQ1PxGVfcAjoEkhDGkMBB0pgrtSerAry5aEzF7cDEcMflGv1A1qgRUN1BeRLYbOYQTrW2h3PlxKzePR6GVFnGUBm4-IQKV9Cu8XXMi4EZidG5XsX5ERQGx1vGIiodHVNj4QNcjKr56RAVL1H74u9_2pFmim7rtbJnQAEa7MdhFUzirJ15rnqnnow2_g66IABtyTo3C3RSBX1lEY7l9Dgo8PnaOvdvJ3m3fPb6d7G8eijvoPJZ0RoUa3tOQEwldBucuCWtixh64GvVngmfNmbSDbuDaItKACwplOGEBoJnqvp0Rye4pirPojormIDOKa2fGGLvtwVZxATsYkmO3Cgq5g-MV9nXVl48LTNyswSY6Pun9PtoKygWJ6KcDsMnALvZf49vb0R7e3WJjCJmG0-Kz4d40KC-43dNFcNSTLJQpkly1AdwmGrhXoaz1iQqjVR-QpHgFut5SOJdJinSAFMo6fQtNIudQMpGSCOZEECh8kf6fY1ePcmhBxmOkDgpnbXqyP-UCbDrg9cB47j50KwnedtxUdGpZQWUm4pZ4fjkSWayvRV30LmNUDl4QwLlIWlIcoIPmFaq4Qa1K0OiSBg7Oryq_iIx6SH1DOS_PL86GPktG7pEaLQPk6AFz6ML0hS-3nO8WX1b20d9XDdoaa1m45xVeNfhqgAHzoEVWmQZ6g_yQx0CXAU1k7V6lrgoaig0jr9Mp0iowxn9nctr77n3--vDFJZA6HVAwHsfQRuOxnrjjcURYPB4Xg9ckUl030xUc3GJ2rwaguV-WfDWy7aq4gDm490r3eu8eyg3SWx0Y-UGk5rAKCZgkDFdoXfwTpTp8lWG6hA-kA_eT7b7L7WpgqlY1AYJRObdEu7-f8MRYqfev2afLLa_SeiG6BbwFvv8B). Put your Exceptionally code in the Code box, your input in the Input box, and click Execute. If you want to use a flag, put it in the Arguments box in this format: `["-q"]`.

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

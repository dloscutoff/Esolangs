#!/usr/bin/python3

import sys
import os
from contextlib import contextmanager
from itertools import zip_longest


whitespace = " \t\n\r"
symbols = "()"

# The empty tuple represents the empty list, nil
nil = ()


# Shortcut functions for print without newline and print to stderr
def write(*args):
    print(*args, end="")


def error(*args):
    print("Error:", *args, file=sys.stderr)


def warn(*args):
    print("Warning:", *args, file=sys.stderr)


def scan(code):
    """Take a string and yield a series of tokens."""
    # Add a space to the end to allow peeking at the next character
    # without requiring a check for end-of-string
    code += " "
    i = 0
    while i < len(code):
        char = code[i]
        if char in whitespace:
            # Whitespace (ignore)
            pass
        elif char in symbols:
            # Reserved symbol
            yield char
        else:
            # Start of a name or literal--scan till the end of it
            a = i
            while code[i+1] not in whitespace + symbols:
                i += 1
            yield code[a:i+1]
        i += 1


def parse(code):
    """Take code and turn it into a parse tree.

The code can be a string or an iterator that yields tokens.
The resulting parse tree is a tinylisp list (i.e. nested tuples).
"""
    if isinstance(code, str):
        # If we're given a raw codestring, scan it before parsing
        code = scan(code)
    try:
        token = next(code)
    except StopIteration:
        token = ")"
    if token == "(":
        element = parse(code)
    elif token == ")":
        return nil
    elif token.isdigit():
        element = int(token)
    else:
        element = token
    return (element, parse(code))


def cons_iter(nested_tuple):
    """Iterate over a cons chain of nested tuples."""
    while nested_tuple:
        yield nested_tuple[0]
        nested_tuple = nested_tuple[1]


# tinylisp built-in functions and macros
# Key = implementation name; value = tinylisp name

builtins = {"tl_cons": "c",
            "tl_head": "h",
            "tl_tail": "t",
            "tl_add2": "a",
            "tl_sub2": "s",
            "tl_less2": "l",
            "tl_eq2": "e",
            "tl_eval": "v",
            "tl_type": "type",
            "tl_disp": "disp",
            "tl_string": "string",
            "tl_chars": "chars",
            # The following five are macros:
            "tl_def": "d",
            "tl_if": "i",
            "tl_quote": "q",
            "tl_load": "load",
            "tl_comment": "comment",
            # The following three are intended for repl use:
            "tl_help": "help",
            "tl_restart": "restart",
            "tl_quit": "quit",
            }

# These are functions and macros that should not output their return
# values when called at the top level (except in repl mode)

top_level_quiet_fns = ["tl_def", "tl_disp", "tl_load", "tl_comment"]

# These are functions and macros that cannot be called from other
# functions or macros, only from the top level

top_level_only_fns = ["tl_load", "tl_comment", "tl_help", "tl_restart",
                      "tl_quit"]


# Decorators for member functions that implement builtins

def macro(pyfunc):
    pyfunc.is_macro = True
    return pyfunc


def function(pyfunc):
    pyfunc.is_macro = False
    return pyfunc


# Exception that is raised by the (quit) macro

class UserQuit(BaseException):
    pass


class Program:
    def __init__(self, repl=False):
        self.repl = repl
        self.modules = []
        self.module_paths = [os.path.abspath(os.path.dirname(__file__))]
        self.names = [{}]
        self.depth = 0
        self.builtins = []
        self.global_names = self.names[0]
        self.local_names = self.global_names
        # Go through the tinylisp builtins and put the corresponding
        # member functions into the top-level symbol table
        for func_name, tl_func_name in builtins.items():
            builtin = getattr(self, func_name)
            self.builtins.append(builtin)
            self.global_names[tl_func_name] = builtin

    def execute(self, code):
        if isinstance(code, str):
            # First determine whether the code is in single-line or
            # multiline form:
            # In single-line form, the code is parsed one line at a time
            # with closing parentheses inferred at the end of each line
            # In multiline form, the code is parsed as a whole, with
            # closing parentheses inferred only at the end
            # If any line in the code contains more closing parens than
            # opening parens, the code is assumed to be in multiline
            # form; otherwise, it's single-line
            codelines = code.split("\n")
            multiline = any(line.count(")") > line.count("(")
                            for line in codelines)
            if not multiline:
                for codeline in codelines:
                    self.execute(parse(codeline))
                return
            else:
                code = parse(code)
        # Evaluate each expression in the code and (possibly) display it
        for expr in cons_iter(code):
            # Figure out which function the outermost call is
            outer_function = None
            if expr and isinstance(expr, tuple) and isinstance(expr[0], str):
                outer_function = self.tl_eval(expr[0])
                if outer_function in self.builtins:
                    outer_function = outer_function.__name__
            result = self.tl_eval(expr, top_level=True)
            # If outer function is in the top_level_quiet_fns list,
            # suppress output--but always show output when running in
            # repl mode
            if self.repl or outer_function not in top_level_quiet_fns:
                self.tl_disp(result)

    def call_data(self, function, raw_args):
        """Returns function/macro flag, param names, body, & arglist."""
        if function[0] == nil:
            # Potential macro
            is_macro = True
            # function should be a nested-tuple structure containing
            # nil, parameter names, and macro body
            if function[1] and function[1][1]:
                param_names = function[1][0]
                body = function[1][1][0]
                # Macro arguments stay unevaluated
                arglist = [arg for arg in cons_iter(raw_args)]
            else:
                error("list too short to be interpreted as macro")
                raise TypeError
        else:
            # Potential function
            is_macro = False
            # function should be a nested-tuple structure containing
            # parameter names and function body
            if function[1]:
                param_names = function[0]
                body = function[1][0]
                # Function arguments are evaluated
                arglist = [self.tl_eval(arg) for arg in cons_iter(raw_args)]
            else:
                error("list too short to be interpreted as function")
                raise TypeError
        return is_macro, param_names, body, arglist

    def call(self, function, raw_args):
        """Perform a function call with a user-defined function or macro."""
        try:
            is_macro, param_names, body, arglist \
                   = self.call_data(function, raw_args)
        except TypeError:
            # There was a problem with the structure of the supposed
            # function/macro (call_data already gave the error message)
            return nil
        with self.new_scope():
            # Loop while recursive calls are optimizable tail-calls
            while function is not None:
                # Assign arg values to param names in local scope
                if isinstance(param_names, tuple):
                    name_iter = cons_iter(param_names)
                    name_count = 0
                    val_count = 0
                    for name, val in zip_longest(name_iter, arglist):
                        if name is None:
                            # Ran out of argument names
                            val_count += 1
                        elif val is None:
                            # Ran out of argument values
                            name_count += 1
                        elif isinstance(name, str):
                            if name in self.global_names:
                                warn("macro" if is_macro else "function",
                                     "parameter name shadows global name",
                                     name)
                            self.local_names[name] = val
                            name_count += 1
                            val_count += 1
                        else:
                            error("parameter list must contain names, not",
                                  self.tl_type(name))
                            return nil
                    if name_count != val_count:
                        # Wrong number of arguments
                        error("macro" if is_macro else "function",
                              "expected", name_count, "arguments, got",
                              val_count)
                        return nil
                elif isinstance(param_names, str):
                    # Single name, bind entire arglist to it
                    arglist_name = param_names
                    if arglist_name in self.global_names:
                        warn("macro" if is_macro else "function",
                             "parameter name shadows global name",
                             arglist_name)
                    args = nil
                    while arglist:
                        args = (arglist.pop(), args)
                    self.local_names[arglist_name] = args
                else:
                    error("parameters must either be name or list of names,",
                          "not", self.tl_type(param_names))
                    return nil

                # Tail-call elimination
                head = None
                # Eliminate any ifs and evals
                while body and isinstance(body, tuple):
                    head = self.tl_eval(body[0])
                    if head == self.tl_if:
                        # The head is (some name for) tl_if
                        tail = body[1]
                        if (tail and tail[1] and tail[1][1]
                                and not tail[1][1][1]):
                            test = self.tl_eval(tail[0])
                            if test == 0 or test == nil:
                                body = tail[1][1][0]
                            else:
                                body = tail[1][0]
                        else:
                            error("wrong number of arguments for tl_if")
                            return nil
                    elif head == self.tl_eval:
                        # The head is (some name for) tl_eval
                        tail = body[1]
                        if tail and not tail[1]:
                            body = self.tl_eval(tail[0])
                        else:
                            error("wrong number of arguments for tl_eval")
                            return nil
                    else:
                        break
                # Are we left with a tail call to a user-defined
                # function/macro (either the same one or a different
                # one)?
                if head and isinstance(head, tuple):
                    # If so, swap out the args from the original call
                    # for the updated args, the function for the new
                    # function (which might be the same function), and
                    # loop for the recursive call
                    raw_args = body[1]
                    function = head
                    try:
                        is_macro, param_names, body, arglist \
                               = self.call_data(function, raw_args)
                    except TypeError:
                        # There was a problem with the structure of the
                        # supposed function/macro (call_data already gave
                        # the error message)
                        return nil
                    # Clear the local scope to prepare for the next
                    # iteration
                    self.local_names.clear()
                else:
                    # Otherwise, eval the final expression, break out
                    # of the loop, and return it
                    return_val = self.tl_eval(body)
                    function = None
        return return_val

    @contextmanager
    def new_scope(self):
        self.depth += 1
        self.names.append({})
        self.local_names = self.names[self.depth]
        try:
            yield self.local_names
        finally:
            self.names.pop()
            self.depth -= 1
            self.local_names = self.names[self.depth]

    @function
    def tl_cons(self, head, tail):
        if isinstance(tail, tuple):
            return (head, tail)
        else:
            error("cannot cons to", self.tl_type(tail), "in tinylisp")
            return nil

    @function
    def tl_head(self, lyst):
        if isinstance(lyst, tuple):
            if lyst == nil:
                return nil
            else:
                return lyst[0]
        else:
            error("cannot get head of", self.tl_type(lyst))
            return nil

    @function
    def tl_tail(self, lyst):
        if isinstance(lyst, tuple):
            if lyst == nil:
                return nil
            else:
                return lyst[1]
        else:
            error("cannot get tail of", self.tl_type(lyst))
            return nil

    @function
    def tl_add2(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            return arg1 + arg2
        else:
            error("cannot add", self.tl_type(arg1), "and", self.tl_type(arg2))
            return nil

    @function
    def tl_sub2(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            return arg1 - arg2
        else:
            error("cannot subtract", self.tl_type(arg1), "and",
                  self.tl_type(arg2))
            return nil

    @function
    def tl_less2(self, arg1, arg2):
        try:
            return int(arg1 < arg2)
        except TypeError:
            error("cannot use less-than to compare", self.tl_type(arg1),
                  "and", self.tl_type(arg2))
            return nil

    @function
    def tl_eq2(self, arg1, arg2):
        return int(arg1 == arg2)

    @function
    def tl_eval(self, code, top_level=False):
        if isinstance(code, tuple):
            if code == nil:
                # Nil evaluates to itself
                return nil
            # Otherwise, it's a function/macro call
            function = self.tl_eval(code[0])
            if function and isinstance(function, tuple):
                # User-defined function or macro
                return self.call(function, code[1])
            elif function in self.builtins:
                # Builtin function or macro
                if function.__name__ in top_level_only_fns and not top_level:
                    error("call to", function.__name__, "cannot be nested")
                    return nil
                if function.is_macro:
                    # Macros receive their args unevaluated
                    args = cons_iter(code[1])
                else:
                    # Functions receive their args evaluated
                    args = (self.tl_eval(arg) for arg in cons_iter(code[1]))
                try:
                    return function(*args)
                except TypeError as err:
                    # Wrong number of arguments to builtin
                    error("wrong number of arguments for", function.__name__)
                    return nil
            else:
                # Trying to call an int or unevaluated name
                error(function, "is not a function or macro")
                return nil
        elif isinstance(code, int):
            # Integer literal
            return code
        elif isinstance(code, str):
            # Name; look up its value
            if code in self.local_names:
                return self.local_names[code]
            elif code in self.global_names:
                return self.global_names[code]
            else:
                error("referencing undefined name", code)
                return nil
        else:
            # Probably a builtin
            return code

    @function
    def tl_type(self, value):
        if isinstance(value, int):
            return "Int"
        elif isinstance(value, str):
            return "Name"
        elif isinstance(value, tuple):
            return "List"
        else:
            return "Builtin"

    @function
    def tl_disp(self, value, end="\n"):
        if value is not None and not self.quiet:
            if value == nil:
                write("()")
            elif isinstance(value, tuple):
                # List (as nested tuple)
                beginning = True
                for item in cons_iter(value):
                    if beginning:
                        write("(")
                        beginning = False
                    else:
                        write(" ")
                    self.tl_disp(item, end="")
                write(")")
            elif value in self.builtins:
                # One of the builtin functions or macros
                write("<builtin %s %s>"
                      % ("macro" if value.is_macro else "function",
                         value.__name__))
            else:
                # Integer or name
                write(value)
            write(end)
        return nil

    @function
    def tl_string(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, int):
            # TBD: chr(value) instead?
            return str(value)
        elif isinstance(value, tuple):
            result = ""
            for char_code in cons_iter(value):
                if isinstance(char_code, int):
                    try:
                        result += chr(char_code)
                    except ValueError:
                        # Can't convert this number to a character
                        warn("cannot convert", char_code, "to character")
                        pass
                else:
                    error("argument of string must be list of Ints, not of",
                          self.tl_type(char_code))
                    return nil
            return result
        else:
            # Builtin
            return value.__name__

    @function
    def tl_chars(self, value):
        if isinstance(value, str):
            result = nil
            for char in reversed(value):
                result = (ord(char), result)
            return result
        else:
            error("argument of chars must be Name, not", self.tl_type(value))
            return nil

    @macro
    def tl_def(self, name, value):
        if isinstance(name, str):
            if name in self.global_names:
                error("name", name, "already in use")
                return nil
            else:
                self.global_names[name] = self.tl_eval(value)
                return name
        else:
            error("cannot define", tl_type(name))
            return nil

    @macro
    def tl_if(self, cond, trueval, falseval):
        # Arguments are not pre-evaluated, so cond needs to be evaluated
        # here
        cond = self.tl_eval(cond)
        if cond == 0 or cond == nil:
            return self.tl_eval(falseval)
        else:
            return self.tl_eval(trueval)

    @macro
    def tl_quote(self, quoted):
        return quoted

    @macro
    def tl_load(self, module):
        if not module.endswith(".tl"):
            module += ".tl"
        abspath = os.path.abspath(os.path.join(self.module_paths[-1], module))
        module_directory, module_name = os.path.split(abspath)
        if abspath not in self.modules:
            # Module has not already been loaded
            try:
                with open(abspath) as f:
                    module_code = f.read()
            except (FileNotFoundError, IOError):
                error("could not load", module_name, "from", module_directory)
                return nil
            else:
                # Add the module to the list of loaded modules
                self.modules.append(abspath)
                # Push the module's directory to the stack of module
                # directories--this allows relative paths in load calls
                # from within the module
                self.module_paths.append(module_directory)
                # Execute the module code
                self.execute(module_code)
                # Put everything back the way it was before loading
                self.module_paths.pop()
        return "Loaded %s" % module

    @macro
    def tl_comment(self, *args):
        return nil

    @macro
    def tl_help(self):
        return help_text

    @macro
    def tl_restart(self):
        self.__init__(repl=self.repl)
        return "Restarting..."

    @macro
    def tl_quit(self):
        raise UserQuit

    @property
    def quiet(self):
        # True (suppress output) while in process of loading modules
        return len(self.module_paths) > 1


def run_file(filename, environment=None):
    if environment is None:
        environment = Program(repl=False)
    try:
        with open(filename) as f:
            code = f.read()
    except FileNotFoundError:
        error("could not find", filename)
    except IOError:
        error("could not read", filename)
    else:
        try:
            environment.execute(code)
        except RecursionError:
            error("recursion depth exceeded. How could you forget "
                  "to use tail calls?!")
        except UserQuit:
            pass


def repl(environment=None):
    print("(welcome to tinylisp)")
    if environment is None:
        environment = Program(repl=True)
    instruction = input_instruction()
    while True:
        try:
            environment.execute(instruction)
        except KeyboardInterrupt:
            error("calculation interrupted by user.")
        except RecursionError:
            error("recursion depth exceeded. How could you forget "
                  "to use tail calls?!")
        except UserQuit:
            break
        except Exception as err:
            error(err)
            break
        instruction = input_instruction()
    print("Bye!")


def input_instruction():
    try:
        instruction = input("tl> ")
    except (EOFError, KeyboardInterrupt):
        instruction = "(quit)"
    return instruction


help_text = """
Enter expressions at the prompt.

- Any run of digits is an integer.
- () is the empty list, nil.
- A series of expressions enclosed in parentheses is a function call.
- Anything else is a name.

Builtin functions and macros:

- c, construct list. Takes a value and a list and returns a new list
     obtained by placing the value at the front of the list.
- h, head (car, in Lisp terminology). Takes a list and returns the first
     item in it, or nil if given nil.
- t, tail (cdr, in Lisp terminology). Takes a list and returns a new
     list containing all but the first item, or nil if given nil.
- a, add. Takes two integers and returns the first plus the second.
- s, subtract. Takes two integers and returns the first minus the
     second.
- l, less than. Takes two integers; returns 1 if the first is less than
     the second, 0 otherwise.
- e, equal. Takes two values; returns 1 if the two are identical, 0
     otherwise.
- v, eval. Takes a value, representing an expression, and evaluates it.
- q, quote (macro). Takes an expression and returns it unevaluated.
- i, if (macro). Takes a condition value, an if-true expression, and an
     if-false expression. If the condition value is 0 or nil, evaluates
     and returns the if-false expression. Otherwise, evaluates and
     returns the if-true expression.
- d, def (macro). Takes a name and an expression. Evaluates the
     expression and binds it to the name at global scope, then returns
     the name. A name cannot be redefined once it has been defined.
- string. Takes a list of integers representing character codes and
     converts it to a name (i.e. a string).
- chars. Takes a name and converts it to a list of integers representing
     character codes.
- type. Takes a value and returns its type, one of Int, Name, List, or
     Builtin.
- disp. Takes a value and writes it to stdout.
- load (macro). Takes a filename and evaluates that file as code.

You can create your own functions and macros. (A macro is like a
function, but doesn't evaluate its arguments; it can therefore be used
to manipulate unevaluated code.)

- To create a function, construct a list of two items. The first item
  should be a list of parameter names. Alternately, it can be a single
  name, in which case it will receive a list of all arguments. The
  second item should be the return expression.
- To create a macro, proceed as with a function, but add nil at the
  beginning of the list.

Use (load library) to access the standard library. It includes long
names for builtins (e.g. cons for c), convenience functions and macros
(list, lambda, etc.), list manipulation, metafunctions, integer
arithmetic, and more.

Special commands for the interactive prompt:

- (restart) clears all user-defined names, starting over from scratch.
- (help) displays this help text.
- (quit) ends the session.
"""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # User specified one or more files--run them
        environment = Program()
        for filename in sys.argv[1:]:
            run_file(filename, environment)
    else:
        # No filename specified, so...
        repl()

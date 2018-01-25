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
write = lambda *args: print(*args, end="")
error = lambda *args: print("Error:", *args, file=sys.stderr)
warn = lambda *args: print("Warning:", *args, file=sys.stderr)


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
    if type(code) is str:
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


def consIter(nestedTuple):
    """Iterate over a cons chain of nested tuples."""
    while nestedTuple:
        yield nestedTuple[0]
        nestedTuple = nestedTuple[1]


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
            # The following four are macros:
            "tl_def": "d",
            "tl_if": "i",
            "tl_quote": "q",
            "tl_load": "load",
            # The following three are intended for repl use:
            "tl_help": "help",
            "tl_restart": "restart",
            "tl_quit": "quit",
            }

# These are functions and macros that should not output their return
# values when called at the top level (except in repl mode)

topLevelQuietFns = ["tl_def", "tl_disp", "tl_load"]

# These are functions and macros that cannot be called from other
# functions or macros, only from the top level

topLevelOnlyFns = ["tl_load", "tl_help", "tl_restart", "tl_quit"]

# Decorators for member functions that implement builtins

def macro(pyFn):
    pyFn.isMacro = True
    return pyFn

def function(pyFn):
    pyFn.isMacro = False
    return pyFn

# Exception that is raised by the (quit) macro

class UserQuit(BaseException): pass


class Program:
    def __init__(self, repl=False):
        self.repl = repl
        self.modules = []
        self.modulePaths = [os.path.abspath(os.path.dirname(__file__))]
        self.names = [{}]
        self.depth = 0
        self.globalNames = self.names[0]
        self.localNames = self.globalNames
        # Go through the tinylisp builtins and put the corresponding
        # member functions into the top-level symbol table
        for fnName, tlName in builtins.items():
            self.globalNames[tlName] = getattr(self, fnName)

    def execute(self, code):
        if type(code) is str:
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
        for expr in consIter(code):
            # Figure out which function the outermost call is
            outerFunction = None
            if type(expr) is tuple and expr != nil and type(expr[0]) is str:
                outerFunction = self.tl_eval(expr[0])
                if type(outerFunction) is type(self.tl_eval):
                    outerFunction = outerFunction.__name__
            result = self.tl_eval(expr, topLevel=True)
            # If outer function is in the topLevelQuietFns list,
            # suppress output--but always show output when running in
            # repl mode
            if self.repl or outerFunction not in topLevelQuietFns:
                self.tl_disp(result)

    def callData(self, function, rawArgs):
        """Returns function/macro flag, param names, body, & arglist."""
        if function[0] == nil:
            # Potential macro
            macro = True
            # function should be a nested-tuple structure containing
            # nil, parameter names, and macro body
            if function[1] and function[1][1]:
                paramNames = function[1][0]
                body = function[1][1][0]
                # Macro arguments stay unevaluated
                arglist = [arg for arg in consIter(rawArgs)]
            else:
                error("list too short to be interpreted as macro")
                raise TypeError
        else:
            # Potential function
            macro = False
            # function should be a nested-tuple structure containing
            # parameter names and function body
            if function[1]:
                paramNames = function[0]
                body = function[1][0]
                # Function arguments are evaluated
                arglist = [self.tl_eval(arg) for arg in consIter(rawArgs)]
            else:
                error("list too short to be interpreted as function")
                raise TypeError
        return macro, paramNames, body, arglist

    def call(self, function, rawArgs):
        """Perform a function call with a user-defined function or macro."""
        try:
            macro, paramNames, body, arglist \
                   = self.callData(function, rawArgs)
        except TypeError:
            # There was a problem with the structure of the supposed
            # function/macro (callData already gave the error message)
            return nil
        with self.newScope():
            # Loop while recursive calls are optimizable tail-calls
            while function is not None:
                # Assign arg values to param names in local scope
                if type(paramNames) is tuple:
                    nameIter = consIter(paramNames)
                    valIter = arglist
                    nameCount = 0
                    valCount = 0
                    for name, val in zip_longest(nameIter, valIter):
                        if name is None:
                            # Ran out of argument names
                            valCount += 1
                        elif val is None:
                            # Ran out of argument values
                            nameCount += 1
                        elif type(name) is str:
                            if name in self.globalNames:
                                warn("macro" if macro else "function",
                                     "parameter name shadows global name",
                                     name)
                            self.localNames[name] = val
                            nameCount += 1
                            valCount += 1
                        else:
                            error("parameter list must contain names, not",
                                  self.tl_type(name))
                            return nil
                    if nameCount != valCount:
                        # Wrong number of arguments
                        error("macro" if macro else "function",
                              "expected", nameCount, "arguments, got",
                              valCount)
                        return nil
                elif type(paramNames) is str:
                    # Single name, bind entire arglist to it
                    arglistName = paramNames
                    if arglistName in self.globalNames:
                        warn("macro" if macro else "function",
                             "parameter name shadows global name",
                             arglistName)
                    args = nil
                    while arglist:
                        args = (arglist.pop(), args)
                    self.localNames[arglistName] = args
                else:
                    error("parameters must either be name or list of names,",
                          "not", self.tl_type(paramNames))
                    return nil
                
                # Tail-call elimination
                head = None
                # Eliminate any ifs and evals
                while body and type(body) is tuple:
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
                if head and type(head) is tuple:
                    # If so, swap out the args from the original call
                    # for the updated args, the function for the new
                    # function (which might be the same function), and
                    # loop for the recursive call
                    rawArgs = body[1]
                    function = head
                    try:
                        macro, paramNames, body, arglist \
                               = self.callData(function, rawArgs)
                    except TypeError:
                        # There was a problem with the structure of the
                        # supposed function/macro (callData already gave
                        # the error message)
                        return nil
                    # Clear the local scope to prepare for the next
                    # iteration
                    self.localNames.clear()
                else:
                    # Otherwise, eval the final expression, break out
                    # of the loop, and return it
                    returnVal = self.tl_eval(body)
                    function = None
        return returnVal

    @contextmanager
    def newScope(self):
        self.depth += 1
        self.names.append({})
        self.localNames = self.names[self.depth]
        try:
            yield self.localNames
        finally:
            self.names.pop()
            self.depth -= 1
            self.localNames = self.names[self.depth]

    @function
    def tl_cons(self, head, tail):
        if type(tail) is not tuple:
            error("cannot cons to non-list in tinylisp")
            return nil
        else:
            return (head, tail)

    @function
    def tl_head(self, lyst):
        if type(lyst) is not tuple:
            error("cannot get head of non-list")
            return nil
        elif lyst == nil:
            return nil
        else:
            return lyst[0]

    @function
    def tl_tail(self, lyst):
        if type(lyst) is not tuple:
            error("cannot get tail of non-list")
            return nil
        elif lyst == nil:
            return nil
        else:
            return lyst[1]

    @function
    def tl_add2(self, arg1, arg2):
        if type(arg1) is not int or type(arg2) is not int:
            error("cannot add non-integers")
            return nil
        else:
            return arg1 + arg2

    @function
    def tl_sub2(self, arg1, arg2):
        if type(arg1) is not int or type(arg2) is not int:
            error("cannot subtract non-integers")
            return nil
        else:
            return arg1 - arg2

    @function
    def tl_less2(self, arg1, arg2):
        try:
            return int(arg1 < arg2)
        except TypeError:
            error("unorderable types:", self.tl_type(arg1), "and",
                  self.tl_type(arg2))

    @function
    def tl_eq2(self, arg1, arg2):
        return int(arg1 == arg2)

    @function
    def tl_eval(self, code, topLevel=False):
        if type(code) is tuple:
            if code == nil:
                # Nil evaluates to itself
                return nil
            # Otherwise, it's a function/macro call
            function = self.tl_eval(code[0])
            if function and type(function) is tuple:
                # User-defined function or macro
                return self.call(function, code[1])
            elif type(function) is type(self.tl_eval):
                # Builtin function or macro
                if function.__name__ in topLevelOnlyFns and not topLevel:
                    error("call to", function.__name__, "cannot be nested")
                    return nil
                if function.isMacro:
                    # Macros receive their args unevaluated
                    args = consIter(code[1])
                else:
                    # Functions receive their args evaluated
                    args = (self.tl_eval(arg) for arg in consIter(code[1]))
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
        elif type(code) is int:
            # Integer literal
            return code
        elif type(code) is str:
            # Name; look up its value
            if code in self.localNames:
                return self.localNames[code]
            elif code in self.globalNames:
                return self.globalNames[code]
            else:
                error("referencing undefined name", code)
                return nil
        else:
            # Probably a builtin
            return code

    @function
    def tl_type(self, value):
        if type(value) is int:
            return "Int"
        elif type(value) is str:
            return "Name"
        elif type(value) is tuple:
            return "List"
        else:
            return "Builtin"

    @function
    def tl_disp(self, value, end="\n"):
        if value is not None and not self.quiet:
            if value == nil:
                write("()")
            elif type(value) is tuple:
                # List (as nested tuple)
                atBeginning = True
                for item in consIter(value):
                    if atBeginning:
                        write("(")
                        atBeginning = False
                    else:
                        write(" ")
                    self.tl_disp(item, end="")
                write(")")
            elif type(value) is type(self.tl_disp):
                # One of the builtin functions or macros
                write("<builtin %s %s>"
                      % ("macro" if value.isMacro else "function",
                         value.__name__))
            else:
                # Integer or name
                write(value)
            write(end)
        return nil

    @function
    def tl_string(self, value):
        if type(value) is str:
            return value
        elif type(value) is int:
            # TBD: chr(value) instead?
            return str(value)
        elif type(value) is tuple:
            result = ""
            for charCode in consIter(value):
                if type(charCode) is int:
                    try:
                        result += chr(charCode)
                    except ValueError:
                        # Can't convert this number to a character
                        warn("cannot convert", charCode, "to character")
                        pass
                else:
                    error("argument of string must be list of Ints, not of",
                          self.tl_type(charCode))
                    return nil
            return result
        else:
            # Builtin
            return value.__name__

    @function
    def tl_chars(self, value):
        if type(value) is str:
            result = nil
            for char in reversed(value):
                result = (ord(char), result)
            return result
        else:
            error("argument of chars must be Name, not", self.tl_type(value))
            return nil

    @macro
    def tl_def(self, name, value):
        if type(name) is int:
            error("cannot def integer")
        elif type(name) is tuple:
            error("cannot def list")
        elif name in self.globalNames:
            error("name already in use")
        else:
            self.globalNames[name] = self.tl_eval(value)
        return name

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
        abspath = os.path.abspath(os.path.join(self.modulePaths[-1], module))
        moduleDirectory, moduleName = os.path.split(abspath)
        if abspath not in self.modules:
            # Module has not already been loaded
            try:
                with open(abspath) as f:
                    moduleCode = f.read()
            except (FileNotFoundError, IOError):
                error("could not load", moduleName, "from", moduleDirectory)
                return nil
            else:
                # Add the module to the list of loaded modules
                self.modules.append(abspath)
                # Push the module's directory to the stack of module
                # directories--this allows relative paths in load calls
                # from within the module
                self.modulePaths.append(moduleDirectory)
                # Execute the module code
                self.execute(moduleCode)
                # Put everything back the way it was before loading
                self.modulePaths.pop()
        return "Loaded %s" % module

    @macro
    def tl_help(self):
        return helpText

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
        return len(self.modulePaths) > 1


def runFile(filename, environment=None):
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
        except UserQuit:
            pass


def repl(environment=None):
    print("(welcome to tinylisp)")
    if environment is None:
        environment = Program(repl=True)
    instruction = inputInstruction()
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
        instruction = inputInstruction()
    print("Bye!")


def inputInstruction():
    try:
        instruction = input("tl> ")
    except (EOFError, KeyboardInterrupt):
        instruction = "(quit)"
    return instruction


helpText = """
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
            runFile(filename, environment)
    else:
        # No filename specified, so...
        repl()


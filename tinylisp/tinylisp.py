#!/usr/bin/python3

import sys, os

whitespace = " \t\n\r"
symbols = "()"

# Shortcut function for print without newline and print to stderr
write = lambda *args: print(*args, end="")
error = lambda *args: print("Error:", *args, file=sys.stderr)

def scan(code):
    i = 0
    # Add a space to the end to allow peeking at the next character without
    # requiring a check for end-of-string
    code += " "
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
    tree = []
    if type(code) is str:
        # If we're given a raw codestring, scan it before parsing
        code = scan(code)
    for token in code:
        if token == "(":
            tree.append(parse(code))
        elif token == ")":
            return tree
        elif token.isdigit():
            tree.append(int(token))
        else:
            tree.append(token)
    return tree


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

# These are functions and macros that should not output their return values
# when called at the top level (except in repl mode)

topLevelQuietFns = ["tl_def", "tl_disp", "tl_load"]

# These are functions and macros that cannot be called from other functions
# or macros, only from the top level

topLevelOnlyFns = ["tl_load", "tl_help", "tl_restart", "tl_quit"]

# Decorators for member functions that implement builtins

def macro(pyFn):
    pyFn.isMacro = True
    return pyFn

def function(pyFn):
    pyFn.isMacro = False
    return pyFn

# Exception that is raised when, in the repl, the user types (quit)

class UserQuit(BaseException): pass


class Program:
    def __init__(self, repl=False):
        self.repl = repl
        self.modules = []
        self.modulePaths = [os.path.abspath(os.path.dirname(__file__))]
        self.names = [{}]
        self.depth = 0
        # Go through the tinylisp builtins and put the corresponding
        # member functions into the top-level symbol table
        for fnName, tlName in builtins.items():
            self.names[0][tlName] = getattr(self, fnName)

    def execute(self, code):
        if type(code) is str:
            code = parse(code)
        # Evaluate each expression in the code and (possibly) display it
        for expr in code:
            # Figure out which function the outermost call is
            outerFunction = None
            if type(expr) is list and type(expr[0]) is str:
                outerFunction = self.tl_eval(expr[0])
                if type(outerFunction) is type(self.tl_eval):
                    outerFunction = outerFunction.__name__
            result = self.tl_eval(expr, topLevel=True)
            # If outer function is in the topLevelQuietFns list, suppress
            # output--but always show output when running in repl mode
            if self.repl or outerFunction not in topLevelQuietFns:
                self.tl_disp(result)

    def call(self, function, args):
        if type(function) is not list:
            error(self.tl_type(function), "is not callable")
            return []
        elif not 2 <= len(function) <= 3:
            error("%d-length list cannot be interpreted as function or macro"
                  % len(function))
            return []
        elif len(function) == 2:
            # Regular function: evaluate all the arguments
            macro = False
            argnames, code = function
            args = [self.tl_eval(arg) for arg in args]
        elif len(function) == 3:
            # Skip first element of macro list, and don't evaluate
            # the arguments
            macro = True
            argnames, code = function[1:]
        self.depth += 1
        self.names.append({})
        while True:
            if type(argnames) is list:
                if len(argnames) == len(args):
                    for name, val in zip(argnames, args):
                        if type(name) is str:
                            self.names[self.depth][name] = val
                        else:
                            error("argument list must contain names, not",
                                  self.tl_type(name))
                            result = []
                            break
                else:
                    error("wrong number of arguments")
                    result = []
                    break
            elif type(argnames) is str:
                # Single name, bind entire arglist to it
                self.names[self.depth][argnames] = args
            else:
                error("arguments must either be name of list of names, not",
                      self.tl_type(argnames))
                result = []
                break
            
            # Tail-call elimination
            returnExpr = code
            head = None
            # Eliminate any ifs
            while type(returnExpr) is list and len(returnExpr) > 0:
                head = self.tl_eval(returnExpr[0])
                if head == self.tl_if:
                    # The head is (some name for) tl_if
                    test = self.tl_eval(returnExpr[1])
                    if test == 0 or test == []:
                        returnExpr = returnExpr[3]
                    else:
                        returnExpr = returnExpr[2]
                else:
                    break
            if type(head) is list and 2 <= len(head) <= 3:
                # Swap out the args from the original call for the updated
                # args, the function for the new function (which might be
                # the same function), and loop for the recursive call
                if len(head) == 2:
                    macro = False
                    argnames, code = head
                    args = [self.tl_eval(arg) for arg in returnExpr[1:]]
                elif len(head) == 3:
                    macro = True
                    argnames, code = head[1:]
                    args = returnExpr[1:]
                self.names[self.depth] = {}
                continue
            else:
                result = self.tl_eval(returnExpr)
                break
        del self.names[self.depth]
        self.depth -= 1
        return result

    @function
    def tl_cons(self, head, tail):
        if type(tail) is not list:
            error("cannot cons to non-list in tinylisp")
            return []
        else:
            return [head] + tail

    @function
    def tl_head(self, lyst):
        if type(lyst) is not list:
            error("cannot get head of non-list")
            return []
        elif len(lyst) == 0:
            return []
        else:
            return lyst[0]

    @function
    def tl_tail(self, lyst):
        if type(lyst) is not list:
            error("cannot get tail of non-list")
            return []
        elif len(lyst) == 0:
            return []
        else:
            return lyst[1:]

    @function
    def tl_add2(self, arg1, arg2):
        if type(arg1) is not int or type(arg2) is not int:
            error("cannot add non-integers")
            return []
        else:
            return arg1 + arg2

    @function
    def tl_sub2(self, arg1, arg2):
        if type(arg1) is not int or type(arg2) is not int:
            error("cannot subtract non-integers")
            return []
        else:
            return arg1 - arg2

    @function
    def tl_less2(self, arg1, arg2):
        try:
            return int(arg1 < arg2)
        except TypeError:
            error("unorderable types: %s and %s"
                  % (self.tl_type(arg1), self.tl_type(arg2)))

    @function
    def tl_eq2(self, arg1, arg2):
        return int(arg1 == arg2)

    @function
    def tl_eval(self, code, topLevel=False):
        if type(code) is list:
            if code == []:
                # Nil evaluates to itself
                return []
            # Otherwise, it's a function/macro call
            function = self.tl_eval(code[0])
            if type(function) is list:
                # User-defined function or macro
                return self.call(function, code[1:])
            elif type(function) is type(self.tl_eval):
                # Builtin function or macro
                if function.__name__ in topLevelOnlyFns and not topLevel:
                    error("call to", function.__name__, "cannot be nested")
                    return []
                if function.isMacro:
                    # Macros receive their args unevaluated
                    args = code[1:]
                else:
                    # Functions receive their args evaluated
                    args = (self.tl_eval(param) for param in code[1:])
                try:
                    return function(*args)
                except TypeError as err:
                    # Wrong number of arguments to builtin
                    error("wrong number of arguments for", function.__name__)
                    return []
            else:
                # Trying to call an int or unevaluated name
                error("%s is not a function or macro" % function)
                return []
        elif type(code) is int:
            # Integer literal
            return code
        elif type(code) is str:
            # Name; look up its value
            if code in self.names[self.depth]:
                return self.names[self.depth][code]
            elif code in self.names[0]:
                return self.names[0][code]
            else:
                error("referencing undefined name", code)
                return []
        else:
            # Probably a builtin
            return code

    @function
    def tl_type(self, value):
        if type(value) is int:
            return "Int"
        elif type(value) is str:
            return "Name"
        elif type(value) is list:
            return "List"
        else:
            return "Builtin"

    @function
    def tl_disp(self, value, end="\n"):
        if value is not None and not self.quiet:
            if value == []:
                # Empty list
                write("()")
            elif type(value) is list:
                # Non-empty list
                write("(")
                self.tl_disp(value[0], end="")
                for item in value[1:]:
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
        return []

    @macro
    def tl_def(self, name, value):
        if type(name) is int:
            error("cannot def integer")
        elif type(name) is list:
            error("cannot def list")
        elif name in self.names[0]:
            error("name already in use")
        else:
            self.names[0][name] = self.tl_eval(value)
        return name

    @macro
    def tl_if(self, cond, trueval, falseval):
        # Arguments are not pre-evaluated, so cond needs to be evaluated here
        cond = self.tl_eval(cond)
        if cond == 0 or cond == []:
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
            else:
                # Add the module to the list of loaded modules
                self.modules.append(abspath)
                # Push the module's directory to the stack of module
                # directories--this allows relative paths in load calls from
                # within the module
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


def repl():
    print("(welcome to tinylisp)")
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
- disp. Takes a value and writes it to stdout.
- load (macro). Takes a filename and evaluates that file as code.

You can create your own functions and macros. (A macro is like a
function, but doesn't evaluate its arguments; it can therefore be used
to manipulate unevaluated code.)

- To create a function, construct a list of two items. The first item
  should be a list of parameter names. Alternately, it can be a single
  name, in which case it will receive a list of all arguments. The
  second item should be the return expression.
- To create a macro, proceed as with a function, but add a third item
  (nil, by convention) at the beginning of the list.

Special commands for the interactive prompt:

- (restart) clears all user-defined names, starting over from scratch.
- (help) displays this help text.
- (quit) ends the session.
"""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # User specified one or more files--run them
        for filename in sys.argv[1:]:
            try:
                with open(filename) as f:
                    code = f.read()
            except FileNotFoundError:
                error("could not find", filename)
            except IOError:
                error("could not read", filename)
            else:
                environment = Program()
                try:
                    environment.execute(code)
                except UserQuit:
                    pass
    else:
        # No filename specified, so...
        repl()


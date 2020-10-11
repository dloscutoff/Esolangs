
"""Small Instruction Set Interpreter (SISI)"""

import re

intRe = re.compile('([0-9]+)')
idRe = re.compile('([a-z]+)')
strRe = re.compile('"([^"]*)"')
opRe = re.compile('([-+*/<>=])')
regexes = {"int":intRe, "id":idRe, "str":strRe, "op":opRe}

class FatalError(Exception): pass

def parseCode(code):
    instSet = {}
    maxLine = -1
    for line in code:
        line = line.strip()
        if line == "":
            continue

        # First integer on line is line number
        lineNumMatch = intRe.match(line)
        if lineNumMatch:
            line = line[lineNumMatch.end():].strip()
            lineNum = int(lineNumMatch.group())
        else:
            die("all nonempty lines must begin with a line number")
        if lineNum <= maxLine:
            die("line numbers must increase, got", lineNum, "after", maxLine)
        else:
            maxLine = lineNum

        # Second token is statement name
        statementMatch = idRe.match(line)
        if statementMatch:
            line = line[statementMatch.end():].strip()
            statement = statementMatch.group()
        else:
            die("expecting statement on line", lineNum)
        if statement not in ["set","print","jumpif","jump"]:
            die("invalid statement name:", statement)

        # Scan the arguments
        args = []
        if not line:
            die("expecting arguments after statement on line", lineNum)
        else:
            while line != "":
                for kind, regex in regexes.items():
                    valueMatch = regex.match(line)
                    if valueMatch:
                        break
                else:
                    die("invalid expression:", line.split()[0])
                value = valueMatch.group(1)
                if kind == "int":
                    value = int(value)
                args.append((kind, value))
                line = line[valueMatch.end():].strip()

        # Store instructions as {lineNum:[statement,(argtype,argval),...]}
        instSet[lineNum] = [statement] + args
    return instSet

def runInstructions(instSet):
    lineNums = list(instSet.keys())
    lineNums.sort()
    pointer = lineNums[0]
    programState = {}
    while True:
        jump = execute(instSet[pointer], programState)
        if jump:
            pointer = jump
        else:
            pointer += 1
        if pointer > lineNums[-1]:
            # Past the end of the program, we're done
            break
        # Find next line and execute it
        while pointer not in lineNums:
            pointer += 1

def execute(instruction, programState):
    """Executes the instruction.
    Modifies programState and returns a jump address, if any."""

    instType = instruction[0]
    args = instruction[1:]
    condition = None
    jump = None
    if instType == "print":
        # One argument; output it
        if len(args) > 1:
            die("cannot pass multiple values to print")
        else:
            argType, argVal = args[0]
            if argType == "op":
                die("cannot pass operator", argVal, "to print")
            else:
                print(getValue(argType, argVal, programState))
    elif instType == "set":
        # Two possibilities:
        # - With two arguments: id and value
        # - With four arguments: id, value, operator, value
        argTypes = [arg[0] for arg in args]
        argVals = [arg[1] for arg in args]
        if argTypes[0] != "id":
            die("cannot assign to", argTypes[0], argVals[0])
        elif len(args) == 2:
            # Variable and value
            varName = argVals[0]
            value = getValue(argTypes[1], argVals[1], programState)
            setVariable(varName, value, programState)
        elif len(args) == 4:
            # Variable and binary expression
            if argTypes[2] != "op":
                die("expected operator, got", argVals[2])
            else:
                # Calculate expression
                varName = argVals[0]
                left = getValue(argTypes[1], argVals[1], programState)
                right = getValue(argTypes[3], argVals[3], programState)
                op = argVals[2]
                value = evaluate(left, op, right)
                setVariable(varName, value, programState)
        else:
            die("expected syntax: set var value [op value]")
    elif instType == "jumpif":
        # Two arguments, a value and a jump
        if len(args) != 2:
            die("expected syntax: jumpif value linenum")
        else:
            argType, argVal = args.pop(0)
            value = getValue(argType, argVal, programState)
            if value == 0 or value == "":
                condition = False
            else:
                condition = True
    if condition is True or instType == "jump":
        # One argument; evaluate it and jump there
        if len(args) > 1:
            die("cannot pass multiple values to jump")
        else:
            argType, argVal = args[0]
            value = getValue(argType, argVal, programState)
            if type(value) == str:
                die("cannot jump to string", value)
            else:
                jump = value
    return jump
            
def getValue(argType, argVal, programState):
    if argType == "int" or argType == "str":
        value = argVal
    elif argType == "id":
        try:
            value = programState[argVal]
        except:
            # Uninitialized variables are 0 by default
            value = 0
    elif argType == "op":
        die("expected value, got operator", argVal)
    return value

def setVariable(varName, value, programState):
    programState[varName] = value

def evaluate(left, operator, right):
    if operator == "=":
        operator = "=="
        # (One of the strangest bits of code I've written...)
    if type(left) == type(right) == int:
        # All integer operations are supported
        pass
    elif type(left) == type(right) == str:
        # Some string operations are not supported
        if operator in "-*/":
            die("cannot use operator", operator, "on strings")
    else:
        # Only + (concatenate) is supported for string and integer
        if operator != "+":
            die("cannot use operator", operator, "on string and int")
        else:
            # Python complains when adding str + int, so cast both to strings
            left = str(left)
            right = str(right)
    # If the args & operator combo was valid, use Python built-in operators
    result = eval("{0}{1}{2}".format(repr(left), operator, repr(right)))
    return result

def runFile(filename):
    try:
        try:
            with open(filename) as f:
                code = f.readlines()
        except:
            die("could not open", filename)
        else:
            instructions = parseCode(code)
            runInstructions(instructions)
    except FatalError:
        # The error message is printed where it is raised; quit silently
        pass

def die(*message):
    print("ERROR:", *message)
    raise FatalError()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        runFile(sys.argv[1])
    else:
        runFile(input("Enter the path to your code: "))
